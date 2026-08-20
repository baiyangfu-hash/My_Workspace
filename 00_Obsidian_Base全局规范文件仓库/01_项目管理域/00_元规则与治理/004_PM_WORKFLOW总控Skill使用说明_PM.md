---
spec_id: PM-004
title: PM_WORKFLOW总控Skill使用说明
version: V1.3.0
domain: pm
lifecycle: stable
type: PM_WORKFLOW
status: active
canonical_path: "00_Obsidian_Base全局规范文件仓库/01_项目管理域/00_元规则与治理/004_PM_WORKFLOW总控Skill使用说明_PM.md"
---

# PM_WORKFLOW 总控Skill 使用说明（PM_SESSION 驱动）

## 1. 目标
- 把“需求澄清 → PRD/REQ/DES → 任务拆解 → 变更/迭代/缺陷/交付”固化为可重复流程
- 通过项目根目录的会话文件作为单一真源，保证跨会话连续：`PM_SESSION_<项目编号>.md`
- **作为 Obsidian 全局规范仓库（`00_Obsidian_Base/`）的唯一维护 owner**：凡规范新建、修改或删除，自动完成注册表更新与全局索引同步
- 以本地文档为任务系统主载体，必要时可再同步到 GitHub

## 2. 核心约定
### 2.1 会话文件（强制）
- 每个项目根目录必须存在：`PM_SESSION_<项目编号>.md`
- 项目编号遵循 RULE-001：`[前缀]-YYYY-NNN`（示例：`SW-2026-005`、`DJ-2026-000`）
- 会话文件名采用 A 方案：`PM_SESSION_<项目编号>.md`

### 2.2 单一真源（Single Source of Truth）
- 任何需求/范围/里程碑/风险/未决问题的“当前结论”必须回写到 PM_SESSION
- PRD/REQ/DES/CHG/TEST/交付等产物路径必须登记在 PM_SESSION 的 `Artifacts Index`

### 2.3 Obsidian 全局规范自动同步硬规则
- `pm-workflow` 独占全局规范的生命周期管理（新建、修订、作废、归档、删除）；
- 任何规范变更发生后，PM 技能必须自动执行：
  1. 更新 `00_Obsidian_Base全局规范文件仓库/spec_registry.json`；
  2. 运行 `auto-pm spec index` 自动重新生成 `00_INDEX_全局规范索引.md` 与通用规范 README；
  3. 运行 `auto-pm spec check` 确保全局 0 孤立规范、0 索引断链。

## 3. 总控Skill 做什么
### 3.1 初始化（已有项目/新项目通用）
- 若项目根目录缺少 `PM_SESSION_<项目编号>.md`：自动生成初始化模板
- 自动挂接已有文档（PRD/REQ/DES/变更/测试/交付等）到 `Artifacts Index`
- 生成“当前状态摘要”：当前焦点、进行中事项、下一步、未决问题、风险依赖
- 默认只做项目级最小检查，不把全工作空间巡检作为每轮会话的默认动作

### 3.2 例行更新（每次活动结束必须做）
把所有项目活动统一为 8 类事件（每次只处理一种）：
- Event A：需求新增/需求变更（Scope Change）
- Event B：迭代推进（Iteration）
- Event C：重构/技术债（Refactor）
- Event D：缺陷审查/修复（Bug）
- Event E：交付/发布（Delivery）
- Event F：规范巡检（Spec Check）— 规范引用/升级/漂移检查
- Event G：项目初始化（Init）— 空文件夹 → 完整项目骨架
- Event H：旧项目补完（Retrofit）— 已有项目注入连续性机制

每个事件结束后，总控Skill会：
- 生成/更新对应文档产物（PRD/REQ/DES/CHG/TEST/交付）
- 生成/更新任务拆解（Epic/Feature/Story/Enabler/Test）
- 回写 PM_SESSION 的当前状态与对应日志（change_log / iteration_log / bug_log / refactor_log / release_log）
- 默认只验证当前项目 `PM_SESSION` 与直接关联文档引用
- 只有在用户明确要求或发生规范变更时，才执行全工作空间规范巡检

## 4. 推荐口令（新对话也适用）
### 4.1 进入/初始化项目
- `pm: 进入 <项目根目录绝对路径>`
- `pm: 初始化 <项目编号> <项目根目录绝对路径>`

