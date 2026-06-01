# PM_SESSION_FB1014

## 0. Meta
- project_id: FB1014
- project_name: FB_1014_StationConveyor 工站输送机编排器
- project_root: c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\01_SharedLibraries\SysLib\actuator\FB_1014_StationConveyor
- last_updated: 2026-05-31
- owners: Trae

## 1. Positioning（项目定位）
- one_liner: 多模式单口双向输送编排器, 默认B进B出, 支持拍正对齐
- users: PLC程序员(OB1实例化), 产线工程师(参数配置)
- non_goals: 不直接驱动物理IO, 不实例化执行器FB(FB_1011/FB_1012在OB1)

## 2. Current Focus（当前焦点）
- current_focus: V6.0.0 B进B出模式工艺重构 + 多模式接口
- milestone: V6.0.0
- acceptance: Mode=1 B进B出完整工艺验证, Mode=0 正常模式回归, SCL/PRD/IFC/DSN同步更新

## 3. Status Summary（当前状态摘要）
- in_progress:
  - V6.0.0 PRD/IFC/DSN/PFL全部文档更新
  - SCL V6.0.0源码注释中文化
- next_up:
  - OB1接线更新适配i_iMode
  - Mode=2 A侧双向预留实现
- open_questions:
  - Mode=2 A侧双向的完整工艺时序待定义
- risks_dependencies:
  - 依赖FB_1011 V9.0.0 + FB_1012 V9.0.0
  - OB1中需新增i_iMode连线
- spec_compliance:
  - last_check: 2026-05-31
  - result: 待验证

## 4. Artifacts Index（文档索引）
- prd:
  - PRD/需求文档_PRD-FB1014-StationConveyor-V6.0.0.md
- pfl:
  - PRD/工艺流程_PFL-FB1014-StationConveyor-V6.0.0.md
- ifc:
  - PRD/接口文档_IFC-FB1014-StationConveyor-V6.0.0.md
- des:
  - PRD/详细设计说明书_DSN-FB1014-StationConveyor-V6.0.0.md
- src:
  - FB_1014_StationConveyor.scl

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-05-31 V6.0.0 B进B出模式工艺重构+多模式接口, Breaking Change, 已完成
  - 2026-05-31 V5.0.0 纯编排器重构, Breaking Change, 已完成