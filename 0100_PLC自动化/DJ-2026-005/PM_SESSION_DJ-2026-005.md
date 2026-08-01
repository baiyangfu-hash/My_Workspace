# PM_SESSION_DJ-2026-005

## 0. Meta
- project_id: DJ-2026-005
- project_name: 边框缓存机
- project_root: c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\DJ-2026-005
- last_updated: 2026-08-02
- owners: fubai / PLC开发团队

## 1. Positioning（项目定位）
- one_liner: 边框缓存机 PLC/HMI 软件工程交付与维护
- users: 设备调试/维护工程师；产线操作人员
- non_goals: 待补充

## 2. Current Focus（当前焦点）
- current_focus: 稳定维护 — P2 任务收尾完成，文档归档就绪
- milestone: 全 7 模块 PRD 四件套 100% 完整，台账 0/0/0，PM_SESSION 双层结构归档 150 行 ✅
- acceptance:
  - ✅ CHG-DOCU-2026-001 闭环 | CHG-PLC-2026-008/009 retrofit | 台帐 005/006 修复
  - ✅ CHG-DOCU-2026-002 闭环 (补齐 7 个 PRD 文档) | 台账 0/0/0 | plc check 21/21
  - ✅ Spec Snapshot 漂移已确认 | LSP-906/907 无漂移 | PM_SESSION 归档 302→150 行

## 3. Status Summary（当前状态摘要）
- in_progress:
  - 稳定维护
- next_up:
  - TIA Portal 编译验证 (P0)
- open_questions:
  - 无
- risks_dependencies:
  - 无 .scltest 运行环境，TIA Portal 编译需现场环境

## 3.1 Version Evolution Matrix（版本演进矩阵）

| 设备主版本 <br>`(.plc.json)` | 变更单 <br>`(CHG)` | `FB_1002` <br>输送机 | `FB_1003` <br>取放料 | `FB_1004` <br>打胶送料 | `FB_2001` <br>报警管理 | 核心架构特征 / 破坏性变更 (Breaking Changes) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **V7.0.0** | CHG-PLC-001 | V9.0.0 | V6.0.0 | V6.0.0 | V2.0.0 | 架构大重写，展开调用 4×FB_1002 |
| **V7.1.0** | CHG-PLC-002 | V10.0.0 | V7.0.0 | V6.0.0 | V2.0.0 | FB_1003 引入 `ST_ServoAxis` V3.0 (`VAR_IN_OUT`) |
| **V7.2.0** | CHG-PLC-004 | V10.0.1 | V7.0.1 | V7.0.0 | V2.1.1 | FB_1004 升级 `VAR_IN_OUT` 架构对齐 FB_1003 |
| **V8.0.0** | CHG-PLC-2026-008 | V11.0.0 | V7.0.1 | V7.0.0 | V2.1.1 | FB_1002 破坏性重构为 VAR_IN_OUT io_stLayer 结构体整块传递 |
| **V9.0.0** | CHG-PLC-2026-009 | V11.0.0 | V8.0.0 | V8.0.0 | V3.0.0 | 全工站 5 大 FB 彻底完成 VAR_IN_OUT 结构体整块传递；OB1 彻底瘦身至 5 行顶级调度代码 |
| **V9.1.0 (当前)** | CHG-PLC-2026-007 | **V11.0.0** | **V8.0.0** | **V7.0.0** | **V3.0.0** | **传感器动态消抖与抗扰升级**；ST_SingleLayerConveyor/ST_GlueFeeder 新增 i_dDebounceMs 控制 |

### 4.1 L1-规范层
- naming-spec:  ../00_通用规范/PLC编程/905_SCL编程规范_LSP.md (替代旧801，含命名/语法/代码结构)

### 4.2 程序级方案（PLC_ST/00_程序方案/）
- req:      02_PLC程序\PLC_ST\00_程序方案\需求分析文档_REQ.md
- int:      02_PLC程序\PLC_ST\00_程序方案\接口文档_INT.md
- tec:      02_PLC程序\PLC_ST\00_程序方案\技术方案文档_TEC.md
- dsn:      02_PLC程序\PLC_ST\00_程序方案\详细设计说明书_DSN.md

### 4.3 L2-架构/设计层（程序文档/，6份核心文档）
- arc:      02_PLC程序\程序文档\程序架构文档_ARC-DJ-2026-005-V2.0.0.md
- dsn:      02_PLC程序\程序文档\详细设计说明书_DSN-DJ-2026-005-V2.0.0.md
- flow:     02_PLC程序\程序文档\018_DJ-2026-005_自动工艺流程图_FLOW.md
- vars:     02_PLC程序\程序文档\PLC变量定义文档_VAR-DJ-2026-005-V2.0.0.md (900+行完整数据字典)
- io:       02_PLC程序\程序文档\015_DJ-2026-005_IO分配表_IO.md
- plc-sum:  02_PLC程序\程序文档\016_DJ-2026-005_PLC程序设计总文档_PLC.md

