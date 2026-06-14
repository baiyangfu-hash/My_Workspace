# 存量资产基线清单

**项目编号**：SW-2026-004  
**项目名称**：Python项目管理工具  
**文档版本**：V2.8.0  
**编制日期**：2026-02-20  
**更新日期**：2026-06-14  
**编制人员**：技术负责人  

---

## 一、代码资产基线

### 1.1 代码文件统计

| 分类 | 文件数量 | 说明 |
|------|---------|------|
| Python源代码文件 | 100+个 | 包含所有业务代码 |
| 配置文件(JSON) | 3个 | 应用/数据库/API配置 |
| 模板数据(YAML) | 5个 | 内置模板数据（数据外置） |
| 依赖配置 | 1个 | requirements.txt |
| 打包脚本 | 2个 | build.py, fix_imports.py |
| 数据库迁移 | 多个 | Alembic版本迁移脚本 |
| **合计** | **110+个** | - |

### 1.2 代码模块结构

```
03_主程序/01_主程序核心代码/
├── main.py                          # 主入口文件
├── setup.py                         # 安装配置
├── requirements.txt                  # 依赖配置
├── build.py                         # 打包脚本
├── fix_imports.py                   # 导入修复脚本
├── config/                          # 配置文件目录
│   ├── app_config.json              # 应用配置
│   ├── database_config.json         # 数据库配置
│   ├── api_config.json              # API配置
│   └── templates/                   # 模板数据目录(V2.8.0 YAML外置)
│       ├── TPL-SINGLE-PLC-001.yaml  # 单机设备(PLC+HMI)
│       ├── TPL-FULLLINE-AUTO-001.yaml # 自动化整线
│       ├── TPL-SINGLE-ROBOT-001.yaml # 单机设备(机器人)
│       ├── TPL-UPGRADE-STD-001.yaml # 系统升级
│       └── TPL-UPPER-STD-001.yaml   # 上位机开发
├── alembic/                         # 数据库迁移(V2.1.0新增)
│   ├── env.py                       # Alembic环境配置
│   └── versions/                    # 版本迁移脚本
│       ├── initial_schema.py        # 初始Schema
│       ├── v21_change_mgmt_upgrade.py # V2.1.0变更管理升级
│       └── v2_8_0_template_optimization.py # V2.8.0模板优化
├── data/                            # 数据目录
│   └── project_manager.db           # SQLite数据库
├── logs/                            # 日志目录
│   └── app.log                      # 应用日志
└── src/                             # 源代码目录
    ├── core/                        # 核心模块 (12个文件)
    │   ├── __init__.py
    │   ├── app.py                   # 应用初始化
    │   ├── config.py                # 配置管理
    │   ├── constants.py             # 常量定义(拆分后主入口)
    │   ├── _template_constants.py   # 模板常量(V2.8.0懒加载YAML)
    │   ├── _change_constants.py     # 变更常量(V2.1.0 Domain/Nature/Scope)
    │   ├── _business_constants.py   # 业务常量(业务线等)
    │   ├── container.py             # 依赖注入容器
    │   ├── version.py               # 版本信息
    │   ├── settings.py              # 设置管理
    │   ├── spec_manager.py          # 规范管理器
    │   ├── plugin_metadata.py       # 插件元数据
    │   └── exceptions/              # 自定义异常
    │       └── __init__.py
    ├── models/                      # 数据模型 (16个文件)
    │   ├── __init__.py
    │   ├── base.py                  # 基础模型
    │   ├── project.py               # 项目模型(含applied_template_version)
    │   ├── template.py              # 模板模型(含schema_version/base_template_id)
    │   ├── plugin.py                # 插件模型
    │   ├── change.py                # 变更模型(V2.1.0三维分类)
    │   ├── spec.py                  # 规范模型
    │   ├── milestone.py             # 里程碑模型
    │   ├── task.py                  # 任务模型
    │   ├── defect.py                # 缺陷模型(V2.3.0新增)
    │   ├── impact.py                # 影响分析模型(V2.3.0新增)
    │   ├── approval.py              # 审批模型(V2.1.0新增)
    │   ├── library.py               # 库模型(V2.4.0新增)
    │   ├── library_version.py       # 库版本模型(V2.4.0新增)
    │   ├── library_dependency.py    # 库依赖模型(V2.4.0新增)
    │   └── library_change.py        # 库变更模型(V2.4.0新增)
    ├── dao/                         # 数据访问层 (15个文件)
    │   ├── __init__.py
    │   ├── database.py              # 数据库管理(SQLAlchemy引擎/会话)
    │   ├── project_dao.py           # 项目DAO
    │   ├── template_dao.py          # 模板DAO
    │   ├── plugin_dao.py            # 插件DAO
    │   ├── change_dao.py            # 变更DAO
    │   ├── spec_dao.py              # 规范DAO
    │   ├── milestone_dao.py         # 里程碑DAO
    │   ├── task_dao.py              # 任务DAO
    │   ├── defect_dao.py            # 缺陷DAO(V2.3.0新增)
    │   ├── approval_dao.py          # 审批DAO(V2.1.0新增)
    │   ├── library_dao.py           # 库DAO(V2.4.0新增)
    │   ├── library_version_dao.py   # 库版本DAO(V2.4.0新增)
    │   ├── library_dependency_dao.py # 库依赖DAO(V2.4.0新增)
    │   └── library_change_dao.py    # 库变更DAO(V2.4.0新增)
    ├── services/                    # 业务服务层 (24个Service)
    │   ├── __init__.py
    │   ├── project_service.py       # 项目服务(通过TemplateService访问模板)
    │   ├── template_service.py      # 模板服务(V2.8.0 YAML加载/继承/版本)
    │   ├── plugin_service.py        # 插件服务
    │   ├── plugin_market_service.py # 插件市场服务(V2.5.0新增)
    │   ├── change_service.py        # 变更服务(V2.1.0三维分类+传播链)
    │   ├── change_analytics_service.py # 变更分析服务(V2.1.0新增)
    │   ├── spec_service.py          # 规范服务
    │   ├── check_service.py         # 检查服务(SCL命名+结构+Python命名)
    │   ├── report_service.py        # 报告服务(通过TemplateService访问模板)
    │   ├── progress_service.py      # 进度服务
    │   ├── statistics_service.py    # 统计服务
    │   ├── export_service.py        # 导出服务
    │   ├── defect_service.py        # 缺陷服务(V2.3.0新增)
    │   ├── impact_service.py        # 影响分析服务(V2.3.0新增)
    │   ├── approval_service.py      # 审批服务(V2.1.0分级审批)
    │   ├── notification_service.py  # 通知服务(V2.1.0新增)
    │   ├── library_service.py       # 库服务(V2.4.0新增)
    │   ├── library_dashboard_service.py # 库仪表盘(V2.4.0新增)
    │   ├── library_change_service.py # 库变更服务(V2.4.0新增)
    │   ├── library_dependency_service.py # 库依赖服务(V2.4.0新增)
    │   ├── library_report_service.py # 库报告服务(V2.4.0新增)
    │   ├── library_spec_service.py  # 库规范服务(V2.4.0新增)
    │   ├── library_version_service.py # 库版本服务(V2.4.0新增)
    │   └── build_deploy_service.py  # 构建部署服务
    ├── api/                         # REST API层 (8个Blueprint)
    │   ├── __init__.py
    │   ├── app.py                   # Flask应用
    │   ├── auth.py                  # JWT认证
    │   ├── client.py                # API客户端
    │   └── routes/
    │       ├── __init__.py
    │       ├── projects.py          # 项目API
    │       ├── templates.py         # 模板API
    │       ├── plugins.py           # 插件API
    │       ├── specs.py             # 规范API
    │       ├── defects.py           # 缺陷API(V2.3.0新增)
    │       ├── libraries.py         # 库API(V2.4.0新增)
    │       ├── library_changes.py   # 库变更API(V2.4.0新增)
    │       └── library_dashboard.py # 库仪表盘API(V2.4.0新增)
    ├── ui/                          # GUI界面层 (PyQt5 9个Tab页签)
    │   ├── __init__.py
    │   ├── main_window.py           # 主窗口
    │   ├── dialogs/
    │   │   ├── __init__.py
    │   │   ├── new_project_dialog.py # 新建项目对话框
    │   │   └── import_project_dialog.py # 导入项目对话框(V2.6.0新增)
    │   └── widgets/
    │       ├── __init__.py
    │       ├── project_list.py      # 项目列表控件
    │       ├── template_manager.py  # 模板管理控件
    │       ├── template_editor.py   # 模板编辑器
    │       ├── plugin_manager.py    # 插件管理控件
    │       ├── plugin_market.py     # 插件市场控件(V2.5.0新增)
    │       ├── plugin_config.py     # 插件配置控件
    │       ├── spec_center.py       # 规范中心控件
    │       ├── change_manager.py    # 变更管理控件
    │       ├── progress_manager.py  # 进度管理控件
    │       ├── report_center.py     # 报告中心控件
    │       └── library_manager.py   # 库管理控件(V2.4.0新增)
    ├── gui/                         # GUI辅助模块
    │   └── spec_sync_dialog.py      # 规范同步对话框(V2.6.0新增)
    ├── utils/                       # 工具模块
    │   ├── __init__.py
    │   ├── logger.py                # 日志工具
    │   ├── file_utils.py            # 文件工具
    │   ├── path_utils.py            # 路径工具
    │   ├── validators.py            # 验证工具
    │   ├── rate_limiter.py          # 限流工具
    │   ├── cache.py                 # 缓存工具
    │   └── security/                # 安全工具
    │       └── __init__.py
    └── plugins/                     # 插件目录 (3个内置插件)
        ├── __init__.py
        ├── code_check/              # 代码检查插件
        │   └── __init__.py
        ├── document_generator/      # 文档生成插件
        │   └── __init__.py
        └── plc_variable_parser/     # PLC变量解析插件(V2.5.0新增)
            ├── __init__.py
            ├── parsers/             # 解析器(4种)
            │   ├── __init__.py
            │   ├── base_parser.py
            │   ├── codesys_parser.py
            │   ├── work3_parser.py
            │   └── autoshop_parser.py
            ├── exporters/           # 导出器
            │   ├── __init__.py
            │   └── exporter.py
            ├── ui/                  # 插件UI
            │   ├── __init__.py
            │   ├── parser_widget.py
            │   ├── variable_table.py
            │   ├── variable_dialog.py
            │   └── batch_edit_dialog.py
            └── utils/               # 插件工具
                ├── __init__.py
                └── encoding_detector.py
```

