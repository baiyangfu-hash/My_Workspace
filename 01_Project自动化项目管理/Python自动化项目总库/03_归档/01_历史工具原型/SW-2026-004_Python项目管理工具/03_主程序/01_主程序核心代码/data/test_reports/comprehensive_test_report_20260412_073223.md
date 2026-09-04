# Python项目管理工具测试报告
> 测试时间: 2026-04-12T07:32:21.128952
> 完成时间: 2026-04-12T07:32:23.074682

## 测试摘要
- 总计测试: 30 项
- 通过: 27 项
- 失败: 3 项
- 跳过: 0 项
- 成功率: 90.00%

## 环境信息
- Python版本: 3.14.2
- 操作系统: Windows-11-10.0.26200-SP0
- 架构: 64bit
- 系统: Windows 11

## 测试详情
### 总库管理
- **总库列表查询**: ✅ 通过
  - 详情: 共2个总库
  - 执行时间: 0.027秒
- **总库统计**: ✅ 通过
  - 详情: 共0个总库
  - 执行时间: 0.001秒
- **总库管理功能**: ❌ 失败
  - 详情: 'list' object has no attribute 'library_id'

### 项目管理
- **项目列表查询**: ✅ 通过
  - 详情: 共33个项目
  - 执行时间: 0.003秒
- **项目统计**: ✅ 通过
  - 详情: 总计33个项目
  - 执行时间: 0.006秒
- **规格管理**: ✅ 通过
  - 详情: 共6个规格
  - 执行时间: 0.006秒

### 变更管理
- **变更管理功能**: ❌ 失败
  - 详情: (sqlite3.OperationalError) no such column: changes.domain
[SQL: SELECT count(*) AS count_1 
FROM (SELECT changes.id AS changes_id, changes.change_id AS changes_change_id, changes.project_id AS changes_project_id, changes.title AS changes_title, changes.domain AS changes_domain, changes.nature AS changes_nature, changes.scope AS changes_scope, changes.priority AS changes_priority, changes.type AS changes_type, changes.impact AS changes_impact, changes.description AS changes_description, changes.reason AS changes_reason, changes.content_before AS changes_content_before, changes.content_after AS changes_content_after, changes.impact_analysis AS changes_impact_analysis, changes.related_changes AS changes_related_changes, changes.propagation_chain AS changes_propagation_chain, changes.approval_level AS changes_approval_level, changes.reviewer AS changes_reviewer, changes.status AS changes_status, changes.proposer AS changes_proposer, changes.approver AS changes_approver, changes.implementer AS changes_implementer, changes.attachment AS changes_attachment, changes.created_at AS changes_created_at, changes.updated_at AS changes_updated_at, changes.approved_at AS changes_approved_at, changes.implemented_at AS changes_implemented_at, changes.completed_at AS changes_completed_at 
FROM changes 
WHERE changes.project_id = ?) AS anon_1]
[parameters: ('PRJ-20260412-bb9ad227',)]
(Background on this error at: https://sqlalche.me/e/14/e3q8)

### 模板管理
- **模板列表**: ✅ 通过
  - 详情: 共5个模板
  - 执行时间: 0.002秒
- **模板类型**: ✅ 通过
  - 详情: 共5种类型
  - 执行时间: 0.001秒

### 插件系统
- **插件列表**: ✅ 通过
  - 详情: 共0个插件
  - 执行时间: 0.002秒
- **插件系统功能**: ❌ 失败
  - 详情: PluginMarketService.get_available_plugins() missing 1 required positional argument: 'self'

### PLC集成
- **PLC变量解析器**: ✅ 通过
  - 详情: 版本: 未知
  - 执行时间: 0.000秒

### 构建部署
- **获取构建信息**: ✅ 通过
  - 详情: 项目类型: setup.py
  - 执行时间: 0.000秒
- **项目路径验证**: ✅ 通过
  - 详情: 路径存在: True
  - 执行时间: 0.000秒
- **Python项目检测**: ✅ 通过
  - 详情: 是Python项目: True
  - 执行时间: 0.000秒
- **项目构建测试**: ✅ 通过
  - 详情: 构建结果: C:\Users\fubai\AppData\Local\Temp\tmpqwhixsq2\python_project_manager-2.1.0-py3-none-any.whl
  - 执行时间: 1.034秒

### 性能测试
- **启动时间**: ✅ 通过
  - 详情: 跳过 - 可执行文件不存在
- **项目列表响应时间**: ✅ 通过
  - 详情: 0.004秒
  - 执行时间: 0.004秒
- **总库列表响应时间**: ✅ 通过
  - 详情: 0.001秒
  - 执行时间: 0.001秒
- **内存占用**: ✅ 通过
  - 详情: 90.09 MB

### 安全测试
- **配置文件权限 - api_config.json**: ✅ 通过
  - 详情: 配置文件存在
- **配置文件权限 - app_config.json**: ✅ 通过
  - 详情: 配置文件存在
- **配置文件权限 - database_config.json**: ✅ 通过
  - 详情: 配置文件存在
- **配置文件权限 - spec_version_config.json**: ✅ 通过
  - 详情: 配置文件存在
- **数据库文件**: ✅ 通过
  - 详情: 数据库文件存在

### 兼容性测试
- **Python版本**: ✅ 通过
  - 详情: Python 3.14.2
- **操作系统**: ✅ 通过
  - 详情: Windows-11-10.0.26200-SP0
- **依赖 - PyQt5**: ✅ 通过
  - 详情: 依赖可用
- **依赖 - psutil**: ✅ 通过
  - 详情: 依赖可用
- **依赖 - sqlalchemy**: ✅ 通过
  - 详情: 依赖可用

## Bug清单
| 编号 | 类别 | 测试项 | 问题描述 |
|------|------|--------|----------|
| 1 | 总库管理 | 总库管理功能 | 'list' object has no attribute 'library_id' |
| 2 | 变更管理 | 变更管理功能 | (sqlite3.OperationalError) no such column: changes.domain
[SQL: SELECT count(*) AS count_1 
FROM (SELECT changes.id AS changes_id, changes.change_id AS changes_change_id, changes.project_id AS changes_project_id, changes.title AS changes_title, changes.domain AS changes_domain, changes.nature AS changes_nature, changes.scope AS changes_scope, changes.priority AS changes_priority, changes.type AS changes_type, changes.impact AS changes_impact, changes.description AS changes_description, changes.reason AS changes_reason, changes.content_before AS changes_content_before, changes.content_after AS changes_content_after, changes.impact_analysis AS changes_impact_analysis, changes.related_changes AS changes_related_changes, changes.propagation_chain AS changes_propagation_chain, changes.approval_level AS changes_approval_level, changes.reviewer AS changes_reviewer, changes.status AS changes_status, changes.proposer AS changes_proposer, changes.approver AS changes_approver, changes.implementer AS changes_implementer, changes.attachment AS changes_attachment, changes.created_at AS changes_created_at, changes.updated_at AS changes_updated_at, changes.approved_at AS changes_approved_at, changes.implemented_at AS changes_implemented_at, changes.completed_at AS changes_completed_at 
FROM changes 
WHERE changes.project_id = ?) AS anon_1]
[parameters: ('PRJ-20260412-bb9ad227',)]
(Background on this error at: https://sqlalche.me/e/14/e3q8) |
| 3 | 插件系统 | 插件系统功能 | PluginMarketService.get_available_plugins() missing 1 required positional argument: 'self' |

## 建议
1. 针对失败的测试项进行修复
2. 优化性能测试中发现的瓶颈
3. 加强安全测试覆盖
4. 确保在不同环境下的兼容性