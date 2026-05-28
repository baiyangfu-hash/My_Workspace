# PM_SESSION_0100_PLC

## 0. Meta
- project_id: 0100_PLC
- project_name: PLC自动化项目库
- project_root: c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化
- last_updated: 2026-05-27 (FB_1011/FB_1012重构为VAR_IN_OUT结构体参数)
- owners: PLC开发团队

## 1. Positioning（项目定位）
- one_liner: PLC自动化工程项目的规范化工作区，整合通用规范、共享库和项目实例
- users: PLC开发工程师、项目经理、调试维护人员
- non_goals: 不包含机械设计、电气原理图绘制等非软件范畴

## 2. Current Focus（当前焦点）
- current_focus: 变量结构化重构 V8.0 - SysLib/types/ 跨项目结构体库 + DJ-2026-005集成验证
- milestone: 阶段5 - 变量结构化重构（V8.0.0）
- acceptance:
  - ✅ 决策确认：结构体存放位置 SysLib/types/（必须跨项目复用）
  - ✅ 决策确认：嵌套深度 ≤3层
  - ✅ 决策确认：单文件多TYPE定义（对齐GlobalVars.db风格）
  - ✅ 决策确认：完整PLCopen标准（每FB独立Done/Busy/CommandAborted/Error）
  - ✅ Phase 0: SysLib/types/ 目录创建 + 8个结构体定义
  - ✅ Phase 1: ST_ServoAxis V2.0 完成（对齐PLCopen五图标准，25字段四段式）
  - ✅ Phase 1: ST_ServoAxis V3.0 完成（按SV功能块分组嵌套，74字段，10个TYPE，新增Halt/Rel/Reset）
  - ✅ Phase 3: FB_1003 V7.0 集成ST_ServoAxis V3.0 (VAR_IN_OUT直连, 完整Power→ABS→Stop流程)
  - ✅ Phase 2: ST_Cylinder V1.1 + ST_ConveyorMotor V1.1 验证完成(FB_1011/FB_1012改用VAR_IN_OUT结构体参数)
  - ⬜ Phase 2: ST_DualSensor/ST_ConveyorLayer/ST_ProductSensors/ST_ExternalDevice 仍待验证
  - ⬜ Phase 4: FB_1004 集成astServoAxis[3](X2轴)

## 3. Status Summary（当前状态摘要）

### 📦 项目库架构（4大模块）

| 模块 | 路径 | 版本 | 状态 | 说明 |
|------|------|------|------|------|
| **通用规范库** | `00_通用规范/` | V2.0.0 | ✅ 成熟 | 8份规范文档（SCL编程/注释/定时器/错误预防/配置等）|
| **共享功能库** | `01_SharedLibraries/SysLib/` | V2.0.0 | ✅ 成熟 | IEC 61131-3标准库（定时器/计数器/边沿/执行器等17个FB/FC）|
| **示例项目** | `DJ-2026-000/` | V1.0.0 | ✅ 完成 | 阀门控制示例（教学用）|
| **主项目** | `DJ-2026-005/` | V2.0.0 | 🔄 进行中 | 边框缓存机（Conveyor重构阶段4完成）|

### 🔧 共享库（SysLib）模块清单

```
01_SharedLibraries/SysLib/
├── timer/      (4个) FB_TON, FB_TOF, FB_TONR, FB_TP
├── convert/    (4个) FC_DINT_TO_TIME, FC_TIME_TO_DINT, FC_INT_TO_TIME, FC_TIME_TO_INT
├── counter/    (3个) FB_CTU, FB_CTD, FB_CTUD
├── edge/       (2个) FB_R_TRIG, FB_F_TRIG
├── log/        (1个) FC_LogMsg
├── pulse/      (1个) FB_TaktGenerator
└── actuator/   (2个) 🆕 FB_1011(气缸), FB_1012(电机)
```

### 📊 主项目 DJ-2026-005 当前状态

- **项目名称**: 边框缓存机 PLC/HMI 软件工程
- **当前里程碑**: 阶段4 - Conveyor子系统架构重构 V7.0.0 ✅ 已完成
- **核心成果**:
  - ✅ FB_1001 取消（87接口→0），系统总接口 -57%
  - ✅ FB_1002 瘦身为编排器（39→33接口）+ 9步状态机
  - ✅ FB_1011/FB_1012 抽取为通用执行器库（可复用）
  - ✅ DB1/OB1/全部PRD文档同步升级至 V7.0.0
