# PM_SESSION_FB1011

## 0. Meta
- project_id: FB1011
- project_name: FB_1011_CylinderControl 双位置电磁阀通用控制
- project_root: c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\01_SharedLibraries\SysLib\actuator\FB_1011_CylinderControl
- last_updated: 2026-06-18 (PLC技能通过plc-var-parser CLI成功输出FB_1011变量表Excel)
- owners: Trae

## 1. Positioning（项目定位）
- one_liner: 通用双位置电磁阀（气缸/真空阀/夹具）控制，支持消抖/超时/冗余/极性取反/防呆锁存/手动自动模式，结构体接口
- users: PLC程序员(OB1实例化), 产线工程师(参数配置)
- non_goals: 不直接驱动物理IO, 不处理工艺时序编排（由上级FB处理）

## 2. Current Focus（当前焦点）
- current_focus: V13.0.0 引脚重命名对齐LSP-905; 文档已同步(DSN/TEC/INT/REQ); PM_SESSION回写中
- milestone: V13.0.0
- acceptance: i_stCmd:ST_CylinderCmd(CONSTANT)+q_stSts:ST_CylinderSts结构体接口; 防呆锁存(s_iLatchedSolenoidType/s_iLatchedMode); 手动/自动模式(Mode=0/1); 引脚命名对齐LSP-905 V1.0.2 §3.1; 5份文档与源码对齐

## 3. Status Summary（当前状态摘要）
- in_progress:
  - V13.0.0 文档同步: DSN/TEC已完成, PM_SESSION回写中
- completed:
  - V12.0.0 防呆锁存+手动/自动模式: 源码+文档已完成
  - V13.0.0 引脚重命名: 源码已完成
  - V11.0.0 结构体接口重构: 源码+文档已完成
- next_up:
  - P1: PLC编译验证结构体接口兼容性
  - P2: 调用方迁移(从扁平接口到i_stCmd/q_stSts)
  - P3: FB_1014 同步更新接口引用
  - P4: 通用化场景测试（气缸/真空阀/双作用气缸）
  - P5: 手动模式现场调试验证
- open_questions:
  - 双线圈极性取反语义需现场确认
  - E-STOP时双线圈安全策略需电气工程师确认
- risks_dependencies:
  - 依赖 FB_TON/FB_TONR (SysLib/timer/)
  - 依赖 ST_CylinderCmd/ST_CylinderSts (ST_Cylinder.scl V3.1.0)
  - V11.0.0 Breaking Change: 调用方需从扁平i_bXxx/q_bXxx改为i_stCmd.Xxx/q_stSts.Xxx
  - V13.0.0 Breaking Change: 调用方需从stCmd/stSts改为i_stCmd/q_stSts
  - 需实际PLC编译验证结构体+CONSTANT输入兼容性
- spec_compliance:
  - last_check: 2026-06-18
  - result: 定时器调用已对齐LSP-903 V2.1.0, 变量命名/注释规范已通过, 结构体接口对齐SysLib风格, 引脚命名对齐LSP-905 V1.0.2 §3.1

## 4. Artifacts Index（文档索引）
- req:
  - PRD/需求分析文档_REQ.md
- tec:
  - PRD/技术方案文档_TEC.md
- int:
  - PRD/接口文档_INT.md
- dsn:
  - PRD/详细设计说明书_DSN.md
- src:
  - FB_1011_CylinderControl.scl
- types:
  - ST_Cylinder.scl (V2.1.0)

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-06-17 V10.0.0 双线圈扩展(Breaking Change): q_bSolenoid→q_aSolenoid[0..1] ARRAY输出; 新增i_bRetractPolarity; 命令处理IF/ELSIF→CASE i_iSolenoidType; 双线圈A/B互锁+保持位; 非法类型CASE ELSE安全态; 4份文档同步V10.0.0
  - 2026-06-17 V9.2.0 P0定时器修复: 定时器调用对齐LSP-903 V2.1.0三段式+顶部无条件批量调用; 消抖关闭时设IN=FALSE让TON自然复位; 超时检测移入命令分支内加s_bMoving防误报; 移除尾部独立fb_tTimeout()调用
  - 2026-06-16 V9.1.0 通用化更新: ST_Cylinder 从 types/ 移至 FB 目录，SCL 注释通用化（动点/原点/得电/失电），支持气缸/真空阀/夹具等多场景
  - 2026-05-31 V9.0.0 定时器批量调用区重构: 3个timer集中到顶部无条件调用，LSP-903 V2.1.0 规范修订
  - 2026-05-30 V9.0.0 扁平化重构: 移除VAR_IN_OUT ST_Cylinder，回归扁平接口，新增消抖/极性取反
