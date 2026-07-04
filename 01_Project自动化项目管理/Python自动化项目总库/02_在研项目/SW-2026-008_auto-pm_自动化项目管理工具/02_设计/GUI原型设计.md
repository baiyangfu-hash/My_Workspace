# auto-pm V2.1 GUI 原型设计

> **版本**: V2.1（2026-07-01 升级，新增「变量表 Tab 设计」章节对齐 V2.3 Week4 实现）
> **V2.0 基线**: 2026-06-22 初版（总库分类导航 + 功能补全 + 交互升级）
> **V2.1 变更**: ① §5.1 项目工作区 Tab 表格更新（变量表 Tab 从"V2.3 延后"改为"V2.3 已完成"）② 新增 §5.5 变量表 Tab 设计章节（对齐 V2.3 Week4 实际实现）③ 新增 §14 V2.1 变更记录
> **审核状态**: ✅ 已审核通过（2026-07-01，用户审核），作为 V0.5.x 稳定期 GUI 演进的基线

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
| 变更 | ✅ V2.0 已实现 | **变更列表 + 创建 + 状态流转** |
| 检查 | ✅ V2.0 已实现 | **PLC/Python 规范检查 + 修复** |
| 文档 | ✅ V2.0 已实现 | **项目文档浏览 + 模板更新** |
| 变量表 | ✅ V2.3 Week4 已实现 | **变量表文件列表 + 表格编辑器 + 批量解析 + 格式转换**（仅 PLC 项目可见，详见 §5.5） |

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

### 5.5 变量表 Tab（V2.1 新增，对齐 V2.3 Week4 实现）

> **实现版本**: V2.3 Week4（T15-T16）已于 2026-07-01 交付
> **生产代码**: `auto_pm/ui/vartable/variable_table_editor.py` + `auto_pm/ui/vartable/vartable_tab.py`
> **测试覆盖**: 33 个 UI 测试（tests/ui/test_vartable_tab.py + tests/ui/test_variable_table_editor.py）
> **可见性**: 仅 PLC 项目工作区可见（Python 项目不显示此 Tab）

#### 5.5.1 布局设计（QSplitter 两栏布局）

```
┌─────────────────────────────────────────────────────────────────────┐
│ [📄 导入文件] [💾 导出] [🔄 批量解析] [🗑️ 清空]    角色: [PLC工程师▼] │
├──────────────┬──────────────────────────────────────────────────────┤
│              │                                                      │
│  文件列表    │           变量表编辑器                                 │
│              │                                                      │
│  ┌─────────┐ │  ┌────────────────────────────────────────────────┐ │
│  │📄 io_   │ │  │ station | signal_type | address | tag | ...   │ │
│  │points   │ │  ├─────────┼────────────┼─────────┼─────┼─────┤ │
│  │.csv     │ │  │ cpu     │ DI         │ %I0.1   │ M1  │ ... │ │
│  │  119行  │ │  │ di_ext  │ DI         │ %I0.2   │ M2  │ ... │ │
│  └─────────┘ │  │ ...     │ ...        │ ...     │ ... │ ... │ │
│  ┌─────────┐ │  └────────────────────────────────────────────────┘ │
│  │📄 prog_ │ │  [➕ 新增行] [🗑️ 删除行] [📋 复制行]                  │
│  │blocks   │ │                                                      │
│  │.yml     │ │                                                      │
│  │  7块    │ │                                                      │
│  └─────────┘ │                                                      │
│              │                                                      │
├──────────────┴──────────────────────────────────────────────────────┤
│ 状态: 已加载 io_points.csv (119 行) | 当前格式: Autoshop | 编码: UTF-8│
└─────────────────────────────────────────────────────────────────────┘
```

> **实现说明**：代码实际为 QSplitter 两栏布局（左=文件列表 + 右=编辑器）。批量解析结果通过 `editor.set_entries(all_entries)` 直接载入编辑器，不设独立右栏统计卡片；统计信息显示在底部状态栏。

#### 5.5.2 文件列表（左栏）

