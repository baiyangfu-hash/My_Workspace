# PLC程序全面重写方案 - V5.0.0 架构重构

## 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | 边框缓存机 PLC程序全面重写方案 |
| **方案版本** | V5.0.0-DRAFT |
| **编制日期** | 2026-05-03 |
| **编制人** | Trae |
| **审核人** | [待审核] |
| **状态** | 📋 待用户批准 |

---

## 1. 重写背景与问题诊断

### 1.1 问题根源

```
历史演变导致的三层架构脱节：

时间线：
V4.0.0 (04-23) → 初始扁平化架构（中文命名）
V4.1.0 (04-25) → FB层改为英文命名（801规范V1.0.5）
V4.2.0 (04-29) → 文件结构优化，但OB1/GlobalVars未同步
V4.3.0 (05-02) → 新增OB1+GlobalVars（复制旧代码，仍为中文）
V4.2.0-fix (05-03) → 尝试修复FB_1001（部分成功，遗漏内部变量）

当前状态：
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  GlobalVars.db   │ ←→ │    OB1.scl      │ ←→ │ FB_1001/1002..  │
│   (中文 ✓)       │     │   (中文 ✓)      │     │  (英文 ✓)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                        匹配                     不匹配！编译失败
```

### 1.2 影响范围统计

| 文件 | 中文变量数 | 需修改行数 | 优先级 |
|------|-----------|-----------|--------|
| OB1.scl | 254处 | ~180行 | 🔴 高 |
| GlobalVars.db | ~220处 | ~250行 | 🔴 高 |
| FB_1001.scl | 10处 | 10行 | 🟡 中 |
| **合计** | **~484处** | **~440行** | - |

### 1.3 编译错误示例

```scl
(* 当前错误 - FB_1001第489行 *)
s_i活跃报警 := fbLayer2.o_iAlarmCode;
// Error: assignment to undeclared symbol: "s_i活跃报警" (TC001)

(* 原因：VAR声明中还是中文名，但应该用英文名 *)
VAR
    s_i活跃报警 : INT;  // ❌ 应改为: s_iActiveAlarmCode : INT;
END_VAR
```

---

## 2. 重写目标与原则

### 2.1 核心目标

✅ **统一性**：所有变量名100%英文，符合IEC 61131-3 + 801规范V1.0.5
✅ **可编译**：消除所有TC001/TC002类型声明错误
✅ **可维护**：清晰的命名语义，降低后期维护成本
✅ **文档同步**：所有相关文档同步更新至V5.0.0

### 2.2 设计原则

1. **最小变更原则**：只修改变量名，不改变业务逻辑和程序架构
2. **向后兼容**：保持现有功能块接口不变（FB_1001/1002/1003/1004已标准化）
3. **渐进式实施**：按依赖顺序分层修改，每步验证编译
4. **文档先行**：先更新规范文档，再修改代码

---

## 3. 新变量命名体系设计

### 3.1 命名映射规则

基于 **801_PLC变量命名与功能块命名规范_DEV-V1.0.5**，制定以下映射表：

#### 3.1.1 系统控制信号（公共部分）

| 中文变量名 | 英文变量名（新） | 类型 | 说明 |
|-----------|-----------------|------|------|
| `i_b使能` | `i_bEnable` | BOOL | 系统总使能 |
| `i_b自动模式` | `i_bAutoMode` | BOOL | 自动模式选择 |
| `i_b手动模式` | `i_bManualMode` | BOOL | 手动模式选择 |
| `i_b启动` | `i_bStart` | BOOL | 启动按钮 |
| `i_b停止` | `i_bStop` | BOOL | 停止按钮 |
| `i_b复位` | `i_bReset` | BOOL | 复位按钮 |

#### 3.1.2 输送机模块信号

