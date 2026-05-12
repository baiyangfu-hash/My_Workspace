# SW-2026-004 Python项目管理工具 - API文档

## 1. 文档基础信息

**文档标题**：SW-2026-004 Python项目管理工具API文档
**文档版本**：INT-V1.0.3
**编制日期**：2026-03-15
**编制人**：技术负责人
**审核人**：技术负责人
**项目编号**：SW-2026-004
**迭代版本**：V1.0.3

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 | 详细说明 |
|--------|----------|--------|----------|----------|
| V1.0.0 | 初始版本 | 技术负责人 | 2026-03-12 | 创建API文档 |
| V1.0.3 | 更新版本号和审核人 | 技术负责人 | 2026-03-15 | 统一版本号为V1.0.3，更新审核人 |

## 3. 接口概述

### 3.1 文档目的

本文档旨在描述SW-2026-004 Python项目管理工具的API接口，包括接口功能、请求参数、响应格式等，为开发人员提供接口使用指南。

### 3.2 接口分类

Python项目管理工具的API接口分为以下几类：
- **项目管理API**：管理项目的创建、查询、更新和删除
- **模板管理API**：管理项目模板的创建、查询、更新和删除
- **插件管理API**：管理插件的安装、启用、禁用和配置
- **规范管理API**：管理项目规范的创建、查询和应用
- **总库管理API**：管理项目总库的查询和统计
- **变更管理API**：管理项目变更的创建、审批和执行

### 3.3 技术选型

| 接口类型 | 技术框架 | 说明 |
|----------|----------|------|
| REST API | Flask ≥2.3.0 | 轻量级Web框架 |
| 认证方式 | API Key | 基于请求头的认证机制 |
| 数据格式 | JSON | 统一的请求和响应格式 |

## 4. 接口基础信息

### 4.1 基础URL

```
http://localhost:5000/api
```

### 2.2 认证方式

API接口采用API Key认证，需要在请求头中添加：

```
X-API-Key: your-api-key
```

### 2.3 通用响应格式

#### 成功响应

