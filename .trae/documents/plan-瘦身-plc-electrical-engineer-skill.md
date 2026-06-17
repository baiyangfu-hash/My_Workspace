# `plc-electrical-engineer` SKILL.md 瘦身方案（拆分+按需加载）

## Summary

目标：在不显著影响既有能力的前提下，降低 `plc-electrical-engineer` 初始上下文体积，避免一次加载过多提示词导致上下文爆炸。

核心策略：

- 将 [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md) 重构为“内核（Kernel）”：只保留定位、硬规则、工作流、任务路由、引用索引与按需加载协议。
- 将大段“知识讲解/模板/清单”拆分到 `refs/` 文档中；需要时再读取对应 `refs/*.md`。
- 清理 `SKILL.md` 顶部 YAML 区的异常超长空白字符（当前 line 2 存在大量空白），这是最直接的 token 浪费来源之一。

## Current State Analysis（基于仓库实际内容）

### 现状文件

- 技能主文件：[SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md)
  - 文件内容包含：定位/边界、三层体系、五通道分析法、证据等级、强制规则、TIA 常识、工程上下文、通用控制场景树、设备场景族、PM 联动、编码/退出协议、评审清单等。
  - YAML 区域存在异常的超长空白（Read 输出中第 2 行显示为大量空白后接 `name:`），会显著增加提示词 token。
- 工作区已存在与本技能相关的长文档（可复用但不应默认加载）：
  - [plc-electrical-engineer-tia-资料基线.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/documents/plc-electrical-engineer-tia-资料基线.md)
  - [plc-electrical-engineer-tia-编程前必要文档.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/documents/plc-electrical-engineer-tia-编程前必要文档.md)
  - [plc-状态机模板对照表.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/documents/plc-状态机模板对照表.md)

### 问题归因（瘦身角度）

- `SKILL.md` 同时承载“路由/流程/硬规则”与“大量可选参考资料”，导致默认加载时上下文远超多数任务所需。
- 存在明显的可压缩区域：
  - 解释性长段落可改为“规则 + 触发条件 + 引用路径”。
  - 场景族、检查表、模板类内容适合放入 `refs/`，由任务类型决定是否读取。
  - YAML 区异常空白应当直接删除。

## Assumptions & Decisions

### 已确认决策（来自本轮澄清）

