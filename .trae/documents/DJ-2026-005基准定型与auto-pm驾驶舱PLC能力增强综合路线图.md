# DJ-2026-005 基准定型 + auto-pm 驾驶舱 PLC 能力增强 综合路线图

> **计划类型**: 综合改进路线图（三方向并行讨论）
> **创建日期**: 2026-07-28
> **创建人**: pm-workflow（Plan Mode）
> **涉及项目**:
>
> * DJ-2026-005（边框缓存机 PLC 单机项目，当前 V9.1.0）
>
> * SW-2026-008 auto-pm（自动化项目管理工具，当前 V1.1.0）
>   **用户决策**:
>
> * 三方向并行讨论（DJ-2026-005 基准定型 + auto-pm PLC 能力增强 + 驾驶舱深度集成）
>
> * FB 级 PRD 版本滞后：全量补齐到当前版本
>
> * 驾驶舱演进重心：采纳 AI 建议（后端能力优先 → 约束扩展 → GUI 优化 → 端到端集成）

***

## 一、Current State Analysis（当前状态分析）

### 1.1 DJ-2026-005 现状（V9.1.0）

**架构基线（V9.0.0 已闭环）**:

* OB1 仅 5 行顶级调度代码，全工站 VAR\_IN\_OUT 结构体整块传递

* PLC\_ST 目录标准化：`00_主程序`/`00_全局数据`/`00_程序方案`/`01_外部设备交互`/`02_输送机`/`03_取放料`/`04_打胶机送料`/`05_公共报警`/`99_基线`/`Test`

* 每个工艺模块都有 `ST_xxx.scl` UDT 类型定义 + `FB_xxx.scl` 功能块 + `PRD/` 四件套

* 已纳入 auto-pm 管理（`.copier-answers.yml` V7.1.1）

* 7 张 CHG-PLC 变更单闭环，auto-pm plc check 20P/1W/0F

**PM\_SESSION §3.1 版本演进矩阵（代码实际版本）**:

| FB                            | 代码版本    | IFC 文档版本 | 滞后量                            |
| ----------------------------- | ------- | -------- | ------------------------------ |
| FB\_1002 输送机                  | V11.1.0 | V7.0.0   | ❌ 4 版本                         |
| FB\_1003 取放料                  | V8.0.0  | V7.0.0   | ❌ 1 版本                         |
| FB\_1004 打胶送料                 | V8.1.0  | V6.0.0   | ❌ 2 版本                         |
| FB\_2001 公共报警                 | V3.0.0  | V6.0.0   | ⚠️ 文档反而比代码高（文档未同步代码 V3.0.0 重构） |
| FB\_ExternalDeviceInteraction | V6.0.0  | V4.1.0   | ❌ 2 版本                         |

**关键缺陷清单**:

* **P0-1**: FB 级 PRD 文档版本严重滞后（5 个 FB 全部滞后）

* **P0-2**: IFC 文档关联源码路径未更新（如 `conveyor/FB_1002_*.scl` 实际是 `02_输送机/FB_1002_*.scl`）

* **P0-3**: 未消除的代码缺陷（FB\_1004 轴控架构落后、安全门信号未纳入 FB\_ExternalDeviceInteraction）

* **P0-4**: TIA Portal 编译验证、.scltest 真实运行、现场复核均未完成

* **P1-1**: PM\_SESSION §3.1 矩阵与 FB 级 PRD 不一致

* **P1-2**: Spec Snapshot 版本漂移（PROJ-016 V1.1.0→V1.2.0, CHG-040 V2.1.0→V2.2.0）

* **P1-3**: 99\_基线只有 V1.0.0，V9.0.0 重构后未升级

* **P2-1**: OB1/DB1 级 PRD 待更新到 V6.0.0

* **P2-2**: 缺少单机模板抽取指南

* **P2-3**: 测试覆盖率低（仅 1 个 basic\_test.scltest，11 个 TC）

### 1.2 auto-pm 现状（V1.1.0）

**已实现能力**:

* 14 个 CLI 子命令组：`project`/`change`/`delivery`/`doc`/`plc`/`python`/`spec`/`template`/`vartable`/`gui`/`pm-session`/`ledger`/`constraint`/`workflow`

