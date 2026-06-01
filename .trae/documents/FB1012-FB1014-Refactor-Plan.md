# 重构计划: FB\_1012注释修复 + FB\_1014系统性重构

## 0. 问题诊断

### 0.1 FB\_1012\_ConveyorMotor - 注释规范违规

**违规项**: LSP-904 V1.2.0 §2.0 注释类型分工规则

| 位置                 | 当前写法                                                         | 应改为             | 规则依据            |
| ------------------ | ------------------------------------------------------------ | --------------- | --------------- |
| VAR\_INPUT 变量行内注释  | `(* 正转命令 *)`                                                 | `// 正转命令`       | 变量/行内用 `//`     |
| VAR\_OUTPUT 变量行内注释 | `(* 正转输出(经互锁后) *)`                                           | `// 正转输出(经互锁后)` | 变量/行内用 `//`     |
| 逻辑分支说明             | `(* ==================== VFD故障检测... ==================== *)` | 保持 `(* *)`      | 逻辑/流程块用 `(* *)` |

**结论**: FB\_1012的头部注释和逻辑块注释合规, 但**所有变量行内注释**使用了 `(* *)` 而非 `//`, 需全部修正.

### 0.2 FB\_1014\_StationConveyor - 系统性缺陷(5类)

#### 缺陷1: 引用已删除的ST\_Cylinder结构体 (致命BUG)

FB\_1014 V4.3.0 使用 `io_stInfeedCyl : ST_Cylinder` 等 VAR\_IN\_OUT, 但:

* FB\_1011 V9.0.0 已移除 ST\_Cylinder, 回归扁平 VAR\_INPUT/OUTPUT

* ST\_Cylinder.scl 文件已不存在

* FB\_1014 的调用方式 `fbInfeedCyl(io_stCyl := io_stInfeedCyl)` 是旧接口, 与 V9.0.0 不兼容

**影响**: FB\_1014 当前代码无法编译通过, 是致命级BUG.

#### 缺陷2: 未复用FB\_1012\_ConveyorMotor (违反高内聚低耦合)

FB\_1014 直接输出裸BOOL电机命令 `q_yFwdCmd/q_yRevCmd/q_ySlowCmd`, 但:

* FB\_1012 已封装方向互斥 + VFD故障检测 + 慢速修饰

* FB\_1014 自己在状态机中手动管理方向互斥, 重复造轮子

* IFC文档 §6 组件复用审查明确写了 "电机控制 | FB\_1012 | 未复用(V4.3.0暂不引入)" - 这是技术债

**影响**: 电机控制无VFD故障检测, 方向互斥逻辑分散在状态机各处, 违反DRY原则.

#### 缺陷3: 气缸控制使用旧接口 (与FB\_1011 V9.0.0不兼容)

FB\_1014 使用 FB\_1011 的旧接口:

```
fbInfeedCyl(io_stCyl := io_stInfeedCyl);  // 旧接口: VAR_IN_OUT ST_Cylinder
```

FB\_1011 V9.0.0 新接口:

```
fbInfeedCyl(
    i_bExtend := ..., i_bRetract := ...,
    i_bExtendedPos := ..., i_bRetractedPos := ...,
    i_iTimeoutMs := ..., i_iDebounceMs := ...,
    i_bExtendPolarity := ...
);
```

**影响**: 编译失败 + 丢失FB\_1011 V9.0.0新增的传感器消抖功能.

#### 缺陷4: 拍正气缸电磁阀手动取反 (FB\_1011已内置极性取反)

FB\_1014 当前代码:

```
q_yAlignSolenoid := NOT fbAlignCyl.q_bSolenoid;  // 手动取反
```

FB\_1011 V9.0.0 已内置 `i_bExtendPolarity` 参数, 设为TRUE时自动处理:

* 电磁阀输出反转

* 传感器映射互换

* 状态输出随极性反转

**影响**: 手动取反是冗余逻辑, 且只反转了电磁阀输出, 未反转传感器映射, 导致状态判断可能错误.

#### 缺陷5: 文档与代码不一致

