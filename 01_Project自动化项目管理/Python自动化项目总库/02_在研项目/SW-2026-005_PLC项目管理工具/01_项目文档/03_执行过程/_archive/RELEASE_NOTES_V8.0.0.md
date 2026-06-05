# 发布说明 — V8.0.0 GUI 数据流修复

> **项目**: SW-2026-005 PLC项目管理工具
> **日期**: 2026-06-03
> **类型**: hotfix

## 问题背景

V7.0.0 全栈重构后，工作空间可以挂载打开，但 GUI 仅显示项目名称，所有详细数据（健康度、文档完成度、规范合规率、统计信息等）均不显示。

## 修复内容

### P0: 状态管理 Proxy 桥接 (store.js)
- **根因**: `store.js` 使用 `Object.defineProperty` 定义 `window.state` 为只读 getter，但 `ipc.js`/`navigation.js`/`dashboard.js` 等所有 JS 文件仍使用 `state.xxx = value` 直接赋值语法，导致状态变更静默丢失
- **修复**: 改用 ES6 Proxy 实现 Store ↔ state 双向桥接，所有 `state.xxx = value` 自动转换为 `Store.set('xxx', value)`

### P1: IPC 事件推送 (webview_window.py)
- **根因**: `mount_workspace` 成功后不发送 `workspace_opened` 事件，前端 `navigation.js` 的 `__ipc_recv` 包装器无法触发 UI 更新
- **修复**: 新增 `_EVENT_MAP` 机制，在 `_route()` 方法中检测成功响应后自动推送对应事件

### P1: project.path 赋值缺失 (project_service.py)
- **根因**: `load_project_from_path()` 加载项目后未设置 `project.path` 为实际路径，导致 `_enrich_project_metadata` 扫描错误的目录，Dashboard 健康度计算返回空
- **修复**: 在 `load_from_file` 后显式设置 `project.path = str(project_root)`

### P2: get_project_overview 数据格式 (project_service.py)
- **修复**: 返回格式增加 `business_identity`、`tech_environment`、`engineering_scale`、`project_status`、`change_ledger` 字段，与前端 `loadProjectOverview()` 期望一致

### P2: list_directory_tree 嵌套结构 (project_service.py)
- **修复**: 从扁平列表改为嵌套树结构（根节点含 `children` 数组，使用 `is_dir` 布尔字段）

### P2: get_dashboard_stats 传参 (ipc.js)
- **修复**: `ipcGetDashboardStats()` 调用时传入 `state.workspacePath`

## 测试覆盖

- 新增 `tests/test_gui_ipc.py`: 14 个 IPC 数据流集成测试
- 新增 `tests/test_frontend_store.py`: 10 个前端 Store 契约测试
- 回归测试: 815 passed, 16 skipped, 0 failed

## 影响范围

| 文件 | 变更类型 |
|------|---------|
| `ui_prototype/js/store.js` | 修改 — Proxy 替代 getter |
| `ui_prototype/js/ipc.js` | 修改 — dashboard_stats 传参 |
| `src/ui/webview_window.py` | 修改 — 自动事件推送 |
| `src/services/project_service.py` | 修改 — project.path + 数据格式 + 嵌套树 |
| `01_项目文档/02_规划过程/007_架构设计文档_ARCH-V8.0.0.md` | 更新 |
| `tests/test_gui_ipc.py` | 新增 |
| `tests/test_frontend_store.py` | 新增 |

## 升级说明

- 无破坏性变更，所有 API 向后兼容
- 无需数据迁移
- 前端 `state.xxx = value` 语法保持不变