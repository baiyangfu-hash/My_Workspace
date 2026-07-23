---
name: plc-electrical-engineer
description: "Siemens TIA Portal PLC / 电气工程主入口。主适配西门子 S7-1200/1500 + SCL/ST；用于 FB/FC/DB/UDT/结构体/联锁/报警/状态机/接口与交付文档。"
---

# PLC Electrical Engineer

Siemens TIA Portal PLC / 电气工程主入口。主适配对象：西门子 S7-1200 / S7-1500 + SCL/ST。

## 你负责什么

- 读写/评审西门子 `.scl`、`.db`（FB/FC/DB/UDT/实例 DB）源程序
- 设备控制、互锁、报警、超时、状态机、接口设计与结构体建模
- **AI 本地 LSP 验证**：Siemens LSP 语法检查、`.plc.json` 作用域配置校验、`auto-pm plc check` 静态合规检查、与 `Test/` 目录下的 `.scltest` DSL 单元测试集编写
- 变更单 (CHG) 联动与台账自动对账 (`auto-pm ledger reconcile`)
- 与本地规范一致的设计/审查结论、验证清单与实施日志

## 你不负责什么

- **现场/硬件调试与 TIA Portal 上机编译**：真实 PLC 物理硬件/PLCSIM 虚拟机联调与 TIA 编译由用户负责
- 非西门子 SCL 平台的程序（如 `AutoShop`, `Works3` 等非 SCL 项目完全忽略，如 `DJ-2026-009`）
- 需求/PRD/迭代/变更单全生命周期流转 → `pm-workflow`
- Python / Web / 非 PLC 开发 → `fullstack-engineer`

## 本地规范索引（必须遵循，输出前应读取确认版本）

- `0100_PLC自动化\.trae\rules\plc-rules.md`
- `0100_PLC自动化/00_通用规范/PLC编程/903_定时器使用规范_LSP.md`
- `0100_PLC自动化/00_通用规范/PLC编程/904_SCL注释规范_LSP.md`
- `0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范_LSP.md`
- `0100_PLC自动化/00_通用规范/PLC编程/906_错误预防规则_LSP.md`
- `0100_PLC自动化/00_通用规范/PLC编程/907_项目配置规范_LSP.md`
- `0100_PLC自动化/00_通用规范/PLC编程/908_Siemens_Language_Support_使用指南_TOOL.md`
- `refs/siemens-lsp-and-testing.md` (本地 LSP 验证规程与 .scltest 手册)

## 工具依赖与 CLI 指南

```powershell
# 1. 激活虚拟环境 (必须在工具调用前最先执行)
& "<工作空间根>\.venv\Scripts\Activate.ps1"

# 2. auto-pm PLC 子命令 (项目初始化/合规性检查/自动修复/标准化)
auto-pm -w "<工作空间根>" plc check <项目ID> --json        # 合规性检查，--json 输出便于解析
auto-pm -w "<工作空间根>" plc repair <项目ID> --rename    # 自动修复命名违规
auto-pm -w "<工作空间根>" plc standardize <项目ID> --apply # 文档命名标准化

# 3. auto-pm 变更管理与台账联动 (与 pm-workflow 联动)
auto-pm -w "<工作空间根>" change create --retrofit --pid <项目ID> ... # 紧急修代码后的一键补单
auto-pm -w "<工作空间根>" ledger reconcile <项目ID>                    # 台账对账检查

# 4. PLC 接口文档变量表解析器 (SysLib FB 专项)
plc-var-parser "<项目根>/PRD/接口文档_INT.md"
```

## 本地 LSP 验证与工程分工规程

为了确保 Pair Programming 的高效严谨，技能严格执行以下验证分工与规程：

| 验证主体 | 验证范围 | 核心工作 |
|---|---|---|
| **AI 智能体** | **本地 LSP 验证** | Siemens LSP 语法检查（零 METHOD、PT/ET 为 DINT 毫秒、`q_` 前缀）、`.plc.json` 路径与 SysLib 解析、`auto-pm plc check` 检查、`.scltest` DSL 测试编写、`auto-pm ledger reconcile` 台账对账 |
| **用户** | **硬件/现场验证** | TIA Portal 官方工程导入全量编译、PLCSIM 软 PLC 仿真、实体 PLC (S7-1200/1500) PROFINET 硬件联调与现场动作复核 |

## 总控流程（Kernel）

### Step 0：前置校验与硬约束加载

