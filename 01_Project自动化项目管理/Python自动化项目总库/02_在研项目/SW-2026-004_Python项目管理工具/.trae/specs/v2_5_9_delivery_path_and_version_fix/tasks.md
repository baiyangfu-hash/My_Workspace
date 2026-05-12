# Tasks

## Phase A: 根因修复（代码层）

- [x] Task 1: 修复 `new_project_dialog.py` 的 Config 导入和路径优先级
  - [x] 将 `from src.core.config import Config` 改为**延迟安全导入**（try/except 包裹，fallback 到手动路径构建）
  - [x] 调整优先级：Config → **跳过 DB root_path**（不可信）→ _detect_project_base_path() → exe_dir/Projects 兜底
  - [x] 移除 cwd 兜底，改为 `{sys.executable.parent}/Projects` 硬兜底

- [x] Task 2: 增强 `library_service.py:_detect_project_base_path()`
  - [x] 新增**策略 0**: 直接返回 `{base_search_dir}/Projects` 并创建目录
  - [x] 作为方法内的第一个返回选项（最高优先级）

- [x] Task 3: 启动时自动清理 DB 中含绝对路径的 root_path
  - [x] 在 `LibraryService.initialize_default_library()` 或 `main.py` 启动流程中增加检测
  - [x] 若 libraries.root_path 包含 `:` (盘符标记)，自动清空为 `""`
  - [x] 确保交付物打包前 DB 已清理

## Phase B: 版本号统一

- [x] Task 4: 统一所有版本号为 2.5.9
  - [x] `src/core/version.py`: VERSION = "2.5.9"
  - [x] `config/app_config.json` (源码): version = "2.5.9"
  - [x] `06_交付物/01_可执行文件/config/app_config.json`: version = "2.5.9"
  - [x] 确认 main.py 标题栏读取逻辑使用统一版本

## Phase C: 数据库 + 打包验证

- [x] Task 5: 清理交付物 DB 的 root_path
  - [x] 运行诊断/清理脚本确保 project_manager.db 的 libraries.root_path 全部为空
  - [x] 验证总库项目数保持不变

- [x] Task 6: PyInstaller 重新打包 V2.5.9
  - [x] 基于以上所有修改重新执行 PyInstaller
  - [x] 复制 EXE 到 06_交付物
  - [x] 创建 ZIP 归档到 06_交付物打包

## Phase D: 文档更新

- [x] Task 7: 更新打包版本记录和发布说明

# Task Dependencies
- [Task 3] depends on [Task 1] (路径策略确定后才能做启动清理)
- [Task 5] depends on [Task 3] (DB 清理在代码修复后)
- [Task 6] depends on [Task 4, Task 5] (版本统一+DB干净后才能打包)