| 元素 | 说明 |
|------|------|
| 文件项 | 显示文件名 + 行数/块数徽标（如 `io_points.csv 119行`） |
| 导入按钮 | 支持多选导入（CSV/YAML/JSON/SCL/Asc 等） |
| 文件类型识别 | 基于 FormatDetector 三级识别（文件名→扩展名→内容特征） |
| 选中事件 | 点击文件项 → 右侧编辑器加载该文件解析结果 |

#### 5.5.3 变量表编辑器（中栏，VariableTableEditor）

**VariableTableModel（QAbstractTableModel，8 列）**：

| 列名 | 数据类型 | 可编辑 | 说明 |
|------|----------|--------|------|
| station | str | ✅ | 工站（如 `cpu`、`di_ext_1`、`remote_io_1`） |
| signal_type | str | ✅ | 信号类型（DI/DO/AI/AO） |
| address | str | ✅ | PLC 地址（如 `%I0.1`、`%Q0.1`、`MW10`） |
| tag | str | ✅ | 标签名（如 `Motor_Start`） |
| signal_name | str | ✅ | 信号名（变量描述） |
| device | str | ✅ | 设备（关联设备名） |
| comment | str | ✅ | 注释 |
| source_format | str | ❌ | 来源格式（Autoshop/Work3/Codesys/SCL/IntDoc/io_points 等，只读自动填充） |

> **字段对齐**：8 列字段名与 `auto_pm/ui/vartable/variable_table_editor.py` 的 `COLUMNS` 常量一致。VarEntry 9 字段中 `line_number` 为解析元数据，不作为可编辑列展示，导出时统一写 0。

**编辑器功能**：

- **工具栏**：[➕ 新增行] [🗑️ 删除行] [📋 复制行] + 导入/导出/刷新按钮
- **右键菜单**：添加行 / 删除行 / 复制行
- **导入导出**：支持 CSV/YAML/JSON 三格式导入导出
- **data_changed 信号**：编辑器内容变更时发射，供 VartableTab 更新状态栏
- **角色权限**：EDITABLE_ROLES = frozenset({"PLCEngineer", "SpecEditor"}) 可编辑，其他角色只读（V0.6.0+ 评估与后端权限系统打通）

#### 5.5.4 批量解析结果（载入编辑器）

> **实现说明**：批量解析不设独立右栏，结果直接载入编辑器。代码实际流程：`BatchParser.parse_directory()` 扫描项目目录 → 合并所有 VarEntry → `editor.set_entries(all_entries)` 载入编辑器 → 状态栏显示统计。

| 元素 | 说明 |
|------|------|
| 批量解析按钮 | 顶部工具栏 [🔄 批量解析]，扫描项目目录下所有支持格式的文件 |
| 结果载入 | 解析结果合并后直接载入编辑器（`set_entries`），不设独立统计卡片 |
| 状态栏统计 | 底部状态栏显示文件数 + 变量总数 + 格式分布 |
| 错误提示 | 解析失败的文件通过状态栏 warning 提示，不阻断整体流程 |
| 导出 | 用户可在编辑器中导出为 CSV/YAML/JSON |

#### 5.5.5 支持的文件格式（8 格式 Parser = 5 变量表 + 3 工程资产 + FormatDetector）

| 格式 | 扩展名 | Parser | 说明 |
|------|--------|--------|------|
| Autoshop | `.csv` | AutoshopParser | Autoshop 导出的 CSV 变量表 |
| Work3 | `.csv` | Work3Parser | Works3 导出的 CSV 变量表 |
| Codesys | `.csv` | CodesysParser | CoDeSys 导出的 CSV 变量表 |
| SCL | `.scl`/`.asc` | SCLParser | Siemens SCL 源文件变量声明 |
| IntDoc | `.csv`/`.xlsx` | IntDocParser | 内部文档格式变量表 |
| io_points | `.csv` | IoPointsParser | 工程资产 io_points.csv（深化 AssetSummaryService） |
| program_blocks | `.yml` | ProgramBlocksParser | 工程资产 program_blocks.yml（→ BlockEntry） |
| communications | `.yml` | CommunicationsParser | 工程资产 communications.yml（→ ChannelEntry） |

