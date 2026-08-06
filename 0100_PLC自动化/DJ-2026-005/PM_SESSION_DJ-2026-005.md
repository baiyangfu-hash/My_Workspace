# PM_SESSION_DJ-2026-005

## 0. Meta
- project_id: DJ-2026-005
- project_name: 边框缓存机
- project_root: c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\DJ-2026-005
- last_updated: 2026-08-07
- owners: fubai / PLC开发团队

## 1. Positioning（项目定位）
- one_liner: 边框缓存机 PLC/HMI 软件工程交付与维护
- users: 设备调试/维护工程师；产线操作人员
- non_goals: 待补充

## 2. Current Focus（当前焦点）
- current_focus: HMI 原型设计补齐 — 补充 11 页面高保真可交互 HTML 原型（含 IO 监控页），HMI 交付物完整
- milestone: 全 7 模块 PRD 四件套 100% 完整；HMI 设计文档 + 原型 100% 完整；台账 0/0/0 ✅
- acceptance:
  - ✅ CHG-DOCU-2026-001 闭环 | CHG-PLC-2026-008/009 retrofit | 台帐 005/006 修复
  - ✅ CHG-DOCU-2026-002 闭环 (补齐 7 个 PRD 文档) | 台账 0/0/0 | plc check 21/21
  - ✅ Spec Snapshot 漂移已确认 | LSP-906/907 无漂移 | PM_SESSION 归档 302→150 行
  - ✅ HMI 原型设计补齐 (11 页面高保真可交互 HTML，含新增 IO 监控页)

## 3. Status Summary（当前状态摘要）
- in_progress:
  - HMI 原型交付物补齐 (11 页面 HTML 原型，含新增 IO 监控页)
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
  - (早期迭代日志已归档至 06_PM_SESSION历史/2026-08-02_V9.1.0.md)

### 4.7 HMI 设计层（03_HMI设计/，HMI-V1.6.0，设计文档+原型 ✅ 齐全）
- hmi-fa:  03_HMI设计\HMI功能分析报告.md ✅ (15基本+2窗口画面, 49类报警, 3级权限)
- hmi-dsn: 03_HMI设计\HMI详细设计说明书.md ✅ (HMI-V1.2.0→V1.3.0, 10页面清单+变量映射+宏设计)
- hmi-pro:  03_HMI设计\HMI原型设计.html ✅ (2026-08-07 V1.6, 工艺方向纠正：①机器人→放边框→本机平台 ②本机→送边框→打胶机→送成品→组框机；两页信号收发徽章/面板名/底部时序说明全部按用户现场工艺重命名)
- hmi-pro-v1.5: 03_HMI设计\HMI原型设计_V1.5_历史备份.html (V1.5 极简左右对照·工艺方向未纠正版备份)
- hmi-pro-v1.4: 03_HMI设计\HMI原型设计_V1.4_历史备份.html (V1.4 工业SCADA风格备份)
- hmi-pro-v1.3: 03_HMI设计\HMI原型设计_V1.3_历史备份.html (V1.3 组框机竖排模板备份)
- hmi-um:   03_HMI设计\操作手册\HMI操作手册.md ✅ (操作说明)
- hmi-src:  03_HMI设计\编译器HMI源程序\边框缓存机.prx (GP-Pro EX源文件)

