# DJ单机项目管理工具迭代规划

## Summary

- 目标：在现有 `SW-2026-005 PLC项目管理工具` 基础上迭代，不新建新工具，使其能够对 `DJ` 单机项目进行有序管理，优先支持 `DJ-2026-005` 这类目录结构、PLC源码、文档体系、变更管理和测试资产。
- 方法：采用“文档先行 + 增量开发 + 不重复造文档”的策略，先固化 DJ 单机项目工作流，再补齐 GUI 能力、变更管理闭环、测试与发布门禁。
- 计划周期：按 `8-10周` 设计 5 个里程碑，先做最小可落地版本，再逐步增强规则校验、GUI 自动化测试和发布门禁。
- 范围边界：本方案明确忽略 `DJ-2026-005/.trae` 与 `DJ-2026-005/.plc-out` 内容，不把它们纳入项目建模、校验、索引与统计范围。

## Current State Analysis

### 1. 现有工具现状

- 现有工具入口和骨架已完整：`main.py`、`src/core/`、`src/ui/`、`src/services/`、`src/checkers/`、`src/diagnostics/`、`src/parsers/` 均已具备。
- 架构基础合理：`EventBus + MainWindow薄壳 + Service分层 + Checker/Diagnostic基础设施` 已可承载后续产品化扩展。
- 已有能力偏“通用 PLC 项目管理”，但对“DJ 单机项目”的建模仍不够深：
  - 项目服务更偏模板创建和基础扫描；
  - 文档服务更偏 Markdown 生成/保存；
  - 规范检查和诊断已有引擎，但尚未和 DJ 项目目录/资产模型深度绑定；
  - GUI 里存在占位页，尚未形成完整的单机项目工作流闭环。

### 2. DJ-2026-005 模板现状

- 该项目本质上是一个“单机项目模板 + 示例工程”，结构完整，覆盖：
  - `00_项目管理`：立项、需求、变更管理
  - `01_需求与设计`：需求、规范、软件方案
  - `02_PLC程序`：PLC 源码、变量表、程序文档、测试文件
  - `03_HMI设计`、`04_现场调试`、`06_文档与交付`、`09_项目总结`、`10_知识库`
- `02_PLC程序/通用ST程序及变量表` 已具备可管理的关键资产：
  - `OB1/OB1.scl`
  - `DB1/GlobalVars.db`
  - 多个工站功能块 `.scl`
  - 功能块 PRD 文档（`DSN/IFC/UM/CHG/ALM`）
  - `Test/basic_test.scltest`
  - `.plc.json`
- 根目录和 PLC 子目录均存在 `.plc.json`，且字段名已正确使用 `libraries`，符合现有规则要求。

### 3. 当前最关键的问题

- 工具侧缺少“DJ 单机项目类型”的显式模型，无法把目录、文档、PLC、测试、变更作为同一项目的结构化资产统一管理。
- 变更管理虽有目录和文档规范，但工具侧未形成“变更单 -> 影响分析 -> 文档同步 -> PLC检查 -> 测试验证 -> 发布归档”的闭环。
- 文档资产很多，但目前仍偏人工维护，缺少“只更新现有文档、不重复新增”的规则约束和落地机制。
- GUI 具备基础外壳，但未围绕 DJ 单机项目的真实流程组织核心页面。
- GUI 测试尚未形成体系，未来一旦扩展变更管理、文档联动和流程门禁，回归风险会快速上升。

## Proposed Changes

### 00. 产品定位与边界收敛

#### 更新文件

- `README.md`
- `05_docs/02_技术文档/007_架构设计文档_ARCH-V1.0.0.md`
- `05_docs/02_技术文档/008_详细设计文档_DES-V1.0.0.md`
- `05_docs/02_技术文档/009_API接口文档_INT-V1.0.0.md`
- `05_docs/02_技术文档/010_代码结构说明_DEV-V1.0.0.md`

#### 变更内容

