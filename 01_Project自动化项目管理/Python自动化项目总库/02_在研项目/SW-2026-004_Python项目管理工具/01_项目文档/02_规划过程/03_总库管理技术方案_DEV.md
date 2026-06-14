# 总库管理技术方案

**文档版本**：DEV V2.8.0
**编制日期**：2026-06-14
**编制人**：技术负责人

## 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 |
|--------|----------|--------|----------|
| DEV V2.8.0 | 对齐V2.8.0实际代码：更新技术栈（PyQt5/Flask 3.1.2/Python 3.11）；更新模块清单（24个Service+9个Widget+8个API Route+3个Plugin）；更新数据模型（16个ORM Model）；更新实现状态；模板管理优化 | 技术负责人 | 2026-06-14 |
| V1.0.0 | 初始创建总库管理技术方案 | 系统 | 2026-02-26 |

## 1. 技术方案内容

### 1.1. 架构设计

#### 1.1.1. 系统架构
- **架构风格**: 分层架构，采用服务导向设计 + 依赖注入容器
- **核心层次**:
  - 表现层（UI/API/CLI）— PyQt5 GUI + Flask REST API
  - 服务层（业务逻辑）— 24个Service模块
  - 数据访问层（DAO）— 13个DAO模块
  - 数据模型层（Models）— 16个SQLAlchemy ORM Model
  - 插件层（Plugins）— 3个内置插件 + 插件市场

#### 1.1.2. 模块划分

**总库核心模块**（已实现）:
| 模块 | 文件 | 状态 | 说明 |
|------|------|------|------|
| 总库管理 | `library_service.py` | ✅ | CRUD + 分类 + 统计 |
| 总库变更 | `library_change_service.py` | ✅ | V2.1.0 三维分类+传播链 |
| 总库仪表盘 | `library_dashboard_service.py` | ✅ | 统计概览+趋势 |
| 总库报告 | `library_report_service.py` | ✅ | 报告生成 |
| 总库依赖 | `library_dependency_service.py` | ✅ | 依赖关系管理 |
| 总库版本 | `library_version_service.py` | ✅ | 版本管理 |
| 总库规范 | `library_spec_service.py` | ✅ | 规范检查集成 |

**项目与变更模块**（已实现）:
| 模块 | 文件 | 状态 | 说明 |
|------|------|------|------|
| 项目管理 | `project_service.py` | ✅ | 导入/创建/编辑/批量操作 |
| 变更管理 | `change_service.py` | ✅ | V2.1.0 Domain×Nature×Scope |
| 变更分析 | `change_analytics_service.py` | ✅ | 变更趋势+统计 |
| 审批管理 | `approval_service.py` | ✅ | 分级审批链 |
| 影响分析 | `impact_service.py` | ✅ | 影响评估 |
| 缺陷管理 | `defect_service.py` | ✅ | Bug跟踪 |

**工具与辅助模块**（已实现）:
| 模块 | 文件 | 状态 | 说明 |
|------|------|------|------|
| 规范检查 | `check_service.py` | ✅ | 目录+命名+文档+代码风格 |
| 规范服务 | `spec_service.py` | ✅ | 规范注册+扫描 |
| 模板管理 | `template_service.py` | ✅ | 5套内置+自定义CRUD |
| 统计服务 | `statistics_service.py` | ✅ | 项目统计 |
| 报告中心 | `report_service.py` | ✅ | 综合报告 |
| 导出服务 | `export_service.py` | ✅ | 数据导出 |
| 进度管理 | `progress_service.py` | ✅ | 里程碑+进度 |
| 通知服务 | `notification_service.py` | ✅ | 通知推送 |
| 构建部署 | `build_deploy_service.py` | ⚠️ | 后端存在，GUI未接入 |
| 插件管理 | `plugin_service.py` | ✅ | 插件加载+生命周期 |
| 插件市场 | `plugin_market_service.py` | ✅ | 在线浏览+安装 |

