# 规范驱动文档体系 - Spec

## Why

当前项目管理系统存在**4个关联问题**：

1. **立项表缺失模板信息**: `constants.py` 中立项表模板内容不含 `template_id`/模板名称字段，用户无法从立项表看出项目使用了哪个模板
2. **HMI目录生成异常**: `TPL-SINGLE-PLC-001` 模板定义了 `20_软件程序/22_HMI_ProFace/Docs` (required=False)，但由于无对应template文件且required=False，实际项目中该目录缺失
3. **文档模板硬编码**: 所有初始文档（立项表、IO分配表、操作手册等共16个）的内容**全部硬编码在 `constants.py` 的 `DEFAULT_TEMPLATES[].templates[]` 中**，与全局规范中心（SpecService）**完全脱节**
4. **无法追踪规范更新**: 当前规范系统只有6个通用编码规范（目录结构、命名、代码风格、Git、API），缺少业务文档模板规范；且项目文档与全局规范之间**无任何关联关系**，规范更新后无法通知到已创建的项目

**用户核心诉求**: 默认文档模板应来自全局规范中心 → 规范更新时应能选择更新项目文档 → 缺失规范/模板时应给出建议

## What Changes

### P0 - 紧急修复（不影响架构）
- **修复立项表模板**: 在 `{project_code}_项目立项表.md` 的模板内容中增加 `| 使用模板 | {template_id} ({template_name}) |` 字段
- **修复HMI目录生成**: 确保 `22_HMI_ProFace/Docs` 目录正确创建（即使 required=False 也要创建空目录+README）

### P1 - 架构改造：建立"文档模板规范"体系
- **扩展 BUILTIN_SPECS**: 在 `spec_service.py` 中新增一类规范 —— `category="文档模板"` (Document Template Specs)
- **每个文档模板对应一个规范ID**, 例如:
  - `SPEC-DOC-INIT-001` → 项目立项表模板
  - `SPEC-DOC-IO-001` → IO分配表模板
  - `SPEC-DOC-OPMAN-001` → 操作手册模板
  - `SPEC-DOC-FAULT-001` → 故障排除手册模板
  - ... （覆盖所有16个现有硬编码文档）
- **规范结构包含**: `spec_id`, `name`(文档名称), `version`, `content`(Markdown模板内容), `applies_to_templates`(适用哪些项目模板), `file_path_pattern`(生成的文件路径模式)

### P2 - 项目创建流程改造
- **改造 `project_service.py` 的 `create_project()`**:
  - 当前的: 从 `template.templates[]` 硬编码读取 content → format替换 → 写文件
  - 改为: 遍历 `template.structure` + 查询 SpecService 获取对应文档模板规范 → 如果找到规范则使用规范内容 → 否则 fallback 到 template.templates[] 的硬编码内容
- **建立映射关系**: 模板的 `templates[].path` 与规范的 `file_path_pattern` 通过路径匹配关联

### P3 - 规范更新感知
- **项目文档元数据增强**: 在 Project 模型中增加 `document_specs` JSON 字段，记录每个生成文档对应的 `spec_id + spec_version`
- **规范更新检查**: 在规范中心增加 "检查项目文档更新" 功能：
  - 对比项目记录的 `spec_version` vs 规范中心的最新版本
  - 列出可更新的文档清单
  - 用户可选择逐个更新或批量更新
- **缺失规范检测**: 创建项目时，如果某个文档在规范中心找不到对应规范 → 在项目创建日志中提示 "建议为 XXX 文档创建规范模板"

## Impact

- Affected specs: 无现有spec受影响（这是新功能）
- Affected code:
  - `src/core/constants.py` — 修改 DEFAULT_TEMPLATES 中立项表模板内容 + HMI structure 标记
  - `src/services/spec_service.py` — 扩展 BUILTIN_SPECS 新增文档模板类规范（约16个）
  - `src/services/project_service.py` — 改造 create_project() 文档生成逻辑
  - `src/models/project.py` — 增加 document_specs 字段
  - `src/ui/widgets/spec_center.py` — 增加"文档模板规范"分类标签页 + 更新检查功能
  - `src/ui/dialogs/new_project_dialog.py` — 显示规范建议信息

## ADDED Requirements