#### 5.5.6 FormatDetector 三级识别策略

```
1. 文件名匹配 → io_points.csv / program_blocks.yml / communications.yml（工程资产类）
       ↓ 未匹配
2. 扩展名匹配 → .scl/.asc → SCL / .yml → YAML 格式 / .csv → 进入内容特征识别
       ↓ 未匹配
3. 内容特征识别 → 检查 CSV 表头/列名 → Autoshop/Work3/Codesys/IntDoc
       ↓ 未匹配
   返回 Unknown（提示用户手动选择格式）
```

#### 5.5.7 数据流设计

```
用户导入文件
    ↓
FormatDetector 三级识别 → 返回格式枚举
    ↓
工厂模式选择对应 Parser → 解析为 VarTable（VarEntry 列表）
    ↓
VariableTableModel 加载 VarTable → QTableView 展示
    ↓
用户编辑（新增/修改/删除行）
    ↓
data_changed 信号发射 → VartableTab 更新状态栏
    ↓
用户导出 → VariableConverter 转换为 CSV/YAML/JSON
```

#### 5.5.8 与 CLI 的对应关系

| GUI 操作 | CLI 命令 | 说明 |
|----------|----------|------|
| 导入文件解析 | `auto-pm vartable parse <file> --format <fmt>` | 单文件解析 |
| 批量解析 | `auto-pm vartable batch-parse <dir>` | 目录批量解析 |
| 格式识别 | `auto-pm vartable detect-format <file>` | FormatDetector 三级识别 |
| 编码检测 | `auto-pm vartable detect-encoding <file>` | BOM 检测 + fallback |
| 列出格式 | `auto-pm vartable list-formats` | 列出支持的格式 |
| 列出编码 | `auto-pm vartable list-encodings` | 列出支持的编码 |
| 导出文件 | `auto-pm vartable convert <file> --output-format <fmt>` | 格式转换 |

#### 5.5.9 已知限制与后续治理方向

- **5 格式 Parser 真实样本覆盖**：当前基于 DJ-2026-005 单一样本验证，V0.5.x 评估引入第 2-3 个真实项目样本
- **VartableTab 角色权限**：目前仅为 GUI 层软约束，未与后端权限系统打通（V0.6.0+ 评估）
- **VariableConverter 字段契约**：固化后新增字段需考虑 CSV/YAML/JSON 三格式兼容性（V0.5.x 评估 schema 版本管理）
- **格式扩展**：新格式支持需补充对应 Parser + 测试，当前 5 格式已覆盖主流场景

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

---

## 十四、V2.1 变更记录

| 日期 | 版本 | 变更内容 | 操作人 |
|------|------|----------|--------|
| 2026-06-22 | V2.0 | 初版发布：总库分类导航 + 功能补全 + 交互升级；13 章设计文档；后端匹配度总览；模块化开发架构；P0/P1/P2 优先级组件清单 | TRAE |
| 2026-07-01 | V2.1 | 升级：① §5.1 项目工作区 Tab 表格更新（概览/变更/检查/文档 4 Tab 标注为 V2.0 已实现 + 变量表 Tab 从"V2.3 延后"改为"V2.3 Week4 已实现"）② 新增 §5.5 变量表 Tab 设计章节（9 小节：布局设计/文件列表/变量表编辑器/批量解析结果/支持文件格式/FormatDetector 三级识别/数据流设计/CLI 对应关系/已知限制）③ 对齐 V2.3 Week4 实际实现（VariableTableModel 8 列 + VariableTableEditor + VartableTab QSplitter 三栏 + 8 格式 Parser = 5 变量表 + 3 工程资产 + FormatDetector + 33 UI 测试）✅ 用户审核通过 | auto-pm（V0.5.0 收口批次） |

### V2.1 升级说明

