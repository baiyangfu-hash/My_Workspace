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

## 工具依赖

### SpecMgr 规范管理工具（SW-2026-006）

SpecMgr 是本工作空间规范体系的核心管理工具，pm-workflow 在规范相关操作中必须调用。

- **源码路径**：`01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-006_规范管理工具/02_源代码/`
- **Wrapper 脚本**：`Python311/Scripts/specmgr.cmd` + `specmgr_run.py`（已配置，任意目录可直接调用）
- **调用方式**：
  ```powershell
  # 直接使用 specmgr 命令（推荐，已通过 wrapper 脚本全局可用）
  specmgr -w "<工作空间根>" check
  specmgr -w "<工作空间根>" index
  specmgr -w "<工作空间根>" frontmatter
  specmgr -w "<工作空间根>" report

  # 备选：cd 到源码目录后用 python -m 调用
  cd "<工作空间根>/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-006_规范管理工具/02_源代码"
  python -m specmgr -w "<工作空间根>" check
  ```
- **关键语法**：`-w` / `--workspace` 是**组级别选项**，必须放在子命令之前，如 `specmgr -w <path> check`（不是 `specmgr check -w <path>`）
- **规范注册表**：`00_Obsidian_Base全局规范文件仓库/spec_registry.json`

## 你在新对话里怎么启动（推荐口令）

- `pm: 进入 <项目根目录绝对路径>`
- `pm: 初始化 <项目编号> <项目根目录绝对路径>`
- `pm: 本轮目标 <一句话>`
- `pm: 需求变更 <一句话>`
- `pm: 迭代开始 <迭代编号/里程碑> <一句话目标>`
- `pm: 报Bug <一句话>；复现=<可选>`
- `pm: 重构提案 <一句话>`
- `pm: 交付准备 <版本号> <范围一句话>`
- `pm: 规范变更 <spec_id或一句话描述>`
- `pm: 健康检查 当前项目`
- `pm: 健康检查 全工作空间`
- `pm: 规范巡检 <check-id>`

## 总控流程（每次执行都遵守）

### Step 0：定位并读取 PM_SESSION

1. 在项目根目录查找 `PM_SESSION_<项目编号>.md`
2. 若不存在：创建初始化版本（见"PM_SESSION 模板"）
3. 读取并输出一段"当前状态摘要"（只要 8-12 行）：
   - 项目定位
   - 当前版本/里程碑
   - 本轮目标
   - 进行中事项（最多 5 条）
   - 未决问题（最多 5 条）
   - 风险/依赖（最多 5 条）
4. **引用完整性验证**（每次读取 PM_SESSION 后必须执行）：
   - 遍历 `artifacts_index` 中所有路径引用，检查对应文件是否存在于磁盘
   - 若发现失效引用：输出 `⚠️ N条引用路径已失效` 警告，列出具体路径
   - 对失效引用建议用户确认是否需要更新或删除
5. **规范弃用检查**（与 spec_registry.json 联动）：
   - 读取工作空间根目录下 `00_Obsidian_Base全局规范文件仓库/spec_registry.json`
   - 遍历 PM_SESSION 中引用的规范文件，检查其 spec_id 是否在注册表中标记为 `deprecated` 或 `archived`
   - 若引用的规范已被 `replaced_by` 替代：输出 `⚠️ 规范 XXX 已被 YYY 替代，建议更新引用` 警告
   - 若引用的规范不在注册表中：输出 `ℹ️ 规范 XXX 未在注册表中登记` 提示
6. **默认健康自检**（每次读取 PM_SESSION 后执行轻量检查）：
   - 默认只检查“当前项目 PM_SESSION + 直接文档引用”的完整性
   - 若可用，优先运行：
     - `specmgr -w "<工作空间根>" check --scope project --project-root "<项目根>"`
   - 若当前环境不支持 `--scope project`：退化为仅手动检查当前 PM_SESSION 中的路径与关键规范引用，不主动触发全工作空间巡检
   - 将结果摘要报告给用户，只说明当前项目是否存在失效引用、已废弃规范引用或明显缺失的关键文档
7. **显式规范巡检**（仅在以下场景执行较重检查）：
   - 用户明确输入 `pm: 健康检查 全工作空间`
   - 用户明确输入 `pm: 规范巡检 <check-id>`
   - 本轮事件属于 Event F：规范变更/版本升级
   - 用户明确要求排查规范漂移、索引失效、交叉引用断裂
   - 执行全仓巡检时，使用 `specmgr -w "<工作空间根>" check`
   - 若只需定向检查，优先使用 `specmgr -w "<工作空间根>" check -c <check-id>`
   - 仅在用户明确要求修复时，才建议 `--auto-fix` 或 `--auto-fix --dry-run`
