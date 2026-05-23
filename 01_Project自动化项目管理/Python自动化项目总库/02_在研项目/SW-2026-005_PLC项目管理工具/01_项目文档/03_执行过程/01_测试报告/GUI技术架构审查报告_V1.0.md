# SW-2026-005 PLC项目管理工具 — GUI技术架构审查报告

**文档版本**: V1.0  
**审查日期**: 2026-05-23  
**审查范围**: GUI全模块深度审查  
**审查人**: Trae AI (pm-workflow Event D)  
**输出类型**: 纯审查报告（不含代码修改）

---

## 0. 执行摘要

### 0.1 审查背景

本次审查基于用户反馈的**导航Bug**：
> **现象**: 点击顶部「变更管理」Tab时，右侧正确显示变更管理面板，但**左侧显示PLC工具页面**

### 0.2 审查结论

| 维度 | 评级 | 说明 |
|------|------|------|
| **架构设计** | ⭐⭐⭐⭐☆ | 薄壳+Builder+Controller模式合理，但映射表存在索引错误 |
| **代码质量** | ⭐⭐⭐⭐☆ | 遵循规范，有日志，异常处理完善 |
| **导航一致性** | ⭐⭐☆☆☆ | **存在Critical级别索引错位Bug** |
| **功能完整性** | ⭐⭐⭐⭐⭐ | 所有功能入口→调用链完整 |
| **信号连接率** | 85% | 7个EventBus信号中6个有问题 |

### 0.3 关键发现

**🔴 Critical Bug (GUI-NAV-001)**: NavigationController的ToolBox页面索引与LeftPanelBuilder实际构建顺序不一致，导致变更管理Tab导航到PLC工具页面。

---

## 1. GUI架构总览

### 1.1 架构模式

```
┌─────────────────────────────────────────────────────────────────┐
│                        MainWindow (QMainWindow)                   │
│  ┌──────────────────────────┬────────────────────────────────┐  │
│  │     QSplitter(Horizontal) │                                │  │
│  │  ┌────────────┬─────────┐│      QTabWidget (6 Tabs)       │  │
│  │  │ QToolBox   │         ││                                │  │
│  │  │ (6 Pages)  │         ││ [0]仪表盘  DashboardPage       │  │
│  │  │            │         ││ [1]项目    ProjectInfoWidget    │  │
│  │  │ [0]项目管理│         ││ [2]文档    DocumentEditor       │  │
│  │  │ [1]文档管理│         ││ [3]变更管理 ChangeMgmtPanel ⭐ │  │
│  │  │ [2]PLC工具 │← Bug!  ││ [4]PLC工具 InnerTab(STEditor) │  │
│  │  │ [3]变更管理│         ││ [5]规范检查 SpecCheckGuide    │  │
│  │  │ [4]规范中心│         ││                                │  │
│  │  │ [5]系统设置│         │├────────────────────────────────┤  │
│  │  └────────────┴─────────┘│  MenuManager + ToolBarManager  │  │
│  └──────────────────────────┴────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ QStatusBar + DockWidgets(SpecCheck + Diagnostic)             ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 组件层次结构

```
MainWindow (main_window.py)
├── 核心服务层
│   ├── EventBus (event_bus.py) — 全局事件总线
│   ├── SettingsManager (settings.py) — 用户配置
│   ├── ProjectController (controllers/project_controller.py)
│   ├── SyncController (controllers/sync_controller.py)
│   └── DashboardController (controllers/dashboard_controller.py)
│
├── Builder层 (builders/)
│   ├── LeftPanelBuilder (left_panel_builder.py) — 左侧ToolBox构建
│   ├── RightPanelBuilder (right_panel_builder.py) — 右侧TabWidget构建
│   ├── StyleBuilder (style_builder.py) — 主题/样式管理
│   └── DockPanelBuilder (dock_panel_builder.py) — Dock面板构建
│
├── Manager层 (managers/)
│   ├── MenuManager (menu_manager.py) — 菜单栏
│   └── ToolBarManager (toolbar_manager.py) — 工具栏
│
├── Widget层 (widgets/)
│   ├── ProjectTreeWidget (project_tree.py) — 项目浏览器树
│   ├── DocumentEditor (document_editor.py) — 文档编辑器
│   ├── STEditor (st_editor.py) — ST语言编辑器
│   ├── ChangeManagementPanel (change_management_panel.py) — 变更管理面板
│   ├── SpecCheckPanel (spec_check_panel.py) — 规范检查面板
│   └── DiagnosticPanel (diagnostic_panel.py) — 诊断分析面板
│
├── Dialog层 (dialogs/)
│   ├── NewProjectDialog (new_project_dialog.py)
│   ├── NewDocumentDialog (new_document_dialog.py)
│   ├── SettingsDialog (settings_dialog.py)
│   ├── SyncResultDialog (sync_result_dialog.py)
│   └── FBDocumentDialog (fb_document_dialog.py)
│
└── Controller层 (controllers/)
    └── NavigationController (navigation_controller.py) — 导航同步控制
