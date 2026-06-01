# PM_SESSION_SysLib

## 0. Meta
- project_id: SysLib
- project_name: PLC共享函数库 (Shared Libraries for PLC)
- project_root: 0100_PLC自动化\01_SharedLibraries\SysLib
- last_updated: 2026-05-31 (LSP-903 V2.1.0 规范修订: 定时器无条件顶格调用 + FB1011定时器批量调用区重构)
- owners: Trae

## 1. Positioning（项目定位）
- one_liner: 为PLC项目提供可复用的标准功能块（定时器/计数器/执行器/通讯握手/边沿检测/类型定义等）
- users: DJ-2026-005及其他PLC项目
- non_goals: 不处理项目级业务逻辑，不包含HMI/SCADA层代码

## 2. Current Focus（当前焦点）
- current_focus: LSP-903 V2.1.0 规范修订完成: 定时器批量无条件调用模式; FB1011定时器重构完成(3个timer集中到顶部调用区); FB1014/FB1020已符合无需修改; 预防规则: 所有timer的()调用必须无条件顶格
- milestone: V9.0.0 (FB1011+FB1012扁平化) / V4.3.0 (FB1014修复完成) / V2.0.0 (FB1020)
- acceptance: FB1011/FB1012 V9.0.0接口扁平化+代码规范合规, 全部文档与代码一致, FB1014调用点同步更新

## 3. Status Summary（当前状态摘要）
- in_progress:
  - LSP-903 V2.1.0规范修订+FB1011定时器批量调用区重构完成: 3个timer集中到顶部无条件调用, FB1014/FB1020已符合 (2026-05-31)
  - FB1011 V9.0.0 代码-PRD同步完成: fb_tTimeout移到命令处理后(对齐DSN)+4份PRD类型同步DINT (2026-05-31)
  - FB1020 EquipmentHandshake V2.0.0 架构重构+LSP-904修复完成 (2026-05-30)
- next_up:
  - FB1014同步更新3个FB_1011实例调用(io_stCyl=>扁平参数) + FB_1012调用点同步更新
  - FB1014在实际项目中集成验证(OB1接线+IO映射)
  - FB1020在实际项目中集成验证(OB1接线+通讯层映射, 需适配V2.0.0接口变更)
  - SCL自动化Lint脚本开发(LINT-001~007)
- open_questions:
  - FB1014的3个FB_1011实例调用需从io_stCyl改为扁平参数, 是否同步修改FB_1014?
  - 定时器PT参数单位: 保持"扫描周期"还是改为"毫秒"(需修改FB_TON)?
  - OB1侧的信号映射代码需要编写(io_stUpStream/io_stDownStream <-> 通讯层, V2.0.0字段路径变更)
  - GlassID WORD类型在通讯传输中的字节序处理(大端/小端)
- risks_dependencies:
  - V9.0.0 Breaking Change: FB_1011移除ST_Cylinder VAR_IN_OUT, FB_1014的3个实例调用需同步更新
  - V9.0.0 Breaking Change: FB_1012移除ST_ConveyorMotor VAR_IN_OUT, FB_1014的FB_1012实例调用需同步更新
  - V4.3.0 Breaking Change: 状态号3~7变为4~8, 外部依赖q_iState的逻辑需更新
  - V2.0.0 Breaking Change: ST_HandshakeCh结构体布局变化, 通讯双方需同步更新
  - ⚠️ D6/D7复发风险: AI编码时易跳过"读源文件确认接口"和"逐条对照规范"步骤, 需在plc-rules.md中强化前置检查规则
