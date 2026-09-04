# Tasks

- [x] Task 1: 修复 webview_bridge.py — get_workspace_projects() 后台线程化
  - [x] SubTask 1.1: 引入 concurrent.futures.ThreadPoolExecutor，在 __init__ 中创建 executor 实例
  - [x] SubTask 1.2: 创建 _run_in_thread() 辅助方法，将耗时操作提交到后台线程执行
  - [x] SubTask 1.3: 将 get_workspace_projects() 改为通过 executor.submit + result(timeout=30) 执行
  - [x] SubTask 1.4: 确保异常情况下返回 error dict 而非挂起

- [x] Task 2: 修复 path_resolver.py — _scan_change_dir 增加深度限制
  - [x] SubTask 2.1: _scan_change_dir 新增 max_depth 参数（默认3）
  - [x] SubTask 2.2: 递归调用前检查 depth < max_depth
  - [x] SubTask 2.3: scan_change_files 传递 max_depth 给 _scan_change_dir

- [x] Task 3: 修复 app.js — 初始化链 try-catch 保护
  - [x] SubTask 3.1: initSpecConstants() 调用外包 try-catch，失败时 console.warn 并继续
  - [x] SubTask 3.2: getWorkspaceInfo() 调用外包 try-catch，失败时走未设置工作空间分支

- [x] Task 4: 修复 api.js — _ensureReady() 超时保护
  - [x] SubTask 4.1: _ensureReady() 新增 10s Promise.race 超时
  - [x] SubTask 4.2: 超时后尝试直接检查 window.pywebview.api 可用性

- [x] Task 5: 更新测试适配异步行为
  - [x] SubTask 5.1: test_webview_bridge.py 适配 get_workspace_projects 现在是异步的（无需修改，ThreadPoolExecutor在测试中正常工作）
  - [x] SubTask 5.2: run_e2e.py MockBridge 确认无需修改（纯 Python 层 mock 不受影响）

- [x] Task 6: 运行全量测试验证无回归
  - [x] SubTask 6.1: 运行 pytest (61项) — 61/61 PASSED
  - [x] SubTask 6.2: 运行 run_e2e.py --no-gui (117项) — 117/117 PASSED
  - [x] SubTask 6.3: 确认全部通过零回归

# Task Dependencies

- [Task 1] 无依赖，可立即开始
- [Task 2] 无依赖，可立即开始
- [Task 3] 无依赖，可立即开始
- [Task 4] 无依赖，可立即开始
- [Task 5] 依赖 [Task 1] (测试适配需基于实际代码改动)
- [Task 6] 依赖 [Task 1-5 全部完成
- Task 1-4 可并行执行；Task 5-6 串行
