# SW-2026-005 Dashboard加载卡死修复 Spec

## Why

SW-2026-005 PLC项目管理工具启动后Dashboard页面永久显示"加载中..."，用户无法使用。根因是PyWebView主线程阻塞导致IPC死锁：后端`get_workspace_projects()`在Python主线程执行同步文件I/O扫描，阻塞了PyWebView事件循环，导致IPC响应无法发送回WebView2前端。前端同时缺少防御性编程（无超时、无try-catch），故障表现被放大。

## What Changes

### A. 后端：Bridge API异步化（核心修复）
- **BREAKING**: `webview_bridge.py` 的 `get_workspace_projects()` 改为在后台线程执行，通过 `concurrent.futures.ThreadPoolExecutor` 异步返回结果
- `path_resolver.py` 的 `_scan_change_dir()` 增加 `max_depth=3` 参数，防止无限递归

### B. 前端：防御性编程
- `app.js`: `initSpecConstants()` 外包 try-catch，失败时不阻断初始化链
- `api.js`: `_ensureReady()` 增加 10s 超时保护

## Impact

- Affected code: webview_bridge.py, path_resolver.py, app.js, api.js
- Affected tests: test_webview_bridge.py (需适配异步行为), run_e2e.py (MockBridge需适配)

## ADDED Requirements

### Requirement: Bridge API 后台线程执行

系统 SHALL 将耗时的 Bridge API 方法（特别是 `get_workspace_projects`）在后台线程执行，避免阻塞 PyWebView 主线程事件循环。

#### Scenario: 大工作空间扫描不卡死UI
- **WHEN** 用户选择包含多个项目的工作空间并打开总览页
- **THEN** 页面在3秒内显示"加载中..."后渲染出项目卡片（或空态提示），不会永久转圈

### Requirement: 变更单目录递归深度限制

系统 SHALL 限制变更单目录的递归扫描深度不超过3层。

#### Scenario: 深层嵌套目录不导致性能退化
- **WHEN** 项目变更管理目录下存在深层嵌套子目录
- **THEN** 扫描在合理时间内完成（<2s），不会无限递归

### Requirement: 前端初始化容错

系统 SHALL 在前端初始化阶段对每个异步步骤提供 try-catch 保护，单个步骤失败不应阻断后续初始化。

#### Scenario: 规范常量同步失败不影响页面加载
- **WHEN** `initSpecConstants()` 因 Bridge 不可用而抛异常
- **THEN** 使用默认值继续初始化，页面正常渲染

### Requirement: pywebviewready 超时保护

系统 SHALL 为 `_ensureReady()` 提供 10s 超时保护。

#### Scenario: pywebviewready 事件丢失
- **WHEN** `pywebviewready` 事件在 10s 内未触发
- **THEN** 自动超时并尝试直接访问 api 对象，或抛出明确错误提示