- spec_compliance:
  - last_check: 2026-05-31
  - result: 通过 - FB1011 V9.0.0 TON调用约定修复(先赋值再调用模式), LSP-904注释合规修复(变量//+分支(* *)+文件头合并), 定时器合规(LSP-903)

## 4. Artifacts Index（文档索引）
- prd:
  - communication/PRD/接口文档_IFC-FB1020-EquipmentHandshake-V2.0.0.md
  - actuator/FB_1013_NinetyDegreeTransfer/PRD/接口文档_IFC-FB1013-NinetyDegreeTransfer-V9.0.0.md
  - actuator/FB_1011_CylinderControl/PRD/接口文档_IFC-FB1011-CylinderControl-V9.0.0.md
  - actuator/FB_1011_CylinderControl/PRD/需求分析文档_REQ-FB1011-CylinderControl-V9.0.0.md
  - actuator/FB_1011_CylinderControl/PRD/技术方案文档_TECH-FB1011-CylinderControl-V9.0.0.md
  - actuator/FB_1012_ConveyorMotor/PRD/接口文档_IFC-FB1012-ConveyorMotor-V9.0.0.md
  - actuator/FB_1014_StationConveyor/PRD/接口文档_IFC-FB1014-StationConveyor-V4.3.0.md
  - actuator/FB_1014_StationConveyor/PRD/需求文档_PRD-FB1014-StationConveyor-V4.2.0.md (旧版)
  - actuator/FB_1014_StationConveyor/PRD/需求文档_PRD-FB1014-StationConveyor-V4.3.0.md
  - actuator/FB_1014_StationConveyor/PRD/工艺流程_PFL-FB1014-StationConveyor-V4.3.0.md
- des:
  - communication/PRD/详细设计说明书_DSN-FB1020-EquipmentHandshake-V2.0.0.md
  - actuator/FB_1013_NinetyDegreeTransfer/PRD/详细设计说明书_DSN-FB1013-NinetyDegreeTransfer-V9.0.0.md
  - actuator/FB_1011_CylinderControl/PRD/详细设计说明书_DSN-FB1011-CylinderControl-V9.0.0.md
  - actuator/FB_1012_ConveyorMotor/PRD/详细设计说明书_DSN-FB1012-ConveyorMotor-V9.0.0.md
  - actuator/FB_1014_StationConveyor/PRD/详细设计说明书_DSN-FB1014-StationConveyor-V4.3.0.md
- src:
  - communication/FB_1020_EquipmentHandshake.scl (V2.0.0)
  - actuator/FB_1013_NinetyDegreeTransfer/FB_1013_NinetyDegreeTransfer.scl (V9.0.0)
  - actuator/FB_1011_CylinderControl/FB_1011_CylinderControl.scl (V9.0.0)
  - actuator/FB_1012_ConveyorMotor/FB_1012_ConveyorMotor.scl (V9.0.0)
  - actuator/FB_1014_StationConveyor/FB_1014_StationConveyor.scl (V4.3.0)
- types:
  - types/ST_HandshakeBits.scl (V1.1.0)
  - types/ST_HandshakeCh.scl (V2.0.0)
  - types/ST_ProductData.scl (V2.0.0)
  - types/ST_Cylinder.scl (V1.2.0)
  - types/ST_ConveyorMotor.scl (V1.1.0)
  - types/ST_ExternalDevice.scl (V1.0.0)
  - types/ST_StationSafety.scl (V1.0.0)
  - types/ST_InfeedSensors.scl (V1.0.0)

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-05-30 FB1014 V4.2.0文档完善: 从IFC/DSN/SCL三份源文件提取需求与工艺, 生成PRD(16项功能需求+5项非功能需求+追溯矩阵)和PFL(6步正常流程+4类异常流程+功能切换映射表+时序参数); V4.2.0核心变更: 传感器/气缸功能随方向切换(单口双向复用) 范围:actuator/PRD/ 完成
  - 2026-05-29 FB1020 V1.0.0新增: 解析各設備交握-5.20.xlsx, 输出IFC+SCL+Types, 双通道状态机+心跳监视+产品数据透传 范围:communication/ + types/ 完成
  - 2026-05-30 FB1014 StationConveyor V1.0.0新增: 从自动修讯机16页源程序图片提取工站输送机逻辑, 排除节拍计时, 生成DSN+IFC; 含入料/出料双向输送, 三段式光电位置检测, 上下游握手集成, 安全优先级链, 加工动作解耦, 8态状态机(IDLE/READY/INFEED/PROCESSING/WAIT_DISCHARGE/DISCHARGE/COMPLETE/FAULT), 37个接口(25输入+12输出), 原程序地址完整对照表 范围:actuator/PRD/ 完成
- bug_log:
  - 2026-05-31 FB1011 V9.0.0 定时器裸调用修复: fb_tDebounceExt/fb_tDebounceRet/fb_tTimeout三处裸调用`()`改为完整参数调用`(IN:=实例.IN, PT:=实例.PT, R:=实例.R, Q=>实例.Q, ET=>实例.ET)`; 根因: D6修复将内联直接传值改为预赋值+裸调用, 但裸调用违反plc-rules规则13(定时器调用必须包含完整参数); LSP-903仅为Go-Gen纯逻辑方案, FB_TON/FB_TONR调用约定规范缺失 范围:FB_1011_CylinderControl.scl 完成
  - 2026-05-31 FB1011 V9.0.0 DINT类型修复: i_iTimeoutMs/i_iDebounceMs=INT→DINT, 前缀i_→d_, 删除INT_TO_DINT转换; 根因: 未读FB_TON/FB_TONR源文件确认PT参数实际类型(DINT), 写成了INT; 预防: 调用SysLib FB前必须读源文件确认参数类型 范围:FB_1011_CylinderControl.scl 完成
  - 2026-05-31 FB1011 V9.0.0 TON调用约定错误(D6): fb_tDebounceExt/fb_tDebounceRet/fb_tTimeout调用了 `(IN := ..., Q => ...)` 内联参数传递, 但FB_TON/FB_TONR使用Siemens #IN/#Q风格, 应使用 `.IN赋值 → ()调用 → .Q读取` 模式; 根因: 写代码前未读取 SysLib/timer/FB_TON.scl + FB_TONR.scl 确认实际接口和调用约定; 预防: 调用任何SysLib FB前必须先读源文件确认接口 范围:FB_1011_CylinderControl.scl 完成
  - 2026-05-31 FB1011 V9.0.0 LSP-904注释规范违规(D7): 8项违规(变量注释用(* *)而非//, IF/ELSIF/ELSE分支缺少(* *)块注释, 文件头15行连续并列(* *)块); 根因: 写代码时未逐条对照LSP-904§1-§2规范内容; 预防: 写.scl文件注释前必须重读LSP-904§1(核心规则表)+§2.0(注释类型分工规则) 范围:FB_1011_CylinderControl.scl 完成
  - 2026-05-31 FB1011 V9.0.0 代码-PRD同步修复(D8): fb_tTimeout调用位置从命令处理前移到命令处理后(对齐DSN§4伪代码, 消除1扫描周期延迟); 4份PRD文档(REQ/IFC/DSN/TECH)全部同步: i_iTimeoutMs→i_dTimeoutMs, i_iDebounceMs→i_dDebounceMs, INT→DINT, 移除INT_TO_DINT转换; s_dExtDebounceEt/s_dRetDebounceEt声明与ET赋值保留(监测用途); 根因: 2026-05-31 DINT类型修复仅改.scl未同步PRD, 导致代码与文档不一致; 预防: 代码修改后必须同步更新所有PRD文档 范围:FB_1011_CylinderControl.scl + REQ + IFC + DSN + TECH 完成
  - 2026-05-31 FB1011 V9.0.0 定时器批量调用区重构(D9): fb_tDebounceRet()和fb_tTimeout()的调用从条件/尾部提到FB顶部无条件批量调用区(与fb_tDebounceExt统一); 3个定时器集中为连续调用块(VAR声明之后, 业务逻辑之前); 业务逻辑仅操作IN/PT/R和读取Q/ET, 不再包含()调用; 根因: FB实例每周期必须执行, 跳过调用导致.Q/.ET僵尸值; 依据: LSP-903 V2.1.0 §3.4+§5; 同步更新DSN/TECH伪代码结构; FB1014/FB1020已符合无需修改 范围:FB_1011_CylinderControl.scl + DSN + TECH 完成
  - 2026-05-30 FB1011 V9.0.0缺陷修复: B1-磁环传感器无消抖(新增FB_TON消抖+ i_iDebounceMs参数, 0=关闭, >0启用TON确认, 参照FB_1014消抖模式); B2-极性取反未完整实现(新增极性映射层: i_bExtendPolarity=TRUE时物理ExtendedPos↔RetractedPos互换映射到逻辑位置, 状态输出q_bIsExtended/q_bIsRetracted随极性反转); 传感器故障检测基于消抖后物理信号(极性映射前) 范围:FB_1011_CylinderControl.scl 完成
  - 2026-05-30 FB1014 V4.3.0修复: 5类缺陷全部修复(定时器三重错误B1-B3: 去DINT_TO_TIME+补Q/ET+PT=DINT直传; 组件复用D1-D2: 引入FB_1011+ST_Cylinder VAR_IN_OUT组合; 物理组件遗漏D3-D5: 新增拍正气缸io_stAlignCyl+磁环到位+ST_ALIGN状态); Quality Gate 8项全部通过; IFC→DSN→PRD→PFL→SCL按序更新(文档先行) 范围:FB_1014+5份文档 完成
  - 2026-05-30 FB1014 V4.2.0质量事故: 5类缺陷(定时器三重错误B1-B3: DINT_TO_TIME类型错误/缺Q ET参数/单位语义错位; 组件复用缺失D1-D2: FB_1011+ST_Cylinder未使用; 物理组件遗漏D3-D5: 拍正气缸/磁环信号/ALIGN状态); 根因: RC1物理验证缺失/RC2组件发现缺失/RC3规范验证缺失/RC4文档驱动未执行/RC5 AI速度陷阱; 6项改进方案S1-S6已制定 范围:FB_1014 全部 已修复
  - 2026-05-30 LSP-904注释合规修复: FB_1020 R3违规(Reserved*产生*)注释终止符, R5违规(VAR区5个连续并列(* *)分隔块改为//); DSN伪代码同步修复Reserved*; ST_ProductData/ST_HandshakeCh无违规 范围:FB_1020+DSN 完成
- spec_change_log:
  - 2026-05-31 LSP-903 V2.0.0→V2.1.0: §5调用位置修订(FB_TON从IF分支内改为无条件顶格调用,与TONR统一); 新增§3.4定时器批量无条件调用模式+FB_1011完整示范案例; 新增E7条件分支内调用错误; §6检查清单更新; 文件重命名V2.0.0→V2.1.0; 影响: FB1011已重构, FB1014/FB1020已符合 完成
  - 2026-05-31 LSP-903 V1.0.0→V2.0.0: 完全重写, 从Go-Gen纯逻辑计数器方案迁移到SysLib FB_TON/FB_TONR调用约定; 定义三段式强制模式(预赋值→全参数调用→读输出); 新增常见错误表E1-E6; 新增Code Review检查清单; Breaking Change: V1.0.0内容全部替换; 影响: 所有使用FB_TON/FB_TONR的项目(SysLib/DJ-2026-005等) 完成
- refactor_log:
  - 2026-05-31 FB1011定时器批量调用区重构: 3个定时器(fb_tDebounceExt/fb_tDebounceRet/fb_tTimeout)的()调用集中到FB顶部无条件批量调用区(VAR声明之后); 业务逻辑解耦为仅操作IN/PT/R和读取Q/ET; 扫描FB1014/FB1020确认已符合新模式; DSN+TECH伪代码结构同步更新; 依据LSP-903 V2.1.0 §3.4+§5; 预防: 所有timer的()调用必须无条件顶格 范围:FB_1011_CylinderControl.scl + DSN + TECH 完成
  - 2026-05-30 FB1012 V9.0.0修正(Breaking Change): 取消安全门信号(执行器不处理安全互锁); 慢速改为方向修饰符(Fwd+Slow=慢速正转, Fwd only=高速正转, Slow alone=无效); 新增i_iCtrlMode控制模式预留(0=端子, 1=通讯); i_rSpeed改为通讯模式预留; 注释改中文; IFC+DSN+SCL全部重写, 代码100%遵守文档 范围:FB_1012_ConveyorMotor 完成
  - 2026-05-30 FB1012 V9.0.0扁平化重构(Breaking Change): 移除VAR_IN_OUT ST_ConveyorMotor, 回归扁平VAR_INPUT(6个)/VAR_OUTPUT(5个); 动机: 简单执行机构无需结构体封装, 扁平化更利于调试; 命名对齐LSP-905(i_/q_前缀); IFC+DSN文档先行更新至V9.0.0; 旧版V7.0.0文档已删除; 下游影响: FB_1014的FB_1012实例调用需同步更新 范围:FB_1012_ConveyorMotor.scl+IFC+DSN 完成
  - 2026-05-30 FB1011 V9.0.0文档全面更新: IFC/DSN/TECH/REQ四份文档从V7.1.0/V8.1.0统一升级至V9.0.0; 移除ST_Cylinder引用; 新增消抖+极性映射描述; 规范引用更新为LSP-905/904/903; 旧版文档已删除 范围:FB_1011_CylinderControl/PRD/ 完成
  - 2026-05-30 FB1011 V9.0.0扁平化重构(Breaking Change): 移除VAR_IN_OUT ST_Cylinder, 回归扁平VAR_INPUT(8个)/VAR_OUTPUT(5个); 动机: 简单执行机构无需结构体封装, 扁平化更利于调试; 命名全面对齐LSP-905(i_/q_/s_/fb_前缀); 规范引用从废弃801/810更新为LSP-905/904/903; 新增传感器TON消抖(i_iDebounceMs); 极性取反完整实现(传感器映射+状态输出反转); 下游影响: FB_1014的3个FB_1011实例需同步更新调用方式 范围:FB_1011_CylinderControl.scl 完成
  - 2026-05-30 FB1011电磁阀类型明确: 明确默认SolenoidType=0为单线圈两位阀(1个线圈,弹簧复位安全), 新增SolenoidType和ExtendPolarity参数到ST_Cylinder(V1.2.0), 所有文档(REQ-V8.1.0/TECH-V8.1.0/IFC-V7.1.0/DSN-V7.1.0)更新电磁阀类型说明,真值表,安全策略; 预留双线圈/3位阀扩展接口 范围:actuator/FB_1011_CylinderControl/ + types/ 完成
  - 2026-05-30 FB1011文档补充: 为FB_1011_CylinderControl新增需求分析文档(REQ-V8.0.0)和技术方案文档(TECH-V8.0.0), 包含需求分解、架构设计、接口规范、验收标准等完整内容, 完善SysLib文档体系 范围:actuator/FB_1011_CylinderControl/PRD/ 完成
  - 2026-05-30 actuator文件夹架构整理: 将平铺的FB文件和混放的PRD文档按FB分类重组, 每个FB独立文件夹(FB_1011/FB_1012/FB_1013/FB_1014), SCL文件和PRD子文件夹归位, 删除旧的actuator/PRD文件夹, 更新artifacts_index路径 范围:actuator/ 完成
  - 2026-05-30 FB1014 V2.0.0接口重构(Breaking Change): 37->19个接口(-49%); 安全信号6 BOOL->ST_StationSafety VAR_IN_OUT(新增SafeToRun计算输出); 位置检测3 BOOL+1 DINT->ST_InfeedSensors VAR_IN_OUT(封装去抖确认+AllConfirmed); 电机驱动2 BOOL->ST_ConveyorMotor VAR_IN_OUT(与FB1012/FB1013一致); i_bInfeedSelected+i_bOutfeedSelected->i_bSelected合并; i_bClampVacDone+i_bEdgeConfirmExt->i_bProcessDone合并(解耦加工细节); i_bLiftUpper/i_bTouchEdgeWait消除(DSN无引用); q_bEStopActive/q_bLightCurtainFault消除(可推导); i_bEStop约定修正(TRUE=触发->TRUE=正常); 新增ST_StationSafety/ST_InfeedSensors类型文件; DSN+IFC同步V2.0.0 范围:FB_1014+DSN+IFC+2个Types 完成
  - 2026-05-30 FB1020 V2.0.0架构重构(Breaking Change): ST_ProductData GlassID 30 INT->16 WORD; ST_HandshakeCh 扁平字段->WriteProduct/ReadProduct嵌入消除冗余; [B1]Disable段不清除Ready/DsReady/Reserved; [B2]上游COMPLETE态增加Write.Complete回传; [B3]产品数据改为MoveBusy上升沿一次性锁存(bUpDataLatched/bDsDataLatched); [D1]新增q_stUpReceivedProduct/q_stDownReceivedProduct输出; DSN+IFC同步V2.0.0 范围:FB_1020+DSN+IFC+ST_ProductData+ST_HandshakeCh 完成
  - 2026-05-29 FB1020 V1.1.0通用化重构: 剥离Modbus依赖→纯协议逻辑, 新增i_bTransportDone/i_dReqDelayMs/i_dHbToggleMs/i_dHbTimeoutMs/i_dCompleteMs可配置参数, 新增q_iUpState/q_iDownState诊断输出, DSN+IFC同步V1.1.0, Types去除Modbus地址注释 范围:FB_1020+DSN+IFC+3个Types 完成
  - 2026-05-29 FB1013 VAR_OUTPUT精简: 70→25个(-45), M0-M10删除, 报警合并WORD, NV合并BYTE, 位置合并INT, IFC/DSN同步升V9.0.0 范围:FB_1013_NinetyDegreeTransfer.scl+IFC+DSN 完成
