# Tasks: 修复项目路径定位错误

## 任务列表

- [x] **Task 1: 重构 library_service.py root_path计算逻辑**
  - [x] 1.1 创建 `_detect_project_base_path()` 辅助方法：从cwd向上查找包含 `01_Project自动化项目管理` 的目录
  - [x] 1.2 修改 `initialize_default_library()` 中两处 root_path 赋值：改用 `_detect_project_base_path()`
  - [x] 1.3 添加 fallback 逻辑：若找不到工作区根，用 `{cwd}/projects` 并记录 WARNING
  - [x] 1.4 确保 `os.makedirs(project_base, exist_ok=True)` 在设置 root_path 之前执行

- [x] **Task 2: 验证 new_project_dialog.py 路径生成**
  - [x] 2.1 确认 `_update_default_path()` 中 lib.root_path 能正确获取到新计算的路径
  - [x] 2.2 确认降级策略不会覆盖有效 root_path
  - [x] 2.3 确认最终路径格式为 `{总库项目目录}\{code}_{name}` 且不在源码目录内

- [x] **Task 3: 功能验证**
  - [x] 3.1 `_detect_project_base_path()` 方法存在且逻辑完整（第403-440行）
  - [x] 3.2 两处 root_path 赋值均已改为调用 `_detect_project_base_path()`（第486行、第496行）
  - [x] 3.3 路径不再依赖 os.getcwd()，而是向上搜索工作区结构

## Task Dependencies

- [Task 1] ✅ 最先执行（核心修改）
- [Task 2] ✅ 依赖 Task 1 完成后验证
- [Task 3] ✅ 最终功能验证
