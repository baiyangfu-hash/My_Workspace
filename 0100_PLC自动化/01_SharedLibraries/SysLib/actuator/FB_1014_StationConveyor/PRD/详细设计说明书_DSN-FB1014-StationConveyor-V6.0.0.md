---
spec_id: DSN-FB1014
version: V6.0.0
domain: plc
lifecycle: in_progress
---

# 详细设计说明书 FB_1014_StationConveyor

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1014 工站输送机详细设计 |
| **文档版本** | V6.0.0 |
| **关联源码** | actuator/FB_1014_StationConveyor.scl |
| **关联IFC** | 接口文档_IFC-FB1014-StationConveyor-V6.0.0.md |
| **编制日期** | 2026-05-31 |
| **编制人** | Trae |
| **遵循规范** | LSP-905 V1.0.2, LSP-904 V1.2.0, LSP-903 V1.0.0, LSP-906 V1.0.0 |

### V6.0.0 变更摘要

V6.0.0引入多模式运行架构, 支持正常/双向模式切换, 并细化对齐和出料阶段的子步骤控制.

核心变更:
1. 新增运行模式接口 i_iMode (0=正常 / 1=B侧双向(默认) / 2=A侧双向)
2. 新增子步骤机变量 m_iAlignStep (拍正对齐子步骤) 和 m_iDischPrepStep (出料准备子步骤)
3. 新增常量 MODE_NORMAL(0) / MODE_B_DUAL(1) / MODE_A_DUAL(2)
4. ST_ALIGN 态重构为子步骤 CASE 结构: Mode=1 四步(M0伸出→M1延时→M2阻挡→M3收回), Mode=0/2 三步(M0伸出+延时→M1阻挡→M2收回)
5. ST_DISCHARGE 态 Mode=1 增加出料准备子步骤: 两步准备(启动+延时确认) + 一步出料
6. ST_PROCESSING 态气缸行为按 Mode 区分: Mode 0 全收回, Mode 1 B侧缸保持, Mode 2 A侧缸保持
7. 安全态(Stop/VFD报警/FAULT)拍正气缸改为伸出(原为收回)
8. 状态转换表体现 Mode 分支, 伪代码全部更新, 新增对齐时序图和出料准备时序图

### V5.0.0 -> V6.0.0 差异总表

| 维度 | V5.0.0 | V6.0.0 | 原因 |
|------|--------|--------|------|
| 运行模式 | 单一模式 | i_iMode 三模式(正常/B侧双向/A侧双向) | 支持双向工站布局 |
| 对齐控制 | 串行 IF 嵌套 | m_iAlignStep 子步骤 CASE | 模式差异化, 可扩展 |
| 出料控制 | 串行延时 | m_iDischPrepStep 子步骤 CASE (Mode=1) | 增加出料准备阶段 |
| 加工态气缸 | 全收回 | 按 Mode 保持对应侧气缸 | 为下一轮进料预置 |
| 安全态拍正 | 收回 | 伸出 | 机械安全屏障 |
| 子步骤变量 | 无 | m_iAlignStep, m_iDischPrepStep | 子步骤机状态保持 |
| 常量 | 无 MODE_xxx | MODE_NORMAL/B_DUAL/A_DUAL | 模式可读性 |

### V5.0.0 -> V6.0.0 接口映射

| V5.0.0 | V6.0.0 | 说明 |
|--------|--------|------|
| (无) | i_iMode : INT | 新增运行模式输入, 默认值 MODE_B_DUAL(1) |
| (无) | m_iAlignStep : INT | 新增对齐子步骤机, 默认值 0 |
| (无) | m_iDischPrepStep : INT | 新增出料准备子步骤机, 默认值 0 |
| (无) | MODE_NORMAL : INT = 0 | 新增常量 |
| (无) | MODE_B_DUAL : INT = 1 | 新增常量 |
| (无) | MODE_A_DUAL : INT = 2 | 新增常量 |
| ST_FAULT: q_bAlignRetract=TRUE | ST_FAULT: q_bAlignExtend=TRUE | 安全态拍正伸出 |

## 1. 设计原则

1. **单口双向**: 同一端口进出, 部件功能随方向切换
2. **反转进料**: 物料从出料口方向反转进入
3. **正转出料**: 物料从入料口方向正转离开
4. **功能切换**: 传感器和气缸功能在进料/出料时互换
5. **纯编排器**: FB_1014只输出命令和输入状态, 不含执行器实例(FB_1011/FB_1012在OB1)
6. **拍正对齐**: 入料后先拍正对齐, 再下降阻挡, 再收回拍正, 保证物料不位移
7. **状态反馈**: 气缸磁环信号通过i_bXxx输入, 非直接访问ST_Cylinder
8. **VFD联动**: VFD报警触发状态机安全响应, FB_1012已切断马达输出, FB_1014补充状态机侧处理
9. **多模式运行**: i_iMode 决定气缸行为、对齐子步骤数、出料准备流程
10. **子步骤控制**: m_iAlignStep/m_iDischPrepStep 实现状态内细粒度步骤编排
11. **安全态拍正伸出**: Stop/VFD报警/FAULT状态下拍正气缸伸出作为机械屏障

### 1.1 运行模式说明

| 模式 | 常量 | 值 | 说明 |
|------|------|---|------|
| 正常模式 | MODE_NORMAL | 0 | A侧入料口, B侧出料口, 标准流向 |
| B侧双向 | MODE_B_DUAL | 1 | B侧为双向端口(默认), 入料和出料均走B侧 |
| A侧双向 | MODE_A_DUAL | 2 | A侧为双向端口, 入料和出料均走A侧 |

## 2. 功能切换映射

### 2.1 Mode 0 (MODE_NORMAL): 正常模式

#### 2.1.1 入料时 (INFEED状态)

```
逻辑功能           FB_1014命令输出                      用途
-----------------------------------------------------------------------
入料检测光电1      i_xPos1                              物料进入时确认
入料检测光电2      i_xPos2                              精定位确认
入料气缸           q_bDischargeExtend=TRUE              放下允许物料进入
                   q_bDischargeRetract=FALSE
阻挡气缸           q_bInfeedRetract=TRUE                抬起阻挡
                   q_bInfeedExtend=FALSE
拍正气缸           q_bAlignExtend=TRUE                  保持默认(伸出)
                   q_bAlignRetract=FALSE
马达               q_bRevCmd=TRUE                       反转进料
```

#### 2.1.2 对齐时 (ALIGN状态)

