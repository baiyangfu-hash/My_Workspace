# Checklist: 修复新建项目对话框路径为空 Bug

## Task 1 验证: library_service.py initialize_default_library() root_path补全

- [x] `initialize_default_library()`方法在返回已存在总库前检查`root_path`是否为空
- [x] 当`root_path`为None或空字符串时，自动设置为`os.getcwd()`
- [x] 补全操作通过`session.commit()`持久化到数据库
- [x] 当`root_path`已有有效值时，不执行覆盖（幂等性保证）
- [x] 补全操作有日志输出

## Task 2 验证: new_project_dialog.py _update_default_path() 降级策略

- [x] `_update_default_path()`方法在有有效`lib.root_path`时使用总库路径
- [x] `_update_default_path()`方法在`lib.root_path`为空时降级使用`os.getcwd()`
- [x] 项目编号为空时不生成路径（保持原有行为）
- [x] 路径格式正确: `{base_path}\{code}_{name}`

## Task 3 验证: 功能验证

- [x] 新建项目对话框打开时，项目路径字段自动填充
- [x] 路径包含选中的总库root_path（或cwd降级）
- [x] 路径包含自动生成的项目编号和名称
- [x] 切换总库选项后路径正确更新
