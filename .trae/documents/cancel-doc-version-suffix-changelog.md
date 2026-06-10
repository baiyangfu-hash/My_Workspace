# 最终变更清单：取消文档文件名版本后缀

## 变更概述

将文档命名格式从 `[文档名称]_[前缀码]-V[版本号].md` 改为 `[文档名称]_[前缀码].md`，移除文件名中的版本后缀。版本信息改为通过文档内部声明（frontmatter version字段 + 文档基础信息表 + 版本变更记录表）和 `spec_registry.json` 管理。

## 测试结果

| 项目 | 结果 | 说明 |
|------|------|------|
| SW-2026-004 | 基础导入和spec_sync测试通过 | 无pyproject.toml，仅运行核心测试 |
| SW-2026-005 | 61 passed, 0 failed | 全量通过 |
| SW-2026-006 | 78 passed, 3 failed | 3个失败为预先存在的bug（PMSessionRefChecker测试数据不含路径分隔符），非本次修改引入 |
| SW-2026-007 | 无测试目录 | 无需测试 |

## 一、规范文件修改

### 1.1 核心规范

| 文件路径 | 修改类型 | 修改内容 |
|---------|---------|---------|
| `00_Obsidian_Base全局规范文件仓库/01_项目管理域/04_变更管理/004_通用项目文档版本管理与变更核心规范_DEV.md` | 内容修改 | 5.2条版本标记改为仅内部声明；5.3条格式改为`_前缀码.md`；7.3条基线命名移除版本号；示例全部更新 |

### 1.2 关联规范

| 文件路径 | 修改类型 | 修改内容 |
|---------|---------|---------|
| `00_Obsidian_Base全局规范文件仓库/01_项目管理域/04_变更管理/044_变更管理文档版本控制规范_PM.md` | 内容修改 | 8.1节文件名格式移除版本号；8.2节版本号描述改为frontmatter维护 |
| `00_Obsidian_Base全局规范文件仓库/01_项目管理域/02_规划阶段/016_通用项目结构模板_PROJ.md` | 内容修改 | 8.1节文档命名规范表5种格式和示例移除版本后缀 |
| `00_Obsidian_Base全局规范文件仓库/01_项目管理域/05_收尾验收/规范发布检查清单_CHK.md` | 内容修改 | A4-01通过标准改为`_前缀码.md`；7.4节正则和标签更新 |
| `00_Obsidian_Base全局规范文件仓库/01_项目管理域/04_变更管理/规范版本管理操作SOP_OPS.md` | 内容修改 | 步骤2.4改为更新frontmatter；步骤3.4改为frontmatter版本确认；5.3.1示例改为无需重命名 |
| `00_Obsidian_Base全局规范文件仓库/01_项目管理域/00_元规则与治理/004_PM_WORKFLOW总控Skill使用说明_PM.md` | 内容修改 | SHC-002改为检测frontmatter版本与注册表版本；自动修复改为更新frontmatter |

## 二、Python工具代码修改

### 2.1 SW-2026-004 Python项目管理工具

| 文件路径 | 修改类型 | 修改内容 |
|---------|---------|---------|
| `SW-2026-004/.../src/services/spec_service.py` | 内容修改 | BUILTIN_SPECS移除版本后缀；命名规范描述更新 |
| `SW-2026-004/.../src/core/constants.py` | 内容修改 | 项目模板路径移除版本后缀 |
| `SW-2026-004/.../src/services/check_service.py` | 内容修改 | 正则表达式移除`-V[\d.]+`要求；描述文本更新 |
| `SW-2026-004/.../src/core/spec_manager.py` | 内容修改 | 新增`_extract_version_from_content()`方法从frontmatter提取版本号；`_find_latest_spec_file()`优先使用内容提取 |
| `SW-2026-004/.../src/services/change_service.py` | 内容修改 | 模板名移除版本后缀；规范引用链接更新 |
| `SW-2026-004/.../scripts/build_delivery.py` | 内容修改 | 交付清单文件名移除版本后缀 |

### 2.2 SW-2026-005 PLC项目管理工具

| 文件路径 | 修改类型 | 修改内容 |
|---------|---------|---------|
| `SW-2026-005/.../src/parsers/proj_parser.py` | 内容修改 | 注释更新为新文件名格式 |
| `SW-2026-005/.../src/utils/path_resolver.py` | 内容修改 | `_PROJ_FILE_PATTERNS`正则移除版本号匹配 |

### 2.3 SW-2026-006 规范管理工具

