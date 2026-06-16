# `plc-electrical-engineer` 技能重构计划

## Summary

本次重构仅针对 [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md) 及其与本地 PLC 规范的映射关系，不扩展到其他技能、业务代码或项目文档。

目标是把 `plc-electrical-engineer` 从“泛 PLC 助手”重构为“明确适配 Siemens TIA Portal / S7-1200 / S7-1500 / SCL 场景”的工业级技能，优先解决当前技能对 TIA 编程模型、实例化/调用方式、工艺优先级和审查顺序理解不准的问题。

成功标准：
- 技能定义明确以 TIA Portal 为主平台，而不是泛 IEC 抽象描述。
- 技能内明确区分“本地 LSP 规则”和“TIA 平台基本编程常识”的边界。
- 技能能先看工艺/物理/互锁，再看语法/规范，再给修改建议。
- 技能输出模板能支持代码阅读、规范检查、调试分析、接口/联锁审查等常见 PLC 工作。
- 技能中不再出现会误导 TIA/SCL 判断的模糊或错误表述。

## Current State Analysis

已确认的现状：

1. 当前技能文件是 [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md)。
2. 当前技能已包含一部分“TIA 常识”补丁，但仍然是追加式修补，结构没有重构，核心问题仍在：
   - 角色定位仍偏“统一 PLC 与电气入口”，但没有把 TIA/S7-1200/1500/SCL 作为主场景写死。
   - 规则顺序仍偏“规范优先”，但没有先建立物理过程、执行机构、互锁、安全态的分析顺序。
   - “本地规范”和“平台事实”没有拆开，容易再次把规则误判成 TIA 平台事实。
   - 工作模式太泛，没有体现“TIA 下代码阅读/改写/审查”的真实分工和输出形式。
3. 本地 PLC 技术栈规则在 [plc-rules.md](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/.trae/rules/plc-rules.md)，已声明核心规范来自：
   - [903_定时器使用规范_LSP.md](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/00_通用规范/PLC编程/903_定时器使用规范_LSP.md)
   - [904_SCL注释规范_LSP.md](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/00_通用规范/PLC编程/904_SCL注释规范_LSP.md)
   - [905_SCL编程规范_LSP.md](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范_LSP.md)
   - [906_错误预防规则_LSP.md](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/00_通用规范/PLC编程/906_错误预防规则_LSP.md)
   - [907_项目配置规范_LSP.md](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/00_通用规范/PLC编程/907_项目配置规范_LSP.md)
4. [plc-rules.md](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/.trae/rules/plc-rules.md) 当前把“FB_TON 调用必须包含完整参数”一类规则写成了本地约束；这类内容需要在技能中表述为“先分清平台事实 vs 本地规范约定”。
5. 通过 GitHub 只读调研，已经拿到可借鉴的工业型分析框架，重点来自：
   - `Czarnak/totally-integrated-claude`
   - 其参考材料强调：
     - 先建立 Process Architect 视角：过程、执行器、传感器、状态、物理约束。
     - 再看安全、硬件、通信、边界条件和防御性编程。
     - 审查严重度要由工艺风险决定，而不是仅由语法问题决定。

## Proposed Changes

### 1. 重写技能定位与适用边界

修改文件：
- [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md)

变更内容：
- 将技能定位改为“Siemens TIA Portal PLC / 电气工程主入口”。
- 明确主适配对象：S7-1200、S7-1500、SCL/ST、FB/FC/DB、实例 DB、扫描周期逻辑。
- 明确非主场景：
  - Python/Web 不负责。
  - PM/需求/项目推进不负责。
  - 若涉及 LAD/FBD、TO/轴控、HMI/网络，仅作为扩展能力，不作为本次重构核心。

目的：
- 让技能名副其实，避免继续以“通用 PLC”口径输出模糊建议。

### 2. 重构“规则优先”章节，拆分为“平台事实 / 本地规范 / 项目约束”

修改文件：
- [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md)

变更内容：
- 新增三层知识边界：
  - `TIA 平台事实`：如实例化、FB 调用、静态变量初始化、扫描周期、实例 DB、符号访问、优化块访问等。
  - `本地 LSP 规范`：来自 [plc-rules.md](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/.trae/rules/plc-rules.md) 和 903/904/905/906/907。
  - `项目级约束`：项目内 PM_SESSION、现有接口、文档版本、变更兼容。
