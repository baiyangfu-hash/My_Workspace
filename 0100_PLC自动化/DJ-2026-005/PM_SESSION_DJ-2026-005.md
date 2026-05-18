# PM_SESSION_DJ-2026-005

## 0. Meta
- project_id: DJ-2026-005
- project_name: 边框缓存机
- project_root: c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\DJ-2026-005
- last_updated: 2026-05-18
- owners: 待补充

## 1. Positioning（项目定位）
- one_liner: 边框缓存机 PLC/HMI 软件工程交付与维护
- users: 设备调试/维护工程师；产线操作人员
- non_goals: 待补充

## 2. Current Focus（当前焦点）
- current_focus: 阶段3完成：全部ST代码重写为V6.0.0，变量100%英文，接口对齐PRD
- milestone: 阶段3 - ST代码重写 ✅
- acceptance:
  - ✅ 阶段0：SRC基线
  - ✅ 阶段1：6份核心文档修正
  - ✅ 规范升级：801_DEV-V1.0.3→V1.0.5（英文标识符强制）
  - ✅ 阶段2：FB级PRD全部重写V6.0.0（FB_1002+FB_1003+FB_1004+FB_2001+FB_External）
  - ✅ 阶段3：ST代码全部重写（8个源文件全部V6.0.0）
  - ⬜ 待定：AxisControl独立轴FB（当前FB1003/1004用轴请求接口占位）
  - ⬜ 待定：TIA Portal编译验证+VS Code LSP诊断

## 3. Status Summary（当前状态摘要）
- in_progress:
  - 阶段3已完成：8个源文件全部重写为V6.0.0
- next_up:
  - 建议：TIA Portal导入编译验证
  - 建议：VS Code LSP语法诊断
  - 建议：HMI通信变量对齐（GlobalVars→HMI Tags）
  - 待定：独立AxisControl轴FB实现
- open_questions:
  - 是否需要立即创建独立的AxisControl FB？当前轴抽象接口（q_bXxxReq + q_rTargetPos）是否足够？
  - FB_1002 的 bPickupConfirmed 是内部VAR变量，如何从FB_1003接入？（需FB级通讯机制）
  - 是否需要编写 .scltest 测试用例？
- risks_dependencies:
  - 现有ST代码与PRD大幅冲突（✅ 阶段3已全部解决）
  - 新增风险：OB1/DB1大改可能影响HMI通信变量映射（需要TIA Portal验证）

## 4. Artifacts Index（文档索引）— ST开发核心文档全景

### 4.0 ST开发文档阅读路径（推荐顺序）
1. 需求分析 → 2. 需求规格说明书 → 3. 程序架构文档 → 4. 工艺流程图 → 5. 变量定义文档+IO分配表 → 6. 详细设计说明书 → 7. FB级接口文档(IFC) → 8. FB级详细设计(DSN) → 9. .scl源码

### 4.1 L0-需求层
- req-analysis: 00_项目管理\01_立项与需求\005_DJ-2026-005_需求分析文档_REQ-V2.0.0.md
- req-spec:     01_需求与设计\13_软件方案\012_DJ-2026-005_需求规格说明书_REQ-V2.0.0.md (F001-F011, 11项功能需求)
- project-init: 00_项目管理\01_立项与需求\003_DJ-2026-005_项目立项表_PROJ-V2.0.0.md

### 4.2 L1-规范层
- naming-spec:  01_需求与设计\10_编程及变量规范\801_PLC变量命名与功能块命名规范_DEV-V1.0.5.md