- **升级原因**：V2.3 Week4（T15-T16）已交付 GUI 变量编辑器 + VartableTab，V2.0 原型设计中的"变量表 Tab V2.3 延后"已不适用
- **升级范围**：仅升级 §5 项目工作区重构章节，其他章节（§1-§4、§6-§13）保持 V2.0 原设计不变
- **审核状态**: ✅ 已审核通过（2026-07-01，用户审核），作为 V0.5.x 稳定期 GUI 演进的基线
- **后续演进**：V0.5.x 稳定期评估 8 格式 Parser 真实样本覆盖 + VartableTab 角色权限移除；V0.6.0+ 根据评估结果启动长期路线（详见 006_技术债评估报告.md §12 长期治理建议）

---

## 十五、V0.6.0 QML 重构方案（2026-07-04 新增）

### 15.1 触发背景

V0.5.x 稳定期深度审查与稳定性加固完成后（V0.5.4 第 16 次 dogfooding 闭环），PySide6 QWidget 方案的 GUI 长期维护痛点显现：

1. **资产规模庞大但低复用**：UI 层 53 文件 11,300 行 + pytest-qt 测试 28 文件 10,000 行，PySide6 特有代码 21,300 行（占 77%），QSS 样式与 Python 逻辑深度耦合
2. **AI 主力维护成本高**：QWidget 每次界面微调需修改 .py 文件 + 调整布局代码 + 跑 pytest-qt 回归，单页改动平均 5-8 次迭代才能稳定
3. **复杂组件实现吃力**：ApprovalTimeline / PropagationView / StatusMachineView 等可视化组件需手写 QPainter 或嵌 QWebEngineView
4. **离线场景适配不足**：用户 90% 离线使用（PLC 工程师同时做 PLC + Python 脚本 + 项目管理），无法依赖浏览器方案（NiceGUI/Flet 等）

### 15.2 方案选型结论

经四轮迭代式评估（NiceGUI → 客观对比 → 全方面评估 → QML 决策），按用户需求加权评分（长期迭代5/AI主力5/测试方便5/模块化4/现代化4/离线5）得出方案 B（NiceGUI）和方案 D（QML）并列 130 分，但 QML 在 6 个关键差异点胜出：

| 差异点 | QML 优势 |
|--------|---------|
| 离线使用 | 原生进程，无浏览器依赖 |
| 变量表编辑器 | QML TableView 原生虚拟化，万行数据流畅 |
| 打包分发 | PyInstaller 单文件 exe，无浏览器运行时 |
| 长期维护 | QML 声明式 UI 改动不破坏 Python 逻辑 |
| 现有代码迁移 | main_window / nav_tree / Service 层可复用 |
| 生态稳定 | Qt 官方主推方向，文档/示例/工具链完整 |

**决策**：采用方案 D（PySide6 + QML 重构）

### 15.3 重构边界

| 保留 | 重写 |
|------|------|
| 后端 Service 层（core/ 12 文件 2,850 行）| UI 层 8 大模块（53 文件 11,300 行 QWidget）|
| DB 层（5 文件 968 行）| main_window.py（部分保留：QQuickWidget 容器）|
| CLI 层（9 文件 2,429 行）| styles.py（QSS → QML 主题）|
| models 层（数据类）| pytest-qt 测试套件（28 文件 10,000 行）|
| HTML 原型设计语言 | - |

**预期复用率**：23%（6,247 行后端可复用）/ 77%（21,300 行 QWidget 特有需重写为 QML）

### 15.4 QML 架构设计