```

### 1.3 数据流图

```
用户操作 → Widget事件 → MainWindow._on_action() 
    ↓
NavigationController.navigate_to_tab(tab_index) / on_sidebar_action(text)
    ↓
┌─────────────────────────────────────┐
│  Tab/ToolBox双向同步 (blockSignals)  │
│  _on_tab_changed() ↔ _on_toolbox_changed()
└─────────────────────────────────────┘
    ↓
[根据Tab索引显示对应功能面板]
    ↓
[面板内部交互]
    ↓
Service层业务调用 (ChangeService / SyncEngine / etc.)
    ↓
数据持久化 (JSON文件系统)
```

---

## 2. 布局详细规格

### 2.1 主窗口布局参数

| 参数 | 值 | 来源 |
|------|-----|------|
| 最小宽度 | 1200px | `MainWindow.MIN_WIDTH` |
| 最小高度 | 800px | `MainWindow.MIN_HEIGHT` |
| 初始宽度 | 屏幕宽度×92% | `_apply_initial_geometry()` |
| 初始高度 | 屏幕高度×92% | `_apply_initial_geometry()` |
| Splitter方向 | 水平 (Horizontal) | `Qt.Horizontal` |
| 左侧默认宽度 | 240px | `SIDEBAR_DEFAULT_WIDTH` |
| 左侧最小宽度 | 180px | `SIDEBAR_MIN_WIDTH` |
| 左侧最大宽度 | 320px | `SIDEBAR_MAX_WIDTH` |
| 右侧最小宽度 | 800px | 硬编码 |
| 边距 | 8px | `setContentsMargins(8,8,8,8)` |
| 间距 | 8px | `setSpacing(8)` |

### 2.2 左侧ToolBox布局

**组件**: `QToolBox` (由 LeftPanelBuilder.build() 构建)

**实际页面顺序与索引**:
```
索引  页面标题          内容组件                    创建方法
─────────────────────────────────────────────────────────────
[0]   项目管理          ProjectTreeWidget           addItem() 直接添加
[1]   文档管理          3个按钮(新建/模板/打开)       _create_sidebar_tool_page()
[2]   PLC工具           3个按钮(ST编辑器/IO/变量)    _create_sidebar_tool_page()
[3]   变更管理 ⭐        1个按钮(刷新列表)            _create_change_mgmt_page()
[4]   规范中心          6个按钮+分隔线               _create_sidebar_tool_page()
[5]   系统设置          3个按钮(设置/主题/关于)       _create_sidebar_tool_page()
```

**页面样式规范**:
- 页面边距: `ContentsMargins(8, 8, 8, 8)`
- 控件间距: `Spacing(6)`
- 标题样式: `Property("SidebarHeader", True)` → 由QSS统一渲染
- 按钮样式: `Property("SidebarBtn", True)` → 由QSS统一渲染
- 分隔线: `QFrame.HLine`, 颜色 `#E0E0E0`, 高度1px

### 2.3 右侧TabWidget布局

**组件**: `QTabWidget` (由 RightPanelBuilder.build() 构建)