- 明确工具定位为“PLC 项目管理工具 V2.x：支持 DJ 单机项目标准化管理”。
- 在现有文档中补充：
  - 项目类型：`DJ_SINGLE_MACHINE`
  - 忽略规则：`.trae`、`.plc-out`
  - 文档先行原则
  - 不重复新增文档原则
  - 变更管理作为一等核心模块
- 所有说明在已有文档内增量更新，不新造一套平行文档。

#### 为什么这样做

- 用户明确要求基于现有工具迭代，且“文档先行、不允许重复文档”；因此必须先把产品边界和设计原则写入现有工具文档，后续编码和测试才能保持一致。

### 01. 建立 DJ 单机项目资产模型

#### 更新文件

- `src/core/constants.py`
- `src/models/project.py`
- `src/models/document.py`
- `src/services/project_service.py`
- `src/services/document_service.py`

#### 新增文件

- `src/models/change_request.py`
- `src/models/project_artifact.py`
- `src/services/artifact_registry_service.py`
- `src/templates/project_structures/DJ_single_machine.json`
- `src/templates/specs/dj_single_machine_artifacts.json`

#### 变更内容

- 在 `constants.py` 增加：
  - 项目类型：`DJ_SINGLE_MACHINE`
  - 资产类型：`PLC_SOURCE / PLC_DB / PLC_TEST / DOC_REQ / DOC_DSN / DOC_IFC / DOC_CHG / DOC_IO / DOC_HMI / DOC_DELIVERY / CHANGE_ORDER`
  - 生命周期阶段：`立项 / 设计 / 开发 / 联调 / 测试 / 交付 / 维护`
- 在 `project.py` 增加项目画像字段：
  - `project_type`
  - `artifact_roots`
  - `workflow_stage`
  - `change_status_summary`
- 通过 `artifact_registry_service.py` 建立 DJ 目录与资产清单映射，重点识别：
  - `00_项目管理/04_变更管理`
  - `02_PLC程序/通用ST程序及变量表`
  - `03_HMI设计`
  - `04_现场调试`
  - `06_文档与交付`
- `project_service.py` 增加“导入 DJ 单机项目”能力：
  - 扫描真实目录
  - 忽略 `.trae` / `.plc-out`
  - 自动识别项目资产
  - 生成资产索引缓存
- `document_service.py` 增加“更新现有文档”模式：
  - 同类文档已存在时优先更新现有文件
  - 新建前必须检查是否已存在同类权威文档
  - 维护唯一文档源映射

#### 为什么这样做

- DJ 项目不是单一 PLC 目录，而是覆盖项目管理、PLC、HMI、测试和交付的复合型项目。
- 如果没有统一的资产模型，后续 GUI、变更管理、规则检查和工作流无法落在同一实体上。

### 02. 把变更管理做成核心工作流

#### 更新文件

- `src/ui/main_window.py`
- `src/ui/managers/menu_manager.py`
- `src/ui/managers/toolbar_manager.py`
- `src/services/project_service.py`
- `src/services/document_service.py`

#### 新增文件

- `src/services/change_service.py`
- `src/services/workflow_service.py`
- `src/ui/widgets/change_management_panel.py`
- `src/ui/dialogs/new_change_request_dialog.py`

#### 变更内容

- 新建 `change_service.py`，以 `00_项目管理/04_变更管理` 为权威目录，提供：
  - 变更单创建
  - 编号规则（按现有 `CHG-DOCU/CHG-PLC/CHG-HMI...` 分类）
  - 台帐同步
  - 状态流转（待评估/待实施/进行中/待验证/已完成）
  - 影响范围挂接（文档、PLC、HMI、调试、交付）
- `workflow_service.py` 负责把变更单接入主工作流：
  - 变更立项
  - 影响分析
  - 实施任务生成
  - 文档同步检查
  - PLC/测试验证
  - 发布归档
