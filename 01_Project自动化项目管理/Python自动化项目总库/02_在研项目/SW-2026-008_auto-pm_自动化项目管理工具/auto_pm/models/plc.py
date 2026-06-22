"""PLC 检查与修复模型（迁移自 plc/models.py:dataclass）

常量（STD_DIRS/STD_PRDS/NAMING_RULES 等）仍保留在 plc/models.py。
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from auto_pm.models.enums import CheckStatus, DocType, ProjectType, RepairStatus


class CheckItem(BaseModel):
    """单条检查项"""

    item: str = Field(..., description="检查项名称")
    status: CheckStatus = Field(..., description="状态: pass/warn/fail")
    message: str = Field("", description="详细说明")

    model_config = ConfigDict()


class CheckResult(BaseModel):
    """结构检查结果"""

    project_path: str = Field(..., description="项目路径")
    project_type: ProjectType = Field("standard", description="项目类型: standard/syslib_fb")
    items: list[CheckItem] = Field(default_factory=list, description="检查项列表")
    pass_count: int = Field(0, description="通过数")
    warn_count: int = Field(0, description="警告数")
    fail_count: int = Field(0, description="失败数")

    model_config = ConfigDict()

    def add(self, item: str, status: str, message: str) -> None:
        """添加一条检查项并更新计数"""
        self.items.append(CheckItem(item=item, status=status, message=message))
        if status == "pass":
            self.pass_count += 1
        elif status == "warn":
            self.warn_count += 1
        else:
            self.fail_count += 1

    @property
    def all_pass(self) -> bool:
        """是否全部通过（无 fail）"""
        return self.fail_count == 0


class RepairAction(BaseModel):
    """单条修复动作"""

    item: str = Field(..., description="修复项名称")
    action: str = Field("", description="修复动作描述")
    destructive: bool = Field(False, description="是否破坏性操作")
    status: RepairStatus = Field(..., description="状态: fixed/skipped/failed")
    detail: str = Field("", description="详细说明")

    model_config = ConfigDict()


class RepairResult(BaseModel):
    """自动修复结果"""

    project_path: str = Field(..., description="项目路径")
    actions: list[RepairAction] = Field(default_factory=list, description="修复动作列表")
    fixed_count: int = Field(0, description="已修复数")
    skipped_count: int = Field(0, description="已跳过数")
    failed_count: int = Field(0, description="失败数")
    before_check: CheckResult | None = Field(None, description="修复前检查结果")
    after_check: CheckResult | None = Field(None, description="修复后检查结果")

    model_config = ConfigDict()

    def add(
        self, item: str, action: str, destructive: bool, status: str, detail: str
    ) -> None:
        """添加一条修复动作并更新计数"""
        self.actions.append(
            RepairAction(
                item=item, action=action, destructive=destructive, status=status, detail=detail
            )
        )
        if status == "fixed":
            self.fixed_count += 1
        elif status == "skipped":
            self.skipped_count += 1
        else:
            self.failed_count += 1


class RenamePlan(BaseModel):
    """文档重命名计划"""

    old_path: str = Field(..., description="原文件路径")
    new_path: str = Field(..., description="新文件路径")
    doc_type: DocType = Field(..., description="文档类型: REQ/INT/DSN/TEC")
    applied: bool = Field(False, description="是否已执行")
    backup_path: str = Field("", description="备份路径（.bak）")

    model_config = ConfigDict()


class StandardizeResult(BaseModel):
    """文档标准化结果"""

    project_path: str = Field(..., description="项目路径")
    plans: list[RenamePlan] = Field(default_factory=list, description="重命名计划列表")
    applied_count: int = Field(0, description="已应用数")
    skipped_count: int = Field(0, description="已跳过数")
    reference_updates: list[str] = Field(default_factory=list, description="引用更新列表")

    model_config = ConfigDict()