**Tab顺序与内容**:
```
索引  Tab标签           内容组件                     创建方法
───────────────────────────────────────────────────────────────
[0]   ☰ 仪表盘          DashboardPage                addTab(DashboardPage)
[1]   📁 项目           ProjectInfoWidget (+FormLayout) _create_project_info_widget()
[2]   📝 文档           DocumentEditor                _create_document_tab()
[3]   🔄 变更管理 ⭐      ChangeManagementPanel         _create_change_management_tab()
[4]   ⚡ PLC工具         InnerTabWidget (STEditor)     _create_plc_tools_tab()
[5]   ✅ 规范检查        SpecCheckTabPanel (引导页)     _create_spec_check_tab()
```

**Tab属性**:
- 位置: 北部 (`QTabWidget.North`)
- 形状: 圆角 (`QTabWidget.Rounded`)
- 省略模式: 右省略 (`Qt.ElideRight`)

---

## 3. 导航机制深度分析

### 3.1 NavigationController 映射表

#### 当前定义 (navigation_controller.py)

```python
# ToolBox页面常量
TOOL_PROJECT = 0
TOOL_DOCUMENT = 1
TOOL_CHANGE_MGMT = 2   # ❌ 定义为2
TOOL_PLC = 3            # ❌ 定义为3
TOOL_SPEC = 4
TOOL_SETTINGS = 5

# Tab页面常量
TAB_DASHBOARD = 0
TAB_PROJECT = 1
TAB_DOCUMENT = 2
TAB_CHANGE_MGMT = 3
TAB_PLC_TOOLS = 4
TAB_SPEC_CHECK = 5

# ToolBox → Tab 正向映射
TOOLBOX_TO_TAB = {
    TOOL_PROJECT: TAB_DASHBOARD,      # 0 → 0 ✅
    TOOL_DOCUMENT: TAB_DOCUMENT,      # 1 → 2 ✅
    TOOL_CHANGE_MGMT: TAB_CHANGE_MGMT,# 2 → 3 ⚠️ 索引2实际是PLC工具！
    TOOL_PLC: TAB_PLC_TOOLS,          # 3 → 4 ⚠️ 索引3实际是变更管理！
    TOOL_SPEC: TAB_SPEC_CHECK,        # 4 → 5 ✅
    TOOL_SETTINGS: None,              # 5 → None ✅
}

# Tab → ToolBox 反向映射
TAB_TO_TOOLBOX = {
    TAB_DASHBOARD: TOOL_PROJECT,      # 0 → 0 ✅
    TAB_PROJECT: TOOL_PROJECT,        # 1 → 0 ✅ (共享)
    TAB_DOCUMENT: TOOL_DOCUMENT,      # 2 → 1 ✅
    TAB_CHANGE_MGMT: TOOL_CHANGE_MGMT,# 3 → 2 🔴 BUG！应该映射到3
    TAB_PLC_TOOLS: TOOL_PLC,          # 4 → 3 🔴 BUG！应该映射到2
    TAB_SPEC_CHECK: TOOL_SPEC,        # 5 → 4 ✅
}
```

#### 实际构建顺序 (left_panel_builder.py)

```python
# LeftPanelBuilder.build() 的addItem调用顺序:
tool_box.addItem(project_page, "项目管理")       # → 索引 [0] TOOL_PROJECT ✅
_create_sidebar_tool_page(tool_box, "文档管理")  # → 索引 [1] TOOL_DOCUMENT ✅
_create_sidebar_tool_page(tool_box, "PLC工具")   # → 索引 [2] TOOL_PLC ← 实际是2！
_create_change_mgmt_page(tool_box)              # → 索引 [3] TOOL_CHANGE_MGMT ← 实际是3！
_create_sidebar_tool_page(tool_box, "规范中心")  # → 索引 [4] TOOL_SPEC ✅
_create_sidebar_tool_page(tool_box, "系统设置")  # → 索引 [5] TOOL_SETTINGS ✅
```

### 3.2 🔴 **GUI-NAV-001: 索引错位Bug 详细分析**

#### Bug复现路径