### 4.4 L3-FB级接口/设计层（各FB的PRD/，版本对齐 V9.1.0，IFC+DSN+CHG+UM ✅ 7/7 完整）
- ob1:      02_PLC程序\PLC_ST\00_主程序\PRD\ (IFC+DSN+CHG) ✅ OB1=V9.0.0
- db1:      02_PLC程序\PLC_ST\00_全局数据\PRD\ (IFC+DSN+CHG+UM) ✅ GlobalVars=V7.0.0
- fb1002:   02_PLC程序\PLC_ST\02_输送机\PRD\ (IFC+DSN+CHG+UM+ARC) ✅ FB_1002=V11.0.0
- fb1003:   02_PLC程序\PLC_ST\03_取放料\PRD\ (IFC+DSN+CHG+UM) ✅ FB_1003=V8.0.0
- fb1004:   02_PLC程序\PLC_ST\04_打胶机送料\PRD\ (IFC+DSN+CHG+UM) ✅ FB_1004=V7.0.0
- fb2001:   02_PLC程序\PLC_ST\05_公共报警\PRD\ (IFC+DSN+CHG+UM) ✅ FB_2001=V3.0.0
- external: 02_PLC程序\PLC_ST\01_外部设备交互\PRD\ (IFC+DSN+CHG+UM) ✅ FB_External=V4.1.0
- syslib:   01_SharedLibraries\SysLib\actuator\PRD\ (IFC+DSN) FB_1011/1012 通用执行器

### 4.5 L4-源代码层（版本对齐 V9.1.0，全部 VAR_IN_OUT 结构体整块传递，LSP-905 合规）
- ob1:      02_PLC程序\PLC_ST\00_主程序\OB1.scl ✅ V9.0.0 (5行顶级调度器)
- db1:      02_PLC程序\PLC_ST\00_全局数据\GlobalVars.db ✅ 具名 UDT 类型声明
- fb1002:   02_PLC程序\PLC_ST\02_输送机\FB_1002_SingleLayerConveyor_BufferFraming.scl ✅ V11.0.0 (9步Step_S + 消抖)
- fb1003:   02_PLC程序\PLC_ST\03_取放料\FB_1003_PickPlace_BufferFraming.scl ✅ V8.0.0 (6步S20~S25)
- fb1004:   02_PLC程序\PLC_ST\04_打胶机送料\FB_1004_GlueMachineFeeder_BufferFraming.scl ✅ V7.0.0 (4步D760)
- fb2001:   02_PLC程序\PLC_ST\05_公共报警\FB_2001_CommonAlarm_AllStation.scl ✅ V3.0.0 (49类报警码)
- external: 02_PLC程序\PLC_ST\01_外部设备交互\FB_ExternalDeviceInteraction.scl ✅ V4.1.0 (8路安全门+急停+总线)
- test:     02_PLC程序\PLC_ST\Test\basic_test.scltest (12个 TC, V7.1.1→待同步 V9.1.0)
- baseline: 02_PLC程序\PLC_ST\99_基线\源程序功能基线_SRC-DJ-2026-005-V1.0.0.md (~530行，I/O全量映射+三轴运动参数+3个状态机+~50F位报警体系+指示灯逻辑)

### 4.6 测试与一致性
- test:
  - 05_测试与验证\程序导出一致性检查报告_DJ-2026-005_V2.0.0.md
  - 05_测试与验证\整改方案_DJ-2026-005_梯形图对照通用ST一致性整改_V1.0.0.md
- change_mgmt:
  - 04_监控\01_变更管理\02_变更记录\01_版本变更台帐.md
- delivery:
  - 06_文档与交付\验收交付清单\验收交付清单.md

### 4.7 ST开发范围外 — 明确忽略清单
> 完整清单已归档至 [06_PM_SESSION历史/2026-08-02_V9.1.0_archive.md](00_项目管理/06_PM_SESSION历史/2026-08-02_V9.1.0_archive.md)
- 🔴 忽略: .plc-out/ .trae/ 03_HMI/ 04_现场调试/ 04_驱动器/ 06_交付/ 07_技术支持/ 08_备件/ 09_总结/ 10_知识库/ *.gx3
- 🟡 部分: 05_测试与验证/(一致性报告) 00_项目管理/04_变更管理/(变更台帐)

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-08-02 CHG-DOCU-2026-002 PRD 四件套补齐: 创建 7 个 PRD 文档（GlobalVars DSN/UM、FB_1002 CHG/UM、FB_External CHG/UM、FB_1003 UM），全 7 模块 IFC+DSN+CHG+UM 100% 完整 | 文档补全完成，已对账
  - 2026-08-02 CHG-DOCU-2026-001 驾驶舱闭环: 审查问题修复 — PM_SESSION 版本对齐与文档一致性整治，9 步状态流转完成 | 已闭环
  - 2026-07-22 CHG-PLC-2026-007 FB_2001输出变量前缀修补与OB1注释清洗 | 规范修补完成,已对账
  - (早期 change_log 已归档至 06_PM_SESSION历史/2026-08-02_V9.1.0.md)