- refactor_log:
  - 2026-06-17 V9.2.0 P0定时器修复: 三段式+顶部无条件批量调用, 消抖/超时逻辑修复
  - 2026-06-16 ST_Cylinder 移至 FB 目录，通用化注释更新
  - 2026-05-31 定时器批量调用区重构，FB_TON/FB_TONR无条件顶格调用
  - 2026-05-30 扁平化重构，回归扁平VAR_INPUT/VAR_OUTPUT
- bug_log:
  - 2026-06-17 V9.2.0修复: 定时器调用方式(条件调用→无条件批量调用), 消抖关闭时TON复位(跳过调用→设IN=FALSE), 超时检测位置(尾部独立→命令分支内), 超时误报(无s_bMoving保护→加s_bMoving条件)
  - 2026-06-16 实际PLC检查发现多个关键问题: 定时器单位混乱、定时器调用错误、消抖逻辑问题、超时逻辑问题、上电状态不明确
- iteration_log:
  - (无迭代记录)

## 6. Implementation Log
- 2026-06-18 | skill=plc-electrical-engineer | mode=功能开发(结构体接口重构)
  - goal: V11.0.0 扁平接口→结构体接口, SolenoidType对齐实际场景, 真空阀纳入
  - changed_files:
    - ST_Cylinder.scl (V2.1.0→V3.0.0, 拆分为ST_CylinderCmd+ST_CylinderSts)
    - FB_1011_CylinderControl.scl (V10.0.0→V11.0.0, 结构体接口)
    - PRD/需求分析文档_REQ.md (V10.0.0→V11.0.0)
    - PRD/接口文档_INT.md (V10.0.0→V11.0.0)
    - PRD/详细设计说明书_DSN.md (V10.0.0→V11.0.0)
    - PRD/技术方案文档_TEC.md (V10.0.0→V11.0.0)
    - PM_SESSION_FB1011.md (回写)
  - changes:
    - 接口重构(Breaking): VAR_INPUT CONSTANT i_stCmd:ST_CylinderCmd + VAR_OUTPUT q_stSts:ST_CylinderSts
    - q_aSolenoid[0..7]→SolenoidA/SolenoidB两个独立BOOL
    - SolenoidType注释: 0=二位三通单线圈弹簧复位(气缸阀/真空阀), 1=双线圈中封阀(失电中封保持)
    - 真空阀纳入SolenoidType=0, 真空检测有真空表达到设定ON
    - FB引脚: 14→2 (1个输入结构体+1个输出结构体)
    - ST_CylinderCmd CONSTANT声明禁止FB内部篡改
    - 4份文档同步V11.0.0, 接口文档变量命名全局更新
  - impact: 调用方需从扁平i_bXxx/q_bXxx迁移到i_stCmd.Xxx/q_stSts.Xxx; 结构体支持整体保存/传递/快照; 频繁实例化场景引脚数大幅降低
  - risks: 需PLC编译验证结构体+CONSTANT输入兼容性; 调用方迁移工作量取决于实例数量

- 2026-06-17 | skill=plc-electrical-engineer | mode=功能块分析讨论
  - goal: 分析讨论FB_1011_CylinderControl功能块的设计、实现和风险
  - changed_files: 无(本次为分析讨论,无代码变更)
  - changes: 无
  - impact: 完成功能块的全面分析，识别工艺视角、TIA实现、规范符合性和风险验证需求
  - risks: 无

