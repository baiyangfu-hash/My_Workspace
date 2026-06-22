# auto-pm V2.0 GUI 原型设计

## 一、设计目标

基于当前 GUI 的核心缺陷，本次重构聚焦三大目标：

1. **总库分类导航**：以 PLC 总库 / Python 总库为一级入口，取代当前项目平铺
2. **功能补全**：将 CLI 已有的变更管理、PLC 检查/修复、模板管理暴露到 GUI
3. **交互升级**：分组视图、多视图模式、排序筛选、批量操作

### 设计原则

- **无角色区分**：使用者一人兼顾项目经理/PLC开发/Python开发，所有功能全部可见，无需角色切换
- **模块化开发**：GUI 按功能模块独立开发、独立测试，每个模块可单独替换
- **后端驱动优先**：按后端服务支撑度排开发优先级，后端已就绪的功能先做

### 后端匹配度总览

| 匹配状态 | 含义 | 占比 | 开发优先级 |
|---------|------|------|----------|
| ✅ 已有 | 后端 Service/Repository 方法完整，可直接调用 | 60% | P0 先做 |
| ⚠️ 部分有 | Repository 有但 Service 未暴露，或字段缺失，需补桥接 | 30% | P0 同步补后端 |
| ❌ 缺失 | 后端完全无，需从零开发 | 10% | P1 后做 |

---

## 二、全局布局

```
┌──────────────────────────────────────────────────────────────────┐
│ 菜单栏：视图 | 工具 | 帮助                                        │
├────────┬─────────────────────────────────────────────────────────┤
│        │ 工具栏：[搜索框] [业务线▼] [新建▼] [导入] [同步] [刷新]    │
│  侧    ├─────────────────────────────────────────────────────────┤
│  边    │                                                         │
│  栏    │                    中央内容区                              │
│        │               (QStackedWidget)                           │
│ 220px  │                                                         │
│        │                                                         │
│        │                                                         │
│        ├─────────────────────────────────────────────────────────┤
│        │ 状态栏：项目数 | 变更数 | DB状态 | 工作空间路径 | 扫描时间   │
└────────┴─────────────────────────────────────────────────────────┘
```

---

## 三、侧边栏导航重构

### 3.1 当前 vs 重构后

| 当前（5项平铺） | 重构后（树形分组） |
|-----------------|-------------------|
| 项目列表 | 📂 PLC 总库 |
| 规范中心 |   ├─ 在研项目 |
| 模板管理 |   ├─ 调试中 |
| 报告中心 |   ├─ 生产中 |
| 系统设置 |   └─ 已归档 |
|               | 📂 Python 总库 |
|               |   ├─ 在研项目 |
|               |   ├─ 调试中 |
|               |   ├─ 生产中 |
|               |   └─ 已归档 |
|               | ───────────── |
|               | 📋 全部项目 |
|               | 🔄 变更中心 |
|               | 📐 规范中心 |
|               | 📦 模板管理 |
|               | 📊 报告中心 |
|               | ⚙️ 系统设置 |

### 3.2 侧边栏交互规则

- **点击总库节点**（PLC 总库 / Python 总库）→ 展示该总库下所有项目的分组视图
- **点击阶段子节点**（在研项目 / 调试中 / ...）→ 筛选该总库下指定阶段的项目
- **点击"全部项目"** → 展示工作空间所有项目，按总库分组
- **点击功能节点**（变更中心 / 规范中心 / ...）→ 切换到对应功能页
- 总库节点默认展开，阶段子节点显示项目计数徽标

### 3.3 侧边栏数据来源

```
总库分类 ← stack 字段（plc → PLC 总库，python → Python 总库）
阶段分组 ← phase 字段（developing/commissioning/production/archived）
项目计数 ← 实时从 DB 缓存查询
```

---

## 四、项目列表页重构

### 4.1 分组视图（默认）