- 在技能中明确一句硬规则：
  - 先判断“这是 TIA 平台事实，还是本地规范约定”，禁止混淆。

目的：
- 避免技能把本地规则错当成西门子平台真相。

### 3. 把工作流程改成“TIA 工程师视角”的审查顺序

修改文件：
- [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md)

变更内容：
- 将现有“写代码前必须先读 / 结束后回写”等流程，前置插入一个新的分析顺序：
  1. 识别工艺对象与物理过程
  2. 识别执行器、传感器、互锁、安全态
  3. 识别运行模式、状态机、手自动边界
  4. 再检查 TIA/SCL 实现方式
  5. 最后才对照本地规范
- 增加“禁止先下语法判决、后补工艺理解”的反模式说明。

目的：
- 把技能从“语法检查器”重构成“真正懂工艺的 PLC 工程助手”。

### 4. 重写 TIA 基本编程常识章节

修改文件：
- [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md)

变更内容：
- 将已有临时补丁整理成完整小节，覆盖：
  - FB/FC/DB/实例 DB 基本模型
  - SCL 中功能块实例调用的典型顺序
  - 静态变量初始化与扫描周期语义
  - 定时器、边沿、状态机的常见写法
  - 手动模式/自动模式/故障模式的边界
  - 传感器缺失、单传感器、反馈超时、执行器卡滞这类真实工艺问题
- 特别加入“不要用纯 IT 语言模型经验覆盖 TIA 事实”的禁止性表述。

目的：
- 把技能的底层知识从“零散补丁”升级为“成体系的 TIA 常识”。

### 5. 重构工作模式与输出模板

修改文件：
- [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md)

变更内容：
- 现有工作模式保留大类，但重写每种模式的最低输出：
  - PLC 编程：必须给出工艺假设、接口影响、互锁影响、回归点。
  - 规范检查：必须区分“平台错误 / 本地规范偏差 / 文档不同步”。
  - 程序文档：必须说明与源程序一致性。
  - 现场调试：必须输出复现条件、临时措施、永久修复建议、风险边界。
- 增加统一结论模板：
  - `工艺视角`
  - `TIA实现视角`
  - `本地规范视角`
  - `风险与人工复核`

目的：
- 让技能输出可直接用于 PLC 审查和交接，而不是只给泛泛建议。

### 6. 加入 GitHub 调研吸收的工业级视角

修改文件：
- [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md)

变更内容：
- 以“参考方法论”形式吸收如下视角，不直接复制外部内容：
  - Process Architect：先看过程与物理约束。
  - Defensive Coding：边界检查、异常路径、输入可信度。
  - Hardware/Security Awareness：当任务涉及硬件配置、通信或保护级别时，必须提醒“需要硬件配置资料，否则只能做保守判断”。

目的：
- 提升技能深度，但仍保持与你当前本地规范体系兼容。

## Assumptions & Decisions

### 已确认决策

- 本次只重构技能本身，不扩展到其他技能。
- 本次重点是 [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md) 与本地规范映射。
- 主适配平台是 TIA Portal 下的 S7-1200/1500 + SCL。
- 最优先解决的是“编程方法错误”，不是文风或措辞问题。

### 当前假设

- 暂不拆子技能。
- 暂不新增额外参考文档文件；优先把技能本体重构清楚。
- 暂不处理 LAD/FBD、TO、轴控、WinCC、网络安全的深层扩展，只保留扩展入口和边界提醒。

## Verification Steps

计划执行后，按下面步骤验证重构是否达标：

1. 通读 [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md)，确认“平台事实 / 本地规范 / 项目约束”三层边界清晰。
2. 抽查技能是否明确写死主场景为 TIA Portal / S7-1200 / S7-1500 / SCL。
3. 抽查技能工作流是否把“工艺/物理/互锁/安全态”放在语法与规范之前。
4. 抽查技能是否删除或改写了会误导 TIA 编程模型的表述。
5. 用一个典型场景做心智验收：
   - 气缸/真空阀/输送机 FB 审查
   - 预期先输出工艺边界、再输出实现问题、最后对照规范
6. 确认技能仍保留 PM_SESSION 回写要求，但不会让连续性规则喧宾夺主。

