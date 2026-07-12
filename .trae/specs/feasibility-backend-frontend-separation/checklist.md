# Checklist

## 阶段 1: API 化

- [ ] FastAPI 服务可启动（`auto-pm server --port 8000`）
- [ ] `/docs` 展示完整的 OpenAPI 文档（5 个域的所有端点）
- [ ] `GET /api/workbench/projects` 返回项目列表
- [ ] `POST /api/workbench/projects` 创建新项目
- [ ] `GET /api/change/{project_id}/changes` 返回变更单列表
- [ ] `POST /api/change/{project_id}/changes` 创建变更单
- [ ] Spec 域 API（check、index、frontmatter、report）可正常调用
- [ ] Delivery 域 API（doc_refresh、report）可正常调用
- [ ] System 域 API（settings、pm_session）可正常调用
- [ ] WebSocket `/ws` 端点可连接并接收事件推送
- [ ] 所有 API 端点有对应的 Pydantic schema 定义
- [ ] 所有 API 集成测试通过

## 阶段 2: 前端适配

- [ ] QML API 客户端封装完成（HTTP + WebSocket）
- [ ] ProjectListView 通过 API 加载项目列表
- [ ] ChangeCenterView 通过 API 管理变更单
- [ ] SpecCenterView 通过 API 执行规范检查
- [ ] PlatformDashboardView 通过 API 获取驾驶舱数据
- [ ] WorkspaceView 通过 API 获取项目工作区数据
- [ ] 16 个对话框通过 API 完成 CRUD 操作
- [ ] VarTableEditorView 通过 API 读写变量表数据
- [ ] WebSocket 事件驱动 UI 更新（替代 Signal 机制）
- [ ] `auto-pm gui` 自动启动后端 + 前端
- [ ] 前端独立运行时可连接远程后端

## 阶段 3: 清理

- [ ] `auto_pm/ui/qml/bridges/` 目录已移除
- [ ] `auto_pm/ui/registry.py` 已移除
- [ ] `auto_pm/ui/qml_main_window.py` 已移除
- [ ] 旧 DTO 文件已清理
- [ ] 现有 CLI 功能不受影响（project, change, spec, plc 等子命令）
- [ ] 现有单元测试全部通过
- [ ] 无 import 残留引用旧模块