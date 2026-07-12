# auto-pm 前后端分离可行性方案 Spec

## Why

auto-pm 当前是 Python + QML 单体架构，前后端通过 Qt Signal/Slot 在进程内通信。用户希望将后端（Trae 负责）与前端（Codex 负责）解耦——后端提供 REST API + 接口文档，前端独立消费 API。本 spec 评估此方案的可行性、所需改造、风险与分阶段实施路径。

## 当前架构分析

### 现有分层

```
QML 前端 (auto_pm/ui/qml/)
  ├── views/       (10 个页面)
  ├── components/  (20+ 组件)
  ├── dialogs/     (16 个对话框)
  └── theme/       (主题系统)
        │
        │ Qt Signal/Slot (context property 注入)
        ▼
Bridge 层 (auto_pm/ui/qml/bridges/)
  ├── workbench_bridge.py  (17 个 @Slot)
  ├── change_bridge.py
  ├── spec_bridge.py
  ├── delivery_bridge.py
  └── system_bridge.py
        │
        │ Python 方法调用
        ▼
Facade 层 (auto_pm/application/)
  ├── workbench_facade.py
  ├── change_facade.py
  ├── spec_facade.py
  ├── delivery_facade.py
  └── system_facade.py
        │
        │ 聚合调用
        ▼
Service 层 (auto_pm/core/, auto_pm/change/, auto_pm/spec/, auto_pm/plc/)
  ├── ProjectService, ChangeService, DashboardService 等 10+ 个 Service
  └── DB 层 (auto_pm/db/) + 模型层 (auto_pm/models/)
```

### 关键数据流

1. **QML → Python**: QML 调用 Bridge 的 `@Slot` 方法 → Bridge 调用 Facade → Facade 调用 Service → 返回 `CommandResult`/`QueryResult`
2. **Python → QML**: Service 结果通过 Bridge 的 `Signal` 发射 → QML 通过 property binding 自动更新 UI
3. **DTO 层**: `auto_pm/ui/contracts/dto/` 定义了 Python 与 QML 之间的数据结构（dataclass → dict → QML `QVariant`）

### 现有 API 接口盘点（5 个域，约 80+ 个 Slot 方法）

| 域 | Bridge | Slot 方法数 | 涉及 Service |
|-----|--------|------------|-------------|
| Workbench | workbench_bridge.py | 17 | ProjectService, DashboardService, TemplateService, AssetSummaryService |
| Change | change_bridge.py | ~20 | ChangeService, LedgerReconciler |
| Spec | spec_bridge.py | ~20 | SpecCheckService, SpecCenterService, IndexService, ReportService, FrontmatterService |
| Delivery | delivery_bridge.py | ~10 | DocRefreshService, ReportService |
| System | system_bridge.py | ~10 | PmSessionService, TemplateService |

## What Changes

### 方案概述

将 auto-pm 拆分为两个独立进程：

1. **auto-pm-server**（后端，Trae 负责）
   - 基于 FastAPI 的 REST API 服务器
   - 复用现有 Service/Facade 层，不修改核心业务逻辑
   - 自动生成 OpenAPI 接口文档（FastAPI 内置）
   - 提供 WebSocket 端点用于实时推送（替代 Signal 机制）

2. **auto-pm-client**（前端，Codex 负责）
   - 可独立运行的 QML 前端（或 Web 前端）
   - 通过 HTTP/WebSocket 与后端通信
   - 移除所有 Bridge/Facade 直接依赖

### 项目结构变更

