# 计划：取消文档文件名版本后缀要求

## 摘要

取消文档文件名中的版本后缀要求（如 `_PROJ-V1.0.0` → `_PROJ`），因为文档内部已有版本声明和记录，文件名缀版本是冗余的。涉及规范文档修改、Python工具代码修改、现有文件重命名、spec_registry.json更新四个层面。

## 已确认决策

1. **SHC-002漂移检测** → 改为检测frontmatter版本与注册表版本的一致性（不再检测文件名版本）
2. **现有文件** → 一次性全部重命名
3. **前缀码** → 保留（如 `_DEV`、`_PM`、`_CHK`），仅移除版本号部分（如 `-V1.0.0`）

## 新的文档命名格式

**旧格式**：`[序号]-[文档名称]_[前缀码]-V[版本号].md`
- 示例：`0-项目立项表_PROJ-V1.0.0.md`、`004_通用项目文档版本管理与变更核心规范_DEV-V1.1.1.md`

**新格式**：`[序号]-[文档名称]_[前缀码].md`
- 示例：`0-项目立项表_PROJ.md`、`004_通用项目文档版本管理与变更核心规范_DEV.md`

**例外**（保留版本后缀）：
- Mermaid图表文件（.mmd/.png/.svg）- 导出产物需版本区分
- ZIP交付包 - 交付物需版本区分

## 现状分析

### 1. 规范层面：DEV-004 明确要求文件名带版本后缀