```
逻辑功能           FB_1014命令输出                      用途
-----------------------------------------------------------------------
拍正气缸           q_bAlignExtend=TRUE                  伸出确认 -> 收回
                   q_bAlignRetract=FALSE
阻挡气缸下降       q_bInfeedExtend=TRUE                 下降压住物料
                   q_bInfeedRetract=FALSE
入料气缸保持       q_bDischargeExtend=TRUE              保持入料气缸功能
                   q_bDischargeRetract=FALSE
马达               q_bRevCmd=FALSE                      停止
```

#### 2.1.3 出料时 (DISCHARGE状态)

```
逻辑功能           FB_1014命令输出                      用途
-----------------------------------------------------------------------
出料检测光电1      i_xPos1                              物料离开时确认
出料检测光电2      i_xPos2                              离开确认
出料气缸           q_bInfeedExtend=TRUE                 放下允许物料出去
                   q_bInfeedRetract=FALSE
阻挡气缸           q_bDischargeRetract=TRUE             抬起阻挡
                   q_bDischargeExtend=FALSE
拍正气缸           q_bAlignRetract=TRUE                 保持收回
                   q_bAlignExtend=FALSE
马达               q_bFwdCmd=TRUE                       正转出料
```

### 2.2 Mode 1 (MODE_B_DUAL): B侧双向模式

#### 2.2.1 入料时 (INFEED状态)

```
逻辑功能           FB_1014命令输出                      用途
-----------------------------------------------------------------------
入料检测光电1      i_xPos1                              物料进入时确认
入料检测光电2      i_xPos2                              精定位确认
入料气缸(B侧)      q_bDischargeExtend=TRUE              放下允许物料从B侧进入
                   q_bDischargeRetract=FALSE
阻挡气缸(A侧)      q_bInfeedRetract=TRUE                抬起阻挡
                   q_bInfeedExtend=FALSE
拍正气缸           q_bAlignExtend=TRUE                  保持默认(伸出)
                   q_bAlignRetract=FALSE
马达               q_bRevCmd=TRUE                       反转进料
```

#### 2.2.2 对齐时 (ALIGN状态) — 四步子步骤

```
逻辑功能           FB_1014命令输出                      用途
-----------------------------------------------------------------------
m_iAlignStep=0     q_bAlignExtend=TRUE                  拍正伸出
                   q_bAlignRetract=FALSE
m_iAlignStep=1     q_bAlignExtend=TRUE                  对齐延时确认
                   启动对齐延时
m_iAlignStep=2     q_bInfeedExtend=TRUE                 阻挡下降压住物料
                   q_bInfeedRetract=FALSE
m_iAlignStep=3     q_bAlignExtend=FALSE                 拍正收回
                   q_bAlignRetract=TRUE
马达               q_bRevCmd=FALSE                      停止
```

#### 2.2.3 出料时 (DISCHARGE状态) — 准备+出料

```
逻辑功能           子步骤             FB_1014命令输出                  用途
-------------------------------------------------------------------------------
出料准备-启动       m_iDischPrepStep=0 q_bFwdCmd=TRUE                 正转出料
                                      q_bInfeedExtend=TRUE            放下出料气缸(B侧)
                                      q_bInfeedRetract=FALSE
                                      q_bDischargeExtend=FALSE        抬起阻挡(A侧)
                                      q_bDischargeRetract=TRUE
出料准备-延时确认   m_iDischPrepStep=1 启动准备延时                    物料开始移动确认
出料                m_iDischPrepStep=2 q_bFwdCmd=TRUE                 延时出料
                                      启动出料延时
拍正气缸            —                  q_bAlignRetract=TRUE            保持收回
                                      q_bAlignExtend=FALSE
```

### 2.3 Mode 2 (MODE_A_DUAL): A侧双向模式

#### 2.3.1 入料时 (INFEED状态)

```
逻辑功能           FB_1014命令输出                      用途
-----------------------------------------------------------------------
入料检测光电1      i_xPos1                              物料进入时确认
入料检测光电2      i_xPos2                              精定位确认
入料气缸(A侧)      q_bInfeedExtend=TRUE                 放下允许物料从A侧进入
                   q_bInfeedRetract=FALSE
阻挡气缸(B侧)      q_bDischargeRetract=TRUE             抬起阻挡
                   q_bDischargeExtend=FALSE
拍正气缸           q_bAlignExtend=TRUE                  保持默认(伸出)
                   q_bAlignRetract=FALSE
马达               q_bFwdCmd=TRUE                       正转进料
```

#### 2.3.2 对齐时 (ALIGN状态) — 三步子步骤

```
逻辑功能           FB_1014命令输出                      用途
-----------------------------------------------------------------------
m_iAlignStep=0     q_bAlignExtend=TRUE                  拍正伸出+延时
                   启动对齐延时
m_iAlignStep=1     q_bDischargeExtend=TRUE              阻挡下降(B侧)
                   q_bDischargeRetract=FALSE
m_iAlignStep=2     q_bAlignExtend=FALSE                 拍正收回
                   q_bAlignRetract=TRUE
马达               q_bFwdCmd=FALSE                      停止
```

#### 2.3.3 出料时 (DISCHARGE状态)

```
逻辑功能           FB_1014命令输出                      用途
-----------------------------------------------------------------------
出料检测光电1      i_xPos1                              物料离开时确认
出料检测光电2      i_xPos2                              离开确认
出料气缸(A侧)      q_bInfeedExtend=TRUE                 放下允许物料出去
                   q_bInfeedRetract=FALSE
阻挡气缸(B侧)      q_bDischargeRetract=TRUE             抬起阻挡
                   q_bDischargeExtend=FALSE
拍正气缸           q_bAlignRetract=TRUE                 保持收回
                   q_bAlignExtend=FALSE
马达               q_bRevCmd=TRUE                       反转出料
```

## 3. 状态定义表

### 3.1 主状态机 (Station_SM)

| 状态值 | 名称 | 触发条件 | 命令输出 | 出口条件 | 出口目标 |
|--------|------|---------|----------|----------|----------|
| 0 | IDLE | 初始/复位 | 全收回 | Auto+Selected | READY |
| 1 | READY | IDLE出口 | 全收回 | 上游请求 | INFEED |
| 2 | INFEED | 上游请求 | 按Mode决定入料侧气缸 | 到位+延时 | ALIGN |
| 3 | ALIGN | INFEED出口 | 子步骤: 拍正→延时→阻挡→收回 | 子步骤完成 | PROCESSING |
| 4 | PROCESSING | ALIGN出口 | 按Mode保持气缸 | 加工完成 | DISCHARGE |
| 5 | DISCHARGE | 加工完成 | 按Mode: 纯延时 / 准备+出料 | 延时到 | COMPLETE |
| 6 | COMPLETE | 延时到 | 全收回 | 脉冲结束 | IDLE |
| 7 | PAUSE | 暂停 | 停马达 | 暂停取消 | 恢复 |
| 8 | FAULT | 停止/VFD报警 | 安全态(拍正伸出,其余收回) | 停止+报警取消 | IDLE |

