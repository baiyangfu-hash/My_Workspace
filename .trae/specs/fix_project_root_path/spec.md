# 修复项目路径定位错误 Spec

## Why

截图显示项目路径为 `程序\01_主程序核心代码\DJ-2026-001_查vvv` — **新建项目被放到了源代码目录中**，这是完全错误的。

### 根因分析

**调用链路**:
1. [library_service.py:447/459](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/services/library_service.py#L447) — `root_path` 基于 `os.getcwd()` 计算
2. 程序从 `01_主程序核心代码` 启动 → `os.getcwd()` = 源码目录
3. 即使设置了 `{cwd}/01_Project自动化项目管理/.../0100_项目`，该路径依赖cwd，在不同启动方式下不稳定
4. 从截图看，最终降级到了 `os.getcwd()` 本身（即源码目录）

**用户的合理关切**:
- 总库是管理项目的容器，项目应该放在总库的专用项目目录下
- 不应与程序源码混在一起
- 需要一个稳定、独立于启动位置的项目存放路径

## What Changes

### 修改1: `library_service.py` — root_path使用稳定的绝对路径检测
- 不再简单使用 `os.getcwd()`
- 改为向上搜索工作区根目录（找到 `01_Project自动化项目管理/Python自动化项目总库/`）
- 基于此确定 `0100_项目/` 作为 root_path
- 若找不到标准结构，fallback 到 `os.getcwd()` 但给出警告日志

### 修改2: `new_project_dialog.py` — 路径显示优化
- 当 root_path 有效时，确保路径正确拼接
- 路径格式确认: `{总库root_path}\{code}_{name}`

## Impact

- Affected specs: fix_empty_project_path (延续修复), regression_fix_cascade_delete (关联)
- Affected code:
  - `src/services/library_service.py` — `initialize_default_library()` 的root_path计算
  - `src/ui/dialogs/new_project_dialog.py` — `_update_default_path()` 验证

## ADDED Requirements

### Requirement: 总库root_path稳定定位

系统 SHALL 使用稳定的工作区相对路径来确定总库的root_path，而非依赖不稳定的 `os.getcwd()`。

#### Scenario: 标准工作区结构
- **WHEN** 系统初始化默认总库
- **AND** 当前工作目录或其父目录包含 `01_Project自动化项目管理/Python自动化项目总库/` 结构
- **THEN** root_path 设置为 `{工作区根}/01_Project自动化项目管理/Python自动化项目总库/0100_项目`
- **AND** 自动创建该目录（如不存在）

#### Scenario: 非标准启动位置
- **WHEN** 系统从非标准目录启动（无法找到总库目录结构）
- **THEN** fallback 到 `os.cwd()/projects`
- **AND** 记录 WARNING 日志提示用户路径可能不理想

### Requirement: 新建项目路径正确性

新建项目对话框 SHALL 显示正确的、位于总库项目目录下的路径。

#### Scenario: 路径生成
- **WHEN** 用户打开新建项目对话框
- **AND** 默认总库有有效的 root_path
- **THEN** "项目路径"字段显示 `{root_path}\{code}_{name}`
- **AND** 该路径不在源代码目录内
