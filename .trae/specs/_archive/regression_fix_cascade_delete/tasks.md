# Tasks: 修复删除项目级联错误 + 全面回归

## 任务列表

- [x] **Task 1: 修复 project_dao.py 删除时library_projects级联错误** ⚠️ P0
  - [x] 1.1 在`delete()`方法的hard_delete分支中，`session.delete(project)`之前添加library_projects清理代码
  - [x] 1.2 使用`synchronize_session=False`参数避免严格行数校验
  - [x] 1.3 保持原有逻辑: 先删changes、清理关联、再删project的顺序

- [x] **Task 1.5: 修复 library_manager.py 扫描导入硬编码错误** ⚠️ P0 (回归发现)
  - [x] 1.5.1 业务线选项从硬编码`["SW","HW","TEST"]`改为动态读取BusinessLine枚举
  - [x] 1.5.2 模板ID从硬编码`"TPL-DEFAULT-001"`改为从TemplateService动态获取
  - [x] 1.5.3 添加业务线值提取逻辑（去除描述部分）和空模板检查

- [x] **Task 2: 模板模块回归检查** 🔍 P1
  - [x] 2.1 ✅ 模板列表加载正常（内置+自定义），list_all/force_delete完整
  - [x] 2.2 ✅ 新建项目能选择模板并正确生成目录结构
  - [x] 2.3 ✅ 编辑按钮可用（builtin模板也可编辑）
  - [x] 2.4 ✅ 重置/删除功能正常，无数据膨胀

- [x] **Task 3: 规范驱动文档回归检查** 🔍 P1
  - [x] 3.1 ✅ 新建项目立项表显示使用的模板名称
  - [x] 3.2 ✅ HMI目录在项目中正确创建
  - [x] 3.3 ✅ 规范中心可浏览22个规范条目，document_specs追踪完整

- [x] **Task 4: 总库管理模块回归检查** 🔍 P1
  - [x] 4.1 ✅ 默认总库自动初始化（无重复），root_path有效
  - [x] 4.2 ✅ 总库管理UI 4个Tab正常显示（详情/项目/分类/统计）
  - [x] 4.3 ✅ 新建项目自动归档到默认总库
  - [x] 4.4 ⚠️ 扫描导入功能有硬编码错误 → 已修复(Task 1.5)

- [x] **Task 5: 路径修复回归检查** 🔍 P1
  - [x] 5.1 ✅ 新建项目对话框"所属总库"默认选中"Python自动化项目总库"
  - [x] 5.2 ✅ "项目路径"自动填充为 `...\0100_项目\{编号}_{名称}`
  - [x] 5.3 ✅ 切换总库选项后路径正确更新

## Task Dependencies

- [Task 1] ✅ 最先执行（P0 Bug修复）
- [Task 1.5] ✅ 回归发现后立即修复
- [Task 2] ~ [Task 5] ✅ 并行执行回归检查完成
