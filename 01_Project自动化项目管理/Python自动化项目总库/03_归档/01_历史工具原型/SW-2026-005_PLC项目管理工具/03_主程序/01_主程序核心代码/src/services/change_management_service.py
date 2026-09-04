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
        verification_conclusion: str = "全部通过",
    ) -> ChangeRequest | None:
        """状态流转（PM-042 V2.2.0 §5.2 状态机）

        更新变更单文件中的审批/实施/验证章节。
        状态机定义见 spec_constants.STATUS_FLOW，门禁规则见 _check_transition_guards。

        验收流程（V2.2.0 新增）:
            implementing → pending_acceptance → accepting → completed
                                                         ↘ implementing（返工）
        """
        file_path = self._find_change_file(change_number)
        if not file_path:
            log.warning("状态流转: 变更单文件未找到 %s", change_number)
            return None

        log.info(
            "状态流转: %s → %s, 审批人=%s, 验证结论=%s",
            change_number, new_status, approver, verification_conclusion,
        )

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

        today = datetime.date.today().isoformat()

        # ---- 分状态处理写入逻辑和门禁校验 ----
        # 门禁规则完整清单: PM-042 V2.2.0 第四章

        if new_status == "completed":
            # [PM-042 §5.2] accepting → completed: 验证通过路径
            # 门禁: verification_conclusion 必须为「全部通过」（参数级前置拦截）
            if verification_conclusion != "全部通过":
                raise TransitionGuardError(
                    f"变更单 {change_number} 验证结论为'{verification_conclusion}'，"
                    "需为'全部通过'才能完成验收；"
                    "如验证不通过请使用「退回返工」(accepting → implementing)"
                )

            # 门禁通过：写入验证行和验证结论到§10
            verify_row = (
                f"| 1 | 实施完成验证 | 所有变更项已实施 | 通过 | 通过 "
                f"| ☑{verification_conclusion} | {approver} | {today} |\n"
            )
            content = self._append_to_verification_table(content, verify_row)
            content = self._update_verification_conclusion(content, verification_conclusion)

            # 写临时文件做二次校验
            tmp_path = file_path + ".tmp"
            write_file(tmp_path, content)
            try:
                tmp_cr = self._parser.parse(tmp_path)
                if tmp_cr.status != new_status:
                    raise TransitionGuardError(
                        f"变更单 {change_number} 写入后状态解析异常: "
                        f"期望 '{new_status}'，实际 '{tmp_cr.status}'"
                    )
            except TransitionGuardError:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise
            except Exception:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        elif new_status == "pending_acceptance":
            # [PM-042 §5.2] implementing → pending_acceptance: 提交验收
            # 门禁: §9 实施记录至少一条（第四章）
            self._check_transition_guards(current_cr, new_status, approver, comment)

        elif new_status == "accepting":
            # [PM-042 §5.2] pending_acceptance → accepting: 开始验收
            # 门禁: 无额外门禁（第四章）
            self._check_transition_guards(current_cr, new_status, approver, comment)

        elif new_status == "implementing" and current_cr.status == "accepting":
            # [PM-042 §5.2] accepting → implementing: 验证不通过，返工重做
            # 门禁: 无额外门禁 — 允许立即返回重做（第四章 路径B）
            self._check_transition_guards(current_cr, new_status, approver, comment)

        else:
            # 其他流转：门禁检查已有内容
            self._check_transition_guards(current_cr, new_status, approver, comment)

        # 1. 更新 §3.4 变更状态字段（状态持久化的主路径）
        content = self._update_status_field(content, new_status)

        # 2. 更新相关章节记录
        if new_status in ("approved", "conditionally_approved", "rejected"):
            approval_row = f"| **{new_status.upper()}** | {approver} | {comment or '同意'} | {today} | {approver} |\n"
            content = self._append_to_approval_table(content, approval_row)
        elif new_status == "implementing":
            # 区分首次实施 vs 返工重做
            if current_cr.status in ("approved", "conditionally_approved"):
                impl_row = f"| {today} | {approver} | 实施中 | 开始实施 | 进行中 | |\n"
            else:
                # accepting → implementing（返工）：记录返工原因
                impl_row = f"| {today} | {approver} | 返工重做 | 验证不通过: {(comment or '需重新实施')[:30]} | 返工中 | |\n"
            content = self._append_to_implementation_table(content, impl_row)
        # completed: §10 已在门禁前写入
        # pending_acceptance / accepting: 无额外章节需要写入

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
        """在验证表格 (§10.1) 末尾追加一行

        在 §10.2 节标题之前插入新行，避免正则匹配偏移。
        """
        # 定位 §10.1 起始位置
        sec_10_1 = re.search(r"^###\s*10\.1", content, re.MULTILINE)
        if not sec_10_1:
            return content + "\n" + row

        # 定位 §10.2 节标题，在其前插入
        remainder = content[sec_10_1.end():]
        next_section = re.search(r"^###\s*10\.2", remainder, re.MULTILINE)
        if next_section:
            insert_pos = sec_10_1.end() + next_section.start()
            return content[:insert_pos].rstrip() + "\n" + row + content[insert_pos:]

        # 无 §10.2：在 §10.1 区域末尾追加
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

    def _update_verification_conclusion(self, content: str, conclusion: str) -> str:
        """更新 §10.2 验证结论为指定值

        兼容三种格式：
        1. 原始模板格式: | 结论 | □ 全部通过,可关闭 □ 部分不通过,需返工 □ 需补充验证 |
        2. 已写入格式:    | **验证结论** | 全部通过 |
        3. § 符号变体:    ### §10.2 或 ### 10.2
        """
        lines = content.splitlines()
        in_section_10_2 = False
        found_conclusion_line = False
        result = []
        for line in lines:
            stripped = line.strip()
            # 匹配 ### 10.2 或 ### §10.2（兼容有无 § 符号）
            if re.match(r"^###\s*§?\s*10\.2\b", stripped):
                in_section_10_2 = True
                result.append(line)
                continue
            if in_section_10_2 and re.match(r"^###\s", stripped):
                in_section_10_2 = False

            if in_section_10_2 and not found_conclusion_line:
                # 格式A: 模板原始格式 | 结论 | □ ... |
                if re.match(r"^\|\s*结论\s*\|", stripped):
                    result.append(f"| **验证结论** | {conclusion} |")
                    found_conclusion_line = True
                    continue
                # 格式B: 已写入的 **验证结论** 格式
                if "**验证结论**" in stripped:
                    result.append(f"| **验证结论** | {conclusion} |")
                    found_conclusion_line = True
                    continue

            result.append(line)

        # 如果进入了 §10.2 但没找到结论行，在节标题后插入
        if in_section_10_2 and not found_conclusion_line:
            # 在 result 中找到 §10.2 标题行后插入
            for i, r in enumerate(result):
                if re.match(r"^###\s*§?\s*10\.2\b", r.strip()):
                    result.insert(i + 1, f"| **验证结论** | {conclusion} |")
                    break

        return "\n".join(result)

    def _check_transition_guards(
        self,
        cr: ChangeRequest,
        target_status: str,
        approver: str,
        comment: str,
    ) -> None:
        """检查流转门禁条件（PM-042 V2.2.0 §5.3）

        读取变更单当前内容，校验是否满足目标状态的前置条件。
        不满足则抛 TransitionGuardError，列出所有未满足的条件。

        门禁规则完整清单见规范第四章。
        completed 状态的门禁校验已提升至 transition_status 方法中
        （参数级前置拦截），此处不再重复。
        """
        violations: list[str] = []

        if target_status == "submitted":
            # [第四章] draft → submitted: 提交变更
            # 门禁: §3全部填写 + §4非空
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
            # [第四章] under_review → approved: 批准通过
            # 门禁: §8.1有审批记录 + 审批人非空
            if not cr.has_section_8_approval and not approver:
                violations.append("§8.1 无审批记录，且未提供审批人")
            if not approver:
                violations.append("审批人(approver)不能为空")

        elif target_status == "conditionally_approved":
            # [第四章] under_review → conditionally_approved: 有条件批准
            # 门禁: 同approved + comment非空
            if not cr.has_section_8_approval and not approver:
                violations.append("§8.1 无审批记录，且未提供审批人")
            if not approver:
                violations.append("审批人(approver)不能为空")
            if not comment:
                violations.append("有条件通过必须附条件说明(comment)")

        elif target_status == "rejected":
            # [第四章] under_review → rejected: 驳回
            # 门禁: 审批人+comment非空
            if not approver:
                violations.append("审批人(approver)不能为空")
            if not comment:
                violations.append("驳回必须附原因(comment)")

        elif target_status == "implementing":
            # [第四章] 两条路径进入 implementing:
            #   路径A: approved/conditionally_approved → implementing（首次实施）
            #     门禁: §7 实施计划至少一条任务
            #   路径B: accepting → implementing（验证不通过，返工重做）
            #     门禁: 无额外门禁（第四章 路径B）
            if cr.status in ("approved", "conditionally_approved"):
                if not cr.has_section_7:
                    violations.append("§7 实施计划未填写（至少一条任务）")
            # 路径B（返工）：不施加额外门禁，允许验证不通过时返回重做

        elif target_status == "pending_acceptance":
            # [第四章] implementing → pending_acceptance: 提交验收
            # 门禁: §9 实施记录至少一条
            if not cr.has_section_9:
                violations.append("§9 实施记录未填写（至少一条实施记录）")

        elif target_status == "accepting":
            # pending_acceptance → accepting: 无额外门禁（PM-042 V2.2.0 第四章）
            pass

        # completed 的门禁已提升至 transition_status 方法中作为参数级前置校验，
        # 不在此处重复检查，避免与参数级校验逻辑冲突。

        if violations:
            msg = (
                f"变更单 {cr.change_number} 不满足 '{target_status}' 的门禁条件:\n"
                + "\n".join(f"  - {v}" for v in violations)
            )
            log.error("门禁校验失败: %s", msg)
            raise TransitionGuardError(msg)