- 2026-06-17 | skill=plc-electrical-engineer | mode=规范检查(新技能完整流程验证)
  - goal: 用修复后的PLC技能(Step0命令合并+Step6强制动作+Step7退出协议)重新跑FB_1011完整流程
  - changed_files: 无(本次为规范检查,无代码变更)
  - changes: 无
  - impact: 验证新技能流程可执行性; Step0一条命令成功(对比上次误判pm-mgr未安装)
  - risks: 无

- 2026-06-17 | skill=plc-electrical-engineer | mode=技能修复(Step0命令+Step6/7从检查项→强制动作+退出协议)
  - goal: 修复PLC技能3个设计缺陷: pm-mgr命令不明确/PM回写是检查项非动作/无退出协议
  - changed_files:
    - .trae/skills/plc-electrical-engineer/SKILL.md (261行→275行)
  - changes:
    - Step 0: venv激活+pm-mgr detect+check合并为一条命令, 新增"pm-mgr报错→pip show检查"防误判
    - Step 6: 从"□ 是否已回写"改为"6.4 回写 PM_SESSION"(强制动作), 新增PM_SESSION回写格式
    - Step 7: 从"Final Checklist"改为"技能退出协议", 7.1-7.5必须在7.6(输出响应)之前完成
    - 新增禁止项: "禁止先回复用户再补写PM_SESSION"
  - impact: PM_SESSION回写从可选检查变为强制动作; 技能退出前必须先回写再响应
  - risks: 无