| 中文变量名 | 英文变量名（新） | 类型 | 说明 |
|-----------|-----------------|------|------|
| `i_r输送速度` | `i_rConveyorSpeed` | REAL | 输送带速度设定 |
| `i_i分料时间` | `i_iSeparateTime` | INT | 分料动作保持时间(ms) |
| `i_i阻挡等待时间` | `i_iBlockWaitTime` | INT | 阻挡气缸动作等待时间(ms) |
| `i_b阻挡下降` | `i_bLx_BlockDown` | BOOL[4] | 手动-阻挡气缸下降 |
| `i_b阻挡上升` | `i_bLx_BlockUp` | BOOL[4] | 手动-阻挡气缸上升 |
| `i_b分料推出` | `i_bLx_SeparatePush` | BOOL[4] | 手动-分料气缸推出 |
| `i_b分料复位` | `i_bLx_SeparateReset` | BOOL[4] | 手动-分料气缸复位 |
| `i_b输送正转` | `i_bLx_ConveyorFwd` | BOOL[4] | 手动-输送带正转 |
| `i_b输送反转` | `i_bLx_ConveyorRev` | BOOL[4] | 手动-输送带反转 |
| `i_b分料前感应器` | `i_bPreSeparateSensor` | BOOL[4] | 分料前传感器 |
| `i_b到位感应器1` | `i_bPositionSensor1` | BOOL[4] | 到位感应器1 |
| `i_b到位感应器2` | `i_bPositionSensor2` | BOOL[4] | 到位感应器2 |
| `i_b阻挡气缸上位` | `i_bBlockCylinderUp` | BOOL[4] | 阻挡气缸升起位置 |
| `i_b阻挡气缸下位` | `i_bBlockCylinderDown` | BOOL[4] | 阻挡气缸下降位置 |
| `i_b分料气缸上位` | `i_bSeparateCylinderUp` | BOOL[4] | 分料气缸收回位置 |
| `i_b分料气缸下位` | `i_bSeparateCylinderDown` | BOOL[4] | 分料气缸推出位置 |
| `i_b取放料完成` | `i_bFeedComplete` | BOOL[4] | 取放料完成反馈 |
| `o_b阻挡电磁阀` | `o_bBlockSolenoid` | BOOL[4] | 阻挡电磁阀输出 |
| `o_b分料电磁阀` | `o_bSeparateSolenoid` | BOOL[4] | 分料电磁阀输出 |
| `o_b输送带正转` | `o_bConveyorFwd` | BOOL[4] | 输送带正转输出 |
| `o_b输送带慢速` | `o_bConveyorSlow` | BOOL[4] | 输送带慢速输出 |
| `o_b输送带反转` | `o_bConveyorRev` | BOOL[4] | 输送带反转输出 |
| `o_b放料完成` | `o_bFeedComplete` | BOOL[4] | 放料完成信号输出 |
| `o_b运行中` | `o_bRunning` | BOOL | 运行状态输出 |
| `o_b故障` | `o_bFault` | BOOL | 故障标志输出 |
| `o_i当前状态` | `o_iCurrentState` | INT | 当前状态码输出 |
| `o_Lx当前步序` | `o_LxCurrentStep` | INT[4] | 各层当前步序 |
| `o_i本站报警代码` | `o_iAlarmCode` | INT | 报警代码输出 |

#### 3.1.3 外部设备交互信号