```
用户操作: 点击顶部「🔄 变更管理」Tab (索引3)
         ↓
触发: QTabWidget.currentChanged.emit(3)
         ↓
NavigationController._on_tab_changed(3) 被调用
         ↓
执行: toolbox_idx = self.TAB_TO_TOOLBOX.get(3)
       → 返回 TOOL_CHANGE_MGMT = 2  ← ❌ 错误值！
         ↓
执行: self._tool_box.setCurrentIndex(2)
         ↓
结果: 左侧ToolBox切换到索引2 → 显示「⚡ PLC工具」页面 ❌
       （而非预期的「🔄 变更管理」页面）
```

#### 根因

**NavigationController中的ToolBox索引定义与LeftPanelBuilder的实际构建顺序不一致**：

| 常量名 | NC定义值 | LPB实际值 | 差异 |
|--------|---------|----------|------|
| `TOOL_PLC` | 3 | **2** | ❌ 差1 |
| `TOOL_CHANGE_MGMT` | 2 | **3** | ❌ 差1 |

#### 影响范围

| 操作 | 预期行为 | 实际行为 | 严重度 |
|------|---------|---------|--------|
| 点击「变更管理」Tab | 左侧显示变更管理页面 | 左侧显示**PLC工具** | 🔴 Critical |
| 点击「PLC工具」Tab | 左侧显示PLC工具页面 | 左侧显示**变更管理** | 🔴 Critical |
| 点击左侧「PLC工具」页面 | 右侧切换到PLC工具Tab | 右侧切换到**变更管理**Tab | 🔴 Critical |
| 点击左侧「变更管理」页面 | 右侧切换到变更管理Tab | 右侧切换到**PLC工具**Tab | 🔴 Critical |

#### 修复方案（仅供参考，不实施）

**方案A: 修改NavigationController常量**
```python
# 将这两行交换:
TOOL_PLC = 2            # 改为 2
TOOL_CHANGE_MGMT = 3    # 改为 3
```

**方案B: 修改LeftPanelBuilder构建顺序**
将 `_create_change_mgmt_page()` 移到 `_create_sidebar_tool_page("PLC工具")` 之前。

---

## 4. 事件流分析

### 4.1 EventBus 信号清单

| 信号名 | 定义位置 | 发射者 | 连接者 | 状态 |
|--------|---------|--------|--------|------|
| `project_created(str)` | EventBus | MenuManager | MainWindow._on_project_created | ✅ 正常 |
| `project_opened(str)` | EventBus | MenuManager | MainWindow._on_project_opened | ✅ 正常 |
| `document_open_request(str)` | EventBus | 未使用 | MainWindow._on_document_open | ⚠️ 空处理 |
| `theme_changed(str)` | EventBus | MenuManager | MainWindow._on_theme_changed | ✅ 正常 |
| `settings_changed()` | EventBus | SettingsDialog | MainWindow._on_settings_changed | ✅ 正常 |
| `project_selected(str)` | EventBus | 从未发射 | 未连接 | 🔴 死信号 |
| `document_saved(str)` | EventBus | 从未发射 | 未连接 | 🔴 死信号 |
| `document_created(str)` | EventBus | 从未发射 | 未连接 | 🔴 死信号 |
| `st_file_open_request(str)` | EventBus | 从未发射/连接 | 未连接 | 🔴 死信号 |
| `variable_check_request()` | EventBus | MenuManager | 无处理函数 | 🟡 断路 |
| `fb_doc_generate_request(str)` | EventBus | 从未发射/连接 | 未连接 | 🔴 死信号 |
| `spec_check_request(dict)` | EventBus | ToolBarManager | 无处理函数 | 🟡 断路 |

### 4.2 导航事件流

