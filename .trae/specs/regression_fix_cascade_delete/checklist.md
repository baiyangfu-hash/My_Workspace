# Checklist: 修复删除项目级联错误 + 全面回归

## Task 1 验证: project_dao.py 删除关联表安全清理

- [x] `delete()`方法hard_delete分支中，session.delete(project)前有library_projects清理步骤
- [x] 清理使用synchronize_session=False宽容模式（不校验实际删除行数）
- [x] 清理顺序正确: library_projects → changes → project
- [x] 删除无关联的老项目不再抛出 "expected to delete 1 row(s)" 异常
- [x] 删除有关联的新项目能同时清理关联记录

## Task 1.5 验证: library_manager.py 硬编码修复

- [x] 业务线选项使用BusinessLine枚举动态生成（非硬编码["SW","HW","TEST"]）
- [x] 模板ID从TemplateService动态获取（非硬编码"TPL-DEFAULT-001"）
- [x] 业务线值提取逻辑正确（split去除描述部分）
- [x] 空模板时有用户友好提示

## Task 2 验证: 模板模块回归

- [x] 模板管理界面正常加载所有模板（含内置标记★）
- [x] 新建项目对话框模板下拉框按业务线分类显示
- [x] 内置模板的编辑按钮为enabled状态
- [x] 模板重置功能可恢复到初始状态
- [x] 模板列表数据无膨胀（应为5个左右）

## Task 3 验证: 规范驱动文档回归

- [x] 新建项目的立项表中显示所使用模板的名称和版本
- [x] 项目目录中包含HMI子目录
- [x] 规范中心可浏览规范列表（≥20条目）
- [x] document_specs字段记录了文档规范追踪信息

## Task 4 验证: 总库管理回归

- [x] 系统启动后数据库中只有1个默认总库（无重复）
- [x] 默认总库有有效的root_path值
- [x] 总库管理界面4个Tab都能正常切换和加载数据
- [x] 新建项目自动出现在总库的项目列表中
- [x] 总库统计面板显示正确的项目数量
- [x] 扫描导入功能使用动态枚举值和模板ID

## Task 5 验证: 路径修复回归

- [x] 新建项目对话框打开时"所属总库"默认显示"Python自动化项目总库"
- [x] "项目路径"字段非空，格式为 `{root_path}\0100_项目\{code}_{name}`
- [x] 输入项目名称后路径实时更新
- [x] 切换到"(不关联总库)"路径降级到cwd
