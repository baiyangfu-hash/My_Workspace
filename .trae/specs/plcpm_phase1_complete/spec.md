# PLCPM Phase 1 完善与扩展 Spec

## Why
当前 PLCPM 项目已建立核心框架（Core/Model/DAO/Service层基础），但缺少关键组件以实现可运行的 MVP。需要完善 Phase 1 剩余工作并为后续 Phase 奠定坚实基础，确保 Trae 国际版可以无缝继续开发。

## What Changes
- **补全 DAO 层**: 新增 ChangeDAO、MilestoneDAO
- **补全 Service 层**: 新增 ChangeService、MilestoneService
- **新增测试框架**: pytest 配置 + 核心模块单元测试
- **新增基础 UI**: PyQt5 主窗口框架（空壳但可运行）
- **内置模板初始化**: DJ/ZD 基础模板数据种子
- **新增工具函数**: UUID生成器、日期工具等
- **完善异常处理**: 统一异常类体系
- **API 层基础**: Flask 应用工厂模式
- **CLI 层基础**: Click 命令行入口
- **文档补全**: Service层规格、API规格、UI规格

## Impact
- Affected specs: 全局架构完整性
- Affected code:
  - `src/dao/change_dao.py` (新建)
  - `src/dao/milestone_dao.py` (新建)
  - `src/services/change_service.py` (新建)
  - `src/services/milestone_service.py` (新建)
  - `src/core/exceptions.py` (新建)
  - `src/core/utils.py` (新建)
  - `src/api/app.py` (新建)
  - `src/api/routes/project_routes.py` (新建)
  - `src/cli/main.py` (新建)
  - `src/ui/main_window.py` (新建)
  - `tests/conftest.py` (新建)
  - `tests/test_core/` (新建目录)
  - `tests/test_models/` (新建目录)
  - `tests/test_dao/` (新建目录)
  - `tests/test_services/` (新建目录)
  - `config/templates/` (新建目录 + 模板种子数据)
  - `docs/specs/service_spec.md` (新建)
  - `docs/specs/api_spec.md` (新建)
  - `docs/specs/ui_spec.md` (新建)

## ADDED Requirements

### Requirement: 完整的 CRUD 数据访问层
系统 SHALL 为所有数据模型提供完整的数据访问对象（DAO），包括 Project、Template、Change、Milestone。

#### Scenario: ChangeDAO 完整操作
- **WHEN** 调用 ChangeDAO.create() 创建变更单
- **THEN** 变更单被持久化到数据库并返回带ID的对象
- **WHEN** 调用 ChangeDAO.list_all(project_id, status, type) 查询变更单列表
- **THEN** 返回符合筛选条件的变更单列表
- **WHEN** 调用 ChangeDAO.update_status() 更新状态
- **THEN** 状态按状态机规则转换

#### Scenario: MilestoneDAO 完整操作
- **WHEN** 调用 MilestoneDAO.create() 创建里程碑
- **THEN** 里程碑关联到指定项目
- **WHEN** 调用 MilestoneDAO.list_by_project() 按项目查询
- **THEN** 返回该项目的所有里程碑

### Requirement: 变更管理业务逻辑
系统 SHALL 提供完整的变更管理业务服务，包括变更单生命周期管理和审批流程。

#### Scenario: 变更单状态流转
- **WHEN** 从 DRAFT 状态调用 approve()
- **THEN** 状态变为 PENDING
- **WHEN** 从 PENDING 状态调用 implement()
- **THEN** 状态变为 IMPLEMENTED
- **WHEN** 尝试非法状态转换
- **THEN** 抛出 InvalidStatusTransition 异常

#### Scenario: 项目变更统计
- **WHEN** 调用 get_project_change_stats()
- **THEN** 返回该项目各类型变更的数量统计

### Requirement: 里程碑管理业务逻辑
系统 SHALL 提供里程碑创建、更新和完成跟踪功能。

#### Scenario: 里程碑完成
- **WHEN** 调用 complete_milestone()
- **THEN** 状态变为 COMPLETED，completed_at 设置为当前时间

#### Scenario: 项目进度计算
- **WHEN** 调用 get_project_progress()
- **THEN** 返回完成百分比和里程碑统计信息

### Requirement: 统一异常处理体系
系统 SHALL 定义统一的异常类层次结构，支持国际化错误消息。

#### Exception Hierarchy:
```
PLCPMBaseException
├── DatabaseError        # 数据库操作错误
├── ValidationError      # 数据校验错误
├── NotFoundError        # 资源未找到
├── DuplicateError       # 重复资源错误
└── BusinessError        # 业务逻辑错误
    └── InvalidStatusTransitionError  # 无效状态转换
```

### Requirement: 测试基础设施
系统 SHALL 提供 pytest 测试框架配置和核心模块的基础测试用例。

#### Scenario: 测试运行
- **WHEN** 执行 `pytest tests/ -v`
- **THEN** 所有核心模块测试通过
- **AND** 测试覆盖率报告生成

### Requirement: 基础 UI 主窗口
系统 SHALL 提供可运行的 PyQt5 主窗口框架，包含菜单栏、工具栏和状态栏。

#### Scenario: 启动 GUI
- **WHEN** 运行 `python -m src.ui.main_window`
- **THEN** 显示主窗口，包含文件/编辑/视图/帮助菜单
- **AND** 工具栏包含常用操作按钮
- **AND** 状态栏显示应用信息和时间

### Requirement: Flask API 基础
系统 SHALL 提供 Flask 应用工厂模式和基础的 REST API 路由。

#### Scenario: API 启动
- **WHEN** 运行 `python -m src.api.app`
- **THEN** Flask 服务启动在配置的端口
- **AND** `/api/projects` 返回项目列表 JSON

### Requirement: Click CLI 入口
系统 SHALL 提供命令行接口用于快速操作。

#### Scenario: CLI 帮助
- **WHEN** 运行 `plcpm --help`
- **THEN** 显示可用命令列表和用法说明

### Requirement: 内置模板种子数据
系统 SHALL 在首次启动时自动初始化 DJ/ZD 业务线的基础模板。

#### Scenario: 首次启动
- **WHEN** 数据库中无模板记录
- **THEN** 自动创建 TPL-DJ-S001（小型单机设备）模板
- **AND** 自动创建 TPL-DJ-M001（中大型单机设备）模板
- **AND** 自动创建 TPL-ZD-L001（自动化整线）模板

## MODIFIED Requirements

### Requirement: Application 初始化流程增强
应用初始化 SHALL 在数据库就绪后执行种子数据初始化和插件扫描。

- **MODIFIED**: `Application.initialize()` 方法增加种子数据和插件加载步骤
- **BREAKING**: 无（向后兼容）

## REMOVED Requirements
无
