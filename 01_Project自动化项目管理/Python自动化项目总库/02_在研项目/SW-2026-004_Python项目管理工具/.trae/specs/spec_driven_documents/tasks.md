# 规范驱动文档体系 - 任务计划

## [x] Task 1: P0紧急修复 - 立项表 + HMI目录 (不涉及架构变更)
- **Priority**: P0
- **Depends On**: None
- **Description**:
  1. **修复立项表模板**: 在 `constants.py` 的 `TPL-SINGLE-PLC-001`（及其他4个模板）的立项表模板 content 中增加一行 `| 使用模板 | {template_id} ({template_name}) |`。需要在 template_vars 中增加 `template_id` 和 `template_name` 两个变量，并在 `project_service.py` 的 create_project() 中传入
  2. **修复HMI目录生成**: 在 `project_service.py` 的目录创建循环中，确保 `required=False` 的目录也创建（当前代码 Line 128-130 只创建 required=True 的目录）。改为无条件创建所有 structure 中定义的目录
- **Files**: src/core/constants.py, src/services/project_service.py
- **Test Requirements**:
  - 新建项目后，立项表md文件内容包含"使用模板"行
  - 使用 TPL-SINGLE-PLC-001 创建项目后，`20_软件程序/22_HMI_ProFace/Docs/` 目录存在

## [x] Task 2: P1 - 扩展规范体系：新增文档模板类规范
- **Priority**: P1
- **Depends On**: None (可与Task1并行)
- **Description**:
  1. **在 spec_service.py 的 BUILTIN_SPECS 中新增约16个文档模板规范**, category="文档模板"。覆盖当前 DEFAULT_TEMPLATES 中所有 templates[] 定义的文档：
     - SPEC-DOC-INIT-001: 项目立项表模板
     - SPEC-DOC-REQ-001: 需求分析文档模板
     - SPEC-DOC-IO-001: IO分配表模板
     - SPEC-DOC-PLCDESIGN-001: PLC程序设计总文档模板
     - SPEC-DOC-ARCH-001: 系统架构设计说明书模板
     - SPEC-DOC-INTERLOCK-001: 联锁逻辑设计说明书模板
     - SPEC-DOC-EPLAN-001: 电气图纸清单模板
     - SPEC-DOC-HWCONFIG-001: PLC硬件配置表模板
     - SPEC-DOC-MECHBOM-001: 机械BOM清单模板
     - SPEC-DOC-OPMAN-001: 操作手册模板
     - SPEC-DOC-FAULT-001: 故障排除手册模板
     - SPEC-DOC-MAINT-001: 维护手册模板
     - SPEC-DOC-ACCEPT-001: 验收检查表模板
     - SPEC-DOC-TRAIN-001: 培训记录模板
     - SPEC-DOC-SUMMARY-001: 项目总结报告模板
     - SPEC-DOC-README-001: 项目README模板
  2. **每个规范的数据结构**:
     ```python
     {
         "spec_id": "SPEC-DOC-INIT-001",
         "name": "项目立项表模板",
         "category": "文档模板",
         "version": "V1.0.0",
         "content": "# {project_name} 项目立项表\n\n| 项目 | 内容 |\n...",  # 从现有硬编码content迁移
         "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001", ...],  # 适用哪些项目模板
         "file_path_pattern": "00_项目管理/01_立项与需求/{project_code}_项目立项表.md",  # 文件路径模式
         "check_rules": [],  # 可选：文档质量检查规则
         "is_active": True
     }
     ```
  3. **SpecService 无需改动**: 新增的规范通过 initialize_builtin_specs() 自动加载（与现有6个规范相同机制）
- **Files**: src/services/spec_service.py
- **Test Requirements**:
  - SpecService.initialize_builtin_specs() 后，BUILTIN_SPECS 包含 6+16=22 个规范
  - 查询 category="文档模板" 返回16个文档模板规范
  - 每个规范的 content 字段包含有效的 Markdown 模板内容

## [x] Task 3: P2 - 改造项目创建流程：优先使用规范模板
- **Priority**: P2
- **Depends On**: Task 1, Task 2
- **Description**:
  1. **扩展 template_vars**: 在 project_service.py create_project() 的 template_vars 字典中增加 `template_id` 和 `template_name`（Task1已部分完成）
  2. **改造文档生成逻辑** (Line 146-159):
     ```python
     # 当前逻辑（硬编码）:
     content = file_def["content"].format(**template_vars)
     
     # 改为:
     if "spec_id" in file_def:
         # 尝试从规范中心获取内容
         spec_content, _ = SpecService.get_spec_content(file_def["spec_id"])
         if spec_content:
             content = spec_content.format(**template_vars)
             # 记录文档元数据
             doc_specs[file_path] = {"spec_id": file_def["spec_id"], "spec_version": get_spec_version(file_def["spec_id"])}
         else:
             # Fallback 到硬编码
             content = file_def["content"].format(**template_vars)
             logger.warning(f"规范 {file_def['spec_id']} 未找到，使用fallback模板")
     else:
         # 无关联规范，使用硬编码
         content = file_def["content"].format(**template_vars)
     ```
  3. **DEFAULT_TEMPLATES 改造**: 为每个 template 条目增加 `spec_id` 字段（指向Task2中创建的对应规范ID）
  4. **Project模型增强**: 增加 `document_specs` JSON 字段用于记录每个文档的来源规范信息
- **Files**: src/services/project_service.py, src/core/constants.py, src/models/project.py
- **Test Requirements**:
  - 创建项目时，文档内容来自规范中心而非硬编码
  - Project.document_specs 字段正确记录每个文档的 spec_id 和 spec_version
  - 当某个 spec_id 不存在时，自动 fallback 到硬编码并记录警告日志

## [x] Task 4: P3 - 规范更新感知功能
- **Priority**: P3
- **Depends On**: Task 2, Task 3
- **Description**:
  1. **新增 SpecService 方法** `check_document_updates(project_id: str) -> Dict`:
     - 读取项目的 document_specs 字段
     - 对比每个文档记录的 spec_version vs 规范中心该 spec 的当前 version
     - 返回可更新的文档列表、已最新的列表、缺失规范的列表
  2. **新增 SpecService 方法** `update_project_document(project_id: str, file_path: str, spec_id: str) -> tuple[bool, str]`:
     - 获取规范中心的最新内容
     - 用新内容覆盖项目的对应文件
     - 更新 document_specs 中的 version
  3. **GUI集成 - 规范中心**: 在 spec_center.py 增加操作按钮或标签页：
     - "检查文档更新" 按钮 → 选择项目 → 显示过期的文档列表 → 用户勾选要更新的 → 执行更新
  4. **缺失规范建议**: create_project() 完成后，如果某些文档没有匹配到任何规范 → 在返回结果或对话框中显示建议列表
- **Files**: src/services/spec_service.py, src/ui/widgets/spec_center.py
- **Test Requirements**:
  - check_document_updates() 能正确检测出版本差异
  - update_project_document() 能用新规范内容覆盖旧文档
  - GUI能显示更新建议并执行选择性更新

## Task Dependencies
- [Task 1] || [Task 2] 可并行执行（P0修复 vs P1规范定义互不影响）
- [Task 3] depends on [Task 1], [Task 2]（需要变量扩展+规范数据就绪）
- [Task 4] depends on [Task 2], [Task 3]（需要规范体系+文档元数据就绪）