* 五层架构：CLI → Application Facade → Core Service → DB Repository → Models

* 6 个工作域 + Modbus 联调工坊

* 9 个约束工作流 YAML 定义

* 72 次 dogfooding 闭环

* 已纳管 5 个样例项目（DJ-2026-002/022/100/901/902）

**PLC 项目管理能力缺口**:

* **G1**: plc check 只检查结构存在性（.plc.json/PM\_SESSION/PRD/目录），不检查内容质量

* **G2**: 无法检测 FB 级 PRD 文档版本与代码版本是否同步（FB\_1002 IFC=V7.0.0 但代码 V11.1.0 检测不出来）

* **G3**: 缺少 SCL 静态分析集成（命名/语法/接口对齐）

* **G4**: 缺少 SysLib 依赖完整性检查（FB\_1011/FB\_1012 抽到 SysLib 后，.plc.json libraries 是否正确声明）

* **G5**: 缺少 FB 级 PRD 完整性矩阵视图（哪个 FB 缺 IFC/DSN/CHG/UM）

* **G6**: 缺少 PLC 项目"健康度"评分（只有 PLC 检查通过/失败二元状态）

* **G7**: 缺少 PLC 项目版本演进可视化（PM\_SESSION §3.1 矩阵手工维护）

* **G8**: 缺少 .scltest 测试运行器集成

* **G9**: 约束工作流未覆盖 PLC 域（plc-rules.md 强制规则未 YAML 化）

* **G10**: Modbus 工坊与 PLC 项目 IO 点表/通信配置无关联

* **G11**: 缺少 PLC 项目交付物自动打包

* **G12**: 缺少"基准模板对比"能力（基于 DJ-2026-005 复制新项目后，无法检测差异）

***

## 二、Proposed Changes（改进方案）

### 总体策略：四阶段递进，后端能力优先

```
阶段 1 (P0): DJ-2026-005 基准定型 + auto-pm PLC 检查器深化
    ├─ A. DJ-2026-005 FB 级 PRD 全量补齐
    ├─ B. auto-pm 新增 PRD-代码版本一致性检查器
    └─ C. auto-pm 新增 SysLib 依赖完整性检查

阶段 2 (P1): 约束系统覆盖 PLC 域 + 工作流扩展
    ├─ D. plc-rules.md 强制规则 YAML 化
    ├─ E. CHG 闭环门禁强化（PLC 域验证项）
    └─ F. 端到端工作流编排（模板复制 → PRD 同步）

阶段 3 (P2): GUI 体验优化 + 可视化能力
    ├─ G. PLC 项目健康度仪表盘
    ├─ H. FB 完整性矩阵热力图
    └─ I. 版本演进时间线可视化

阶段 4 (P3): 端到端集成 + 交付自动化
    ├─ J. .scltest 测试运行器集成
    ├─ K. SysLib 依赖变更影响分析
    ├─ L. Modbus 工坊与 PLC 项目关联
    └─ M. PLC 项目交付物自动打包
```

***

### 阶段 1: DJ-2026-005 基准定型 + auto-pm PLC 检查器深化（P0）

#### A. DJ-2026-005 FB 级 PRD 全量补齐

**目标**: 把 5 个 FB 的 IFC/DSN/CHG/UM 全部补到代码实际版本

**任务清单**:

| 序号  | 任务                                                        | 文件路径                                                                                                                         | 工作量                                             |
| --- | --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| A1  | FB\_1002 IFC/DSN 从 V7.0.0 升级到 V11.1.0                     | `02_PLC程序/PLC_ST/02_输送机/PRD/接口文档_IFC-FB1002-SingleLayerConveyor.md` + `详细设计说明书_DSN-FB1002-SingleLayerConveyor.md`            | 高（4 版本跨度，需补 V8/V9/V10/V11 四轮 VAR\_IN\_OUT 重构说明） |
| A2  | FB\_1003 IFC/DSN 从 V7.0.0 升级到 V8.0.0                      | `02_PLC程序/PLC_ST/03_取放料/PRD/接口文档_IFC-FB1003-PickPlace.md` + `详细设计说明书_DSN-FB1003-PickPlace.md`                                | 中（1 版本跨度，主要补 VAR\_IN\_OUT 整块传递）                 |
| A3  | FB\_1004 IFC/DSN 从 V6.0.0 升级到 V8.1.0                      | `02_PLC程序/PLC_ST/04_打胶机送料/PRD/接口文档_IFC-FB1004-GlueMachineFeeder.md` + `详细设计说明书_DSN-FB1004-GlueMachineFeeder.md`              | 中（2 版本跨度，补 V7 VAR\_IN\_OUT + V8.1 消抖参数）         |
| A4  | FB\_2001 IFC/DSN 从 V6.0.0 修正到 V3.0.0                      | `02_PLC程序/PLC_ST/05_公共报警/PRD/接口文档_IFC-FB2001-CommonAlarm.md` + `详细设计说明书_DSN-FB2001-CommonAlarm.md`                           | 中（文档版本反而比代码高，需要核对实际代码状态）                        |
| A5  | FB\_ExternalDeviceInteraction IFC/DSN 从 V4.1.0 升级到 V6.0.0 | `02_PLC程序/PLC_ST/01_外部设备交互/PRD/接口文档_IFC-FB3001-ExternalDeviceInteraction.md` + `详细设计说明书_DSN-FB-ExternalDeviceInteraction.md` | 中（2 版本跨度，补 V5/V6 安全门信号纳入）                       |
| A6  | 修复所有 IFC 文档关联源码路径                                         | 所有 5 个 IFC 文档的"关联源码"字段                                                                                                       | 低（机械替换 `conveyor/` → `02_输送机/` 等）               |
| A7  | OB1/DB1 级 PRD 升级到 V6.0.0                                  | `02_PLC程序/PLC_ST/00_主程序/PRD/` + `02_PLC程序/PLC_ST/00_全局数据/PRD/`                                                               | 中（OB1 V9.0.0 架构 + DB1 V6.0.0 UDT 类型）            |
| A8  | 99\_基线 SRC 升级到 V9.0.0                                     | `02_PLC程序/PLC_ST/99_基线/源程序功能基线_SRC-DJ-2026-005-V1.0.0.md` → 新建 V9.0.0 版本                                                     | 高（需要重新提取 V9.0.0 架构下的 I/O 映射/状态机/报警体系）           |
| A9  | PM\_SESSION §3.1 矩阵与 FB 级 PRD 同步                          | `PM_SESSION_DJ-2026-005.md` §3.1 + §4.4                                                                                      | 低（核对版本号一致性）                                     |
| A10 | CHG-PLC-2026-008 变更单闭环                                    | `04_监控/01_变更管理/01_变更单/CHG-PLC/CHG-PLC-2026-008.md`                                                                           | 中（12 章节完整填写）                                    |

**实施约束**:

* 必须通过 `auto-pm change create` CLI 创建 CHG-PLC-2026-008

* 修改 .scl 源码前必须触发 `plc-electrical-engineer` 技能（本轮只改 PRD 文档，不改 .scl）

* 每个 FB 的 PRD 升级需通过 `plc check` 验证（20P/1W/0F 保持）

* 台账对账强制：CHG 闭环后执行 `ledger reconcile DJ-2026-005 --auto-fix`

**未消除的 P0 代码缺陷处理**:

* FB\_1004 轴控架构落后：**本轮不修复**，登记为 CHG-PLC-2026-009 待办（需要触发 plc-electrical-engineer 技能）

* 安全门信号未纳入 FB\_ExternalDeviceInteraction：**本轮不修复**，登记为 CHG-PLC-2026-010 待办（同上）

理由：PRD 文档补齐是"记录现状"，代码缺陷修复是"改变现状"，两者不能混在一个 CHG 中。

***

#### B. auto-pm 新增 PRD-代码版本一致性检查器

**目标**: 让 plc check 能自动检测 FB 级 PRD 文档版本与代码版本是否同步

**实现方案**:

1. **新增检查器** `auto_pm/plc/checkers/prd_version_consistency.py`

   * 解析 `.scl` 文件头部注释提取代码版本（如 `// V9.0.0 (2026-07-26): CHG-PLC-2026-006`）

   * 解析 `PRD/接口文档_IFC-*.md` frontmatter 或 §0 文档基础信息表提取文档版本

   * 对比两者，差异 ≥1 版本时告警

