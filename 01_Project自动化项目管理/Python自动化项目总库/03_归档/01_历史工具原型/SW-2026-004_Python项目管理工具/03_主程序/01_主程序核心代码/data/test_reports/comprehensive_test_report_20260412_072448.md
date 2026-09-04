# Python项目管理工具测试报告
> 测试时间: 2026-04-12T07:24:47.482593
> 完成时间: 2026-04-12T07:24:48.358091

## 测试摘要
- 总计测试: 20 项
- 通过: 12 项
- 失败: 8 项
- 跳过: 0 项
- 成功率: 60.00%

## 环境信息
- Python版本: 3.14.2
- 操作系统: Windows-11-10.0.26200-SP0
- 架构: 64bit
- 系统: Windows 11

## 测试详情
### 总库管理
- **总库管理功能**: ❌ 失败
  - 详情: type object 'Domain' has no attribute 'CFG'

### 项目管理
- **项目管理功能**: ❌ 失败
  - 详情: type object 'Domain' has no attribute 'CFG'

### 变更管理
- **变更管理功能**: ❌ 失败
  - 详情: type object 'Domain' has no attribute 'CFG'

### 模板管理
- **模板管理功能**: ❌ 失败
  - 详情: type object 'Domain' has no attribute 'CFG'

### 插件系统
- **插件系统功能**: ❌ 失败
  - 详情: type object 'Domain' has no attribute 'CFG'

### PLC集成
- **PLC变量解析器**: ✅ 通过
  - 详情: 版本: 未知
  - 执行时间: 0.000秒

### 构建部署
- **构建部署功能**: ❌ 失败
  - 详情: type object 'Domain' has no attribute 'CFG'

### 性能测试
- **启动时间**: ❌ 失败
  - 详情: [WinError 225] 无法成功完成操作，因为文件包含病毒或潜在的垃圾软件。
- **响应时间**: ❌ 失败
  - 详情: type object 'Domain' has no attribute 'CFG'
- **内存占用**: ✅ 通过
  - 详情: 51.73 MB

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
| 1 | 总库管理 | 总库管理功能 | type object 'Domain' has no attribute 'CFG' |
| 2 | 项目管理 | 项目管理功能 | type object 'Domain' has no attribute 'CFG' |
| 3 | 变更管理 | 变更管理功能 | type object 'Domain' has no attribute 'CFG' |
| 4 | 模板管理 | 模板管理功能 | type object 'Domain' has no attribute 'CFG' |
| 5 | 插件系统 | 插件系统功能 | type object 'Domain' has no attribute 'CFG' |
| 6 | 构建部署 | 构建部署功能 | type object 'Domain' has no attribute 'CFG' |
| 7 | 性能测试 | 启动时间 | [WinError 225] 无法成功完成操作，因为文件包含病毒或潜在的垃圾软件。 |
| 8 | 性能测试 | 响应时间 | type object 'Domain' has no attribute 'CFG' |

## 建议
1. 针对失败的测试项进行修复
2. 优化性能测试中发现的瓶颈
3. 加强安全测试覆盖
4. 确保在不同环境下的兼容性