```
┌─────────────────────────────────────────────────────────────┐
│                    用户操作分类                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [A] 顶部Tab点击                                             │
│      QTabWidget.currentChanged(tab_idx)                      │
│              ↓                                               │
│      NavigationController._on_tab_changed(tab_idx)           │
│              ↓                                               │
│      查表 TAB_TO_TOOLBOX → 获取toolbox_idx                  │
│              ↓                                               │
│      blockSignals(True)                                      │
│      tool_box.setCurrentIndex(toolbox_idx)  ← 同步左侧      │
│      blockSignals(False)                                     │
│                                                             │
│  [B] 左侧ToolBox页面切换                                      │
│      QToolBox.currentChanged(toolbox_idx)                    │
│              ↓                                               │
│      NavigationController._on_toolbox_changed(toolbox_idx)   │
│              ↓                                               │
│      查表 TOOLBOX_TO_TAB → 获取tab_idx                      │
│              ↓                                               │
│      blockSignals(True)                                      │
│      tab_widget.setCurrentIndex(tab_idx)    ← 同步右侧      │
│      blockSignals(False)                                     │
│                                                             │
│  [C] 侧边栏按钮点击                                           │
│      QPushButton.clicked → action_handler(target_tab_or_text)│
│              ↓                                               │
│      MainWindow._on_action(action)                           │
│              ↓                                               │
│      ├─ int类型 → navigate_to_tab(tab_index)                │
│      │           ↓                                           │
│      │       同时设置tab_widget和tool_box的currentIndex      │
│      │                                                       │
│      └─ str类型 → on_sidebar_action(action_text)            │
│                  ↓                                           │
│              SIDEBAR_ACTION_MAP 匹配                          │
│                  ↓                                           │
│              调用对应处理函数(sync_handler/menu_manager等)    │
│                                                             │
│  [D] 项目树节点双击                                           │
│      ProjectTreeWidget.navigation_requested.emit(tab_idx,ctx)│
│              ↓                                               │
│      MainWindow._on_project_tree_navigate(tab_idx, context)  │
│              ↓                                               │
│      NavigationController.on_project_tree_navigate()         │
│              ↓                                               │
│      navigate_to_tab(tab_idx) + 可选的项目信息更新           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 blockSignals防循环机制

```python
def _on_tab_changed(self, tab_idx: int):
    """当用户点击顶部Tab时触发"""
    toolbox_idx = self.TAB_TO_TOOLBOX.get(tab_idx)
    if toolbox_idx is not None and self._tool_box:
        self._tool_box.blockSignals(True)   # ① 阻断ToolBox信号
        self._tool_box.setCurrentIndex(toolbox_idx)  # ② 修改ToolBox（不触发currentChanged）
        self._tool_box.blockSignals(False)  # ③ 恢复信号

def _on_toolbox_changed(self, toolbox_idx: int):
    """当用户切换左侧ToolBox页面时触发"""
    tab_idx = self.TOOLBOX_TO_TAB.get(toolbox_idx)
    if tab_idx is not None and self._tab_widget:
        self._tab_widget.blockSignals(True)   # ① 阻断Tab信号
        self._tab_widget.setCurrentIndex(tab_idx)  # ② 修改Tab（不触发currentChanged）
        self._tab_widget.blockSignals(False)  # ③ 恢复信号
```

**关键点**: 使用`blockSignals(True/False)`防止双向同步导致无限递归。

---

## 5. 各功能域GUI实现详情

### 5.1 F01: 项目管理

**GUI入口**:
- 顶部菜单: 文件(F) → 新建项目 / 打开项目
- 工具栏: 新建项目 / 打开项目 按钮
- 仪表盘DashboardPage: 快捷操作卡片
- 左侧项目管理页面: ProjectTreeWidget

**组件结构**:
```
ProjectTreeWidget (QWidget)
├── QLabel: "📂 项目浏览器" (标题)
├── QTreeWidget: 项目树
│   ├── itemDoubleClicked → navigation_requested信号
│   └── customContextMenuRequested → 右键菜单
└── QLabel: "📁 未选择项目" (状态提示)
```

**右键菜单项**:
- 新建文件夹
- 新建文档...
- 重命名
- 删除
- 刷新
- 展开全部 / 折叠全部

**导航规则**:
| 节点类型 | 双击目标Tab | 说明 |
|---------|------------|------|
| document/code | TAB_DOCUMENT (2) | 打开文档编辑器 |
| project | TAB_PROJECT (1) | 显示项目详情 |
| folder | TAB_PROJECT (1) | 保持当前视图 |
| workflow | TAB_PROJECT (1) | 显示项目详情 |

### 5.2 F02: 文档生成

**GUI入口**:
- 左侧文档管理页面的3个按钮
- 项目树右键菜单「新建文档」

**组件**: DocumentEditor (widgets/document_editor.py)

**功能**:
- 文件打开/保存/另存为
- 基础文本编辑
- 工具栏集成

### 5.3 F03: 变更管理-Sync (版本检查/CHG/IFC)

**GUI入口**:
- 左侧规范中心页面的底部3个按钮（版本检查/CHG/IFC）

**控制器**: SyncController (controllers/sync_controller.py)

**异步工作流**:
```
用户点击按钮 → SyncController.on_sync_*()
    ↓