| 文件路径 | 修改类型 | 修改内容 |
|---------|---------|---------|
| `SW-2026-006/.../specmgr/core/scanner.py` | 内容修改 | `_PREFIX_VER_SUFFIX_RE`重命名为`_PREFIX_SUFFIX_RE`，正则改为仅匹配前缀码 |
| `SW-2026-006/.../specmgr/services/fix_svc.py` | 内容修改 | `_fix_shc_002()`从重命名文件改为更新frontmatter版本字段；修复f-string语法错误 |
| `SW-2026-006/.../specmgr/core/config.py` | 内容修改 | 索引输出路径移除版本后缀 |
| `SW-2026-006/.../specmgr/services/index_svc.py` | 内容修改 | 索引标题从注册表动态读取版本号 |
| `SW-2026-006/.../specmgr/core/checker_base.py` | 内容修改 | `VersionMismatchChecker`优先从frontmatter提取版本号比较 |

### 2.4 测试文件修改

| 文件路径 | 修改类型 | 修改内容 |
|---------|---------|---------|
| `SW-2026-005/.../tests/test_proj_parser.py` | 内容修改 | 测试数据文件名移除版本后缀 |
| `SW-2026-005/.../tests/conftest.py` | 内容修改 | 测试数据文件名移除版本后缀 |
| `SW-2026-006/.../tests/conftest.py` | 内容修改 | canonical_path测试数据移除版本后缀 |
| `SW-2026-006/.../tests/test_services.py` | 内容修改 | 测试数据文件名移除版本后缀 |
| `SW-2026-006/.../tests/test_checker_base.py` | 内容修改 | 测试数据文件名移除版本后缀 |
| `SW-2026-006/.../tests/test_scanner.py` | 内容修改 | 测试数据文件名移除版本后缀 |

## 三、文档文件重命名

### 3.1 规范仓库文件（00_Obsidian_Base全局规范文件仓库/）

约39个.md文件从 `_前缀码-V版本号.md` 重命名为 `_前缀码.md`，包括：
- 01_项目管理域/ 下所有规范文档
- 02_需求域/ 下所有规范文档
- 03_执行过程/ 下所有规范文档
- _archive/ 下部分文档

### 3.2 Python项目文件（01_Project自动化项目管理/）

约80个.md文件重命名，包括：
- SW-2026-004/ 下项目文档、发布说明、交付物
- SW-2026-005/ 下项目文档、PRD、架构文档
- SW-2026-006/ 下需求与设计文档
- SW-2026-001/ 下项目文档
- 00_通用规范/ 下规范文档

### 3.3 PLC项目文件（0100_PLC自动化/）

约31个.md文件重命名，包括：
- DJ-2026-005/ 下项目管理文档
- 00_通用规范/ 下PLC编程规范文档
- 01_SharedLibraries/ 下FB的PRD文档

## 四、配置数据更新

| 文件路径 | 修改类型 | 修改内容 |
|---------|---------|---------|
| `00_Obsidian_Base全局规范文件仓库/spec_registry.json` | 内容修改 | 58条canonical_path移除版本后缀；DEV-801 drift_warning更新 |

## 五、跨文档引用更新

### 5.1 Python项目文档引用更新（约46个文件）

| 类别 | 文件数 | 说明 |
|------|--------|------|
| PM_SESSION文件 | 4 | SW-2026-001/004/005/006的PM_SESSION路径引用 |
| README文件 | 5 | 项目根README、基础信息README、规划过程README、通用规范README |
| 项目文档 | 8 | 立项表、技术设计文档、PRD、发布说明、对比报告等 |
| frontmatter canonical_path | 52 | 各.md文件的YAML frontmatter中canonical_path字段 |

### 5.2 PLC项目文档引用更新（约11个文件）

| 类别 | 文件数 | 说明 |
|------|--------|------|
| PM_SESSION文件 | 1 | DJ-2026-005的PM_SESSION路径引用 |
| README文件 | 1 | PLC通用规范README |
| 项目文档 | 3 | 立项表、变更单、程序文档 |
| SysLib FB文档 | 6 | FB_1011/FB_1013/FB_1014/FB_1020的PRD文档中规范路径引用 |

## 六、修复的Bug

| 文件路径 | Bug描述 | 修复方式 |
|---------|---------|---------|
| `SW-2026-006/.../specmgr/services/fix_svc.py` 第107行 | f-string表达式中包含反斜杠，Python 3.11不支持 | 将`.lstrip('\n')`提取到变量`remaining`中 |

## 统计

| 类别 | 数量 |
|------|------|
| 规范文件修改 | 6 |
| Python源代码修改 | 13 |
| 测试文件修改 | 6 |
| 文档文件重命名 | ~150 |
| spec_registry.json更新 | 58条 |
| frontmatter canonical_path更新 | 52 |
| 跨文档引用更新 | ~57 |
| Bug修复 | 1 |
