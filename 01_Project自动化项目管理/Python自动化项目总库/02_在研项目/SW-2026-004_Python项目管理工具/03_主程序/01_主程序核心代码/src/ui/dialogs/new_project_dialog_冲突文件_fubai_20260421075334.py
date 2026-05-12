# -*- coding: utf-8 -*-
"""
新建项目对话框
"""
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QTextEdit, QPushButton,
    QFileDialog, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt

from src.services.project_service import ProjectService
from src.services.template_service import TemplateService
from src.services.library_service import LibraryService
from src.core.constants import BusinessLine, BUSINESS_LINE_DESC, BUSINESS_LINE_TEMPLATES
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class NewProjectDialog(QDialog):
    """新建项目对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建项目")
        self.setMinimumSize(500, 400)
        self.setWindowModality(Qt.WindowModal)
        
        self.templates = []
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # 业务线
        self.business_line_combo = QComboBox()
        for bl in BusinessLine:
            self.business_line_combo.addItem(BUSINESS_LINE_DESC[bl], bl.value)
        self.business_line_combo.currentIndexChanged.connect(self._on_business_line_changed)
        form_layout.addRow("业务线:", self.business_line_combo)
        
        # 项目编号
        self.code_input = QLineEdit()
        self.code_input.setReadOnly(True)
        form_layout.addRow("项目编号:", self.code_input)
        
        # 项目名称
        self.name_input = QLineEdit()
        self.name_input.textChanged.connect(self._generate_project_code)
        form_layout.addRow("项目名称:", self.name_input)
        
        # 项目模板
        self.template_combo = QComboBox()
        form_layout.addRow("项目模板:", self.template_combo)
        
        # 所属总库选择
        self.lib_combo = QComboBox()
        self.lib_combo.setMinimumWidth(200)
        self.lib_combo.currentIndexChanged.connect(self._on_library_changed)
        form_layout.addRow("所属总库:", self.lib_combo)
        
        # 负责人
        self.manager_input = QLineEdit()
        form_layout.addRow("负责人:", self.manager_input)
        
        # 项目描述
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("项目描述:", self.description_input)
        
        # 项目路径
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(browse_btn)
        form_layout.addRow("项目路径:", path_layout)
        
        layout.addLayout(form_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.create_btn = QPushButton("创建")
        self.create_btn.clicked.connect(self._on_create)
        self.create_btn.setDefault(True)
        btn_layout.addWidget(self.create_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_data(self):
        """加载模板数据"""
        try:
            self.templates = TemplateService.list_templates()
        except Exception as e:
            logger.exception(f"加载模板列表失败: {e}")
            self.templates = []
            QMessageBox.warning(self, "警告", f"加载模板列表失败，将使用空列表: {str(e)}")

        self._update_template_combo()
        self._generate_project_code()

        try:
            libraries, _ = LibraryService.list_libraries()
        except Exception as e:
            logger.exception(f"加载总库列表失败: {e}")
            libraries = []
            QMessageBox.warning(self, "警告", f"加载总库列表失败: {str(e)}")

        self.lib_combo.addItem("(不关联总库)", "")
        for lib in libraries:
            self.lib_combo.addItem(lib.name, lib.library_id)
        default_idx = None
        for i in range(1, self.lib_combo.count()):
            if self.lib_combo.itemText(i) == "Python自动化项目总库":
                default_idx = i
                break
        if default_idx is not None:
            self.lib_combo.setCurrentIndex(default_idx)

        self._update_default_path()
    
    def _on_business_line_changed(self):
        """业务线变更时更新模板列表"""
        self._generate_project_code()
        self._update_template_combo()
    
    def _update_template_combo(self):
        """根据业务线更新模板下拉框"""
        business_line = self.business_line_combo.currentData()
        self.template_combo.clear()
        
        recommended_ids = BUSINESS_LINE_TEMPLATES.get(business_line, [])
        
        recommended_templates = []
        other_templates = []
        
        for template in self.templates:
            if template.template_id in recommended_ids:
                recommended_templates.append(template)
            else:
                other_templates.append(template)
        
        for template in recommended_templates:
            self.template_combo.addItem(f"★ {template.name} ({template.version}) [推荐]", template.template_id)
        
        if recommended_templates and other_templates:
            self.template_combo.insertSeparator(len(recommended_templates))
        
        for template in other_templates:
            self.template_combo.addItem(f"{template.name} ({template.version})", template.template_id)
    
    def _on_library_changed(self, index):
        """总库选择变更时自动更新项目路径到该总库目录下"""
        self._update_default_path()
    
    def _generate_project_code(self):
        """生成项目编号"""
        try:
            business_line = self.business_line_combo.currentData()
            if business_line:
                code, _ = ProjectService.generate_project_code(business_line)
                self.code_input.setText(code)
        except Exception as e:
            logger.exception(f"生成项目编号失败: {e}")
        self._update_default_path()

    def _update_default_path(self):
        """根据总库、编号、名称自动生成项目路径（带跨机器兼容性验证）

        优先级链路:
            优先级 1 (最高): Config.get_resolved_project_path() → {exe_dir}/Projects
            优先级 2 (回退):  总库 root_path (仅当不含盘符时使用)
            优先级 3 (回退):  自动检测 → 必须以 exe_dir 为基准
            优先级 4 (兜底):  exe_dir/Projects (硬兜底)
        """
        import sys
        from pathlib import Path

        try:
            lib_id = self.lib_combo.currentData()
            code = self.code_input.text().strip()
            name = self.name_input.text().strip() or "未命名项目"

            if not code:
                return

            base_path = ""
            path_source = ""  # 记录路径来源，用于日志

            # ============================================================
            # 优先级 1: Config 延迟安全导入（PyInstaller 兼容）
            # ============================================================
            try:
                from src.core.config import Config
                configured_path = Config.get_resolved_project_path()
                if configured_path:
                    base_path = configured_path
                    path_source = "配置文件(default_project_path)"
                    logger.info(f"使用配置文件的项目基础路径: {configured_path}")
            except ImportError as import_err:
                # PyInstaller 冻结环境下模块可能不存在，静默跳过
                logger.debug(f"Config 模块导入失败(可能是冻结环境)，回退: {import_err}")
            except Exception as config_err:
                # 其他异常也安全处理
                logger.debug(f"读取配置路径失败，回退到下一优先级: {config_err}")

            # ============================================================
            # 优先级 2: 总库 root_path（仅当不含盘符时使用）
            # ============================================================
            if not base_path and lib_id:
                try:
                    lib = LibraryService.get_library(lib_id)
                    if lib and lib.root_path:
                        # 安全检查：如果包含盘符标记(:)，说明是旧绝对路径，不可信，必须跳过
                        if ":" in lib.root_path:
                            logger.warning(
                                f"跳过总库root_path(含盘符，疑似旧绝对路径): {lib.root_path}"
                            )
                        else:
                            # 验证 root_path 是否有效且可写
                            lib_path = Path(lib.root_path)
                            if lib_path.exists() and lib_path.is_dir():
                                try:
                                    test_file = lib_path / ".write_test_tmp"
                                    test_file.touch()
                                    test_file.unlink()
                                    base_path = lib.root_path
                                    path_source = "总库root_path(回退,相对路径)"
                                except Exception as write_err:
                                    logger.warning(f"总库root_path不可写: {write_err}")
                            else:
                                path_source = "总库root_path(无效)"
                except Exception as e:
                    logger.exception(f"获取总库路径失败: {e}")

            # ============================================================
            # 优先级 3: 自动检测（必须以 exe_dir 为基准）
            # ============================================================
            if not base_path:
                try:
                    detected = LibraryService._detect_project_base_path()
                    if detected:
                        # 确保检测到的路径不以 cwd 为基准（开发/部署一致性）
                        base_path = detected
                        path_source = "自动检测路径(回退)"
                except Exception as detect_err:
                    logger.exception(f"自动检测路径失败: {detect_err}")

            # ============================================================
            # 优先级 4: 硬兜底 → exe_dir/Projects（替代 os.getcwd()）
            # ============================================================
            if not base_path:
                try:
                    # 获取可执行文件所在目录（兼容 PyInstaller 冻结环境和开发环境）
                    if getattr(sys, 'frozen', False):
                        # PyInstaller 冻结环境：sys.executable 指向 exe 文件
                        exe_dir = Path(sys.executable).parent
                    else:
                        # 开发环境：使用当前文件所在项目的上级目录
                        exe_dir = Path.cwd().parent

                    fallback_path = exe_dir / "Projects"
                    base_path = str(fallback_path)
                    path_source = f"exe_dir/Projects(硬兜底, exe_dir={exe_dir})"
                    logger.info(f"使用硬兜底路径: {base_path}")
                except Exception as fallback_err:
                    logger.exception(f"构建兜底路径失败，最终降级到cwd: {fallback_err}")
                    base_path = os.getcwd()
                    path_source = "os.getcwd()(最终降级)"

            if base_path:
                project_dir = f"{code}_{name}"
                full_path = os.path.join(base_path, project_dir)
                self.path_input.setText(full_path)
        except Exception as e:
            logger.exception(f"更新默认路径失败: {e}")
    
    def _browse_path(self):
        """浏览项目路径"""
        path = QFileDialog.getExistingDirectory(self, "选择项目保存目录")
        if path:
            # 生成默认路径
            name = self.name_input.text().strip() or "未命名项目"
            code = self.code_input.text()
            project_dir = f"{code}_{name}"
            full_path = os.path.join(path, project_dir)
            self.path_input.setText(full_path)
    
    def _on_create(self):
        """创建项目"""
        business_line = self.business_line_combo.currentData()
        name = self.name_input.text().strip()
        template_id = self.template_combo.currentData()
        manager = self.manager_input.text().strip()
        description = self.description_input.toPlainText().strip()
        custom_path = self.path_input.text().strip()
        library_id = self.lib_combo.currentData()  # 获取当前选中项的 data (library_id)

        # 验证自定义路径的有效性（跨机器兼容性检查）
        if custom_path:
            from pathlib import Path
            custom_path_obj = Path(custom_path)

            # 检查驱动器是否存在（Windows 特有问题）
            if custom_path_obj.drive and not custom_path_obj.is_absolute():
                reply = QMessageBox.warning(
                    self,
                    "路径警告",
                    f"项目路径可能无效:\n{custom_path}\n\n"
                    "该路径看起来不是绝对路径。\n"
                    "系统将尝试自动修正为有效路径。\n\n"
                    "是否继续？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply == QMessageBox.No:
                    return

            # 检查父目录是否存在
            parent_dir = custom_path_obj.parent
            if parent_dir and not parent_dir.exists():
                logger.warning(f"项目路径的父目录不存在: {parent_dir}")
                # 不阻止用户，让 service 层处理回退

        # 验证输入（保持原有逻辑不变）
        if not name:
            QMessageBox.warning(self, "警告", "项目名称不能为空")
            self.name_input.setFocus()
            return
        
        if not template_id:
            QMessageBox.warning(self, "警告", "请选择项目模板")
            self.template_combo.setFocus()
            return
        
        # 创建项目
        project, error = ProjectService.create_project(
            business_line=business_line,
            name=name,
            template_id=template_id,
            manager=manager,
            description=description,
            custom_path=custom_path if custom_path else None,
            library_id=library_id
        )
        
        if error:
            QMessageBox.critical(self, "错误", f"创建项目失败: {error}")
            return
        
        QMessageBox.information(self, "成功", f"项目创建成功!\n项目编号: {project.code}\n项目路径: {project.path}")
        self.accept()
    
    def get_project(self):
        """获取创建的项目（在accept后调用）"""
        # 这里可以返回最新创建的项目
        projects, _ = ProjectService.list_projects(page=1, size=1)
        return projects[0] if projects else None