### 1.3 代码行数统计

| 模块 | 文件数 | 预估代码行数 | 说明 |
|------|--------|-------------|------|
| core (核心模块) | 12 | ~1200行 | 配置管理、常量拆分、DI容器、版本信息 |
| models (数据模型) | 16 | ~1500行 | 16个SQLAlchemy ORM模型 |
| dao (数据访问层) | 15 | ~1500行 | 15个DAO模块 |
| services (业务服务层) | 24 | ~5000行 | 24个Service模块 |
| api (REST API层) | 12 | ~800行 | 8个Blueprint + JWT认证 |
| ui (GUI界面层) | 15 | ~3000行 | PyQt5 9个Tab页签 |
| gui (GUI辅助) | 1 | ~200行 | 规范同步对话框 |
| utils (工具模块) | 8 | ~600行 | 日志/文件/路径/验证/安全/缓存/限流 |
| plugins (插件系统) | 15 | ~1500行 | 3个内置插件 |
| alembic (数据库迁移) | 4 | ~300行 | 3个版本迁移脚本 |
| main.py (入口) | 1 | ~160行 | 主入口和CLI命令 |
| build.py (打包) | 1 | ~180行 | PyInstaller打包脚本 |
| **合计** | **124** | **~15940行** | - |

### 1.4 技术栈清单

