# -*- coding: utf-8 -*-
"""
全局事件总线 - 模块间松耦合通信

使用单例模式的QObject，定义所有跨模块通信的信号。
UI层发射信号 -> EventBus广播 -> 各Manager/Panel响应

设计原则:
- 解耦UI组件间的直接依赖
- 统一事件命名规范
- 支持异步事件处理
- 线程安全的单例实现
"""
from PyQt5.QtCore import QObject, pyqtSignal
import threading


class EventBus(QObject):
    """
    全局事件总线 (单例模式)

    使用方式:
        from src.core.event_bus import EventBus
        bus = EventBus.get_instance()
        bus.project_selected.emit("/path/to/project")

    信号分类:
        - 项目事件: 项目创建/打开/选择
        - 文档事件: 文档打开/保存/新建
        - PLC/ST事件: ST文件操作/变量检查
        - IO事件: IO表管理
        - HMI事件: HMI映射工具
        - 规范事件: 规范检查请求
        - 系统事件: 主题切换/设置变更
    """
    _instance = None
    _lock = threading.Lock()

    # ===== 项目事件 =====
    project_selected = pyqtSignal(str)       # 参数: 项目路径
    project_created = pyqtSignal(str)        # 参数: 新建项目路径
    project_opened = pyqtSignal(str)         # 参数: 打开的项目路径

    # ===== 文档事件 =====
    document_open_request = pyqtSignal(str)  # 参数: 文档路径, 请求打开文档
    document_saved = pyqtSignal(str)         # 参数: 文档路径, 保存成功
    document_created = pyqtSignal(str)       # 参数: 文档路径, 新建成功

    # ===== PLC/ST事件 =====
    st_file_open_request = pyqtSignal(str)   # 参数: ST文件路径
    variable_check_request = pyqtSignal()    # 无参数, 触发变量检查面板
    fb_doc_generate_request = pyqtSignal(str)# 参数: ST文件路径

    # ===== IO事件 =====
    io_table_open_request = pyqtSignal()     # 无参数, 打开IO表管理

    # ===== HMI事件 =====
    hmi_mapper_open_request = pyqtSignal()   # 无参数, 打开映射工具

    # ===== 规范事件 =====
    spec_check_request = pyqtSignal(dict)    # 参数: 检查配置dict

    # ===== 系统事件 =====
    theme_changed = pyqtSignal(str)          # 参数: 'light' | 'dark'
    settings_changed = pyqtSignal()          # 设置已更改

    def __new__(cls):
        """单例模式 - 线程安全"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'EventBus':
        """
        获取全局单例

        Returns:
            EventBus: 全局唯一的事件总线实例
        """
        return cls()

    @classmethod
    def reset_instance(cls):
        """
        重置单例 (主要用于测试)

        Warning:
            生产环境不建议调用此方法
        """
        with cls._lock:
            cls._instance = None