2. **扩展 PlcChecker** `auto_pm/plc/checker.py`

   * 在 `check_project()` 中新增检查项 `PRD_VERSION_CONSISTENCY`

   * 检查结果分级：PASS（版本一致）/ WARN（差异 1 版本）/ FAIL（差异 ≥2 版本）

3. **测试用例** `tests/plc/test_prd_version_consistency.py`

   * TC01: 版本一致 → PASS

   * TC02: 文档滞后 1 版本 → WARN

   * TC03: 文档滞后 2 版本 → FAIL

   * TC04: 文档超前代码 → WARN

   * TC05: 无法解析版本 → SKIP

   * TC06: 多 FB 项目全量检查

   * TC07: DJ-2026-005 真实样例验证（修复后应该 PASS）

4. **CHG 变更单**: CHG-SCPT-2026-143（SCPT+OPT+MODULE+SYSTEM）

**预期收益**:

* 防止未来再次出现 FB\_1002 滞后 4 版本这类问题

* 作为 DJ-2026-005 基准定型后的"持续守门员"

***

#### C. auto-pm 新增 SysLib 依赖完整性检查

**目标**: 检测项目 .plc.json 是否正确声明 SysLib libraries 引用

**实现方案**:

1. **新增检查器** `auto_pm/plc/checkers/syslib_dependency.py`

   * 扫描所有 .scl 文件，提取 `FB_1011`/`FB_1012`/`FB_TON`/`FB_CTU`/`FB_CTD`/`FB_R_TRIG`/`FB_F_TRIG` 等 SysLib FB 调用

   * 读取 `.plc.json` 的 `libraries` 字段

   * 对比：调用了 SysLib FB 但 .plc.json 未声明 → FAIL

2. **扩展 PlcChecker**

   * 新增检查项 `SYSLIB_DEPENDENCY`

3. **测试用例** `tests/plc/test_syslib_dependency.py`

   * TC01: 无 SysLib 调用 → SKIP

   * TC02: 有 SysLib 调用且 .plc.json 声明 → PASS

   * TC03: 有 SysLib 调用但 .plc.json 未声明 → FAIL

   * TC04: DJ-2026-005 真实样例验证

4. **CHG 变更单**: CHG-SCPT-2026-144（SCPT+OPT+MODULE+SYSTEM）

***

### 阶段 2: 约束系统覆盖 PLC 域 + 工作流扩展（P1）

#### D. plc-rules.md 强制规则 YAML 化

**目标**: 把 plc-rules.md 中的强制规则机化为 YAML 约束定义

**任务清单**:

| 序号 | 约束 ID         | 规则来源                                              | YAML 文件                                                              |
| -- | ------------- | ------------------------------------------------- | -------------------------------------------------------------------- |
| D1 | CST-SKILL-001 | 修改 .scl 前必须触发 plc-electrical-engineer 技能（已存在，需复核） | `auto_pm/constraint/definitions/skill_change_requires_chg.yaml`（已存在） |
| D2 | CST-PLC-001   | 修改 .scl 源码前必须创建 CHG-PLC 变更单                       | `auto_pm/constraint/definitions/plc_chg_before_scl.yaml`（新建）         |
| D3 | CST-PLC-002   | .scl 文件变量命名必须符合 LSP-905 §3（小驼峰）                   | `auto_pm/constraint/definitions/plc_naming_lsp905.yaml`（新建）          |
| D4 | CST-PLC-003   | .scl 文件注释必须符合 LSP-904（英文半角标点、禁止嵌套）                | `auto_pm/constraint/definitions/plc_comment_lsp904.yaml`（新建）         |
| D5 | CST-PLC-004   | FB 级 PRD 四件套完整性（IFC+DSN+CHG+UM）                   | `auto_pm/constraint/definitions/plc_prd_completeness.yaml`（新建）       |
| D6 | CST-PLC-005   | .plc.json libraries 字段与 SysLib 调用一致性              | `auto_pm/constraint/definitions/plc_syslib_libraries.yaml`（新建）       |

**实施约束**:

* 每个约束需补齐 `checker.py` 检查逻辑 + `healer.py` 自愈逻辑（可选）

* 测试覆盖率 ≥90%

* 通过 `constraint list/check/guard/verify/heal` CLI 命令验证

***

