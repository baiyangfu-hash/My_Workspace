"""UI 对话框层

项目 CRUD 对话框（V2.0 阶段 E）：
- NewProjectDialog: 新建项目（调用 Copier 模板生成骨架）
- EditProjectDialog: 编辑项目元数据（阶段/版本/描述）
- DeleteProjectDialog: 删除项目（带二次确认）
- ImportProjectDialog: 导入已有项目目录到工作空间

变更管理对话框：
- CreateChangeDialog: 创建变更单（调用 ChangeService.create_change_request）
- TransitionDialog: 状态流转确认（调用 ChangeService.transition_status）
"""

from auto_pm.ui.dialogs.create_change_dialog import CreateChangeDialog
from auto_pm.ui.dialogs.delete_project_dialog import DeleteProjectDialog
from auto_pm.ui.dialogs.edit_project_dialog import EditProjectDialog
from auto_pm.ui.dialogs.import_project_dialog import ImportProjectDialog
from auto_pm.ui.dialogs.new_project_dialog import NewProjectDialog
from auto_pm.ui.dialogs.transition_dialog import TransitionDialog

__all__ = [
    "NewProjectDialog",
    "EditProjectDialog",
    "DeleteProjectDialog",
    "ImportProjectDialog",
    "CreateChangeDialog",
    "TransitionDialog",
]
