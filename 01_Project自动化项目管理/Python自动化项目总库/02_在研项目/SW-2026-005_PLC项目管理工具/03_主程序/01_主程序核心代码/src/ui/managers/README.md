# UI Managers 模块接口说明

## 模块概述

UI Managers模块负责将MainWindow中的UI构建逻辑抽取为独立的管理器类，实现UI层的职责分离和代码复用。

**创建时间**: Phase 0 架构重构
**设计模式**: 委托模式 + 事件驱动

---

## 模块结构

```
src/ui/managers/
├── __init__.py           # 模块初始化文件
├── menu_manager.py       # 菜单管理器 (核心)
└── toolbar_manager.py    # 工具栏管理器 (核心)
```

---

## 公共API列表

### 1. MenuManager (菜单管理器)

**文件**: `menu_manager.py`

#### 类: MenuManager

```python
class MenuManager:
    """菜单管理器 - 负责构建和管理所有菜单项"""
    
    def __init__(self, parent: QMainWindow, event_bus: EventBus):
        """
        初始化菜单管理器
        
        Args:
            parent: 主窗口实例 (QMainWindow)
            event_bus: 全局事件总线实例
        """
    
    def build(self) -> QMenuBar:
        """
        构建完整菜单栏并返回
        
        Returns:
            QMenuBar: 构建完成的菜单栏对象
        
        菜单结构:
            文件(F): 新建/打开/最近项目/保存/设置/退出
            编辑(E): 撤销/重做/查找/替换
            工具(T): 规范检查/变量检查/生成报告
            视图(V): 主题(浅色/深色)
            帮助(H): 关于
        """
    
    # ===== 内部方法 (私有) =====
    
    def _create_file_menu(self) -> QMenu: ...
    def _create_edit_menu(self) -> QMenu: ...
    def _create_tools_menu(self) -> QMenu: ...
    def _create_view_menu(self) -> QMenu: ...
    def _create_help_menu(self) -> QMenu: ...
    
    # ===== 事件处理方法 =====
    
    def _on_new_project(self): ...         # 新建项目
    def _on_open_project(self): ...        # 打开项目
    def _on_save(self): ...                # 保存
    def _on_settings(self): ...            # 打开设置对话框
    def _on_run_check(self): ...           # 规范检查
    def _on_variable_check(self): ...      # 变量检查
    def _on_generate_report(self): ...     # 生成报告
    def _switch_theme(self, theme_name): ...  # 切换主题
    def _on_about(self): ...               # 显示关于
    
    # ===== 辅助方法 =====
    
    def _refresh_recent_projects(self): ...   # 刷新最近项目列表
    def _open_recent_project(self, path): ... # 打开最近项目
    def _clear_recent_projects(self): ...     # 清除历史记录
    def _fallback_settings(self): ...         # 回退内联设置(兼容性)
```

#### 使用示例

```python
from src.ui.managers.menu_manager import MenuManager
from src.core.event_bus import EventBus

# 获取EventBus单例
event_bus = EventBus.get_instance()

# 创建菜单管理器
menu_manager = MenuManager(main_window, event_bus)

# 构建菜单栏
menu_bar = menu_manager.build()
```

---

### 2. ToolBarManager (工具栏管理器)

**文件**: `toolbar_manager.py`

#### 类: ToolBarManager

```python
class ToolBarManager:
    """工具栏管理器 - 负责构建和管理主工具栏"""
    
    def __init__(self, parent: QMainWindow, event_bus: EventBus):
        """
        初始化工具栏管理器
        
        Args:
            parent: 主窗口实例 (QMainWindow)
            event_bus: 全局事件总线实例
        """
    
    def build(self) -> QToolBar:
        """
        构建工具栏并添加到主窗口
        
        工具栏按钮顺序:
            1. 新建项目
            2. 打开项目
            ---
            3. 保存
            ---
            4. 规范检查
        
        Returns:
            QToolBar: 构建完成的工具栏对象
        """
    
    def set_icon_size(self, size: QSize):
        """
        设置工具栏图标大小
        
        Args:
            size: 图标尺寸 (宽, 高)
        """
    
    # ===== 事件处理方法 =====
    
    def _on_new_project(self): ...    # 委托给MenuManager
    def _on_open_project(self): ...   # 委托给MenuManager
    def _on_save(self): ...           # 更新状态栏
    def _on_run_check(self): ...      # 发射EventBus信号
```

#### 使用示例

