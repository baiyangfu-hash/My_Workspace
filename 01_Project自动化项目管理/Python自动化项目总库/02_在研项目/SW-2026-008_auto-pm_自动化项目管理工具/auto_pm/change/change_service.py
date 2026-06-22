"""变更管理 Service - 变更单 CRUD + 状态流转

M3-Iter2 重构：从 870 行上帝类拆分为 4 个职责单一的类：
- ChangeService（本类）：CRUD + 状态流转编排
- ChangeFileLocator：文件路径定位
- ChangeMarkdownEditor：Markdown 内容编辑
- TransitionGuardChecker：状态流转门禁检查

本类通过组合方式使用上述模块，保留旧方法签名以向后兼容。
"""

from __future__ import annotations

import datetime
import os
from typing import Optional

from auto_pm.change.file_locator import ChangeFileLocator
from auto_pm.change.guard_checker import TransitionGuardChecker
from auto_pm.change.markdown_editor import ChangeMarkdownEditor
from auto_pm.change.models import (
    ChangeRequest,
    ChangeSummary,
    SpecViolationError,
    TransitionGuardError,
    validate_business_nature,
    validate_domain,
    validate_impact_scope,
    validate_status_transition,
    validate_urgency,
)
from auto_pm.change.parser import ChgParser
from auto_pm.change.path_resolver import find_ledger_file
from auto_pm.db.connection import DatabaseManager
from auto_pm.db.repository import ChangeRequestRepository
from auto_pm.logging.logging import setup_logger as get_logger
from auto_pm.utils.file_utils import get_mtime, read_file, write_file

log = get_logger(log_level="INFO", app_name="auto_pm")