**核心规范** [004_通用项目文档版本管理与变更核心规范_DEV-V1.1.1.md](file:///c:/Users/fubai/Desktop/My_Workspace/00_Obsidian_Base全局规范文件仓库/01_项目管理域/04_变更管理/004_通用项目文档版本管理与变更核心规范_DEV-V1.1.1.md)：
- 第5.2条第3款："版本标记：在文档的文件名和文档内部都应包含版本号"
- 第5.3条：格式为 `[文档名称]_[前缀码]-[版本号].md`
- 示例：`需求分析文档_REQ-DJ-2026-005-V1.0.0.md`

**关联规范**（均引用DEV-004的文件名版本要求）：
- [044_变更管理文档版本控制规范_PM-V1.0.0.md](file:///c:/Users/fubai/Desktop/My_Workspace/00_Obsidian_Base全局规范文件仓库/01_项目管理域/04_变更管理/044_变更管理文档版本控制规范_PM-V1.0.0.md) - 8.1节
- [016_通用项目结构模板_PROJ-V1.0.0.md](file:///c:/Users/fubai/Desktop/My_Workspace/00_Obsidian_Base全局规范文件仓库/01_项目管理域/02_规划阶段/016_通用项目结构模板_PROJ-V1.0.0.md) - 8.1节
- [规范发布检查清单_CHK-V1.0.0.md](file:///c:/Users/fubai/Desktop/My_Workspace/00_Obsidian_Base全局规范文件仓库/01_项目管理域/05_收尾验收/规范发布检查清单_CHK-V1.0.0.md) - A4-01检查项
- [规范版本管理操作SOP_OPS-V1.0.0.md](file:///c:/Users/fubai/Desktop/My_Workspace/00_Obsidian_Base全局规范文件仓库/01_项目管理域/04_变更管理/规范版本管理操作SOP_OPS-V1.0.0.md) - 步骤2.4、3.4
- [004_PM_WORKFLOW总控Skill使用说明_PM-V1.0.0.md](file:///c:/Users/fubai/Desktop/My_Workspace/00_Obsidian_Base全局规范文件仓库/01_项目管理域/00_元规则与治理/004_PM_WORKFLOW总控Skill使用说明_PM-V1.0.0.md) - SHC-002漂移检测

### 2. 代码层面：多处硬编码了版本后缀

| 文件 | 问题 |
|------|------|
| [spec_service.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/services/spec_service.py) 第31-33行 | BUILTIN_SPECS中硬编码 `_PROJ-V1.0.0.md`、`_REQ-V1.0.0.md` 等 |
| [constants.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/core/constants.py) 第587-593行 | 项目模板路径硬编码 `_PROJ-V1.0.0.md`、`_REQ-V1.0.0.md` |
| [check_service.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/services/check_service.py) 第197行 | 正则 `_[A-Z]+-V[\d.]+` 强制要求版本后缀 |
| [spec_manager.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/core/spec_manager.py) 第61-68行、167行、332行 | `_extract_version_from_filename()` 从文件名提取版本号 |
| [change_service.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/services/change_service.py) 第391、599、748行 | 引用带版本后缀的模板名 |
| [build_delivery.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/scripts/build_delivery.py) 第222行 | 生成 `01_交付清单_DEL-{version}.md` |
| [scanner.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-006_规范管理工具/02_源代码/specmgr/core/scanner.py) 第25-28行 | `_PREFIX_VER_SUFFIX_RE` 正则匹配 `_PREFIX-V` 模式 |
| [fix_svc.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-006_规范管理工具/02_源代码/specmgr/services/fix_svc.py) 第50-118行 | `_fix_shc_002()` 自动重命名文件更新版本后缀 |
| [config.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-006_规范管理工具/02_源代码/specmgr/core/config.py) 第31行 | 索引输出路径硬编码 `_V2.0.0.md` |
| [index_svc.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-006_规范管理工具/02_源代码/specmgr/services/index_svc.py) 第93-96行 | 索引标题硬编码版本号 |
| [proj_parser.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-005_PLC项目管理工具/03_主程序/01_主程序核心代码/src/parsers/proj_parser.py) 第65-83行 | 从文件名提取项目编号，注释引用带版本后缀格式 |
| [path_resolver.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-005_PLC项目管理工具/03_主程序/01_主程序核心代码/src/utils/path_resolver.py) 第24-28行 | `_PROJ_FILE_PATTERNS` 匹配 `_PROJ-` 后缀模式 |

### 3. pm-mgr 初始化：模板文件名不带版本后缀（已正确）

[bootstrap.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-007_pm工作流工具链/pm_mgr/bootstrap.py) 第54-67行的模板映射：
- `"00_立项表.md"` -> `"00_项目基础信息/立项表.md"`（无版本后缀）
- `"01_PRD.md"` -> `"01_项目文档/01_需求/PRD.md"`（无版本后缀）

**pm-mgr init 生成的文件名本身不带版本后缀，这是正确的**。但问题在于 SW-2026-004 的 constants.py 和 spec_service.py 中硬编码了带版本后缀的路径，与 pm-mgr init 的行为不一致。

### 4. pm-workflow 技能

[SKILL.md](file:///c:/Users/fubai/Desktop/My_Workspace/.trae/skills/pm-workflow/SKILL.md) 本身不定义文档命名格式，它引用 DEV-004 规范。修改 DEV-004 后，pm-workflow 会自动遵循新规范。

### 5. spec_registry.json

[spec_registry.json](file:///c:/Users/fubai/Desktop/My_Workspace/00_Obsidian_Base全局规范文件仓库/spec_registry.json) 中 `canonical_path` 字段目前包含版本后缀（如 `004_通用项目文档版本管理与变更核心规范_DEV-V1.1.1.md`），取消版本后缀后需要同步更新。

## 实施步骤

### 步骤1：修改核心规范 DEV-004

**文件**：`00_Obsidian_Base全局规范文件仓库/01_项目管理域/04_变更管理/004_通用项目文档版本管理与变更核心规范_DEV-V1.1.1.md`

修改内容：
- 5.2条第3款：从"在文档的文件名和文档内部都应包含版本号"改为"版本号仅在文档内部声明（frontmatter version字段 + 文档基础信息表 + 版本变更记录表），文件名不包含版本号"
- 5.3条命名格式：从 `[文档名称]_[前缀码]-[版本号].md` 改为 `[文档名称]_[前缀码].md`
- 更新所有示例，移除版本后缀
- 新增说明：版本信息的权威来源是 frontmatter 和 spec_registry.json

### 步骤2：修改关联规范

1. **PM-044** (`044_变更管理文档版本控制规范_PM-V1.0.0.md`) - 修改8.1节文件名格式
2. **PROJ-016** (`016_通用项目结构模板_PROJ-V1.0.0.md`) - 修改8.1节文档命名规范表
3. **CHK检查清单** (`规范发布检查清单_CHK-V1.0.0.md`) - 修改A4-01检查项正则和通过标准
4. **OPS-SOP** (`规范版本管理操作SOP_OPS-V1.0.0.md`) - 移除步骤2.4、3.4中关于文件名版本同步的描述
5. **PM-004** (`004_PM_WORKFLOW总控Skill使用说明_PM-V1.0.0.md`) - 修改SHC-002描述为"检测frontmatter版本与注册表版本一致性"

### 步骤3：修改 SW-2026-004 Python项目管理工具代码

1. **spec_service.py** - BUILTIN_SPECS中移除版本后缀：`_PROJ-V1.0.0.md` → `_PROJ.md`，`_REQ-V1.0.0.md` → `_REQ.md` 等
2. **constants.py** - 项目模板路径移除版本后缀：`0-项目立项表_PROJ-V1.0.0.md` → `0-项目立项表_PROJ.md`
3. **check_service.py** - 修改正则：`_[A-Z]+-V[\d.]+\.` → `_[A-Z]+\.`，更新描述
4. **spec_manager.py** - 修改 `_extract_version_from_filename()` 不再从文件名提取版本号，改为从frontmatter提取；修改 `re.sub(r'[_-][Vv]\d+\.\d+\.\d+.*$', '', filename)` 逻辑
5. **change_service.py** - 移除模板名中的版本后缀引用
6. **build_delivery.py** - 交付清单文件名移除版本后缀

### 步骤4：修改 SW-2026-005 PLC项目管理工具代码

1. **proj_parser.py** - 更新注释，适配新文件名格式
2. **path_resolver.py** - 更新 `_PROJ_FILE_PATTERNS` 匹配模式，移除版本号匹配

### 步骤5：修改 SW-2026-006 规范管理工具代码

1. **scanner.py** - 修改 `_PREFIX_VER_SUFFIX_RE` 正则，仅匹配前缀码不再匹配版本号；`extract_version()` 已从文件内容提取，无需改动
2. **fix_svc.py** - 修改 `_fix_shc_002()` 逻辑：不再通过重命名文件修复版本漂移，改为更新frontmatter中的version字段
3. **config.py** - 索引输出路径移除版本后缀：`_V2.0.0.md` → `.md`
4. **index_svc.py** - 索引标题从注册表读取版本号，不再硬编码
5. **checker_base.py** - 修改 `VersionMismatchChecker`：比较frontmatter版本与注册表版本，而非文件名版本

### 步骤6：重命名现有文档文件

扫描工作空间中所有带版本后缀的 .md 文件，批量重命名：
- `004_通用项目文档版本管理与变更核心规范_DEV-V1.1.1.md` → `004_通用项目文档版本管理与变更核心规范_DEV.md`
- 以此类推所有文件

使用 `git mv` 操作以保留Git历史。

### 步骤7：更新 spec_registry.json

更新所有 `canonical_path` 字段，移除文件名中的版本后缀部分。

### 步骤8：更新跨文档引用

扫描所有文档中引用带版本后缀文件名的链接，同步更新为新文件名。

### 步骤9：验证

1. 运行 `specmgr -w "<工作空间根>" check` 确认无命名错误
2. 运行 `pm-mgr -w "<工作空间根>" check <项目根>` 确认项目健康
3. 确认所有现有文档文件名已正确重命名
4. 确认 spec_registry.json 中 canonical_path 已全部更新
5. 确认 check_service.py 的正则能正确匹配新格式文件名

## 风险与注意事项

1. **文件重命名影响大** - 现有文档数量多，重命名可能影响其他引用这些文档的链接
2. **Git历史追踪** - 重命名文件会导致Git历史中断，需用 `git mv` 操作
3. **跨文档引用** - 其他文档中可能有指向带版本后缀文件名的链接，需要同步更新
4. **代码回归** - 修改正则和版本提取逻辑后，需确保工具链功能正常