```
SW-2026-008_auto-pm_自动化项目管理工具/
├── server/                      # 新增：后端 API 服务器
│   ├── __init__.py
│   ├── main.py                  # FastAPI 应用入口
│   ├── api/                     # API 路由层
│   │   ├── __init__.py
│   │   ├── workbench.py         # /api/workbench/*
│   │   ├── change.py            # /api/change/*
│   │   ├── spec.py              # /api/spec/*
│   │   ├── delivery.py          # /api/delivery/*
│   │   └── system.py            # /api/system/*
│   ├── schemas/                 # Pydantic 请求/响应模型
│   │   ├── __init__.py
│   │   ├── workbench.py
│   │   ├── change.py
│   │   ├── spec.py
│   │   ├── delivery.py
│   │   └── system.py
│   ├── dependencies.py          # FastAPI 依赖注入（复用 Service 容器）
│   └── websocket.py             # WebSocket 实时推送
├── client/                      # 新增：独立前端
│   ├── src/                     # QML 源码（从 auto_pm/ui/qml/ 迁移）
│   ├── api/                     # API 客户端封装
│   │   ├── client.ts            # HTTP 客户端（TypeScript/JS）
│   │   └── types.ts             # API 类型定义
│   └── package.json
├── auto_pm/                     # 保留：核心业务逻辑（Service 层）
│   ├── core/                    # 不变
│   ├── change/                  # 不变
│   ├── spec/                    # 不变
│   ├── plc/                     # 不变
│   ├── models/                  # 不变
│   ├── db/                      # 不变
│   ├── cli/                     # 保留 CLI 入口
│   ├── application/             # Facade 层保留（供 API 路由复用）
│   └── ui/                      # 逐步废弃
│       ├── contracts/dto/       # DTO 迁移到 server/schemas/
│       └── qml/                 # QML 迁移到 client/src/
└── pyproject.toml               # 新增 server 依赖（fastapi, uvicorn）
```

### 关键技术决策

1. **后端框架**: FastAPI（自动生成 OpenAPI 文档，Pydantic 原生支持，与现有 pydantic 依赖一致）
2. **前端通信**: 
   - 查询类操作 → HTTP GET（REST）
   - 命令类操作 → HTTP POST/PUT/DELETE（REST）
   - 实时更新 → WebSocket（替代 Qt Signal）
3. **API 契约**: OpenAPI 3.0 规范，由 FastAPI 自动生成，作为 Trae 和 Codex 的接口契约
4. **前端技术栈选项**:
   - **选项 A（推荐）**: 保留 QML + 新增 JS API 客户端层（QML 支持 JavaScript/XMLHttpRequest）
   - **选项 B**: 迁移到 Web 前端（React/Vue），通过 WebView 或独立浏览器运行
   - **选项 C**: 迁移到 Electron + Web 前端

## Impact

- Affected specs: 全部 5 个域（Workbench, Change, Spec, Delivery, System）
- Affected code: 
  - `auto_pm/ui/qml/bridges/` → 替换为 HTTP API 客户端
  - `auto_pm/ui/qml_main_window.py` → 拆分为 server main.py + client 入口
  - `auto_pm/ui/contracts/` → 迁移到 server/schemas/
  - `auto_pm/application/` → 保留，API 路由复用
  - **BREAKING**: QML 中所有 `bridge.xxx()` 调用需替换为 HTTP 请求
  - **BREAKING**: 移除 Qt Signal 依赖，改用 WebSocket 推送

## ADDED Requirements

### Requirement: REST API Server
系统 SHALL 提供基于 FastAPI 的 REST API 服务器，暴露所有业务功能。

#### Scenario: 启动后端服务
- **WHEN** 用户执行 `auto-pm server --port 8000`
- **THEN** FastAPI 服务器在指定端口启动，并输出 OpenAPI 文档地址

#### Scenario: 查询项目列表
- **WHEN** 前端发送 `GET /api/workbench/projects`
- **THEN** 返回项目列表 JSON（含 project_id, name, stack, phase, open_change_count 等）

#### Scenario: 创建项目
- **WHEN** 前端发送 `POST /api/workbench/projects` 附带项目信息
- **THEN** 后端创建项目目录结构，返回项目详情，并通过 WebSocket 推送 `project_created` 事件

### Requirement: OpenAPI 接口文档
系统 SHALL 自动生成 OpenAPI 3.0 规范的接口文档。

#### Scenario: 访问接口文档
- **WHEN** 开发者访问 `http://localhost:8000/docs`
- **THEN** 显示 Swagger UI 交互式文档，包含所有 API 端点的请求/响应 schema

### Requirement: WebSocket 实时推送
系统 SHALL 通过 WebSocket 推送状态变更事件，替代 Qt Signal 机制。

#### Scenario: 项目变更通知
- **WHEN** 后端检测到项目状态变更（如新建/删除项目）
- **THEN** 通过 WebSocket 向所有连接的客户端推送 `project_changed` 事件