- `change_management_panel.py` 作为核心 GUI 页面，展示：
  - 变更列表
  - 状态筛选
  - 影响资产清单
  - 验证结果
  - 台帐同步状态
- 菜单和工具栏提供：
  - 新建变更单
  - 发起影响分析
  - 执行一致性检查
  - 生成验证清单

#### 为什么这样做

- 用户明确指出“变更管理模块很重要，GUI 也很重要，希望能落地”。
- DJ 项目的真实迭代核心不是“新建项目”，而是“围绕现有项目做受控变更”；因此变更管理必须从附属功能升级为主流程入口。

### 03. 固化 DJ 单机项目工作流

#### 更新文件

- `src/core/event_bus.py`
- `src/services/project_service.py`
- `src/services/document_service.py`
- `src/services/spec_service.py`
- `src/services/plc_service.py`
- `src/services/test_management_service.py`
- `src/ui/widgets/project_tree.py`
- `src/ui/dashboard.py`

#### 新增文件

- `src/models/workflow_checkpoint.py`
- `src/ui/widgets/workflow_board.py`

#### 变更内容

- 用 `workflow_service.py + workflow_board.py` 落地 DJ 单机项目标准工作流：
  - `立项与需求`
  - `方案与架构`
  - `PLC开发`
  - `HMI联动`
  - `现场调试`
  - `测试验证`
  - `交付归档`
- 每个阶段绑定实际资产检查项，例如：
  - 设计阶段必须存在需求/架构/变量或接口文档
  - PLC开发阶段必须识别到 `OB1`、`GlobalVars`、关键 FB
  - 测试阶段至少识别到 `.scltest` 或测试报告
  - 交付阶段必须存在操作手册/验收清单/维护文档
- `project_tree.py` 改为按“项目阶段 + 资产类型”混合视图展示，而非只按文件树。
- `dashboard.py` 显示：
  - 当前阶段
  - 阻塞项
  - 未关闭变更
  - 文档缺口
  - 测试状态

#### 为什么这样做

- 当前工具虽然有项目树、仪表盘、检查与诊断能力，但没有把它们组织成用户真正能执行的工作流。
- 对 DJ 单机项目，工作流比单点工具更重要，因为它决定团队是否能按照统一节奏推进项目。

### 04. 让 PLC / 文档 / 测试三者形成联动校验

#### 更新文件

- `src/services/spec_checker_service.py`
- `src/services/plc_service.py`
- `src/services/diagnostic_service.py`
- `src/services/test_management_service.py`
- `src/parsers/spec_doc_parser.py`
- `src/parsers/scltest_parser.py`
- `src/ui/widgets/spec_check_panel.py`
- `src/ui/widgets/test_runner_panel.py`
- `src/ui/widgets/diagnostic_panel.py`

#### 新增文件

- `src/services/consistency_audit_service.py`
- `src/parsers/plc_project_manifest_parser.py`

#### 变更内容

- 规范检查增加 DJ 项目定制规则：
  - 忽略 `.trae` / `.plc-out`
  - 校验 `.plc.json` 的 `libraries`
  - 校验核心目录是否齐备
  - 校验 `OB1 / DB1 / FB / Test / PRD` 关联完整性
- 新增一致性审计服务，输出以下问题：
  - 文档已存在但 PLC 源文件缺失
  - PLC 已变更但变更单/变更记录未更新
  - `.scltest` 缺失或未覆盖关键工站
  - HMI / 现场调试 / 交付文档未同步
- `test_management_service.py` 优先支持识别和执行现有 `Test/basic_test.scltest` 这类资产，形成项目级测试视图。
- `diagnostic_panel.py` 除通用诊断外，增加“项目治理诊断”：
  - 变更闭环完整性
  - 文档一致性
  - 测试覆盖状态
  - 发布门禁状态

#### 为什么这样做

- 该模板最容易失控的点不是单纯语法错误，而是“文档、PLC、测试三者不一致”。
- 工具必须从“代码检查器”升级为“项目治理检查器”。