### 3.2 ALIGN 态子步骤 (m_iAlignStep)

#### Mode 0 (MODE_NORMAL) / Mode 2 (MODE_A_DUAL): 三步

| 步骤 | 触发条件 | 命令输出 | 出口条件 | 出口目标 |
|------|---------|----------|----------|----------|
| 0 | 进入ALIGN | 拍正伸出, 启动对齐延时 | 拍正到位+延时到 | 步骤1 |
| 1 | 步骤0出口 | 阻挡下降 | 阻挡到位 | 步骤2 |
| 2 | 步骤1出口 | 拍正收回 | 拍正收回到位 | PROCESSING |

#### Mode 1 (MODE_B_DUAL): 四步

| 步骤 | 触发条件 | 命令输出 | 出口条件 | 出口目标 |
|------|---------|----------|----------|----------|
| 0 | 进入ALIGN | 拍正伸出 | 拍正到位 | 步骤1 |
| 1 | 步骤0出口 | 保持拍正, 启动对齐延时 | 延时到 | 步骤2 |
| 2 | 步骤1出口 | 阻挡下降 | 阻挡到位 | 步骤3 |
| 3 | 步骤2出口 | 拍正收回 | 拍正收回到位 | PROCESSING |

### 3.3 DISCHARGE 态出料准备子步骤 (m_iDischPrepStep) — Mode 1 专用

| 步骤 | 触发条件 | 命令输出 | 出口条件 | 出口目标 |
|------|---------|----------|----------|----------|
| 0 | 进入DISCHARGE | 马达正转, 出料侧气缸放下 | 命令已输出(立即) | 步骤1 |
| 1 | 步骤0出口 | 保持马达/气缸, 启动准备延时 | 准备延时到 | 步骤2 |
| 2 | 步骤1出口 | 保持马达/气缸, 启动出料延时 | 出料延时到 | COMPLETE |

### 3.4 PROCESSING 态气缸行为按Mode

| Mode | q_bInfeed | q_bAlign | q_bDischarge | 说明 |
|------|-----------|----------|--------------|------|
| MODE_NORMAL(0) | 收回 | 收回 | 收回 | 全收回, 加工安全态 |
| MODE_B_DUAL(1) | 收回 | 收回 | 伸出 | B侧缸预置, 为下一轮B侧入料准备 |
| MODE_A_DUAL(2) | 伸出 | 收回 | 收回 | A侧缸预置, 为下一轮A侧入料准备 |

## 4. 详细伪代码

### 4.1 停止/暂停/VFD报警优先级链

```pascal
// 最高优先级: 停止
IF i_bStop THEN
    q_bFwdCmd := FALSE;
    q_bRevCmd := FALSE;
    q_bSlowCmd := FALSE;
    // 气缸: 安全态 — 拍正伸出, 其余收回
    q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
    q_bAlignExtend := TRUE;      q_bAlignRetract := FALSE;
    q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
    q_bReplyUpstream := FALSE;
    q_bReplyDownstream := FALSE;
    q_bInfeedActive := FALSE;
    q_iState := ST_FAULT;
    iState := ST_FAULT;
    RETURN;
END_IF;

// 次高优先级: VFD报警
IF i_bVfdAlarm THEN
    q_bFwdCmd := FALSE;
    q_bRevCmd := FALSE;
    q_bSlowCmd := FALSE;
    // 气缸: 安全态 — 拍正伸出, 其余收回
    q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
    q_bAlignExtend := TRUE;      q_bAlignRetract := FALSE;
    q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
    q_bReplyUpstream := FALSE;
    q_bReplyDownstream := FALSE;
    q_bInfeedActive := FALSE;
    q_iState := ST_FAULT;
    iState := ST_FAULT;
    RETURN;
END_IF;

// 第三优先级: 暂停
IF i_bPause THEN
    IF iState <> ST_PAUSE THEN
        m_iPauseState := iState;
    END_IF;
    q_bFwdCmd := FALSE;
    q_bRevCmd := FALSE;
    q_bSlowCmd := FALSE;
    q_iState := ST_PAUSE;
    iState := ST_PAUSE;
    RETURN;
END_IF;
```

### 4.2 VFD报警处理

```
触发条件: i_bVfdAlarm = TRUE
响应行为:
  1. 进入ST_FAULT状态
  2. 停止所有马达命令(q_bFwdCmd/q_bRevCmd/q_bSlowCmd := FALSE)
  3. 安全态: 拍正伸出(q_bAlignExtend := TRUE), 其余收回
  4. 清除通信信号(q_bReplyUpstream/q_bReplyDownstream := FALSE)
  5. 清除进料标志(q_bInfeedActive := FALSE)

退出条件: NOT i_bStop AND NOT i_bVfdAlarm -> ST_IDLE

设计说明:
  - FB_1012在VFD故障时已自行切断马达物理输出
  - FB_1014的VFD报警处理是状态机层面的补充响应
  - 确保状态机与物理输出状态一致, 避免VFD恢复后状态机仍在INFEED/DISCHARGE等状态
  - Stop与VFD报警共享ST_FAULT状态, 两者均需清除才能退出
  - 安全态拍正伸出作为机械屏障, 防止物料意外移动
```

### 4.3 传感器去抖 (LSP-903/LSP-906合规)

```pascal
// 光电去抖 - PT为DINT(扫描周期数, 假设1ms/周期)
tPosStart(IN := i_xInfeedStart, PT := i_dDebounceMs,
          Q => m_bPosStartQ, ET => m_dPosStartET);
IF m_bPosStartQ THEN
    m_bStartConfirmed := TRUE;
END_IF;

tPos1(IN := i_xPos1, PT := i_dDebounceMs,
      Q => m_bPos1Q, ET => m_dPos1ET);
IF m_bPos1Q THEN
    m_bPos1Confirmed := TRUE;
END_IF;

tPos2(IN := i_xPos2, PT := i_dDebounceMs,
      Q => m_bPos2Q, ET => m_dPos2ET);
IF m_bPos2Q THEN
    m_bPos2Confirmed := TRUE;
END_IF;

m_bAllConfirmed := m_bStartConfirmed
    AND m_bPos1Confirmed
    AND m_bPos2Confirmed;
```

### 4.4 手动模式处理