### 4.3 L2-架构/设计层（程序文档/，6份核心文档）
- arc:      02_PLC程序\程序文档\程序架构文档_ARC-DJ-2026-005-V2.0.0.md
- dsn:      02_PLC程序\程序文档\详细设计说明书_DSN-DJ-2026-005-V2.0.0.md
- flow:     02_PLC程序\程序文档\018_DJ-2026-005_自动工艺流程图_FLOW-V2.0.0.md
- vars:     02_PLC程序\程序文档\PLC变量定义文档_VAR-DJ-2026-005-V2.0.0.md (900+行完整数据字典)
- io:       02_PLC程序\程序文档\015_DJ-2026-005_IO分配表_IO-V2.0.0.md
- plc-sum:  02_PLC程序\程序文档\016_DJ-2026-005_PLC程序设计总文档_PLC-V2.0.0.md

### 4.4 L3-FB级接口/设计层（各FB的PRD/，全部V6.0.0，IFC+DSN+CHG+UM）
- ob1:      02_PLC程序\通用ST程序及变量表\OB1\PRD\ (IFC-V5.0.0 + DSN + CHG) — 待更新到V6.0.0
- db1:      02_PLC程序\通用ST程序及变量表\DB1\PRD\ (IFC-V3.0.0 258变量5结构 + CHG) — 待更新到V6.0.0
- fb1001:   02_PLC程序\通用ST程序及变量表\conveyor\PRD\ (IFC-V4.3.0 + DSN + UM + CHG) — 待更新到V6.0.0
- fb1002:   02_PLC程序\通用ST程序及变量表\conveyor\PRD\ (IFC-V6.0.0 + DSN-V6.0.0 + CHG-V6.0.0 + UM-V6.0.0) ✅ 新增
- fb1003:   02_PLC程序\通用ST程序及变量表\pickplace\PRD\ (IFC-V6.0.0 + DSN-V6.0.0 + CHG-V6.0.0 + UM-V6.0.0) ✅
- fb1004:   02_PLC程序\通用ST程序及变量表\feeder\PRD\ (IFC-V6.0.0 + CHG-V6.0.0 + UM-V6.0.0) ✅
- fb2001:   02_PLC程序\通用ST程序及变量表\common\PRD\ (IFC-V6.0.0 + CHG-V6.0.0 + UM-V6.0.0) ✅
- external: 02_PLC程序\通用ST程序及变量表\external\PRD\ (IFC-V6.0.0 + CHG-V6.0.0 + UM-V6.0.0) ✅

### 4.5 L4-源代码层（全部V6.0.0 ✅ 变量100%英文，801规范合规）
- ob1:      02_PLC程序\通用ST程序及变量表\OB1\OB1.scl ✅ V6.0.0
- db1:      02_PLC程序\通用ST程序及变量表\DB1\GlobalVars.db ✅ V6.0.0
- fb1001:   02_PLC程序\通用ST程序及变量表\conveyor\FB_1001_Conveyor4Layer_BufferFraming.scl ✅ V6.0.0
- fb1002:   02_PLC程序\通用ST程序及变量表\conveyor\FB_1002_SingleLayerConveyor_BufferFraming.scl ✅ V6.0.0 (9步Step_S)
- fb1003:   02_PLC程序\通用ST程序及变量表\pickplace\FB_1003_PickPlace_BufferFraming.scl ✅ V6.0.0 (6步S20~S25)
- fb1004:   02_PLC程序\通用ST程序及变量表\feeder\FB_1004_GlueMachineFeeder_BufferFraming.scl ✅ V6.0.0 (4步D760)
- fb2001:   02_PLC程序\通用ST程序及变量表\common\FB_2001_CommonAlarm_AllStation.scl ✅ V6.0.0
- external: 02_PLC程序\通用ST程序及变量表\external\FB_ExternalDeviceInteraction.scl ✅ V6.0.0
- test:     02_PLC程序\通用ST程序及变量表\Test\basic_test.scltest

### 4.5a 源程序功能基线（SRC - Truth Anchor）
- baseline: 02_PLC程序\通用ST程序及变量表\PRD-SRC\源程序功能基线_SRC-DJ-2026-005-V1.0.0.md (~530行，I/O全量映射+三轴运动参数+3个状态机+~50F位报警体系+指示灯逻辑)

