# pm-workflow 超时与全仓扫描诊断修复计划

## 1. Summary

- 目标：修复 `pm-workflow` 在本工作空间中每次任务都触发高成本扫描、思考时间过长、频繁超时的问题。
- 结论：当前问题不是单点故障，而是 `pm-workflow` 提示词与 `specmgr` 默认扫描模型叠加导致的结构性性能问题。
- 修复策略：采用“结构性修复 + 默认项目级最小检查”方案。
- 保持兼容：保留显式的全工作空间巡检能力，但不再作为 PM 每轮任务的默认动作。

## 2. Current State Analysis

### 2.1 已确认的根因

1. `pm-workflow` 将全工作空间健康检查定义为每次读取 PM_SESSION 后的强制步骤。  
   证据文件：`c:\Users\fubai\Desktop\My_Workspace\.trae\skills\pm-workflow\SKILL.md`
   - Step 0 明确写明“每次读取 PM_SESSION 后必须执行”：
     - `specmgr -w "<工作空间根>" check`
   - 同一阶段还要求 PLC 项目执行项目下全部 `*.scl` 注释扫描。

2. `specmgr check` 在未指定检查项时会执行 `HealthChecker.run_all()`。  
   证据文件：`01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-006_规范管理工具/02_源代码/specmgr/commands/check.py`
   - `CheckService.run()` 在 `check_ids` 为空时调用 `run_all()`。

3. `specmgr` 的规范扫描本身采用递归 `rglob("*.md")`。  
   证据文件：`.../specmgr/core/scanner.py`
   - `_collect_md_files()` 直接递归扫描默认规范目录下全部 Markdown。

4. 检查器中新增的 PM/交叉引用检查进一步扩大扫描范围。  
   证据文件：`.../specmgr/core/checker_base.py`
   - `PMSessionRefChecker` 使用 `workspace.rglob("PM_SESSION_*.md")` 扫描整个工作空间。
   - `SpecCrossRefChecker` 会遍历所有规范文件的 Markdown 链接。

5. PM 使用说明文档与 skill 内容存在同步漂移，导致“重扫描策略”被重复固化。  
   证据文件：`00_Obsidian_Base全局规范文件仓库/01_项目管理域/00_元规则与治理/004_PM_WORKFLOW总控Skill使用说明_PM-V1.0.0.md`
   - 该权威说明仍强调全量 `specmgr` 巡检，且命令示例与工作区规则中的推荐写法不完全一致。

### 2.2 非根因但会放大问题的因素

1. 工作空间体量很大，且存在多个 `PM_SESSION_*.md`。
2. 工作空间根下 `.trae/.ignore` 为空，当前没有为 PM 工作流提供额外的裁剪提示。
3. 现有 PM skill 缺少“项目级默认动作”和“显式全仓巡检”的分层边界。

### 2.3 本次修复的设计决策

- 默认行为改为：项目级最小检查。
- 全工作空间检查改为：显式触发。
- `specmgr` 默认 CLI 兼容现状，不破坏现有已有脚本。
- `pm-workflow` 不再把 `specmgr -w <工作空间根> check` 作为每轮任务的强制动作。

## 3. Proposed Changes

### 3.1 调整 PM skill 默认流程

#### 文件

- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\pm-workflow\SKILL.md`

#### 修改内容

1. 重写 Step 0 的“例行自检”策略：
   - 保留读取 `PM_SESSION_<项目编号>.md`
   - 保留当前状态摘要输出
   - 保留项目内引用完整性检查
   - 删除“每次都必须运行 `specmgr -w "<工作空间根>" check`”的强制要求
   - 删除“每次都必须扫描项目下所有 `*.scl`”的强制要求

2. 引入新的默认策略：
   - 默认仅执行“当前项目 PM_SESSION + 直接文档引用”的轻量检查
   - 只有在以下场景才建议更重的检查：
     - 用户显式要求“全仓巡检/规范健康检查”
     - 本轮事件属于“规范变更/版本升级”
     - 用户要求排查规范漂移、失效链接、索引异常

3. 增加明确口令约定，避免模型自行扩大范围：
   - `pm: 健康检查 当前项目`
   - `pm: 健康检查 全工作空间`
   - `pm: 规范巡检 <check-id>`

#### 修改原因

- 当前超时主因来自 skill 层把高成本动作定义成“每次都做”。
- 优先在 prompt 层收缩默认范围，能立刻减少 token、搜索轮次和外部工具调用成本。

### 3.2 同步更新 PM 权威说明文档

#### 文件

- `c:\Users\fubai\Desktop\My_Workspace\00_Obsidian_Base全局规范文件仓库\01_项目管理域\00_元规则与治理\004_PM_WORKFLOW总控Skill使用说明_PM-V1.0.0.md`

#### 修改内容

1. 将使用说明与 `pm-workflow` 新默认策略对齐。
2. 明确区分：
   - 日常 PM 会话：项目级最小检查
   - 规范治理任务：显式全仓巡检
3. 统一 `specmgr` 命令写法为工作区规则要求的形式：
   - `specmgr -w "<工作空间根>" check`
   - 不再混用 `specmgr check -w ...`

#### 修改原因

- 目前 skill 与权威文档都在重复放大全仓扫描策略。
- 若只改 skill 不改规范说明，后续容易被再次覆盖回旧行为。

### 3.3 为 `specmgr check` 增加项目级模式

#### 文件

- `.../specmgr/commands/check.py`
- `.../specmgr/services/check_svc.py`
- `.../specmgr/core/scanner.py`
- `.../specmgr/core/checker_base.py`
- `.../specmgr/core/config.py`

#### 修改内容

1. 在 `check` 命令增加范围参数：
   - `--scope workspace|project`
   - 默认值保持 `workspace`
   - 新增 `--project-root <绝对路径>`，当 `--scope project` 时必填

2. 在 `CheckService.run()` 中引入范围感知逻辑：
   - `scope="workspace"`：保持现有行为
   - `scope="project"`：
     - 若用户未显式传 `-c/--check-id`，默认只执行 `SHC-009`
     - 若用户显式传了检查项，则仅执行指定检查项

3. 在 `SpecScanner` 中增加项目范围上下文：
   - 保存可选 `project_root`
   - 新增帮助方法，供检查器只遍历项目内 `PM_SESSION_*.md`

4. 重构 `PMSessionRefChecker`：
   - 不再直接 `workspace.rglob("PM_SESSION_*.md")`
   - 改为调用 `scanner` 提供的 PM_SESSION 枚举接口
   - 在 project 模式下仅扫描 `project_root` 子树中的 `PM_SESSION`

5. 保持 `SHC-010` 仍为工作空间级检查：
   - 不纳入 project 模式默认检查集
   - 仅在用户明确需要规范交叉引用巡检时运行

#### 修改原因

- 仅修改 skill 可以止血，但不足以提供稳定、可复用、可测试的项目级检查能力。
- 通过 CLI 增加显式 scope，可以让 PM skill、手工命令、后续自动化都复用同一条轻量路径。

### 3.4 测试补强

#### 文件

- `.../tests/test_cli.py`
- `.../tests/test_checker_base.py`
- `.../tests/test_services.py`

#### 修改内容

1. 为 CLI 新增测试：
   - `check --scope project --project-root <path>` 能正常执行
   - `check --scope project` 缺少 `--project-root` 时给出错误

2. 为服务层新增测试：
   - project 模式默认只跑 `SHC-009`
   - workspace 模式保持原有 `run_all()` 行为

3. 为检查器新增测试：
   - `PMSessionRefChecker` 在 project 模式下不会扫描项目根之外的 `PM_SESSION`

#### 修改原因

- 这次修复的风险点在“范围控制”是否真的生效，必须用测试锁住。

## 4. Implementation Plan

1. 先修改 `pm-workflow` skill，去掉默认全仓巡检和默认全项目 `*.scl` 扫描的强制语义，加入显式口令和触发条件。
2. 再修改 PM 权威说明文档，确保规范和 skill 一致，避免后续漂移。
3. 为 `specmgr check` 增加 `--scope` 与 `--project-root` 参数，并把 project 模式下的默认检查集收缩到 `SHC-009`。
4. 重构 `SpecScanner`/`PMSessionRefChecker`，把 PM_SESSION 扫描范围从“整个工作空间”改为“由 scope 决定”。
5. 增加 CLI、服务层、检查器三类测试，验证范围隔离和兼容性。
6. 运行相关测试与诊断检查，确认没有引入回归。

## 5. Assumptions & Decisions

- 假设用户口中的“pm skill”即当前工作空间自定义的 `pm-workflow`。
- 决策：保留 `specmgr` 现有 workspace 级默认行为，避免破坏已有手工使用方式。
- 决策：PM 默认不再自动触发全仓规范巡检。
- 决策：规范交叉引用检查 `SHC-010` 属于治理类重操作，不进入默认项目级路径。
- 决策：PLC 注释合规扫描改为按需触发，不再作为 PM 每轮任务默认动作。

## 6. Verification Steps

1. 静态验证
   - 检查 `pm-workflow` 文本中不再出现“每次读取 PM_SESSION 后必须执行 `specmgr -w "<工作空间根>" check`”。
   - 检查 PM 使用说明文档的命令示例与 `project-rule.md` 保持一致。

2. 单元测试
   - 在 `SW-2026-006_规范管理工具` 源码目录运行相关测试：
     - `tests/test_cli.py`
     - `tests/test_checker_base.py`
     - `tests/test_services.py`

3. 行为验证
   - 用一个项目根执行：
     - `specmgr -w "<工作空间根>" check --scope project --project-root "<项目根>"`
   - 预期：
     - 仅检查当前项目下的 `PM_SESSION`
     - 不遍历整个工作空间的全部 `PM_SESSION`
     - 不默认触发 `SHC-010`

4. 回归验证
   - 执行原有命令：
     - `specmgr -w "<工作空间根>" check`
   - 预期：
     - 仍按原 workspace 级模式工作
     - 不影响已有全仓规范治理流程

## 7. 预期收益

- 显著减少 PM skill 每轮任务的搜索范围与 token 消耗。
- 降低无关规范治理操作对普通项目会话的干扰。
- 将“项目级工作流”和“全仓治理流程”清晰分层，避免再次出现默认全仓扫描。
