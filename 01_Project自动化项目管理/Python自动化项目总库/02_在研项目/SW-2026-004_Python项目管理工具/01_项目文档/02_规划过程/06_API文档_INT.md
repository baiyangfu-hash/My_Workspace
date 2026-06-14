# SW-2026-004 Python项目管理工具 - API文档

## 1. 文档基础信息

**文档标题**：SW-2026-004 Python项目管理工具API文档
**文档版本**：INT V2.8.0
**编制日期**：2026-06-14
**编制人**：技术负责人
**审核人**：技术负责人
**项目编号**：SW-2026-004
**迭代版本**：V2.8.0

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 | 详细说明 |
|--------|----------|--------|----------|----------|
| INT V1.0.0 | 初始版本 | 技术负责人 | 2026-03-12 | 创建API文档 |
| INT V1.0.3 | 更新版本号和审核人 | 技术负责人 | 2026-03-15 | 统一版本号为V1.0.3 |
| INT V2.7.0 | 版本号同步更新 | 技术负责人 | 2026-06-14 | 版本号对齐V2.7.0；健康检查版本号更新 |
| INT V2.6.0 | 重构为实际API路由 | 技术负责人 | 2026-06-12 | 基于 src/api/app.py 实际路由重写；认证方式更新为JWT；新增defects/libraries/library-changes/library-dashboard Blueprint端点；统一响应格式增加request_id字段 |

## 3. 接口概述

### 3.1 文档目的

本文档描述SW-2026-004 Python项目管理工具的REST API接口，包括接口功能、请求参数、响应格式，供前端开发和第三方集成使用。

### 3.2 接口分类

| 分类 | 说明 | Blueprint |
|------|------|-----------|
| 认证 | 用户登录与JWT令牌管理 | 内置路由 |
| 公共 | 健康检查 | 内置路由 |
| 项目管理 | 项目CRUD、规范检查、报告生成 | `/api/v1/projects` |
| 模板管理 | 模板CRUD、导入导出、结构校验 | `/api/v1/templates` |
| 插件管理 | 插件安装/启用/禁用/卸载/配置/执行 | `/api/v1/plugins` |
| 规范管理 | 规范CRUD、内容查询 | `/api/v1/specs` |
| 总库管理 | 总库CRUD、项目管理、目录扫描、统计 | `/api/v1/libraries` |
| 总库变更 | 变更CRUD、审批/驳回、统计 | `/api/v1/library-changes` |
| 总库仪表盘 | 总览、趋势、健康度、报告生成 | `/api/v1/library-dashboard` |
| 缺陷管理 | 缺陷CRUD、状态变更、分配/解决、统计 | `/api/v1/defects` |

### 3.3 技术选型

| 项目 | 说明 |
|------|------|
| 框架 | Flask ≥2.3.0 |
| 认证 | JWT (Bearer Token)，HS256算法 |
| 数据格式 | JSON |
| 跨域 | Flask-CORS |

## 4. 接口基础信息

### 4.1 基础URL

```
http://localhost:5000/api/v1
```

> 主机和端口可通过 `config/api_config.json` 中的 `api.host` / `api.port` 配置。

### 4.2 认证方式

API采用JWT Bearer Token认证。除 `/api/v1/login` 和 `/api/v1/health` 外，受保护端点需在请求头中携带Token：

```
Authorization: Bearer <token>
```

Token获取方式：调用 `/api/v1/login`，请求体 `{"username": "<用户名>", "password": "<密码>"}`，成功返回 `token` 字段。

Token有效时长由 `settings.security.api_token_expire_hours` 配置（默认24小时）。

### 4.3 统一响应格式

**成功响应**（所有端点）：

