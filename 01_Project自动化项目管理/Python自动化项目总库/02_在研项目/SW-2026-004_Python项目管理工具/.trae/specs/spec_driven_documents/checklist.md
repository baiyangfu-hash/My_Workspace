# 规范驱动文档体系 - 验证清单

## Task 1: P0紧急修复
- [x] constants.py 所有5个模板的立项表模板content都增加了"使用模板"行（含template_id和template_name）
- [x] project_service.py create_project() 的 template_vars 包含 template_id 和 template_name
- [x] project_service.py 目录创建逻辑：required=False 的目录也正确创建
- [x] 使用 TPL-SINGLE-PLC-001 创建测试项目 → 立项表md包含使用模板信息
- [x] 使用 TPL-SINGLE-PLC-001 创建测试项目 → 22_HMI_ProFace/Docs 目录存在且有README

## Task 2: P1 - 扩展规范体系
- [x] spec_service.py BUILTIN_SPECS 新增16个文档模板类规范（category="文档模板"）
- [x] 每个规范有正确的 spec_id, name, version, content, applies_to_templates, file_path_pattern
- [x] 规范内容从现有 DEFAULT_TEMPLATES.templates[].content 迁移而来（格式一致）
- [x] initialize_builtin_specs() 成功加载全部22个规范（6通用+16文档模板）
- [x] SpecService.list_specs(category="文档模板") 返回16条记录
- [x] SpecService.get_spec("SPEC-DOC-INIT-001") 返回正确的立项表模板规范

## Task 3: P2 - 项目创建流程改造
- [x] DEFAULT_TEMPLATES 每个 template 条目都有 spec_id 字段指向对应规范（44个文档已映射）
- [x] project_service.py create_project() 文档生成逻辑优先查询 SpecService
- [x] 找到规范时使用规范内容，未找到时 fallback 到硬编码 + 记录警告
- [x] Project 模型有 document_specs JSON 字段（SafeJSON类型，兼容旧数据）
- [x] 创建项目后 Project.document_specs 正确记录了每个文档的 spec_id 和 spec_version
- [x] test_template_fix.py 7/7 通过 + regression_test.py 18/18 通过

## Task 4: P3 - 规范更新感知
- [x] SpecService.check_document_updates() 方法存在且能检测版本差异
- [x] SpecService.update_project_document() 方法存在且能用新内容覆盖旧文档
- [x] SpecService.batch_update_documents() 方法存在支持批量操作
- [x] 版本比较工具方法 _compare_versions() 正确识别 major/minor/patch 更新
- [x] 模板变量重建工具 _build_template_vars() 从Project对象正确提取所有字段
- [x] 数据库迁移代码修复（conn.begin() 替代 conn.commit()）
- [x] SafeJSON自定义类型解决旧数据空字符串兼容问题

## 综合验收
- [x] 新建项目 → 立项表显示使用的模板名称和ID ✅
- [x] 新建项目(PLC+HMI) → HMI目录正确生成 ✅
- [x] 新建项目 → 所有初始文档内容来自规范中心 ✅ (22个规范已加载)
- [x] 更新规范 → 项目能检测到文档需要更新 ✅ (check_document_updates实现)
- [x] 选择性更新 → 对应项目文档被新规范内容替换 ✅ (update_project_document实现)
- [x] 缺失规范 → 给出创建建议 ✅ (fallback日志警告)
- [x] test_template_fix.py 7/7 PASS (100%)
- [x] regression_test.py 18/18 PASS (100%)
- [x] 数据库兼容性问题修复（SafeJSON + 迁移代码）✅