```
┌─────────────────────────────────────────────────────────┐
│ [卡片视图] [列表视图]     排序: 编号▼ | 阶段 | 修改时间    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ▼ PLC 总库 · 单机 (DJ) — 3 个项目                        │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                 │
│ │ DJ-2026  │ │ DJ-2026  │ │ DJ-2026  │                 │
│ │ -000     │ │ -005     │ │ -010     │                 │
│ │ 单机设备  │ │ 输送线   │ │ 包装机   │                 │
│ │ [plc]    │ │ [plc]    │ │ [plc]    │                 │
│ └──────────┘ └──────────┘ └──────────┘                 │
│                                                         │
│ ▼ Python 总库 · 软件 (SW) — 3 个项目                     │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                 │
│ │ SW-2026  │ │ SW-2026  │ │ SW-2026  │                 │
│ │ -001     │ │ -004     │ │ -008     │                 │
│ │ 变量表   │ │ 项目管理  │ │ auto-pm  │                 │
│ │ [python] │ │ [python] │ │ [python] │                 │
│ └──────────┘ └──────────┘ └──────────┘                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**分组维度**（可切换）：
- 按总库+业务线（默认）← 推荐，与工作空间目录结构对齐
- 按总库+阶段
- 按业务线
- 按阶段

### 4.2 列表视图

```
┌──────┬──────────┬──────────────┬──────┬──────┬──────┬────────┬──────────┐
│ 编号  │ 业务线    │ 项目名称      │ 技术栈│ 阶段  │ 版本  │ 变更数  │ 修改时间  │
├──────┼──────────┼──────────────┼──────┼──────┼──────┼────────┼──────────┤
│ DJ-0 │ DJ       │ 单机设备项目  │ PLC  │ 开发中│ 1.0  │ 2      │ 06-18    │
│ DJ-5 │ DJ       │ 输送线项目    │ PLC  │ 调试中│ 2.1  │ 5      │ 06-15    │
│ SW-1 │ SW       │ 变量表解析    │ Py   │ 生产中│ 1.2  │ 0      │ 05-20    │
│ SW-8 │ SW       │ auto-pm     │ Py   │ 开发中│ 0.1  │ 3      │ 06-20    │
└──────┴──────────┴──────────────┴──────┴──────┴──────┴────────┴──────────┘
```

- 支持列排序（点击列头）
- 支持列宽拖拽
- 右键行 → 编辑/删除/打开目录/PLC检查/创建变更单

### 4.3 卡片增强

```
┌─────────────────────────┐
│ [PLC]  DJ         v2.1  │  ← 技术栈徽标 + 业务线 + 版本
│                         │
│ 输送线自动化项目          │  ← 项目名称（加粗）
│ DJ-2026-005             │  ← 项目编号（灰色）
│                         │
│ 阶段: [调试中]           │  ← 阶段徽标（彩色）
│ 变更: 5 活跃 / 12 总计   │  ← 变更统计
│                         │
│ 修改: 2026-06-15         │  ← 最近修改时间
└─────────────────────────┘
```

---

## 五、项目工作区重构

### 5.1 当前 vs 重构后

| Tab | 当前状态 | 重构后功能 |
|-----|---------|-----------|
| 概览 | ✅ 已实现 | 保留，增强元数据编辑 |
| 变更 | 占位 | **变更列表 + 创建 + 状态流转** |
| 检查 | 占位 | **PLC/Python 规范检查 + 修复** |
| 文档 | 占位 | **项目文档浏览 + 模板更新** |
| 变量表 | 占位 | V2.3 延后（仅 PLC 项目可见） |

### 5.2 变更 Tab（新增）

```
┌─────────────────────────────────────────────────────────┐
│ [+ 创建变更单]    筛选: [全部状态▼] [全部领域▼]            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─ CHG-SW-2026-008-001 ───────────────────── [实施中] ─┐│
│ │ 领域: 代码 | 性质: 修正 | 范围: 局部                    ││
│ │ 申请人: fubai | 创建: 2026-06-18                       ││
│ │ 背景: 修复 project edit --phase 枚举校验缺失            ││
│ └───────────────────────────────────────────────────────┘│
│                                                         │
│ ┌─ CHG-SW-2026-008-002 ───────────────────── [草稿] ───┐│
│ │ 领域: 文档 | 性质: 新增 | 范围: 局部                    ││
│ │ 申请人: fubai | 创建: 2026-06-20                       ││
│ │ 背景: 新增 GUI 原型设计文档                             ││
│ └───────────────────────────────────────────────────────┘│
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.3 检查 Tab（新增）