```json
{
  "code": 200,
  "message": "成功",
  "data": {
    // 响应数据
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

#### 失败响应

```json
{
  "code": 400,
  "message": "错误信息",
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 2.4 错误码

| 错误码 | 描述 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 3. 项目管理API

### 3.1 创建项目

**接口URL**：`/api/projects`

**请求方法**：POST

**功能描述**：创建新项目

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| business_line | string | 是 | 业务线代码 |
| name | string | 是 | 项目名称 |
| template_id | string | 是 | 模板ID |
| manager | string | 否 | 项目负责人 |
| description | string | 否 | 项目描述 |
| path | string | 否 | 自定义项目路径 |

**请求示例**：

```json
{
  "business_line": "ZD",
  "name": "测试项目",
  "template_id": "TPL-001",
  "manager": "张三",
  "description": "测试项目描述"
}
```

**响应示例**：

```json
{
  "code": 201,
  "message": "项目创建成功",
  "data": {
    "project": {
      "id": "PROJ-001",
      "code": "ZD-2026-001",
      "name": "测试项目",
      "business_line": "ZD",
      "manager": "张三",
      "description": "测试项目描述",
      "status": "active",
      "created_at": "2026-03-10T12:00:00Z",
      "updated_at": "2026-03-10T12:00:00Z"
    }
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 3.2 获取项目列表

**接口URL**：`/api/projects`

**请求方法**：GET

**功能描述**：获取项目列表

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 | 默认值 |
|--------|------|------|------|--------|
| status | string | 否 | 项目状态 | 无 |
| business_line | string | 否 | 业务线代码 | 无 |
| keyword | string | 否 | 搜索关键词 | 无 |
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
        "code": "ZD-2026-001",
        "name": "测试项目",
        "business_line": "ZD",
        "manager": "张三",
        "status": "active",
        "created_at": "2026-03-10T12:00:00Z"
      }
    ],
    "pagination": {
      "total": 1,
      "page": 1,
      "size": 20,
      "pages": 1
    }
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 3.3 获取项目详情

**接口URL**：`/api/projects/{project_id}`

**请求方法**：GET

**功能描述**：获取项目详情

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
      "code": "ZD-2026-001",
      "name": "测试项目",
      "business_line": "ZD",
      "manager": "张三",
      "description": "测试项目描述",
      "status": "active",
      "created_at": "2026-03-10T12:00:00Z",
      "updated_at": "2026-03-10T12:00:00Z",
      "statistics": {}
    }
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 3.4 更新项目信息

**接口URL**：`/api/projects/{project_id}`

**请求方法**：PUT

**功能描述**：更新项目信息

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |

**请求参数**：

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
  "description": "更新后的项目描述"
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "project": {
      "id": "PROJ-001",
      "code": "ZD-2026-001",
      "name": "更新后的项目名称",
      "business_line": "ZD",
      "manager": "李四",
      "description": "更新后的项目描述",
      "status": "active",
      "created_at": "2026-03-10T12:00:00Z",
      "updated_at": "2026-03-10T12:30:00Z"
    }
  },
  "timestamp": "2026-03-10T12:30:00Z"
}
```

### 3.5 删除项目

**接口URL**：`/api/projects/{project_id}`

**请求方法**：DELETE

**功能描述**：删除项目（软删除）

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "删除成功",
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 3.6 生成项目编号

**接口URL**：`/api/projects/generate-code`

**请求方法**：GET

**功能描述**：生成项目编号

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| business_line | string | 是 | 业务线代码 |

**响应示例**：

```json
{
  "code": 200,
  "message": "生成成功",
  "data": {
    "project_code": "ZD-2026-001"
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 3.7 执行项目规范检查

**接口URL**：`/api/projects/{project_id}/check`

**请求方法**：POST

**功能描述**：执行项目规范检查

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| check_types | array | 否 | 检查类型列表 |

**请求示例**：

```json
{
  "check_types": ["structure", "naming", "code"]
}
```

**响应示例**：

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
    "report_path": "path/to/report.md"
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 3.8 生成项目报告

**接口URL**：`/api/projects/{project_id}/report`

**请求方法**：POST

**功能描述**：生成项目报告

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "报告生成成功",
  "data": {
    "report_path": "path/to/project_report.md"
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 3.9 获取项目统计信息

**接口URL**：`/api/projects/statistics`

**请求方法**：GET

**功能描述**：获取项目统计信息

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
      "ZD": 5,
      "DJ": 3,
      "XT": 2
    }
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

## 4. 模板管理API

### 4.1 获取模板列表

**接口URL**：`/api/templates`

**请求方法**：GET

**功能描述**：获取模板列表

**请求参数**：

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
        "id": "TPL-001",
        "name": "标准模板",
        "compiler": "Work3",
        "scene": "general",
        "is_builtin": true,
        "created_at": "2026-03-10T12:00:00Z"
      }
    ],
    "total": 1
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 4.2 获取模板详情

**接口URL**：`/api/templates/{template_id}`

**请求方法**：GET

**功能描述**：获取模板详情

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| template_id | string | 是 | 模板ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "template": {
      "id": "TPL-001",
      "name": "标准模板",
      "compiler": "Work3",
      "scene": "general",
      "is_builtin": true,
      "structure": {},
      "created_at": "2026-03-10T12:00:00Z",
      "updated_at": "2026-03-10T12:00:00Z"
    }
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 4.3 创建自定义模板

**接口URL**：`/api/templates`

**请求方法**：POST

**功能描述**：创建自定义模板

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 是 | 模板名称 |
| compiler | string | 是 | 编译器类型 |
| scene | string | 是 | 应用场景 |
| structure | object | 是 | 模板结构 |

**请求示例**：

```json
{
  "name": "自定义模板",
  "compiler": "Work3",
  "scene": "general",
  "structure": {
    "folders": [
      {
        "name": "程序",
        "subfolders": []
      }
    ]
  }
}
```

**响应示例**：

```json
{
  "code": 201,
  "message": "模板创建成功",
  "data": {
    "template": {
      "id": "TPL-002",
      "name": "自定义模板",
      "compiler": "Work3",
      "scene": "general",
      "is_builtin": false,
      "structure": {},
      "created_at": "2026-03-10T12:00:00Z",
      "updated_at": "2026-03-10T12:00:00Z"
    }
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 4.4 更新模板信息

**接口URL**：`/api/templates/{template_id}`

**请求方法**：PUT

**功能描述**：更新模板信息

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| template_id | string | 是 | 模板ID |

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 否 | 模板名称 |
| structure | object | 否 | 模板结构 |

**请求示例**：

```json
{
  "name": "更新后的模板名称",
  "structure": {
    "folders": [
      {
        "name": "程序",
        "subfolders": [
          {
            "name": "功能块"
          }
        ]
      }
    ]
  }
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "template": {
      "id": "TPL-002",
      "name": "更新后的模板名称",
      "compiler": "Work3",
      "scene": "general",
      "is_builtin": false,
      "structure": {},
      "created_at": "2026-03-10T12:00:00Z",
      "updated_at": "2026-03-10T12:30:00Z"
    }
  },
  "timestamp": "2026-03-10T12:30:00Z"
}
```

### 4.5 删除模板

**接口URL**：`/api/templates/{template_id}`

**请求方法**：DELETE

**功能描述**：删除模板

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| template_id | string | 是 | 模板ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "删除成功",
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 4.6 导出模板

**接口URL**：`/api/templates/{template_id}/export`

**请求方法**：GET

**功能描述**：导出模板

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| template_id | string | 是 | 模板ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "导出成功",
  "data": {
    "template_json": {
      "name": "标准模板",
      "compiler": "Work3",
      "scene": "general",
      "structure": {}
    }
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 4.7 导入模板

**接口URL**：`/api/templates/import`

**请求方法**：POST

**功能描述**：导入模板

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| template_json | object | 是 | 模板JSON数据 |

**请求示例**：

```json
{
  "template_json": {
    "name": "导入模板",
    "compiler": "Work3",
    "scene": "general",
    "structure": {}
  }
}
```

**响应示例**：

```json
{
  "code": 201,
  "message": "导入成功",
  "data": {
    "template": {
      "id": "TPL-003",
      "name": "导入模板",
      "compiler": "Work3",
      "scene": "general",
      "is_builtin": false,
      "structure": {},
      "created_at": "2026-03-10T12:00:00Z",
      "updated_at": "2026-03-10T12:00:00Z"
    }
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 4.8 验证模板结构

**接口URL**：`/api/templates/validate`

**请求方法**：POST

**功能描述**：验证模板结构

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| structure | object | 是 | 模板结构 |

**请求示例**：

```json
{
  "structure": {
    "folders": [
      {
        "name": "程序",
        "subfolders": []
      }
    ]
  }
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "模板结构验证通过",
  "data": {
    "valid": true
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

## 5. 插件管理API

### 5.1 获取插件列表

**接口URL**：`/api/plugins`

**请求方法**：GET

**功能描述**：获取插件列表

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
    ]
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 5.2 安装插件

**接口URL**：`/api/plugins`

**请求方法**：POST

**功能描述**：安装插件

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| plugin_path | string | 是 | 插件文件路径 |

**请求示例**：

```json
{
  "plugin_path": "path/to/plugin.zip"
}
```

**响应示例**：

```json
{
  "code": 201,
  "message": "插件安装成功",
  "data": {
    "plugin": {
      "id": "PLUGIN-002",
      "name": "新插件",
      "version": "1.0.0",
      "status": "disabled",
      "description": "新插件描述"
    }
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 5.3 启用插件

**接口URL**：`/api/plugins/{plugin_id}/enable`

**请求方法**：POST

**功能描述**：启用插件

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| plugin_id | string | 是 | 插件ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "插件启用成功",
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 5.4 禁用插件

**接口URL**：`/api/plugins/{plugin_id}/disable`

**请求方法**：POST

**功能描述**：禁用插件

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| plugin_id | string | 是 | 插件ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "插件禁用成功",
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 5.5 卸载插件

**接口URL**：`/api/plugins/{plugin_id}`

**请求方法**：DELETE

**功能描述**：卸载插件

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| plugin_id | string | 是 | 插件ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "插件卸载成功",
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 5.6 配置插件

**接口URL**：`/api/plugins/{plugin_id}/config`

**请求方法**：PUT

**功能描述**：配置插件

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| plugin_id | string | 是 | 插件ID |

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| config | object | 是 | 插件配置 |

**请求示例**：

```json
{
  "config": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "插件配置成功",
  "timestamp": "2026-03-10T12:00:00Z"
}
```

## 6. 规范管理API

### 6.1 获取规范列表

**接口URL**：`/api/specs`

**请求方法**：GET

**功能描述**：获取规范列表

**响应示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "specs": [
      {
        "id": "SPEC-001",
        "name": "命名规范",
        "type": "naming",
        "description": "项目命名规范"
      }
    ]
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 6.2 获取规范详情

**接口URL**：`/api/specs/{spec_id}`

**请求方法**：GET

**功能描述**：获取规范详情

**路径参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| spec_id | string | 是 | 规范ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "spec": {
      "id": "SPEC-001",
      "name": "命名规范",
      "type": "naming",
      "description": "项目命名规范",
      "content": "命名规范内容"
    }
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

## 7. 总库管理API

### 7.1 获取总库统计信息

**接口URL**：`/api/library-dashboard`

**请求方法**：GET

**功能描述**：获取总库统计信息

**响应示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total_projects": 100,
    "projects_by_status": {
      "active": 80,
      "completed": 20
    },
    "projects_by_business": {
      "ZD": 40,
      "DJ": 30,
      "XT": 20,
      "WX": 10
    }
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

### 7.2 获取总库变更记录

**接口URL**：`/api/library-changes`

**请求方法**：GET

**功能描述**：获取总库变更记录

**响应示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "changes": [
      {
        "id": "CHANGE-001",
        "project_code": "ZD-2026-001",
        "type": "create",
        "description": "创建项目",
        "created_at": "2026-03-10T12:00:00Z"
      }
    ]
  },
  "timestamp": "2026-03-10T12:00:00Z"
}
```

## 8. 接口扩展性

### 8.1 添加新接口

按照现有接口风格添加新接口，遵循以下原则：
- 使用RESTful设计风格
- 统一的响应格式
- 明确的参数验证
- 详细的错误处理

### 8.2 版本控制

API接口支持版本控制，如：

```
http://localhost:5000/api/v1/projects
```

### 8.3 性能优化

- **缓存**：对频繁访问的数据进行缓存
- **异步处理**：对耗时操作采用异步处理
- **分页**：对列表接口使用分页机制

## 9. 附录

### 9.1 参考资料

- [Flask官方文档](https://flask.palletsprojects.com/en/2.0.x/)
- [RESTful API设计指南](https://restfulapi.net/)
- [Python官方文档](https://docs.python.org/zh-cn/3/)

### 9.2 术语表

| 术语 | 解释 |
|------|------|
| API | 应用程序接口(Application Programming Interface) |
| REST | 表述性状态转移(Representational State Transfer) |
| JSON | JavaScript对象表示法(JavaScript Object Notation) |
| HTTP | 超文本传输协议(Hypertext Transfer Protocol) |
| PLC | 可编程逻辑控制器(Programmable Logic Controller) |

### 9.3 接口变更记录

| 版本 | 变更日期 | 变更内容 | 变更人 |
|------|----------|----------|--------|
| V1.0.0 | 2026-03-10 | 创建API文档 | 系统 |

---

**文档版本**：V1.0.0
**编写日期**：2026-03-10
**编写人员**：系统