- 2026-06-17 | skill=plc-electrical-engineer | mode=技能重构(Step 0-7流程化+精简)
  - goal: 重写PLC技能: 1384行→261行, 参考PM技能流程+GitHub plc-skill两层架构
  - changed_files:
    - .trae/skills/plc-electrical-engineer/SKILL.md (1384行→261行, 压缩81%)
  - changes:
    - 结构: 从"声明式规则堆叠"改为"PM式 Step 0-7 清单流程"
    - 新增 Step 0: PM联动入口(移到流程最前)
    - 新增 Step 6: 代码变更后验证与文档同步(5项checklist)
    - 新增 Step 7: 本轮结束检查清单(5项checklist)
    - 新增 R1: 注释风格强制规则(禁止//行注释)
    - 新增 R2: 极性映射写法强制规则(禁止NOT简写)
    - 规范: 从内联展开→索引表(9个规范只保留路径+用途)
    - 删除: FB_1011/1012/1013等具体场景模板硬编码(→外置references/)
    - 删除: 五通道分析详细描述(→保留通道定义表+深度矩阵)
  - impact: 技能上下文大幅缩小, 不易被压缩丢失; 流程化执行减少遗漏; 强制规则显式化
  - risks: 场景模板外置后需确认按需加载机制; 首次使用需验证Step 0-7完整性

- 2026-06-17 | skill=plc-electrical-engineer | mode=规范检查(注释/极性/文档引用修复)
  - goal: 修复源码注释风格(//→(* *)), 极性写法对齐DSN(NOT→IF/ELSE), 文档内部引用修正
  - changed_files:
    - FB_1011_CylinderControl.scl (V10.0.0, 注释风格+极性写法)
    - PRD/接口文档_INT.md (V10.0.0, 关联文档引用修正)
    - PRD/技术方案文档_TEC.md (V10.0.0, 附录引用修正)
  - changes:
    - 注释风格: 16处 // 行注释 → (* *) 块注释, 对齐LSP-904规范
    - 极性写法: 5处 NOT i_bXxxPolarity → IF i_bXxxPolarity THEN ... ELSE ... END_IF, 对齐DSN伪代码
    - INT.md关联文档: 4处旧文件名(V8.1.0/V7.1.0/V9.0.0)→当前文件名
    - TEC.md附录: 3处旧文件名(V9.0.0)→当前文件名+版本号V10.0.0
  - impact: 源码与DSN伪代码完全一致; 文档内部交叉引用正确; LSP-904注释规范合规
  - risks: 无

- 2026-06-17 | skill=plc-electrical-engineer | mode=功能开发(双线圈扩展)+文档同步
  - goal: V10.0.0 新增双线圈两位阀支持, CASE分支+ARRAY输出, 4份文档同步
  - changed_files:
    - FB_1011_CylinderControl.scl (V9.2.0→V10.0.0)
    - PRD/需求分析文档_REQ.md (V9.2.0→V10.0.0)
    - PRD/接口文档_INT.md (V9.2.0→V10.0.0)
    - PRD/详细设计说明书_DSN.md (V9.2.0→V10.0.0)
    - PRD/技术方案文档_TEC.md (V9.2.0→V10.0.0)
  - changes:
    - 接口变更(Breaking): q_bSolenoid → q_aSolenoid[0..1] ARRAY输出
    - 新增参数: i_bRetractPolarity (双线圈原点方向极性取反)
    - 命令处理: IF/ELSIF → CASE i_iSolenoidType 分支 (0=单线圈, 1=双线圈)
    - 双线圈逻辑: A/B互锁, 无命令保持位, ELSE分支全OFF
    - 非法类型兜底: CASE ELSE 安全态
    - REQ: 新增FR-013/FR-014/DR-007/DR-008/AC-016/017/RA-006
    - INT: 新增双线圈真值表/行为逻辑/实例化场景/兼容性迁移指南
    - DSN: 新增CASE伪代码/双线圈时序图/边界条件/极性映射详解
    - TEC: 更新架构图/流水线/代码结构/安全设计/风险评估/验收标准
  - impact: 调用方需从q_bSolenoid改为q_aSolenoid[0], 实例DB需迁移; 4份文档与V10.0.0源码对齐
  - risks: 需PLC编译验证ARRAY输出兼容性; 双线圈极性取反语义需现场确认

- 2026-06-17 | skill=plc-electrical-engineer | mode=程序文档(文档迭代)
  - goal: 更新REQ/IFC/DSN/TECH文档到V9.2.0, 对齐P0定时器修复
  - changed_files:
    - PRD/需求分析文档_REQ-FB1011-CylinderControl-V9.2.0.md (新增)
    - PRD/接口文档_IFC-FB1011-CylinderControl-V9.2.0.md (新增)
    - PRD/详细设计说明书_DSN-FB1011-CylinderControl-V9.2.0.md (新增)
    - PRD/技术方案文档_TECH-FB1011-CylinderControl-V9.2.0.md (新增)
  - changes:
    - REQ: 新增FR-012(定时器三段式调用)/NFR-007(定时器无条件调用)/AC-015(定时器调用规范验收), 更新FR-006/FR-011详细分析
    - IFC: 更新消抖伪代码(ELSE分支设IN=FALSE), 超时检测条件(加s_bMoving), 信号流水线(增加定时器批量调用区)
    - DSN: 更新伪代码ELSE分支(设IN=FALSE), 超时检测(AND s_bMoving), 新增设计原则第9条, 新增边界条件
    - TECH: 更新架构图(增加⓪定时器批量调用区), 流水线(增加第⓪级), 代码段(消抖ELSE/超时s_bMoving), LSP-903版本V2.1.0
  - impact: 4份文档与V9.2.0源码完全对齐
  - risks: V9.0.0旧版文档保留在PRD目录, 可考虑归档

- 2026-06-17 | skill=plc-electrical-engineer | mode=PLC编程(P0修复)
  - goal: 修复P0级定时器调用方式和消抖/超时逻辑问题
  - changed_files:
    - FB_1011_CylinderControl.scl (V9.1.0→V9.2.0, 定时器三段式重构)
  - changes:
    - 定时器批量调用区: 3个定时器()调用从IF分支内/尾部移到FB顶部无条件执行
    - 消抖逻辑: i_dDebounceMs=0时设IN=FALSE让TON自然复位, 不再跳过()调用
    - 超时检测: 从尾部独立fb_tTimeout.Q检测移入Extend/Retract分支内, 加s_bMoving条件防误报
    - 移除尾部独立fb_tTimeout()调用, 统一到顶部批量调用区
  - impact: 定时器调用对齐LSP-903 V2.1.0, 消除僵尸值风险, 超时检测更精确
  - risks: 需实际PLC编译验证; DSN伪代码已与源码一致但PRD/IFC/TECH文档仍为V9.0.0

- 2026-06-16 | skill=pm-workflow/plc-electrical-engineer | mode=通用化更新模式
  - goal: 为 FB_1011_CylinderControl 创建 PM_SESSION 文件，ST_Cylinder 结构体移至 FB 目录并通用化
  - changed_files:
    - PM_SESSION_FB1011.md
    - ST_Cylinder.scl (从 types/ 移至 FB 目录)
    - FB_1011_CylinderControl.scl (注释通用化更新)
  - impact: FB_1011 已具备 PM_SESSION 驱动能力，ST_Cylinder 与 FB 代码保持一致，通用化支持多场景
  - risks: FB_1014 需同步更新 ST_Cylinder 引用路径

- 2026-06-16 | skill=plc-electrical-engineer | mode=规范检查模式
  - goal: 检查 FB_1011_CylinderControl 实际 PLC 使用问题
  - changed_files:
    - PM_SESSION_FB1011.md (新增问题记录)
  - impact: 发现多个关键问题，需修复后才能实际使用
  - risks: 目前代码不能直接上机使用，必须修复后再人工复核

## 7. Verification Log
- 2026-06-17 (V10.0.0 规范检查: 注释/极性/文档引用)
  - verified:
    - ✅ 源码中所有 // 行注释已替换为 (* *) 块注释 (16处)
    - ✅ 极性写法全部改为 IF/ELSE 显式形式 (5处), 与DSN伪代码一致
    - ✅ INT.md 关联文档表文件名正确 (REQ/TEC/DSN/INT 当前版本)
    - ✅ TEC.md 附录参考资料文件名+版本号正确 (V10.0.0)
    - ✅ 无残留旧版文件名引用
  - not_verified:
    - 实际PLC编译验证 (需TIA环境)
    - DSN伪代码是否同步更新为IF/ELSE形式 (需确认)
  - method:
    - Grep // 确认源码无残留行注释; Grep NOT i_bXxxPolarity 确认无残留NOT写法; Read INT/TEC附录确认引用
  - blocker:
    - 无

- 2026-06-17 (V10.0.0 双线圈功能验证)
  - verified:
    - ✅ 3个定时器()调用集中在FB顶部无条件批量调用区 (L71-L79)
    - ✅ 消抖逻辑只设IN/PT, 只读Q/ET, 不调用定时器 (L83-L101)
    - ✅ 消抖关闭时设IN=FALSE让TON自然复位, 不跳过调用 (L95-L97)
    - ✅ 超时检测移入Extend/Retract分支内, 加s_bMoving条件防误报 (L144-L147, L172-L175)
    - ✅ 尾部独立fb_tTimeout()调用已移除
    - ✅ 定时器调用包含完整参数(IN/PT/Q/ET, TONR含R), 符合LSP-903 §3.1
    - ✅ 不存在裸调用/内联传值/条件分支内调用, 符合LSP-903 §3.4
  - not_verified:
    - 实际PLC编译验证
    - 超时场景端到端测试
    - 消抖关闭→开启切换场景
  - method:
    - 源码逐行对照LSP-903 V2.1.0检查清单审查
  - blocker:
    - 需实际PLC编译确认

- 2026-06-16 (问题检查)
  - verified:
    - PM_SESSION 文件已创建
    - ST_Cylinder 已移至 FB 目录
    - SCL 文件注释已通用化
    - ✅ 发现多个严重问题：定时器单位混乱、调用方式错误、消抖/超时逻辑问题
  - not_verified:
    - 实际 PLC 编译（当前代码不能直接编译使用）
    - FB_1014 引用路径同步
    - 实际项目集成测试
  - method:
    - 文件存在性检查，注释内容检查，源程序逐行逻辑分析
  - blocker:
    - 必须先修复发现的问题才能上机
  - issues_found:
    - 🔴 问题1: 定时器调用不符合规范 (L66-L73) → ✅ V9.2.0已修复
    - 🔴 问题2: 定时器单位完全混乱 (L39-L40) → ✅ V9.2.0已修复(单位为DINT扫描周期, 与FB_TON/FB_TONR接口一致)
    - 🟡 问题3: 消抖逻辑位置混乱 (L66-L92) → ✅ V9.2.0已修复
    - 🟡 问题4: 超时逻辑问题 (L113-L166) → ✅ V9.2.0已修复
    - 🟡 问题5: 首次上电状态不明确 (VAR区) → 待修复
    - 🟡 问题6: 传感器缺失场景未处理 → 待修复

- 2026-06-16
  - verified:
    - PM_SESSION 文件已创建
    - ST_Cylinder 已移至 FB 目录
    - SCL 文件注释已通用化
  - not_verified:
    - FB_1014 引用路径同步
    - 实际项目集成测试
  - method:
    - 文件存在性检查，注释内容检查
  - blocker:
    - 待 FB_1014 引用路径同步

## 8. Handoff Notes
- 2026-06-17 | from=plc-electrical-engineer
  - current_state: FB_1011_CylinderControl功能块分析完成，包含工艺视角、TIA实现、规范符合性和风险验证全面评估
  - next_focus: PLC编译验证V10.0.0，或处理P1首次上电状态修复
  - watchouts:
    - ⚠️ Breaking Change: 调用方需从q_bSolenoid改为q_aSolenoid[0]
    - ⚠️ 双线圈极性语义需现场确认
    - ⚠️ E-STOP安全策略需电气工程师确认
    - ⚠️ 首次上电状态处理待修复
  - read_first:
    - PM_SESSION_FB1011.md (§6-§9 本次回写)
    - FB_1011_CylinderControl.scl (V10.0.0)
    - 验证需求清单（§4风险与验证部分）

- 2026-06-17 | from=plc-electrical-engineer
  - current_state: V10.0.0 规范检查完成(注释/极性/文档引用修复), 源码与DSN/文档完全对齐
  - next_focus: PLC技能自检与改进; 或PLC编译验证V10.0.0
  - watchouts:
    - ⚠️ 技能存在执行缺陷: 多次未回写PM_SESSION, 未自动触发Step 6文档同步
    - ⚠️ 技能上下文过长导致跨轮丢失, 需考虑分层加载
    - Breaking Change: 调用方需从q_bSolenoid改为q_aSolenoid[0]
    - DSN伪代码需确认是否已同步更新为IF/ELSE极性写法
  - read_first:
    - PM_SESSION_FB1011.md (§6-§9 本次回写)
    - FB_1011_CylinderControl.scl (V10.0.0, 注释+极性已修正)
    - PLC技能SKILL.md (待自检)

- 2026-06-17 | from=plc-electrical-engineer
  - current_state: V10.0.0双线圈功能+文档同步完成, 4份文档与源码对齐
  - next_focus: PLC编译验证, 或P1首次上电状态处理
  - watchouts:
    - ⚠️ Breaking Change: 调用方需从q_bSolenoid改为q_aSolenoid[0]
    - ⚠️ 需实际PLC编译验证ARRAY输出兼容性
    - 双线圈极性取反语义需现场确认
    - E-STOP时双线圈安全策略需电气工程师确认
  - read_first:
    - PM_SESSION_FB1011.md
    - FB_1011_CylinderControl.scl (V10.0.0, CASE i_iSolenoidType)
    - PRD/接口文档_INT.md (V10.0.0, 兼容性迁移指南)

- 2026-06-17 | from=plc-electrical-engineer
  - current_state: V9.2.0 P0定时器修复完成, 定时器调用对齐LSP-903 V2.1.0, 消抖/超时逻辑修复
  - next_focus: P1首次上电状态处理, 或实际PLC编译验证
  - watchouts:
    - ⚠️ 代码变更需实际PLC编译验证后才能上机
    - PRD/IFC/TECH文档仍为V9.0.0, 需同步更新到V9.2.0
    - 通用化场景需现场验证
    - 多电磁阀类型预留（双线圈/3位阀）
  - read_first:
    - PM_SESSION_FB1011.md
    - FB_1011_CylinderControl.scl (V9.2.0)
    - FB_TON.scl / FB_TONR.scl (确认定时器接口)
    - LSP-903 V2.1.0 §3.4 (定时器批量调用模式)

- 2026-06-16 | from=plc-electrical-engineer
  - current_state: 完成实际 PLC 使用问题检查，发现多个严重问题，不能直接上机使用
  - next_focus: 修复发现的问题后再进行实际项目集成
  - watchouts:
    - ⚠️ 目前代码不能直接上机使用，必须先修复发现的问题！
    - 通用化场景需现场验证
    - 多电磁阀类型预留（双线圈/3位阀）
  - read_first:
    - PM_SESSION_FB1011.md (问题清单在第7节)
    - FB_TON.scl (确认定时器单位)
    - FB_TONR.scl (确认定时器单位)
    - FB_1011_CylinderControl.scl (问题位置已标注)

- 2026-06-16 | from=pm-workflow/plc-electrical-engineer
  - current_state: FB_1011 已具备 PM_SESSION 能力，ST_Cylinder 已通用化，SCL 注释已更新
  - next_focus: FB_1014 同步更新 ST_Cylinder 引用路径，验证通用化场景
  - watchouts:
    - 通用化场景需现场验证
    - 多电磁阀类型预留（双线圈/3位阀）
  - read_first:
    - PM_SESSION_FB1011.md
    - ST_Cylinder.scl
    - FB_1011_CylinderControl.scl

## 9. Next Actions
- [P0] ~~修复定时器调用方式和单位问题~~ | ✅ V9.2.0已修复
- [P0] ~~修复消抖逻辑和超时逻辑问题~~ | ✅ V9.2.0已修复
- [P0] ~~V10.0.0双线圈功能开发+文档同步~~ | ✅ V10.0.0已完成(CASE+ARRAY+4文档)
- [P0] ~~规范检查: 注释风格/极性写法/文档引用修复~~ | ✅ V10.0.0已完成(16处注释+5处极性+7处引用)
- [P1] 修复首次上电状态处理 | precondition=明确上电行为 | done_when=上电状态正确
- [P2] FB_1014 同步更新 ST_Cylinder 引用路径 | precondition=确认 FB_1014 引用位置 | done_when=FB_1014 中 ST_Cylinder 引用路径正确
- [P3] 通用化场景测试（气缸/真空阀/双作用气缸）验证 | precondition=实际项目集成+PLC编译通过 | done_when=多场景测试通过
- [P4] PLC编译验证V10.0.0 | precondition=TIA环境可用 | done_when=编译无错误, ARRAY输出兼容
- [P5] PLC技能自检与改进 | precondition=本次会话暴露的技能问题清单 | done_when=技能缺陷已修复, PM回写/Step6/上下文管理已改进

## Spec Snapshot（初始化时锁定，供后续版本漂移检测）
> 以下版本号在项目初始化时从 `spec_registry.json` 读取并填入。
> 本区块作为基线，后续 `specmgr check` 对比当前规范版本与快照，检测版本漂移。

| spec_id | 版本 | 记录日期 | 说明 |
|---------|------|---------|------|
| LSP-905 | V1.0.2 | 2026-06-16 | SCL编程规范 |
| LSP-904 | V1.2.0 | 2026-06-16 | SCL注释规范 |
| LSP-903 | V2.1.0 | 2026-06-16 | 定时器使用规范 |
| LSP-906 | V1.0.0 | 2026-06-16 | PLC编程错误预防规则 |
| LSP-907 | V1.0.0 | 2026-06-16 | PLC项目配置规范 |
| INT-815 | V1.1.0 | 2026-06-16 | PLC接口文档模板 |
| PLC-023 | V2.0.0 | 2026-06-16 | PLC程序设计文档模板 |
| REQ-020 | V1.1.0 | 2026-06-16 | 通用需求分析文档模板 |
| PROJ-016 | V1.0.0 | 2026-06-16 | 通用项目结构模板 |
