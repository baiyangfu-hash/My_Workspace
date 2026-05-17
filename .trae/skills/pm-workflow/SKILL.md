---
name: pm-workflow
description: "Standardizes product/project management across sessions using PM_SESSION_<项目编号>.md. Invoke when starting/continuing a project, handling change/iteration/bug/refactor/release, or user says 'pm:' commands."
---

# PM Workflow（产品型项目经理总控）

目标：把“需求澄清 → PRD/REQ/DES → 任务拆解 → 变更/迭代/缺陷/交付”全部固化为可重复流程，并用项目根目录的 `PM_SESSION_<项目编号>.md` 作为单一真源，保证每次新对话无需从零开始。

## 适用范围

- 适用于本工作区内的 PLC 工程与自动化工具类项目（例如 SW-2026-005、DJ-2026-000 等）
- 任务系统以本地文档为主（可选再同步到 GitHub）

## 文件约定（强制）

- 每个项目根目录必须存在会话文件：`PM_SESSION_<项目编号>.md`
- 项目编号优先从项目目录名解析（如 `SW-2026-005_xxx` → `SW-2026-005`）；解析失败则询问用户确认

## 你在新对话里怎么启动（推荐口令）

- `pm: 进入 <项目根目录绝对路径>`
- `pm: 初始化 <项目编号> <项目根目录绝对路径>`
- `pm: 本轮目标 <一句话>`
- `pm: 需求变更 <一句话>`
- `pm: 迭代开始 <迭代编号/里程碑> <一句话目标>`
- `pm: 报Bug <一句话>；复现=<可选>`
- `pm: 重构提案 <一句话>`
- `pm: 交付准备 <版本号> <范围一句话>`

## 总控流程（每次执行都遵守）

### Step 0：定位并读取 PM_SESSION

1. 在项目根目录查找 `PM_SESSION_<项目编号>.md`
2. 若不存在：创建初始化版本（见“PM_SESSION 模板”）
3. 读取并输出一段“当前状态摘要”（只要 8-12 行）：
   - 项目定位
   - 当前版本/里程碑
   - 本轮目标
   - 进行中事项（最多 5 条）
   - 未决问题（最多 5 条）
   - 风险/依赖（最多 5 条）

### Step 1：判定本次事件类型（Event）

把所有活动归一为 5 类事件，并且每次只处理 1 个事件：

- Event A：需求新增/需求变更（Scope Change）
- Event B：迭代推进（Iteration）
- Event C：重构/技术债（Refactor）
- Event D：缺陷审查/修复（Bug）
- Event E：交付/发布（Delivery）

若用户描述同时包含多个事件：先要求拆分，并按优先级一次处理一个。

### Step 2：最小提问（不超过 2-3 个问题一轮）

按事件类型提问，目标是把本轮活动变成“可验收”的条目：

- 需求变更：变更原因 + 影响范围（功能/界面/数据/兼容）+ 是否影响里程碑
- 迭代：迭代目标 + 验收标准 + 风险/依赖
- 重构：动机 + 边界 + 不可破坏行为（回归清单）
- Bug：复现步骤 + 期望/实际 + 影响范围/优先级
- 交付：版本号 + 交付范围 + 验收人/验收项

### Step 3：产物更新（文档为主）

按事件类型更新/生成文档，并把索引写回 PM_SESSION：

- PRD/REQ：用 `product-requirements` / `prd` 的方法论完成澄清与落稿
- 任务拆解：用 `breakdown-plan` 的结构把需求落到 Epic/Feature/Story/Enabler/Test
- UI/线框：用 `wireframe-design` + `wireframe-prototyping` 产出线框交付清单与状态覆盖（空态/错态/加载态）
- GitHub 项目管理（可选）：用 `github-project-management` 做看板/里程碑同步

### Step 4：会话落盘（PM_SESSION 更新规则）

1. 每次事件处理完，必须更新 `PM_SESSION_<项目编号>.md` 的：
   - `current_focus`
   - `status_summary`
   - `artifacts_index`
   - `change_log / iteration_log / bug_log / refactor_log / release_log`（按事件写一条）
   - `open_questions`（未解决问题）
2. 不覆盖历史记录；新增条目用递增序号或日期

## PM_SESSION 模板（初始化用）

将以下模板保存为项目根目录的 `PM_SESSION_<项目编号>.md`，并在首次初始化时尽可能自动补齐链接。

```markdown
# PM_SESSION_<项目编号>

## 0. Meta
- project_id: <项目编号>
- project_name: <项目名称>
- project_root: <绝对路径>
- last_updated: <YYYY-MM-DD>
- owners: <负责人/角色>

## 1. Positioning（项目定位）
- one_liner: <一句话定位>
- users: <目标用户/使用场景>
- non_goals: <明确不做>

## 2. Current Focus（当前焦点）
- current_focus: <本轮目标一句话>
- milestone: <里程碑/版本>
- acceptance: <验收口径（可量化）>

## 3. Status Summary（当前状态摘要）
- in_progress:
  - <最多5条>
- next_up:
  - <最多5条>
- open_questions:
  - <最多5条>
- risks_dependencies:
  - <最多5条>

## 4. Artifacts Index（文档索引）
- prd:
  - <路径或链接>
- req:
  - <路径或链接>
- des:
  - <路径或链接>
- test:
  - <路径或链接>
- change_mgmt:
  - <路径或链接>
- delivery:
  - <路径或链接>

## 5. Logs（按事件沉淀）
- change_log:
  - <YYYY-MM-DD> <变更摘要> <影响范围> <状态>
- iteration_log:
  - <YYYY-MM-DD> <迭代编号> <目标> <状态>
- bug_log:
  - <YYYY-MM-DD> <Bug摘要> <优先级> <状态>
- refactor_log:
  - <YYYY-MM-DD> <重构摘要> <范围> <状态>
- release_log:
  - <YYYY-MM-DD> <版本号> <范围> <状态>
```

## 与“本地文档同步”的建议

- 纯文本（md/json/yaml）：建议用 Git 管理历史；云盘只做镜像备份
- 二进制附件（图片/安装包/导出文件）：放云盘，并在 `Artifacts Index` 里记录可追溯路径