### Requirement: 前端独立运行
前端 SHALL 可以独立于后端启动，通过配置的 API 地址连接后端。

#### Scenario: 前端连接后端
- **WHEN** 前端启动时配置 `API_BASE_URL=http://localhost:8000`
- **THEN** 前端所有数据请求通过 HTTP 发送到该地址，WebSocket 连接到 `ws://localhost:8000/ws`

## MODIFIED Requirements

### Requirement: CLI 入口
CLI 入口 SHALL 新增 `server` 子命令启动 API 服务器，`gui` 子命令行为不变。

#### Scenario: 启动 GUI
- **WHEN** 用户执行 `auto-pm gui`
- **THEN** 启动 QML 前端（若已拆分，则启动独立客户端，自动启动后端服务）

## 风险评估

### 高风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| **QML 的 Qt 耦合** | QML 深度依赖 Qt 的 Signal/Slot/Property 绑定，HTTP 异步模型与 QML 声明式绑定不兼容 | 在 QML 中封装 JS API 客户端层，使用 Timer 轮询 + WebSocket 事件驱动替代 property binding |
| **性能退化** | 进程内调用（微秒级）→ HTTP 调用（毫秒级），大数据量场景（如变量表编辑器）可能卡顿 | 对变量表等大数据接口使用分页/流式传输；WebSocket 保持长连接减少握手开销 |
| **API 契约漂移** | Trae 和 Codex 独立开发，接口定义可能不一致 | FastAPI 自动生成 OpenAPI 文档作为契约；使用 Pydantic schema 确保类型安全；CI 中加入契约测试 |
| **文件系统访问** | 当前后端直接读写项目文件（Markdown、PLC 源码等），前端分离后无法直接访问文件系统 | 后端提供文件内容读写 API；文件选择通过后端 API 返回路径列表 |

### 中风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| **QML 组件重写量大** | 16 个对话框 + 20+ 组件全部需要改造 API 调用方式 | 分阶段迁移，先迁移核心页面（ProjectList、ChangeCenter），再迁移对话框 |
| **WebSocket 代替 Signal 复杂度** | 当前 Signal 是 Qt 原生机制，WebSocket 需要手动管理连接/重连/心跳 | 封装 WebSocket 管理模块，自动重连 + 心跳检测 |
| **双工具协作成本** | Trae 和 Codex 需要协调开发节奏和接口变更 | 以 OpenAPI 文档为单一真源，接口变更走变更单流程 |

### 低风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| **CLI 功能不受影响** | CLI 直接调用 Service 层，不经过 Bridge | 无需改造 |
| **现有测试兼容性** | 单元测试不依赖 UI，集成测试可能需要适配 | 后端 API 测试用 FastAPI TestClient；前端测试用 QML TestCase |

## 分阶段实施建议

### 阶段 1: API 化（2-3 周，Trae 主导）
- 搭建 FastAPI 服务器骨架
- 将 5 个域的 Bridge Slot 方法逐一映射为 REST API 端点
- 生成 OpenAPI 文档
- 编写 API 集成测试

### 阶段 2: 前端适配（2-3 周，Codex 主导）
- 基于 OpenAPI 文档实现 JS API 客户端
- 改造 QML 核心页面（ProjectListView → ChangeCenterView → SpecCenterView）
- 实现 WebSocket 事件驱动

### 阶段 3: 全量迁移 + 清理（1-2 周）
- 迁移剩余页面和对话框
- 移除 Bridge/Facade 层（如果不再需要）
- 清理 `auto_pm/ui/` 目录

## 推荐方案总结

**推荐选项 A（QML + JS API 客户端）**，理由：
1. 保留现有 QML UI 投资（10 页面 + 36 组件/对话框），避免从零重写
2. QML 原生支持 JavaScript 和 XMLHttpRequest，可以无缝添加 HTTP 调用层
3. 后端 Service 层零改动，仅新增 API 路由层
4. 如果未来 QML 不再满足需求，API 层已就绪，可平滑迁移到 Web 前端

**不推荐选项 B/C（Web 前端/Electron）**，理由：
- 需要完全重写 UI，工作量巨大
- 当前项目是桌面工具，Electron 增加约 100MB 包体积
- QML 在桌面端的原生体验（性能、系统集成）优于 Web 技术