| 类别 | 技术/框架 | 版本 | 用途 |
|------|----------|------|------|
| GUI框架 | PyQt5 | 5.15.10 | 桌面界面开发 |
| Web框架 | Flask | 3.1.2 | REST API服务 |
| ORM框架 | SQLAlchemy | 2.0.27 | 数据库操作 |
| 数据库迁移 | Alembic | 1.13.1 | Schema版本管理 |
| 依赖注入 | dependency-injector | 4.41.0 | DI容器 |
| 数据库 | SQLite | 3.x | 本地数据存储 |
| CLI工具 | Click | 8.1.7 | 命令行接口 |
| 测试框架 | pytest | 8.0+ | 单元测试 |
| 打包工具 | PyInstaller | 6.4.0 | 可执行文件打包 |
| 模板数据 | PyYAML | 6.0+ | YAML模板文件解析(V2.8.0新增) |
| 安全 | bcrypt | 4.1.2 | 密码哈希 |
| 日期处理 | python-dateutil | 2.8.2 | 日期时间处理 |
| Markdown | markdown | 3.5.2 | Markdown渲染 |
| HTTP请求 | requests | 2.31.0 | HTTP客户端 |
| 环境变量 | python-dotenv | 1.0.1 | 环境变量管理 |

---

## 二、文档资产基线

