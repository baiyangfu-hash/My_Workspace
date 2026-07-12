# Tasks

## 阶段 1: API 化（后端，Trae 主导）

- [ ] Task 1: 搭建 FastAPI 服务器骨架
  - [ ] 1.1 在 `pyproject.toml` 中添加 `fastapi` 和 `uvicorn` 依赖
  - [ ] 1.2 创建 `server/` 目录结构（main.py, api/, schemas/, dependencies.py, websocket.py）
  - [ ] 1.3 实现 `server/main.py`：FastAPI 应用入口，挂载路由，配置 CORS
  - [ ] 1.4 实现 `server/dependencies.py`：复用现有 Service 容器，提供 FastAPI `Depends` 注入
  - [ ] 1.5 新增 CLI 命令 `auto-pm server --port 8000`，启动 uvicorn

- [ ] Task 2: 实现 Workbench 域 API
  - [ ] 2.1 创建 `server/schemas/workbench.py`：Pydantic 请求/响应模型
  - [ ] 2.2 创建 `server/api/workbench.py`：映射 WorkbenchBridge 的 17 个 Slot 为 REST 端点
  - [ ] 2.3 验证：`GET /docs` 可查看 Workbench API 文档

- [ ] Task 3: 实现 Change 域 API
  - [ ] 3.1 创建 `server/schemas/change.py`：Pydantic 请求/响应模型
  - [ ] 3.2 创建 `server/api/change.py`：映射 ChangeBridge 的 Slot 为 REST 端点
  - [ ] 3.3 验证：API 文档完整

- [ ] Task 4: 实现 Spec 域 API
  - [ ] 4.1 创建 `server/schemas/spec.py`
  - [ ] 4.2 创建 `server/api/spec.py`
  - [ ] 4.3 验证：API 文档完整

- [ ] Task 5: 实现 Delivery 和 System 域 API
  - [ ] 5.1 创建 `server/schemas/delivery.py` + `server/api/delivery.py`
  - [ ] 5.2 创建 `server/schemas/system.py` + `server/api/system.py`
  - [ ] 5.3 验证：API 文档完整

- [ ] Task 6: 实现 WebSocket 实时推送
  - [ ] 6.1 创建 `server/websocket.py`：WebSocket 连接管理 + 事件广播
  - [ ] 6.2 在 Facade 层关键操作后触发 WebSocket 事件（project_created, change_updated 等）
  - [ ] 6.3 验证：WebSocket 连接可收发消息

- [ ] Task 7: 编写 API 集成测试
  - [ ] 7.1 使用 FastAPI TestClient 编写 Workbench API 测试
  - [ ] 7.2 编写 Change/Spec/Delivery/System API 测试
  - [ ] 7.3 验证：所有 API 测试通过

## 阶段 2: 前端适配（Codex 主导）

- [ ] Task 8: 实现 QML API 客户端层
  - [ ] 8.1 创建 `client/src/api/ApiClient.qml`：封装 XMLHttpRequest 的 HTTP 客户端
  - [ ] 8.2 创建 `client/src/api/ApiTypes.qml`：JS 类型定义（对应后端 Pydantic schema）
  - [ ] 8.3 实现 WebSocket 客户端封装（自动重连、心跳）

- [ ] Task 9: 迁移核心页面
  - [ ] 9.1 改造 `ProjectListView.qml`：Bridge 调用 → API 客户端调用
  - [ ] 9.2 改造 `ChangeCenterView.qml`
  - [ ] 9.3 改造 `SpecCenterView.qml`
  - [ ] 9.4 改造 `PlatformDashboardView.qml`

- [ ] Task 10: 迁移工作区页面和对话框
  - [ ] 10.1 改造 `WorkspaceView.qml`、`DocBrowserView.qml`、`TemplateView.qml`
  - [ ] 10.2 改造 16 个对话框（NewProjectWizard, ChangeDialog 等）
  - [ ] 10.3 改造 `ReportView.qml`、`SettingsView.qml`、`VarTableEditorView.qml`

- [ ] Task 11: 实现独立前端启动
  - [ ] 11.1 创建 `client/` 目录的独立启动脚本
  - [ ] 11.2 实现 `auto-pm gui` 自动启动后端 + 前端
  - [ ] 11.3 验证：前端独立运行并可连接后端

## 阶段 3: 清理

- [ ] Task 12: 移除旧代码
  - [ ] 12.1 移除 `auto_pm/ui/qml/bridges/`（5 个 Bridge 文件）
  - [ ] 12.2 移除 `auto_pm/ui/registry.py`（FacadeRegistry）
  - [ ] 12.3 移除 `auto_pm/ui/qml_main_window.py`（旧 QML 入口）
  - [ ] 12.4 清理 `auto_pm/ui/contracts/` 中不再需要的 DTO

# Task Dependencies

- Task 2-5 依赖 Task 1（API 骨架）
- Task 6 依赖 Task 2-5（WebSocket 事件需在 API 操作中触发）
- Task 7 依赖 Task 2-6
- Task 8 依赖 Task 1（API 客户端需要知道后端地址和接口格式）
- Task 9-10 依赖 Task 8（API 客户端）
- Task 11 依赖 Task 9-10（所有页面迁移完成）
- Task 12 依赖 Task 11（清理在迁移完成后进行）
- Task 2-5 可并行执行
- Task 8 和 Task 2-7 可并行执行（前后端独立开发）