### 4.2 事件触发（选一条即可）
- `pm: 本轮目标 <一句话>`
- `pm: 需求变更 <一句话>`
- `pm: 迭代开始 <里程碑/版本> <一句话目标>`
- `pm: 报Bug <一句话>；复现=<可选>`
- `pm: 重构提案 <一句话>`
- `pm: 交付准备 <版本号> <范围一句话>`
- `pm: 健康检查 当前项目`
- `pm: 健康检查 全工作空间`
- `pm: 规范巡检 <check-id>`

## 5. 与本仓库模板的映射
### 5.1 需求与设计
- PRD：使用 [PRD-001 产品需求文档模板](../01_启动阶段/001_产品需求文档模板_PRD.md)
- REQ：使用 [REQ-020 需求分析文档模板](../02_规划阶段/020_通用需求分析文档模板_REQ.md) 或 [REQ-028 迭代SRS模板](../02_规划阶段/028_迭代需求规格说明书模板_REQ.md)
- DES：使用 [DES-021 详细设计说明书模板](../02_规划阶段/021_通用详细设计说明书模板_DES.md)
- TECH：使用 [TECH-014 技术方案模板](../02_规划阶段/014_技术方案文档模板_TECH.md)

### 5.2 计划、里程碑与迭代
- 迭代计划：使用 [PM-027 迭代项目计划模板](../02_规划阶段/027_迭代项目计划模板_PM.md)
- 里程碑清单：使用 [PM-030 迭代里程碑清单模板](../02_规划阶段/030_迭代里程碑清单模板_PM.md)
- 迭代流程SOP：使用 [PM-033 功能模块迭代流程标准](../02_规划阶段/033_功能模块迭代流程标准_PM.md)

### 5.3 变更、缺陷、测试与交付
- 变更核心规范：使用 [004 文档版本管理与变更核心规范](../04_变更管理/004_通用项目文档版本管理与变更核心规范_DEV.md)
- 变更单/台账/流程：使用 [040 变更单模板](../04_变更管理/040_通用变更单模板_CHG.md)、[041 版本变更台账模板](../04_变更管理/041_通用版本变更台帐模板_CHG.md)、[042 变更管理流程规范](../04_变更管理/042_通用变更管理流程规范_PM.md)
- 缺陷追踪：使用 [019 缺陷跟踪表模板](../03_执行管控/019_缺陷跟踪表模板_BUG.md)
- 测试报告：使用 [018 测试报告模板](../03_执行管控/018_测试报告模板_TEST.md)
- 交付规范：使用 [030 通用项目交付规范](../03_执行管控/030_通用项目交付规范_DEV.md)

## 6. 本地文档同步建议（云盘/多端）
### 6.1 推荐组合（稳定）
- 文本类（md/json/yaml）：使用 Git 管理历史；云盘做镜像备份
- 二进制附件（图片/安装包/导出文件）：放云盘，并在 PM_SESSION 的 `Artifacts Index` 登记路径

### 6.2 仅云盘同步（可用但需纪律）
- 同一时间只允许一个设备编辑同一个 `PM_SESSION_<项目编号>.md`
- 发现冲突文件：以“最新 last_updated 的主文件”为准，将差异合并后删除冲突副本

## 7. 最小落地清单（建议复制到项目 README）
- [ ] 项目根目录存在 `PM_SESSION_<项目编号>.md`
- [ ] PM_SESSION 已登记 PRD/REQ/DES/变更/测试/交付的路径
- [ ] 任一需求变更/bug/重构/迭代/交付后，PM_SESSION 的 Logs 有新增一条记录

## 8. SpecMgr CLI — 规范健康检查与自动修复

SpecMgr（SW-2026-006）提供规范体系的自动化检查与修复能力，工具路径：`01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-006_规范管理工具/02_源代码/`

### 8.0 使用边界

- 日常 PM 会话：默认只做项目级最小检查，重点验证当前项目 `PM_SESSION` 和直接文档引用
- 规范治理任务：当用户明确要求全仓巡检，或本轮属于规范变更/版本升级时，再执行全工作空间检查
- PLC 注释规范扫描：仅在用户明确要求代码规范巡检时执行，不作为 PM 默认动作

