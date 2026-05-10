# Widget 层接口说明

## 模块概述

Widget层包含所有可复用的UI组件控件，是构建界面的基础积木。每个Widget封装了特定的UI功能和交互逻辑。

**设计目标**:
- 高内聚: 每个Widget只负责一个明确的UI功能
- 低耦合: Widget之间通过EventBus或回调函数通信
- 可复用: 支持在不同场景下组合使用
- 可测试: 独立的Widget可单独进行单元测试

---

## 模块结构

```
src/ui/widgets/
├── __init__.py             # 模块初始化
├── project_tree.py         # 项目浏览器树形视图 ⭐ (已实现)
├── document_editor.py      # 文档编辑器 (TODO Phase 1)
├── st_editor.py            # ST代码编辑器 (TODO Phase 2)
├── variable_checker.py     # 变量检查器 (TODO Phase 2)
├── io_table.py             # IO分配表 (TODO Phase 2)
└── hmi_mapper.py           # HMI映射工具 (TODO Phase 4)
```

---

## 公共API列表

### 1. ProjectTreeWidget (项目浏览器树形视图) ⭐

**文件**: `project_tree.py`
**状态**: ✅ 已实现 (Phase 0)

```python
class ProjectTreeWidget(QWidget):
    """
    项目浏览器树形视图
    
    功能:
    - 展示当前打开项目的目录结构
    - 以图标区分不同类型的节点 (文件夹/文档/代码)
    - 支持双击打开文档
    - 右键菜单支持新建/删除/重命名等操作
    - 与主窗口TabWidget联动切换内容区
    """
    
    def __init__(self, parent=None):
        """
        初始化树形视图
        
        Args:
            parent: 父QWidget
        """
    
    def load_project(self, project):
        """
        加载并显示项目目录结构
        
        Args:
            project: Project对象 (来自ProjectService)
                     必须有 .name 和 .path 属性
        """
    
    @property
    def current_project(self):
        """
        获取当前加载的项目对象
        
        Returns:
            Project | None: 当前项目或None
        """
    
    # ===== 私有方法 (内部实现) =====
    
    def _show_empty_state(self): ...                    # 显示空状态
    def _on_item_double_clicked(self, item, column): ... # 双击事件
    def _on_context_menu(self, position): ...            # 右键菜单
    def _on_new_document(self, item): ...               # 新建文档
    def _refresh_tree(self, item): ...                  # 刷新节点
    def _expand_all(self, item): ...                    # 展开全部
    def _collapse_all(self, item): ...                  # 折叠全部
```

#### 使用示例

```python
from src.ui.widgets.project_tree import ProjectTreeWidget
from src.services.project_service import ProjectService

# 创建组件
tree_widget = ProjectTreeWidget(parent=main_window)
layout.addWidget(tree_widget)

# 加载项目
project, error = ProjectService.load_project_from_path("./Projects/DJ-2026-006_示例")
if project:
    tree_widget.load_project(project)

# 获取当前项目
current = tree_widget.current_project
```

#### 标准节点类型

| 图标 | 类型标识 | 说明 |
|------|----------|------|
| 📁 | `folder` | 目录节点 |
| 📄 | `document` | 文档节点 |
| 💻 | `code` | 代码节点 |

#### 右键菜单功能

- 新建文档...
- 刷新
- ---
- 展开全部
- 折叠全部

---

### 2. DocumentEditor (文档编辑器)

**文件**: `document_editor.py`
**状态**: 🔨 TODO (Phase 1 实现)

```python
class DocumentEditor(QWidget):
    """
    Markdown文档编辑器
    
    功能 (规划):
    - Markdown实时预览 (分屏模式)
    - 工具栏 (加粗/斜体/标题/列表/表格等)
    - 模板插入 (基于DocumentTemplate)
    - 自动保存
    - 语法高亮
    """
    
    def __init__(self, parent=None): ...
    
    def open_document(self, file_path: str): ...
    def save_document(self): ...
    def get_content(self) -> str: ...
    def set_content(self, content: str): ...
    def is_modified(self) -> bool: ...
```

---

### 3. STEditor (ST代码编辑器)

**文件**: `st_editor.py`
**状态**: 🔄 增强中（QScintilla缺失时自动回退并给出安装引导）

```python
class STEditor(QWidget):
    """
    ST (Structured Text) 代码编辑器
    
    功能 (规划):
    - 语法高亮 (IEC 61131-3关键字)
    - 自动补全 (变量名/FB实例)
    - 代码折叠
    - 行号显示
    - 错误标记 (集成VariableChecker)
    """
    
    def __init__(self, parent=None, show_dependency_notice: bool = True): ...
    
    def get_text(self) -> str: ...
    def set_text(self, code: str): ...
    @property
    def has_full_features(self) -> bool: ...
```

---

### 4. VariableChecker (变量检查器)

**文件**: `variable_checker.py`
**状态**: 🔨 TODO (Phase 2 实现)

```python
class VariableChecker(QWidget):
    """
    变量检查面板
    
    功能 (规划):
    - 显示变量检查结果列表
    - 错误/警告分类统计
    - 点击跳转到ST编辑器对应行
    - 导出检查报告
    """
    
    def __init__(self, parent=None): ...
    
    def run_check(self, st_files: list[str]): ...
    def clear_results(self): ...
    def get_statistics(self) -> dict: ...
```

---

### 5. IOTable (IO分配表)

**文件**: `io_table.py`
**状态**: 🔨 TODO (Phase 2 实现)

```python
class IOTable(QWidget):
    """
    IO地址分配表编辑器
    
    功能 (规划):
    - 表格化编辑IO点
    - 地址冲突检测
    - 导入/导出CSV/Excel
    - 类型筛选 (DI/DO/AI/AO)
    """
    
    def __init__(self, parent=None): ...
    
    def load_from_project(self, project_path: str): ...
    def add_io_point(self, io_data: dict): ...
    def validate_addresses(self) -> list: ...
    def export_to_csv(self, file_path: str): ...
```