### 2.1 项目文档清单（V2.8.0）

| 序号 | 文档名称 | 文档路径 | 版本 | 状态 |
|------|---------|---------|------|------|
| 1 | 产品化项目章程 | 01_启动过程/01_项目立项/006_产品化项目章程_PM.md | PM-V1.0.0 | 历史文档 |
| 2 | 产品路线图 | 01_启动过程/01_项目立项/007_产品路线图_PM.md | PM-V1.0.0 | 历史文档 |
| 3 | 存量资产基线清单 | 01_启动过程/01_存量资产基线清单_BASELINE.md | V2.8.0 | ✅ 已更新 |
| 4 | 项目启动完整流程图 | 01_启动过程/00_项目启动完整流程图_FLOW.md | V2.8.0 | ✅ 新增 |
| 5 | 项目启动检查清单 | 01_启动过程/00_项目启动检查清单_CHECKLIST.md | V2.8.0 | ✅ 新增 |
| 6 | 需求规格说明书 | 02_规划过程/01_需求规格说明书_REQ.md | V2.8.0 | ✅ 已更新 |
| 7 | 总库管理技术方案 | 02_规划过程/03_总库管理技术方案_DEV.md | V2.8.0 | ✅ 已更新 |
| 8 | 风险登记册 | 02_规划过程/05_风险登记册_REP.md | V2.8.0 | ✅ 已更新 |
| 9 | API文档 | 02_规划过程/06_API文档_INT.md | V2.8.0 | ✅ 已更新 |
| 10 | 架构设计文档 | 02_规划过程/07_架构设计文档_ARCH.md | V2.8.0 | ✅ 已更新 |
| 11 | 详细设计文档 | 02_规划过程/08_详细设计文档_DES.md | V2.8.0 | ✅ 已更新 |
| 12 | UI原型 | 02_规划过程/UI_Prototype_V2.7.0.html | V2.7.0 | ✅ 新增 |
| 13 | 用户操作手册 | 03_执行过程/01_用户操作手册_MAN.md | V2.8.0 | ✅ 已更新 |
| 14 | PM快速入门 | 03_执行过程/05_PM快速入门指南_PM.md | V2.6.0 | ✅ 已更新 |
| 15 | PLC工程师快速入门 | 03_执行过程/06_PLC工程师快速入门指南_PLC.md | V2.6.0 | ✅ 已更新 |
| 16 | 测试计划 | 03_执行过程/03_测试计划_TEST.md | V2.8.0 | ✅ 已更新 |
| 17 | 变更管理技术方案 | 04_监控和控制/01_变更管理技术方案_DEV.md | V2.1.0 | ✅ 已更新 |
| 18 | 版本变更台帐 | 04_监控和控制/06_版本变更台帐_CHG.md | V2.8.0 | ✅ 已更新 |
| 19 | 文档审查机制 | 04_监控和控制/05_文档审查机制_DOC.md | V2.8.0 | ✅ 已更新 |
| 20 | 模板管理优化技术方案 | 04_监控和控制/07_模板管理优化技术方案_DEV.md | V2.8.0 | ✅ 新增 |
| 21 | 项目会话 | PM_SESSION_SW-2026-004.md | V2.8.0 | ✅ 活跃 |

---

## 三、功能完成度（V2.8.0）

### 3.1 模块完成度

| 模块 | 完成度 | 说明 |
|------|--------|------|
| 总库管理 | 100% | 总库创建与配置、项目导入与管理、项目分类管理、项目搜索与过滤 |
| 监控与统计 | 100% | 项目状态监控、总库统计分析、依赖关系分析、健康状态评估 |
| 变更管理 | 100% | 二维分类(Domain×Nature×Scope)、传播链追踪、分级审批、变更台账 |
| 审批管理 | 100% | 分级审批流程、审批记录、审批等级自动匹配 |
| 缺陷管理 | 100% | 缺陷跟踪、缺陷统计、缺陷状态流转 |
| 影响分析 | 100% | 变更影响范围分析、传播链追踪 |
| 模板管理 | 100% | YAML外置加载、模板继承合并、模板版本管理、模板ID生成(TPL-CUSTOM格式) |
| 库管理 | 100% | 库注册、版本管理、依赖分析、变更追踪、仪表盘 |
| 插件系统 | 100% | 插件安装与管理、插件配置、插件市场、PLC变量解析插件 |
| 系统设置 | 100% | 基本设置、数据库设置、用户管理 |
| 数据导入导出 | 100% | 数据导入、数据导出 |
| GUI界面 | 100% | PyQt5 9个Tab页签 |
| REST API | 100% | 8个Blueprint + JWT认证 |
| CLI | 100% | Click命令行接口 |
| 打包发布 | 100% | PyInstaller目录模式打包 |
| **总体完成度** | **100%** | - |