8. **代码规范合规自检**（仅在 PLC 项目且用户明确要求代码规范巡检时执行）：
   - 使用 `greprg` 扫描项目下所有 `*.scl` 文件，检测以下注释合规问题（参照 LSP-904 V1.2.0）：
     - **R1-中文标点**：`，` `。` `：` `；` `（）` 等全角标点，应替换为英文半角
     - **R2-嵌套注释**：`(* ... (* ... *) ... *)` 严格禁止
     - **R3-注释内容含标记**：注释文本中不能出现 `(*` 或 `*)` 字符串
     - **R4-变量注释格式**：变量声明行注释应使用 `//` 而非 `(* *)`
   - 将违规清单报告给用户，按优先级（R1>R2>R3>R4）排列
   - 若用户未明确要求代码规范巡检：不要默认扫描整个项目的 `*.scl`
   - 若发现违规：输出 `🔴 N处注释不合规，建议运行 .trae/temp/check_scl_comments.ps1 详细检查`

### Step 1：判定本次事件类型（Event）

把所有活动归一为 6 类事件，并且每次只处理 1 个事件：

- Event A：需求新增/需求变更（Scope Change）
- Event B：迭代推进（Iteration）
- Event C：重构/技术债（Refactor）
- Event D：缺陷审查/修复（Bug）
- Event E：交付/发布（Delivery）
- Event F：规范变更/版本升级（Spec Change）

若用户描述同时包含多个事件：先要求拆分，并按优先级一次处理一个。

### Step 2：最小提问（不超过 2-3 个问题一轮）

按事件类型提问，目标是把本轮活动变成“可验收”的条目：

- 需求变更：变更原因 + 影响范围（功能/界面/数据/兼容）+ 是否影响里程碑
- 迭代：迭代目标 + 验收标准 + 风险/依赖
- 重构：动机 + 边界 + 不可破坏行为（回归清单）
- Bug：复现步骤 + 期望/实际 + 影响范围/优先级
- 交付：版本号 + 交付范围 + 验收人/验收项
- 规范变更：变更范围（哪些 spec_id）+ 影响项目 + 是否 Breaking Change + 替代规范（replaced_by）

### Step 3：产物更新（文档为主）

按事件类型更新/生成文档，并把索引写回 PM_SESSION：

- PRD/REQ：用 `product-requirements` / `prd` 的方法论完成澄清与落稿
- 任务拆解：用 `breakdown-plan` 的结构把需求落到 Epic/Feature/Story/Enabler/Test
- UI/线框：用 `wireframe-design` + `wireframe-prototyping` 产出线框交付清单与状态覆盖（空态/错态/加载态）
- GitHub 项目管理（可选）：用 `github-project-management` 做看板/里程碑同步
- **SpecMgr 规范健康检查**（当本次事件涉及规范文件变更时必须执行）：
  - 规范变更时优先运行 `specmgr -w "<工作空间根>" check`
  - 若发现版本漂移（SHC-002）或链接断裂（SHC-006），建议运行 `specmgr -w "<工作空间根>" check --auto-fix --dry-run` 预览修复
  - 将检查结果摘要写入 PM_SESSION 的 `spec_compliance` 字段

### Step 4：会话落盘（PM_SESSION 更新规则）

1. 每次事件处理完，必须更新 `PM_SESSION_<项目编号>.md` 的：
   - `current_focus`
   - `status_summary`
   - `artifacts_index`
   - `change_log / iteration_log / bug_log / refactor_log / release_log / spec_change_log`（按事件写一条）
   - `open_questions`（未解决问题）
2. 不覆盖历史记录；新增条目用递增序号或日期
3. **规范漂移预防**（当本次事件涉及规范文件时必须执行）：
   - 若修改了规范文件，验证项目级副本（如有）的版本号与 `spec_registry.json` 中的 `canonical_path` 版本一致
   - 若修改了规范文件，更新 `spec_registry.json` 中对应条目的 `version` 和 `canonical_path`（如版本号或路径变更）
   - 若规范被替代（replaced_by），更新所有引用该规范的 PM_SESSION 中的路径

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
- spec_compliance:
  - last_check: <YYYY-MM-DD>
  - result: <通过/警告摘要>

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
- spec_change_log:
  - <YYYY-MM-DD> <spec_id> <变更类型(升级/替代/废弃)> <影响项目> <状态>
```

## 与“本地文档同步”的建议

- 纯文本（md/json/yaml）：建议用 Git 管理历史；云盘只做镜像备份
- 二进制附件（图片/安装包/导出文件）：放云盘，并在 `Artifacts Index` 里记录可追溯路径
