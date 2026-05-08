# Checklist: 修复项目路径定位错误

## Task 1 验证: library_service.py root_path重构

- [x] 存在 `_detect_project_base_path()` 辅助方法（第403-440行），包含向上搜索逻辑
- [x] root_path 不再直接等于 `os.getcwd()`
- [x] root_path 包含 `01_Project自动化项目管理/Python自动化项目总库/0100_项目` 路径段
- [x] 目标目录在设置 root_path 前已被 os.makedirs 创建
- [x] fallback 场景有 WARNING 日志

## Task 2 验证: new_project_dialog.py 路径生成

- [x] `_update_default_path()` 正确获取 lib.root_path（通过 LibraryService.get_library）
- [x] 生成的路径不以 `01_主程序核心代码` 或 `src` 结尾
- [x] 路径格式为 `{root_path}\{code}_{name}`

## Task 3 验证: 功能验证

- [x] `_detect_project_base_path()` 方法存在且逻辑完整
- [x] 补全和新建两处均使用新方法（第486行、第496行）
- [x] 路径与源码目录完全分离，指向总库的 `0100_项目` 子目录
