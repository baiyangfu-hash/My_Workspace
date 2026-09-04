# 模板管理模块迭代优化 Spec

## Why

用户反馈模板管理功能模块存在多个问题：
1. **数据库中显示12个模板**（旧11个+新1个），但 constants.py 已更新为5个新模板 — 旧模板残留未清理
2. **内置模板被完全锁定** — `update_template()` 直接拒绝修改 `is_builtin=True` 的模板，用户无法编辑任何内置模板
3. **删除内置模板后重启恢复** — `initialize_builtin_templates()` 的 `if not exists` 逻辑导致被删的内置模板自动重建
4. **业务线枚举值不一致** — template_editor.py 硬编码 SW/DJ/ZD/LX/XT/QT/WX，但 BusinessLine 枚举用 SOFTWARE/DEVICE/AUTOMATION/UPGRADE/MAINTENANCE
5. **GUI操作列** 只显示"操作"文字没有实际按钮，依赖右键菜单不够直观

本次优化**仅针对模板管理模块**（service层 + dao层 + GUI层 + editor对话框），不影响其他模块。

## What Changes

### P0-Bug修复
- **修复旧模板残留**: `initialize_builtin_templates()` 增加清理不在 DEFAULT_TEMPLATES 中的旧记录
- **修复业务线枚举不一致**: 统一 template_editor.py 与 BusinessLine 枚举值

### P1-功能增强
- **允许编辑内置模板**: 移除 `update_template()` 中对 is_builtin 的硬性拒绝，改为允许修改非关键字段（名称/描述/结构/文档），禁止修改 template_id 和 is_builtin 标志
- **增加"重置内置模板"按钮**: 提供一键将所有内置模板恢复到 DEFAULT_TEMPLATES 定义的功能
- **增加"清理无效模板"按钮**: 清理数据库中不在 DEFAULT_TEMPLATES 中的非内置模板

### P2-GUI优化
- **操作列改为实际按钮**: 在表格的操作列添加 编辑/导出/复制/删除 按钮（不再仅依赖右键菜单）
- **内置模板行高亮/图标区分**: 用不同颜色或图标区分内置模板和自定义模板
- **模板统计信息栏**: 底部显示 "共X个模板 (Y个内置 / Z个自定义)"

## Impact
- Affected code:
  - `src/services/template_service.py` — 修复initialize/update/delete/add reset/cleanup方法
  - `src/ui/widgets/template_manager.py` — GUI优化(按钮列/高亮/统计栏/新增按钮)
  - `src/ui/widgets/template_editor.py` — 修复业务线枚举/移除readonly硬限制
  - `src/core/constants.py` — 无需修改(已完成5类模板更新)
- 不影响: main_window.py, project_service.py, change_service.py 等其他模块

## ADDED Requirements

### Requirement: 模板初始化时清理孤立记录
The system SHALL remove database records for templates whose ID does NOT exist in DEFAULT_TEMPLATES AND are marked as is_builtin=True.

#### Scenario: 启动应用后只显示正确的5个内置模板
- **WHEN** application starts and calls `initialize_builtin_templates()`
- **THEN** old builtin templates (TPL-001, TPL-002, etc.) that no longer exist in DEFAULT_TEMPLATES are deleted from DB
- **AND** only the 5 new templates from DEFAULT_TEMPLATES exist as builtin templates in DB

### Requirement: 允许编辑内置模板的非标识字段
The system SHALL allow users to edit builtin templates' name, description, structure, templates content, but NOT template_id or is_builtin flag.

#### Scenario: 用户修改内置模板的名称和结构
- **WHEN** user opens a builtin template in TemplateEditorDialog
- **THEN** name/description/compiler/scene/structure/templates fields are editable
- **AND** template_id field remains readonly
- **AND** save calls update_template() which allows updating non-identity fields of builtin templates

### Requirement: 一键重置内置模板
The system SHALL provide a "Reset Builtin Templates" button that restores all builtin templates to match DEFAULT_TEMPLATES exactly.

#### Scenario: 用户误改内置模板后想恢复原样
- **WHEN** user clicks "Reset Builtin Templates" button with confirmation dialog
- **THEN** all records where is_builtin=True are deleted and re-created from DEFAULT_TEMPLATES
- **AND** custom templates (is_builtin=False) are untouched

### Requirement: GUI操作列按钮化
The system SHALL display actual action buttons (Edit/Export/Copy/Delete) in the table's operation column, not just text.

### Requirement: 内置/自定义模板视觉区分
The system SHALL visually distinguish builtin templates from custom templates using color coding or icons in the template list.

## MODIFIED Requirements

### Requirement: update_template 方法
**原**: `if template.is_builtin: return None, "内置模板不能修改"`
**改**: 允许修改非 identity 字段(name/version/compiler/scene/description/structure/templates/business_lines)，拒绝修改 template_id 和 is_builtin。如果尝试修改这些字段返回友好提示而非直接拒绝整个更新。

### Requirement: delete_template 方法  
**原**: DAO.delete() 不区分内置/自定义
**改**: 允许删除内置模板（用户明确选择删除），但下次启动 initialize_builtin_templates() 会重新创建。在删除时给出警告提示。

### Requirement: 业务线枚举一致性
**原**: template_editor.py 硬编码 SW/DJ/ZD/LX/XT/QT/WX
**改**: 动态从 BusinessLine 枚举读取，与 constants.py 保持一致

## REMOVED Requirements
无