**GUI组件**（已实现）:
| 组件 | 文件 | 说明 |
|------|------|------|
| 主窗口 | `main_window.py` | Tab式主界面 |
| 总库管理 | `library_manager.py` | 总库CRUD+分类树 |
| 项目列表 | `project_list.py` | 项目浏览+搜索+过滤 |
| 变更管理 | `change_manager.py` | 变更台账+审批流 |
| 模板管理 | `template_manager.py` | 模板浏览+选择 |
| 模板编辑 | `template_editor.py` | 自定义模板编辑 |
| 规范中心 | `spec_center.py` | 规范检查结果 |
| 进度管理 | `progress_manager.py` | 甘特图+里程碑 |
| 报告中心 | `report_center.py` | 报告生成+查看 |
| 插件管理 | `plugin_manager.py` | 已安装插件 |
| 插件市场 | `plugin_market.py` | 在线插件浏览 |
| 插件配置 | `plugin_config.py` | 插件参数设置 |

**API路由**（已实现）:
| 路由模块 | 文件 | 端点前缀 |
|----------|------|----------|
| 总库管理 | `libraries.py` | `/api/libraries` |
| 项目管理 | `projects.py` | `/api/projects` |
| 总库变更 | `library_changes.py` | `/api/libraries/{id}/changes` |
| 仪表盘 | `library_dashboard.py` | `/api/libraries/{id}/dashboard` |
| 规范管理 | `specs.py` | `/api/specs` |
| 模板管理 | `templates.py` | `/api/templates` |
| 缺陷管理 | `defects.py` | `/api/defects` |
| 插件管理 | `plugins.py` | `/api/plugins` |

**内置插件**:
| 插件 | 目录 | 说明 |
|------|------|------|
| PLC变量解析 | `plc_variable_parser/` | AutoShop/CODESYS/Work3解析器+导出+批量编辑 |
| 代码检查 | `code_check/` | 代码质量检查 |
| 文档生成 | `document_generator/` | 自动文档生成 |

#### 1.1.3. 数据结构设计（实际ORM模型）

**总库模型** (`Library`):
- `library_id`: 总库唯一标识（主键）
- `name`: 总库名称
- `description`: 总库描述
- `root_path`: 总库根路径
- `status`: 总库状态
- `created_at`: 创建时间
- `updated_at`: 更新时间

**分类模型** (`Category`):
- `category_id`: 分类唯一标识（主键）
- `library_id`: 所属总库ID（外键）
- `name`: 分类名称
- `description`: 分类描述
- `parent_id`: 父分类ID（外键，支持多级分类）

**总库项目关联** (`LibraryProject`):
- `library_id`: 总库ID（外键）
- `project_id`: 项目ID（外键）
- `added_at`: 添加时间
- `category_id`: 分类ID（外键）

**项目模型** (`Project`):
- `project_id`: 项目唯一标识（主键）
- `name`: 项目名称
- `project_number`: 项目编号
- `description`: 项目描述
- `root_path`: 项目根路径
- `status`: 项目状态（active/archived/deprecated）
- `business_line`: 业务线
- `library_id`: 所属总库ID（外键）
- `category_id`: 分类ID（外键）
- `created_at`/`updated_at`: 时间戳

**变更模型** (`Change`) — V2.1.0:
- `change_id`: 变更唯一标识（主键）
- `project_id`: 关联项目ID（外键）
- `title`: 变更标题
- `description`: 变更描述
- `domain`: 变更域（code/config/doc/spec/infra）
- `nature`: 变更性质（feature/fix/refactor/enhancement/removal）
- `scope`: 影响范围（local/module/cross_module/cross_project/cross_domain）
- `status`: 变更状态（draft/submitted/approved/implementing/completed/rejected/cancelled）
- `priority`: 优先级
- `propagation_chain`: 传播链（JSON）
- `approval_level`: 所需审批级别
- `requested_by`/`approved_by`: 申请人/审批人
- `created_at`/`updated_at`: 时间戳

**总库变更模型** (`LibraryChange`):
- `change_id`: 变更唯一标识（主键）
- `library_id`: 总库ID（外键）
- `change_type`: 变更类型
- `status`: 变更状态
- `title`/`description`: 标题/描述
- `requested_by`/`approved_by`: 申请人/审批人
- `impact_assessment`: 影响评估（JSON）
- `implementation_plan`: 实施计划（JSON）
- `created_at`/`updated_at`: 时间戳

**审批模型** (`Approval`):
- `approval_id`: 审批唯一标识（主键）
- `change_id`: 关联变更ID（外键）
- `approver`: 审批人
- `status`: 审批状态
- `comment`: 审批意见
- `created_at`/`updated_at`: 时间戳

