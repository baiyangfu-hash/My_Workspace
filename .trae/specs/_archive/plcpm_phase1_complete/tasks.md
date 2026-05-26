# Tasks

## Phase 1A: 核心层补全（无依赖，可并行）

- [x] Task 1: 创建统一异常处理体系
  - [x] 1.1 创建 `src/core/exceptions.py`，定义 PLCPMBaseException 及子类
  - [x] 1.2 实现 DatabaseError, ValidationError, NotFoundError, DuplicateError
  - [x] 1.3 实现 BusinessError 和 InvalidStatusTransitionError
  - [x] 1.4 所有异常支持国际化消息和错误码

- [x] Task 2: 创建通用工具函数模块
  - [x] 2.1 创建 `src/core/utils.py`
  - [x] 2.2 实现 generate_uuid() - UUID生成器
  - [x] 2.3 实现日期工具函数 (format_datetime, parse_datetime)
  - [x] 2.4 实现字符串工具函数 (truncate, sanitize)
  - [x] 2.5 实现字典深度合并工具

## Phase 1B: DAO 层补全（依赖 Task 1）

- [x] Task 3: 实现 ChangeDAO 数据访问对象
  - [x] 3.1 创建 `src/dao/change_dao.py`
  - [x] 3.2 实现 create(change) - 创建变更单
  - [x] 3.3 实现 get_by_id / get_by_project_id - 查询方法
  - [x] 3.4 实现 list_all(project_id, status, type) - 多条件列表查询
  - [x] 3.5 实现 update() / update_status() - 更新方法
  - [x] 3.6 实现统计方法 count_by_type(), count_by_status()

- [x] Task 4: 实现 MilestoneDAO 数据访问对象
  - [x] 4.1 创建 `src/dao/milestone_dao.py`
  - [x] 4.2 实现 create(milestone) - 创建里程碑
  - [x] 4.3 实现 get_by_id / list_by_project - 查询方法
  - [x] 4.4 实现 update() / complete() - 更新和完成方法
  - [x] 4.5 统计方法 count_by_status()

## Phase 1C: Service 层补全（依赖 Task 3, 4）

- [x] Task 5: 实现 ChangeService 变更管理服务
  - [x] 5.1 创建 `src/services/change_service.py`
  - [x] 5.2 实现 create_change() - 创建变更单（含校验）
  - [x] 5.3 实现状态机 transition_status() 方法
  - [x] 5.4 实现 approve() / reject() / implement() / close() 业务方法
  - [x] 5.5 实现 get_project_change_stats() 统计方法
  - [x] 5.6 状态转换规则验证逻辑

- [x] Task 6: 实现 MilestoneService 里程碑服务
  - [x] 6.1 创建 `src/services/milestone_service.py`
  - [x] 6.2 实现 create_milestone() - 创建里程碑
  - [x] 6.3 实现 complete_milestone() - 完成里程碑
  - [x] 6.4 实现 get_project_progress() - 计算项目进度
  - [x] 6.5 实现 list_milestones_by_project() - 查询项目里程碑

## Phase 1D: 种子数据与初始化增强

- [x] Task 7: 创建内置模板种子数据
  - [x] 7.1 创建 `config/templates/dj_small_device.json` - DJ小型单机设备模板
  - [x] 7.4 创建 `src/services/seed_service.py` - 种子数据初始化服务

## Phase 1E: API 层基础（依赖 Task 5, 6）

- [x] Task 8: 实现 Flask API 基础框架
  - [x] 8.1 创建 `src/api/app.py` - Flask 应用工厂
  - [x] 8.2 创建 `src/api/routes/__init__.py`
  - [x] 8.3 创建 `src/api/routes/project_routes.py` - 项目API路由
  - [x] 8.4 实现 GET /api/projects - 项目列表
  - [x] 8.5 实现 GET /api/projects/<id> - 项目详情
  - [x] 8.6 实现 POST /api/projects - 创建项目
  - [x] 8.7 实现 PUT /api/projects/<id> - 更新项目
  - [x] 8.8 实现 DELETE /api/projects/<id> - 删除项目（软删除）
  - [x] 8.9 统一错误处理和响应格式

## Phase 1F: CLI 层基础

- [x] Task 9: 实现 Click 命令行接口
  - [x] 9.1 创建 `src/cli/main.py` - CLI入口
  - [x] 9.2 实现 `plcpm init` - 初始化项目命令
  - [x] 9.3 实现 `plcpm project list` - 列出项目
  - [x] 9.4 实现 `plcpm project create` - 创建项目
  - [x] 9.5 实现 `plcpm template list` - 列出模板
  - [x] 9.6 实现 `plcpm --version` 显示版本信息

## Phase 1G: UI 基础框架

- [x] Task 10: 实现 PyQt5 主窗口框架
  - [x] 10.1 创建 `src/ui/main_window.py` - 主窗口类
  - [x] 10.2 实现菜单栏（文件/编辑/视图/帮助）
  - [x] 10.3 实现工具栏（新建/打开/保存/删除）
  - [x] 10.4 实现状态栏（状态信息/时间显示）
  - [x] 10.5 实现中央区域（QTabWidget占位）
  - [x] 10.6 创建 `src/ui/__main__.py` - GUI启动入口

## Phase 1H: 测试基础设施

- [x] Task 11: 配置测试框架并编写核心测试
  - [x] 11.1 创建 `tests/conftest.py` - pytest配置和fixtures
  - [x] 11.2 创建 `tests/test_core/test_path_resolver.py` - 路径解析测试
  - [x] 11.3 创建 `tests/test_core/test_config.py` - 配置管理测试
  - [x] 11.4 创建 `tests/test_models/test_project.py` - Project模型测试
  - [x] 11.6 创建 `tests/test_models/test_change.py` - Change模型测试
  - [x] 11.7 创建 `tests/test_dao/test_project_dao.py` - ProjectDAO测试
  - [x] 11.8 创建 `tests/test_dao/test_change_dao.py` - ChangeDAO测试
  - [x] 11.9 创建 `tests/test_services/test_project_service.py` - ProjectService测试
  - [x] 11.10 创建 `pytest.ini` - pytest配置文件

## Phase 1I: 文档完善

- [x] Task 12: 补全模块规格文档
  - [x] 12.1 创建 `docs/specs/service_spec.md` - Service层规格说明书
  - [x] 12.2 创建 `docs/specs/api_spec.md` - API层规格说明书
  - [x] 12.3 创建 `docs/specs/ui_spec.md` - UI层规格说明书

# Task Dependencies
- [Task 3, 4] depends on [Task 1]
- [Task 5] depends on [Task 3]
- [Task 6] depends on [Task 4]
- [Task 8] depends on [Task 5, 6]
- [Task 11] depends on [Task 1, 2, 3, 4, 5, 6]

# Parallelizable Groups
- **Group A** (无依赖): Task 1, Task 2 ✅
- **Group B** (依赖Group A): Task 3, Task 4 ✅
- **Group C** (依赖Group B): Task 5, 6, 7, 9, 10 ✅
- **Group D** (依赖Group C): Task 8, 11, 12 ✅