### Requirement: 立项表显示使用的模板信息
The system SHALL record the template ID and name in the project initiation document.

#### Scenario: 用户查看新建项目的立项表
- **WHEN** a project is created using template `TPL-SINGLE-PLC-001`
- **THEN** the file `{project_code}_项目立项表.md` contains a row `| 使用模板 | TPL-SINGLE-PLC-001 (单机设备PLC+HMI) |`

### Requirement: HMI目录正确生成
The system SHALL create all directories defined in template structure, including optional ones.

#### Scenario: 使用PLC+HMI模板创建项目
- **WHEN** project is created with `TPL-SINGLE-PLC-001`
- **THEN** directory `20_软件程序/22_HMI_ProFace/Docs/` exists with README.md placeholder

### Requirement: 文档模板规范体系
The system SHALL define each document template as a formal spec in the global spec center.

#### Scenario: 浏览规范中心的"文档模板"分类
- **WHEN** user opens SpecCenter and selects "文档模板" category
- **THEN** user sees list of document template specs (e.g., SPEC-DOC-INIT-001, SPEC-DOC-IO-001, etc.)
- **AND** each spec shows: name, version, applicable templates, file path pattern, and full markdown template content

### Requirement: 项目创建时优先使用规范模板
The system SHALL use spec-driven document templates when creating projects, falling back to hardcoded templates only when no matching spec exists.

#### Scenario: 使用有完整规范覆盖的模板创建项目
- **WHEN** project is created and all documents have matching specs in SpecCenter
- **THEN** all generated documents use content from the corresponding specs
- **AND** each document's metadata records the source `spec_id` and `spec_version`

#### Scenario: 使用部分规范覆盖的模板创建项目
- **WHEN** project is created and some documents have no matching spec
- **THEN** documents WITH matching specs use spec content
- **AND** documents WITHOUT matching specs fall back to hardcoded `template.templates[]` content
- **AND** a warning log entry suggests creating missing specs

### Requirement: 规范更新感知与选择性更新
The system SHALL detect when document template specs are updated and allow users to update existing project documents.

#### Scenario: 规范中心更新了某个文档模板规范
- **WHEN** admin updates `SPEC-DOC-OPMAN-001` from V1.0.0 to V1.1.0
- **AND** user runs "Check Document Updates" on an existing project
- **THEN** system shows: "操作手册模板有新版本 V1.0.0 → V1.1.0"
- **AND** user can choose to update or skip each outdated document

### Requirement: 缺失规范建议
The system SHALL suggest creating new document template specs when gaps are detected.

#### Scenario: 新建了一个自定义模板但对应文档没有规范
- **WHEN** custom template has document definitions without matching specs
- **THEN** system logs suggestion: "建议为 [文档名称] 创建文档模板规范"
- **AND** shows the suggestion in the project creation result dialog

## MODIFIED Requirements

### Requirement: DEFAULT_TEMPLATES 数据结构
**原**: `templates[]` 中每个条目包含 `path`, `type`, `content`(硬编码)
**改**: `templates[]` 保持不变作为 fallback，但优先级低于规范中心。新增可选字段 `spec_id` 用于显式指定关联的规范ID

```python
# 改造后的模板定义示例
{
    "path": "00_项目管理/01_立项与需求/{project_code}_项目立项表.md",
    "type": "document", 
    "spec_id": "SPEC-DOC-INIT-001",  # 新增：关联的规范ID
    "content": "# {project_name} 项目立项表\n..."  # 保留作为fallback
}
```

### Requirement: BUILTIN_SPECS 数据结构
**原**: 只有6个通用编码规范
**改**: 新增约16个文档模板类规范（category="文档模板"），每个包含 `applies_to_templates` 和 `file_path_pattern` 字段

### Requirement: Project 模型
**原**: 无文档规范追踪字段
**改**: 新增 `document_specs` JSON 字段，格式:
```json
{
  "00_项目管理/01_立项与需求/DJ-2026-002_项目立项表.md": {
    "spec_id": "SPEC-DOC-INIT-001",
    "spec_version": "V1.0.0",
    "updated_at": "2026-04-12"
  }
}
```

## REMOVED Requirements
无（所有现有功能保持兼容，仅增加新能力）
