# SW-2026-004 全面优化迭代 Spec

## Why

用户反馈两个关键问题：
1. **新建项目时模板无法选择** - GUI对话框中"项目模板"下拉框为空，导致无法创建项目
2. **项目文件结构混乱** - 根目录堆积40+个脚本文件（测试/工具/临时/调试），文档分散且冗余，严重影响可维护性

本次优化旨在系统性地解决上述问题，使工具恢复正常功能并建立清晰的项目结构。

## What Changes

### P0 - 紧急修复（模板选择问题）
- **修复模板初始化**: 取消 `main_window.py:348` 中 `initialize_builtin_templates()` 的注释，确保内置模板在启动时加载到数据库
- **验证模板数据流**: 确保 DEFAULT_TEMPLATES → TemplateService.initialize_builtin_templates() → 数据库 → NewProjectDialog 下拉框 完整链路畅通

### P1 - 脚本文件清理（根目录混乱）
- **分类整理40+个.py文件**:
  - ✅ 保留: main.py, setup.py, build.py, regression_test.py (核心)
  - 📁 归档到 tests/: comprehensive_test_v2.py, run_all_tests.py, test_*.py 等（测试脚本）
  - 🗑️ 删除临时/调试: debug_imports.py, test_connection.py, test_import.py, test_phase*.py, create_*.py, verify_*.py, cleanup_*.py, force_*.py
- **清理.bat/ps1文件**: 合并为统一的运行脚本

### P2 - 文档结构优化
- **精简01_项目文档/**: 移除重复/过时的诊断报告（CHK-V1.0.2~V1.6 多版本）, 保留最新版
- **统一测试报告位置**: 将散落的测试报告归入 data/test_reports/
- **更新版本变更台帐**: 记录本次所有修改

### P3 - 全面回归测试
- 运行 regression_test.py (18项)
- 验证 GUI 启动和新建项目流程
- 验证模板选择和项目创建完整链路

## Impact

- Affected specs: template_location, template_reorganization, update_and_repackage (本spec综合覆盖并超越这些未完成spec的范围)
- Affected code:
  - `src/ui/main_window.py` - 取消注释模板初始化
  - 根目录 40+ .py/.bat/.ps1 文件 - 清理重组
  - `01_项目文档/` - 文档精简

## ADDED Requirements

### Requirement: 模板初始化修复
The system SHALL initialize built-in templates into database on application startup.

#### Scenario: 新建项目时模板可选
- **WHEN** 用户打开"新建项目"对话框
- **THEN** "项目模板"下拉框应显示至少1个可用模板（基于当前选择的业务线）
- **AND** 推荐模板标记★显示在最前面

#### Scenario: 应用首次启动
- **WHEN** 应用程序启动（MainWindow初始化）
- **THEN** `TemplateService.initialize_builtin_templates()` 应被执行
- **AND** 数据库中应存在 DEFAULT_TEMPLATES 中定义的所有内置模板

### Requirement: 项目目录整洁
The project root directory SHALL only contain essential files.

#### Scenario: 根目录文件清单
- **WHEN** 列出根目录 .py 文件
- **THEN** 仅保留: main.py, setup.py, build.py, regression_test.py
- **AND** 所有测试脚本移至 tests/ 子目录
- **AND** 所有临时/调试脚本被删除

### Requirement: 测试通过率100%
All regression tests SHALL pass after optimization.

## MODIFIED Requirements

### Requirement: 应用启动流程
**原**: MainWindow._load_data() 中模板初始化被注释
**改**: MainWindow._load_data() 应调用 TemplateService.initialize_builtin_templates() 确保模板就绪

## REMOVED Requirements

### Requirement: 临时测试脚本
**Reason**: 这些是开发过程中的临时调试产物，不再需要
**Migration**: 关键测试逻辑已整合进 regression_test.py 和 comprehensive_test_v2.py
- debug_imports.py
- test_connection.py  
- test_import.py
- test_phase1.py ~ test_phase4.py
- create_conveyor_project.py
- create_plc_project.py
- create_test_projects.py
- create_upper_test.py
- create_templates.py
- cleanup_templates.py
- force_cleanup_templates.py
- verify_templates.py
- verify_change_document_generation.py
- test_manual_document_generation.py
- test_create_projects_with_templates.py
- test_project_creation.py