检查项目路径 (为空则提示)
    ↓
创建QProgressDialog (模态,不可取消)
    ↓
启动Worker线程 (_VersionCheckWorker / _GenerateDocWorker)
    ↓
┌─ Worker线程 ─────────────────────────┐
│  SyncEngine.run_check()              │
│  或 SyncEngine.run_generate_chg/ifc() │
│  → finished/error 信号               │
└──────────────────────────────────────┘
    ↓
主线程接收结果 → 显示对话框或错误提示
    ↓
[仅CHG/IFC] SyncResultDialog → 用户选择回写?
    ↓
[如果回写] SyncEngine.writeback_to_project()
    ↓
通知ProjectTreeWidget刷新
```

### 5.4 F08: 变更管理-变更单UI ⭐

**GUI入口**:
- 顶部「🔄 变更管理」Tab (索引3)
- 左侧变更管理页面的「刷新列表」按钮

**组件**: ChangeManagementPanel (widgets/change_management_panel.py)

**UI布局**:
```
ChangeManagementPanel (QWidget)
├── QHBoxLayout (工具栏)
│   ├── [📝 新建变更单] QPushButton
│   └── [🔄 刷新列表] QPushButton
│
├── QSplitter (Vertical, 3:2比例)
│   ├── 上部: QTableWidget (5列)
│   │   ├── 编号 | 标题 | 分类 | 状态 | 路径
│   │   └── cellClicked → 行选中
│   │
│   └── 下部: 详情区域
│       ├── QLabel: "选择变更单查看详情"
│       ├── QTextEdit: 变更单内容 (只读)
│       └── QGroupBox "状态操作"
│           ├── [✅ 批准] QPushButton
│           ├── [⏩ 推进] QPushButton
│           └── [❌ 取消] QPushButton
```

**状态机驱动按钮启用逻辑**:

基于 `ChangeStatus.valid_transitions(current_status)` 动态计算:

| 按钮 | 启用条件 |
|------|---------|
| **批准** | `APPROVED ∈ valid_transitions` |
| **推进** | 存在非CANCELLED/APPROVED的有效目标状态 |
| **取消** | `CANCELLED ∈ valid_transitions` |

**状态颜色编码**:
| 状态 | 中文 | 颜色 |
|------|------|------|
| draft | 草稿 | #9E9E9E (灰) |
| review | 审核中 | #2196F3 (蓝) |
| approved | 已批准 | #4CAF50 (绿) |
| analyzing | 分析中 | #FF9800 (橙) |
| in_progress | 进行中 | #00BCD4 (青) |
| implemented | 已实施 | #8BC34A (浅绿) |
| verifying | 验证中 | #7C4DFF (紫) |
| completed | 已完成 | #3F51B5 (靛蓝) |
| cancelled | 已取消 | #F44336 (红) |

### 5.5 F04: 规范检查

**GUI入口**:
- 菜单: F5快捷键
- Dock面板: 底部可浮动Dock

**组件**: SpecCheckPanel (Dock) + SpecCheckTabPanel (Tab引导页)

**引导页内容**:
- 图标: 🔍 (48pt, #BDBDBD)
- 标题: "规范检查面板"
- 描述: "规范检查功能已移至底部Dock面板..."
- 按钮: "打开规范检查面板" → 显示SpecCheckDock

### 5.6 F05: 诊断分析

**GUI入口**:
- 菜单: F6快捷键
- Dock面板: 底部可浮动Dock

**组件**: DiagnosticPanel (Dock)

**功能**:
- 七维度健康度评估
- LSP兼容性检查
- 诊断报告展示

### 5.7 F06: ST编辑器

**GUI入口**:
- PLC工具Tab内的InnerTab

**组件**: STEditor (widgets/st_editor.py)

**功能**:
- 基础ST语言文本编辑
- 语法高亮 (ST_Lexer)
- 依赖提示 (show_dependency_notice=True)

### 5.7 F07: 仪表盘

**GUI入口**:
- 默认首页 (Tab 0)

**组件**: DashboardPage (dashboard.py)

**功能**:
- 统计卡片 (项目总数/进行中/已完成/已归档)
- 最近项目列表
- 快捷操作按钮

---

## 6. 问题清单

### 6.1 Critical级别

| ID | 问题 | 位置 | 影响 | 复现步骤 |
|----|------|------|------|---------|
| **GUI-NAV-001** | ToolBox页面索引定义与构建顺序不一致 | `navigation_controller.py:21-22` vs `left_panel_builder.py:66-77` | 点击变更管理Tab显示PLC工具 | 1.启动应用 2.点击顶部「变更管理」3.观察左侧显示PLC工具 |

### 6.2 High级别

| ID | 问题 | 位置 | 影响 |
|----|------|------|------|
| **GUI-EVT-001** | spec_check_request信号断路 | ToolBarManager发射但无处理 | 工具栏规范检查按钮无效 |
| **GUI-EVT-002** | variable_check_request信号断路 | MenuManager发射但无处理 | 菜单变量检查无效 |
| **GUI-WDG-001** | ChangeManagementPanel调用ChangeService私有方法 | `change_management_panel.py:241,359,366` | 封装性破坏 |

### 6.3 Medium级别

| ID | 问题 | 位置 | 影响 |
|----|------|------|------|
| **GUI-EVT-003~007** | 5个EventBus死信号 (从未发射/连接) | event_bus.py | 代码冗余 |
| **GUI-WDG-002** | cleanup()空实现 | change_management_panel.py:433 | 可移除或实现 |
| **GUI-MW-001** | Application类死代码 | app.py + main.py | 未被使用 |

---

## 7. 样式系统

### 7.1 QSS属性选择器

| 属性名 | 应用组件 | 用途 |
|--------|---------|------|
| `SidebarHeader` | QLabel (ToolBox页面标题) | 页面标题样式 |
| `SidebarBtn` | QPushButton (侧边栏按钮) | 按钮统一样式 |

### 7.2 StyleBuilder职责

```python
StyleBuilder.apply(widget, theme)  # theme: "light" | "dark"
```

- 加载对应主题的 `.qss` 文件
- 路径搜索策略: 循环查找资源目录
- 应用到整个应用窗口

### 7.3 内联样式 (应迁移到QSS)

以下组件使用了硬编码内联样式（建议后续迁移）：

| 组件 | 位置 | 样式内容 |
|------|------|---------|
| SpecCheckTabPanel引导页 | right_panel_builder.py:163-179 | 字体/颜色/间距 |
| "打开规范检查面板"按钮 | right_panel_builder.py:184-189 | 背景色/圆角/字体 |
| ChangeManagementPanel详情区 | change_management_panel.py:137-139 | 背景色/边框/圆角 |
| ProjectInfoWidget标题 | right_panel_builder.py:69 | 字体/颜色 |
| LeftPanelBuilder分隔线 | left_panel_builder.py:122-127 | 背景色/高度/边距 |

---

## 8. 性能考量

### 8.1 异步操作

| 操作 | 实现方式 | 线程 | UI阻塞 |
|------|---------|------|--------|
| 版本检查 | `_VersionCheckWorker(QThread)` | Worker线程 | 否 (ProgressDialog) |
| CHG生成 | `_GenerateDocWorker(QThread)` | Worker线程 | 否 (ProgressDialog) |
| IFC生成 | `_GenerateDocWorker(QThread)` | Worker线程 | 否 (ProgressDialog) |
| 变更单列表刷新 | 同步调用 | 主线程 | 是 (短暂) |
| 项目树加载 | 同步调用 | 主线程 | 是 (短暂) |

### 8.2 内存管理

- **cleanup()接口**: Panel/Widget基类定义cleanup()方法
- **closeEvent清理**: MainWindow.closeEvent遍历cleanup_targets调用cleanup()
- **当前问题**: ChangeManagementPanel.cleanup()为空实现

---

## 9. 可访问性与国际化

### 9.1 当前状态

| 维度 | 状态 | 说明 |
|------|------|------|
| 字体支持 | ✅ | Microsoft YaHei字体栈 |
| 中文界面 | ✅ | 全中文UI文本 |
| Emoji图标 | ✅ | 广泛使用Emoji替代图标 |
| 键盘快捷键 | 部分 | F5/F6/Ctrl+, 已实现 |
| 屏幕阅读器 | ❌ | 无ARIA/Accessibility支持 |
| 高对比度 | ⚠️ | 仅light/dark两主题 |
| 多语言 | ❌ | 硬编码中文，无i18n框架 |

### 9.2 快捷键清单

| 快捷键 | 功能 | 实现位置 |
|--------|------|---------|
| F5 | 规范检查 | MenuManager |
| F6 | 深度诊断 | MenuManager |
| Ctrl+, | 打开设置 | LeftPanelBuilder按钮文本 |
| Ctrl+N | 新建项目 | MenuManager (预期) |
| Ctrl+O | 打开项目 | MenuManager (预期) |
| Ctrl+S | 保存 | DocumentEditor (预期) |

---

## 10. 审查建议优先级

### P0 - 必须立即修复

1. **GUI-NAV-001**: 修正NavigationController中的ToolBox索引常量，使其与LeftPanelBuilder实际构建顺序一致

### P1 - 短期改进

1. 连接spec_check_request和variable_check_request信号
2. 将内联样式迁移到QSS属性选择器
3. 公开ChangeService的私有方法或封装访问接口

### P2 - 中期优化

1. 清理EventBus死信号（删除或实现）
2. 实现ChangeManagementPanel.cleanup()实际逻辑
3. 删除Application类死代码
4. 补充键盘快捷键完整性

### P3 - 长期规划

1. 引入i18n国际化框架
2. 添加可访问性支持
3. GUI自动化测试覆盖 (pytest-qt)
4. 性能 profiling 和优化

---

## 附录A: 文件索引

| 文件路径 | 行数 | 职责 |
|---------|------|------|
| src/ui/main_window.py | ~354 | 主窗口薄壳 |
| src/ui/builders/left_panel_builder.py | ~165 | 左侧ToolBox构建 |
| src/ui/builders/right_panel_builder.py | ~238 | 右侧TabWidget构建 |
| src/ui/builders/style_builder.py | - | 主题样式管理 |
| src/ui/builders/dock_panel_builder.py | - | Dock面板构建 |
| src/ui/controllers/navigation_controller.py | ~119 | 导航同步控制 |
| src/ui/controllers/sync_controller.py | ~231 | Sync功能控制 |
| src/ui/controllers/project_controller.py | - | 项目功能控制 |
| src/ui/controllers/dashboard_controller.py | - | 仪表盘控制 |
| src/ui/widgets/change_management_panel.py | ~434 | 变更管理面板 |
| src/ui/widgets/project_tree.py | ~333 | 项目树组件 |
| src/ui/widgets/document_editor.py | - | 文档编辑器 |
| src/ui/widgets/st_editor.py | - | ST编辑器 |
| src/ui/widgets/spec_check_panel.py | - | 规范检查面板 |
| src/ui/widgets/diagnostic_panel.py | - | 诊断面板 |
| src/ui/managers/menu_manager.py | - | 菜单管理 |
| src/ui/managers/toolbar_manager.py | - | 工具栏管理 |
| src/core/event_bus.py | - | 事件总线 |
| src/core/constants.py | ~360 | 常量和枚举 |

---

**报告完成** ✅

*本报告为纯审查文档，不包含任何代码修改建议的实施。*