```
┌─────────────────────────────────────────────────────────┐
│ [▶ 执行检查]  [🔧 自动修复]  [📝 标准化命名]              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ PLC 项目结构检查 (LSP-907)                               │
│                                                         │
│ ✅ 目录结构                                              │
│   ✅ 00_通用规范/ 存在                                    │
│   ✅ 01_程序/ 存在                                       │
│   ✅ 02_HMI/ 存在                                        │
│                                                         │
│ ⚠️ 标志文件                                              │
│   ✅ .plc.json 存在                                      │
│   ⚠️ PM_SESSION_*.md 缺失 — [修复]                      │
│                                                         │
│ ❌ 命名规范                                              │
│   ✅ FB_ 前缀正确                                        │
│   ❌ DB1_变量命名不符合905规范 — [修复] [标准化]           │
│                                                         │
│ ─────────────────────────────────────                   │
│ 检查结果: 8 通过 / 2 警告 / 1 失败                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.4 文档 Tab（新增）

```
┌─────────────────────────────────────────────────────────┐
│ [🔄 模板更新]                                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 📄 项目文档                                              │
│ ├─ 📋 PM_SESSION_DJ-2026-005.md                        │
│ ├─ 📋 立项表_DJ-2026-005.md                             │
│ ├─ 📋 变更单_CHG-DJ-2026-005-001.md                    │
│ └─ 📁 09_整改项/                                        │
│                                                         │
│ 模板信息                                                 │
│ 模板: plc-project-template v1.0                         │
│ 上次更新: 2026-05-01                                     │
│ [检查更新]                                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 六、变更中心页（新增全局页）

```
┌─────────────────────────────────────────────────────────┐
│ [全部] [草稿] [待审批] [实施中] [已完成] [已归档]          │
├──────────────────────┬──────────────────────────────────┤
│                      │                                  │
│ 变更单列表            │ 变更单详情                        │
│                      │                                  │
│ ┌ CHG-SW-8-001 ───┐ │ 编号: CHG-SW-2026-008-001       │
│ │ [实施中] 代码/修正│ │ 状态: 实施中                     │
│ └─────────────────┘ │ 领域: 代码 | 性质: 修正           │
│                      │ 范围: 局部                        │
│ ┌ CHG-SW-8-002 ───┐ │ 申请人: fubai                    │
│ │ [草稿] 文档/新增  │ │ 创建: 2026-06-18                │
│ └─────────────────┘ │                                  │
│                      │ ── 背景 ──                       │
│                      │ 修复 project edit --phase 枚举   │
│                      │ 校验缺失导致项目列表崩溃          │
│                      │                                  │
│                      │ ── 操作 ──                       │
│                      │ [提交审批] [实施] [验收] [归档]    │
│                      │                                  │
└──────────────────────┴──────────────────────────────────┘
```

---

## 七、新建对话框增强

### 7.1 新建项目下拉拆分

```
[+ 新建 ▼]
  ├─ PLC 项目       → NewProjectDialog(stack=plc)
  ├─ Python 项目    → NewProjectDialog(stack=python)
  └─ 变更单         → CreateChangeDialog
```

### 7.2 CreateChangeDialog（新增）

```
┌─ 创建变更单 ────────────────────────────────────┐
│                                                 │
│ 项目: [SW-2026-008 auto-pm        ▼]            │
│                                                 │
│ 领域: [代码 ▼]  性质: [修正 ▼]  范围: [局部 ▼]   │
│                                                 │
│ 申请人: [fubai           ]                       │
│                                                 │
│ 背景 (*):                                       │
│ ┌─────────────────────────────────────────────┐ │
│ │                                             │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ 必要性:                                          │
│ ┌─────────────────────────────────────────────┐ │
│ │                                             │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ 紧急度: [普通 ▼]   计划日期: [          📅]      │
│                                                 │
│              [取消]  [创建]                       │
└─────────────────────────────────────────────────┘
```