## 6. Implementation Log
- 2026-08-07 | 通用原型 CLI 指令验证: 使用全新 `auto-pm prototype check --pid DJ-2026-005` 完成 80 个 PLC 寄存器标记与 HTML 语法一致性验证；运行 `auto-pm prototype bundle --pid DJ-2026-005 --version V1.6.1` 完成单文件归档备份 `HMI原型设计_V1.6.1_历史备份.html` | 008 通用 prototype CLI [已验证(实际)]
- 2026-08-07 | HMI原型 V1.6 工艺方向纠正: [HMI原型设计.html](03_HMI设计/HMI原型设计.html) 用户明确现场工艺：①机器人交互=机器人把边框放到本机平台上 ②打胶机交互=本机把边框送给打胶机，打胶完成后打胶机给组框机；两页交互方向徽章(发/收)、面板名、信号文字描述、标题栏pill、页脚时序说明全部重写匹配真实工艺；V1.5原版备份 [HMI原型设计_V1.5_历史备份.html](03_HMI设计/HMI原型设计_V1.5_历史备份.html) | HMI-V1.5→V1.6 [已验证(静态)]
- 2026-08-07 | HMI原型 V1.5 极简版改版: [HMI原型设计.html](03_HMI设计/HMI原型设计.html) 用户反馈V1.4 SCADA风太复杂怪+不好理解 → 两交互页彻底简化为左右列对照(x-* 样式族)：上下两大块(打胶机=入料/出料 机器人=抓取/放盘)，每块 3列 grid：左本机4信号(发/收徽章) 右对端4信号 最右异常放行竖排大按钮；去掉8步进度条/底部两张统计卡片，时序说明压缩为底部一行文字；V1.4 备份 [HMI原型设计_V1.4_历史备份.html](03_HMI设计/HMI原型设计_V1.4_历史备份.html)。| HMI-V1.4→V1.5 保留 1280×800 大尺寸 [已验证(静态)]
- 2026-08-07 | HMI交互画面改版: [HMI原型设计.html](03_HMI设计/HMI原型设计.html) 打胶机交互+机器人交互两页完整替换为组框机模板信号表风格（竖排主标签+4色子标签+信号行含红黄色(1)(4)(5)(7)/(2)(3)(6)(8)编号+地址tag+大圆形LED+竖排异常放行按钮+右上角✕关闭）。打胶机入料/出料双块 16信号，机器人码料/成品双块 16信号；(1)(4)(5)(7)=本机发出(2)(3)(6)(8)=对端发出 交替握手时序 | CSS新增.xface-* 完整样式族 [已验证(静态)]
- 2026-08-06 | HMI原型补齐: 新增 [HMI原型设计.html](03_HMI设计/HMI原型设计.html) → 11页面高保真可交互原型，含新增IO监控页；覆盖登录/主画面/手动/自动/参数/状态/IO/报警/打胶机交互/机器人交互/系统设置 | 原型可直接浏览器打开，顶部Tab+画面内按钮均可跳转 [已验证(静态)]
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
- 2026-08-07 | from=pm-workflow | reason=HMI原型 V1.6 工艺方向纠正 (用户描述真实现场工艺)
  - current_state: HMI原型 V1.6，核心纠正真实工艺方向：①机器人交互页 = 机器人 →(放边框)→ 本机上料平台；②打胶机交互页 = 本机 →(送边框)→ 打胶机(打胶)→(送成品)→ 组框机；两页面板名/方向徽章(发/收)/信号描述/标题pill/页脚时序全部重写匹配真实工艺。四版历史备份保留：V1.3组框机模板 / V1.4 SCADA复杂版 / V1.5 极简对照(方向未纠) / V1.6 极简对照(方向已纠主文件)
  - next_focus:
    1. [P0] TIA Portal 编译验证（现场环境）
    2. [P1] 用户走查 V1.6：两交互页工艺方向是否符合现场、信号名/地址是否要继续调整
  - skill_handoff: 若信号地址/握手时序确认后需同步 .prx，触发 plc-electrical-engineer 技能
  - watchouts:
    - 代码约束: .prx 需 GP-Pro EX；信号地址tag 需 PLC DB/接线双核对
    - 流程约束: V1.6 信号数量(16/握手8步/收发对称 (1)(4)(5)(7)发 (2)(3)(6)(8)收)逻辑未变，仅命名+方向+文字改工艺化
    - 环境约束: 无 TIA Portal/.scltest 编译执行环境
  - read_first:
    1. [HMI原型设计.html](03_HMI设计/HMI原型设计.html) (V1.6 工艺方向已纠主文件)
    2. [HMI原型设计_V1.5_历史备份.html](03_HMI设计/HMI原型设计_V1.5_历史备份.html) (V1.5 工艺方向未纠备份)
    3. [HMI原型设计_V1.4_历史备份.html](03_HMI设计/HMI原型设计_V1.4_历史备份.html) (V1.4 SCADA风)
    4. [HMI原型设计_V1.3_历史备份.html](03_HMI设计/HMI原型设计_V1.3_历史备份.html) (V1.3 组框机模板)
    5. [HMI详细设计说明书.md](03_HMI设计/HMI详细设计说明书.md) §5 变量映射表

## 9. Next Actions
- [P0] TIA Portal 编译验证 FB_1002 V10.0.0 | done_when=无编译错误
- [P1] 用户走查 V1.6：工艺方向(机器人放料到本机/本机送料到打胶机→组框机)是否完全符合现场真实逻辑 | done_when=用户确认工艺方向
- [P2] 走查通过后若需同步 .prx，触发 plc-electrical-engineer 技能同步更新 HMI 源程序

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