| 中文变量名 | 英文变量名（新） | 类型 | 说明 |
|-----------|-----------------|------|------|
| `i_b组框机_自动中` | `i_bFrameMachine_AutoRunning` | BOOL | 组框机自动运行中 |
| `i_b组框机_允许送料` | `i_bFrameMachine_AllowFeed` | BOOL | 组框机允许送料 |
| `i_b组框机_有料请求` | `i_bFrameMaterialRequest` | BOOL | 组框机有料请求 |
| `i_b组框机_开门请求` | `i_bDoorOpenRequest` | BOOL | 开门请求 |
| `i_b组框机_急停` | `i_bFrameMachine_EStop` | BOOL | 组框机急停 |
| `i_b组框机_安全异常` | `i_bFrameMachine_SafetyErr` | BOOL | 组框机安全异常 |
| `i_b组框机_通讯异常` | `i_bFrameMachine_CommErr` | BOOL | 组框机通讯异常 |
| `i_b打胶机_自动中` | `i_bGlueMachine_AutoRunning` | BOOL | 打胶机自动运行中 |
| `i_b打胶机_允许送料` | `i_bGlueMachine_AllowFeed` | BOOL | 打胶机允许送料 |
| `i_b打胶机_取料完成` | `i_bGlueMachine_PickComplete` | BOOL | 打胶机取料完成 |
| `i_b打胶机_故障` | `i_bGlueMachine_Fault` | BOOL | 打胶机故障 |
| `i_b打胶机_急停` | `i_bGlueMachine_EStop` | BOOL | 打胶机急停 |
| `i_b打胶机_通讯异常` | `i_bGlueMachine_CommErr` | BOOL | 打胶机通讯异常 |
| `i_b机器人_自动中` | `i_bRobot_AutoRunning` | BOOL | 机器人自动运行中 |
| `i_b机器人_码料完成` | `i_bRobot_StackComplete` | BOOL | 机器人码料完成 |
| `i_b机器人_故障` | `i_bRobot_Fault` | BOOL | 机器人故障 |
| `i_b机器人_急停` | `i_bRobot_EStop` | BOOL | 机器人急停 |
| `i_b机器人_通讯异常` | `i_bRobot_CommErr` | BOOL | 机器人通讯异常 |
| `q_b组框机_请求送料` | `q_bFrameMachine_RequestFeed` | BOOL | 请求送料信号 |
| `q_b组框机_暂停` | `q_bFrameMachine_Pause` | BOOL | 暂停信号 |
| `q_b申请开门` | `q_bDoorOpenRequest` | BOOL | 申请开门 |
| `q_b组框机_就绪` | `q_bFrameMachine_Ready` | BOOL | 组框机就绪 |
| `q_b打胶机_请求运行` | `q_bGlueMachine_RequestRun` | BOOL | 请求运行信号 |
| `q_b允许抓料` | `q_bAllowPickup` | BOOL | 允许抓料信号 |
| `q_b安全区信号` | `q_bSafetyZoneSignal` | BOOL | 安全区信号 |
| `q_b打胶机_复位请求` | `q_bGlueMachine_ResetReq` | BOOL | 复位请求信号 |
| `q_b机器人_允许码料` | `q_bRobot_AllowStacking` | BOOL | 允许码料信号 |
| `q_b机器人_停止码料` | `q_bRobot_StopStacking` | BOOL | 停止码料信号 |
| `q_b机器人_复位请求` | `q_bRobot_ResetReq` | BOOL | 复位请求信号 |
| `q_b组框机紧急停止` | `q_bFrameMachine_EmergencyStop` | BOOL | 紧急停止信号 |
| `q_b外部设备故障` | `q_bExternalDeviceFault` | BOOL | 外部设备故障标志 |
| `q_i外部设备报警汇总` | `q_iExternalDeviceAlarmSummary` | INT | 外部设备报警汇总 |
| `q_b系统安全条件满足` | `q_bSystemSafetyConditionMet` | BOOL | 系统安全条件满足 |
| `i_b本机就绪` | `i_bLocalReady` | BOOL | 本机就绪信号 |
| `i_b任何报警激活` | `i_bAnyAlarmActive` | BOOL | 任何报警激活 |
| `i_b系统故障` | `i_bSystemFault` | BOOL | 系统故障标志 |

#### 3.1.4 取放料机构信号

