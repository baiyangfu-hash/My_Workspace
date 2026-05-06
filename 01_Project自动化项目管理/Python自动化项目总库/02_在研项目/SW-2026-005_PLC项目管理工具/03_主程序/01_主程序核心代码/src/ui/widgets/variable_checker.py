# -*- coding: utf-8 -*-
"""
变量检查器组件 - 组合SpecCheckPanel的薄壳组件

将原有的模拟数据实现替换为真实的SpecCheckPanel组合，
保持类名VariableCheckerWidget不变，确保向后兼容。

设计模式：
- 组合模式：内部包含SpecCheckPanel实例
- 代理模式：转发信号和方法调用到SpecCheckPanel
- 薄壳设计：本类只负责组装，不包含业务逻辑

改进点：
- 移除所有模拟数据
- 使用真实检查引擎
- 支持项目级/文件级检查
- 集成结果可视化和源码跳转功能
"""
from typing import Optional

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PyQt5.QtCore import pyqtSignal

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class VariableCheckerWidget(QWidget):
    """
    变量检查器组件 (基于SpecCheckPanel的组合实现)

    功能:
    - 扫描ST源码中的所有变量声明
    - 检测重复变量定义 (同名不同作用域警告)
    - 数据类型使用一致性检查
    - 命名规范验证 (匈牙利命名法/前缀规范)
    - 未使用变量检测
    - 变量引用关系图展示

    Signals:
        check_started: 开始检查时发出（从SpecCheckPanel转发）
        check_finished: 检查完成时发出（从SpecCheckPanel转发）
        source_jump_requested: 用户请求跳转到源码位置时发出（从SpecCheckPanel转发）

    Usage:
        widget = VariableCheckerWidget()
        widget.start_check("/path/to/project")
    """

    # 转发SpecCheckPanel的信号
    check_started = pyqtSignal()
    check_finished = pyqtSignal(object)  # CheckReport
    source_jump_requested = pyqtSignal(str, int)  # 文件路径, 行号

    def __init__(self, parent=None):
        """
        初始化变量检查器组件

        Args:
            parent: 父窗口组件
        """
        super().__init__(parent)

        # 内部组合的SpecCheckPanel实例
        self._spec_check_panel = None

        # 初始化UI
        self._init_ui()

        logger.info("变量检查器组件初始化完成 (组合SpecCheckPanel)")

    def _init_ui(self):
        """初始化UI布局 - 组合SpecCheckPanel"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        try:
            # 导入并创建SpecCheckPanel实例
            from src.ui.widgets.spec_check_panel import SpecCheckPanel

            self._spec_check_panel = SpecCheckPanel(self)

            # 连接信号转发
            self._spec_check_panel.check_started.connect(
                self.check_started.emit
            )
            self._spec_check_panel.check_finished.connect(
                self.check_finished.emit
            )
            self._spec_check_panel.source_jump_requested.connect(
                self.source_jump_requested.emit
            )

            # 添加到布局
            layout.addWidget(self._spec_check_panel)

            logger.info("SpecCheckPanel已成功组合")

        except ImportError as e:
            logger.error(f"无法导入SpecCheckPanel: {e}")
            # 显示错误提示
            from PyQt5.QtWidgets import QLabel
            error_label = QLabel(
                f"\u274C \u65E0\u6CD5\u52A0\u8F7D\u89C4\u8303\u68C0\u67E5\u9762\u677F\n\n"
                f"\u9519\u8BEF\u4FE1\u606F: {str(e)}"
            )
            error_label.setAlignment(
                __import__(
                    'PyQt5.QtCore', fromlist=['Qt']
                ).Qt.AlignCenter
            )
            error_label.setStyleSheet(
                "color: #C62828; font-size: 12pt; padding: 20px;"
            )
            layout.addWidget(error_label)

        except Exception as e:
            logger.exception(f"初始化SpecCheckPanel失败: {e}")
            raise

    # ===== 公共API方法（代理到SpecCheckPanel） =====

    def start_check(
        self,
        project_path: str,
        file_path: Optional[str] = None,
    ):
        """
        启动后台检查线程

        Args:
            project_path: 项目根目录路径
            file_path: 单文件检查路径（可选）
        """
        if self._spec_check_panel:
            self._spec_check_panel.start_check(project_path, file_path)
            logger.info(
                f"变量检查已启动 - "
                f"路径: {project_path}, "
                f"模式: {'单文件' if file_path else '全项目'}"
            )
        else:
            logger.error("SpecCheckPanel未初始化，无法执行检查")

    def on_check_finished(self, report):
        """
        检查完成回调（代理方法）

        Args:
            report: 检查报告对象
        """
        if self._spec_check_panel:
            self._spec_check_panel.on_check_finished(report)

    def get_current_report(self):
        """
        获取当前的检查报告（代理方法）

        Returns:
            CheckReport或None: 当前报告对象
        """
        if self._spec_check_panel:
            return self._spec_check_panel.get_current_report()
        return None

    def clear_all(self):
        """清空所有数据和UI状态（代理方法）"""
        if self._spec_check_panel:
            self._spec_check_panel.clear_all()
            logger.info("变量检查数据已清空")

    # ===== 向后兼容接口 =====

    def _on_scan(self):
        """
        执行变量扫描（向后兼容接口）

        注意：此方法保留用于兼容旧代码，
        新代码应直接调用 start_check() 方法
        """
        logger.warning("_on_scan() 是遗留接口，建议使用 start_check()")
        # 尝试触发检查（需要先设置项目路径）
        if self._spec_check_panel:
            # 这里可以添加默认项目路径的逻辑
            # 或者发出信号让外部提供路径
            pass
