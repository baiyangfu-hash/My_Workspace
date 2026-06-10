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
  - 00_项目基础信息/01-产品需求文档_PRD.md
- req:
  - 01_项目文档/02_规划过程/01_需求规格说明书_REQ.md
  - 01_项目文档/02_规划过程/02_迭代需求规格说明书_REQ.md
- des:
  - 01_项目文档/02_规划过程/08_详细设计文档_DES.md
- arch:
  - 01_项目文档/02_规划过程/07_架构设计文档_ARCH.md
- test:
  - 01_项目文档/03_执行过程/03_测试计划_TEST.md
  - 01_项目文档/03_执行过程/04_综合测试报告_TEST.md
- change_mgmt:
  - 01_项目文档/04_监控和控制/01_变更管理技术方案_DEV.md
  - 01_项目文档/04_监控和控制/06_版本变更台帐_CHG.md
- delivery:
  - 02_发布说明/01_交付清单_DEL.md
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

## Spec Snapshot（初始化时锁定，供后续版本漂移检测）

> 以下版本号在项目初始化时从 `spec_registry.json` 读取并填入。
> 本区块作为基线，后续 `specmgr check` 对比当前规范版本与快照，检测版本漂移。

| spec_id | 版本 | 记录日期 | 说明 |
|---------|------|---------|------|
| PROJ-016 | V1.0.0 | 2026-06-06 | 通用项目结构模板 |
| REQ-020 | V1.1.0 | 2026-06-06 | 通用需求分析文档模板 |
| LSP-905 | V1.0.2 | 2026-06-06 | SCL编程规范 |
| LSP-904 | V1.2.0 | 2026-06-06 | SCL注释规范 |
| LSP-903 | V2.1.0 | 2026-06-06 | 定时器使用规范 |
| LSP-906 | V1.0.0 | 2026-06-06 | PLC编程错误预防规则 |
| LSP-907 | V1.0.0 | 2026-06-06 | PLC项目配置规范 |
| INT-815 | V1.1.0 | 2026-06-06 | PLC接口文档模板 |
| PLC-023 | V2.0.0 | 2026-06-06 | PLC程序设计文档模板 |
| DEV-004 | V1.1.1 | 2026-06-06 | 通用项目文档版本管理与变更核心规范 |
| CHG-040 | V2.0.0 | 2026-06-06 | 通用变更单模板 |
| CHG-041 | V2.1.0 | 2026-06-06 | 通用版本变更台帐模板 |
| PM-042 | V2.1.0 | 2026-06-06 | 通用变更管理流程规范 |

## 6. Implementation Log
- 2026-05-27 | skill=pm-workflow | mode=项目初始化
  - goal: 创建PM_SESSION，启动散装脚本归位整改
  - changed_files: PM_SESSION_SW-2026-004.md
  - impact: 项目具备PM_SESSION驱动能力
  - risks: 散装脚本可能被其他脚本import，删除前需搜索引用

## 7. Verification Log
- 2026-05-27
  - verified: PM_SESSION已创建
  - not_verified: 散装脚本归位完成，数据库迁移状态
  - method: 文件存在性检查
  - blocker: 散装脚本引用关系需排查

## 8. Handoff Notes
- 2026-05-27 | from=pm-workflow
  - current_state: V2.5.x稳定版维护中，散装脚本归位整改进行中
  - next_focus: 完成散装脚本归位，补全交付清单
  - watchouts: 散装脚本可能被import; 数据库迁移状态需确认; .env含硬编码密钥需轮换
  - read_first: PM_SESSION_SW-2026-004.md

## 9. Next Actions
- [P1] 完成散装脚本归位整改 | precondition=排查所有import引用 | done_when=19个散装脚本归位到scripts/目录
- [P1] .env密钥轮换 + 加入.gitignore | precondition=确认.env未被提交到版本库 | done_when=API_SECRET_KEY已更换为随机值且.env在.gitignore中
- [P2] V2.5.9+交付清单补全 | precondition=散装脚本归位完成 | done_when=交付清单DEL.md更新至最新版本