| 中文变量名 | 英文变量名（新） | 类型 | 说明 |
|-----------|-----------------|------|------|
| `i_bZ轴点动上` | `i_bLx_ZAxis_JogUp` | BOOL | Z轴点动上升 |
| `i_bZ轴点动下` | `i_bLx_ZAxis_JogDown` | BOOL | Z轴点动下降 |
| `i_bX1轴点动前` | `i_bLx_X1Axis_JogFwd` | BOOL | X1轴点动前进 |
| `i_bX1轴点动后` | `i_bLx_X1Axis_JogRev` | BOOL | X1轴点动后退 |
| `i_b升降上升` | `i_bLx_LiftUp` | BOOL | 升降机构上升 |
| `i_b升降下降` | `i_bLx_LiftDown` | BOOL | 升降机构下降 |
| `i_b前夹紧夹紧` | `i_bLx_FrontGrip_Close` | BOOL | 前夹紧夹紧 |
| `i_b前夹紧松开` | `i_bLx_FrontGrip_Open` | BOOL | 前夹紧松开 |
| `i_b后夹紧夹紧` | `i_bLx_RearGrip_Close` | BOOL | 后夹紧夹紧 |
| `i_b后夹紧松开` | `i_bLx_RearGrip_Open` | BOOL | 后夹紧松开 |
| `i_b前夹紧2夹紧` | `i_bLx_FrontGrip2_Close` | BOOL | 前夹紧2夹紧 |
| `i_b前夹紧2松开` | `i_bLx_FrontGrip2_Open` | BOOL | 前夹紧2松开 |

#### 3.1.5 内部辅助变量

| 中文变量名 | 英文变量名（新） | 类型 | 说明 |
|-----------|-----------------|------|------|
| `s_i活跃报警` | `s_iActiveAlarmCode` | INT | 当前最高优先级报警代码(临时计算用) |
| `s_iLayerIdx` | `s_iLayerIndex` | INT | FOR循环索引(层号1-4) |

---

## 4. 重写实施方案

### 4.1 实施阶段划分

#### **阶段1：修复FB_1001遗留问题** ⏱️ 预计15分钟
- [ ] 替换`s_i活跃报警` → `s_iActiveAlarmCode`（10处）
- [ ] 验证FB_1001编译通过
- [ ] 更新FB_1001版本号至V4.3.0

#### **阶段2：重写GlobalVars.db数据块** ⏱️ 预计30分钟
- [ ] 复制GlobalVars.db为GlobalVars_V5.0.0.db（备份）
- [ ] 按照映射表替换所有中文变量名（~220处）
- [ ] 保持STRUCT结构和注释格式不变
- [ ] 更新文件头版本信息至V5.0.0
- [ ] 验证语法正确性

#### **阶段3：重写OB1主程序** ⏱️ 预计45分钟
- [ ] 复制OB1.scl为OB1_V4.3.0.scl（备份）
- [ ] 按照映射表替换所有中文变量名（254处）
- [ ] 重点检查6个功能块的实例化调用：
  - FB_ExternalDeviceInteraction（27输入/20输出）
  - FB_1001_Conveyor4Layer（24输入/14输出）
  - FB_1003_PickPlace（55输入/30输出）
  - FB_1004_GlueMachineFeeder（17输入/14输出）
  - FB_2001_CommonAlarm（4输入/16输出）
- [ ] 更新文件头版本信息至V5.0.0
- [ ] 验证完整编译通过

#### **阶段4：文档同步更新** ⏱️ 预计60分钟
- [ ] 更新程序架构文档_ARC-DJ-2026-005至V5.0.0
- [ ] 更新PLC变量定义文档_VAR-DJ-2026-005至V5.0.0
- [ ] 更新各FB的接口文档（IFC-FB1001/1003/1004等）
- [ ] 更新各FB的使用说明文档（UM-FB1001/1003/1004等）
- [ ] 更新各FB的变更记录文档（CHG-FB1001/1003/1004等）
- [ ] 创建本次重写的专项变更记录_CHG-V5.0.0-Rewrite.md