### 8.1 基本用法

```bash
# 运行规范健康检查（检测版本漂移、命名不合规、链接失效等8类问题）
specmgr -w <工作空间根目录> check

# 仅检查特定检查项
specmgr -w <工作空间根目录> check -c SHC-002 -c SHC-007

# 仅检查当前项目 PM_SESSION 及其直接引用
specmgr -w <工作空间根目录> check --scope project --project-root <项目根目录>

# JSON格式输出（适合脚本解析）
specmgr -w <工作空间根目录> check --format json

# 只显示错误级别
specmgr -w <工作空间根目录> check --severity error
```

### 8.2 自动修复

```bash
# 预览可自动修复的问题（不实际修改文件）
specmgr -w <工作空间根目录> check --auto-fix --dry-run

# 执行自动修复
specmgr -w <工作空间根目录> check --auto-fix
```

### 8.3 可自动修复的问题类型

| 检查ID | 问题类型 | 自动修复行为 |
|--------|---------|-------------|
| SHC-002 | 版本漂移（frontmatter版本 ≠ 注册表版本） | 更新frontmatter版本字段使其与注册表版本一致，同步更新canonical_path |
| SHC-007 | frontmatter缺失或不完整 | 从注册表数据自动补全spec_id/title/version/lifecycle/canonical_path |

### 8.4 仅检测不可自动修复的问题类型

| 检查ID | 问题类型 | 原因 |
|--------|---------|------|
| SHC-001 | 规范文件重复 | 需人工判断保留哪个 |
| SHC-003 | 引用了已废弃规范 | 需人工确认替代规范 |
| SHC-004 | 索引链接失效 | 需运行 `specmgr index` 重新生成 |
| SHC-005 | 规范未在注册表登记 | 需人工填写完整元数据 |
| SHC-006 | Obsidian/Markdown链接失效 | 需人工确认链接目标 |
| SHC-008 | 规则文件引用路径无效 | 需人工确认正确路径 |

### 8.5 典型使用场景

**场景1：规范迭代后验证一致性**
```bash
# 修改规范文件后，检查是否有版本漂移或命名不合规
specmgr -w <workspace> check
# 发现问题后预览修复
specmgr -w <workspace> check --auto-fix --dry-run
# 确认后执行修复
specmgr -w <workspace> check --auto-fix
```

**场景2：新增规范文件后补全元数据**
```bash
# 新建规范文件后，检查frontmatter是否完整
specmgr -w <workspace> check -c SHC-007
# 自动补全缺失的frontmatter字段
specmgr -w <workspace> check --auto-fix -c SHC-007
```

**场景3：定期规范体系巡检**
```bash
# 每周运行一次全量检查，只看错误和警告
specmgr -w <workspace> check --severity warning
# 发现问题后针对性修复
specmgr -w <workspace> check --auto-fix -c SHC-002
```

### 8.6 其他SpecMgr命令

```bash
# 自动生成规范索引文件（按域生成README）
specmgr -w <工作空间根目录> index
specmgr -w <工作空间根目录> index --domain plc

# 批量添加/更新规范frontmatter
specmgr -w <工作空间根目录> frontmatter --dry-run
specmgr -w <工作空间根目录> frontmatter

# 生成规范元数据汇总报告
specmgr -w <工作空间根目录> report
specmgr -w <工作空间根目录> report --format json
```

## 9. pm-mgr CLI — 项目工作流工具链

pm-mgr（SW-2026-007）提供项目初始化、旧项目补完、健康检查、类型检测和 Spec Snapshot 管理能力。

安装：`pip install -e .`（项目路径：`01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-007_pm工作流工具链/`）

### 9.1 全局选项

所有命令共享 `-w / --workspace <工作空间根目录>`，也可通过环境变量 `PM_MGR_WORKSPACE` 设置。若均未指定，自动向上查找包含 `.trae/` 的目录。

### 9.2 命令接口