---

## 八、模块化开发架构

### 8.1 模块划分

GUI 按功能域拆分为独立模块，每个模块一个 Python 包，可独立开发、独立测试：

```
auto_pm/ui/
├── __init__.py
├── main_window.py          # 主窗口（布局容器，组合各模块）
├── navigation/             # 模块1: 导航系统
│   ├── __init__.py
│   ├── nav_tree.py         # 树形侧边栏 (QTreeWidget)
│   └── nav_model.py        # 导航数据模型（总库/阶段/功能节点）
├── project_list/           # 模块2: 项目列表
│   ├── __init__.py
│   ├── list_view.py        # 项目列表页（分组+双视图）
│   ├── card_view.py        # 卡片网格视图
│   ├── table_view.py       # 列表表格视图
│   ├── project_card.py     # 项目卡片组件
│   ├── group_header.py     # 分组标题组件
│   └── view_controls.py    # 视图切换+排序+分组控件
├── workspace/              # 模块3: 项目工作区
│   ├── __init__.py
│   ├── workspace_view.py   # 工作区容器（Header+TabBar）
│   ├── overview_tab.py     # 概览 Tab
│   ├── change_tab.py       # 变更 Tab
│   ├── check_tab.py        # 检查 Tab
│   └── doc_tab.py          # 文档 Tab
├── change_center/          # 模块4: 变更中心
│   ├── __init__.py
│   ├── center_view.py      # 变更中心页（左右分栏）
│   ├── change_list_panel.py # 变更单列表面板
│   └── change_detail_panel.py # 变更单详情面板
├── dialogs/                # 模块5: 对话框
│   ├── __init__.py
│   ├── new_project_dialog.py    # 新建项目（保留）
│   ├── edit_project_dialog.py   # 编辑项目（保留）
│   ├── delete_project_dialog.py # 删除项目（保留）
│   ├── import_project_dialog.py # 导入项目（保留）
│   ├── create_change_dialog.py  # 创建变更单（新增）
│   └── transition_dialog.py     # 状态流转确认（新增）
├── global_pages/           # 模块6: 全局功能页
│   ├── __init__.py
│   ├── spec_center.py      # 规范中心
│   ├── template_page.py    # 模板管理
│   ├── report_page.py      # 报告中心
│   └── settings_page.py    # 系统设置
├── widgets/                # 模块7: 通用组件
│   ├── __init__.py
│   ├── stats_bar.py        # 统计栏（保留）
│   ├── filter_bar.py       # 筛选栏（保留）
│   ├── status_badge.py     # 状态徽标组件
│   └── search_box.py       # 搜索框组件
└── models/                 # 模块8: UI 数据模型
    ├── __init__.py
    └── project_model.py    # Qt 数据模型（保留）
```

### 8.2 模块依赖关系

```
main_window
  ├── navigation        (无外部依赖)
  ├── project_list      (依赖: widgets, models)
  ├── workspace         (依赖: widgets, dialogs)
  ├── change_center     (依赖: widgets, dialogs)
  ├── global_pages      (依赖: widgets)
  └── widgets           (无外部依赖)
```

### 8.3 模块开发顺序

按依赖关系和功能优先级，建议分 4 批开发：

**第1批：基础框架**（所有后续模块的前置依赖）

| 序号 | 模块 | 组件 | 说明 |
|------|------|------|------|
| 1-1 | navigation | nav_tree + nav_model | 树形侧边栏，总库分组+阶段子节点+计数徽标 |
| 1-2 | widgets | status_badge + search_box | 通用组件 |
| 1-3 | main_window | 重构 | 替换 QListWidget→QTreeWidget，移除角色菜单 |