| 文档         | 问题                                                      |
| ---------- | ------------------------------------------------------- |
| PRD V4.3.0 | 引用ST\_Cylinder(已删除); 关联PFL写V4.2.0但实际文件是V4.3.0           |
| IFC V4.3.0 | §3.4 定义VAR\_IN\_OUT ST\_Cylinder(已删除); §6 承认未复用FB\_1012 |
| DSN V4.3.0 | §4.1 伪代码使用旧接口; §7.4 定义VAR\_IN\_OUT ST\_Cylinder(已删除)    |
| PFL V4.3.0 | 引用FB\_1012 V8.0.0(实际已V9.0.0); 引用ST\_Cylinder(已删除)       |

### 0.3 根因分析

**核心根因**: FB\_1011/FB\_1012 升级到 V9.0.0 (Breaking Change: 移除ST\_Cylinder, 回归扁平接口) 时, FB\_1014 未同步更新. 这是pm-workflow的依赖链管理缺失 - 下游组件未跟随上游Breaking Change升级.

***

## 1. 重构方案

### 1.1 FB\_1012 注释修复 (独立任务, 不影响接口)

将所有变量行内注释从 `(* *)` 改为 `//`, 逻辑块注释保持 `(* *)`.

### 1.2 FB\_1014 重构为 V5.0.0 (Breaking Change)

#### 1.2.1 接口重构原则

| 原则     | 说明                                               |
| ------ | ------------------------------------------------ |
| 扁平接口   | 不使用结构体封装, 与FB\_1011/FB\_1012 V9.0.0风格一致          |
| 组件复用   | 气缸用FB\_1011, 电机用FB\_1012, 消除重复造轮子                |
| 高内聚低耦合 | FB\_1014是编排器, 只负责状态机逻辑, 执行细节委托给FB\_1011/FB\_1012 |
| 文档先行   | 先更新4份文档, 再改代码                                    |

#### 1.2.2 新接口设计 (V5.0.0)

**移除项**:

* `VAR_IN_OUT io_stInfeedCyl/io_stAlignCyl/io_stDischargeCyl : ST_Cylinder` (结构体已删除)

* `q_yFwdCmd/q_yRevCmd/q_ySlowCmd` (改用FB\_1012输出)

**新增项 - 气缸传感器输入 (替代ST\_Cylinder)**:

| 新增输入                | 类型   | 默认值   | 说明           |
| ------------------- | ---- | ----- | ------------ |
| i\_bInfeedExtPos    | BOOL | FALSE | A侧阻挡气缸伸出位传感器 |
| i\_bInfeedRetPos    | BOOL | FALSE | A侧阻挡气缸收回位传感器 |
| i\_bAlignExtPos     | BOOL | FALSE | 拍正气缸伸出位传感器   |
| i\_bAlignRetPos     | BOOL | FALSE | 拍正气缸收回位传感器   |
| i\_bDischargeExtPos | BOOL | FALSE | B侧出料气缸伸出位传感器 |
| i\_bDischargeRetPos | BOOL | FALSE | B侧出料气缸收回位传感器 |

**新增项 - 气缸配置参数**:

| 新增输入                   | 类型  | 默认值  | 说明            |
| ---------------------- | --- | ---- | ------------- |
| i\_iInfeedTimeoutMs    | INT | 5000 | A侧阻挡气缸超时(ms)  |
| i\_iAlignTimeoutMs     | INT | 5000 | 拍正气缸超时(ms)    |
| i\_iDischargeTimeoutMs | INT | 5000 | B侧出料气缸超时(ms)  |
| i\_iCylDebounceMs      | INT | 0    | 气缸传感器消抖(扫描周期) |

**新增项 - VFD故障输入 (FB\_1012需要)**:

| 新增输入         | 类型   | 默认值   | 说明      |
| ------------ | ---- | ----- | ------- |
| i\_bVfdFault | BOOL | FALSE | 变频器故障信号 |

**变更项 - 电机输出 (改用FB\_1012输出)**:

| 旧输出         | 新输出              | 说明                |
| ----------- | ---------------- | ----------------- |
| q\_yFwdCmd  | q\_bFwdOut       | 经FB\_1012互锁后的正转输出 |
| q\_yRevCmd  | q\_bRevOut       | 经FB\_1012互锁后的反转输出 |
| q\_ySlowCmd | q\_bSlowOut      | 经FB\_1012互锁后的慢速输出 |
| (无)         | q\_bMotorRunning | 电机运行中(FB\_1012)   |
| (无)         | q\_bVfdAlarm     | VFD报警(FB\_1012)   |

**新增项 - 气缸诊断输出 (FB\_1011透传)**:

| 新增输出                    | 类型   | 说明          |
| ----------------------- | ---- | ----------- |
| q\_bInfeedCylTimeout    | BOOL | A侧阻挡气缸超时    |
| q\_bInfeedCylFault      | BOOL | A侧阻挡气缸传感器冲突 |
| q\_bAlignCylTimeout     | BOOL | 拍正气缸超时      |
| q\_bAlignCylFault       | BOOL | 拍正气缸传感器冲突   |
| q\_bDischargeCylTimeout | BOOL | B侧出料气缸超时    |
| q\_bDischargeCylFault   | BOOL | B侧出料气缸传感器冲突 |

**新增项 - 气缸到位输出 (FB\_1011透传)**:

| 新增输出                     | 类型   | 说明          |
| ------------------------ | ---- | ----------- |
| q\_bInfeedIsExtended     | BOOL | A侧阻挡气缸已伸出   |
| q\_bInfeedIsRetracted    | BOOL | A侧阻挡气缸已收回   |
| q\_bAlignIsExtended      | BOOL | 拍正气缸已伸出(逻辑) |
| q\_bAlignIsRetracted     | BOOL | 拍正气缸已收回(逻辑) |
| q\_bDischargeIsExtended  | BOOL | B侧出料气缸已伸出   |
| q\_bDischargeIsRetracted | BOOL | B侧出料气缸已收回   |

#### 1.2.3 内部实现变更

**FB\_1011 实例化 (V9.0.0 新接口)**:

```
// A侧阻挡气缸 (正常极性)
fbInfeedCyl(
    i_bExtend := m_bInfeedExtendCmd,
    i_bRetract := m_bInfeedRetractCmd,
    i_bExtendedPos := i_bInfeedExtPos,
    i_bRetractedPos := i_bInfeedRetPos,
    i_iTimeoutMs := i_iInfeedTimeoutMs,
    i_iDebounceMs := i_iCylDebounceMs,
    i_bExtendPolarity := FALSE
);
q_yInfeedSolenoid := fbInfeedCyl.q_bSolenoid;
q_bInfeedIsExtended := fbInfeedCyl.q_bIsExtended;
q_bInfeedIsRetracted := fbInfeedCyl.q_bIsRetracted;
q_bInfeedCylTimeout := fbInfeedCyl.q_bTimeout;
q_bInfeedCylFault := fbInfeedCyl.q_bSensorFault;

// 拍正气缸 (极性取反 - FB_1011内置处理, 无需手动NOT)
fbAlignCyl(
    i_bExtend := m_bAlignExtendCmd,
    i_bRetract := m_bAlignRetractCmd,
    i_bExtendedPos := i_bAlignExtPos,
    i_bRetractedPos := i_bAlignRetPos,
    i_iTimeoutMs := i_iAlignTimeoutMs,
    i_iDebounceMs := i_iCylDebounceMs,
    i_bExtendPolarity := TRUE   // 弹簧复位型, 内置极性取反
);
q_yAlignSolenoid := fbAlignCyl.q_bSolenoid;  // 无需NOT, FB_1011已处理
q_bAlignIsExtended := fbAlignCyl.q_bIsExtended;
q_bAlignIsRetracted := fbAlignCyl.q_bIsRetracted;
q_bAlignCylTimeout := fbAlignCyl.q_bTimeout;
q_bAlignCylFault := fbAlignCyl.q_bSensorFault;

// B侧出料气缸 (正常极性)
fbDischargeCyl(
    i_bExtend := m_bDischargeExtendCmd,
    i_bRetract := m_bDischargeRetractCmd,
    i_bExtendedPos := i_bDischargeExtPos,
    i_bRetractedPos := i_bDischargeRetPos,
    i_iTimeoutMs := i_iDischargeTimeoutMs,
    i_iDebounceMs := i_iCylDebounceMs,
    i_bExtendPolarity := FALSE
);
q_yDischargeSolenoid := fbDischargeCyl.q_bSolenoid;
q_bDischargeIsExtended := fbDischargeCyl.q_bIsExtended;
q_bDischargeIsRetracted := fbDischargeCyl.q_bIsRetracted;
q_bDischargeCylTimeout := fbDischargeCyl.q_bTimeout;
q_bDischargeCylFault := fbDischargeCyl.q_bSensorFault;
```