#### E. CHG 闭环门禁强化（PLC 域验证项）

**目标**: CHG-PLC 变更单闭环时强制验证 PLC 域特定项

**实现方案**:

1. **扩展 CHG §10.1 验证项模板**

   * 新增 PLC 域专属验证项：

     * `plc_check_passed`: auto-pm plc check 20P/0W/0F

     * `prd_version_consistent`: PRD-代码版本一致性检查通过

     * `syslib_dependency_complete`: SysLib 依赖完整性检查通过

     * `scl_static_analysis`: SCL 静态分析无错误（如启用）

     * `tia_portal_compiled`: TIA Portal 编译通过（可选，需人工执行）

     * `scltest_passed`: .scltest 测试通过（可选，需 LSP 测试运行器）

2. **修改 ChangeService.transition\_status()**

   * 在 `completed` 状态流转时，对 PLC 项目额外检查上述验证项

   * 未通过则阻止闭环（除非 `--allow-partial-verification`）

3. **CHG 变更单**: CHG-SCPT-2026-145（SCPT+OPT+MODULE+SYSTEM）

***

#### F. 端到端工作流编排（模板复制 → PRD 同步）

**目标**: 用 WorkflowEngine 编排 PLC 项目全生命周期

**实现方案**:

1. **新建工作流** `auto_pm/constraint/workflows/plc_project_lifecycle.yaml`

   ```yaml
   id: WF-PLC-001
   name: PLC 项目全生命周期
   steps:
     - template_apply: 基于 plc-standard-project 模板创建项目
     - plc_init: auto-pm plc init <project_id>
     - code_development: 编码阶段（触发 plc-electrical-engineer 技能）
     - prd_sync: PRD 文档同步到代码版本
     - plc_check: auto-pm plc check <project_id>
     - scltest: .scltest 测试运行
     - tia_compile: TIA Portal 编译验证（人工）
     - chg_closeout: CHG 变更单闭环
     - ledger_reconcile: 台账对账
   ```

2. **CLI 集成**: `auto-pm workflow run WF-PLC-001 --project <project_id>`

3. **CHG 变更单**: CHG-SCPT-2026-146（SCPT+OPT+MODULE+SYSTEM）

***

### 阶段 3: GUI 体验优化 + 可视化能力（P2）

#### G. PLC 项目健康度仪表盘

**目标**: 在驾驶舱 GUI 展示 PLC 项目多维度健康度评分

**实现方案**:

1. **新增 DashboardService 方法** `get_plc_project_health(project_id)`

   * 返回多维度评分：

     * 结构合规度（plc check 通过率）

     * PRD 完整度（IFC/DSN/CHG/UM 四件套覆盖率）

     * PRD 版本一致性（文档版本 vs 代码版本）

     * SysLib 依赖完整性

     * 测试覆盖率（.scltest TC 数量）

     * CHG 闭环率（已闭环/总数）

   * 综合评分 0-100

2. **QML 组件** `PlcHealthDashboard.qml`

   * 雷达图展示 6 维度

   * 红黄绿三色评分

   * 点击维度钻取详情

3. **CHG 变更单**: CHG-SCPT-2026-147（SCPT+OPT+MODULE+SYSTEM）

***

#### H. FB 完整性矩阵热力图

**目标**: 一眼看出哪个 FB 缺哪种 PRD 文档

**实现方案**:

1. **新增 Service** `PlcPrdMatrixService`

   * 扫描所有 FB 目录，统计 IFC/DSN/CHG/UM 四件套

   * 返回矩阵数据：`{fb_id: {ifc: bool, dsn: bool, chg: bool, um: bool}}`

2. **QML 组件** `FbPrdMatrixView.qml`

   * 表格形式：行=FB，列=IFC/DSN/CHG/UM

   * 单元格颜色：绿=存在且版本一致，黄=存在但版本滞后，红=缺失

   * 点击单元格跳转到对应文档

3. **CHG 变更单**: CHG-SCPT-2026-148（SCPT+OPT+MODULE+SYSTEM）

***

#### I. 版本演进时间线可视化

**目标**: 自动从 PM\_SESSION §3.1 解析版本演进矩阵，生成时间线

**实现方案**:

1. **扩展 PmSessionParser**

   * 新增 `parse_version_evolution_matrix()` 方法

   * 解析 §3.1 表格，返回结构化数据