**第2批：核心功能**（用户最高频使用）

| 序号 | 模块 | 组件 | 说明 |
|------|------|------|------|
| 2-1 | project_list | list_view + card_view + table_view + group_header + view_controls | 分组卡片+列表双视图 |
| 2-2 | project_list | project_card (增强) | 增加变更数、修改时间 |
| 2-3 | workspace | change_tab + change_detail | 变更 Tab |
| 2-4 | dialogs | create_change_dialog + transition_dialog | 变更对话框 |

**第3批：扩展功能**

| 序号 | 模块 | 组件 | 说明 |
|------|------|------|------|
| 3-1 | workspace | check_tab | PLC 检查/修复/标准化 |
| 3-2 | workspace | doc_tab | 文档浏览+模板更新 |
| 3-3 | change_center | center_view + list_panel + detail_panel | 变更中心全局页 |

**第4批：辅助功能**

| 序号 | 模块 | 组件 | 说明 |
|------|------|------|------|
| 4-1 | global_pages | template_page | 模板管理 |
| 4-2 | global_pages | report_page | 报告中心 |
| 4-3 | global_pages | settings_page | 系统设置 |
| 4-4 | global_pages | spec_center | 规范中心 |

### 8.4 模块间通信

模块间通过 Qt 信号/槽机制通信，主窗口作为信号中转站：

```
NavigationTree.project_selected(stack, phase)  → MainWindow → ProjectListView.set_filter(stack, phase)
ProjectListView.project_clicked(project_id)    → MainWindow → WorkspaceView.load_project(project_id)
ChangeTab.change_created(project_id)           → MainWindow → ProjectListView.refresh_counts()
ChangeTab.change_created(project_id)           → MainWindow → ChangeCenterView.refresh()
```

---

## 九、页面路由映射

| 侧边栏节点 | 中央页面 | QStackedWidget Index |
|------------|---------|---------------------|
| PLC 总库 | ProjectListView(stack=plc) | 0 |
| PLC 总库 > 在研项目 | ProjectListView(stack=plc, phase=developing) | 0 |
| PLC 总库 > 调试中 | ProjectListView(stack=plc, phase=commissioning) | 0 |
| PLC 总库 > 生产中 | ProjectListView(stack=plc, phase=production) | 0 |
| PLC 总库 > 已归档 | ProjectListView(stack=plc, phase=archived) | 0 |
| Python 总库 | ProjectListView(stack=python) | 0 |
| Python 总库 > 在研项目 | ProjectListView(stack=python, phase=developing) | 0 |
| Python 总库 > ... | ... | 0 |
| 全部项目 | ProjectListView(stack=all) | 0 |
| 变更中心 | ChangeCenterView | 3 |
| 规范中心 | SpecCenterView | 2 |
| 模板管理 | TemplatePage | 4 |
| 报告中心 | ReportPage | 5 |
| 系统设置 | SettingsPage | 6 |
| (点击项目卡片) | ProjectWorkspaceView | 1 |

---

## 十、组件清单与优先级

### P0 — 核心体验（必须实现）

| 组件 | 模块 | 类型 | 说明 |
|------|------|------|------|
| NavigationTree | navigation | 重构 | 树形侧边栏，含总库分组和阶段子节点 |
| ProjectListView | project_list | 重构 | 分组视图 + 列表视图双模式 |
| ProjectCard | project_list | 增强 | 增加变更数、修改时间、描述摘要 |
| ChangeTab | workspace | 新增 | 项目工作区变更 Tab |
| CheckTab | workspace | 新增 | 项目工作区检查 Tab |
| CreateChangeDialog | dialogs | 新增 | 创建变更单对话框 |
| ChangeCenterView | change_center | 新增 | 变更中心全局页 |

### P1 — 体验优化