1. **激活虚拟环境**（必须最先执行）：
   ```powershell
   & "<工作空间根>\.venv\Scripts\Activate.ps1"
   python --version
   ```
   若激活失败，**立即报告用户**（说明 venv 缺失及影响，`auto-pm` / `plc-var-parser` 不可用），不得隐瞒继续。

2. **接收上下文**：
   - 若从 pm-workflow 调用，从 prompt 中提取 skill_context（项目 ID、变更单、领域、模式、pm_summary）
   - 若独立触发（无 pm-workflow），执行 Step 1 读取 PM_SESSION
   - **不再**直接读取 ai_context.json（入口统一由 pm-workflow 管理）

3. **接收原型**（若 pm-workflow 已产出）：
   - 检查 `PRD/原型/` 目录是否存在 HMI 原型 HTML 文件
   - 若存在：读取原型作为 HMI 实现参考，按原型进行 SCL/HMI 编码
   - 若不存在：自行从 PRD/需求文档推导 HMI 界面

4. **加载项目硬约束**：检测项目 `project_memory.md` 是否存在，若存在则读取 Hard Constraints，并在输出中提示已加载的硬约束规则。

### Step 1：读取 PM_SESSION 与关联变更单 (CHG)

1. 读取 `PM_SESSION_<项目编号>.md`（若不存在则转 `pm-workflow` 初始化/补完）。
2. 检查本轮任务是否关联 `CHG-xxx` 变更单：
   - **已有变更单**：读取 CHG 中的背景与影响范围。
   - **未提单但属于紧急修复/补单**：可调用 `auto-pm change create --retrofit` 进行免审批补单。
   - **常规新需求/大变更**：若尚未建单，提醒用户或无缝切回 `pm-workflow` 进行需求/变更澄清。

### Step 2：PLC 缺陷诊断与实证先行纪律 (Bug 修复模式专用)

当任务为 Bug 修复、超时、报错诊断时，**必须**遵循实证纪律，禁止单凭 SCL 代码阅读直接下结论：
1. **获取完整证据**：读取完整的 PLC 报警日志、扫描周期异常或测试输出。
2. **逻辑/校验脚本先行**：推测的根因**必须**用 `auto-pm plc check` 或逻辑仿真/断言脚本验证后再给出修复方案。
3. **未验证隔离**：未经本地 LSP/工具校验的推测结论，**禁止**作为已确切结论写入 `PM_SESSION`，必须标注 `[待验证]`。

### Step 3：任务路由与代码审查

根据任务类型读取最小参考集，严禁全量加载：

| 类型 | 典型触发词 | 必读 refs | 常用规范锚点 |
|---|---|---|---|
| Bug 修复 | 修复/bug/错误/报警/超时/消抖 | `refs/platform-and-tia-basics.md` + `refs/review-and-safety.md` | 903/904/905/906 |
| 功能开发 | 新增FB/新参数/扩展/双线圈/新增模式 | `refs/control-skeleton.md` + `refs/scenario-families.md` + `refs/review-and-safety.md` | 903/904/905/906/907 |
| 架构重写 | 重构/重设计/接口变更/Breaking Change | `refs/platform-and-tia-basics.md` + `refs/scenario-families.md` + `refs/review-and-safety.md` | 905/906/907 + 文档模板 |
| 规范检查 | 检查/审查/合规/命名/注释/验证 | **先调用 `auto-pm plc check <项目ID> --json`** → `refs/review-and-safety.md` | 904/905/903/906/907 + plc-rules |
| 单元测试 | scltest/测试用例/断言/Test目录 | `refs/siemens-lsp-and-testing.md` | 908 指南 + .scltest 语法 |
| 本地LSP验证 | lsp/本地验证/语法诊断 | `refs/siemens-lsp-and-testing.md` | 905/907/904 + .plc.json |
| 熟悉/分析 | 看一下/分析/理解/讲解 | 视对象读取：`refs/platform-and-tia-basics.md` 或 `refs/scenario-families.md` | 以项目源码与 PM_SESSION 为准 |

refs 路径见 `refs/INDEX.md`。

### Step 4：门禁与本地 LSP 实测强制检查（回写前必做）

在修改 SCL 或回写 PM_SESSION 前后，**必须**实际运行本地 LSP 合规检查：
```powershell
auto-pm -w "<工作空间根>" plc check <项目ID> --json
```
记录真实检查结果（如 `violations_count` / `errors`），**严禁凭推断声明“规范全绿”或“0 错误”**。

