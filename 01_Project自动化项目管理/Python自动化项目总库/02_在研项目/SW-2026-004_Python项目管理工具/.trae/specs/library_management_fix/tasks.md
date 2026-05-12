# 总库管理模块完善 - 任务计划

## [x] Task 1: 默认总库初始化机制
- **Priority**: P0
- **Depends On**: None
- **Description**:
  1. 在 `library_service.py` 中新增 `initialize_default_library()` 静态方法：
     - 检查数据库中是否存在 library_id="LIB-DEFAULT-001" 的总库
     - 如果不存在 → 创建默认总库 + 为每个 BusinessLine 枚举值创建 Category
     - 如果已存在 → 跳过（幂等）
  2. 在 `main_window.py` 的启动流程中调用 `LibraryService.initialize_default_library()`
  3. 验证：启动系统后，总库管理界面能看到默认总库及其分类
- **Files**: src/services/library_service.py, src/ui/main_window.py (或 main.py)

## [x] Task 2: 项目创建自动归档 + 对话框增强
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  1. 改造 `project_service.py` 的 `create_project()` 方法签名，增加 `library_id` 参数（默认值="LIB-DEFAULT-001"）
  2. 在创建项目成功后，创建 LibraryProject 关联记录
  3. 在 `new_project_dialog.py` 中增加 QComboBox "所属总库" 下拉框
     - 从 LibraryService.list_libraries() 加载可用总库列表
     - 默认选中 LIB-DEFAULT-001
     - 允许选择"(不关联总库)"选项
  4. 将选中的 library_id 传递给 create_project()
  5. 同步改造 `change_template()` 方法中的文档生成逻辑（如果也涉及重新关联）
- **Files**: src/services/project_service.py, src/ui/dialogs/new_project_dialog.py, src/dao/library_dao.py

## [x] Task 3: 总库管理界面激活
- **Priority**: P1
- **Depends On**: Task 1, Task 2
- **Description**:
  1. **总库详情标签页**: 显示选中总库的名称、描述、根路径、状态、创建时间、项目数量
  2. **项目管理标签页**:
     - QTableWidget 显示该总库下的所有项目（code/name/business线/status/template/date）
     - 双击行打开项目详情
     - "添加项目"按钮：弹出对话框选择未关联的项目加入本总库
     - "移出总库"按钮：移除选中项目的 LibraryProject 关联（不删除项目本身）
  3. **分类管理标签页**:
     - 树形视图(QTreeWidget)显示分类层级
     - 点击分类过滤项目列表
  4. **统计信息标签页**:
     - QLabel 显示总数、各状态计数、各业务线计数
     - 使用 QChart 或简单文本统计展示
  5. 确保工具栏的"新建总库"/"刷新"/"更新总库"/"删除总库"按钮有实际功能
- **Files**: src/ui/widgets/library_manager.py (或 library_dashboard.py 等，需确认实际文件名)

## [x] Task 4: 回归测试验证
- **Priority**: P1
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  1. 运行 regression_test.py 确保 18/18 通过
  2. 运行 test_template_fix.py 确保 7/7 通过
  3. 新建测试：验证默认总库自动创建
  4. 新建测试：验证创建项目后出现在总库项目列表中
  5. 新建测试：验证总库统计数据正确
  6. GUI手动验证：打开总库管理 → 4个标签页均有正确数据显示
- **Files**: test files (新建或扩展)

## Task Dependencies
- [Task 1] → [Task 2] (需要先有默认总库才能归档)
- [Task 1] → [Task 3] (需要有总库数据才能显示)
- [Task 2] || [Task 3] 可部分并行（对话框改造 vs 界面激活可同时进行）
- [Task 4] depends on ALL
