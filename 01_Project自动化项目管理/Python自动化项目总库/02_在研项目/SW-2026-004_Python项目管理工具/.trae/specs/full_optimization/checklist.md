# SW-2026-004 全面优化迭代 - 验证清单

## Task 1: 模板初始化修复
- [x] main_window.py 中 initialize_builtin_templates() 调用已取消注释
- [x] 应用启动后数据库 templates 表有记录（11个模板）
- [x] NewProjectDialog 打开时模板下拉框显示模板列表（11个可选）
- [x] 切换业务线时模板列表正确过滤更新

## Task 2: 脚本文件清理
- [x] tests/ 目录已创建
- [x] 测试脚本已归档到 tests/（12个: comprehensive_test*.py, run_*.py, test_*.py, auto_test_all.py, simple_test.py, full_functional_test.py）
- [x] 临时/调试脚本已删除（19个: debug_imports.py, test_connection.py, test_import.py, test_phase*.py, create_*.py, cleanup_*.py, force_*.py, verify_*.py 等）
- [x] 根目录 .py 文件 ≤ 5 个（实际4个: main.py, setup.py, build.py, regression_test.py）
- [x] .bat/.ps1 文件已整理（删除3个，保留run_auto_tests.bat）

## Task 3: 文档精简
- [x] 01_项目文档/ 中无明显重复的诊断报告版本（删除5个旧版CHK报告，保留V1.0.6）
- [x] data/reports/ 和 data/test_reports/ 已确认整洁
- [x] 版本变更台帐已更新记录本次修改（V2.2.0追加）

## Task 4: 回归测试验证
- [x] regression_test.py 18/18 测试通过 (100%)
- [x] comprehensive_test_v2.py 全部测试通过
- [x] GUI MainWindow 正常创建无报错
- [x] 新建项目对话框中模板可选择（11个模板可用，不为空）
- [x] 选择模板后能成功创建项目（验证链路畅通）
- [x] 创建的项目目录结构符合所选模板定义

## 综合验收
- [x] 项目根目录整洁，无冗余临时文件（36+ → 4个 .py 文件，减少89%）
- [x] 所有核心功能正常工作（18项回归测试 + GUI + 模板 + 插件 + 规范）
- [x] 无新增语法错误或导入错误
- [x] 11个内置模板全部加载可用（TPL-001 ~ TPL-PY-DATA-001）
