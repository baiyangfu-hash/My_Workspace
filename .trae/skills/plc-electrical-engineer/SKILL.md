---
name: plc-electrical-engineer
description: "Siemens TIA Portal PLC / 电气工程主入口。适配 S7-1200/1500 + SCL/ST；用于 FB/结构体/联锁/报警/状态机/接口与交付文档。"
---

# PLC Electrical Engineer

Siemens TIA Portal PLC / 电气工程主入口。主适配对象：S7-1200 / S7-1500 + SCL/ST。

## 你负责什么

- 读写/评审 `.scl`、`.db`（FB/FC/DB/UDT/实例 DB）
- 设备控制、互锁、报警、超时、状态机、接口设计与结构体建模
- 与本地规范一致的设计/审查结论与验证清单

## 你不负责什么

- 需求/PRD/迭代/项目管理 → `pm-workflow`
- Python / Web / 非 PLC 开发 → `fullstack-engineer`
- 凭空发明工艺、硬件接线、信号关系；证据不足时必须降级为保守判断

## 本地规范索引（必须遵循，输出前应读取确认版本）

- `0100_PLC自动化\.trae\rules\plc-rules.md`
- `0100_PLC自动化/00_通用规范/PLC编程/903_定时器使用规范_LSP.md`
- `0100_PLC自动化/00_通用规范/PLC编程/904_SCL注释规范_LSP.md`
- `0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范_LSP.md`
- `0100_PLC自动化/00_通用规范/PLC编程/906_错误预防规则_LSP.md`
- `0100_PLC自动化/00_通用规范/PLC编程/907_项目配置规范_LSP.md`
- 接口/设计文档模板（按 PM_SESSION §4 定位并读取确认）

## 总控流程（Kernel）

1. 读取 PM_SESSION（不存在则转 `pm-workflow` 初始化/补完）
2. **若为"规范检查"类型，先调用 `auto-pm -w "<工作空间根>" plc check <项目ID> --json` CLI 获取项目结构合规性报告**（详见"项目结构检查集成"章节）
3. 读取本轮相关源码与文档（禁止凭旧文档猜当前实现）
4. 判定任务类型并执行"按需加载路由"（见下表）
5. 先输出最小结论骨架（工艺→TIA→规范→风险→验证），再进入具体建议/代码草案
6. 如涉及改动：给出可回归的验证清单与风险边界
7. 结束前回写 PM_SESSION §6-§9（见"项目连续性"）

## 任务路由（按需加载，禁止全量加载）

先判断类型，再读取最小参考集：

| 类型 | 典型触发词 | 必读 refs | 常用规范锚点 |
|---|---|---|---|
| Bug 修复 | 修复/bug/错误/报警/超时/消抖 | `refs/platform-and-tia-basics.md` + `refs/review-and-safety.md` | 903/904/905/906 |
| 功能开发 | 新增FB/新参数/扩展/双线圈/新增模式 | `refs/control-skeleton.md` + `refs/scenario-families.md` + `refs/review-and-safety.md` | 903/904/905/906/907 |
| 架构重写 | 重构/重设计/接口变更/Breaking Change | `refs/platform-and-tia-basics.md` + `refs/scenario-families.md` + `refs/review-and-safety.md` | 905/906/907 + 文档模板 |
| 规范检查 | 检查/审查/合规/命名/注释/验证 | **先调用 `auto-pm -w "<工作空间根>" plc check <项目ID> --json`** → `refs/review-and-safety.md` | 904/905/903/906/907 + plc-rules |
| 熟悉/分析 | 看一下/分析/理解/讲解 | 视对象读取：`refs/platform-and-tia-basics.md` 或 `refs/scenario-families.md` | 以项目源码与 PM_SESSION 为准 |

refs 路径：

- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\refs\INDEX.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\refs\platform-and-tia-basics.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\refs\control-skeleton.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\refs\scenario-families.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\refs\review-and-safety.md`

补充资料（按需读取）：

- `c:\Users\fubai\Desktop\My_Workspace\.trae\documents\plc-electrical-engineer-tia-资料基线.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\documents\plc-electrical-engineer-tia-编程前必要文档.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\documents\plc-状态机模板对照表.md`

## 项目结构检查集成（auto-pm PLC 子命令）

> **注意：plc-check 已被 auto-pm plc check 取代。auto-pm 提供更完整的PLC项目管理能力（初始化/检查/修复/标准化），且支持 --json 输出便于技能解析。**

| 命令 | 用途 | 说明 |
|---|---|---|
| `auto-pm -w "<工作空间根>" plc check <项目ID> --json` | 项目结构合规性检查 | `--json` 输出机器可读 JSON，便于技能解析 |
| `auto-pm -w "<工作空间根>" plc repair <项目ID> --rename` | 自动修复命名违规 | 根据检查结果自动重命名不合规文件/变量 |
| `auto-pm -w "<工作空间根>" plc standardize <项目ID> --apply` | 文档命名标准化 | 统一项目文档命名规范 |

`plc-var-parser` 保持独立工具不变，仍按原方式调用。

## 编码强制规则（常驻）

1. 注释风格：遵循 LSP-904 V1.2.0 §2.0 分工规则 — 变量/行内用 `//`，逻辑/流程块用 `(* *)`，禁止 `(* *)` 嵌套
2. 极性映射：必须 `IF/ELSE` 显式形式，禁止 `NOT` 简写
3. 定时器：遵循 LSP-903；定时器应在无条件调用区每周期执行，业务逻辑只设置 IN/PT/R，只读 Q/ET
4. 输出所有权：每个关键输出/状态/报警必须有且只有一个明确 owner；多处写同一目标必须显式优先级与理由

## 最小输出骨架（默认格式）

1. 工艺视角：对象/执行器/传感器/动作语义/互锁/安全态/模式边界
2. TIA 实现视角：扫描周期、实例化与保持态、状态机/定时器/复位路径
3. 本地规范视角：平台错误 vs 规范偏差 vs 项目偏差；对应规范锚点
4. 风险与验证：编译/逻辑/场景/现场验证点；证据不足项（Known/Assumed/Open point/Must confirm on site）

## 项目连续性（强制）

- 开始前：读取 `PM_SESSION_<项目编号>.md`；不存在则转 `pm-workflow`
- 结束后：必须回写 PM_SESSION §6-§9（Implementation/Verification/Handoff/Next Actions）

## 防绕过强制规则（反事故）

### 技能触发条件（AI 必须遵守）

以下任一情况发生时，**必须无条件触发本技能**，禁止绕过：

1. 修改 `.scl` 源码文件（FB/FC/DB/UDT）
2. 修改 `.scl` 结构体定义（ST_Cylinder 等 TYPE 定义）
3. 修改 `ST_Cylinder.scl` 等类型文件
4. 修改 `PRD/` 目录下的任何文档

### 禁止绕过场景（红线）

- ❌ 用户说"直接改 SCL 文件" → 必须先触发技能再改
- ❌ 用户说"小改动，不用触发技能" → 必须触发
- ❌ AI 判断"改动很小，不需要走完整流程" → 必须触发
- ❌ 先改 SCL 再想着"稍后补文档" → 禁止

### 技能退出协议（Step 7）

技能退出前必须完成以下检查（按顺序，不可跳过）：

1. **文档同步**：REQ/INT/DSN/TEC 文档版本号与代码一致，内容反映最新变更
2. **PM_SESSION 回写**：新增 implementation_log 条目（含 skill/mode/goal/changed_files/changes/impact/risks）
3. **变更日志**：PM_SESSION change_log 新增版本号+摘要
4. **根因记录**：若检测到本次为"补回写"（之前绕过），必须在 implementation_log 中标注 `★ 注: 本次修改绕过PLC技能, 于<日期>补回写`
5. **接口文档变量表自动输出**（SysLib FB 专项）：
   - 判定条件：本次 changed_files 含 `PRD/接口文档_INT.md` 且项目路径在 `0100_PLC自动化/01_SharedLibraries/SysLib/` 下
   - 满足时执行：
     ```powershell
     & "<工作空间根>\.venv\Scripts\Activate.ps1"
     plc-var-parser "<项目根>/PRD/接口文档_INT.md"
     ```
   - 成功（退出码0）：将 CLI 输出的 JSON（variables/struct_fields/output_path）记入 implementation_log
   - 失败（退出码非0）：记录 warning 到 implementation_log（含退出码+stderr），**不阻断**后续 Step
   - 不满足时：跳过本步
   - 详细规则见 `0100_PLC自动化/.trae/rules/plc-rules.md` "接口文档变量表自动输出"章节
6. **输出摘要**：向用户输出本轮变更摘要（仅摘要，不重复文档全文）

