# 三技能整合一次性替代方案计划

## 1. Summary

- 目标：将当前工作区本地技能从 8 个收敛为 3 个业务主技能 + 1 个维护技能，形成稳定、低歧义的入口体系。
- 保留的业务主技能：
  - `pm-workflow`：保留现有 PM 入口名，但重写内容，吸收需求/PRD/拆解/线框/GitHub 项目推进能力。
  - `fullstack-engineer`：新增，覆盖前端、后端、联调、评审、调试、小程序模式。
  - `plc-electrical-engineer`：新增，覆盖 PLC 编程、规范核对、电气技术文档、IO/报警/调试交付。
- 保留的维护技能：
  - `find-skills`：保留，不作为主业务入口。
- 一次性下线并归档的本地技能：
  - `breakdown-plan`
  - `github-project-management`
  - `prd`
  - `product-requirements`
  - `wireframe-design`
  - `wireframe-prototyping`

## 2. Current State Analysis

### 2.1 本地技能现状

- 当前本地技能目录为 `c:\Users\fubai\Desktop\My_Workspace\.trae\skills`
- 实际存在 8 个本地技能：
  - `breakdown-plan`
  - `find-skills`
  - `github-project-management`
  - `pm-workflow`
  - `prd`
  - `product-requirements`
  - `wireframe-design`
  - `wireframe-prototyping`
- 现状判断：
  - 本地技能几乎全部集中在 PM/需求/规划链路。
  - 本地目录中没有 `fullstack-engineer` 或 `plc-electrical-engineer` 类技能。
  - `web-dev`、`TRAE-code-review`、`TRAE-debugger`、`TRAE-generate-mini-app` 属于平台可用技能，不在当前工作区本地技能目录中，不能通过“删本地文件”的方式整合，只能在新技能说明中约定其调用时机。

### 2.2 重复与冲突

- `prd` 与 `product-requirements`：
  - 都服务于“需求澄清 -> PRD 产出”。
  - 前者偏文档模板，后者偏互动提问和质量评分。
  - 对最终用户来说，属于同一入口问题。
- `breakdown-plan` 与 `github-project-management`：
  - 都处理任务拆解、Issue、里程碑、项目板。
  - 前者偏拆解模板，后者偏 GitHub 操作自动化。
  - 实际使用时强耦合，不应分裂为两个入口。
- `wireframe-design` 与 `wireframe-prototyping`：
  - 都服务于方案前置和界面表达。
  - 一个偏原则，一个偏原型执行。
  - 适合作为 PM 技能的子模式，而不是独立入口。
- `pm-workflow`：
  - 已经承担了会话总控职责，并且明确依赖 `PM_SESSION_<项目编号>.md`，是最适合保留为唯一 PM 入口的技能。
  - 当前内容中已经显式引用了其他 5 个本地 PM 技能，说明当前体系是“总控 + 多子技能”的组织方式。

### 2.3 两类项目证据

#### A. Python 产品型项目：`SW-2026-005_PLC项目管理工具`

- 项目根目录：
  - `c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-005_PLC项目管理工具`
- PM 会话文件：
  - `PM_SESSION_SW-2026-005.md`
- 实际工作流特征：
  - 有 PRD、DES、API、UI prototype、tests、Bridge、PyWebView 前后端结构。
  - `PM_SESSION_SW-2026-005.md` 已体现完整产品化流程：需求重置、技术设计、Bridge 打通、UI 页面实现、稳定化阶段。
  - `001_产品需求文档_PRD-V8.0.0.md` 显示该项目高度依赖“需求澄清 -> 技术架构 -> UI/交互 -> 变更管理”的产品链路。
- 结论：
  - 需要强 PM 技能 + 全栈技能组合。

#### B. PLC 电气交付项目：`DJ-2026-005`

- 项目根目录：
  - `c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\DJ-2026-005`
- PM 会话文件：
  - `PM_SESSION_DJ-2026-005.md`
- 实际工作流特征：
  - 有立项/需求/变更管理/程序文档/PRD-SRC/ST 源码/HMI/现场调试/交付文档的完整工业工程链路。
  - `PM_SESSION_DJ-2026-005.md` 明确区分 L0-L4 文档层级、规范层、ST 源码层、测试与一致性。
  - `016_DJ-2026-005_PLC程序设计总文档_PLC-V2.0.0.md` 显示该项目有强规范、强文档、强架构重构背景。
  - 该项目还受 `plc-rules.md` 强约束，尤其是 `LSP-905/904/903/906/907`。
