# V2.5.9 Spec: 交付物路径一致性 + 版本号一致性 + 稳定性修复

## Why

用户解压 V2.5.8 交付物后测试发现**三个严重问题**：

1. **路径错误（截图证实）**: 新建项目路径显示 `..\My_Workspace\01_Project自动化项目管理\P`，总库 root_path 仍为 `D:\BaiduSyncdisk\...\0100_项目` — 均未指向解压目录下的 `Projects` 文件夹
2. **版本号不一致（截图证实）**: 标题栏显示 `v2.5.6`，与打包版本号不匹配
3. **闪退风险**: `new_project_dialog.py` 中新增的 `from src.core.config import Config` 可能在 PyInstaller 冻结环境下导入失败导致崩溃

**核心诉求**: 无论本机还是其他电脑，默认总库和新建项目都必须在**解压后的 Projects 文件夹内**；打包文件版本号和运行时显示必须一致。

## What Changes

### Bug F1: 路径未生效（严重）

**现象**: 新建项目路径 ≠ `{exe_dir}\Projects\...`

**根因链路分析**:

```
_update_default_path() 实际执行路径:
  ① Config.get_resolved_project_path()
     → 可能因 PyInstaller 导入失败 → except 捕获 → base_path 仍为空 ❌
  ② lib.root_path (DB)
     → DB 中仍存旧值 "D:\BaiduSyncdisk\...\0100_项目"
     → 路径存在且可写 → 直接使用 ❌
  ③ _detect_project_base_path()
     → 向上搜索找到工作区结构 → 返回绝对路径 ❌
  ④ cwd 兜底
```

**三个层面都需要修复**:
1. **Config 导入兼容性**: 确保 PyInstaller 冻结环境下能正常导入
2. **DB root_path 清理**: 总库的 root_path 必须清空或设为相对值
3. **_detect_project_base_path() 策略调整**: 最优先返回 `{exe_dir}/Projects`

### Bug F2: 版本号不一致（中等）

**现象**: 标题栏 = v2.5.6, 打包文件 = V2.5.8

**根因**: 存在多个版本号来源未同步:
- `version.py` → 2.5.8 ✅
- `config/app_config.json` (源码) → 2.5.7 ❌ (应为 2.5.8)
- `config/app_config.json` (交付物) → 2.5.7 ❌
- 运行时标题栏读取来源需确认（可能从 app_config.json 或 version.py）

**修复**: 统一所有版本号为 2.5.9，并确认运行时读取逻辑

### Bug F3: 总库 root_path 污染（严重）

**现象**: 总库管理界面显示 `根据路径: D:\BaiduSyncdisk\...\0100_项目`

**根因**: V2.5.7 执行了 `diagnose_rootpath.py` 清理 root_path 为空字符串，但**重新打包时使用的 project_manager.db 是源码目录的副本**，该副本可能未被清理，或运行时初始化又写入了旧路径。

**修复**: 打包前必须确保交付物中的 DB 的 libraries.root_path 全部为空

## Impact

- Affected code: `new_project_dialog.py`, `config.py`, `library_service.py`, `project_service.py`, `main.py`(版本显示), `version.py`
- Affected data: `data/project_manager.db` (libraries 表 root_path 字段)
- Affected config: `app_config.json` × 3 处 (源码/交付物/打包后)

## ADDED Requirements

### REQ-F1: 项目路径强制使用相对路径

系统 SHALL 在新建项目对话框中，**始终优先**使用 `{exe所在目录}\Projects` 作为项目基础路径，无论任何配置或数据库状态。

#### Scenario F1.1: 正常解压运行
- **GIVEN** 用户将交付物解压到任意位置（如 `E:\工具\Python项目管理工具\`）
- **WHEN** 用户点击「新建项目」
- **THEN** 项目路径默认值为 `{E:\工具\Python项目管理工具}\Projects\DJ-xxx_xxx\`

#### Scenario F1.2: 无 D 盘机器
- **GIVEN** 电脑只有 C 盘，解压到 `C:\Users\xxx\Tools\`
- **WHEN** 打开新建项目对话框
- **THEN** 项目路径为 `C:\Users\xxx\Tools\Projects\DJ-xxx_xxx`，无报错无闪退

#### Scenario F1.3: 总库 root_path 一致性
- **GIVEN** 解压后首次运行
- **WHEN** 查看「总库管理」详情
- **THEN** 根据路径显示为 `{exe_dir}` 或空（不再显示 D 盘绝对路径）

### REQ-F2: 版本号三合一一致

系统 SHALL 保证以下三处版本号完全一致：
1. `src/core/version.py` 的 VERSION 常量
2. `config/app_config.json` 的 version 字段  
3. 运行时窗口标题栏显示的版本号

**三者必须相等**，偏差视为 BUG。

#### Scenario F2.1: 标题栏验证
- **GIVEN** 使用 V2.5.9 交付物解压后运行
- **WHEN** 观察窗口标题栏
- **THEN** 显示 `Python项目管理工具 v2.5.9`

### REQ-F3: PyInstaller 冻结环境导入安全

`new_project_dialog.py` 中对 `Config` 的导入 SHALL 在 PyInstaller 冻结环境和开发环境均正常工作，不会导致闪退。

#### Scenario F3.1: 冻结环境启动
- **GIVEN** 使用 PyInstaller 打包的 EXE 运行
- **WHEN** 点击「新建项目」按钮
- **THEN** 对话框正常弹出，无闪退，路径正确显示

### REQ-F4: 数据库 root_path 零污染

交付物中的 `project_manager.db` 的 `libraries` 表 `root_path` 字段 SHALL 全部为空字符串，不包含任何机器相关的绝对路径。

## MODIFIED Requirements

### REQ-M1: _update_default_path() 重构

`new_project_dialog.py:_update_default_path()` 方法 SHALL 按**严格优先级**选择路径：

```
优先级 1 (最高): Config.get_resolved_project_path() → {exe_dir}/Projects
优先级 2 (回退):  仅当优先级1异常时 → 总库 root_path (如非绝对路径则跳过)
优先级 3 (回退):  自动检测 → 必须以 exe_dir 为基准
优先级 4 (兜底):  exe_dir/Projects (硬兜底，不再用 cwd)
```

**关键变更**: 不再信任 DB 中的 root_path（可能含旧绝对路径），cwd 不再作为兜底。

### REQ-M2: _detect_project_base_path() 增强

`library_service.py:_detect_project_base_path()` SHALL 增加**策略 0**：直接返回 `{base_dir}/Projects`，作为最优先选项。

### REQ-M3: 初始化时 root_path 清理

程序启动时（或首次检测到 root_path 含盘符时），自动将 libraries 表中的 root_path 清空。

## REMOVED Requirements

无。

---

## 架构决策记录

| 决策 | 选择 | 原因 |
|------|------|------|
| Config 导入方式 | 改为延迟导入 + fallback | 避免 PyInstaller 循环导入/缺失模块导致闪退 |
| DB root_path 处理 | 启动时检测+自动清零 | 不能依赖手动清理脚本，必须程序自愈 |
| cwd 兜底 | 移除 | cwd 在不同启动方式下不可预测 |
| 版本号统一值 | 2.5.9 | 所有文件统一一个值 |