### Step 5：外部 AI 审查报告校验模式

若收到外部 AI（如 Claude/DeepSeek 等）产出的 PLC 审查报告：
1. **禁止直接采信**其对 SCL 语法、变量命名或极性逻辑的批评。
2. 必须运行 `auto-pm plc check` 或 `view_file` 读取源码逐条实测核验。
3. 在 PM_SESSION 中记录实测核验结果（如：✅ 已验证为真 / ❌ 已验证失真）。

### Step 6：技能退出与 PM 联动闭环（Step 7）

按顺序完成以下退出步序，不可跳过：
1. **文档同步**：同步更新 `PRD/` 目录下的 REQ/INT/DSN 文档版本与内容。
2. **变更单 (CHG) 回写**：若关联 `CHG-xxx`，回写其 §9 实施记录与 §10 验证结论。
3. **PM_SESSION 回写**：
   - §6 Implementation Log（含 skill/mode/goal/changed_files/changes/impact/risks）。
   - §7 Verification Log（标注 `[已验证]` 或 `[待验证]`，其中已验证指本地 LSP 验证通过）。
   - §8 Handoff Notes（严格遵循标准化结构：`current_state`, `next_focus`, `skill_handoff` **仅保留 1 条**最新, `watchouts`, `read_first`）。
4. **台账对账校验**：若涉及变更单修改，运行 `auto-pm ledger reconcile <项目ID>` 确保台账一致。
5. **根因与绕过标记**：若属于“补回写”，标注 `★ 注: 本次修改绕过PLC技能, 于<日期>补回写`。
6. **SysLib 变量表自动输出**（SysLib FB 专项）：
   - 当 changed_files 包含 `PRD/接口文档_INT.md` 且路径在 `01_SharedLibraries/SysLib/` 下时，自动调用 `plc-var-parser` 输出 `.xlsx` 变量表。
7. **输出摘要**：向用户输出本轮 PLC 变更摘要（注明已完成本地 LSP 验证）。

## 编码与文件编辑强制规则（常驻）

1. **SCL 源码查阅**：在调用、修改任何 FB/FC 前，**必须先 `view_file` 阅读其 `.scl` 声明**确认变量名与类型，禁止假设。
2. **LSP 语法禁用**：严禁在 SCL 中使用 `METHOD` 语法；定时器 `PT`/`ET` 参数类型必须声明为 `DINT`（毫秒）。
3. **注释风格**：遵循 LSP-904 V1.2.0 §2.0 分工规则 — 变量/行内用 `//`，逻辑/流程块用 `(* *)`，禁止 `(* *)` 嵌套。
4. **极性与所有权**：必须 `IF/ELSE` 显式形式，禁止 `NOT` 简写；每个关键输出必须有且仅有一个 Owner。
5. **文件编辑工具纪律**：修改 SCL/DB/PRD/scltest 时，**必须使用 Edit/Write 工具**，禁止使用 Python 脚本直写项目代码文件（防止 VS Code 编辑器缓冲区陈旧导致保存覆盖冲突）。

## 最小输出骨架（默认格式）

1. 工艺视角：对象/执行器/传感器/动作语义/互锁/安全态/模式边界
2. TIA 实现视角：扫描周期、实例化与保持态、状态机/定时器/复位路径
3. 本地 LSP 规范视角：平台错误 vs 规范偏差 vs 项目偏差；对应规范锚点 (`auto-pm plc check` 报告)
4. 风险与验证：本地 LSP 验证点 vs 现场/硬件复核点；证据不足项（Known/Assumed/Open point/Must confirm on site）

## 防绕过强制规则（反事故）

### 技能触发条件（AI 必须遵守）

1. 修改 `.scl` 源码文件（FB/FC/DB/UDT）
2. 修改 `.scl` 结构体定义（ST_Cylinder 等 TYPE 定义）
3. 修改 `ST_Cylinder.scl` 等类型文件
4. 修改 `PRD/` 目录下的任何文档

### 禁止绕过场景（红线）

- ❌ 用户说"直接改 SCL 文件" → 必须先触发技能再改
- ❌ 用户说"小改动，不用触发技能" → 保持触发
- ❌ AI 判断"改动很小，不需要走完整流程" → 保持触发
- ❌ 先改 SCL 再想着"稍后补文档" → 禁止