```
auto_pm/ui/
├── main_window.py              # 改造：QMainWindow + QQuickWidget 容器（< 100 行）
├── qml_bridge.py               # 新增：QmlBridge(QObject) 暴露 3 个 Service
├── qml/
│   ├── main.qml                # 入口：ApplicationWindow + StackView
│   ├── theme/
│   │   └── Theme.qml           # 主题：Colors/Typography/Spacing（20+ 设计 token）
│   ├── models/
│   │   └── project_list_model.py  # ProjectListModel(QAbstractListModel)
│   ├── components/
│   │   ├── Card.qml            # 基础组件：项目卡片
│   │   ├── Badge.qml           # 基础组件：状态徽标
│   │   ├── TabBar.qml          # 基础组件：标签栏
│   │   ├── Button.qml          # 基础组件：按钮
│   │   ├── Dialog.qml          # 基础组件：对话框
│   │   ├── ApprovalTimeline.qml    # 复杂组件：审批时间线（Canvas）
│   │   ├── PropagationView.qml     # 复杂组件：传播链（Flexbox+箭头）
│   │   ├── StatusMachineView.qml   # 复杂组件：9 步状态机（圆角徽标+箭头）
│   │   └── PhaseProgress.qml       # 复杂组件：阶段进度条
│   ├── views/
│   │   ├── ProjectListView.qml     # 项目列表页（ListView + 卡片 delegate）
│   │   ├── WorkspaceView.qml       # 项目工作区页（5 Tab）
│   │   ├── ChangeCenterView.qml    # 变更中心页
│   │   ├── OverviewTab.qml         # 工作区-概览 Tab
│   │   ├── ChangeTab.qml           # 工作区-变更 Tab
│   │   ├── CheckTab.qml            # 工作区-检查 Tab
│   │   ├── DocTab.qml              # 工作区-文档 Tab
│   │   └── VarTableTab.qml         # 工作区-变量表 Tab（TableView）
│   └── dialogs/
│       ├── NewProjectWizard.qml    # 新建项目向导（3 步分步）
│       ├── NewChangeDialog.qml     # 变更单新建
│       ├── ProjectSettingsDialog.qml   # 项目设置
│       ├── SyncCacheDialog.qml     # 同步缓存
│       ├── ImportProjectDialog.qml # 导入项目
│       ├── AboutDialog.qml         # 关于/帮助
│       ├── ReportDialog.qml        # 报告生成
│       └── SettingsDialog.qml      # 全局设置
└── (删除) navigation/ project_list/ workspace/ change_center/ dialogs/ global_pages/ vartable/ widgets/ models/ styles.py
```

### 15.5 Python ↔ QML 数据桥设计

```python
# auto_pm/ui/qml_bridge.py
class QmlBridge(QObject):
    """Python ↔ QML 数据桥，暴露后端 Service 给 QML 侧调用"""

    def __init__(self, workspace_root: Path):
        super().__init__()
        self._project_service = ProjectService(workspace_root)
        self._change_service = ChangeService(workspace_root)
        self._db_service = DbService(workspace_root)

    @Property(QObject, constant=True)
    def projectService(self) -> ProjectService:
        return self._project_service

    @Property(QObject, constant=True)
    def changeService(self) -> ChangeService:
        return self._change_service

    @Property(QObject, constant=True)
    def dbService(self) -> DbService:
        return self._db_service
```

QML 侧使用方式：
```qml
import QtQuick

ListView {
    model: bridge.projectService.list_projects()  // 直接调用 Python 方法
    delegate: ProjectCard {
        projectData: model.display
    }
}
```

### 15.6 设计系统映射（CSS → QML Theme）

| HTML 原型 CSS 变量 | QML Theme 属性 | 用途 |
|-------------------|---------------|------|
| `--sidebar-bg: #1e1e2e` | `Theme.sidebarBg: "#1e1e2e"` | 侧边栏背景 |
| `--primary: #4a6cf7` | `Theme.primary: "#4a6cf7"` | 主色 |
| `--success: #22c55e` | `Theme.success: "#22c55e"` | 成功色 |
| `--badge-plc: #2563eb` | `Theme.badgePlc: "#2563eb"` | PLC 徽标色 |
| `--phase-developing: #3b82f6` | `Theme.phaseDeveloping: "#3b82f6"` | 在研阶段色 |
| ... | ... | （共 20+ 设计 token）|

### 15.7 4 周迭代路线图