class ChangeService:
    """变更管理 Service - 变更单 CRUD + 状态流转

    通过组合 ChangeFileLocator / ChangeMarkdownEditor / TransitionGuardChecker
    实现职责分离。本类保留对外的旧方法签名（如 _find_change_file 等）以避免
    破坏调用方，内部全部委托给组合对象。
    """

    # update_change_request 允许修改的字段
    _UPDATABLE_FIELDS: set[str] = {
        "background",
        "necessity",
        "references",
        "planned_date",
        "urgency",
    }

    # update_change_request 禁止修改的字段（受保护）
    _PROTECTED_FIELDS: set[str] = {"change_number", "project_id", "status"}

    def __init__(self, workspace_root: str, db: DatabaseManager | None = None) -> None:
        self.workspace_root = workspace_root
        self._parser = ChgParser()
        # 延迟导入，避免循环依赖
        self._generator = None
        self._ledger_updater = None
        # DB 缓存（可选，传入后 list_all_changes/update/delete 会同步缓存）
        self.db = db
        self._repo: ChangeRequestRepository | None = (
            ChangeRequestRepository(db) if db else None
        )
        # M3-Iter2: 组合职责单一的辅助类
        self._locator = ChangeFileLocator(workspace_root, self._parser)
        self._editor = ChangeMarkdownEditor()
        self._guard = TransitionGuardChecker()

    def _get_generator(self):
        if self._generator is None:
            from auto_pm.change.generator import ChgGenerator
            self._generator = ChgGenerator()
        return self._generator

    def _get_ledger_updater(self):
        if self._ledger_updater is None:
            from auto_pm.change.ledger_updater import LedgerUpdater
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
        project_path = self._locator.get_project_path(project_id)
        if not project_path:
            log.error("创建变更单失败: 项目不存在 %s", project_id)
            raise ValueError(f"项目不存在: {project_id}")

        # 规范校验：创建前必须通过
        validate_domain(domain)
        validate_business_nature(business_nature)
        validate_impact_scope(impact_scope)
        validate_urgency(urgency)

        # 生成变更编号
        change_number = self._locator.generate_change_number(project_path, domain)
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
        file_path = self._locator.get_change_file_path(project_path, change_number)

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
        project_path = self._locator.get_project_path(project_id)
        if not project_path:
            log.warning("列出变更单: 项目不存在 %s", project_id)
            return []

        from auto_pm.change.path_resolver import scan_change_files
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
        file_path = self._locator.find_change_file(change_number)
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
        file_path = self._locator.find_change_file(change_number)
        if not file_path:
            log.warning("状态流转: 变更单文件未找到 %s", change_number)
            return None

        log.info(
            "状态流转: %s → %s, 审批人=%s, 验证结论=%s",
            change_number, new_status, approver, verification_conclusion,
        )

        # 读取当前内容，获取当前状态
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
            content = self._editor.append_to_verification_table(content, verify_row)
            content = self._editor.update_verification_conclusion(content, verification_conclusion)
            # 注意：§3.4 状态字段更新统一在下方第 299 行执行，避免时序 bug（KNOWN-1 修复）

        elif new_status == "archived":
            # [PM-042 V2.3.0 §5.2] completed → archived: 归档
            # 门禁: 仅 completed 状态可归档（在 _check_transition_guards 中校验）
            self._guard.check(current_cr, new_status, approver, comment)

        elif new_status == "pending_acceptance":
            # [PM-042 §5.2] implementing → pending_acceptance: 提交验收
            # 门禁: §9 实施记录至少一条（第四章）
            self._guard.check(current_cr, new_status, approver, comment)

        elif new_status == "accepting":
            # [PM-042 §5.2] pending_acceptance → accepting: 开始验收
            # 门禁: 无额外门禁（第四章）
            self._guard.check(current_cr, new_status, approver, comment)

        elif new_status == "implementing" and current_cr.status == "accepting":
            # [PM-042 §5.2] accepting → implementing: 验证不通过，返工重做
            # 门禁: 无额外门禁 — 允许立即返回重做（第四章 路径B）
            self._guard.check(current_cr, new_status, approver, comment)

        else:
            # 其他流转：门禁检查已有内容
            self._guard.check(current_cr, new_status, approver, comment)

        # 1. 更新 §3.4 变更状态字段（状态持久化的主路径）
        content = self._editor.update_status_field(content, new_status)

        # 2. 更新相关章节记录
        if new_status in ("approved", "conditionally_approved", "rejected"):
            # 审批环节名称使用中文语义化标签（对齐 STATUS_LABELS）
            from auto_pm.change.models import STATUS_LABELS
            status_label = STATUS_LABELS.get(new_status, new_status)
            approval_row = f"| **{status_label}** | {approver} | {comment or '同意'} | {today} | {approver} |\n"
            content = self._editor.append_to_approval_table(content, approval_row)
        elif new_status == "implementing":
            # 区分首次实施 vs 返工重做
            if current_cr.status in ("approved", "conditionally_approved"):
                impl_row = f"| {today} | {approver} | 实施中 | 开始实施 | 进行中 | |\n"
            else:
                # accepting → implementing（返工）：记录返工原因
                impl_row = f"| {today} | {approver} | 返工重做 | 验证不通过: {(comment or '需重新实施')[:30]} | 返工中 | |\n"
            content = self._editor.append_to_implementation_table(content, impl_row)
        # completed: §10 已在门禁前写入
        # pending_acceptance / accepting: 无额外章节需要写入

        write_file(file_path, content)

        # 重新解析返回
        result = self._parser.parse(file_path)
        log.info("状态流转完成: %s, 新状态=%s", change_number, result.status)
        return result

    # ---- 跨项目查询 / 修改 / 删除 ----

    def list_all_changes(
        self,
        status: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> list[ChangeSummary]:
        """跨项目查询所有变更单（用于变更中心全局列表）

        Args:
            status: 按状态筛选（draft/submitted/approved/implementing/completed/archived 等）
            domain: 按领域筛选（ELEC/MECH/PLC/HMI/SCPT/DOCU/SAFE）

        Returns:
            变更单摘要列表，按 change_number 排序
        """
        # 优先从 DB 缓存查询；未注入 DB 时回退到文件系统扫描
        if self._repo is not None:
            changes = self._repo.list_all()
        else:
            changes = self._locator.scan_all_change_files()

        if status:
            changes = [c for c in changes if c.status == status]
        if domain:
            changes = [c for c in changes if c.domain == domain]

        log.info(
            "跨项目查询变更单: status=%s domain=%s → %d 条",
            status, domain, len(changes),
        )
        return sorted(changes, key=lambda c: c.change_number)

    def update_change_request(
        self,
        change_number: str,
        **kwargs,
    ) -> Optional[ChangeRequest]:
        """修改变更单字段

        支持修改的字段：background, necessity, urgency, planned_date, references
        不允许修改：change_number, project_id, status（用 transition_status）

        Args:
            change_number: 变更单编号
            **kwargs: 要修改的字段

        Returns:
            更新后的 ChangeRequest，失败返回 None

        Raises:
            ValueError: 尝试修改受保护字段
            SpecViolationError: urgency 值不合法
        """
        # 1. 校验字段合法性
        for key in kwargs:
            if key in self._PROTECTED_FIELDS:
                log.error("修改变更单: 字段 %s 不允许修改", key)
                raise ValueError(
                    f"字段 '{key}' 不允许修改"
                    + ("（使用 transition_status 修改状态）" if key == "status" else "")
                )

        # 2. 获取变更单文件
        file_path = self._locator.find_change_file(change_number)
        if not file_path:
            log.warning("修改变更单: 文件未找到 %s", change_number)
            return None

        # 3. 校验 urgency 合法性
        if "urgency" in kwargs and kwargs["urgency"] is not None:
            validate_urgency(kwargs["urgency"])

        # 4. 读取文件内容
        content = read_file(file_path)
        if not content:
            log.error("修改变更单: 读取文件失败 %s", file_path)
            return None

        # 5. 逐字段修改 .md 章节
        updated_fields: list[str] = []
        for field, value in kwargs.items():
            if field not in self._UPDATABLE_FIELDS or value is None:
                log.debug("修改变更单: 跳过字段 %s（不可修改或为 None）", field)
                continue
            new_content = self._editor.update_field(content, field, value)
            if new_content != content:
                content = new_content
                updated_fields.append(field)

        if not updated_fields:
            log.warning("修改变更单: 无有效字段被更新 %s", change_number)
            return self._parser.parse(file_path)

        # 6. 写回文件
        write_file(file_path, content)
        log.info("变更单已修改: %s, 字段=%s", change_number, updated_fields)

        # 7. 重新解析
        updated = self._parser.parse(file_path)

        # 8. 更新 DB 缓存
        if self._repo is not None:
            summary = self._parser.to_summary(updated)
            self._repo.upsert(summary, file_path, get_mtime(file_path))
            log.debug("DB 缓存已更新: %s", change_number)

        return updated

    def delete_change_request(self, change_number: str) -> bool:
        """删除变更单（文件 + DB 缓存）

        Args:
            change_number: 变更单编号

        Returns:
            True 删除成功，False 不存在
        """
        file_path = self._locator.find_change_file(change_number)
        file_deleted = False

        # 1. 删除 .md 文件
        if file_path:
            try:
                os.remove(file_path)
                file_deleted = True
                log.info("变更单文件已删除: %s", file_path)
            except OSError as e:
                log.error("删除变更单文件失败: %s: %s", file_path, e)
        else:
            log.warning("删除变更单: 文件未找到 %s", change_number)

        # 2. 从 DB 缓存删除
        db_deleted = False
        if self._repo is not None:
            db_deleted = self._repo.delete(change_number)
            if db_deleted:
                log.info("DB 缓存记录已删除: %s", change_number)

        # 文件或 DB 任一删除成功即视为成功
        return file_deleted or db_deleted

    # ── 向后兼容的委托方法（M3-Iter2 保留签名，内部委托给组合对象） ──

    def _get_project_path(self, project_id: str) -> str | None:
        """[已委托] 根据项目编号获取项目路径（向后兼容包装）"""
        return self._locator.get_project_path(project_id)

    def _generate_change_number(self, project_path: str, domain: str) -> str:
        """[已委托] 生成变更编号（向后兼容包装）"""
        return self._locator.generate_change_number(project_path, domain)

    def _get_change_file_path(self, project_path: str, change_number: str) -> str:
        """[已委托] 根据变更编号获取文件路径（向后兼容包装）"""
        return self._locator.get_change_file_path(project_path, change_number)

    def _find_change_file(self, change_number: str) -> str | None:
        """[已委托] 根据变更编号查找文件（向后兼容包装）"""
        return self._locator.find_change_file(change_number)

    def _scan_all_change_files(self) -> list[ChangeSummary]:
        """[已委托] 扫描工作空间所有项目的变更单文件（向后兼容包装）"""
        return self._locator.scan_all_change_files()

    def _append_to_approval_table(self, content: str, row: str) -> str:
        """[已委托] 在审批流程表格末尾追加一行（向后兼容包装）"""
        return self._editor.append_to_approval_table(content, row)

    def _append_to_implementation_table(self, content: str, row: str) -> str:
        """[已委托] 在实施记录表格末尾追加一行（向后兼容包装）"""
        return self._editor.append_to_implementation_table(content, row)

    def _append_to_verification_table(self, content: str, row: str) -> str:
        """[已委托] 在验证表格末尾追加一行（向后兼容包装）"""
        return self._editor.append_to_verification_table(content, row)

    def _update_status_field(self, content: str, new_status: str) -> str:
        """[已委托] 更新 §3.4 变更状态字段（向后兼容包装）"""
        return self._editor.update_status_field(content, new_status)

    def _update_verification_conclusion(self, content: str, conclusion: str) -> str:
        """[已委托] 更新 §10.2 验证结论（向后兼容包装）"""
        return self._editor.update_verification_conclusion(content, conclusion)

    def _update_field(self, content: str, field: str, value: str) -> str:
        """[已委托] 根据字段名分发到对应的章节更新逻辑（向后兼容包装）"""
        return self._editor.update_field(content, field, value)

    def _update_text_block(self, content: str, label: str, value: str) -> str:
        """[已委托] 更新 §4 中的文本块（向后兼容包装）"""
        return self._editor._update_text_block(content, label, value)

    def _update_table_field(self, content: str, field_name: str, value: str) -> str:
        """[已委托] 更新 §3.4 表格中的字段值（向后兼容包装）"""
        return self._editor._update_table_field(content, field_name, value)

    def _check_transition_guards(
        self,
        cr: ChangeRequest,
        target_status: str,
        approver: str,
        comment: str,
    ) -> None:
        """[已委托] 检查流转门禁条件（向后兼容包装）"""
        self._guard.check(cr, target_status, approver, comment)

    @staticmethod
    def _render_urgency_value(urgency: str) -> str:
        """[已委托] 渲染紧急程度为 ☑/□ 格式（向后兼容包装）"""
        return ChangeMarkdownEditor.render_urgency_value(urgency)

    # 保留旧类属性以兼容外部引用
    _CHANGE_FILE_SEARCH_PATHS = ChangeFileLocator.CHANGE_FILE_SEARCH_PATHS