| 组件 | 模块 | 类型 | 说明 |
|------|------|------|------|
| DocTab | workspace | 新增 | 项目工作区文档 Tab |
| TemplatePage | global_pages | 新增 | 模板管理全局页 |
| ReportPage | global_pages | 新增 | 报告中心全局页 |
| SettingsPage | global_pages | 新增 | 系统设置全局页 |
| NewProjectDropdown | main_window | 重构 | 新建按钮下拉拆分 |
| StatusBar | main_window | 增强 | 显示工作空间路径 + 实际扫描时间 |

### P2 — 锦上添花

| 组件 | 模块 | 类型 | 说明 |
|------|------|------|------|
| VarTableTab | workspace | 新增 | 变量表 Tab（仅 PLC 项目可见） |
| SpecCenterView | global_pages | 新增 | 规范中心 |
| BatchOperations | project_list | 新增 | 批量检查/批量删除 |
| KeyboardShortcuts | main_window | 新增 | Ctrl+N/R/F 等快捷键 |

---

## 十一、数据流设计

### 11.1 侧边栏项目计数

```
ProjectService.list_projects_cached()
  → 按 stack 分组计数 → 总库节点徽标
  → 按 stack+phase 分组计数 → 阶段子节点徽标
```

### 11.2 变更数据流

```
ChangeService.list_change_requests(project_id)
  → 变更 Tab 列表
  → 卡片变更数统计

ChangeService.create_change_request(...)
  → CreateChangeDialog 提交

ChangeService.transition_change_request(chg_id, to_status, comment)
  → 变更 Tab / 变更中心 状态流转
```

### 11.3 PLC 检查数据流

```
PlcChecker.check(project_id)
  → 检查 Tab 结果列表

PlcRepairer.repair(project_id, dry_run=True)
  → 修复预览

PlcStandardizer.standardize(project_id, apply=False)
  → 标准化预览
```

---

## 十二、与当前代码的映射

| 原组件 | 处理方式 | 新模块 | 新组件 |
|--------|---------|--------|--------|
| MainWindow.navList (QListWidget) | 替换为 QTreeWidget | navigation | NavigationTree |
| MainWindow._nav_items | 重构为树形数据模型 | navigation | NavModel |
| MainWindow._role_menu | **删除** | — | — |
| MainWindow.apply_role() | **删除** | — | — |
| ProjectListView | 重构分组逻辑 | project_list | ProjectListView (enhanced) |
| ProjectCard | 增加字段 | project_list | ProjectCard (enhanced) |
| GlobalView | 拆分为独立页面 | global_pages | SpecCenter/TemplatePage/ReportPage/SettingsPage |
| ProjectWorkspaceView._tabs | 替换占位为实际组件 | workspace | ChangeTab/CheckTab/DocTab |
| FilterBar | 保留，与侧边栏联动 | widgets | FilterBar |
| StatsBar | 保留 | widgets | StatsBar |
| NewProjectDialog | 保留 | dialogs | NewProjectDialog |
| EditProjectDialog | 保留 | dialogs | EditProjectDialog |
| DeleteProjectDialog | 保留 | dialogs | DeleteProjectDialog |
| ImportProjectDialog | 保留 | dialogs | ImportProjectDialog |
| roles.py | **删除** | — | — |

---

## 十三、后端匹配度详细分析

### 13.1 项目列表页

| 原型功能 | 后端方法 | 匹配状态 | 说明 |
|----------|----------|----------|------|
| 按总库(stack)筛选 | `ProjectRepository.list_by_stack()` | ⚠️部分有 | Repository 有，Service 未暴露，需补 `list_projects_filtered()` |
| 按阶段(phase)筛选 | 无 | ⚠️部分有 | DB 有索引但 Repository 缺 `list_by_phase()`，需新增 |
| 按业务线筛选 | `ProjectRepository.list_by_business_line()` | ⚠️部分有 | Repository 有，Service 未暴露 |
| 分组视图 | `ProjectInfo` 含 stack/bl/phase | ✅已有 | 前端分组聚合即可 |
| 变更数统计 | `ChangeRequestRepository.count_by_project()` | ⚠️部分有 | Repository 有，DTO 预留字段，Service 需补 JOIN 查询 |
| 最近修改时间 | `ProjectRecord.file_mtime` | ⚠️部分有 | ProjectInfo 缺此字段，需扩展 |

