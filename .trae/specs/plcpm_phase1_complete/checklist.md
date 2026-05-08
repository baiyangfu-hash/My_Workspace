# Checklist

## Core 层补全
- [x] `src/core/exceptions.py` 存在且包含完整的异常类层次结构
- [x] PLCPMBaseException 基类定义正确，支持错误码和消息
- [x] DatabaseError, ValidationError, NotFoundError, DuplicateError 子类存在
- [x] BusinessError 和 InvalidStatusTransitionError 存在
- [x] `src/core/utils.py` 存在且包含 UUID 生成器
- [x] 日期工具函数 (format_datetime, parse_datetime) 可正常工作
- [x] 字符串工具函数可正常工作

## DAO 层补全
- [x] `src/dao/change_dao.py` 文件存在
- [x] ChangeDAO.create() 可创建变更单并返回带ID对象
- [x] ChangeDAO.get_by_id() 可按ID查询变更单
- [x] ChangeDAO.list_all() 支持多条件筛选（project_id, status, type）
- [x] ChangeDAO.update_status() 可更新状态
- [x] ChangeDAO.count_by_type() 返回各类型统计
- [x] `src/dao/milestone_dao.py` 文件存在
- [x] MilestoneDAO.create() 可创建里程碑
- [x] MilestoneDAO.list_by_project() 可按项目查询里程碑
- [x] MilestoneDAO.complete() 可完成里程碑

## Service 层补全
- [x] `src/services/change_service.py` 文件存在
- [x] ChangeService.create_change() 包含数据校验逻辑
- [x] 状态机 transition_status() 方法实现完整的状态转换规则
- [x] approve/reject/implement/close 业务方法存在且逻辑正确
- [x] 非法状态转换抛出 InvalidStatusTransitionError
- [x] get_project_change_stats() 返回正确的统计数据
- [x] `src/services/milestone_service.py` 文件存在
- [x] MilestoneService.create_milestone() 可创建里程碑
- [x] MilestoneService.complete_milestone() 设置 completed_at 时间戳
- [x] MilestoneService.get_project_progress() 计算进度百分比

## 种子数据与初始化
- [x] DJ小型单机设备模板 JSON 文件存在于 config/templates/
- [x] `src/services/seed_service.py` 文件存在
- [x] Application.initialize() 调用种子数据初始化（通过SeedService）

## API 层基础
- [x] `src/api/app.py` Flask 应用工厂存在
- [x] GET /api/projects 返回项目列表JSON
- [x] GET /api/projects/<id> 返回项目详情
- [x] POST /api/projects 创建新项目
- [x] PUT /api/projects/<id> 更新项目信息
- [x] DELETE /api/projects/<id> 执行软删除
- [x] 统一错误响应格式（code, message, data）
- [x] 404/400/500 错误处理正确

## CLI 层基础
- [x] `src/cli/main.py` Click CLI入口存在
- [x] CLI 命令组 (init/project/template) 存在
- [x] 项目管理命令 (list/create) 存在
- [x] 模板管理命令 (list/init) 存在

## UI 基础框架
- [x] `src/ui/main_window.py` 主窗口类存在
- [x] 主窗口包含菜单栏（文件/编辑/视图/帮助）
- [x] 工具栏包含新建/打开/保存/删除按钮
- [x] 状态栏显示应用信息和当前时间
- [x] 中央区域使用QTabWidget占位
- [x] `src/ui/__main__.py` 启动入口存在

## 测试基础设施
- [x] `tests/conftest.py` pytest配置存在
- [x] pytest.ini 配置文件存在
- [x] test_core/test_path_resolver.py 路径解析测试存在
- [x] test_core/test_config.py 配置管理测试存在
- [x] test_models/test_project.py Project模型测试存在
- [x] test_models/test_change.py Change模型测试存在
- [x] test_dao/test_project_dao.py DAO测试存在
- [x] test_dao/test_change_dao.py ChangeDAO测试存在
- [x] test_services/test_project_service.py Service层测试存在

## 文档完善
- [x] docs/specs/service_spec.md Service层规格文档存在且完整
- [x] docs/specs/api_spec.md API层规格文档存在且完整
- [x] docs/specs/ui_spec.md UI层规格文档存在且完整

## 集成验证
- [x] verify_project.py 检查项覆盖所有新增组件
- [x] 项目目录结构完整（src/core/models/dao/services/api/cli/ui/tests/docs/config）