**缺陷模型** (`Defect`):
- `defect_id`: 缺陷唯一标识（主键）
- `project_id`: 关联项目ID（外键）
- `title`/`description`: 标题/描述
- `severity`: 严重程度
- `status`: 缺陷状态
- `created_at`/`updated_at`: 时间戳

**模板模型** (`Template`):
- `template_id`: 模板唯一标识（主键）
- `name`: 模板名称
- `template_type`: 模板类型（built_in/custom）
- `description`: 模板描述
- `structure`: 模板结构定义（JSON）
- `created_at`/`updated_at`: 时间戳

**规范模型** (`Spec`):
- `spec_id`: 规范唯一标识（主键）
- `name`/`version`/`description`: 名称/版本/描述
- `spec_type`: 规范类型
- `content`: 规范内容（JSON）
- `created_at`/`updated_at`: 时间戳

**其他模型**: `LibraryVersion`、`LibraryDependency`、`Impact`、`Milestone`、`Task`、`Plugin`

### 1.2. 核心功能实现

#### 1.2.1. 总库版本控制 ✅
- **版本管理**（`library_version_service.py`）:
  - 总库版本创建与管理
  - 版本变更记录与追踪
  - 版本号遵循语义化版本规范

- **实现方案**:
  - 基于SQLAlchemy ORM的数据版本管理
  - 版本号遵循语义化版本规范（MAJOR.MINOR.PATCH）
  - 通过 `library_version_dao.py` 提供数据访问

#### 1.2.2. 总库变更管理 ✅
- **变更流程**（`change_service.py` + `library_change_service.py`）:
  - V2.1.0 三维分类体系：Domain × Nature × Scope
  - 完整审批链：草稿→提交→审批→实施→完成（含驳回/取消）
  - 变更传播链追踪
  - 分级审批触发机制

- **变更域（Domain）**: code / config / doc / spec / infra
- **变更性质（Nature）**: feature / fix / refactor / enhancement / removal
- **影响范围（Scope）**: local / module / cross_module / cross_project / cross_domain

#### 1.2.3. 总库依赖管理 ✅
- **依赖分析**（`library_dependency_service.py`）:
  - 跨项目依赖识别
  - 依赖关系存储与查询
  - 通过 `library_dependency_dao.py` 数据访问

- **待增强**:
  - 依赖冲突检测
  - 依赖关系图谱可视化

#### 1.2.4. 总库规范管理 ✅
- **规范执行**（`check_service.py` + `spec_service.py`）:
  - 目录结构检查
  - 命名规范检查
  - 文档完整性检查
  - 代码风格检查（SCL命名/结构 + Python命名规范）

- **规范版本**（`library_spec_service.py`）:
  - 规范注册与扫描
  - 规范版本管理

#### 1.2.5. 总库发布管理 ⚠️
- **发布流程**（`build_deploy_service.py`）:
  - 后端服务已实现
  - GUI界面未接入（后续版本补齐）

### 1.3. 技术选型

#### 1.3.1. 核心技术栈（实际使用）
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11.9 | 运行时 |
| PyQt5 | 6.x | GUI框架（Qt6绑定） |
| Flask | 3.1.2 | REST API框架 |
| SQLAlchemy | 2.x | ORM框架 |
| SQLite | 内置 | 本地数据库 |
| Alembic | 最新 | 数据库迁移 |
| Click | 最新 | CLI工具 |

#### 1.3.2. 第三方库
| 库 | 用途 |
|------|------|
| SQLAlchemy | ORM框架 + 数据迁移 |
| Flask | REST API + Blueprint路由 |
| PyQt5 | GUI框架（替代原计划PyQt5） |
| Alembic | 数据库Schema迁移 |
| Jinja2 | 模板引擎 |
| Markdown | 文档生成 |

## 2. 实现路径

### 2.1. 阶段一：核心功能完善 ✅ 已完成
1. **总库版本控制模块** ✅
   - `library_version_service.py` + `library_version_dao.py` + `LibraryVersion` model

2. **总库依赖管理模块** ✅
   - `library_dependency_service.py` + `library_dependency_dao.py` + `LibraryDependency` model

3. **总库规范管理模块** ✅
   - `check_service.py` + `spec_service.py` + `library_spec_service.py`

### 2.2. 阶段二：高级功能开发 🔄 进行中
1. **总库发布管理模块** ⚠️
   - 后端 `build_deploy_service.py` 已实现
   - GUI界面待接入