```pascal
IF NOT i_bAutoMode THEN
    q_bFwdCmd := FALSE;
    q_bRevCmd := FALSE;
    q_bSlowCmd := FALSE;
    q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
    q_bAlignExtend := FALSE;     q_bAlignRetract := TRUE;
    q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
    q_bReplyUpstream := FALSE;
    q_bReplyDownstream := FALSE;
    q_bInfeedActive := FALSE;
    m_bReplyUpOk := FALSE;
    m_bStartConfirmed := FALSE;
    m_bPos1Confirmed := FALSE;
    m_bPos2Confirmed := FALSE;
    m_bInfeedDelayIn := FALSE;
    m_bDischargeDelayIn := FALSE;
    m_bAlignDelayIn := FALSE;
    m_bDischPrepDelayIn := FALSE;
    m_iAlignStep := 0;
    m_iDischPrepStep := 0;
    q_iState := ST_IDLE;
    iState := ST_IDLE;
    RETURN;
END_IF;
```

### 4.5 下游中断报警

```pascal
IF i_xInfeedStart AND i_bAutoMode
    AND (NOT i_bDownstreamReq) AND q_bInfeedActive THEN
    q_bIntAlarmMem := TRUE;
END_IF;
```

### 4.6 回应上游逻辑

```pascal
IF i_xInfeedStart
    AND m_bPos1Confirmed AND m_bPos2Confirmed
    AND i_bAutoMode
    AND (iState = ST_IDLE OR iState = ST_READY)
    AND (NOT m_bReplyUpOk) THEN
    m_bReplyUpOk := TRUE;
    q_bReplyUpstream := TRUE;
END_IF;
```

### 4.7 延时定时器 (LSP-903/LSP-906合规)

```pascal
// 入料延时
tInfeedDelay(IN := m_bInfeedDelayIn, PT := i_dInfeedDelayMs,
             Q => m_bInfeedDelayQ, ET => m_dInfeedDelayET);

// 出料延时
tDischargeDelay(IN := m_bDischargeDelayIn, PT := i_dDischargeDelayMs,
                Q => m_bDischargeDelayQ, ET => m_dDischargeDelayET);

// 对齐延时
tAlignDelay(IN := m_bAlignDelayIn, PT := i_dAlignDelayMs,
            Q => m_bAlignDelayQ, ET => m_dAlignDelayET);

// 出料准备延时 (Mode 1专用)
tDischPrepDelay(IN := m_bDischPrepDelayIn, PT := i_dDischPrepDelayMs,
                Q => m_bDischPrepDelayQ, ET => m_dDischPrepDelayET);
```

### 4.8 状态机CASE逻辑

