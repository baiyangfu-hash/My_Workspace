---
version: V1.1.0
domain: 01_项目管理域/00_元规则与治理
type: PM_WORKFLOW
status: active
---

# PM_WORKFLOW 总控Skill 使用说明（PM_SESSION 驱动）

## 1. 目标
- 把“需求澄清 → PRD/REQ/DES → 任务拆解 → 变更/迭代/缺陷/交付”固化为可重复流程
- 通过项目根目录的会话文件作为单一真源，保证跨会话连续：`PM_SESSION_<项目编号>.md`
- 以本地文档为任务系统主载体，必要时可再同步到 GitHub

## 2. 核心约定
### 2.1 会话文件（强制）
- 每个项目根目录必须存在：`PM_SESSION_<项目编号>.md`
- 项目编号遵循 RULE-001：`[前缀]-YYYY-NNN`（示例：`SW-2026-005`、`DJ-2026-000`）
- 会话文件名采用 A 方案：`PM_SESSION_<项目编号>.md`

### 2.2 单一真源（Single Source of Truth）
- 任何需求/范围/里程碑/风险/未决问题的“当前结论”必须回写到 PM_SESSION
- PRD/REQ/DES/CHG/TEST/交付等产物路径必须登记在 PM_SESSION 的 `Artifacts Index`

## 3. 总控Skill 做什么
### 3.1 初始化（已有项目/新项目通用）
- 若项目根目录缺少 `PM_SESSION_<项目编号>.md`：自动生成初始化模板
- 自动挂接已有文档（PRD/REQ/DES/变更/测试/交付等）到 `Artifacts Index`
- 生成“当前状态摘要”：当前焦点、进行中事项、下一步、未决问题、风险依赖

### 3.2 例行更新（每次活动结束必须做）
把所有项目活动统一为 5 类事件（每次只处理一种）：
- Event A：需求新增/需求变更（Scope Change）
- Event B：迭代推进（Iteration）
- Event C：重构/技术债（Refactor）
- Event D：缺陷审查/修复（Bug）
- Event E：交付/发布（Delivery）

每个事件结束后，总控Skill会：
- 生成/更新对应文档产物（PRD/REQ/DES/CHG/TEST/交付）
- 生成/更新任务拆解（Epic/Feature/Story/Enabler/Test）
- 回写 PM_SESSION 的当前状态与对应日志（change_log / iteration_log / bug_log / refactor_log / release_log）

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

## 5. 与本仓库模板的映射
### 5.1 需求与设计
- PRD：使用 [PRD-001 产品需求文档模板](../01_启动阶段/001_产品需求文档模板_PRD-V1.0.0.md)
- REQ：使用 [REQ-020 需求分析文档模板](../02_规划阶段/020_通用需求分析文档模板_REQ-V1.1.0.md) 或 [REQ-028 迭代SRS模板](../02_规划阶段/028_迭代需求规格说明书模板_REQ-V1.0.0.md)
- DES：使用 [DES-021 详细设计说明书模板](../02_规划阶段/021_通用详细设计说明书模板_DES-V1.0.0.md)
- TECH：使用 [TECH-014 技术方案模板](../02_规划阶段/014_技术方案文档模板_TECH-V1.0.0.md)

### 5.2 计划、里程碑与迭代
- 迭代计划：使用 [PM-027 迭代项目计划模板](../02_规划阶段/027_迭代项目计划模板_PM-V1.0.0.md)
- 里程碑清单：使用 [PM-030 迭代里程碑清单模板](../02_规划阶段/030_迭代里程碑清单模板_PM-V1.0.0.md)
- 迭代流程SOP：使用 [PM-033 功能模块迭代流程标准](../02_规划阶段/033_功能模块迭代流程标准_PM-V1.0.0.md)

### 5.3 变更、缺陷、测试与交付
- 变更核心规范：使用 [004 文档版本管理与变更核心规范](../04_变更管理/004_通用项目文档版本管理与变更核心规范_DEV-V1.1.1.md)
- 变更单/台账/流程：使用 [040 变更单模板](../04_变更管理/040_通用变更单模板_CHG-V2.0.0.md)、[041 版本变更台账模板](../04_变更管理/041_通用版本变更台帐模板_CHG-V2.1.0.md)、[042 变更管理流程规范](../04_变更管理/042_通用变更管理流程规范_PM-V2.1.0.md)
- 缺陷追踪：使用 [019 缺陷跟踪表模板](../03_执行管控/019_缺陷跟踪表模板_BUG-V1.0.0.md)
- 测试报告：使用 [018 测试报告模板](../03_执行管控/018_测试报告模板_TEST-V1.0.0.md)
- 交付规范：使用 [030 通用项目交付规范](../03_执行管控/030_通用项目交付规范_DEV-V1.2.0.md)

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

### 8.1 基本用法

```bash
# 运行规范健康检查（检测版本漂移、命名不合规、链接失效等8类问题）
specmgr check -w <工作空间根目录>

# 仅检查特定检查项
specmgr check -w <工作空间根目录> -c SHC-002 -c SHC-007

# JSON格式输出（适合脚本解析）
specmgr check -w <工作空间根目录> --format json

# 只显示错误级别
specmgr check -w <工作空间根目录> --severity error
```

### 8.2 自动修复

```bash
# 预览可自动修复的问题（不实际修改文件）
specmgr check -w <工作空间根目录> --auto-fix --dry-run

# 执行自动修复
specmgr check -w <工作空间根目录> --auto-fix
```

### 8.3 可自动修复的问题类型

| 检查ID | 问题类型 | 自动修复行为 |
|--------|---------|-------------|
| SHC-002 | 版本漂移（文件名版本 ≠ 注册表版本） | 重命名文件使其与注册表版本一致，同步更新frontmatter和canonical_path |
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
specmgr check -w <workspace>
# 发现问题后预览修复
specmgr check -w <workspace> --auto-fix --dry-run
# 确认后执行修复
specmgr check -w <workspace> --auto-fix
```

**场景2：新增规范文件后补全元数据**
```bash
# 新建规范文件后，检查frontmatter是否完整
specmgr check -w <workspace> -c SHC-007
# 自动补全缺失的frontmatter字段
specmgr check -w <workspace> --auto-fix -c SHC-007
```

**场景3：定期规范体系巡检**
```bash
# 每周运行一次全量检查，只看错误和警告
specmgr check -w <workspace> --severity warning
# 发现问题后针对性修复
specmgr check -w <workspace> --auto-fix -c SHC-002
```

### 8.6 其他SpecMgr命令

```bash
# 自动生成规范索引文件（按域生成README）
specmgr index -w <工作空间根目录>
specmgr index -w <工作空间根目录> --domain plc

# 批量添加/更新规范frontmatter
specmgr frontmatter -w <工作空间根目录> --dry-run
specmgr frontmatter -w <工作空间根目录>

# 生成规范元数据汇总报告
specmgr report -w <工作空间根目录>
specmgr report -w <工作空间根目录> --format json
```

