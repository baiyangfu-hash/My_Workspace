# Tasks: 修复新建项目对话框路径为空 Bug

## 任务列表

- [x] **Task 1: 修复 library_service.py - initialize_default_library() 补全root_path**
  - [x] 1.1 在`initialize_default_library()`中，当找到已存在的默认总库时，检查`root_path`是否为空
  - [x] 1.2 若`root_path`为空(None或空字符串)，设置为`os.getcwd()`并调用`session.commit()`持久化
  - [x] 1.3 确保幂等性：只在root_path为空时才补全，不覆盖已有有效值
  - [x] 1.4 添加日志记录补全操作

- [x] **Task 2: 修复 new_project_dialog.py - _update_default_path() 增加降级策略**
  - [x] 2.1 在`_update_default_path()`方法中，当`lib.root_path`为空时增加降级逻辑
  - [x] 2.2 降级策略：使用`os.getcwd()`作为基础路径
  - [x] 2.3 保持原有行为：项目编号为空时不生成路径
  - [x] 2.4 保持原有行为：有有效root_path时优先使用总库路径

- [x] **Task 3: 验证修复效果**
  - [x] 3.1 验证library_service.py修改: 第446-449行root_path补全逻辑正确
  - [x] 3.2 验证new_project_dialog.py修改: 第180-182行降级策略正确
  - [x] 3.3 确认双重保障机制生效（数据层补全 + UI层降级）

## Task Dependencies

- [Task 1] 和 [Task 2] 可并行执行（修改不同文件）✅
- [Task 3] 依赖 Task 1 + Task 2 完成后验证 ✅