- 结论：
  - 需要独立的 PLC 电气技能，不能与 Web/产品 PM 混用。

## 3. Assumptions & Decisions

### 3.1 已锁定决策

- 迁移方式：一次性替代，不走并行试运行。
- PM 入口保留：保留技能名 `pm-workflow`。
- 其他技能处理策略：
  - 本地冗余 PM 技能全部归档，不保留到常用列表。
  - `find-skills` 保留为维护技能。
- 执行范围：
  - 仅调整工作区本地技能目录 `c:\Users\fubai\Desktop\My_Workspace\.trae\skills`
  - 不修改两个项目代码或项目文档内容。

### 3.2 设计原则

- 原则 1：入口按“角色”而不是按“工序碎片”组织。
- 原则 2：本地技能只保留高频、稳定、跨项目可复用的主入口。
- 原则 3：平台内置技能不重复造轮子，而是在新技能中定义调用时机。
- 原则 4：PLC 技能必须显式包含规范优先、文档优先、人工复核、安全边界。

## 4. Proposed Changes

### 4.1 重写 `pm-workflow`

- 文件：
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\pm-workflow\SKILL.md`
- 变更目标：
  - 保留技能名和 PM 入口习惯。
  - 将其从“总控 + 调其他 PM 子技能”改为“单技能闭环执行”。
- 吸收内容：
  - `product-requirements` 的需求澄清与补问逻辑。
  - `prd` 的 PRD 结构化输出逻辑。
  - `breakdown-plan` 的 Epic/Feature/Story/Enabler/Test 拆解逻辑。
  - `github-project-management` 的里程碑/Issue/项目板同步建议。
  - `wireframe-design` 与 `wireframe-prototyping` 的低保真/中保真/状态覆盖方法。
- 重写后建议的内部子模式：
  - 需求模式
  - PRD 模式
  - 方案/线框模式
  - 拆解模式
  - 项目推进模式
  - 变更/缺陷/发布模式
- 重写重点：
  - 保留 `PM_SESSION_<项目编号>.md` 作为单一真源。
  - 保留当前 `SpecMgr`、引用完整性校验、规范漂移检查逻辑。
  - 删除对旧 PM 子技能的显式依赖描述，避免形成循环依赖或僵尸入口。

### 4.2 新增 `fullstack-engineer`

- 新增目录：
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\fullstack-engineer\`
- 新增文件：
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\fullstack-engineer\SKILL.md`
- 服务对象：
  - 类似 `SW-2026-005_PLC项目管理工具` 的 Python/Web/前后端项目。
- 技能职责：
  - 前端页面与交互实现
  - 后端服务与接口实现
  - API/数据流/联调
  - 缺陷定位与修复
  - 代码评审
  - 小程序模式（仅作为子模式）
- 需要显式引用的项目现实依据：
  - `SW-2026-005` 中存在 `main.py`、`src/services/`、`src/bridge/`、`ui/js/`、`tests/` 等典型全栈结构。
- 与平台技能的关系：
  - 需要在文案中约定：
    - 新建 Web 页面/站点优先转交平台 `web-dev`
    - 复杂运行时问题优先转交平台 `TRAE-debugger`
    - 代码审查任务优先转交平台 `TRAE-code-review`
    - 小程序意图触发平台 `TRAE-generate-mini-app`
  - 本地 `fullstack-engineer` 负责“统一入口”和“选择正确子流程”，不与平台技能重复。
- 建议内部子模式：
  - 前端模式
  - 后端模式
  - 全栈联调模式
  - 评审模式
  - 调试模式
  - 小程序模式

### 4.3 新增 `plc-electrical-engineer`

- 新增目录：
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\`
- 新增文件：
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\SKILL.md`
- 服务对象：
  - 类似 `DJ-2026-005` 的 PLC/HMI/电气交付项目。
- 技能职责：
  - PLC 程序阅读、改写、重构建议
  - 规范核对与实现前检查
  - IO/变量/报警/联锁文档编写
  - 程序设计文档、接口文档、详细设计说明书编制
  - 调试问题记录与交付资料整理