2. **QML 组件** `VersionEvolutionTimeline.qml`

   * 横轴=版本（V7.0.0 → V9.1.0）

   * 纵轴=FB（FB\_1002/FB\_1003/FB\_1004/FB\_2001/FB\_External）

   * 节点=CHG 编号 + 架构特征

   * 点击节点跳转到 CHG 文档

3. **CHG 变更单**: CHG-SCPT-2026-149（SCPT+OPT+MODULE+SYSTEM）

***

### 阶段 4: 端到端集成 + 交付自动化（P3）

#### J. .scltest 测试运行器集成

**目标**: 在驾驶舱内运行 .scltest 并查看结果

**实现方案**:

* 调研 LSP 测试运行器 API（VS Code 测试资源管理器集成）

* 新增 `ScltestRunner` 服务

* GUI 展示 TC 通过/失败状态

**CHG 变更单**: CHG-SCPT-2026-150（SCPT+OPT+MODULE+SYSTEM）

***

#### K. SysLib 依赖变更影响分析

**目标**: 当 SysLib FB 接口变化时，自动检测影响哪些项目

**实现方案**:

* 扫描所有项目的 SysLib 调用

* 当 SysLib 版本升级时，对比接口差异

* 生成影响范围报告

**CHG 变更单**: CHG-SCPT-2026-151（SCPT+OPT+MODULE+SYSTEM）

***

#### L. Modbus 工坊与 PLC 项目关联

**目标**: Modbus 调试工坊可读取 PLC 项目的 IO 点表/通信配置

**实现方案**:

* 解析 `工程资产/communications.yml` + `io_points.csv`

* 在 Modbus 工坊中预加载项目配置

* 支持按项目切换调试上下文

**CHG 变更单**: CHG-SCPT-2026-152（SCPT+OPT+MODULE+SYSTEM）

***

#### M. PLC 项目交付物自动打包

**目标**: 基于工程资产 + 程序文档自动生成交付包

**实现方案**:

* 新增 `DeliveryPackager` 服务

* 打包内容：.scl 源码 + .plc.json + 工程资产 + 程序文档 + PRD + CHG 闭环证据

* 输出 ZIP 包，命名 `DJ-YYYY-XXX_PLC_交付包_V<version>.zip`

* 旧版本归档到 `06_文档与交付/归档/`

**CHG 变更单**: CHG-SCPT-2026-153（SCPT+OPT+MODULE+SYSTEM）

***

## 三、Assumptions & Decisions（假设与决策）

### 决策记录

| ID   | 决策点                   | 选项                                     | 决策            | 理由                                   |
| ---- | --------------------- | -------------------------------------- | ------------- | ------------------------------------ |
| D-01 | FB 级 PRD 滞后处理方式       | A.全量补齐 / B.抽取独立模板 / C.工具驱动补齐 / D.暂不处理  | A.全量补齐        | 用户决策：一次到位，避免遗留                       |
| D-02 | 驾驶舱演进重心               | A.PLC 深化 / B.GUI 优化 / C.约束扩展 / D.端到端集成 | 四阶段递进：A→C→B→D | AI 建议：后端能力是基础，GUI 是表现层               |
| D-03 | DJ-2026-005 P0 代码缺陷处理 | 与 PRD 补齐同步 / 单独 CHG                    | 单独 CHG        | PRD 补齐是"记录现状"，代码修复是"改变现状"，不能混在一个 CHG |
| D-04 | 99\_基线 SRC 升级         | V1.0.0 保留 / 新建 V9.0.0                  | 新建 V9.0.0     | V1.0.0 是历史基线，V9.0.0 是当前架构基线，两者并存     |
| D-05 | 约束工作流 PLC 域覆盖范围       | 仅 .scl 修改 / 全 PLC 生命周期                 | 全 PLC 生命周期    | 防止未来再次出现 PRD 滞后、SysLib 依赖缺失等问题       |

### 假设