```python
from src.ui.managers.toolbar_manager import ToolBarManager
from src.core.event_bus import EventBus
from PyQt5.QtCore import QSize

# 获取EventBus单例
event_bus = EventBus.get_instance()

# 创建工具栏管理器
toolbar_manager = ToolBarManager(main_window, event_bus)

# 可选: 自定义图标大小
toolbar_manager.set_icon_size(QSize(24, 24))

# 构建工具栏
toolbar = toolbar_manager.build()
```

---

## 依赖关系

### 上游依赖 (导入的模块)

| 模块 | 用途 |
|------|------|
| `PyQt5.QtWidgets` | Qt界面组件基类 |
| `PyQt5.QtCore` | Qt核心功能 (QSize, Qt) |
| `PyQt5.QtGui` | QIcon图标类 |
| `src.core.event_bus.EventBus` | 全局事件总线 |
| `src.core.constants` | APP_NAME, VERSION常量 |
| `src.core.config.ConfigLoader` | 配置加载器 |
| `src.core.settings.SettingsManager` | 用户设置管理 |
| `src.utils.logger.setup_logger` | 日志初始化 |

### 下游依赖 (被使用的模块)

| 模块 | 用途 |
|------|------|
| `src.ui.dialogs.new_project_dialog` | 新建项目向导 (按需导入) |
| `src.ui.dialogs.settings_dialog` | 设置对话框 (按需导入) |
| `src.ui.main_window.MainWindow` | 父窗口 (通过构造函数注入) |

---

## EventBus 信号交互

### MenuManager 发射的信号

| 信号名 | 参数 | 触发时机 |
|--------|------|----------|
| `project_created` | `str` (项目路径) | 新建项目成功后 |
| `project_opened` | `str` (项目路径) | 打开项目成功后 |
| `spec_check_request` | `dict` (配置) | 点击规范检查时 |
| `variable_check_request` | 无参数 | 点击变量检查时 |
| `theme_changed` | `str` ('light'\|'dark') | 切换主题时 |
| `settings_changed` | 无参数 | 设置保存成功后 |

### MenuManager 监听的信号

当前版本未监听外部信号（后续Phase可扩展）

### ToolBarManager 发射的信号

| 信号名 | 参数 | 触发时机 |
|--------|------|----------|
| `spec_check_request` | `dict` ({}) | 点击规范检查按钮时 |

---

## 设计原则

### 1. 单一职责原则 (SRP)
- **MenuManager**: 只负责菜单的创建、管理和事件处理
- **ToolBarManager**: 只负责工具栏的创建和管理
- 不包含业务逻辑，只负责UI层面的事件转发

### 2. 依赖倒置原则 (DIP)
- 通过构造函数注入 `parent` 和 `event_bus`
- 不直接依赖具体的Service层，而是通过EventBus间接通信
- 支持单元测试时的Mock替换

### 3. 开闭原则 (OCP)
- 对扩展开放: 可以通过继承添加新的菜单项或工具栏按钮
- 对修改关闭: 核心构建逻辑稳定，不需要频繁修改

### 4. 接口隔离原则 (ISP)
- 提供清晰的公共API (`build()` 方法)
- 内部实现细节封装为私有方法

---

## 扩展指南

### 添加新菜单项

```python
# 在 MenuManager._create_xxx_menu() 中添加
new_action = QAction("新功能", self._parent)
new_action.setShortcut("Ctrl+Shift+N")
new_action.triggered.connect(self._on_new_feature)
menu.addAction(new_action)
```

### 添加新的EventBus信号

1. 在 `src/core/event_bus.py` 的 EventBus 类中定义新信号
2. 在需要的地方发射信号: `self._event_bus.new_signal.emit(data)`
3. 在监听者处连接槽函数: `bus.new_signal.connect(handler)`

### 自定义工具栏布局

```python
# 继承 ToolBarManager 并重写 build() 方法
class CustomToolBarManager(ToolBarManager):
    def build(self) -> QToolBar:
        toolbar = super().build()
        # 添加自定义按钮
        custom_btn = QAction("自定义", self._parent)
        toolbar.addAction(custom_btn)
        return toolbar
```

---

## 注意事项

1. **线程安全**: 所有UI操作必须在主线程执行，EventBus信号会自动在发射线程调用槽函数
2. **内存管理**: Manager的生命周期与MainWindow绑定，无需手动释放
3. **兼容性**: MenuManager内置了 `_fallback_settings()` 回退机制，防止SettingsDialog导入失败
4. **日志记录**: 所有关键操作都有日志输出，便于调试

---

## 版本历史

- **v1.0.0** (Phase 0): 初始版本
  - 从 main_window.py 提取菜单逻辑 (~100行)
  - 从 main_window.py 提取工具栏逻辑 (~30行)
  - 集成 EventBus 事件通信
  - 实现最近项目列表动态刷新