```pascal
CASE iState OF

    ST_IDLE:
        q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
        q_bAlignExtend := FALSE;     q_bAlignRetract := TRUE;
        q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
        q_bReplyUpstream := FALSE;
        q_bReplyDownstream := FALSE;
        q_bInfeedActive := FALSE;
        m_bReplyUpOk := FALSE;
        m_bStartConfirmed := FALSE;
        m_bPos1Confirmed := FALSE;
        m_bPos2Confirmed := FALSE;
        m_bInfeedDelayIn := FALSE;
        m_bDischargeDelayIn := FALSE;
        m_bAlignDelayIn := FALSE;
        m_bDischPrepDelayIn := FALSE;
        m_iAlignStep := 0;
        m_iDischPrepStep := 0;

        IF i_bAutoMode AND i_bSelected THEN
            iState := ST_READY;
        END_IF;

    ST_READY:
        q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
        q_bAlignExtend := FALSE;     q_bAlignRetract := TRUE;
        q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;

        IF i_bUpstreamReq AND m_bReplyUpOk AND i_bSelected THEN
            iState := ST_INFEED;
            q_bInfeedActive := TRUE;
            // 按Mode决定马达方向
            IF i_iMode = MODE_A_DUAL THEN
                q_bFwdCmd := TRUE;
            ELSE
                q_bRevCmd := TRUE;
            END_IF;
        END_IF;

    ST_INFEED:
        // 马达: 按Mode决定方向
        IF i_iMode = MODE_A_DUAL THEN
            q_bFwdCmd := TRUE;
        ELSE
            q_bRevCmd := TRUE;
        END_IF;

        // 功能切换: 按Mode决定入料侧气缸
        IF i_iMode = MODE_A_DUAL THEN
            // A侧双向: InfeedCyl为入料气缸
            q_bInfeedExtend := TRUE;  q_bInfeedRetract := FALSE;
            q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
        ELSE
            // Mode 0/1: DischargeCyl为入料气缸
            q_bDischargeExtend := TRUE;  q_bDischargeRetract := FALSE;
            q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
        END_IF;

        q_bAlignExtend := TRUE;  q_bAlignRetract := FALSE;
        q_bInfeedActive := TRUE;

        IF m_bStartConfirmed THEN
            q_bSlowCmd := TRUE;
        ELSE
            q_bSlowCmd := FALSE;
        END_IF;

        m_bInfeedDelayIn := TRUE;
        IF m_bAllConfirmed AND m_bInfeedDelayQ THEN
            iState := ST_ALIGN;
            q_bFwdCmd := FALSE;
            q_bRevCmd := FALSE;
            q_bSlowCmd := FALSE;
            m_bInfeedDelayIn := FALSE;
            m_iAlignStep := 0;
        END_IF;

    ST_ALIGN:
        // 马达停止
        q_bFwdCmd := FALSE;
        q_bRevCmd := FALSE;
        q_bSlowCmd := FALSE;
        q_bInfeedActive := TRUE;

        // 公有基础: 入料侧气缸保持放下
        IF i_iMode = MODE_A_DUAL THEN
            q_bInfeedExtend := TRUE;  q_bInfeedRetract := FALSE;
            q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
        ELSE
            q_bDischargeExtend := TRUE;  q_bDischargeRetract := FALSE;
            q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
        END_IF;

        // 子步骤 CASE 结构
        CASE m_iAlignStep OF
            0:  // 拍正伸出 (+ 延时, Mode 0/2 合并)
                q_bAlignExtend := TRUE;  q_bAlignRetract := FALSE;

                IF i_iMode = MODE_B_DUAL THEN
                    // Mode 1: 四步 — 伸出到位即进入延时步骤
                    IF i_bAlignIsExtended THEN
                        m_iAlignStep := 1;
                    END_IF;
                ELSE
                    // Mode 0/2: 三步 — 伸出+延时一步完成
                    m_bAlignDelayIn := TRUE;
                    IF i_bAlignIsExtended AND m_bAlignDelayQ THEN
                        m_bAlignDelayIn := FALSE;
                        m_iAlignStep := 1;
                    END_IF;
                END_IF;

            1:  // 延时 (仅Mode 1) / 阻挡下降 (Mode 0/2)
                IF i_iMode = MODE_B_DUAL THEN
                    // Mode 1: 四步 — 独立延时步骤
                    q_bAlignExtend := TRUE;  q_bAlignRetract := FALSE;
                    m_bAlignDelayIn := TRUE;
                    IF m_bAlignDelayQ THEN
                        m_bAlignDelayIn := FALSE;
                        m_iAlignStep := 2;
                    END_IF;
                ELSE
                    // Mode 0/2: 三步 — 阻挡下降
                    q_bAlignExtend := TRUE;  q_bAlignRetract := FALSE;
                    IF i_iMode = MODE_A_DUAL THEN
                        // A侧双向: 阻挡在B侧
                        q_bDischargeExtend := TRUE;  q_bDischargeRetract := FALSE;
                        IF i_bDischargeIsExtended THEN
                            m_iAlignStep := 2;
                        END_IF;
                    ELSE
                        // Mode 0: 阻挡在A侧
                        q_bInfeedExtend := TRUE;  q_bInfeedRetract := FALSE;
                        IF i_bInfeedIsExtended THEN
                            m_iAlignStep := 2;
                        END_IF;
                    END_IF;
                END_IF;

            2:  // 阻挡下降 (Mode 1) / 拍正收回 (Mode 0/2)
                IF i_iMode = MODE_B_DUAL THEN
                    // Mode 1: 四步 — 阻挡下降
                    q_bAlignExtend := TRUE;  q_bAlignRetract := FALSE;
                    q_bInfeedExtend := TRUE;  q_bInfeedRetract := FALSE;
                    IF i_bInfeedIsExtended THEN
                        m_iAlignStep := 3;
                    END_IF;
                ELSE
                    // Mode 0/2: 三步 — 拍正收回
                    q_bAlignExtend := FALSE;  q_bAlignRetract := TRUE;
                    IF i_bAlignIsRetracted THEN
                        iState := ST_PROCESSING;
                        IF i_iMode = MODE_A_DUAL THEN
                            q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
                        ELSE
                            q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
                            q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
                        END_IF;
                        q_bInfeedActive := FALSE;
                        m_iAlignStep := 0;
                    END_IF;
                END_IF;

            3:  // 拍正收回 (仅Mode 1)
                q_bAlignExtend := FALSE;  q_bAlignRetract := TRUE;
                q_bInfeedExtend := TRUE;  q_bInfeedRetract := FALSE;
                IF i_bAlignIsRetracted THEN
                    iState := ST_PROCESSING;
                    q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
                    q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
                    q_bInfeedActive := FALSE;
                    m_iAlignStep := 0;
                END_IF;
        END_CASE;

    ST_PROCESSING:
        q_bFwdCmd := FALSE;
        q_bRevCmd := FALSE;
        q_bSlowCmd := FALSE;

        // 气缸行为按Mode区分
        IF i_iMode = MODE_B_DUAL THEN
            // B侧双向: B侧缸保持伸出, 其余收回
            q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
            q_bAlignExtend := FALSE;     q_bAlignRetract := TRUE;
            q_bDischargeExtend := TRUE;  q_bDischargeRetract := FALSE;
        ELSIF i_iMode = MODE_A_DUAL THEN
            // A侧双向: A侧缸保持伸出, 其余收回
            q_bInfeedExtend := TRUE;     q_bInfeedRetract := FALSE;
            q_bAlignExtend := FALSE;     q_bAlignRetract := TRUE;
            q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
        ELSE
            // Mode 0: 全收回
            q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
            q_bAlignExtend := FALSE;     q_bAlignRetract := TRUE;
            q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
        END_IF;

        m_bStartConfirmed := FALSE;
        m_bPos1Confirmed := FALSE;
        m_bPos2Confirmed := FALSE;
        m_bReplyUpOk := FALSE;
        q_bIntAlarmMem := FALSE;

        IF i_bProcessDone THEN
            iState := ST_DISCHARGE;
            q_bReplyDownstream := TRUE;
            m_iDischPrepStep := 0;
        END_IF;

    ST_DISCHARGE:
        // 拍正保持收回
        q_bAlignExtend := FALSE;  q_bAlignRetract := TRUE;

        IF i_iMode = MODE_B_DUAL THEN
            // --- Mode 1: B侧双向, 出料准备子步骤 ---
            CASE m_iDischPrepStep OF
                0:  // 准备步骤1: 马达启动+出料气缸放下
                    q_bFwdCmd := TRUE;
                    q_bInfeedExtend := TRUE;  q_bInfeedRetract := FALSE;
                    q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
                    IF i_bSlowMode THEN
                        q_bSlowCmd := TRUE;
                    END_IF;
                    m_bDischPrepDelayIn := TRUE;
                    m_iDischPrepStep := 1;

                1:  // 准备步骤2: 等待准备延时确认
                    q_bFwdCmd := TRUE;
                    q_bInfeedExtend := TRUE;  q_bInfeedRetract := FALSE;
                    q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
                    IF m_bDischPrepDelayQ THEN
                        m_bDischPrepDelayIn := FALSE;
                        m_bDischargeDelayIn := TRUE;
                        m_iDischPrepStep := 2;
                    END_IF;

                2:  // 出料步骤: 正常出料延时
                    q_bFwdCmd := TRUE;
                    q_bInfeedExtend := TRUE;  q_bInfeedRetract := FALSE;
                    q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
                    IF m_bDischargeDelayQ THEN
                        iState := ST_COMPLETE;
                        q_bSlowCmd := FALSE;
                        m_bDischargeDelayIn := FALSE;
                        m_iDischPrepStep := 0;
                    END_IF;
            END_CASE;

        ELSIF i_iMode = MODE_A_DUAL THEN
            // --- Mode 2: A侧双向, 反转出料 ---
            q_bRevCmd := TRUE;
            q_bInfeedExtend := TRUE;  q_bInfeedRetract := FALSE;
            q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
            IF i_bSlowMode THEN
                q_bSlowCmd := TRUE;
            END_IF;
            m_bDischargeDelayIn := TRUE;
            IF m_bDischargeDelayQ THEN
                iState := ST_COMPLETE;
                q_bSlowCmd := FALSE;
                q_bRevCmd := FALSE;
            END_IF;

        ELSE
            // --- Mode 0: 正常模式, 正转出料 ---
            q_bFwdCmd := TRUE;
            q_bInfeedExtend := TRUE;  q_bInfeedRetract := FALSE;
            q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
            IF i_bSlowMode THEN
                q_bSlowCmd := TRUE;
            END_IF;
            m_bDischargeDelayIn := TRUE;
            IF m_bDischargeDelayQ THEN
                iState := ST_COMPLETE;
                q_bSlowCmd := FALSE;
            END_IF;
        END_IF;

    ST_COMPLETE:
        q_bFwdCmd := FALSE;
        q_bRevCmd := FALSE;
        q_bSlowCmd := FALSE;
        q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
        q_bAlignExtend := FALSE;     q_bAlignRetract := TRUE;
        q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
        q_bReplyDownstream := FALSE;
        q_bInfeedActive := FALSE;
        q_dwProductionCount := q_dwProductionCount + 1;
        q_bIntAlarmMem := FALSE;
        m_bDischargeDelayIn := FALSE;
        m_bDischPrepDelayIn := FALSE;
        m_iDischPrepStep := 0;
        iState := ST_IDLE;

    ST_PAUSE:
        q_bFwdCmd := FALSE;
        q_bRevCmd := FALSE;
        q_bSlowCmd := FALSE;
        iState := m_iPauseState;

    ST_FAULT:
        q_bFwdCmd := FALSE;
        q_bRevCmd := FALSE;
        q_bSlowCmd := FALSE;
        // 安全态: 拍正伸出, 其余收回
        q_bInfeedExtend := FALSE;    q_bInfeedRetract := TRUE;
        q_bAlignExtend := TRUE;      q_bAlignRetract := FALSE;
        q_bDischargeExtend := FALSE; q_bDischargeRetract := TRUE;
        q_bReplyUpstream := FALSE;
        q_bReplyDownstream := FALSE;

        IF NOT i_bStop AND NOT i_bVfdAlarm THEN
            iState := ST_IDLE;
        END_IF;

END_CASE;

q_iState := iState;

// 下游请求恢复时清除中断报警
IF i_bDownstreamReq THEN
    q_bIntAlarmMem := FALSE;
END_IF;
```