- 采用“拆分 + 按需加载（推荐）”方案。
- 引用内容优先放到 `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\refs\` 目录内。

### 约束与兼容性原则

- 保持技能入口文件路径不变：`plc-electrical-engineer/SKILL.md` 仍然存在且为主入口。
- 不引入新的外部依赖；仅做 Markdown 文档拆分与文本重写。
- 不新增任何注释规则以外的“代码行为改变”；目标是“默认加载更小 + 需要时仍能取回相同信息”。

## Proposed Changes（决策完备的改动清单）

### 1) 新增 `refs/` 目录与索引文件

新增目录：

- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\refs\`

新增文件：

- `refs/INDEX.md`
  - 内容：refs 的目录树、每份文档的用途、典型触发条件、读取优先级、与 `.trae/documents` 既有材料的对应关系。

### 2) 拆分长内容到 `refs/*.md`

从当前 `SKILL.md` 中迁移（剪切）以下大块内容到 `refs/`，并在迁移后对内容做“轻量格式压缩”（避免长篇散文，保留可执行规则与检查点）：

- `refs/platform-and-tia-basics.md`
  - 来源：`TIA Portal 编程常识`、`TIA 工程上下文意识` 相关章节
  - 用途：当任务涉及“实例化/调用/扫描周期/优化访问/生成块/导入导出/兼容性”等平台判断时读取
- `refs/control-skeleton.md`
  - 来源：`通用控制场景树`、通用控制骨架相关段落
  - 用途：当任务是“新建 FB/重构 FB/需要输出结构骨架”时读取
- `refs/scenario-families.md`
  - 来源：`设备 / 功能场景族` 及其子场景说明（双位置执行器、真空、输送、步序、报警联锁等）
  - 用途：当用户点名对象（气缸/真空阀/夹具/输送/状态机/报警联锁）时读取
- `refs/review-and-safety.md`
  - 来源：高风险反模式、FB 设计检查清单、代码评审 6 维度、必须人工复核/安全边界等
  - 用途：当任务是“评审/规范检查/交付审查/安全边界提示”时读取

说明：

- `Step 0-7` 这类“工作流与刚性协议”属于内核能力，继续保留在 `SKILL.md`，但改为更短的步骤表述，并把细节性的检查表移入 `refs/`。
- 对“已有 `.trae/documents` 长文档”不做删除；在 `refs/INDEX.md` 和 `SKILL.md` 中保留指向它们的索引，避免重复维护。

### 3) 重写 `SKILL.md` 为 Kernel（并清理 YAML 异常空白）

改动文件：

- [SKILL.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/skills/plc-electrical-engineer/SKILL.md)

改动目标（结构）：

1. YAML 头：移除所有异常空白字符，保持 3-6 行简洁元数据。
2. 定位与边界：保留“负责/不负责/主平台”与本地规范索引（以路径列表形式）。
3. 任务路由（最关键）：给出“工作类型判定 → 需要读取哪些 refs/与哪些 LSP 规范”的表格（最小集合原则）。
4. 硬规则（只留必须常驻的）：
   - R1 注释只允许 `(* *)`（保留）
   - R2 极性映射必须 IF/ELSE（保留）
   - R3 定时器调用三段式（保留，但把长解释移入 `refs/platform-and-tia-basics.md` 或引用 LSP-903）
   - R6 输出所有权（保留核心约束，详细检查点移入 `refs/review-and-safety.md`）
5. 按需加载协议（明确且可执行）：
   - 在回答前先判定任务类型与对象；按路由读取对应 `refs/*.md` 与必要规范文件；禁止“把 refs 全部读一遍”。
   - 若证据不足，必须输出 Known/Assumed/Open point/Must confirm on site 标签（简述版），详细机制放入 `refs/review-and-safety.md` 或引用现有 documents。
6. 与 `pm-workflow`/`fullstack-engineer` 的切换规则：保留（但压缩为 10-20 行）。

### 4) 迁移一致性与去重

- 迁移时不做“新增知识”，只做“位置变化 + 表述压缩 + 去重”。
- `SKILL.md` 只保留：
  - 任务路由与必读列表
  - 核心硬规则
  - 输出格式（最小模板）
  - 退出协议（PM_SESSION 回写等）概要
- 所有“长解释/长清单/长模板”都移至 `refs/`，并在 `SKILL.md` 用 1 行触发条件 + 1 行路径指向。

## Verification Steps（执行阶段验证）

1. 体积验证
   - 对比改造前后 `SKILL.md` 的行数与文件大小，确认显著下降（至少去除 YAML 异常空白 + 大段迁移）。
2. 能力回归（心智验收）
   - 任选 3 类典型任务做“手工走流程”验收：
     - 气缸/真空阀 FB 评审（应触发读取 `refs/scenario-families.md` + `refs/review-and-safety.md`）
     - 定时器/超时/消抖修复建议（应触发读取 `refs/platform-and-tia-basics.md` + LSP-903）
     - 状态机/步序设计（应触发读取 `plc-状态机模板对照表.md` 或 `refs/scenario-families.md` 中对应索引）
3. 路由覆盖验证
   - 检查 `SKILL.md` 的路由表：每个工作类型至少关联 1 个 refs 文档或本地规范文件；避免“路由缺口导致不知道读什么”。
4. 可维护性验证
   - `refs/INDEX.md` 中每份 refs 文档都有明确用途与触发条件；避免 refs 成为新的“垃圾场”。

