"""变更管理 Service - 变更单 CRUD + 状态流转"""

from __future__ import annotations

import datetime
import os
import re

from src.models.change_request import ChangeRequest, ChangeSummary
from src.models.spec_constants import (
    SpecViolationError,
    TransitionGuardError,
    validate_business_nature,
    validate_domain,
    validate_impact_scope,
    validate_status_transition,
    validate_urgency,
)
from src.parsers.chg_parser import ChgParser
from src.utils.file_utils import write_file
from src.utils.logger import get_logger
from src.utils.path_resolver import (
    extract_domain_from_change_number,
    find_ledger_file,
    scan_change_files,
)

log = get_logger(__name__)


class ChangeManagementService:
    """变更管理 Service - 变更单 CRUD + 状态流转"""

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = workspace_root
        self._parser = ChgParser()
        # 延迟导入，避免循环依赖
        self._generator = None
        self._ledger_updater = None

    def _get_generator(self):
        if self._generator is None:
            from src.generators.chg_generator import ChgGenerator
            self._generator = ChgGenerator()
        return self._generator

    def _get_ledger_updater(self):
        if self._ledger_updater is None:
            from src.generators.ledger_updater import LedgerUpdater
            self._ledger_updater = LedgerUpdater()
        return self._ledger_updater

    def create_change_request(
        self,
        project_id: str,
        domain: str,
        business_nature: str,
        impact_scope: list[str],
        applicant: str,
        background: str,
        necessity: str,
        references: str = "",
        planned_date: str | None = None,
        urgency: str = "normal",
    ) -> ChangeRequest:
        """创建变更单

        1. 生成变更编号 CHG-{DOMAIN}-{YYYY}-{XXX}
        2. 渲染 CHG-040 模板
        3. 保存 Markdown 文件
        4. 更新版本变更台帐
        """
        project_path = self._get_project_path(project_id)
        if not project_path:
            log.error("创建变更单失败: 项目不存在 %s", project_id)
            raise ValueError(f"项目不存在: {project_id}")

        # 规范校验：创建前必须通过
        validate_domain(domain)
        validate_business_nature(business_nature)
        validate_impact_scope(impact_scope)
        validate_urgency(urgency)

        # 生成变更编号
        change_number = self._generate_change_number(project_path, domain)
        log.info("创建变更单: %s, 项目=%s, 领域=%s, 性质=%s, 范围=%s",
                 change_number, project_id, domain, business_nature, impact_scope)

        # 构造 ChangeRequest
        today = datetime.date.today().isoformat()
        cr = ChangeRequest(
            change_number=change_number,
            project_id=project_id,
            project_name=project_id,
            domain=domain,
            business_nature=business_nature,
            impact_scope=impact_scope,
            applicant=applicant,
            apply_date=today,
            planned_date=planned_date or today,
            urgency=urgency,
            background=background,
            necessity=necessity,
            references=references,
            status="draft",
        )

        # 生成文件路径
        file_path = self._get_change_file_path(project_path, change_number)

        # 渲染并保存
        content = self._get_generator().render(cr)
        write_file(file_path, content)
        cr.file_path = file_path
        log.info("变更单文件已保存: %s", file_path)

        # 更新台帐
        ledger_path = find_ledger_file(project_path)
        if ledger_path:
            self._get_ledger_updater().update(
                ledger_path, change_number, background[:50]
            )
            log.info("台帐已更新: %s", ledger_path)
        else:
            log.warning("台帐文件未找到，跳过更新: %s", project_path)

        return cr

    def list_change_requests(
        self,
        project_id: str,
        status: str | None = None,
        domain: str | None = None,
    ) -> list[ChangeSummary]:
        """列出变更单，支持筛选"""
        project_path = self._get_project_path(project_id)
        if not project_path:
            log.warning("列出变更单: 项目不存在 %s", project_id)
            return []

        change_files = scan_change_files(project_path)
        log.info("列出变更单: %s, 共%d个文件, 筛选status=%s domain=%s",
                 project_id, len(change_files), status, domain)
        summaries: list[ChangeSummary] = []
        for cf in change_files:
            cr = self._parser.parse(cf)
            summary = self._parser.to_summary(cr)
            # 筛选
            if status and summary.status != status:
                continue
            if domain and summary.domain != domain:
                continue
            summaries.append(summary)

        log.info("筛选结果: %d 条变更单", len(summaries))
        return summaries

    def get_change_request(self, change_number: str) -> ChangeRequest | None:
        """获取变更单完整内容"""
        file_path = self._find_change_file(change_number)
        if not file_path:
            log.warning("获取变更单: 文件未找到 %s", change_number)
            return None
        log.debug("获取变更单: %s, 文件=%s", change_number, file_path)
        return self._parser.parse(file_path)

    def transition_status(
        self,
        change_number: str,
        new_status: str,
        approver: str = "",
        comment: str = "",
    ) -> ChangeRequest | None:
        """状态流转

        更新变更单文件中的审批/实施/验证章节
        """
        file_path = self._find_change_file(change_number)
        if not file_path:
            log.warning("状态流转: 变更单文件未找到 %s", change_number)
            return None

        log.info("状态流转: %s → %s, 审批人=%s", change_number, new_status, approver)

        # 读取当前内容，获取当前状态
        from src.utils.file_utils import read_file
        content = read_file(file_path)
        if not content:
            log.error("状态流转: 读取变更单内容失败 %s", file_path)
            return None

        # 规范校验：状态流转必须合法
        current_cr = self._parser.parse(file_path)
        try:
            validate_status_transition(current_cr.status, new_status)
        except SpecViolationError as e:
            log.error("状态流转校验失败: %s", e)
            raise

        # 门禁校验：变更单内容必须满足流转前置条件
        self._check_transition_guards(current_cr, new_status, approver, comment)

        # 1. 更新 §3.4 变更状态字段（状态持久化的主路径）
        content = self._update_status_field(content, new_status)

        # 2. 更新相关章节记录
        today = datetime.date.today().isoformat()
        if new_status in ("approved", "conditionally_approved", "rejected"):
            # 在审批流程表格中追加一行
            approval_row = f"| **{new_status.upper()}** | {approver} | {comment or '同意'} | {today} | {approver} |\n"
            content = self._append_to_approval_table(content, approval_row)
        elif new_status == "implementing":
            # 在 §9 实施记录中追加一行
            impl_row = f"| {today} | {approver} | 实施中 | 开始实施 | 进行中 | |\n"
            content = self._append_to_implementation_table(content, impl_row)
        elif new_status == "completed":
            # 在 §10 验证中追加一行
            verify_row = f"| 1 | 实施完成验证 | 所有变更项已实施 | 通过 | 通过 | ☑通过 | {approver} | {today} |\n"
            content = self._append_to_verification_table(content, verify_row)

        write_file(file_path, content)

        # 重新解析返回
        result = self._parser.parse(file_path)
        log.info("状态流转完成: %s, 新状态=%s", change_number, result.status)
        return result

    # ---- 内部方法 ----

    def _get_project_path(self, project_id: str) -> str | None:
        """根据项目编号获取项目路径"""
        candidate = os.path.join(self.workspace_root, project_id)
        if os.path.isdir(candidate):
            return candidate
        return None

    def _generate_change_number(self, project_path: str, domain: str) -> str:
        """生成变更编号 CHG-{DOMAIN}-{YYYY}-{XXX}

        扫描已有变更单，确定下一个序号
        """
        year = str(datetime.date.today().year)
        change_files = scan_change_files(project_path)

        # 找出同领域同年的最大序号
        max_seq = 0
        prefix = f"CHG-{domain}-{year}-"
        for cf in change_files:
            basename = os.path.splitext(os.path.basename(cf))[0]
            if basename.startswith(prefix):
                seq_str = basename[len(prefix):]
                try:
                    seq = int(seq_str)
                    max_seq = max(max_seq, seq)
                except ValueError:
                    pass

        next_seq = max_seq + 1
        result = f"CHG-{domain}-{year}-{next_seq:03d}"
        log.debug("生成变更编号: %s (已有同领域最大序号=%d)", result, max_seq)
        return result

    def _get_change_file_path(self, project_path: str, change_number: str) -> str:
        """根据变更编号获取文件路径

        格式: 00_项目管理/04_变更管理/01_变更单/CHG-{DOMAIN}/CHG-{DOMAIN}-{YYYY}-{XXX}.md
        """
        domain = extract_domain_from_change_number(change_number)
        return os.path.join(
            project_path,
            "00_项目管理", "04_变更管理", "01_变更单",
            f"CHG-{domain}",
            f"{change_number}.md",
        )

    def _find_change_file(self, change_number: str) -> str | None:
        """根据变更编号查找文件"""
        domain = extract_domain_from_change_number(change_number)
        if not domain:
            log.warning("查找变更单: 无法从编号提取领域 %s", change_number)
            return None

        # 遍历工作空间下的项目查找
        if not os.path.isdir(self.workspace_root):
            log.warning("查找变更单: 工作空间目录不存在 %s", self.workspace_root)
            return None

        for name in os.listdir(self.workspace_root):
            project_path = os.path.join(self.workspace_root, name)
            if not os.path.isdir(project_path):
                continue
            candidate = os.path.join(
                project_path,
                "00_项目管理", "04_变更管理", "01_变更单",
                f"CHG-{domain}",
                f"{change_number}.md",
            )
            if os.path.isfile(candidate):
                return candidate

        return None

    def _append_to_approval_table(self, content: str, row: str) -> str:
        """在审批流程表格末尾追加一行"""
        # 查找 §8.1 审批流程
        pattern = re.compile(
            r"(###\s*8\.1.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|\n)((?:\|[\s\-:|]+\|\n)?(?:\|.*\|\n)*)",
            re.DOTALL,
        )
        match = pattern.search(content)
        if match:
            return content[:match.end()] + row + content[match.end():]
        # 兜底：在 §8 章节末尾追加
        return content + "\n" + row

    def _append_to_implementation_table(self, content: str, row: str) -> str:
        """在实施记录表格末尾追加一行"""
        pattern = re.compile(
            r"(##\s*9\..*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|\n)((?:\|[\s\-:|]+\|\n)?(?:\|.*\|\n)*)",
            re.DOTALL,
        )
        match = pattern.search(content)
        if match:
            return content[:match.end()] + row + content[match.end():]
        return content + "\n" + row

    def _append_to_verification_table(self, content: str, row: str) -> str:
        """在验证表格末尾追加一行"""
        pattern = re.compile(
            r"(###\s*10\.1.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|\n)((?:\|[\s\-:|]+\|\n)?(?:\|.*\|\n)*)",
            re.DOTALL,
        )
        match = pattern.search(content)
        if match:
            return content[:match.end()] + row + content[match.end():]
        return content + "\n" + row

    def _update_status_field(self, content: str, new_status: str) -> str:
        """更新 §3.4 申请信息表中的"变更状态"字段

        如果已有"变更状态"行，替换值；如果没有，在紧急程度行后追加。
        """
        # 替换已有的变更状态行
        pattern = re.compile(r"(\|\s*变更状态\s*\|\s*)\S+(\s*\|)")
        if pattern.search(content):
            return pattern.sub(r"\g<1>" + new_status + r"\2", content)
        # 没有变更状态行，在紧急程度行后追加
        urgency_pattern = re.compile(r"(\|\s*紧急程度\s*\|.*?\|)\n")
        match = urgency_pattern.search(content)
        if match:
            return content[:match.end()] + f"| 变更状态 | {new_status} |\n" + content[match.end():]
        # 兜底：在 §3.4 末尾追加
        return content + f"\n| 变更状态 | {new_status} |\n"

    def _check_transition_guards(
        self,
        cr: ChangeRequest,
        target_status: str,
        approver: str,
        comment: str,
    ) -> None:
        """检查流转门禁条件（DES V1.2.0 §5.3）

        读取变更单当前内容，校验是否满足目标状态的前置条件。
        不满足则抛 TransitionGuardError，列出所有未满足的条件。
        """
        violations: list[str] = []

        if target_status == "submitted":
            # draft → submitted: §3 全部子章节已填写 + §4 变更原因非空
            if not cr.domain:
                violations.append("§3.1 技术领域未填写")
            if not cr.business_nature:
                violations.append("§3.2 业务性质未填写")
            if not cr.impact_scope:
                violations.append("§3.3 影响范围未填写")
            if not cr.applicant or cr.applicant == "待补充":
                violations.append("§3.4 变更申请人未填写")
            if not cr.has_section_4:
                violations.append("§4 变更原因未填写")

        elif target_status == "approved":
            # under_review → approved: §8.1 至少一条审批记录 + approver 非空
            if not cr.has_section_8_approval and not approver:
                violations.append("§8.1 无审批记录，且未提供审批人")
            if not approver:
                violations.append("审批人(approver)不能为空")

        elif target_status == "conditionally_approved":
            # under_review → conditionally_approved: 同 approved + comment 非空
            if not cr.has_section_8_approval and not approver:
                violations.append("§8.1 无审批记录，且未提供审批人")
            if not approver:
                violations.append("审批人(approver)不能为空")
            if not comment:
                violations.append("有条件通过必须附条件说明(comment)")

        elif target_status == "rejected":
            # under_review → rejected: approver 非空 + comment 非空
            if not approver:
                violations.append("审批人(approver)不能为空")
            if not comment:
                violations.append("驳回必须附原因(comment)")

        elif target_status == "implementing":
            # approved/conditionally_approved → implementing: §7 实施计划至少一条任务
            if not cr.has_section_7:
                violations.append("§7 实施计划未填写（至少一条任务）")

        elif target_status == "completed":
            # implementing → completed: §9 实施记录 + §10 验证通过
            if not cr.has_section_9:
                violations.append("§9 实施记录未填写（至少一条记录）")
            if not cr.has_section_10_verify:
                violations.append("§10.1 验证项未填写（至少一条验证项）")
            if cr.section_10_conclusion != "全部通过":
                violations.append(
                    f"§10.2 验证结论为'{cr.section_10_conclusion or '空'}'，"
                    "需为'全部通过'才能完成"
                )

        if violations:
            msg = (
                f"变更单 {cr.change_number} 不满足 '{target_status}' 的门禁条件:\n"
                + "\n".join(f"  - {v}" for v in violations)
            )
            log.error("门禁校验失败: %s", msg)
            raise TransitionGuardError(msg)