## 5. 时序图

### 5.1 Mode 0 正常模式主流程时序

```
时间轴 ->

设备              FB_1014(编排器)                                  说明
  |                     |
  |-- UpstreamReq ----->|  [READY] 全收回
  |<-- ReplyUpstream ---|  X421/X422检测
  |                     |  -> [INFEED]
  |                     |  q_bRevCmd=ON  -> OB1 -> FB_1012(反转)
  |                     |  q_bDischargeExtend=ON -> OB1 -> FB_1011(入料气缸)
  |<-------------------+  物料从出料口进入
  |                     |  到位光电触发
  |                     |  -> [ALIGN] m_iAlignStep=0
  |                     |  q_bRevCmd=OFF -> OB1 -> FB_1012(停止)
  |                     |  q_bAlignExtend=ON -> OB1 -> FB_1011(拍正伸出)
  |                     |  对齐延时...
  |                     |  i_bAlignIsExtended=TRUE <- OB1 <- FB_1011
  |                     |  -> m_iAlignStep=1
  |                     |  q_bInfeedExtend=ON -> OB1 -> FB_1011(阻挡下降)
  |                     |  i_bInfeedIsExtended=TRUE <- OB1 <- FB_1011
  |                     |  -> m_iAlignStep=2
  |                     |  q_bAlignRetract=ON -> OB1 -> FB_1011(拍正收回)
  |                     |  i_bAlignIsRetracted=TRUE <- OB1 <- FB_1011
  |                     |  -> [PROCESSING] 全收回
  |<-- ProcessDone -----|  等待加工
  |<-- ReplyDownstream -|  -> [DISCHARGE]
  |                     |  q_bFwdCmd=ON -> OB1 -> FB_1012(正转)
  |                     |  q_bInfeedExtend=ON -> OB1 -> FB_1011(出料气缸)
  |                     |  延时...
  |                     |  -> [COMPLETE]
  |                     |  -> [IDLE]
  +-------------------->  物料从入料口出去
```

### 5.2 Mode 1 B侧双向模式 — 对齐时序(四步子步骤)

```
时间轴 ->

设备              FB_1014(编排器)                                 说明
  |                     |
...INFEED完成, 进入ALIGN...
  |                     |  -> [ALIGN] m_iAlignStep=0
  |                     |  q_bAlignExtend=ON -> OB1 -> FB_1011(拍正伸出)
  |                     |
  |<- AlignIsExtended --|  i_bAlignIsExtended=TRUE <- OB1 <- FB_1011
  |                     |
  |                     |  -> m_iAlignStep=1
  |                     |  q_bAlignExtend=ON(保持)
  |                     |  对齐延时 tAlignDelay...
  |                     |
  |                     |  m_bAlignDelayQ=TRUE
  |                     |  -> m_iAlignStep=2
  |                     |  q_bInfeedExtend=ON -> OB1 -> FB_1011(阻挡下降)
  |                     |
  |<- InfeedIsExtended -|  i_bInfeedIsExtended=TRUE <- OB1 <- FB_1011
  |                     |
  |                     |  -> m_iAlignStep=3
  |                     |  q_bAlignExtend=OFF, q_bAlignRetract=ON(拍正收回)
  |                     |
  |<- AlignIsRetracted -|  i_bAlignIsRetracted=TRUE <- OB1 <- FB_1011
  |                     |
  |                     |  -> [PROCESSING]
  +--------------------->  进入加工
```

### 5.3 Mode 1 B侧双向模式 — 出料准备+出料时序

```
时间轴 ->

设备              FB_1014(编排器)                                 说明
  |                     |
...PROCESSING完成...
  |<-- ProcessDone -----|
  |<-- ReplyDownstream -|  -> [DISCHARGE] m_iDischPrepStep=0
  |                     |
  |                     |  q_bFwdCmd=ON -> OB1 -> FB_1012(正转)
  |                     |  q_bInfeedExtend=ON -> OB1 -> FB_1011(出料气缸放下)
  |                     |  启动准备延时 tDischPrepDelay...
  |                     |  -> m_iDischPrepStep=1
  |                     |
  |                     |  m_bDischPrepDelayQ=TRUE
  |                     |  -> m_iDischPrepStep=2
  |                     |  启动出料延时 tDischargeDelay...
  |                     |
  +-------------------->  物料从B侧出口出去
  |                     |
  |                     |  m_bDischargeDelayQ=TRUE
  |                     |  -> [COMPLETE]
  |                     |  -> [IDLE]
```

### 5.4 Mode 2 A侧双向模式主流程时序

