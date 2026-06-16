# PLC 状态机模板对照表

## 1. 文档目的

本表用于为 `plc-electrical-engineer` 技能提供“工艺步序 / 状态机”场景的实证基线，避免后续状态机设计继续靠临场发挥。

本表基于以下优先级样本整理：

- A: `FB_1002_SingleLayerConveyor_BufferFraming`
- A: `FB_1003_PickPlace_BufferFraming`
- A-: `FB_1013_NinetyDegreeTransfer`
- B+: `FB_1014_StationConveyor`
- B: `FB_1020_EquipmentHandshake`
- C: `FB_1004_GlueMachineFeeder_BufferFraming`

## 2. 总览对照

| 优先级 | FB | 场景类型 | 状态机形态 | 推荐用途 | 结论 |
|---|---|---|---|---|---|
| A | `FB_1002_SingleLayerConveyor_BufferFraming` | 设备顺控 | 单主 `CASE` + `bStepEntry` | 设备顺控母模板 | 最均衡 |
| A | `FB_1003_PickPlace_BufferFraming` | 机构动作 | 单主 `CASE` + 轴控/定时器 | 中高复杂机构模板 | 适合机构编排 |
| A- | `FB_1013_NinetyDegreeTransfer` | 共享库复杂顺控 | 单主 `CASE` + 多执行器聚合 | 共享库复杂顺控模板 | 最强但偏重 |
| B+ | `FB_1014_StationConveyor` | 多模式输送站 | 主状态机 + 子步骤 | 多模式输送站模板 | 场景化较强 |
| B | `FB_1020_EquipmentHandshake` | 协议状态机 | 上游/下游双 `CASE` | 通信握手模板 | 不适合机械顺控直套 |
| C | `FB_1004_GlueMachineFeeder_BufferFraming` | 轻量交互 | 4步单主 `CASE` | 轻量交互模板 | 简洁好读 |

## 3. 各模板特征

### 3.1 FB_1002_SingleLayerConveyor_BufferFraming