### 4.6 测试与一致性
- test:
  - 05_测试与验证\程序导出一致性检查报告_DJ-2026-005_V2.0.0.md
  - 05_测试与验证\整改方案_DJ-2026-005_梯形图对照通用ST一致性整改_V1.0.0.md
- change_mgmt:
  - 00_项目管理\04_变更管理\04_变更记录\01_版本变更台帐.md
- delivery:
  - 06_文档与交付\验收交付清单\验收交付清单.md

### 4.7 ST开发范围外 — 明确忽略清单（不在ST文档索引中引用）

| 路径 | 原因 | 标记 |
|------|------|:----:|
| `.plc-out/` | Go运行时自动生成代码 | 🔴 |
| `.trae/` | AI辅助开发的内部specs/plans | 🔴 |
| `.plc.json` | 项目配置文件（库引用等） | 🔴 |
| `03_HMI设计/` | HMI界面设计，非ST程序 | 🟡 仅报警码/状态字需对齐 |
| `04_现场调试/` | 现场调试，运维范畴 | 🔴 |
| `04_驱动器与设备/` | 伺服/变频器硬件配置 | 🔴 |
| `05_测试与验证/`(部分) | 电路整改/Eplan报告，非ST | 🟡 一致性报告可用作回归参考 |
| `06_文档与交付/` | 交付物/操作手册/维护手册 | 🔴 |
| `07_技术支持/` | 运维手册 | 🔴 |
| `08_备件管理/` | 运维手册 | 🔴 |
| `09_项目总结/` | 一次性总结 | 🔴 |
| `10_知识库/` | 知识分享 | 🔴 |
| `00_项目管理/04_变更管理/` | 流程文档 | 🟡 变更台帐可追溯历史 |
| `02_PLC程序/编译器源程序文件/*.gx3` | 二进制编译器文件 | 🔴 |
| `02_PLC程序/分料送料.pdf` | 原始PDF（已提取文本到.trae/） | 🔴 |