### 3.2 内置模板清单（V2.8.0 YAML外置）

| 模板ID | 模板名称 | 业务线 | 数据来源 |
|--------|---------|--------|---------|
| TPL-SINGLE-PLC-001 | 单机设备(PLC+HMI) | DJ, ZD | YAML |
| TPL-FULLLINE-AUTO-001 | 自动化整线 | ZD | YAML |
| TPL-SINGLE-ROBOT-001 | 单机设备(机器人) | DJ | YAML |
| TPL-UPGRADE-STD-001 | 系统升级 | XT | YAML |
| TPL-UPPER-STD-001 | 上位机开发 | SW | YAML |

### 3.3 质量指标

| 指标 | 目标值 | 实际值 | 状态 |
|------|--------|--------|------|
| 代码规范符合率 | ≥90% | 95% | ✅ 达标 |
| 功能测试通过率 | ≥95% | 100% | ✅ 达标 |
| 文档完整性 | 100% | 100% | ✅ 达标 |
| API接口覆盖率 | ≥80% | 95% | ✅ 达标 |
| 打包文件大小 | <150MB | ~120MB | ✅ 达标 |
| 内置模板数量 | ≥5个 | 5个(YAML) | ✅ 达标 |

---

## 四、数据模型基线（V2.8.0）

### 4.1 核心数据模型

| 模型 | 文件 | 关键字段 | 版本变更 |
|------|------|---------|---------|
| Project | project.py | id, name, path, status, business_line, **applied_template_version** | V2.8.0新增applied_template_version |
| Template | template.py | id, name, content, business_lines, **schema_version**, **base_template_id** | V2.8.0新增schema_version/base_template_id |
| Change | change.py | id, title, domain, nature, scope, approval_level | V2.1.0三维分类 |
| Approval | approval.py | id, change_id, level, status, approver | V2.1.0新增 |
| Impact | impact.py | id, change_id, target_type, target_id | V2.3.0新增 |
| Defect | defect.py | id, title, severity, status | V2.3.0新增 |
| Library | library.py | id, name, current_version | V2.4.0新增 |
| LibraryVersion | library_version.py | id, library_id, version, changelog | V2.4.0新增 |
| LibraryDependency | library_dependency.py | id, library_id, depends_on_id | V2.4.0新增 |
| LibraryChange | library_change.py | id, library_id, change_type | V2.4.0新增 |
| Plugin | plugin.py | id, name, version, author, is_builtin | - |
| Spec | spec.py | id, spec_id, title, version | - |
| Milestone | milestone.py | id, project_id, name, due_date | - |
| Task | task.py | id, milestone_id, name, status | - |

---

## 五、变更记录

| 日期 | 版本 | 变更类型 | 变更内容 | 变更人 |
|------|------|----------|----------|--------|
| 2026-02-19 | V1.0.0 | 新增文档 | 创建存量资产基线清单 | Trae AI |
| 2026-02-20 | V1.1.0 | 更新文档 | 更新代码统计、新增V1.1.0功能模块 | Trae AI |
| 2026-02-20 | V1.1.1 | 更新文档 | 新增模板编辑器、更新模板数量 | Trae AI |
| 2026-06-14 | V2.8.0 | 全面重写 | 对齐V2.8.0实际代码：更新文件统计(70→110+)、模块结构(24 Service/16 Model/15 DAO/8 Blueprint/3 Plugin)、数据模型(14个ORM)、技术栈(PyQt5/Flask 3.1.2/Alembic/PyYAML)、模板清单(YAML外置5个)、文档清单(21份) | 技术负责人 |

---

**文档状态**：✅ 已完成  
**审核状态**：⏳ 待审核  
**批准状态**：⏳ 待批准  

*文档更新时间：2026-06-14*