2. **总库仪表盘** ✅
   - `library_dashboard_service.py` + API路由已实现

3. **跨项目分析工具** ⚠️
   - 依赖分析已有基础，图谱可视化待实现

### 2.3. 阶段三：集成与优化 📋 待启动
1. **API接口完善** — 8个Blueprint路由已实现，Swagger文档待补齐
2. **GUI功能增强** — 9个Widget已实现，构建部署Tab待接入
3. **性能优化** — 数据库索引优化、缓存机制待实现

## 3. 关键技术点

### 3.1. 依赖注入容器
- **实现**: `container.py` 提供DI容器
- **当前状态**: 基础框架存在，部分Service未注册
- **待完善**: 全量Service注册 + 自动注入

### 3.2. 变更管理V2.1.0
- **三维分类**: Domain × Nature × Scope
- **传播链**: JSON存储变更传播路径
- **分级审批**: 根据Scope自动触发对应审批级别
- **变更台账**: `change_analytics_service.py` 提供统计分析

### 3.3. 插件系统
- **插件加载**: `plugin_service.py` 管理插件生命周期
- **插件市场**: `plugin_market_service.py` 在线浏览+安装
- **内置插件**: PLC变量解析器、代码检查、文档生成
- **插件配置**: `plugin_config.py` Widget 提供参数设置界面

### 3.4. 规范检查引擎
- **检查类型**: 目录结构 + 命名规范 + 文档完整性 + 代码风格
- **代码风格**: SCL命名/结构检查 + Python命名规范检查
- **规范注册**: `spec_service.py` + `spec_dao.py` 管理规范元数据

## 4. 预期交付物

### 4.1. 核心模块 ✅ 已交付
- 24个Service模块
- 13个DAO模块
- 16个ORM Model
- 8个API Blueprint路由

### 4.2. API接口 ✅ 已交付
- `/api/libraries` — 总库管理
- `/api/projects` — 项目管理
- `/api/libraries/{id}/changes` — 总库变更
- `/api/libraries/{id}/dashboard` — 仪表盘
- `/api/specs` — 规范管理
- `/api/templates` — 模板管理
- `/api/defects` — 缺陷管理
- `/api/plugins` — 插件管理

### 4.3. GUI组件 ✅ 已交付
- 9个核心Widget + 2个Dialog + 主窗口
- 3个插件UI组件

### 4.4. 待交付
- 构建部署GUI界面
- 依赖关系图谱可视化
- Swagger API文档
- 性能优化（缓存+索引）

## 5. 风险评估

### 5.1. 技术风险
| 风险 | 等级 | 状态 | 应对措施 |
|------|------|------|----------|
| 依赖分析性能 | 高 | 待验证 | 增量分析+缓存+算法优化 |
| DI容器未全量注册 | 中 | 已知 | 逐步补齐Service注册 |
| 规范检查准确性 | 中 | 持续优化 | 建立测试用例+持续优化规则 |
| 变更单ID新格式兼容 | 中 | 已修复 | CHG-{DOMAIN}-{SEQ} 格式已实现 |

### 5.2. 实施风险
| 风险 | 等级 | 状态 | 应对措施 |
|------|------|------|----------|
| plugin_config参数保存 | 中 | 已知 | 需验证持久化机制 |
| 审批人硬编码 | 低 | 已知 | 后续版本引入用户系统 |
| 甘特图30天截断 | 低 | 已知 | 进度管理Widget需修复 |

## 6. 质量保证

### 6.1. 测试策略
- **单元测试**: 核心Service模块测试
- **集成测试**: API接口+数据库流程测试
- **端到端测试**: GUI交互流程测试

### 6.2. 性能指标
| 指标 | 目标 | 当前状态 |
|------|------|----------|
| API响应时间 | < 1秒 | 待测试 |
| 依赖分析时间 | < 30秒 | 待测试 |
| GUI操作响应 | < 500ms | 待测试 |
| 内存使用 | < 500MB | 待测试 |

## 7. 结论

本技术方案已从V1.0.0的规划阶段推进到V2.6.0的实现阶段。核心功能（总库管理、项目管理、变更管理V2.1.0、规范检查、模板管理、插件系统）均已实现。待完善项为构建部署GUI接入、依赖图谱可视化、DI容器全量注册和性能优化。