### 05. GUI 重构重点与页面规划

#### 更新文件

- `src/ui/main_window.py`
- `src/ui/dashboard.py`
- `src/ui/widgets/project_tree.py`
- `src/ui/widgets/document_editor.py`
- `src/ui/widgets/spec_check_panel.py`
- `src/ui/widgets/test_runner_panel.py`
- `src/ui/widgets/diagnostic_panel.py`
- `src/ui/dialogs/new_project_dialog.py`

#### 新增文件

- `src/ui/widgets/change_management_panel.py`
- `src/ui/widgets/artifact_overview_panel.py`
- `src/ui/widgets/workflow_board.py`
- `src/ui/dialogs/import_dj_project_dialog.py`

#### GUI 信息架构

- 左侧导航以“项目治理”为核心，不再以纯技术功能分散：
  - 项目总览
  - 工作流
  - 变更管理
  - PLC 资产
  - 文档资产
  - 测试与验证
  - 诊断与发布
- 右侧主内容区建议采用固定 Tab：
  - `总览`
  - `工作流`
  - `变更`
  - `文档`
  - `PLC`
  - `测试`
  - `诊断`
- `import_dj_project_dialog.py` 提供导入现有 DJ 项目的入口，而不是只偏向“新建项目”。
- `document_editor.py` 需支持从资产映射中打开权威文档，避免用户重复创建。

#### 为什么这样做

- 当前 GUI 能力比较分散，适合工具演示，不适合真实项目治理。
- 如果变更管理和工作流是主线，GUI 也必须围绕它们重排信息架构。

### 06. GUI 测试方案

#### 更新文件

- `requirements.txt`
- `tests/test_integration.py`

#### 新增文件

- `tests/gui/test_main_window_smoke.py`
- `tests/gui/test_dj_project_import.py`
- `tests/gui/test_change_management_workflow.py`
- `tests/gui/test_document_no_duplicate_rule.py`
- `tests/gui/test_workflow_gate_checks.py`
- `tests/gui/conftest.py`
- `tests/fixtures/dj_single_machine/minimal_project/`（最小 DJ 样例夹具）

#### 测试策略

- 继续使用现有技术栈：`pytest + pytest-qt`
- 分 4 层测试：
  - `Smoke`：窗口启动、菜单装载、核心 Panel 创建
  - `Workflow`：导入 DJ 项目 -> 识别资产 -> 发起变更 -> 校验门禁
  - `Rule`：不重复文档、忽略 `.trae/.plc-out`、`.plc.json libraries` 校验
  - `Regression`：以最小 DJ 样例夹具进行固定回归
- GUI 自动化只覆盖“关键闭环”，不追求大而全的录制式 UI 测试。
- 对复杂逻辑尽量沉到 `service` 层做可重复测试，GUI 只验证联动、状态显示和关键交互路径。

#### 为什么这样做

- 现有工具已经有测试基础，但 GUI 扩展后没有回归防线会非常危险。
- `pytest-qt` 已在依赖中存在，适合直接落地，不需要引入新的庞大测试框架。

### 07. 交付与发布工作流

#### 更新文件

- `src/services/document_service.py`
- `src/services/project_service.py`
- `src/services/diagnostic_service.py`

#### 新增文件

- `src/services/release_gate_service.py`
- `src/services/delivery_package_service.py`

#### 变更内容

- 发布前统一执行发布门禁：
  - 未关闭关键变更不得发布
  - 核心文档缺失不得发布
  - 关键测试未通过不得发布
  - 一致性审计失败不得发布
- `delivery_package_service.py` 负责生成交付清单视图，不重复生成已有文档，只汇总和校验现有交付物是否完整。
- 将交付校验结果回写到仪表盘与诊断面板。

#### 为什么这样做

- 用户要“有序管理 DJ 单机项目”，最终落点一定是“能不能受控交付”，否则前面的变更管理和测试都只是过程能力。