- 必须内置的约束：
  - 明确遵循 `0100_PLC自动化\.trae\rules\plc-rules.md`
  - 明确优先使用：
    - `LSP-905`
    - `LSP-904`
    - `LSP-903`
    - `LSP-906`
    - `LSP-907`
  - 写 `.scl` 前先读规范和实际 FB 接口，禁止凭经验假设。
  - 禁止把 AI 生成内容直接视为可上机程序，必须人工复核。
- 需要显式引用的项目现实依据：
  - `DJ-2026-005` 中存在 `02_PLC程序\通用ST程序及变量表\*.scl`
  - 存在 `02_PLC程序\程序文档\*.md`
  - 存在 `00_项目管理\04_变更管理\`、`04_现场调试\`、`06_文档与交付\`
- 建议内部子模式：
  - PLC 编程模式
  - 规范检查模式
  - 程序文档模式
  - IO/变量/报警模式
  - 现场调试模式
  - 交付资料模式

### 4.4 保留 `find-skills`

- 文件：
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\find-skills\SKILL.md`
- 处理方式：
  - 内容不改或仅做最小补充。
  - 不作为主业务入口，不在整合后的“推荐常用入口”中宣传。

### 4.5 归档冗余本地 PM 技能

- 归档对象：
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\breakdown-plan\`
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\github-project-management\`
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\prd\`
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\product-requirements\`
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\wireframe-design\`
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\wireframe-prototyping\`
- 建议归档方式：
  - 迁移到 `c:\Users\fubai\Desktop\My_Workspace\.trae\skills_archive\`
  - 不建议直接删除，保留一次回滚能力。
- 原因：
  - 一次性替代需要界面变干净，但仍要保留审计和回退可能性。

### 4.6 可选新增总览文档

- 可选新增文件：
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\README.md`
- 作用：
  - 明确本地常用技能只推荐：
    - `pm-workflow`
    - `fullstack-engineer`
    - `plc-electrical-engineer`
    - `find-skills`
  - 作为后续维护入口说明。

## 5. Execution Steps

### Step 1：备份与基线确认

- 记录当前 `.trae\skills` 目录结构。
- 备份 6 个将下线的本地 PM 技能目录。
- 备份 `pm-workflow\SKILL.md` 当前版本。

### Step 2：重写 `pm-workflow`

- 删除当前文案中对旧 PM 子技能的直接依赖描述。
- 融合需求/PRD/线框/拆解/GitHub 项目推进方法。
- 保留 `PM_SESSION` 与 `SpecMgr` 机制。
- 保留对 Python 工具类项目和 PLC 项目的通用适用范围。

### Step 3：新增 `fullstack-engineer`

- 创建新目录和 `SKILL.md`。
- 写清楚触发词、适用项目、子模式、与平台技能的边界。
- 让其覆盖 `SW-2026-005` 这类项目的实际任务链路。

### Step 4：新增 `plc-electrical-engineer`

- 创建新目录和 `SKILL.md`。
- 将规范、文档、程序、现场调试、交付全部纳入统一入口。
- 将 PLC 安全边界写成强约束。

### Step 5：归档旧技能