| 命令 | 用途 | 必填参数 |
|------|------|---------|
| `pm-mgr init <项目目录>` | 初始化新项目骨架 | `-t software/plc` `-i 项目编号` `-n 项目名称` |
| `pm-mgr retrofit <项目目录>` | 旧项目注入连续性机制 | 项目目录（必须存在） |
| `pm-mgr detect <项目目录>` | 检测项目类型 | 项目目录 |
| `pm-mgr check <项目目录>` | 健康检查 | 项目目录 |
| `pm-mgr snapshot <项目目录>` | 刷新 Spec Snapshot | 项目目录 |

### 9.3 init 创建的产物

| 项目类型 | 目录 | 文档模板 | 骨架文件 | 其他 |
|---------|------|---------|---------|------|
| software | 11 个目录（含PM流程5阶段） | 立项表、PRD、REQ、DES、测试计划 | README、pyproject.toml | hooks + handoffs |
| plc | 24 个目录 | 立项表、需求分析、IO分配表等6个 | README、.plc.json、版本变更台帐 | hooks + handoffs |

### 9.4 check 检查项

| 检查项 | 判定标准 |
|--------|---------|
| PM_SESSION | `PM_SESSION*.md` 文件存在 |
| hooks | `.github/hooks/hooks.json` + 4 个脚本全部存在 |
| handoffs | `.trae/handoffs/` 目录存在 |
| Spec Snapshot | PM_SESSION 中含 `## Spec Snapshot` 区块 |
| PM_SESSION章节完整性 | §0 Meta ~ §9 Next Actions 共10个章节齐全 |
| .gitignore | 项目根目录存在 .gitignore 文件 |

### 9.5 detect 检测优先级

| 优先级 | 信号 | 结果 |
|--------|------|------|
| 1 | `.plc.json` 存在（深度≤3） | `plc` |
| 2 | `pyproject.toml` 存在（深度≤3） | `software` |
| 3 | `*.scl` / `*.db` 文件存在（深度≤3） | `plc` |
| 4 | `main.py` / `package.json` 存在 | `software` |
| 5 | PM_SESSION 上下文推断 | 按内容判定 |

### 9.6 snapshot 规范列表

| 项目类型 | 包含的规范 |
|---------|-----------|
| software | PROJ-016, PRD-001, DEV-031, DEV-032, DEV-210, DEV-211, DEV-220, INT-215, DEV-004, CHG-040, CHG-041, PM-042 |
| plc | PROJ-016, REQ-020, LSP-905, LSP-904, LSP-903, LSP-906, LSP-907, INT-815, PLC-023, DEV-004, CHG-040, CHG-041, PM-042 |

## 10. PM_SESSION 完整模板结构

PM_SESSION 文件包含以下10个章节，所有章节均为必填：

| 章节 | 标题 | 必填字段 | 说明 |
|------|------|---------|------|
| §0 | Meta | project_id, project_name, project_root, last_updated, owners | 项目元信息 |
| §1 | Positioning | one_liner, users, non_goals | 项目定位与边界 |
| §2 | Current Focus | current_focus, milestone, acceptance | 当前焦点与里程碑 |
| §3 | Status Summary | in_progress, next_up, open_questions, risks_dependencies | 状态摘要 |
| §4 | Artifacts Index | prd, req, des, test, delivery 等 | 文档产物索引 |
| §5 | Logs | change_log, iteration_log, bug_log, refactor_log, release_log, spec_change_log | 事件日志（只追加） |
| §6 | Implementation Log | date, skill, mode, goal, changed_files, impact, risks | 实现记录 |
| §7 | Verification Log | verified, not_verified, method, blocker | 验证记录 |
| §8 | Handoff Notes | current_state, next_focus, watchouts, read_first | 交接摘要 |
| §9 | Next Actions | ≥3条，带 precondition + done_when | 下一步行动 |

此外，PM_SESSION 应包含 **Spec Snapshot** 区块（位于 §0 之后或文件末尾），记录项目初始化时锁定的规范版本基线，供后续 `specmgr check` 检测版本漂移。

### 10.1 日志回写规则

- 每次事件处理完必须回写 PM_SESSION
- §5 Logs 只追加，不覆盖历史
- §6 Implementation Log 由 fullstack-engineer / plc-electrical-engineer 技能执行后回写
- §7 Verification Log 记录验证结果和阻塞项
- §8 Handoff Notes 确保下次会话可快速恢复上下文
