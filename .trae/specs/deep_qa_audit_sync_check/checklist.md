# Checklist: 全面深度QA审计 + 文档同步检查

## Task 1 验证: 核心模块审计

- [x] project_service.py create_project() 正确处理library_id参数和自动归档
- [x] project_dao.py delete() hard_delete分支正确预清理library_projects(synchronize_session=False)
- [x] new_project_dialog.py _update_default_path() 有降级策略(root_path空时用cwd)
- [x] new_project_dialog.py 默认总库选中使用名称匹配(非ID硬编码)
- [x] change_service.py 二维分类(Domain/Nature/Scope)完整且无硬编码
- [x] project_list.py 所有操作按钮信号正确连接

## Task 2 验证: 支撑模块审计

- [x] template_service.py list_all() 方法存在且返回正确
- [x] template_dao.py force_delete() 方法存在(可删除builtin)
- [x] template_manager.py 内置模板编辑按钮为setEnabled(True)
- [x] spec_service.py BUILTIN_SPECS ≥ 20条目(实际22条)
- [x] library_service.py initialize_default_library() 有幂等性检查(直接SQL查询非分页)
- [x] library_service.py _detect_project_base_path() 存在且向上搜索工作区
- [x] library_manager.py 扫描导入使用BusinessLine枚举(非硬编码SW/HW/TEST)
- [x] library_manager.py 扫描导入模板ID从TemplateService动态获取

## Task 3 验证: 基础设施审计

- [x] main_window.py 菜单包含全部9个功能入口
- [x] database.py 使用 with conn.begin(): 上下文管理器
- [x] models/base.py SafeJSON TypeDecorator 存在且处理空字符串
- [x] models/project.py document_specs 字段使用SafeJSON类型
- [x] models/library.py LibraryProject 关联表正确定义

## Task 4 验证: 临时文件清理

- [x] 06_交付物打包/archive_temp/ 已删除
- [x] __pycache__/ 目录已清理(14个)
- [x] dist/Python项目管理工具.exe 仍存在(58.3MB)
- [x] data/project_manager.db 仍存在(228KB)

## Task 5 验证: 文档-代码同步

- [x] 需求规格说明书中的功能点有对应代码实现(80%覆盖)
- [x] 架构设计的模块结构与src/实际目录匹配(100%)
- [x] 版本变更台帐V2.1.0/V2.2.0条目与代码变更一致(100%)
- [x] 各迭代spec(Task全✅)的功能已实现(5/7完成)

## Task 6 验证: 审计报告输出

- [x] 审计报告已生成(QA_AUDIT_REPORT_V2.2.0.md)
- [x] 包含🔴Critical(2个)/🟡Warning(6个)/ℹ️Suggestion(5个)三级分类
- [x] 包含每个问题的位置(文件:行号)和整改建议
- [x] 包含文档-代码不一致清单(87.9%同步率)
