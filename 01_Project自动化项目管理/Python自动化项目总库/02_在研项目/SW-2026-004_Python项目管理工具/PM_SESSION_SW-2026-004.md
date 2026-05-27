# PM_SESSION_SW-2026-004

## 0. Meta
- project_id: SW-2026-004
- project_name: Python项目管理工具
- project_root: c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-004_Python项目管理工具
- last_updated: 2026-05-27
- owners: 技术团队

## 1. Positioning（项目定位）
- one_liner: 自动化领域全生命周期项目管理工具，支持PLC/Python/上位机多技术栈
- users: 自动化开发团队、PLC工程师、Python开发团队、项目管理人员
- non_goals: 不做在线协作、不做云部署、不做CI/CD流水线

## 2. Current Focus（当前焦点）
- current_focus: V2.5.x稳定版维护 + 散装脚本归位整改
- milestone: V2.5.2 已交付
- acceptance: 散装脚本归位完成，项目根目录整洁

## 3. Status Summary（当前状态摘要）
- in_progress:
  - 散装脚本归位整改（19个诊断/修复/测试脚本）
  - 旧目录 `01_主程序核心_code/` 清理
- next_up:
  - V2.5.9+ 交付清单补全
  - 诊断/修复脚本集成到CLI
- open_questions:
  - 散装脚本中哪些诊断逻辑有持续价值需集成？
  - `01_主程序核心_code/` 目录是否还有依赖？
- risks_dependencies:
  - 散装脚本可能被其他脚本import，删除前需搜索引用
  - 数据库迁移(alembic)状态需确认

## 4. Artifacts Index（文档索引）
- prd:
  - 00_项目基础信息/01-产品需求文档_PRD-V1.0.0.md
- req:
  - 01_项目文档/02_规划过程/01_需求规格说明书_REQ-V1.0.3.md
  - 01_项目文档/02_规划过程/02_迭代需求规格说明书_REQ-V1.1.0.md
- des:
  - 01_项目文档/02_规划过程/08_详细设计文档_DES-V1.0.0.md
- arch:
  - 01_项目文档/02_规划过程/07_架构设计文档_ARCH-V1.0.0.md
- test:
  - 01_项目文档/03_执行过程/03_测试计划_TEST-V1.0.0.md
  - 01_项目文档/03_执行过程/04_综合测试报告_TEST-V1.0.0.md
- change_mgmt:
  - 01_项目文档/04_监控和控制/01_变更管理技术方案_DEV-V2.1.0.md
  - 01_项目文档/04_监控和控制/06_版本变更台帐_CHG-V2.1.0.md
- delivery:
  - 02_发布说明/01_交付清单_DEL-V2.5.2.md
  - 02_发布说明/V2.5.2_更新说明.md

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-05-27 创建PM_SESSION，启动散装脚本归位整改
- iteration_log:
  - 2026-04-16 V2.5.2 Bug Fix Release 交付
- bug_log:
- refactor_log:
  - 2026-05-27 启动散装脚本归位重构（19个文件）
- release_log:
  - 2026-04-16 V2.5.2 Bug Fix Release
  - 2026-04-15 V2.5.1 Bug Fix Release
  - 2026-04-14 V2.5.0 Feature Release