## 5. Logs（按事件沉淀）
- refactor_log:
  - 2026-05-18 INT→WORD类型重构: FB_2001报警码(wAlarmCode:WORD) + MES队列(aMesQueue:WORD[10]) + 字面量(ALM_NONE:WORD:=16#0000); FOR/算术/索引变量保留INT(移植性); FB_1002/1003/1004/External原始INT保持(避免跨FB引用断裂); 801规范V1.0.6新增w/dw前缀; DSN/IFC同步更新
  - 2026-05-18 ST code validation: Ran LSP diagnostics on all .scl files; no errors detected.
- bug_log:
  - 2026-05-18 OB1针脚不匹配: GlobalVars.stGlobal中q_iCurrentAlarmCode→q_wCurrentAlarmCode(INT→WORD)和q_aMesQueue(INT→WORD)未同步FB_2001 V6.0.0 WORD类型, 导致OB1编译报错 | P0 | ✅已修复
- iteration_log:
  - 2026-05-18 阶段3完成：全部8个ST源文件重写为V6.0.0，变量名100%英文，接口100%对齐V6.0.0 PRD文档。清理14个含中文变量名的旧版PRD文件。FB_1002(V1.0.0→V6.0.0, 8步先分料后输送→9步先输送后分料Step_S, o_→q_前缀, 新增STEP_INIT反转初始化/安全门互锁/传感器冗余一致性检查/分料超时报警100~103); FB_1003(V6.0.0, 11步→6步S20~S25, 移除直接伺服控制改用轴抽象请求q_bXxxReq+q_rTargetPos, 4夹爪独立控制, 产品检测在S22步内, 按层选放料L1/L3→D520 L2/L4→D540, 边框检测阻塞); FB_1004(V6.0.0, 6步→4步D760, X2轴请求接口, 打胶机安全区Y47+允许取料Y44); FB_2001(V2.1.0→V6.0.0, 3INT→~25BOOL分类输入, 49类报警码优先级表(系统/安全门/输送/取放/送料/外部), 指示灯(绿/红/黄Y24~Y26)+蜂鸣器Y27+复位灯Y50, MES去重队列10条); FB_External(V5.0.0→V6.0.0, 8路安全门X140~X147+急停X101+HMI STOP X77+总线健康, 简化接口移除冗余Enable/AutoMode/ManualMode); FB_1001(V4.3.0→V6.0.0, 同步FB_1002新接口, i_bEnable/i_bReset→i_bAutoMode/i_bManualMode/i_bStop, 新增安全信号+传感器冗余输出); DB1(V3.0.0→V6.0.0, 全部5个STRUCT同步新FB接口, stGlobal新增~25输入+指示灯/蜂鸣器输出); OB1(V6.0.0, 5个FB调用完全同步新接口)
  - 2026-05-17 规范升级：801_DEV-V1.0.3→V1.0.5(英文标识符强制+定时器计数器简化命名+注释模板+合规自检清单)。阶段2完成：5个FB全部重写V6.0.0。FB_1002(新增独立PRD, IFC 28in/18out, DSN含完整Step_S伪代码+冗余检查+超时报警100~103/130~163); FB_1003(11→6步S20~S25, IFC 40in/25out, 按层选放料点, 轴Request模式); FB_1004(6→4步D760, X2轴区4传感器); FB_2001(~20→~50类报警, 新增强制急停/8安全门/4变频器/传感器冗余/边框阻塞/总线健康, 5路指示灯蜂鸣器); FB_External(8安全门+急停X101+HMI STOP X77+总线健康位)。共19个文件。
  - 2026-05-17 阶段1完成：6份核心程序文档全部基于SRC基线修正。REQ: 状态机3个重写(S20~S25/D760/Step_S)+功能从11项扩到14项+架构表更新+验收12项; FLOW: 5个Mermaid图全重绘(系统模式状态图+三工站主流程+3个真状态机); DSN: 组件层次图+3个状态机表+交叉引用修正; ARC: 架构图+组件表+步数描述统一; IO: 新增§12源程序差异对照+指示灯输出补全; VAR: 取放料11→6步+送料6→4步D760+常量表重写; PLC-sum: 全部步数统一。共计30+处修正。
  - 2026-05-17 阶段0完成：源程序功能基线_SRC-V1.0.0 建立(~530行)。从三菱FX5U源程序提取：I/O全量映射(X0~X157/Y0~Y50)、三轴运动参数(DSZR/DDRVA/D点位/教导)、3个状态机(S20~S25取放料/D760送料/Step_S输送)、~50个F位报警体系、指示灯/安全门/变频器完整信号。与当前架构差距量化：P0致命4项（输送机工艺流程颠倒/取放料6步vs11步/送料4步vs6步/轴控无实现）、P1重要缺失10项、P2建议补充4项。
  - 2026-05-17 文档完整性诊断完成：全景图L0-L4四级覆盖、7个FB全部有IFC/DSN/CHG/UM四件套、可支撑ST持续开发；发现5个需修复问题（版本不一致/路径陈旧/内容重复/缺少GlobalVars-DSN/缺少开发者指南）；已标记ST开发范围外目录清单
  - 2026-05-17 PDF MCP解析与一致性检查 进行中
  - 2026-05-17 排查：pp_structurev3 调用失败定位为 paddlepaddle 3.3.1 推理异常；建议固定 paddlepaddle==3.2.2
  - 2026-05-17 输出梯形图对照通用ST一致性整改方案V1.0.0（含风险点、任务拆解、测试用例建议）
  - 2026-05-17 决策：取消CC-Link对齐；不要求地址对齐；最终交付以OB1/DB/FB为主；轴控以可移植的抽象接口/占位符对齐
  - 2026-05-17 程序文档梳理：补齐导出PNG索引；重命名ARC/DSN/FLOW文件并统一到V2.0.0；同步修正交叉引用