```
时间轴 ->

设备              FB_1014(编排器)                                 说明
  |                     |
  |-- UpstreamReq ----->|  [READY] 全收回
  |<-- ReplyUpstream ---|  X421/X422检测
  |                     |  -> [INFEED]
  |                     |  q_bFwdCmd=ON  -> OB1 -> FB_1012(正转进料)
  |                     |  q_bInfeedExtend=ON -> OB1 -> FB_1011(A侧入料气缸)
  |<-------------------+  物料从A侧进入
  |                     |  到位光电触发
  |                     |  -> [ALIGN] m_iAlignStep=0
  |                     |  q_bFwdCmd=OFF -> OB1 -> FB_1012(停止)
  |                     |  q_bAlignExtend=ON -> OB1 -> FB_1011(拍正伸出)
  |                     |  对齐延时...
  |                     |  i_bAlignIsExtended=TRUE <- OB1 <- FB_1011
  |                     |  -> m_iAlignStep=1
  |                     |  q_bDischargeExtend=ON -> OB1 -> FB_1011(B侧阻挡下降)
  |                     |  i_bDischargeIsExtended=TRUE <- OB1 <- FB_1011
  |                     |  -> m_iAlignStep=2
  |                     |  q_bAlignRetract=ON -> OB1 -> FB_1011(拍正收回)
  |                     |  i_bAlignIsRetracted=TRUE <- OB1 <- FB_1011
  |                     |  -> [PROCESSING]  A侧缸保持伸出
  |<-- ProcessDone -----|  等待加工
  |<-- ReplyDownstream -|  -> [DISCHARGE]
  |                     |  q_bRevCmd=ON -> OB1 -> FB_1012(反转出料)
  |                     |  q_bInfeedExtend=ON -> OB1 -> FB_1011(A侧出料气缸)
  |                     |  延时...
  |                     |  -> [COMPLETE]
  |                     |  -> [IDLE]
  +-------------------->  物料从A侧出去
```

### 5.5 VFD报警时序(安全态拍正伸出)

```
时间轴 ->

FB_1012             FB_1014                                  说明
  |                     |
  |-- VFD Fault ------>|  i_bVfdAlarm=TRUE
  |                     |  -> [FAULT]
  |                     |  q_bFwdCmd=FALSE, q_bRevCmd=FALSE
  |                     |  q_bSlowCmd=FALSE
  |                     |  q_bAlignExtend=TRUE(安全态拍正伸出)
  |                     |  q_bInfeedRetract=TRUE
  |                     |  q_bDischargeRetract=TRUE
  |  (马达输出已切断)   |  状态机同步进入安全态
  |                     |
  |-- VFD Recover ---->|  i_bVfdAlarm=FALSE
  |                     |  (需同时i_bStop=FALSE)
  |                     |  -> [IDLE]
```

## 6. 边界条件处理

| 场景 | 行为 |
|------|------|
| AutoMode=FALSE | 所有输出清零, 气缸收回命令, 状态归IDLE, 子步骤机归零 |
| Stop触发 | 立即停止马达命令, 拍正伸出(安全态), 其余气缸收回命令 |
| VFD报警触发 | 与Stop同等级安全响应, 拍正伸出, 进入ST_FAULT |
| Pause触发 | 停止马达命令, 保持当前气缸命令状态 |
| 到位光电未触发 | 等待光电确认 |
| 拍正气缸磁环信号丢失 | i_bAlignIsExtended保持FALSE, 停留在对应m_iAlignStep; FB_1011在OB1侧报超时 |
| 阻挡气缸下降超时 | 对应磁环信号保持FALSE, 停留在对应m_iAlignStep; FB_1011在OB1侧报超时 |
| 拍正气缸收回超时 | i_bAlignIsRetracted保持FALSE, 停留在对应m_iAlignStep; FB_1011在OB1侧报超时 |
| Mode切换时不在IDLE | 当前周期继续按原模式执行, 下个完整周期生效 |
| i_iMode值超出范围 | Mode 0/1/2有效, 其他值按MODE_B_DUAL(1)处理 |
| 出料准备延时超时 | tDischPrepDelay正常超时后进入出料步骤 |
| 传感器冲突(双位同时ON) | FB_1011在OB1侧检测SensorFault |
| 加工中ProcessDone=FALSE | 保持PROCESSING态 |
| 工站未选中 | 保持IDLE |
| VFD报警+Stop同时存在 | 需两者均清除才能退出ST_FAULT |
| VFD报警期间Pause无效 | VFD报警优先级高于暂停, FAULT状态下不响应暂停 |
| Mode 1 B侧双向: 出料准备中触发Stop | 优先级链拦截, 安全态拍正伸出 |

## 7. 变量定义详情

### 7.1 VAR_INPUT (控制)

| 变量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| i_bAutoMode | BOOL | FALSE | 自动模式使能 |
| i_bUpstreamReq | BOOL | FALSE | 上游请求 |
| i_bDownstreamReq | BOOL | FALSE | 下游请求 |
| i_bSelected | BOOL | FALSE | 工站选中 |
| i_bProcessDone | BOOL | FALSE | 加工完成 |
| i_bStop | BOOL | FALSE | 停止信号 |
| i_bPause | BOOL | FALSE | 暂停信号 |
| i_bSlowMode | BOOL | FALSE | 慢速模式使能 |
| i_bVfdAlarm | BOOL | FALSE | VFD报警信号(来自FB_1012) |
| i_iMode | INT | 1 | 运行模式: 0=正常, 1=B侧双向(默认), 2=A侧双向 |

### 7.2 VAR_INPUT (参数)

| 变量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| i_dInfeedDelayMs | DINT | 1000 | 入料延时(ms) |
| i_dDischargeDelayMs | DINT | 1000 | 出料延时(ms) |
| i_dAlignDelayMs | DINT | 500 | 拍正对齐延时(ms) |
| i_dDebounceMs | DINT | 200 | 去抖延时(ms) |
| i_dDischPrepDelayMs | DINT | 300 | 出料准备延时(ms) (Mode 1专用) |

### 7.3 VAR_INPUT (传感器)

| 变量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| i_xInfeedStart | BOOL | FALSE | 入料开始光电(X420) |
| i_xPos1 | BOOL | FALSE | 位置1光电(X421) |
| i_xPos2 | BOOL | FALSE | 位置2光电(X422) |

### 7.4 VAR_INPUT (气缸状态 - 来自FB_1011)

| 变量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| i_bInfeedIsExtended | BOOL | FALSE | A侧阻挡气缸伸出到位 |
| i_bInfeedIsRetracted | BOOL | FALSE | A侧阻挡气缸收回到位 |
| i_bAlignIsExtended | BOOL | FALSE | 拍正气缸伸出到位 |
| i_bAlignIsRetracted | BOOL | FALSE | 拍正气缸收回到位 |
| i_bDischargeIsExtended | BOOL | FALSE | B侧出料气缸伸出到位 |
| i_bDischargeIsRetracted | BOOL | FALSE | B侧出料气缸收回到位 |