---

### 6. HMIMapper (HMI变量映射)

**文件**: `hmi_mapper.py`
**状态**: 🔨 TODO (Phase 4 实现)

```python
class HMIMapper(QWidget):
    """
    HMI变量映射配置工具
    
    功能 (规划):
    - PLC变量 <-> HMI控件的映射关系
    - 拖拽式绑定
    - 数据类型转换规则
    - 报警关联配置
    """
    
    def __init__(self, parent=None): ...
    
    def load_plc_variables(self, var_list: list): ...
    def create_mapping(self, plc_var, hmi_control): ...
    def export_mapping(self, format: str): ...
```

---

## 依赖关系

### 上游依赖 (导入的模块)

| 模块 | 用途 |
|------|------|
| `PyQt5.QtWidgets` | Qt基础控件 |
| `PyQt5.QtCore` | Qt核心 (Qt, Signal等) |
| `src.core.event_bus.EventBus` | 事件总线 (可选) |
| `src.models.*` | 数据模型 |
| `src.services.*` | 业务服务 (按需导入) |
| `src.utils.logger` | 日志记录 |

### 下游依赖 (使用本层的模块)

| 模块 | 用途 |
|------|------|
| `src.ui.main_window.MainWindow` | 主窗口组装 |
| `src.ui.dashboard.DashboardPage` | 仪表盘页面 |
| `src.ui.dialogs.*` | 对话框嵌入 |

---

## 设计规范

### 1. 命名规范

- **类名**: PascalCase (如 `ProjectTreeWidget`)
- **私有方法**: 下划线前缀 (如 `_on_click`)
- **信号槽**: `_on_` 前缀 (如 `_on_item_selected`)
- **属性**: `@property` 装饰器 (如 `current_project`)

### 2. 尺寸规范

- **最小宽度**: 控件应设置合理的 minimum size
- **弹性布局**: 使用 Layout + StretchFactor 实现自适应
- **字体大小**: 
  - 标题: 12pt bold
  - 正文: 10pt
  - 辅助文字: 9pt
  - 提示文字: 8pt

### 3. 样式规范

- **颜色主题**: 使用Material Design色板
  - Primary: #1976D2 (蓝色)
  - Success: #4CAF50 (绿色)
  - Warning: #FFC107 (黄色)
  - Error: #F44336 (红色)
- **圆角**: 4px - 8px
- **间距**: 8px / 12px / 16px (倍数递增)

### 4. 交互规范

- **鼠标样式**: 可点击元素使用 `PointingHandCursor`
- **Tooltip**: 所有可能性操作添加 StatusTip
- **快捷键**: 重要功能提供键盘快捷键
- **状态反馈**: 操作完成后更新状态栏或显示提示

---

## EventBus 信号交互

### Widget 发射的信号

| Widget | 信号 | 参数 | 说明 |
|--------|------|------|------|
| ProjectTreeWidget | (自定义Signal) | 节点数据 | 双击打开文档时 |
| DocumentEditor | (自定义Signal) | 文档路径 | 文档保存成功时 |
| VariableChecker | (自定义Signal) | 检查结果 | 检查完成时 |

### Widget 监听的信号

| Widget | 监听信号 | 响应动作 |
|--------|----------|----------|
| ProjectTreeWidget | `project_created` | 刷新项目树 |
| DocumentEditor | `document_open_request` | 打开指定文档 |
| VariableChecker | `variable_check_request` | 开始检查 |

---

## 扩展指南

### 创建新的Widget

1. **创建文件**: `src/ui/widgets/new_widget.py`
2. **继承基类**: 通常继承 `QWidget` 或更具体的Qt控件
3. **实现标准接口**:
   ```python
   class NewWidget(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self._init_ui()
       
       def _init_ui(self):
           # 构建UI布局
           pass
       
       # 公共方法
       def load_data(self, data): ...
       def clear(self): ...
       def refresh(self): ...
   ```
4. **注册到__init__.py** (可选)
5. **编写单元测试**
6. **更新本文档**

### Widget组合模式

复杂界面可通过组合多个简单Widget实现:

```python
class ComplexPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 组合多个子Widget
        self.tree = ProjectTreeWidget(self)
        self.editor = DocumentEditor(self)
        self.checker = VariableChecker(self)
        
        # 布局组装
        layout = QHBoxLayout(self)
        layout.addWidget(self.tree, stretch=1)
        layout.addWidget(self.editor, stretch=2)
```

---

## 测试要求

每个Widget应包含以下测试:

1. **UI渲染测试**: 验证正常显示无崩溃
2. **数据加载测试**: 验证load_xxx方法正确性
3. **用户交互测试**: 模拟点击/输入操作
4. **边界条件测试**: 空数据/大数据量/特殊字符
5. **性能测试**: 大数据量下的响应时间

测试框架: `pytest` + `pytest-qt` (Qt测试扩展)

---

## 注意事项

1. **父窗口传递**: 所有Widget必须接受 `parent` 参数以支持内存管理
2. **线程安全**: UI操作必须在主线程，后台任务使用 QThread
3. **资源释放**: 重写 `closeEvent` 清理资源 (如文件句柄、网络连接)
4. **国际化**: 用户可见文本支持多语言 (i18n)，使用 tr() 包装
5. **可访问性**: 为屏幕阅读器设置 accessibleName/description

---

## 版本历史

- **v1.0.0** (Phase 0): 初始版本
  - ✅ ProjectTreeWidget: 基础实现完成
  - 🔨 其他Widget: 规划中 (Phase 1-4)