| Week | 里程碑 | 版本 | 关键交付 |
|------|--------|------|---------|
| 1 | QML 基础设施 + PoC | V0.6.0a1 | QmlBridge + PoC 项目列表页 |
| 2 | 核心页面迁移 | V0.6.0b1 | 项目列表 + 工作区 + 变更中心 QML 化 |
| 3 | 复杂组件 + 对话框 | V0.6.0rc1 | 4 可视化组件 + 变量表编辑器 + 8 对话框 |
| 4 | 测试 + 收尾 | V0.6.0 | 旧代码删除 + dogfooding 闭环 |

详细 Epic/Feature/Story/Test 拆解见：`00_项目管理/03_执行过程/2026-07-04_V0.6.0_QML重构_4周迭代计划.md`

### 15.8 dogfooding 闭环

| CHG 编号 | 主题 | 启动 | 闭环 | 状态 |
|---------|------|------|------|------|
| CHG-SCPT-2026-086 | V0.6.0 GUI QML 重构 | 2026-07-04 | 2026-07-25 | draft |

### 15.9 预期成果

| 指标 | V0.5.4 基线 | V0.6.0 目标 |
|------|------------|------------|
| UI 代码行数 | 11,300（QWidget）| ≤8,000（QML）|
| 测试代码行数 | 10,000（pytest-qt）| ≤6,000（QML TestCase + pytest 复用）|
| UI 改动平均迭代次数 | 5-8 次 | ≤3 次（QML 声明式）|
| 变量表万行渲染 FPS | 未测（QWidget 卡顿）| ≥30 FPS |
| AI 维护效率 | 低（QSS + Python 耦合）| 高（QML 声明式）|

### 15.10 风险登记

| # | 风险 | 概率 | 影响 | 缓解措施 |
|---|------|------|------|---------|
| R1 | QML 与 Python 信号槽跨语言通信踩坑 | 中 | 高 | PoC 阶段先验证（W1-S5/S6），失败则降级为 Q_PROPERTY + property bind |
| R2 | QML Canvas 性能不足（复杂可视化组件）| 低 | 中 | 限制节点数 ≤20，超出用 ListView 替代 |
| R3 | 变量表编辑器虚拟化不达预期 | 中 | 高 | 先 mock 10,000 行数据验证，失败则保留 QWidget 版本作为降级 |
| R4 | QML TestCase 与 pytest-qt 集成困难 | 低 | 中 | Qt 官方文档支持，备选用 pytest-qt 直接驱动 QML 引擎 |
| R5 | 旧代码删除遗漏引用 | 低 | 中 | grep 全量扫描 + 全量回归 + 可见模式端到端验证 |

### 15.11 V2.1 → V0.6.0 设计延续性

V0.6.0 QML 重构**完全继承** V2.1 设计系统的：
- 设计 token（CSS 变量 → QML Theme 属性）
- 8 大页面布局结构（项目列表/工作区/变更中心/规范中心/模板管理/报告中心/系统设置 + 项目工作区 5 Tab）
- 3 对话框交互流（新建项目向导/变更单新建/项目设置）
- 4 状态覆盖（加载骨架屏/空状态/正常/错误）
- 组件优先级（P0/P1/P2 清单）

**不继承**的部分（V0.6.0 重写）：
- QWidget 实现细节（QSS 样式 → QML 主题）
- pytest-qt 测试实现（→ QML TestCase）
- QPainter 自定义绘制（→ QML Canvas）

---

### V0.6.0 变更记录

| 日期 | 版本 | 变更内容 | 操作人 |
|------|------|----------|--------|
| 2026-07-04 | V0.6.0-draft | 新增 §15 QML 重构方案章节：触发背景 + 方案选型结论 + 重构边界 + QML 架构设计 + Python ↔ QML 数据桥 + 设计系统映射 + 4 周迭代路线图 + dogfooding 闭环 + 预期成果 + 风险登记 + V2.1 延续性 | TraeAI（pm-workflow Skill）|

**审核状态**：⏳ 待审核（2026-07-04，待用户审批后启动 Week 1 实施）

**附件**：
- `00_项目管理/03_执行过程/2026-07-04_V0.6.0_QML重构_4周迭代计划.md`（4 周详细 Epic/Feature/Story/Test 拆解）
- `00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-086.md`（dogfooding 变更单）