- 文件: [FB_1002_SingleLayerConveyor_BufferFraming.scl](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/conveyor/FB_1002_SingleLayerConveyor_BufferFraming.scl)
- 接口与状态变量: [FB_1002_SingleLayerConveyor_BufferFraming.scl:L38-L143](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/conveyor/FB_1002_SingleLayerConveyor_BufferFraming.scl#L38-L143)
- 主状态机: [FB_1002_SingleLayerConveyor_BufferFraming.scl:L260-L408](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/conveyor/FB_1002_SingleLayerConveyor_BufferFraming.scl#L260-L408)

特点：

- `bStepEntry` 用法标准
- 步号常量集中
- 自动 / 手动分支清晰
- 子设备拆成 `FB_1011`、`FB_1012` 调用，编排层职责明确

适合沉淀：

- 标准设备顺控母模板
- “主状态机 + 执行器子块” 的组合模式

逻辑验证：

- 优点：步序迁移可读性好，手动旁路清晰
- 风险：`STEP_CONVEYOR_FWD` 与 `STEP_CONVEYOR_SLOW` 都要求 `i_bPositionSensor1 AND i_bPositionSensor2`，若现场采用单传感器或冗余不同步，流程会卡住且当前块本身无超时保护
- 风险：自动启动使用 `bStartTriggered` 锁存，若回零路径没有统一清除，二次启动依赖外层时序

### 3.2 FB_1003_PickPlace_BufferFraming

- 文件: [FB_1003_PickPlace_BufferFraming.scl](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/pickplace/FB_1003_PickPlace_BufferFraming.scl)
- 接口与状态变量: [FB_1003_PickPlace_BufferFraming.scl:L35-L159](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/pickplace/FB_1003_PickPlace_BufferFraming.scl#L35-L159)
- 主状态机: [FB_1003_PickPlace_BufferFraming.scl:L214-L452](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/pickplace/FB_1003_PickPlace_BufferFraming.scl#L214-L452)

特点：

- 机构动作步序清晰
- 轴控命令、限位互锁、超时逻辑都在步内闭环
- 故障分类比 `FB_1002` 更完整

适合沉淀：

- 带轴控的机构状态机模板
- “动作步 + 超时 + 轴错误 + 回空闲”的机构模式

逻辑验证：

- 优点：每个轴动作步基本都有 Done / Error / Timeout 分支
- 风险：`S23_MOVE_TO_PLACE` 没有与 `S21`、`S24` 对称的超时定时器，X1 若既不 Done 也不触发光电，将卡在该步
- 风险：`q_bPlaceDoneToFeeder` 在 `S25` 置位后回到 `S20_IDLE`，缺少当前块内部的脉冲复位定时闭环，依赖外部步入口清除

### 3.3 FB_1013_NinetyDegreeTransfer

- 文件: [FB_1013_NinetyDegreeTransfer.scl](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1013_NinetyDegreeTransfer/FB_1013_NinetyDegreeTransfer.scl)
- 接口与状态变量: [FB_1013_NinetyDegreeTransfer.scl:L34-L136](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1013_NinetyDegreeTransfer/FB_1013_NinetyDegreeTransfer.scl#L34-L136)
- 自动主流程: [FB_1013_NinetyDegreeTransfer.scl:L321-L559](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1013_NinetyDegreeTransfer/FB_1013_NinetyDegreeTransfer.scl#L321-L559)

特点：

- 多执行器聚合
- 报警位图、错误分类、PLCopen 输出都比较完整
- 共享库级风格明显

适合沉淀：

- 重型共享库顺控模板
- “动作执行 + 错误位图 + 断电保持” 的复杂模板

逻辑验证：

- 优点：错误分类和外部接口成熟
- 风险：大量步骤在超时置错后没有统一强制迁移到 Fault/Idle，而是仅置报警位，后续行为依赖块外复位策略
- 风险：在步内使用 `RETURN` 提前退出，容易使当前扫描周期后续收尾逻辑不一致，作为模板时应谨慎

### 3.4 FB_1014_StationConveyor

- 文件: [FB_1014_StationConveyor.scl](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1014_StationConveyor/FB_1014_StationConveyor.scl)
- 接口与状态变量: [FB_1014_StationConveyor.scl:L30-L136](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1014_StationConveyor/FB_1014_StationConveyor.scl#L30-L136)
- 主状态机与子步骤: [FB_1014_StationConveyor.scl:L268-L507](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1014_StationConveyor/FB_1014_StationConveyor.scl#L268-L507)

特点：

- 主状态机 + `m_iAlignStep` / `m_iDischPrepStep`
- 运行模式分流明显
- 适合多模式工站

适合沉淀：

- “主状态 + 子步骤” 模板
- 多模式工站输送模板

逻辑验证：

- 优点：模式分流可读性较强
- 风险：多个子步骤无独立超时，若气缸不到位会卡在子步骤
- 风险：`iState := q_iState` 的镜像方式对调试友好，但若输出回写顺序处理不严谨，容易出现状态不同步认知

### 3.5 FB_1020_EquipmentHandshake

- 文件: [FB_1020_EquipmentHandshake.scl](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/01_SharedLibraries/SysLib/communication/FB_1020_EquipmentHandshake.scl)
- 接口与状态变量: [FB_1020_EquipmentHandshake.scl:L32-L103](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/01_SharedLibraries/SysLib/communication/FB_1020_EquipmentHandshake.scl#L32-L103)
- 上下游双状态机: [FB_1020_EquipmentHandshake.scl:L220-L438](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/01_SharedLibraries/SysLib/communication/FB_1020_EquipmentHandshake.scl#L220-L438)

特点：

- 上下游双通道独立状态机
- 心跳、完成脉冲、通信故障模型完整
- 更像协议状态机，不是机械步序

适合沉淀：

- 设备通信 / 握手状态机模板
- “双通道并行 CASE” 模板

逻辑验证：

- 优点：通道拆分明确，状态对称性较好
- 风险：Phase 2 定时器集中调用采用“成员传成员”的写法，模板可读性弱，容易被误用
- 风险：上游和下游故障恢复条件略有差异，若一侧超时恢复而另一侧仍在旧态，现场需要额外联调验证

### 3.6 FB_1004_GlueMachineFeeder_BufferFraming

- 文件: [FB_1004_GlueMachineFeeder_BufferFraming.scl](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/feeder/FB_1004_GlueMachineFeeder_BufferFraming.scl)
- 接口与状态变量: [FB_1004_GlueMachineFeeder_BufferFraming.scl:L27-L102](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/feeder/FB_1004_GlueMachineFeeder_BufferFraming.scl#L27-L102)
- 主状态机: [FB_1004_GlueMachineFeeder_BufferFraming.scl:L133-L272](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/feeder/FB_1004_GlueMachineFeeder_BufferFraming.scl#L133-L272)

特点：

- 4步轻量状态机
- 外设协同强
- 可作为“短链路模板”

适合沉淀：

- 轻量交互型状态机模板
- 外设握手 + 单轴动作模板

逻辑验证：

- 优点：步数少，职责边界清晰
- 风险：`tCommTimer` 已定义但当前主流程几乎未见有效使用，通信超时策略没有真正落地
- 风险：启动锁存 `bStartTriggered` 回空闲后只在部分路径清除，连续多周期复用需谨慎

## 4. 模板提炼结论

### 4.1 推荐直接沉淀为技能母模板的对象

1. `FB_1002`：设备顺控母模板
2. `FB_1003`：机构动作母模板
3. `FB_1013`：共享库复杂顺控模板
4. `FB_1020`：协议状态机模板

### 4.2 作为补充模式保留的对象

1. `FB_1014`：主状态 + 子步骤模板
2. `FB_1004`：轻量交互模板

## 5. 通用验证清单

对任何 PLC 状态机，至少验证：

1. 状态机是否有非法状态兜底
2. 步入口动作是否只执行一次
3. 自动 / 手动切换是否清理锁存
4. 停止 / 复位是否清理定时器和输出
5. 每个关键动作步是否有超时或错误退路
6. 子步骤是否可能卡死
7. 报警后是否明确冻结、回零或回空闲
8. `q_iCurrentState` / `q_bRunning` 是否真实反映内部状态

## 6. 对技能的要求

基于本表，`plc-electrical-engineer` 在处理状态机场景时必须：

1. 先判断是设备顺控、机构动作、共享库复杂顺控、主状态+子步骤，还是协议状态机
2. 先选模板，再输出设计或审查意见
3. 默认附带逻辑验证清单
4. 明确指出“可作为模板的部分”和“只能作为项目实现参考的部分”