### 7.5 VAR_OUTPUT (气缸命令 - 到FB_1011)

| 变量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| q_bInfeedExtend | BOOL | FALSE | A侧阻挡气缸伸出命令 |
| q_bInfeedRetract | BOOL | FALSE | A侧阻挡气缸收回命令 |
| q_bAlignExtend | BOOL | FALSE | 拍正气缸伸出命令 |
| q_bAlignRetract | BOOL | FALSE | 拍正气缸收回命令 |
| q_bDischargeExtend | BOOL | FALSE | B侧出料气缸伸出命令 |
| q_bDischargeRetract | BOOL | FALSE | B侧出料气缸收回命令 |

### 7.6 VAR_OUTPUT (马达命令 - 到FB_1012)

| 变量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| q_bFwdCmd | BOOL | FALSE | 正转命令 |
| q_bRevCmd | BOOL | FALSE | 反转命令 |
| q_bSlowCmd | BOOL | FALSE | 慢速命令 |

### 7.7 VAR_OUTPUT (通信/状态)

| 变量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| q_bReplyUpstream | BOOL | FALSE | 回应上游 |
| q_bReplyDownstream | BOOL | FALSE | 回应下游 |
| q_iState | INT | 0 | 当前状态(0-8) |
| q_dwProductionCount | DWORD | 0 | 累计产量 |
| q_bInfeedActive | BOOL | FALSE | 输送进行中 |
| q_bIntAlarmMem | BOOL | FALSE | 中断报警暂存 |

### 7.8 VAR (内部变量)

| 变量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| iState | INT | 0 | 状态机当前状态 |
| m_iPauseState | INT | 0 | 暂停前状态 |
| m_iAlignStep | INT | 0 | 拍正对齐子步骤机(0-3) |
| m_iDischPrepStep | INT | 0 | 出料准备子步骤机(0-2, Mode 1专用) |
| tPosStart | FB_TON | - | 入料开始光电去抖 |
| tPos1 | FB_TON | - | 位置1光电去抖 |
| tPos2 | FB_TON | - | 位置2光电去抖 |
| tInfeedDelay | FB_TON | - | 入料延时定时器 |
| tDischargeDelay | FB_TON | - | 出料延时定时器 |
| tAlignDelay | FB_TON | - | 对齐延时定时器 |
| tDischPrepDelay | FB_TON | - | 出料准备延时定时器(Mode 1专用) |
| m_bPosStartQ | BOOL | FALSE | tPosStart.Q接收 |
| m_bPos1Q | BOOL | FALSE | tPos1.Q接收 |
| m_bPos2Q | BOOL | FALSE | tPos2.Q接收 |
| m_bInfeedDelayQ | BOOL | FALSE | tInfeedDelay.Q接收 |
| m_bDischargeDelayQ | BOOL | FALSE | tDischargeDelay.Q接收 |
| m_bAlignDelayQ | BOOL | FALSE | tAlignDelay.Q接收 |
| m_bDischPrepDelayQ | BOOL | FALSE | tDischPrepDelay.Q接收 |
| m_dPosStartET | DINT | 0 | tPosStart.ET接收 |
| m_dPos1ET | DINT | 0 | tPos1.ET接收 |
| m_dPos2ET | DINT | 0 | tPos2.ET接收 |
| m_dInfeedDelayET | DINT | 0 | tInfeedDelay.ET接收 |
| m_dDischargeDelayET | DINT | 0 | tDischargeDelay.ET接收 |
| m_dAlignDelayET | DINT | 0 | tAlignDelay.ET接收 |
| m_dDischPrepDelayET | DINT | 0 | tDischPrepDelay.ET接收 |
| m_bInfeedDelayIn | BOOL | FALSE | tInfeedDelay.IN控制 |
| m_bDischargeDelayIn | BOOL | FALSE | tDischargeDelay.IN控制 |
| m_bAlignDelayIn | BOOL | FALSE | tAlignDelay.IN控制 |
| m_bDischPrepDelayIn | BOOL | FALSE | tDischPrepDelay.IN控制 |
| m_bStartConfirmed | BOOL | FALSE | 开始光电确认 |
| m_bPos1Confirmed | BOOL | FALSE | 位置1确认 |
| m_bPos2Confirmed | BOOL | FALSE | 位置2确认 |
| m_bAllConfirmed | BOOL | FALSE | 全部确认 |
| m_bReplyUpOk | BOOL | FALSE | 回应上游OK |

### 7.9 VAR CONSTANT

| 变量 | 类型 | 值 | 说明 |
|------|------|---|------|
| ST_IDLE | INT | 0 | 空闲状态 |
| ST_READY | INT | 1 | 就绪状态 |
| ST_INFEED | INT | 2 | 入料状态 |
| ST_ALIGN | INT | 3 | 对齐状态 |
| ST_PROCESSING | INT | 4 | 加工中状态 |
| ST_DISCHARGE | INT | 5 | 出料状态 |
| ST_COMPLETE | INT | 6 | 完成状态 |
| ST_PAUSE | INT | 7 | 暂停状态 |
| ST_FAULT | INT | 8 | 停止/故障状态 |
| MODE_NORMAL | INT | 0 | 正常模式(A侧入料口/B侧出料口) |
| MODE_B_DUAL | INT | 1 | B侧双向模式(入料和出料均走B侧) |
| MODE_A_DUAL | INT | 2 | A侧双向模式(入料和出料均走A侧) |

## 8. 关联文档

| 文档 | 路径 | 版本 |
|------|------|:----:|
| IFC | 接口文档_IFC-FB1014-StationConveyor-V6.0.0.md | V6.0.0 |
| V5.0.0 DSN | 详细设计说明书_DSN-FB1014-StationConveyor-V5.0.0.md | V5.0.0 |
| FB_1011 | actuator/FB_1011_CylinderControl.scl | V8.0.0 |
| FB_1012 | actuator/FB_1012_ConveyorDrive.scl | - |
| FB_TON | timer/FB_TON.scl | - |
| LSP-905 | 905_SCL编程规范_LSP-V1.0.2.md | V1.0.2 |
| LSP-904 | 904_SCL注释规范_LSP-V1.2.0.md | V1.2.0 |
| LSP-903 | 903_定时器使用规范_LSP-V1.0.0.md | V1.0.0 |
| LSP-906 | 906_错误预防规则_LSP-V1.0.0.md | V1.0.0 |