**FB\_1012 实例化 (新增)**:

```
// 输送电机控制
fbConveyorMotor(
    i_bFwdCmd := m_bFwdCmd,
    i_bRevCmd := m_bRevCmd,
    i_bSlowCmd := m_bSlowCmd,
    i_bVfdFault := i_bVfdFault,
    i_iCtrlMode := 0,           // 端子控制
    i_rSpeed := 100.0
);
q_bFwdOut := fbConveyorMotor.q_bFwdOut;
q_bRevOut := fbConveyorMotor.q_bRevOut;
q_bSlowOut := fbConveyorMotor.q_bSlowOut;
q_bMotorRunning := fbConveyorMotor.q_bRunning;
q_bVfdAlarm := fbConveyorMotor.q_bVfdAlarm;
```

**状态机变更**:

* 气缸控制: `io_stInfeedCyl.Extend := TRUE` → `m_bInfeedExtendCmd := TRUE; m_bInfeedRetractCmd := FALSE`

* 气缸到位判断: `io_stAlignCyl.IsExtended` → `fbAlignCyl.q_bIsExtended`

* 电机控制: `q_yFwdCmd := TRUE` → `m_bFwdCmd := TRUE`

* VFD故障: 自动由FB\_1012处理, 状态机无需额外逻辑

***

## 2. 执行步骤

### Phase 1: FB\_1012 注释修复 (独立, 可先行)

| 步骤  | 操作                                | 文件                          |
| --- | --------------------------------- | --------------------------- |
| 1.1 | VAR\_INPUT 变量行内注释 `(* *)` → `//`  | FB\_1012\_ConveyorMotor.scl |
| 1.2 | VAR\_OUTPUT 变量行内注释 `(* *)` → `//` | FB\_1012\_ConveyorMotor.scl |
| 1.3 | 逻辑块注释保持 `(* *)` 不变                | (无需修改)                      |

### Phase 2: FB\_1014 文档重构 (文档先行!)

按顺序更新4份文档, 版本号统一升级为 V5.0.0:

| 步骤  | 操作     | 文件                                                | 关键变更点                                                          |
| --- | ------ | ------------------------------------------------- | -------------------------------------------------------------- |
| 2.1 | 更新需求文档 | PRD/需求文档\_PRD-FB1014-StationConveyor-V5.0.0.md    | 移除ST\_Cylinder引用; 新增气缸传感器/配置/VFD故障需求; 新增FB\_1012复用需求; 更新接口需求汇总 |
| 2.2 | 更新接口文档 | PRD/接口文档\_IFC-FB1014-StationConveyor-V5.0.0.md    | 移除VAR\_IN\_OUT; 新增气缸传感器/配置输入; 电机输出改用FB\_1012; 新增诊断输出; 更新组件复用审查 |
| 2.3 | 更新详细设计 | PRD/详细设计说明书\_DSN-FB1014-StationConveyor-V5.0.0.md | FB\_1011新接口伪代码; FB\_1012实例化伪代码; 状态机变量改为内部命令; 移除手动NOT取反         |
| 2.4 | 更新工艺流程 | PRD/工艺流程\_PFL-FB1014-StationConveyor-V5.0.0.md    | 更新组件引用版本; 移除ST\_Cylinder; 气缸到位判断改为FB\_1011输出                   |

### Phase 3: FB\_1014 代码实现