### 13.2 项目工作区

| 原型功能 | 后端方法 | 匹配状态 | 说明 |
|----------|----------|----------|------|
| 概览Tab | `OverviewTab.load_project()` | ✅已有 | 现有实现保留 |
| 变更Tab - 列表 | `ChangeService.list_change_requests(pid, status, domain)` | ✅已有 | 支持 status/domain 筛选 |
| 变更Tab - 创建 | `ChangeService.create_change_request(...)` | ✅已有 | 完整流程 |
| 变更Tab - 详情 | `ChangeService.get_change_request(num)` | ✅已有 | 返回完整 ChangeRequest |
| 变更Tab - 状态流转 | `ChangeService.transition_status(...)` | ✅已有 | 10 状态全覆盖+门禁 |
| 变更Tab - 编辑 | 无 | ❌缺失 | 需新增 `update_change_request()` |
| 变更Tab - 删除 | 无 | ❌缺失 | 需新增 `delete_change_request()` |
| 检查Tab - 结构检查 | `PlcChecker.check_project()` | ✅已有 | 返回 CheckResult |
| 检查Tab - 自动修复 | `PlcRepairer.repair_project(dry_run)` | ✅已有 | 支持 dry_run |
| 检查Tab - 标准化 | `PlcRepairer.standardize_docs(apply)` | ✅已有 | 注意：在 repairer.py 内，无独立 standardizer |
| 文档Tab - 文件列表 | 无专门服务 | ⚠️部分有 | 需新增项目文档扫描方法 |
| 文档Tab - 模板更新 | `TemplateService.update_template()` | ✅已有 | 基于 Copier |

### 13.3 变更中心

| 原型功能 | 后端方法 | 匹配状态 | 说明 |
|----------|----------|----------|------|
| 全局变更列表 | `ChangeRequestRepository.list_all()` | ⚠️部分有 | Repository 有，Service 强制要求 project_id，需补 `list_all_changes()` |
| 按状态筛选 | `ChangeService.list_change_requests(pid, status)` | ⚠️部分有 | 仅限单项目，全局筛选需补 |
| 按领域筛选 | 同上 | ⚠️部分有 | 同上 |
| 状态流转 | `ChangeService.transition_status()` | ✅已有 | 完整状态机 |

### 13.4 全局功能页

| 原型功能 | 后端方法 | 匹配状态 | 说明 |
|----------|----------|----------|------|
| 规范中心 | 无 | ❌缺失 | specmgr 是独立工具，未集成 |
| 模板管理 - 列表 | `TemplateService.list_templates()` | ✅已有 | |
| 模板管理 - 更新 | `TemplateService.update_template()` | ✅已有 | |
| 报告中心 | 无 | ❌缺失 | 需新建 `ReportService` |
| 系统设置 | `AutoPmConfig` | ⚠️部分有 | 仅 2 个字段，需扩展 |

### 13.5 后端补充清单

| 序号 | 模块 | 方法 | 优先级 | 所属迭代 |
|------|------|------|--------|---------|
| B1 | ProjectRepository | `list_by_phase(phase)` | P0 | 迭代1 |
| B2 | ProjectService | `list_projects_filtered(stack, phase, bl)` | P0 | 迭代1 |
| B3 | ProjectService | `list_projects_with_change_count()` | P0 | 迭代1 |
| B4 | ProjectInfo | 增加 `file_mtime` 字段 | P0 | 迭代1 |
| B5 | ChangeService | `list_all_changes(status, domain)` | P0 | 迭代2 |
| B6 | ChangeService | `update_change_request(num, **kwargs)` | P1 | 迭代2 |
| B7 | ChangeService | `delete_change_request(num)` | P1 | 迭代2 |
| B8 | ReportService | 新建（统计聚合） | P1 | 迭代4 |
| B9 | AutoPmConfig | 扩展配置项 | P1 | 迭代4 |