## Milestones And Timeline

### M1（第1-2周）资产建模与文档对齐

- 更新现有工具文档，明确 DJ 单机项目定位与边界
- 建立 `DJ_SINGLE_MACHINE` 项目类型与资产映射
- 完成现有 DJ 项目导入能力
- 完成“忽略 `.trae/.plc-out` + 不重复文档”的基础规则

### M2（第3-4周）变更管理落地

- 完成 `change_service.py`
- 完成变更台帐与变更单同步逻辑
- 完成变更管理 GUI 初版
- 支持变更影响资产挂接

### M3（第5-6周）工作流与治理诊断

- 完成 `workflow_service.py + workflow_board.py`
- 在仪表盘显示阶段、阻塞项、变更状态
- 新增一致性审计服务
- 完成文档/PLC/测试联动检查

### M4（第7-8周）GUI 可用化与测试闭环

- 完成导入、变更、工作流、文档打开的核心 GUI 流程
- 补齐关键 GUI 自动化测试
- 完成最小 DJ 示例夹具和回归用例

### M5（第9-10周）试点与收口

- 用 `DJ-2026-005` 做试点导入和治理验证
- 修复高频易错点
- 完成 API / 架构 / 使用说明增量更新
- 形成可持续迭代的 V2.x 基线

## Assumptions & Decisions

- 决策 1：只在现有 `SW-2026-005 PLC项目管理工具` 上迭代，不创建新工具。
- 决策 2：当前首要目标不是“全新模板生成器”，而是“可管理既有 DJ 单机项目模板与项目实例”。
- 决策 3：变更管理是核心模块，不再作为附属文档工具处理。
- 决策 4：文档先行，所有设计与使用说明优先更新现有文档，不重复新增同类文档。
- 决策 5：采用敏捷/增量开发，先保证最小可落地闭环，再逐步增强自动化。
- 决策 6：第一阶段自动化深度采用“半自动管理”，工具负责识别、索引、校验、生成清单和提醒，关键内容仍由工程师确认。
- 决策 7：GUI 测试采用 `pytest-qt`，只覆盖关键闭环，不做高成本全录制式测试。
- 假设 1：`DJ-2026-005` 的目录组织可作为 DJ 单机项目的第一版样板。
- 假设 2：根目录与 `02_PLC程序/通用ST程序及变量表` 下的 `.plc.json` 将继续作为项目识别与 PLC 子项目识别的重要入口。
- 假设 3：现有 FB 文档、变更单、测试文件命名策略基本可延续，工具主要做映射、校验和流程固化。

## Verification Steps

### 方案验收标准

- 工具能成功导入 `DJ-2026-005`，且不会扫描或展示 `.trae` 与 `.plc-out`。
- 工具能正确识别 DJ 项目中的关键资产：
  - 变更管理目录
  - PLC 源码与 DB
  - 功能块 PRD 文档
  - `.scltest`
  - 交付类文档
- 工具能从 GUI 发起变更单，并同步到对应台帐，不生成重复文档。
- 工具能给出至少一条完整工作流路径：
  - 导入项目
  - 识别资产
  - 发起变更
  - 执行检查
  - 查看测试/诊断
  - 检查发布门禁
- GUI 自动化测试至少覆盖：
  - 主窗口启动
  - DJ 项目导入
  - 变更单创建
  - 不重复文档规则
  - 工作流门禁检查
- 现有架构、详细设计、API、代码结构说明文档均被增量更新，且不新增重复说明文档。

### 实施时的只读核查点

- 核查 `DJ-2026-005` 资产识别结果与真实目录是否一致
- 核查 `.plc.json` 的 `libraries` 字段与相对路径规则是否保持正确
- 核查变更管理目录的“Single Source of Truth”原则是否被工具遵守
- 核查新服务是否仍符合 `EventBus + Service + Model` 的现有架构边界