| 步骤  | 操作            | 说明                                                                                                                                  |
| --- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 3.1 | 重写VAR\_INPUT  | 移除VAR\_IN\_OUT, 新增气缸传感器/配置/VFD输入                                                                                                    |
| 3.2 | 重写VAR\_OUTPUT | 电机输出改FB\_1012风格, 新增气缸诊断/到位输出                                                                                                        |
| 3.3 | 重写VAR         | FB\_1011新接口实例变量; 新增FB\_1012实例; 气缸命令中间变量                                                                                             |
| 3.4 | 重写FB\_1011调用  | 使用V9.0.0扁平接口, 拍正气缸用i\_bExtendPolarity=TRUE                                                                                          |
| 3.5 | 新增FB\_1012调用  | 实例化FB\_1012, 状态机通过中间变量控制                                                                                                            |
| 3.6 | 重写状态机         | io\_stXxx.Extend/Retract → m\_bXxxExtendCmd/m\_bXxxRetractCmd; io\_stXxx.IsExtended → fbXxx.q\_bIsExtended; q\_yFwdCmd → m\_bFwdCmd |
| 3.7 | 注释合规          | 全部变量行内用 `//`, 逻辑块用 `(* *)`, 英文半角标点                                                                                                  |

### Phase 4: 验证

| 步骤  | 操作                                   |
| --- | ------------------------------------ |
| 4.1 | FB\_1012: 逐行检查注释格式是否符合LSP-904 V1.2.0 |
| 4.2 | FB\_1014: 检查注释格式是否符合LSP-904 V1.2.0   |
| 4.3 | FB\_1014: 接口定义与IFC文档逐项对照             |
| 4.4 | FB\_1014: 状态机逻辑与DSN伪代码逐行对照           |
| 4.5 | FB\_1014: 气缸动作与PFL工艺表逐项对照            |
| 4.6 | 检查无ST\_Cylinder残留引用                  |
| 4.7 | 检查无手动NOT取反(拍正气缸由FB\_1011极性参数处理)      |

***

## 3. V5.0.0 接口统计对比

| 项目                  | V4.3.0 | V5.0.0 |             变化             |
| ------------------- | :----: | :----: | :------------------------: |
| VAR\_INPUT (控制)     |    8   |    8   |             不变             |
| VAR\_INPUT (参数-延时)  |    4   |    4   |             不变             |
| VAR\_INPUT (参数-气缸)  |    0   |    4   |          +4(超时+消抖)         |
| VAR\_INPUT (传感器-输送) |    3   |    3   |             不变             |
| VAR\_INPUT (传感器-气缸) |    0   |    6   |         +6(3气缸x2位)         |
| VAR\_INPUT (VFD)    |    0   |    1   |             +1             |
| VAR\_IN\_OUT (气缸)   |    3   |    0   |     -3(移除ST\_Cylinder)     |
| VAR\_OUTPUT (电磁阀)   |    3   |    3   |             不变             |
| VAR\_OUTPUT (电机)    |    3   |    5   |  +2(Running+VfdAlarm), 重命名 |
| VAR\_OUTPUT (握手)    |    2   |    2   |             不变             |
| VAR\_OUTPUT (诊断-状态) |    4   |    4   |             不变             |
| VAR\_OUTPUT (诊断-气缸) |    0   |   10   | +10(3气缸x2诊断+3气缸x2到位+1对齐到位) |
| **总计**              | **30** | **50** |           **+20**          |

接口数量增加主要来自: 气缸传感器扁平化(+6), 气缸配置(+4), 气缸诊断输出(+10), VFD(+1), 电机诊断(+2), 移除VAR\_IN\_OUT(-3). 这是扁平接口的正常代价, 换来了编译可通+组件复用+规范合规.

***

## 4. 风险与注意事项

| 风险                   | 缓解措施                                                       |
| -------------------- | ---------------------------------------------------------- |
| Breaking Change影响调用方 | V5.0.0版本号明确标记, OB1调用需同步更新                                  |
| 接口膨胀(50个信号)          | 扁平接口是FB\_1011/FB\_1012 V9.0.0的设计哲学, 保持一致性                  |
| 拍正气缸极性取反行为变化         | FB\_1011 i\_bExtendPolarity=TRUE自动处理, 无需手动NOT, 但需验证传感器映射正确 |
| 文档-代码同步              | 严格按文档先行流程, 代码实现必须与文档一致                                     |

