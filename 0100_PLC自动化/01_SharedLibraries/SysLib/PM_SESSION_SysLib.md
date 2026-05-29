# PM_SESSION_SysLib

## 0. Meta
- project_id: SysLib
- project_name: PLC共享函数库 (Shared Libraries for PLC)
- project_root: 0100_PLC自动化\01_SharedLibraries\SysLib
- last_updated: 2026-05-29
- owners: Trae

## 1. Positioning（项目定位）
- one_liner: 为PLC项目提供可复用的标准功能块（定时器/计数器/执行器/通讯握手/边沿检测/类型定义等）
- users: DJ-2026-005及其他PLC项目
- non_goals: 不处理项目级业务逻辑，不包含HMI/SCADA层代码

## 2. Current Focus（当前焦点）
- current_focus: FB1020设备通讯握手功能块 V1.1.0 通用化重构完成
- milestone: V1.1.0
- acceptance: 纯协议逻辑(传输层无关), DSN+IFC+SCL+Types四文档同步, 可配置时序参数

## 3. Status Summary（当前状态摘要）
- in_progress:
  - FB1020 EquipmentHandshake V1.1.0 通用化重构完成 (2026-05-29)
  - FB1013 V9.0.0 I/O精简重构完成 (2026-05-29)
- next_up:
  - FB1020在实际项目中集成验证（OB1接线+通讯层映射）
  - FB1011/FB1012类似I/O精简 (待评估)
  - V9.0.0版本在实际项目中验证
- open_questions:
  - OB1侧的信号映射代码需要编写（io_stUpStream/io_stDownStream ↔ 通讯层）
  - GlassID中文字符编码在通讯传输中的处理方案
  - V7.0.0旧版接口的迁移方案（是否有旧实例需要更新）
- risks_dependencies:
  - 依赖ST_Cylinder V1.1.0和ST_ConveyorMotor V1.1.0结构体定义
  - WORD类型报警需要FB_2001报警管理块适配
  - FB_1020信号映射由调用方负责，需确保通讯层正确对接
- spec_compliance:
  - last_check: 2026-05-29
  - result: 通过

## 4. Artifacts Index（文档索引）
- prd:
  - communication/PRD/接口文档_IFC-FB1020-EquipmentHandshake-V1.1.0.md
  - actuator/PRD/接口文档_IFC-FB1013-NinetyDegreeTransfer-V9.0.0.md
- des:
  - communication/PRD/详细设计说明书_DSN-FB1020-EquipmentHandshake-V1.1.0.md
  - actuator/PRD/详细设计说明书_DSN-FB1013-NinetyDegreeTransfer-V9.0.0.md
- src:
  - communication/FB_1020_EquipmentHandshake.scl (V1.1.0)
  - actuator/FB_1013_NinetyDegreeTransfer.scl (V9.0.0)
  - actuator/FB_1011_CylinderControl.scl (V8.0.0)
  - actuator/FB_1012_ConveyorMotor.scl (V8.0.0)
- types:
  - types/ST_HandshakeBits.scl (V1.1.0)
  - types/ST_HandshakeCh.scl (V1.1.0)
  - types/ST_ProductData.scl (V1.0.0)
  - types/ST_Cylinder.scl (V1.1.0)
  - types/ST_ConveyorMotor.scl (V1.1.0)
  - types/ST_ExternalDevice.scl (V1.0.0)

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-05-29 FB1020 V1.0.0新增: 解析各設備交握-5.20.xlsx, 输出IFC+SCL+Types, 双通道状态机+心跳监视+产品数据透传 范围:communication/ + types/ 完成
- refactor_log:
  - 2026-05-29 FB1020 V1.1.0通用化重构: 剥离Modbus依赖→纯协议逻辑, 新增i_bTransportDone/i_dReqDelayMs/i_dHbToggleMs/i_dHbTimeoutMs/i_dCompleteMs可配置参数, 新增q_iUpState/q_iDownState诊断输出, DSN+IFC同步V1.1.0, Types去除Modbus地址注释 范围:FB_1020+DSN+IFC+3个Types 完成
  - 2026-05-29 FB1013 VAR_OUTPUT精简: 70→25个(-45), M0-M10删除, 报警合并WORD, NV合并BYTE, 位置合并INT, IFC/DSN同步升V9.0.0 范围:FB_1013_NinetyDegreeTransfer.scl+IFC+DSN 完成