1. **DJ-2026-005 的 .scl 代码版本号准确**：PM\_SESSION §3.1 矩阵显示的 V11.1.0/V8.0.0/V8.1.0/V3.0.0/V6.0.0 是真实代码版本
2. **auto-pm 五层架构稳定**：Facade/Bridge/Service 分层不会在计划实施期间大改
3. **LSP-905/LSP-904/LSP-907 规范版本稳定**：不会在计划实施期间发布破坏性变更
4. **TIA Portal 编译验证由人工执行**：auto-pm 不集成 TIA Portal 编译能力（非本地化场景）

### 依赖与风险

| 依赖                                 | 风险                 | 缓解措施                                  |
| ---------------------------------- | ------------------ | ------------------------------------- |
| FB 级 PRD 补齐需要核对 .scl 源码            | 工作量大（A1 任务 4 版本跨度） | 分 CHG 推进，每个 FB 一个子任务                  |
| auto-pm 新增检查器需要 DJ-2026-005 真实样例验证 | 真实样例可能暴露检查器 bug    | 先在 DJ-2026-005 修复前验证检查器能检出问题，修复后再验证通过 |
| 约束工作流 PLC 域覆盖可能影响开发效率              | 规则过严会拖慢迭代          | 先 warning 级别，验证 1-2 个迭代后再升级 error     |
| GUI 可视化依赖后端数据完整性                   | 后端数据不全时 GUI 展示空数据  | 阶段 3 在阶段 1/2 完成后启动                    |

***

## 四、Verification Steps（验证步骤）

### 阶段 1 验证

```powershell
# 1. 激活 venv
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"

# 2. DJ-2026-005 PRD 补齐验证
auto-pm -w "c:\Users\fubai\Desktop\My_Workspace" plc check DJ-2026-005
# 预期：20P/1W/0F（保持）+ 新增 PRD_VERSION_CONSISTENCY 检查项 PASS

# 3. auto-pm 新检查器验证
auto-pm -w "c:\Users\fubai\Desktop\My_Workspace" plc check DJ-2026-005 --verbose
# 预期：新增 PRD_VERSION_CONSISTENCY + SYSLIB_DEPENDENCY 检查项

# 4. 单元测试
python -m pytest tests/plc/test_prd_version_consistency.py -v
python -m pytest tests/plc/test_syslib_dependency.py -v

# 5. 全量回归
python -m pytest --no-cov --timeout=60

# 6. 台账对账
auto-pm -w "c:\Users\fubai\Desktop\My_Workspace" ledger reconcile DJ-2026-005 --auto-fix
```

### 阶段 2 验证

```powershell
# 1. 约束检查
auto-pm -w "c:\Users\fubai\Desktop\My_Workspace" constraint list
# 预期：9 → 14 个约束定义

auto-pm -w "c:\Users\fubai\Desktop\My_Workspace" constraint check --project DJ-2026-005
# 预期：PLC 域约束全部通过

# 2. 工作流验证
auto-pm -w "c:\Users\fubai\Desktop\My_Workspace" workflow list
# 预期：新增 WF-PLC-001 PLC 项目全生命周期
```

### 阶段 3 验证

```powershell
# 1. GUI 冒烟测试（可见模式）
$env:GUI_VISIBLE=1
python -m pytest tests/qml/test_plc_health_dashboard.py -v
python -m pytest tests/qml/test_fb_prd_matrix_view.py -v
python -m pytest tests/qml/test_version_evolution_timeline.py -v

# 2. 真实样例验证
auto-pm -w "c:\Users\fubai\Desktop\My_Workspace" gui
# 在 GUI 中打开 DJ-2026-005，验证三个新视图
```

### 阶段 4 验证

```powershell
# 1. .scltest 集成验证
auto-pm -w "c:\Users\fubai\Desktop\My_Workspace" plc test DJ-2026-005
# 预期：运行 basic_test.scltest 并返回结果

# 2. 交付物打包验证
auto-pm -w "c:\Users\fubai\Desktop\My_Workspace" delivery package DJ-2026-005
# 预期：生成 DJ-2026-005_PLC_交付包_V9.1.0.zip
```

***

## 五、实施优先级与里程碑

### 里程碑总览

