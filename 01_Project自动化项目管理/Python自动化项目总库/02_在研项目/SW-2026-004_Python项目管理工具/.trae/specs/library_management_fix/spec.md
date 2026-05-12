# 总库管理模块完善 - Spec

## Why

当前总库管理系统是一个**空壳架构**：
1. **没有默认总库** — 系统启动后总库列表为空，用户必须手动创建
2. **项目创建不关联总库** — `project_service.py` 的 `create_project()` 完全不涉及 library，新建项目全部"散装"
3. **GUI有框架无逻辑** — 总库管理界面（总库详情/项目管理/分类管理/统计信息标签页）存在但后端服务未接通
4. **已有模型未使用** — Library/LibraryProject/Category 模型已定义，library_dao/library_service 等文件已存在，但核心流程断裂

**用户诉求**: 完善总库管理功能模块，使其从"架子"变为可用的完整功能 — 有默认总库、项目自动归档、跨项目统计。

## What Changes

### 核心改造（让总库真正工作）

- **默认总库初始化**: 系统启动时自动创建默认总库 "Python自动化项目总库"（类似模板的 initialize_builtin_templates 机制）
- **项目创建自动归档**: 改造 `create_project()` 使新项目自动加入默认总库（或用户指定的总库）
- **新建项目对话框增强**: 在新建项目界面增加"所属总库"选择下拉框（默认选中默认总库）
- **总库统计面板激活**: 总库管理的"统计信息"标签页显示真实数据（项目数/状态分布/业务线分布）
- **总库项目管理标签页激活**: 显示该总库下的所有项目列表，支持添加/移除操作
- **分类管理基础功能**: 默认总库下按业务线自动创建分类（SOFTWARE/DEVICE/AUTOMATION等）

### 不做（控制范围）
- ❌ 总库版本控制（Git集成）— 过于复杂，后续迭代
- ❌ 总库依赖关系图谱 — 后续迭代
- ❌ 总库发布管理 — 后续迭代
- ❌ 多总库高级管理 — 本次只做"默认单总库"场景

## Impact

- Affected specs: 无现有spec受影响
- Affected code:
  - `src/services/library_service.py` — 新增初始化/归档/统计方法
  - `src/services/project_service.py` — 改造create_project()增加总库关联
  - `src/ui/dialogs/new_project_dialog.py` — 增加总库选择UI
  - `src/ui/widgets/library_manager.py` (或类似名称) — 激活各标签页功能
  - `src/dao/library_dao.py` — 可能需要新增查询方法
  - `main_window.py` / `main.py` — 启动时调用总库初始化

## ADDED Requirements

### Requirement: 默认总库自动初始化
The system SHALL automatically create a default library on startup if none exists.

#### Scenario: 首次启动系统
- **WHEN** application starts and no libraries exist in database
- **THEN** system creates a default library with:
  - `library_id`: "LIB-DEFAULT-001"
  - `name`: "Python自动化项目总库"
  - `root_path`: 项目根目录路径
  - Auto-created categories for each BusinessLine enum value

#### Scenario: 已有总库时启动
- **WHEN** application starts and libraries already exist
- **THEN** no duplicate default library is created (idempotent)

### Requirement: 项目创建时自动归档到总库
The system SHALL associate each newly created project with a library.

#### Scenario: 使用默认设置创建项目
- **WHEN** user creates a project without explicitly selecting a library
- **THEN** project is automatically added to the default library
- **AND** a LibraryProject association record is created
- **AND** project appears in the library's project list

#### Scenario: 选择指定总库创建项目
- **WHEN** user selects a specific library in the new project dialog
- **THEN** project is created and associated with that selected library

### Requirement: 新建项目对话框显示总库选择
The system SHALL provide library selection in the new project creation dialog.

#### Scenario: 打开新建项目对话框
- **WHEN** user clicks "New Project"
- **THEN** dialog shows a "所属总库" dropdown (QComboBox)
- **AND** default library is pre-selected
- **AND** user can change to another library or select "(无)" to not associate

### Requirement: 总库统计信息面板
The system SHALL display real-time statistics for the selected library.

#### Scenario: 查看默认总库的统计信息
- **WHEN** user opens library manager and selects the default library
- **AND** clicks "统计信息" tab
- **THEN** panel shows:
  - Total project count
  - Projects by status (planning/in-progress/completed/paused)
  - Projects by business line (SOFTWARE/DEVICE/AUTOMATION/UPGRADE/MAINTENANCE)
  - Recent activity timeline (last 5 projects created)

### Requirement: 总库项目管理标签页
The system SHALL allow viewing and managing projects within a library.

#### Scenario: 查看总库下的项目列表
- **WHEN** user selects a library and clicks "项目管理" tab
- **THEN** table shows all projects in that library
- **AND** each row shows: project code, name, business line, status, template, created date
- **AND** user can double-click a row to open that project's details

#### Scenario: 手动将已有项目添加到总库
- **WHEN** user has existing unassociated projects
- **AND** uses "添加项目" button in library's project tab
- **THEN** can select from unassociated projects to add to this library

### Requirement: 自动按业务线分类
The system SHALL auto-categorize projects by business line within a library.

#### Scenario: PLC项目被自动归类
- **WHEN** a project with business_line="AUTOMATION" is created/added to library
- **THEN** it automatically appears under "自动化项目" category
- **AND** category was auto-created from BusinessLine enum on library initialization

## MODIFIED Requirements

### Requirement: Project 模型
**原**: Project 模型无 library 关联字段（或有关联但未使用）
**改**: 确保 Project.library_id 外键正确工作，Project.library relationship 可用

### Requirement: main_window.py 启动流程
**原**: 启动时调用 initialize_builtin_templates()
**改**: 启动时额外调用 initialize_default_library()

## REMOVED Requirements
无