#### **阶段5：集成测试验证** ⏱️ 预计30分钟
- [ ] VS Code PLC调试器加载测试
- [ ] 功能块实例化验证
- [ ] 变量交叉引用检查
- [ ] 编译错误清零确认
- [ ] 用户验收测试（UAT）

### 4.2 文件修改清单

| 序号 | 文件路径 | 操作 | 变更内容 |
|------|---------|------|----------|
| 01 | `conveyor/FB_1001_Conveyor4Layer_BufferFraming.scl` | 修改 | 替换10处`s_i活跃报警`→`s_iActiveAlarmCode` |
| 02 | `DB1/GlobalVars.db` | 重写 | 全部变量名英文化(~220处) |
| 03 | `OB1/OB1.scl` | 重写 | 全部变量名英文化(254处) |
| 04 | `程序架构文档_ARC-DJ-2026-005-V4.2.0.md` | 更新 | 升级至V5.0.0，反映新命名体系 |
| 05 | `PLC变量定义文档_VAR-DJ-2026-005-V4.2.0.md` | 更新 | 升级至V5.0.0，更新所有变量表 |
| 06 | `conveyor/接口文档_IFC-FB1001-Conveyor4Layer.md` | 更新 | 同步新变量名 |
| 07 | `conveyor/使用说明_UM-FB1001-Conveyor4Layer.md` | 更新 | 示例代码更新 |
| 08 | `conveyor/变更记录_CHG-FB1001-Conveyor4Layer.md` | 新增 | V4.3.0 + V5.0.0变更记录 |
| 09 | `pickplace/接口文档_IFC-FB1003-PickPlace.md` | 更新 | 如果OB1调用的变量名有变化 |
| 10 | `pickplace/使用说明_UM-FB1003-PickPlace.md` | 更新 | 示例代码更新 |
| 11 | `pickplace/变更记录_CHG-FB1003-PickPlace.md` | 新增 | V5.0.0变更记录 |
| 12 | `feeder/接口文档_IFC-FB1004-GlueMachineFeeder.md` | 更新 | 如果OB1调用的变量名有变化 |
| 13 | `feeder/使用说明_UM-FB1004-GlueMachineFeeder.md` | 更新 | 示例代码更新 |
| 14 | `feeder/变更记录_CHG-FB1004-GlueMachineFeeder.md` | 新增 | V5.0.0变更记录 |
| 15 | `external/接口文档_IFC-FB-ExternalDeviceInteraction.md` | 更新 | 大量变量名变化 |
| 16 | `external/使用说明_UM-FB-ExternalDeviceInteraction.md` | 更新 | 示例代码更新 |
| 17 | `external/变更记录_CHG-FB-ExternalDeviceInteraction.md` | 新增 | V5.0.0变更记录 |
| 18 | `common/变更记录_CHG-FB2001-CommonAlarm.md` | 新增 | V5.0.0变更记录（如有影响） |
| 19 | **新建** `变更记录_CHG-V5.0.0-Rewrite.md` | 新建 | 本次全面重写的总变更记录 |

---

## 5. 质量保证措施

### 5.1 编译验证清单

每个阶段完成后必须执行：

```powershell
# PowerShell验证脚本概念
# 1. 检查是否还有残留的中文变量名（排除注释）
Select-String -Path "*.scl","*.db" -Pattern '[\u4e00-\u9fa5]' |
  Where-Object { $_.Line -match '^\s*(VAR|i_|q_|o_|s_)\s' } |
  Select-Object Path, LineNumber, Line

# 预期结果：0匹配（所有代码中的中文变量名已清除）
```

### 5.2 交叉引用检查

- [ ] GlobalVars.db的所有变量在OB1中有引用
- [ ] OB1中引用的所有变量在GlobalVars.db中有定义
- [ ] OB1传给FB的参数名与FB的VAR_INPUT完全匹配
- [ ] FB返回给OB1的参数名与FB的VAR_OUTPUT完全匹配

### 5.3 回滚预案