- refactor_log:
  - (Log entries archived)
- bug_log: (已归档至 06_PM_SESSION历史/2026-08-02_V9.1.0_archive.md)
  - 2026-05-20 TC11 Z轴定位测试失效 (P0, ✅已修复 V7.1.1)
  - 2026-05-18 OB1针脚不匹配 (P0, ✅已修复)
- iteration_log:
  - (早期迭代日志已归档至 06_PM_SESSION历史/2026-08-02_V9.1.0.md)

## 6. Implementation Log
- 2026-08-02 | CHG-DOCU-2026-002: 补齐 7 个 PRD 文档 → 全模块 IFC+DSN+CHG+UM 100% | plc check 21/21, 台账 0/0/0 [已验证]
- 2026-08-02 | CHG-DOCU-2026-001 闭环 + CHG-PLC-2026-008/009 retrofit: 审查修复+版本演进空白填充 | plc check 21/21, 台账 0/0/0 [已验证]
- 2026-08-01 | CHG-DOCU-2026-001: PM_SESSION 版本对齐与文档一致性整治 | plc check 20P/1W/0F [已验证]
- 早期 Implementation Log 已归档至 [06_PM_SESSION历史/](00_项目管理/06_PM_SESSION历史/)

## 7. Verification Log
> 详细验证记录已归档至 [06_PM_SESSION历史/2026-08-02_V9.1.0_archive.md](00_项目管理/06_PM_SESSION历史/2026-08-02_V9.1.0_archive.md)
- 2026-06-17: 测试文件修复静态审查 (basic_test.scltest V7.1.1) — TC01-TC11 RESET段覆盖审查，TC11 轴使能/断言/状态转换修复 [已验证(静态)]
- 2026-06-16: 规范审查与兼容性验证 — LSP-905/904 合规，FB_1011/1012 参数匹配，向后兼容 [已验证(静态)]
- blocker: 缺少 TIA Portal 编译环境与 .scltest 测试执行环境

## 8. Handoff Notes
- 2026-08-02 | from=pm-workflow | reason=P2 任务收尾
  - current_state: CHG-DOCU-2026-002 已闭环，全 7 模块 PRD 四件套 100% 完整，台账 0/0/0，spec 无漂移。[已验证]
  - next_focus: P0: TIA Portal 编译验证
  - watchouts: 无 .scltest 运行环境 | 修改 .scl 前触发 plc-electrical-engineer | 后续变更必须走 CHG 闭环
  - read_first: PM_SESSION §3.1 (版本演进矩阵), CHG-DOCU-2026-002.md

## 9. Next Actions
- [P0] TIA Portal 编译验证 FB_1002 V10.0.0 | done_when=无编译错误

## Spec Snapshot（基线，供版本漂移检测）
| spec_id | 版本 | 记录日期 | 说明 |
|---------|------|---------|------|
| PROJ-016 | V1.2.0 | 2026-08-01 | 通用项目结构模板 (已漂移 V1.1.0→V1.2.0，已确认) |
| REQ-020 | V1.1.0 | 2026-06-06 | 通用需求分析文档模板 |
| LSP-905 | V1.0.3 | 2026-06-06 | SCL编程规范 |
| LSP-904 | V1.2.0 | 2026-06-06 | SCL注释规范 |
| LSP-903 | V2.1.0 | 2026-06-06 | 定时器使用规范 |
| LSP-906 | V2.0.0 | 2026-06-06 | PLC编程错误预防规则 |
| LSP-907 | V1.2.1 | 2026-06-06 | PLC项目配置规范 |
| INT-815 | V1.1.0 | 2026-06-06 | PLC接口文档模板 |
| PLC-023 | V2.1.0 | 2026-06-06 | PLC程序设计文档模板 |
| DEV-004 | V1.1.1 | 2026-06-06 | 通用项目文档版本管理与变更核心规范 |
| CHG-040 | V2.2.0 | 2026-08-01 | 通用变更单模板 (已漂移 V2.1.0→V2.2.0，已确认) |
| CHG-041 | V2.1.0 | 2026-06-06 | 通用版本变更台帐模板 |
| PM-042 | V2.3.0 | 2026-06-06 | 通用变更管理流程规范 |
