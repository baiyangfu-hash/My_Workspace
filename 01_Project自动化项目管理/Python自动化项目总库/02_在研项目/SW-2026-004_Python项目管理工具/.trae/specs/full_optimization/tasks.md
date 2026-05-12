# SW-2026-004 全面优化迭代 - 任务计划

## [x] Task 1: 修复模板初始化（P0 - 紧急）
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 修改 `src/ui/main_window.py` 第348行附近，取消 `TemplateService.initialize_builtin_templates()` 的注释
  - 确保在 `_load_data()` 或应用启动早期调用此方法
  - 验证 DEFAULT_TEMPLATES 中的模板能正确加载到数据库
- **Acceptance Criteria**: AC-模板初始化
- **Test Requirements**:
  - `programmatic` TR-1.1: 启动应用后，数据库 templates 表中应有记录
  - `programmatic` TR-1.2: NewProjectDialog 打开时模板下拉框不为空
- **Files**: src/ui/main_window.py

## [x] Task 2: 清理根目录脚本文件（P1）
- **Priority**: P1
- **Depends On**: None (可与Task1并行)
- **Description**:
  - 创建 tests/ 目录
  - 将以下测试/工具脚本移入 tests/:
    - comprehensive_test.py, comprehensive_test_v2.py, comprehensive_test_framework.py
    - run_tests.py, run_all_tests.py, run_full_test_suite.py, auto_test_all.py
    - simple_test.py, full_functional_test.py
    - test_spec_sync.py, test_api_service.py, test_api_client.py
  - 删除以下临时/调试脚本（共约18个）:
    - debug_imports.py, test_connection.py, test_import.py
    - test_phase1.py ~ test_phase4.py
    - create_conveyor_project.py, create_plc_project.py, create_test_projects.py, create_upper_test.py, create_templates.py
    - cleanup_templates.py, force_cleanup_templates.py, verify_templates.py
    - verify_change_document_generation.py, test_manual_document_generation.py
    - test_create_projects_with_templates.py, test_project_creation.py
  - 清理 .bat/.ps1 文件，保留 run_auto_tests.bat 合并其他功能
- **Acceptance Criteria**: AC-目录整洁
- **Test Requirements**:
  - `programmatic` TR-2.1: 根目录 .py 文件 ≤ 5个
  - `programmatic` TR-2.2: tests/ 目录包含所有归档的测试脚本
- **Files**: 根目录 *.py, *.bat, *.ps1

## [x] Task 3: 精简项目文档（P2）
- **Priority**: P2
- **Depends On**: Task 2
- **Description**:
  - 审查 01_项目文档/04_监控和控制/ 下的诊断报告
  - 保留最新版 CHK-V1.0x，归档或删除旧版本重复报告
  - 将 data/reports/ 和 data/test_reports/ 中的测试报告整理合并
  - 更新 06_版本变更台帐_CHG-V2.1.0.md 记录本次修改
- **Acceptance Criteria**: AC-文档整洁
- **Test Requirements**:
  - `human-judgment` TR-3.1: 无明显重复文档
  - `human-judgment` TR-3.2: 变更台帐已更新
- **Files**: 01_项目文档/, data/

## [x] Task 4: 全面回归测试（P0）
- **Priority**: P0
- **Depends On**: Task 1, Task 2
- **Description**:
  - 运行 regression_test.py 验证 18项基础导入和GUI组件
  - 运行 comprehensive_test_v2.py 验证业务功能
  - 手动验证新建项目对话框中模板可选择
  - 验证项目创建完整流程（选择模板 → 填写信息 → 创建成功）
- **Acceptance Criteria**: AC-测试通过
- **Test Requirements**:
  - `programmatic` TR-4.1: regression_test.py 18/18 通过
  - `programmatic` TR-4.2: comprehensive_test_v2.py 全部通过
  - `programmatic` TR-4.3: 模板下拉框有可选项
  - `programmatic` TR-4.4: 项目创建流程端到端正常
- **Files**: regression_test.py, comprehensive_test_v2.py

## Task Dependencies
- [Task 4] depends on [Task 1], [Task 2]
- [Task 3] depends on [Task 2]
- [Task 1] || [Task 2] 可并行执行