```json
{
  "code": 200,
  "message": "操作描述",
  "data": { "具体数据" },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

**失败响应**（错误码 ≥ 400）：

```json
{
  "code": 400,
  "message": "错误描述",
  "data": null,
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 4.4 错误码

| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| 200 | 200 | 操作成功（GET/PUT/DELETE） |
| 201 | 201 | 创建成功（POST） |
| 400 | 400 | 请求参数错误 / 缺少必填字段 |
| 401 | 401 | 未认证（Token缺失/过期/无效） |
| 403 | 403 | 权限不足（角色不满足 `role_required`） |
| 404 | 404 | 资源不存在 |
| 500 | 500 | 服务器内部错误 |

## 5. 认证接口

### 5.1 用户登录

**接口URL**：`/api/v1/login`

**请求方法**：POST

**认证**：无需认证

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例**：
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**成功响应**（200）：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "username": "admin",
      "role": "admin"
    }
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

**失败响应**（401）：
```json
{
  "code": 401,
  "message": "用户名或密码错误",
  "data": null,
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

## 6. 公共接口

### 6.1 健康检查

**接口URL**：`/api/v1/health`

**请求方法**：GET

**认证**：无需认证

**响应示例**：
```json
{
  "status": "ok",
  "version": "2.6.0",
  "timestamp": "2026-06-12T10:00:00.000000"
}
```

## 7. 项目管理API — `/api/v1/projects`

### 7.1 创建项目

**接口URL**：`/api/v1/projects`

**请求方法**：POST

**认证**：需要（Bearer Token）

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| business_line | string | 是 | 业务线代码（如 DJ/ZD/XT） |
| name | string | 是 | 项目名称 |
| template_id | string | 是 | 模板ID |
| manager | string | 否 | 项目负责人 |
| description | string | 否 | 项目描述 |
| path | string | 否 | 自定义项目路径 |

**请求示例**：
```json
{
  "business_line": "DJ",
  "name": "某生产线PLC项目",
  "template_id": "TPL-SINGLE-PLC-001",
  "manager": "张三",
  "description": "某生产线PLC控制系统"
}
```

**成功响应**（201）：
```json
{
  "code": 201,
  "message": "项目创建成功",
  "data": {
    "project": {
      "id": "PROJ-001",
      "code": "DJ-2026-001",
      "name": "某生产线PLC项目",
      "business_line": "DJ",
      "manager": "张三",
      "description": "某生产线PLC控制系统",
      "status": "active",
      "created_at": "2026-06-12T10:00:00Z",
      "updated_at": "2026-06-12T10:00:00Z"
    }
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 7.2 获取项目列表

**接口URL**：`/api/v1/projects`

**请求方法**：GET

**认证**：需要

**查询参数**：

| 参数名 | 类型 | 必填 | 描述 | 默认值 |
|--------|------|------|------|--------|
| status | string | 否 | 项目状态过滤 | - |
| business_line | string | 否 | 业务线过滤 | - |
| keyword | string | 否 | 搜索关键词 | - |
| page | int | 否 | 页码 | 1 |
| size | int | 否 | 每页数量 | 20 |

**响应示例**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "projects": [
      {
        "id": "PROJ-001",
        "code": "DJ-2026-001",
        "name": "某生产线PLC项目",
        "business_line": "DJ",
        "manager": "张三",
        "status": "active",
        "created_at": "2026-06-12T10:00:00Z"
      }
    ],
    "pagination": {
      "total": 1,
      "page": 1,
      "size": 20,
      "pages": 1
    }
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 7.3 获取项目详情

**接口URL**：`/api/v1/projects/{project_id}`

**请求方法**：GET

**认证**：需要

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |

**响应示例**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "project": {
      "id": "PROJ-001",
      "code": "DJ-2026-001",
      "name": "某生产线PLC项目",
      "business_line": "DJ",
      "manager": "张三",
      "description": "某生产线PLC控制系统",
      "status": "active",
      "created_at": "2026-06-12T10:00:00Z",
      "updated_at": "2026-06-12T10:00:00Z",
      "statistics": {}
    }
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 7.4 更新项目信息

**接口URL**：`/api/v1/projects/{project_id}`

**请求方法**：PUT

**认证**：需要

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 否 | 项目名称 |
| manager | string | 否 | 项目负责人 |
| description | string | 否 | 项目描述 |
| status | string | 否 | 项目状态 |

**请求示例**：
```json
{
  "name": "更新后的项目名称",
  "manager": "李四",
  "description": "更新后的描述"
}
```

**成功响应**（200）：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "project": {
      "id": "PROJ-001",
      "code": "DJ-2026-001",
      "name": "更新后的项目名称",
      "business_line": "DJ",
      "manager": "李四",
      "description": "更新后的描述",
      "status": "active",
      "created_at": "2026-06-12T10:00:00Z",
      "updated_at": "2026-06-12T10:30:00Z"
    }
  },
  "timestamp": "2026-06-12T10:30:00.000000",
  "request_id": "req-20260612-d4e5f6"
}
```

### 7.5 删除项目

**接口URL**：`/api/v1/projects/{project_id}`

**请求方法**：DELETE

**认证**：需要

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |

**成功响应**（200）：
```json
{
  "code": 200,
  "message": "删除成功",
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 7.6 生成项目编号

**接口URL**：`/api/v1/projects/generate-code`

**请求方法**：GET

**认证**：需要

**查询参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| business_line | string | 是 | 业务线代码 |

**响应示例**：
```json
{
  "code": 200,
  "message": "生成成功",
  "data": {
    "project_code": "DJ-2026-001"
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 7.7 执行项目规范检查

**接口URL**：`/api/v1/projects/{project_id}/check`

**请求方法**：POST

**认证**：需要

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| check_types | array | 否 | 检查类型列表，如 `["structure", "naming", "code"]` |

**请求示例**：
```json
{
  "check_types": ["structure", "naming", "code"]
}
```

**成功响应**（200）：
```json
{
  "code": 200,
  "message": "检查完成",
  "data": {
    "report": {
      "total": 10,
      "passed": 8,
      "failed": 2,
      "details": []
    },
    "report_path": "data/reports/check_report_20260612.md"
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 7.8 生成项目报告

**接口URL**：`/api/v1/projects/{project_id}/report`

**请求方法**：POST

**认证**：需要

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |

**成功响应**（200）：
```json
{
  "code": 200,
  "message": "报告生成成功",
  "data": {
    "report_path": "data/reports/project_report_20260612.md"
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 7.9 获取项目统计信息

**接口URL**：`/api/v1/projects/statistics`

**请求方法**：GET

**认证**：需要

**响应示例**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total_projects": 10,
    "active_projects": 8,
    "completed_projects": 2,
    "projects_by_business": {
      "DJ": 5,
      "ZD": 3,
      "XT": 2
    }
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

## 8. 模板管理API — `/api/v1/templates`

### 8.1 获取模板列表

**URL**：`GET /api/v1/templates`

**查询参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| compiler | string | 否 | 编译器类型 |
| scene | string | 否 | 应用场景 |
| is_builtin | boolean | 否 | 是否内置模板 |

**响应示例**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "templates": [
      {
        "id": "TPL-SINGLE-PLC-001",
        "name": "单机PLC项目模板",
        "compiler": "Work3",
        "scene": "plc",
        "is_builtin": true,
        "created_at": "2026-06-12T10:00:00Z"
      }
    ],
    "total": 1
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 8.2 获取模板详情

**URL**：`GET /api/v1/templates/{template_id}`

**响应示例**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "template": {
      "id": "TPL-SINGLE-PLC-001",
      "name": "单机PLC项目模板",
      "compiler": "Work3",
      "scene": "plc",
      "is_builtin": true,
      "structure": {},
      "created_at": "2026-06-12T10:00:00Z",
      "updated_at": "2026-06-12T10:00:00Z"
    }
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 8.3 创建自定义模板

**URL**：`POST /api/v1/templates`

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 是 | 模板名称 |
| compiler | string | 是 | 编译器类型 |
| scene | string | 是 | 应用场景 |
| structure | object | 是 | 模板目录结构 |

**请求示例**：
```json
{
  "name": "自定义PLC模板",
  "compiler": "Work3",
  "scene": "plc",
  "structure": {
    "folders": [
      { "name": "02_PLC程序", "subfolders": [] },
      { "name": "03_HMI设计", "subfolders": [] }
    ]
  }
}
```

**成功响应**（201）：
```json
{
  "code": 201,
  "message": "模板创建成功",
  "data": {
    "template": {
      "id": "TPL-CUSTOM-001",
      "name": "自定义PLC模板",
      "compiler": "Work3",
      "scene": "plc",
      "is_builtin": false,
      "structure": {},
      "created_at": "2026-06-12T10:00:00Z"
    }
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 8.4 更新模板信息

**URL**：`PUT /api/v1/templates/{template_id}`

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 否 | 模板名称 |
| structure | object | 否 | 模板结构 |

### 8.5 删除模板

**URL**：`DELETE /api/v1/templates/{template_id}`

> 内置模板（is_builtin=true）不可删除。

### 8.6 导出模板

**URL**：`GET /api/v1/templates/{template_id}/export`

**响应示例**：
```json
{
  "code": 200,
  "message": "导出成功",
  "data": {
    "template_json": {
      "name": "单机PLC项目模板",
      "compiler": "Work3",
      "scene": "plc",
      "structure": {}
    }
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 8.7 导入模板

**URL**：`POST /api/v1/templates/import`

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| template_json | object | 是 | 模板JSON数据 |

### 8.8 验证模板结构

**URL**：`POST /api/v1/templates/validate`

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| structure | object | 是 | 模板结构 |

**响应示例**：
```json
{
  "code": 200,
  "message": "模板结构验证通过",
  "data": { "valid": true },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

## 9. 插件管理API — `/api/v1/plugins`

### 9.1 获取插件列表

**URL**：`GET /api/v1/plugins`

**查询参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| status | string | 否 | 插件状态过滤 |

**响应示例**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "plugins": [
      {
        "id": "PLUGIN-001",
        "name": "PLC变量表解析",
        "version": "1.0.0",
        "status": "enabled",
        "description": "解析PLC变量表文件"
      }
    ],
    "total": 1
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 9.2 安装插件

**URL**：`POST /api/v1/plugins/install`

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| plugin_path | string | 是 | 插件文件路径 |

**成功响应**（201）：
```json
{
  "code": 201,
  "message": "插件安装成功",
  "data": {
    "plugin": {
      "id": "PLUGIN-002",
      "name": "新插件",
      "version": "1.0.0",
      "status": "disabled"
    }
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 9.3 获取插件详情

**URL**：`GET /api/v1/plugins/{plugin_id}`

### 9.4 启用插件

**URL**：`PUT /api/v1/plugins/{plugin_id}/enable`

**响应示例**：
```json
{
  "code": 200,
  "message": "插件已启用",
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 9.5 禁用插件

**URL**：`PUT /api/v1/plugins/{plugin_id}/disable`

### 9.6 卸载插件

**URL**：`DELETE /api/v1/plugins/{plugin_id}/uninstall`

> 内置插件不可卸载。

### 9.7 执行插件功能

**URL**：`POST /api/v1/plugins/{plugin_id}/execute`

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| action | string | 是 | 执行动作 |
| params | object | 否 | 执行参数 |

### 9.8 更新插件配置

**URL**：`PUT /api/v1/plugins/{plugin_id}/config`

**请求体**：任意配置JSON对象。

## 10. 规范管理API — `/api/v1/specs`

### 10.1 获取规范列表

**URL**：`GET /api/v1/specs`

**查询参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| category | string | 否 | 规范分类 |
| keyword | string | 否 | 搜索关键词 |

**响应示例**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "specs": [
      {
        "id": "SPEC-001",
        "name": "905_SCL编程规范",
        "type": "plc",
        "description": "SCL编程风格与命名规范",
        "version": "V1.0.0"
      }
    ],
    "total": 1
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 10.2 获取规范详情

**URL**：`GET /api/v1/specs/{spec_id}`

### 10.3 获取规范内容

**URL**：`GET /api/v1/specs/{spec_id}/content`

**响应示例**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "content": "# 905 SCL编程规范\n\n..."
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 10.4 创建新规范

**URL**：`POST /api/v1/specs`

**成功响应**（201）。

## 11. 总库管理API — `/api/v1/libraries`

### 11.1 获取总库列表

**URL**：`GET /api/v1/libraries`

### 11.2 创建总库

**URL**：`POST /api/v1/libraries`

### 11.3 获取总库详情

**URL**：`GET /api/v1/libraries/{library_id}`

### 11.4 更新总库

**URL**：`PUT /api/v1/libraries/{library_id}`

### 11.5 删除总库

**URL**：`DELETE /api/v1/libraries/{library_id}`

### 11.6 获取总库下项目列表

**URL**：`GET /api/v1/libraries/{library_id}/projects`

### 11.7 向总库添加项目

**URL**：`POST /api/v1/libraries/{library_id}/projects`

### 11.8 从总库移除项目

**URL**：`DELETE /api/v1/libraries/{library_id}/projects/{project_id}`

### 11.9 获取总库目录分类

**URL**：`GET /api/v1/libraries/{library_id}/categories`

### 11.10 创建总库目录分类

**URL**：`POST /api/v1/libraries/{library_id}/categories`

### 11.11 扫描总库目录

**URL**：`POST /api/v1/libraries/{library_id}/scan`

### 11.12 总库统计

**URL**：`GET /api/v1/libraries/{library_id}/statistics`

## 12. 总库变更API — `/api/v1/library-changes`

### 12.1 获取变更列表

**URL**：`GET /api/v1/library-changes`

**响应示例**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "changes": [
      {
        "id": "CHANGE-001",
        "project_code": "DJ-2026-001",
        "type": "create",
        "description": "创建项目",
        "status": "pending",
        "created_at": "2026-06-12T10:00:00Z"
      }
    ]
  },
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 12.2 创建变更

**URL**：`POST /api/v1/library-changes`

### 12.3 获取变更详情

**URL**：`GET /api/v1/library-changes/{change_id}`

### 12.4 更新变更

**URL**：`PUT /api/v1/library-changes/{change_id}`

### 12.5 删除变更

**URL**：`DELETE /api/v1/library-changes/{change_id}`

### 12.6 审批变更

**URL**：`POST /api/v1/library-changes/{change_id}/approve`

**响应示例**：
```json
{
  "code": 200,
  "message": "变更已审批",
  "timestamp": "2026-06-12T10:00:00.000000",
  "request_id": "req-20260612-a1b2c3"
}
```

### 12.7 驳回变更

**URL**：`POST /api/v1/library-changes/{change_id}/reject`

### 12.8 变更统计

**URL**：`GET /api/v1/library-changes/statistics`

## 13. 总库仪表盘API — `/api/v1/library-dashboard`

### 13.1 仪表盘概览

**URL**：`GET /api/v1/library-dashboard/{library_id}/overview`

### 13.2 趋势数据

**URL**：`GET /api/v1/library-dashboard/{library_id}/trends`

### 13.3 健康度检查

**URL**：`GET /api/v1/library-dashboard/{library_id}/health`

### 13.4 生成概览报告

**URL**：`POST /api/v1/library-dashboard/{library_id}/reports/overview`

### 13.5 生成统计报告

**URL**：`POST /api/v1/library-dashboard/{library_id}/reports/statistics`

### 13.6 生成趋势报告

**URL**：`POST /api/v1/library-dashboard/{library_id}/reports/trend`

## 14. 缺陷管理API — `/api/v1/defects`

### 14.1 获取缺陷列表

**URL**：`GET /api/v1/defects`

**查询参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| status | string | 否 | 缺陷状态 |
| priority | string | 否 | 优先级 |
| severity | string | 否 | 严重程度 |
| project_id | int | 否 | 关联项目ID |
| library_id | int | 否 | 关联总库ID |
| reporter | string | 否 | 报告人 |
| assignee | string | 否 | 责任人 |
| keyword | string | 否 | 搜索关键词 |

### 14.2 创建缺陷

**URL**：`POST /api/v1/defects`

**请求体**（必填）：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| title | string | 是 | 缺陷标题 |
| description | string | 是 | 缺陷描述 |
| reporter | string | 是 | 报告人 |

**成功响应**（201）。

### 14.3 获取缺陷详情

**URL**：`GET /api/v1/defects/{defect_id}`

> 注意：defect_id 为整数类型。

### 14.4 更新缺陷

**URL**：`PUT /api/v1/defects/{defect_id}`

### 14.5 删除缺陷

**URL**：`DELETE /api/v1/defects/{defect_id}`

### 14.6 变更缺陷状态

**URL**：`PATCH /api/v1/defects/{defect_id}/status`

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| status | string | 是 | 新状态 |

### 14.7 分配缺陷

**URL**：`PATCH /api/v1/defects/{defect_id}/assign`

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| assignee | string | 是 | 责任人 |

### 14.8 解决缺陷

**URL**：`PATCH /api/v1/defects/{defect_id}/resolve`

**请求体**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| resolution | string | 是 | 解决方案 |
| fix_version | string | 是 | 修复版本 |

### 14.9 缺陷统计

**URL**：`GET /api/v1/defects/statistics`

### 14.10 按项目查询缺陷

**URL**：`GET /api/v1/defects/project/{project_id}`

### 14.11 按总库查询缺陷

**URL**：`GET /api/v1/defects/library/{library_id}`

### 14.12 搜索缺陷

**URL**：`GET /api/v1/defects/search?keyword={keyword}`

## 15. 接口扩展指南

### 15.1 添加新端点

1. 在 `src/api/routes/` 下创建新Blueprint模块
2. 在 `src/api/routes/__init__.py` 中注册Blueprint
3. 在 `src/api/app.py` 中调用 `app.register_blueprint`
4. 需要认证的端点使用 `@auth_required` 装饰器
5. 需要角色控制的端点叠加 `@role_required(["admin"])`

### 15.2 认证装饰器使用

```python
from src.api.auth import auth_required, role_required

@bp.route("/sensitive", methods=["GET"])
@auth_required
def sensitive_route():
    # g.username, g.user_role 可用
    pass

@bp.route("/admin-only", methods=["POST"])
@auth_required
@role_required(["admin"])
def admin_route():
    pass
```

### 15.3 性能建议

- 列表接口使用分页机制
- 频繁访问的数据考虑缓存
- 耗时操作采用异步处理

## 16. 附录

### 16.1 API路由速查表

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/login` | 用户登录 |
| GET | `/api/v1/health` | 健康检查 |
| GET/POST | `/api/v1/projects` | 项目列表/创建 |
| GET/PUT/DELETE | `/api/v1/projects/{id}` | 项目详情/更新/删除 |
| GET | `/api/v1/projects/generate-code` | 生成项目编号 |
| POST | `/api/v1/projects/{id}/check` | 规范检查 |
| POST | `/api/v1/projects/{id}/report` | 生成报告 |
| GET | `/api/v1/projects/statistics` | 项目统计 |
| GET/POST | `/api/v1/templates` | 模板列表/创建 |
| GET/PUT/DELETE | `/api/v1/templates/{id}` | 模板详情/更新/删除 |
| GET | `/api/v1/templates/{id}/export` | 导出模板 |
| POST | `/api/v1/templates/import` | 导入模板 |
| POST | `/api/v1/templates/validate` | 验证模板结构 |
| GET | `/api/v1/plugins` | 插件列表 |
| POST | `/api/v1/plugins/install` | 安装插件 |
| GET | `/api/v1/plugins/{id}` | 插件详情 |
| PUT | `/api/v1/plugins/{id}/enable` | 启用插件 |
| PUT | `/api/v1/plugins/{id}/disable` | 禁用插件 |
| DELETE | `/api/v1/plugins/{id}/uninstall` | 卸载插件 |
| POST | `/api/v1/plugins/{id}/execute` | 执行插件 |
| PUT | `/api/v1/plugins/{id}/config` | 更新插件配置 |
| GET/POST | `/api/v1/specs` | 规范列表/创建 |
| GET | `/api/v1/specs/{id}` | 规范详情 |
| GET | `/api/v1/specs/{id}/content` | 规范内容 |
| GET/POST | `/api/v1/libraries` | 总库列表/创建 |
| GET/PUT/DELETE | `/api/v1/libraries/{id}` | 总库详情/更新/删除 |
| GET/POST | `/api/v1/libraries/{id}/projects` | 总库项目列表/添加 |
| DELETE | `/api/v1/libraries/{id}/projects/{pid}` | 从总库移除项目 |
| GET/POST | `/api/v1/libraries/{id}/categories` | 目录分类 |
| POST | `/api/v1/libraries/{id}/scan` | 扫描目录 |
| GET | `/api/v1/libraries/{id}/statistics` | 总库统计 |
| GET/POST | `/api/v1/library-changes` | 变更列表/创建 |
| GET/PUT/DELETE | `/api/v1/library-changes/{id}` | 变更详情/更新/删除 |
| POST | `/api/v1/library-changes/{id}/approve` | 审批变更 |
| POST | `/api/v1/library-changes/{id}/reject` | 驳回变更 |
| GET | `/api/v1/library-changes/statistics` | 变更统计 |
| GET | `/api/v1/library-dashboard/{id}/overview` | 仪表盘概览 |
| GET | `/api/v1/library-dashboard/{id}/trends` | 趋势数据 |
| GET | `/api/v1/library-dashboard/{id}/health` | 健康度 |
| POST | `/api/v1/library-dashboard/{id}/reports/overview` | 生成概览报告 |
| POST | `/api/v1/library-dashboard/{id}/reports/statistics` | 生成统计报告 |
| POST | `/api/v1/library-dashboard/{id}/reports/trend` | 生成趋势报告 |
| GET/POST | `/api/v1/defects` | 缺陷列表/创建 |
| GET/PUT/DELETE | `/api/v1/defects/{id}` | 缺陷详情/更新/删除 |
| PATCH | `/api/v1/defects/{id}/status` | 变更缺陷状态 |
| PATCH | `/api/v1/defects/{id}/assign` | 分配缺陷 |
| PATCH | `/api/v1/defects/{id}/resolve` | 解决缺陷 |
| GET | `/api/v1/defects/statistics` | 缺陷统计 |
| GET | `/api/v1/defects/project/{pid}` | 按项目查询缺陷 |
| GET | `/api/v1/defects/library/{lid}` | 按总库查询缺陷 |
| GET | `/api/v1/defects/search` | 搜索缺陷 |

### 16.2 参考资料

- [Flask官方文档](https://flask.palletsprojects.com/)
- [JWT认证标准](https://jwt.io/)
- [RESTful API设计指南](https://restfulapi.net/)

### 16.3 术语表

| 术语 | 解释 |
|------|------|
| API | 应用程序接口 (Application Programming Interface) |
| REST | 表述性状态转移 (Representational State Transfer) |
| JSON | JavaScript对象表示法 (JavaScript Object Notation) |
| JWT | JSON Web Token |
| Blueprint | Flask模块化路由组织方式 |
| PLC | 可编程逻辑控制器 (Programmable Logic Controller) |

---

**文档版本**：INT V2.8.0
**编写日期**：2026-06-14
**编写人员**：技术负责人