- **待决策事项**:
  - ⬜ AxisControl独立轴FB是否需要
  - ⬜ TIA Portal编译验证时机
  - ⬜ 阶段5：变量结构化重构 V8.0.0（2026-05-20 决策确认中）

### 🔧 阶段5：变量结构化重构（进行中）

| 决策项 | 决策结果 | 日期 |
|--------|----------|------|
| 结构体存放位置 | **SysLib/types/** (必须跨项目复用) | 2026-05-20 |
| 嵌套深度限制 | **≤3层** (如 `stConveyor.astLayer[1].stBlockCylinder`) | 2026-05-20 |
| 参考基准结构体 | **SV_jog** (Enable/jog/Forward/Backward/Velocity/Decel/Accel/Curvetype/Busy/Commandaborted/Error/ErrorID, 11字段) | 2026-05-20 |

### 📚 规范体系完整性

| 层级 | 内容 | 数量 | 状态 |
|------|------|------|------|
| L0-需求层 | 立项表/需求分析/规格说明书 | 3份 | ✅ |
| L1-规范层 | 变量命名规范801 | 1份 | ✅ V1.0.5 |
| L2-架构层 | 程序架构/详细设计/流程图/变量定义/IO分配 | 6份 | ✅ V2.0.0 |
| L3-FB级层 | IFC接口文档+DSN详细设计+CHG变更记录+UM使用说明 | 28份 | ✅ V6.0/V7.0 |
| L4-代码层 | ST源程序(.scl) + 测试用例(.scltest) | 9份 | ✅ |

## 4. Artifacts Index（文档索引）

### 4.1 通用规范库
- scl-spec: 00_通用规范/PLC编程/905_SCL编程规范.md (⭐核心规范)
- timer-guide: 00_通用规范/PLC编程/903_定时器使用规范.md
- comment-rule: 00_通用规范/PLC编程/904_SCL注释规范.md
- error-prevent: 00_通用规范/PLC编程/906_错误预防规则.md (🟠实战bug总结)
- project-config: 00_通用规范/PLC编程/907_项目配置规范.md
- doc-template: 00_通用规范/PLC编程/023_PLC程序设计文档模板_PLC-V2.0.0.md
- ifc-template: 00_通用规范/PLC编程/815_PLC接口文档模板_INT-V1.1.0.md
- git-guide: 00_通用规范/项目管理/902_Git使用指南.md

### 4.2 共享功能库（SysLib）
- syslib-readme: 01_SharedLibraries/SysLib/README.md (📘完整兼容性指南)
- actuator-ifc1011: 01_SharedLibraries/SysLib/actuator/PRD/接口文档_IFC-FB1011-CylinderControl-V7.0.0.md
- actuator-dsn1011: 01_SharedLibraries/SysLib/actuator/PRD/详细设计说明书_DSN-FB1011-CylinderControl-V7.0.0.md
- actuator-ifc1012: 01_SharedLibraries/SysLib/actuator/PRD/接口文档_IFC-FB1012-ConveyorMotor-V7.0.0.md
- actuator-dsn1012: 01_SharedLibraries/SysLib/actuator/PRD/详细设计说明书_DSN-FB1012-ConveyorMotor-V7.0.0.md

### 4.3 主项目 DJ-2026-005
- pm-session: DJ-2026-005/PM_SESSION_DJ-2026-005.md (📋完整项目会话)
- req-spec: DJ-2026-005/01_需求与设计/13_软件方案/012_DJ-2026-005_需求规格说明书_REQ-V2.0.0.md
- arc-doc: DJ-2026-005/02_PLC程序/程序文档/程序架构文档_ARC-DJ-2026-005-V2.0.0.md
- dsn-doc: DJ-2026-005/02_PLC程序/程序文档/详细设计说明书_DSN-DJ-2026-005-V2.0.0.md

## 5. Logs（按事件沉淀）

### iteration_log:
  - 2026-05-20 Iter-001 ST_ServoAxis V3.0集成验证: FB_1003 V6.0→V7.0重构, 删除6个悬空轴请求输出, 新增VAR_IN_OUT io_stZAxis/io_stX1Axis:ST_ServoAxis, OB1直连astServoAxis[1]/[2], GlobalVars.db新增astServoAxis[1..3], 完整验证SV_Power/SV_ABS/SV_Stop/ST_Sensor控制流程 | ✅ 已完成

### refactor_log:
  - 2026-05-20 FB_1003 V7.0+OB1+GlobalVars集成ST_ServoAxis V3.0: FB_1003从间接请求接口(6个q_*轴请求输出)改为VAR_IN_OUT直连ST_ServoAxis(2个io_st*轴引用), 内部代码全面改写为stPower(使能检查)/stAbs(绝对定位Execute/Position/Velocity/Done/Error)/stStop(急停)/stSensor(FwdLimit/RevLimit互锁/ServoAlarm), 影响范围4文件(FB_1003/OB1/GlobalVars.db/IFC文档), 发现原V6.0的6个轴请求输出在OB1中完全悬空无人桥接 | ✅ 已完成
  - 2026-05-20 ST_ServoAxis V2.0→V3.0重大重构: 扁平25字段四段式→按8个SV功能块分组嵌套(74字段), 单文件10个TYPE定义(对齐GlobalVars.db风格), 对齐PLCopen MC Part 1完整标准(每FB独立Done/Busy/CommandAborted/Error/ErrorID), 新增SV_Halt(减速暂停/MC_Halt)/SV_Rel(相对定位/MC_MoveRelative)/SV_Reset(错误复位/MC_Reset)三个功能块, 新增Jerk字段(S型曲线支持,0=T型), 传感器独立ST_Sensor结构体, 访问路径从2层→3层(astServoAxis[i].stXxx.Field), 命名规范ST_SvXxx(Sv=Servo域前缀) | ✅ 已完成
- 2026-05-20 ST_ServoAxis V1.0→V2.0重构: 对齐PLCopen五图标准(SV_Power/SV_Jog/SV_Home/SV_Stop/SV_ABS)，21→25字段，三段式→四段式分区(命令6/参数5/传感器5/状态9)，新增ExecuteStop/CurveType/Done/Status(4字段)，重命名7字段(HomeRequest→ExecuteHome, MoveAbsReq→ExecuteAbs, JogFwd→JogForward, JogRev→JogBackward, TargetPos→Position, HomePos→HomeSensor[修复BOOL命名歧义], ServoFault→ServoAlarm)，同步更新README.md | ✅ 已完成
- 2026-05-20 变量结构化重构提案 V8.0.0: 基于散装变量诊断（161→20顶层变量，-88%），设计8个通用结构体（ST_ServoAxis/ST_Cylinder/ST_DualSensor/ST_ConveyorMotor/ST_ConveyorLayer/ST_ClampGroup/ST_ProductSensors/ST_ExternalDevice），决策：存放SysLib/types/跨项目复用，嵌套≤3层，参考SV_jog结构体（11字段jog控制）；文档输出至 DJ-2026-005/.trae/documents/变量结构化重构方案_V1.0.0.md | 方案待实施

### change_log:
- 2026-05-20 初始化项目库PM_SESSION，完成内容总览

### iteration_log:
- 2026-05-18 DJ-2026-005 阶段4完成：Conveyor子系统高内聚低耦合重构（V7.0.0）

## 6. 治理建议

### ✅ 已具备的能力
1. **规范驱动开发**: 8份通用规范覆盖编码/注释/配置/错误预防全流程
2. **组件复用体系**: SysLib提供17个标准FB/FC，支持多平台移植
3. **文档四级架构**: L0需求→L1规范→L2架构→L3 FB级→L4代码，完整追溯链
4. **实战验证**: DJ-2026-005项目已完成4个阶段重构，产出30+份文档

### 🔄 可优化方向
1. **新项目模板**: 基于 DJ-2026-005 提取标准化项目骨架
2. **自动化检查**: 集成906错误预防规则到CI流程
3. **测试覆盖**: 为SysLib核心模块补充.scltest测试用例
4. **版本发布**: 建立SysLib的语义化版本管理机制