- 把 6 个本地冗余 PM 技能移出 `.trae\skills\` 主目录。
- 保留 `find-skills` 在主目录中。

### Step 6：更新使用说明

- 如采用 README，则写明：
  - PM 相关统一走 `pm-workflow`
  - 软件研发统一走 `fullstack-engineer`
  - PLC/电气统一走 `plc-electrical-engineer`
  - 扩展技能发现走 `find-skills`

### Step 7：场景化验证

- 用 `SW-2026-005` 进行验证：
  - PM 任务：需求变更、迭代推进、变更台账、稳定化规划
  - 全栈任务：UI/Bridge/API/测试/调试
- 用 `DJ-2026-005` 进行验证：
  - PM 任务：变更、交付、文档索引、PM_SESSION 更新
  - PLC 任务：ST 改动建议、规范检查、接口文档、现场调试记录
- 验证结果要求：
  - 不再需要用户在多个 PM 技能之间判断入口。
  - PLC 任务不会误导到 Web/PRD 工作流。
  - 软件开发任务不会误导到 PLC 规范流。

## 6. Risks

| 风险 | 说明 | 影响 | 缓解措施 |
|------|------|------|----------|
| PM 技能过度膨胀 | `pm-workflow` 吸收 5 个技能后可能太长 | 中 | 用“子模式 + 触发词 + 分阶段流程”组织，避免平铺叙述 |
| 本地技能与平台技能边界不清 | `fullstack-engineer` 可能与 `web-dev`/`TRAE-debugger` 重叠 | 中 | 在 `SKILL.md` 中明确“何时由本地技能统一编排，何时转交平台技能” |
| PLC 技能误生成不安全建议 | PLC 场景风险高 | 高 | 在 `plc-electrical-engineer` 中加入强制规范检查、人工复核、禁止直接上机等约束 |
| 一次性替代导致使用习惯中断 | 用户原来会直接点 `prd`/`wireframe-*` | 中 | 保留 `pm-workflow` 名称不变；补充 README 和技能说明，降低切换成本 |
| 误删本地技能导致不可回退 | 一次性下线不可逆 | 中 | 归档而非直接删除 |

## 7. Impact on Existing Project Development

### 7.1 对 `SW-2026-005` 的影响

- 正向影响：
  - 规划、需求、PRD、页面原型、任务拆解不再分散到多个 PM 技能中，减少入口选择成本。
  - 新增 `fullstack-engineer` 后，`main.py`、`src/services/`、`src/bridge/`、`ui/js/`、`tests/` 这类真实结构可以统一归口。
  - 对当前 `Phase 3 稳定化` 更友好，后续“端到端测试 + 性能优化 + 打包 exe”可以直接走全栈技能。
- 负面影响：
  - 早期几次使用需要适应新的单入口模式。
  - 如果 `fullstack-engineer` 边界没写好，可能把“新建网站”和“修改现有工程”混为一谈。
- 对代码与文档的直接影响：
  - 本轮不触碰项目代码、不触碰项目 PRD/DES/API/PM_SESSION。
  - 影响仅发生在后续 AI 协作方式上。

### 7.2 对 `DJ-2026-005` 的影响

- 正向影响：
  - PLC 编码、文档、IO/报警、交付资料不再需要借道 PM 技能或临时通用提示词。
  - 与 `PM_SESSION_DJ-2026-005.md` 中的 L0-L4 文档层级、变更、测试、交付链路更加一致。
  - 有利于后续围绕 `OB1.scl`、`GlobalVars.db`、`FB_1002/1003/1004`、`程序文档` 做统一风格的 AI 协作。
- 风险：
  - PLC 技能如果不显式约束规范版本，可能沿用历史废弃规范或旧文件命名。
  - 需要特别避免把“程序设计文档输出”和“实际 PLC 程序变更”混成一步。
- 对代码与文档的直接影响：
  - 本轮不修改 `DJ-2026-005` 项目内任何 `.scl`、`.db`、`.md`、`.xlsx` 文件。
  - 影响仅发生在后续 AI 任务入口与输出风格上。

### 7.3 对整体开发方式的影响

- 从“按工序选技能”变为“按角色选技能”：
  - 产品/项目管理 -> `pm-workflow`
  - 软件开发 -> `fullstack-engineer`
  - PLC/电气 -> `plc-electrical-engineer`
- 决策成本下降，但对技能说明质量要求更高。
- 本次整合不会改变仓库结构、测试结果、构建链、项目规范本身。

## 8. Verification

- 目录验证：
  - `.trae\skills` 最终仅保留 4 个目录：
    - `pm-workflow`
    - `fullstack-engineer`
    - `plc-electrical-engineer`
    - `find-skills`
- 归档验证：
  - 6 个冗余 PM 技能全部存在于 `skills_archive`，不再出现在主目录。
- 触发验证：
  - 输入“写 PRD / 拆需求 / 做线框 / 出 issue 计划”时，只应命中 `pm-workflow`
  - 输入“做前端 / 改后端 / 联调 / review / debug”时，应命中 `fullstack-engineer`
  - 输入“改 PLC / 看 SCL / 补 IO 文档 / 报警表 / 调试记录”时，应命中 `plc-electrical-engineer`
- 项目适配验证：
  - `SW-2026-005` 的典型任务均可被 `pm-workflow` 或 `fullstack-engineer` 正确覆盖
  - `DJ-2026-005` 的典型任务均可被 `pm-workflow` 或 `plc-electrical-engineer` 正确覆盖
- 安全验证：
  - PLC 技能必须显式提醒人工复核与规范优先。
  - 本轮整合不应导致任何项目文件被误修改。

