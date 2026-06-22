# PM_SESSION_SW-2026-007

> **归档通知**: 本项目（SW-2026-007 pm-mgr）已被 SW-2026-008 auto-pm 取代。
> 所有 pm-mgr 功能已迁移至 auto-pm，pm-workflow 技能已更新为调用 auto-pm。
> 本项目不再维护，仅供历史参考。

## 0. Meta
- project_id: SW-2026-007
- project_name: pm工作流工具链 (pm-mgr)
- status: 已归档
- project_root: c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-007_pm工作流工具链
- last_updated: 2026-06-19
- owners: fubai

## 1. Positioning（项目定位）
- one_liner: pm-workflow技能的CLI工具链，提供项目初始化、旧项目补完、健康检查、类型检测和Spec Snapshot管理
- users: AI助手(pm-workflow技能)、开发者
- non_goals: 不做GUI、不做规范内容编辑、不做在线协作
- key_principle: 自身必须符合规范才能管理其他项目

## 2. Current Focus（当前焦点）
- current_focus: V0.1.0功能修复 — 补全规范列表、修复搜索深度、增强健康检查
- milestone: V0.2.0 功能完善
- acceptance: pm-mgr check 对自身执行全部通过 / snapshot 包含完整规范列表 / detect 5秒内返回

## 3. Status Summary（当前状态摘要）
- in_progress:
  - 代码功能修复（detect/snapshot/check/bootstrap）
  - PM-004规范升级对齐
- next_up:
  - 补充单元测试
  - 安装到全局环境（pip install -e .）
- open_questions:
  - 是否需要支持自定义 SPEC_IDS（用户扩展规范列表）
- risks_dependencies:
  - 依赖 spec_registry.json 格式稳定性
  - 依赖 .trae/project-bootstrap/ 模板目录结构

## 4. Artifacts Index（文档索引）
- prd:
  - README.md（当前作为产品说明）
- req:
  - (待创建)
- des:
  - (待创建)
- test:
  - (待创建)
- change_mgmt:
  - (无)
- delivery:
  - (无)

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-06-06 创建PM_SESSION，启动功能修复
- iteration_log:
  - V0.1.0 初始版本完成（5个子命令可用）
- bug_log:
  - detect.py rglob无深度限制，大目录扫描极慢
  - snapshot.py SPEC_IDS硬编码且不完整
  - check.py 缺少PM_SESSION章节完整性检查
  - bootstrap.py software目录结构缺PM流程子目录
- refactor_log:
- release_log:
  - V0.1.0 初始版本

## 6. Implementation Log
- 2026-06-06 | skill=pm-workflow | mode=规范
  - goal: 创建PM_SESSION并修复代码功能缺陷
  - changed_files: PM_SESSION_SW-2026-007.md, detect.py, snapshot.py, check.py, bootstrap.py
  - artifacts: PM_SESSION
  - impact: 项目具备完整的PM_SESSION驱动能力
  - risks: 仍需补充单元测试和安装验证

## 7. Verification Log
- 2026-06-06
  - verified:
    - PM_SESSION 文件已生成
  - not_verified:
    - pm-mgr check 对自身执行结果
    - 单元测试覆盖
  - method:
    - 文件存在性检查
  - blocker:
    - pm-mgr 未安装到全局环境

## 8. Handoff Notes
- 2026-06-06 | from=pm-workflow
  - current_state: PM_SESSION已创建，代码修复进行中
  - next_focus: 完成代码修复后安装到全局环境验证
  - watchouts:
    - pm-mgr 未安装到全局环境，需 pip install -e . 后验证
  - read_first:
    - PM_SESSION_SW-2026-007.md
    - README.md

## 9. Next Actions
- [P0] 完成代码修复(detect/snapshot/check/bootstrap) | precondition=无 | done_when=pm-mgr check 对自身全部通过
- [P1] 安装到全局环境验证 | precondition=P0通过 | done_when=pm-mgr detect/check/snapshot 命令全局可用
- [P2] 补充单元测试 | precondition=P0通过 | done_when=pytest 覆盖所有修复点

## Spec Snapshot（初始化时锁定，供后续版本漂移检测）

> 以下版本号在项目初始化时从 `spec_registry.json` 读取并填入。
> 本区块作为基线，后续 `specmgr check` 对比当前规范版本与快照，检测版本漂移。

| spec_id | 版本 | 记录日期 | 说明 |
|---------|------|---------|------|
| PROJ-016 | V1.0.0 | 2026-06-06 | 通用项目结构模板 |
| PRD-001 | V1.0.0 | 2026-06-06 | 产品需求文档模板 |
| DEV-031 | V1.0.0 | 2026-06-06 | 通用测试规范 |
| DEV-032 | V1.0.0 | 2026-06-06 | GUI测试方案标准 |
| DEV-210 | V1.1.0 | 2026-06-06 | Python编程规范 |
| DEV-211 | V1.0.0 | 2026-06-06 | Python代码审查规范 |
| DEV-220 | V2.2.0 | 2026-06-06 | Python项目打包规范 |
| INT-215 | V1.0.0 | 2026-06-06 | Python接口文档模板 |
| DEV-004 | V1.1.1 | 2026-06-06 | 通用项目文档版本管理与变更核心规范 |
| CHG-040 | V2.0.0 | 2026-06-06 | 通用变更单模板 |
| CHG-041 | V2.1.0 | 2026-06-06 | 通用版本变更台帐模板 |
| PM-042 | V2.1.0 | 2026-06-06 | 通用变更管理流程规范 |