| 里程碑                   | 内容                       | 预计周期  | 前置条件          |
| --------------------- | ------------------------ | ----- | ------------- |
| M1: DJ-2026-005 基准定型  | 阶段 1-A（FB 级 PRD 全量补齐）    | 1-2 周 | 用户审批本计划       |
| M2: auto-pm PLC 检查器深化 | 阶段 1-B + 1-C（新增 2 个检查器）  | 1 周   | M1 完成（提供真实样例） |
| M3: 约束系统 PLC 域覆盖      | 阶段 2-D + 2-E + 2-F       | 1-2 周 | M2 完成         |
| M4: GUI 可视化           | 阶段 3-G + 3-H + 3-I       | 2-3 周 | M3 完成         |
| M5: 端到端集成             | 阶段 4-J + 4-K + 4-L + 4-M | 3-4 周 | M4 完成         |

### 建议启动顺序

**第一波（立即启动）**:

* M1: DJ-2026-005 FB 级 PRD 全量补齐（CHG-PLC-2026-008）

  * 用户决策"全量补齐"，可立即启动

  * 工作量最大，需先启动

**第二波（M1 完成后）**:

* M2: auto-pm 新增 PRD-代码版本一致性检查器 + SysLib 依赖检查器

  * 用 M1 修复前的 DJ-2026-005 作为"反例"验证检查器能检出问题

  * 用 M1 修复后的 DJ-2026-005 作为"正例"验证检查器通过

**第三波（M2 完成后）**:

* M3: 约束系统 PLC 域覆盖

  * 依赖 M2 的检查器作为约束执行引擎

**后续（M3 完成后）**:

* M4 + M5 可并行推进

***

## 六、Open Questions（待确认问题）

1. **FB\_2001 版本矛盾**：PM\_SESSION §3.1 显示 FB\_2001 代码版本 V3.0.0，但 IFC 文档版本 V6.0.0。需要核对 .scl 源码确认真实版本（是代码降级了还是文档从未同步？）
2. **99\_基线 V9.0.0 升级方式**：是重新提取 V9.0.0 架构下的 I/O 映射/状态机/报警体系，还是基于 V1.0.0 增量更新？
3. **约束工作流初始级别**：新增的 5 个 PLC 约束（D2-D6）初始是 warning 还是 error？建议 warning，验证 1-2 个迭代后再升级
4. **GUI 可视化优先级**：G（健康度仪表盘）/H（FB 矩阵热力图）/I（版本演进时间线）哪个最先做？建议 H（最实用，能直接暴露 PRD 滞后问题）
5. **.scltest 集成方式**：是调用 VS Code 测试资源管理器 API，还是独立实现 LSP 测试运行器？需要调研
6. **交付物打包范围**：是否包含 .gx3 编译器文件？用户记忆中提到"最终交付产品需打包为可直接运行的exe"，但 PLC 项目交付物通常是源码 + 文档，不是 exe

***

## 七、References（参考文件）

### DJ-2026-005 关键文件

* `PM_SESSION_DJ-2026-005.md`（项目真源）

* `02_PLC程序/PLC_ST/00_主程序/OB1.scl`（V9.0.0 顶级调度器）

* `02_PLC程序/PLC_ST/02_输送机/PRD/接口文档_IFC-FB1002-SingleLayerConveyor.md`（V7.0.0，待升级到 V11.1.0）

* `02_PLC程序/PLC_ST/99_基线/源程序功能基线_SRC-DJ-2026-005-V1.0.0.md`（V1.0.0，待升级到 V9.0.0）

### auto-pm 关键文件

* `PM_SESSION_SW-2026-008.md`（项目真源）

* `auto_pm/plc/checker.py`（PLC 检查器，待扩展）

* `auto_pm/plc/models.py`（PLC 数据模型，含 STD\_DIRS/STD\_PRDS 常量）

* `auto_pm/constraint/definitions/`（9 个约束 YAML，待新增 5 个 PLC 域约束）

* `02_规划/001_产品需求文档_PRD.md`（V3.2.0，6 工作域 + Modbus 工坊）

### 规范文件

* `0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范_LSP.md`（命名/语法/代码结构）

* `0100_PLC自动化/00_通用规范/PLC编程/907_项目配置规范_LSP.md`（.plc.json + 目录结构）

* `0100_PLC自动化/.trae/rules/plc-rules.md`（PLC 技术栈规则，强制规则待 YAML 化）

* `.trae/rules/project-rule.md`（全局开发规则）

* `.trae/rules/git-commit-message.md`（提交信息规范）