如果V5.0.0出现严重问题：
1. 立即停止部署
2. 恢复备份文件（OB1_V4.3.0.scl, GlobalVars_V4.3.0.db）
3. 回退文档至V4.3.0版本
4. 分析问题根因并修订方案

---

## 6. 风险评估与缓解

| 风险项 | 可能性 | 影响程度 | 缓解措施 |
|--------|-------|---------|----------|
| 遗漏某些变量名未替换 | 中 | 高 | 使用正则表达式批量扫描+人工复核 |
| 注释与代码不一致 | 低 | 中 | 只改代码变量名，注释保持中文（符合规范） |
| 文档更新滞后 | 中 | 低 | 采用"文档先行"策略，边改代码边更新 |
| 编译器兼容性问题 | 低 | 高 | 在VS Code PLC调试器中实时验证 |
| 业务逻辑意外改变 | 极低 | 极高 | 严格遵循"只改名不改逻辑"原则 |

---

## 7. 成功标准

### 7.1 技术指标

- ✅ **零编译错误**：TC001/TC002/TC003等声明类错误数为0
- ✅ **零中文变量名**：代码中无任何中文标识符（注释除外）
- ✅ **100%规范符合**：所有变量名符合801规范V1.0.5
- ✅ **文档完整性**：所有19个文件全部更新至V5.0.0

### 7.2 质量指标

- ✅ **可读性提升**：变量名自解释，减少注释依赖
- ✅ **维护性提升**：IDE自动补全、重构工具正常工作
- ✅ **国际化支持**：纯英文标识符，无编码问题

---

## 8. 时间估算汇总

| 阶段 | 工作内容 | 预计时间 | 累计时间 |
|------|---------|---------|---------|
| 1 | 修复FB_1001遗留问题 | 15分钟 | 15分钟 |
| 2 | 重写GlobalVars.db | 30分钟 | 45分钟 |
| 3 | 重写OB1主程序 | 45分钟 | 1.5小时 |
| 4 | 文档同步更新 | 60分钟 | 2.5小时 |
| 5 | 集成测试验证 | 30分钟 | **3小时** |
| **Buffer** | 问题处理缓冲 | 30分钟 | **3.5小时** |
| **总计** | | | **约3.5小时** |

---

## 9. 批准事项

请审阅以上方案，确认以下关键决策：

- [ ] **确认重写范围**：19个文件，484处变量名替换
- [ ] **确认命名体系**：采用上述3.1节的映射表
- [ ] **确认实施顺序**：按照4.1节的5个阶段执行
- [ ] **同意开始执行**：批准后立即启动阶段1

---

## 附录A：快速参考 - 常用前缀速查

| 前缀 | 含义 | 适用范围 | 示例 |
|------|------|---------|------|
| `i_` | Input | VAR_INPUT | `i_bEnable` |
| `q_` / `o_` | Output | VAR_OUTPUT | `q_bMotorRun`, `o_bFault` |
| `i_bLx_` | Logic auxiliary input | HMI缓存的手动操作变量 | `i_bLx_BlockDown` |
| `s_` | Static/Internal | VAR（内部变量） | `s_iActiveAlarmCode` |
| `fb` | Function Block instance | FB实例名 | `fbLayer1`, `fbAlarm` |

## 附录B：命名转换工具（可选）

如需自动化批量替换，可使用以下PowerShell脚本框架：

```powershell
# 变量名映射表（CSV格式）
$mapping = @(
    @{Old='i_b使能';             New='i_bEnable'},
    @{Old='i_b自动模式';          New='i_bAutoMode'},
    # ... 完整映射表见3.1节
)

# 执行替换
foreach ($item in $mapping) {
    $content = Get-Content 'OB1.scl' -Raw -Encoding UTF8
    $content = $content.Replace($item.Old, $item.New)
    Set-Content 'OB1.scl' -Value $content -Encoding UTF8NoBOM
}
```

---

**文档结束**

*下次更新：用户批准后进入实施阶段*
