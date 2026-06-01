---
spec_id: PFL-FB1014
version: V6.0.0
domain: plc
lifecycle: stable
---

# 工艺流程 FB_1014_StationConveyor

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1014 工站输送机工艺流程 |
| **文档版本** | V6.0.0 |
| **关联源码** | actuator/FB_1014_StationConveyor.scl |
| **关联PRD** | 需求文档_PRD-FB1014-StationConveyor-V6.0.0.md |
| **关联IFC** | 接口文档_IFC-FB1014-StationConveyor-V6.0.0.md |
| **关联DSN** | 详细设计说明书_DSN-FB1014-StationConveyor-V6.0.0.md |
| **编制日期** | 2026-05-31 |
| **编制人** | Trae |
| **遵循规范** | LSP-905 V1.0.2, LSP-904 V1.2.0, LSP-903 V1.0.0 |

### V6.0.0 变更摘要 (Breaking Change)

| 变更项 | V5.0.0 | V6.0.0 | 理由 |
|--------|:------:|:------:|------|
| 运行模式 | 无(固定B进A出) | **新增i_iMode接口(0=正常/1=B侧双向/2=A侧双向)** | 支持单口双向多模式 |
| 默认模式 | B进A出 | **B进B出(Mode=1)** | 实际工艺需求 |
| S2拍正作用 | 不参与入料 | **配合阻挡防止工件超位** | 修正工艺描述 |
| S2b拍正B侧 | 保持放下 | **升起(阻挡), 三面围住拍正** | 防止拍正时工件偏移 |
| S2b拍正后 | B侧保持放下 | **两侧下降(不干涉工件)** | 释放工件进入加工 |
| S3加工时 | 两侧抬起(阻挡) | **两侧下降(不干涉工件)** | 加工时气缸不干涉 |
| S3加工完成 | 直接出料 | **拍正伸出+阻挡升起后再出料** | 拍正提前就位 |
| S4出料方向 | A侧出(正转) | **B侧出(正转), Mode=1时** | B进B出模式 |
| S4出料A侧 | 放下(出料气缸) | **抬起(阻挡屏障), Mode=1时** | A侧屏障确保B向出料 |

### V5.0.0 变更摘要 (保留)

| 变更项 | V4.3.0 | V5.0.0 | 理由 |
|--------|:------:|:------:|------|
| 气缸控制 | io_stXxx.Extend/Retract (VAR_IN_OUT ST_Cylinder) | **q_bXxxExtend/Retract (扁平BOOL输出)** | 纯编排器, 解耦FB_1011实例 |
| 气缸状态 | io_stXxx.IsExtended/IsRetracted (ST_Cylinder内) | **i_bXxxIsExtended/IsRetracted (扁平BOOL输入)** | 从FB_1011 q_bIsExtended/Retracted读取 |
| 电机命令 | q_yFwdCmd/RevCmd/SlowCmd | **q_bFwdCmd/RevCmd/SlowCmd** | 命名对齐LSP-905前缀规范 |
| 握手信号 | q_yReplyUpstream/Downstream | **q_bReplyUpstream/Downstream** | 命名对齐LSP-905前缀规范 |
| 拍正取反 | FB_1014内部NOT q_yAlignSolenoid | **OB1中FB_1011 i_bExtendPolarity=TRUE** | 极性逻辑归属执行器层 |
| VFD报警 | 无 | **新增i_bVfdAlarm异常流程** | FB_1012故障时状态机响应 |
| ST_Cylinder | VAR_IN_OUT依赖 | **移除** | FB_1011 V9.0.0已扁平化 |

---

## 1. 工艺概述

### 1.1 工艺定义

工站输送机实现**多模式单口双向输送**工艺: 通过运行模式选择, 同一物理端口既作物料入口又作物料出口, 通过皮带正反转和气缸/传感器功能切换实现. 入料后增加**拍正对齐**步骤, 确保物料定位精度.

FB_1014为**纯编排器**: 输出命令到FB_1011(气缸)和FB_1012(电机), 读取状态反馈, 自身不直接驱动物理IO.

### 1.2 运行模式

| 模式值 | 模式名称 | 进料方向 | 出料方向 | 皮带进料 | 皮带出料 | 说明 |
|:------:|---------|---------|---------|---------|---------|------|
| 0 | 正常模式 | A进 | B出 | 正转 | 正转 | 传统A进B出 |
| 1 | B侧双向(默认) | B进 | B出 | 反转 | 正转 | B侧进出, A侧拍正+阻挡 |
| 2 | A侧双向(预留) | A进 | A出 | 正转 | 反转 | A侧进出, B侧阻挡 |

**模式切换**: 仅在ST_IDLE状态下生效, 运行中切换模式不改变当前工艺行为.

### 1.3 工艺特征

| 特征 | 说明 |
|------|------|
| 输送方式 | 多模式单口双向 (默认B进B出) |
| 定位方式 | 三光电去抖确认 (X420+X421+X422) |
| 阻挡方式 | 三气缸 (A侧阻挡+拍正, B侧阻挡, 功能随模式切换) |
| 拍正对齐 | 弹簧复位型拍正气缸, 入料时配合阻挡防超位, 拍正时B侧升起三面围住, 拍正后两侧下降不干涉 |
| 磁环到位确认 | 通过FB_1011 q_bIsExtended/IsRetracted反馈, 消除盲操 |
| 握手方式 | 上下游请求-应答握手 |
| 安全机制 | 停止>暂停>VFD报警>运行 四级优先 |

### 1.4 物料流向图

```
                    工站输送机
    ========================================
    |                                      |
    |  [X420]     [X421]     [X422]       |
    |  入料开始   位置1      位置2          |
    |  (靠近A侧)            (靠近B侧)      |
    |                                      |
    |  ======== 皮带 ========             |
    |   A→B = 正转    B→A = 反转          |
    |                                      |
    |  A侧:                                 |
    |  ┌──────────────────┐                |
    |  │ 阻挡气缸          │ ← 装在拍正气缸上 |
    |  │ q_bInfeedExtend   │   可独立升降    |
    |  │ q_bInfeedRetract  │                |
    |  ├──────────────────┤                |
    |  │ 拍正气缸(底座)     │ ← 弹簧复位型   |
    |  │ q_bAlignExtend    │   默认伸出     |
    |  │ q_bAlignRetract   │               |
    |  └──────────────────┘                |
    |                                      |
    |  B侧:                                 |
    |  [阻挡气缸]                            |
    |  q_bDischargeExtend                   |
    |  q_bDischargeRetract                  |
    ========================================

    Mode=1 (B侧双向, 默认):
         B侧 ←── 进料(反转) ── 上游设备
         B侧 ──→ 出料(正转) ──→ 下游设备

    Mode=0 (正常模式):
         A侧 ──→ 进料(正转) ──→ 上游设备
         B侧 ──→ 出料(正转) ──→ 下游设备
```

---

## 2. 正常工艺流程 (Mode=1: B侧双向, 默认模式)

### 2.1 完整工艺时序

```
步骤    状态           皮带    A侧阻挡气缸    A侧拍正气缸    B侧阻挡气缸    握手          说明
──────────────────────────────────────────────────────────────────────────────────────────────────────────────
S0     IDLE           停止    抬起(阻挡)      伸出(默认)     抬起(阻挡)     --            初始待机
S1     READY          停止    抬起(阻挡)      伸出(默认)     抬起(阻挡)     ReplyUp=OK    就绪等待
S2     INFEED         反转    抬起(阻挡)      伸出(阻挡超位) 放下(入料)     --            B侧反转进料
S2a    INFEED(慢速)   反转慢  抬起(阻挡)      伸出(阻挡超位) 放下(入料)     --            X420触发后减速
S2b    ALIGN          停止    抬起(阻挡)      伸出(拍正)     升起(阻挡)     --            三面围住拍正
S2b'   ALIGN完成      停止    下降(不干涉)    收回           下降(不干涉)   --            两侧释放工件
S3     PROCESSING     停止    下降(不干涉)    收回           下降(不干涉)   ReplyDn=OK    等待加工
S3'    加工完成准备    停止    升起(阻挡)      伸出(就绪)     下降(出料)     --            拍正就位+阻挡升起
S4     DISCHARGE      正转    抬起(阻挡)      伸出(就绪)     放下(出料)     --            B侧正转出料
S5     COMPLETE       停止    抬起(阻挡)      伸出(默认)     抬起(阻挡)     --            计数+复位
→ S0   IDLE           停止    抬起(阻挡)      伸出(默认)     抬起(阻挡)     --            循环结束
```

### 2.2 分步详细流程

#### S0: IDLE (初始待机)

```
触发: 上电/复位/循环结束
条件: 无
动作:
  - 皮带: 停止 (q_bFwdCmd=FALSE, q_bRevCmd=FALSE)
  - q_bInfeedExtend=FALSE, q_bInfeedRetract=TRUE → 抬起 = 阻挡
  - q_bAlignExtend=TRUE, q_bAlignRetract=FALSE → 伸出(默认就绪)
  - q_bDischargeExtend=FALSE, q_bDischargeRetract=TRUE → 抬起 = 阻挡
  - 握手: q_bReplyUpstream=FALSE, q_bReplyDownstream=FALSE
  - 确认标志: 全部清零
  - 定时器: 全部复位
出口: i_bAutoMode=TRUE AND i_bSelected=TRUE → S1
```

#### S1: READY (就绪等待)

```
触发: IDLE出口条件满足
前置: 传感器确认完成(m_bAllConfirmed=TRUE) AND m_bReplyUpOk=TRUE
动作:
  - 皮带: 停止
  - q_bInfeedExtend=FALSE, q_bInfeedRetract=TRUE → 抬起 = 阻挡
  - q_bAlignExtend=TRUE, q_bAlignRetract=FALSE → 伸出(就绪)
  - q_bDischargeExtend=FALSE, q_bDischargeRetract=TRUE → 抬起 = 阻挡
  - 握手: q_bReplyUpstream=TRUE (已在上游回应逻辑中置位)
出口: i_bUpstreamReq=TRUE AND m_bReplyUpOk=TRUE AND i_bSelected=TRUE → S2
```

#### S2: INFEED (反转进料)

```
触发: 上游请求+回应OK+工站选中
动作:
  - 皮带: 反转 (q_bRevCmd=TRUE)
  - q_bDischargeExtend=TRUE, q_bDischargeRetract=FALSE → 放下 = 允许B侧入料
  - q_bInfeedExtend=FALSE, q_bInfeedRetract=TRUE → 抬起 = A侧阻挡
  - q_bAlignExtend=TRUE, q_bAlignRetract=FALSE → 伸出 = 配合阻挡防止工件超位
  - q_bInfeedActive=TRUE
子步骤:
  S2a: 物料触达X420 → m_bStartConfirmed=TRUE → q_bSlowCmd=TRUE (慢速)
  S2b: 物料触达X421 → m_bPos1Confirmed=TRUE (入料检测1)
  S2c: 物料触达X422 → m_bPos2Confirmed=TRUE (入料检测2)
  S2d: 全部确认 AND 入料延时到 → 出口
出口: m_bAllConfirmed=TRUE AND tInfeedDelay.Q=TRUE → S2b(ALIGN)
```

**工艺要点**:
- X421/X422 在此阶段作为**入料检测光电**, 确认物料从B侧进入
- B侧阻挡气缸放下, 允许物料从B侧进入
- A侧拍正气缸伸出, **配合A侧阻挡气缸共同防止工件超位置运行**
- A侧阻挡气缸抬起, 阻止工件从A侧脱出

#### S2b: ALIGN (拍正对齐)

```
触发: 入料到位+入料延时到
动作(按序执行, 每步依赖FB_1011磁环到位确认):

  步骤1: 马达停止
    - q_bRevCmd=FALSE, q_bSlowCmd=FALSE

  步骤2: A侧拍正气缸保持伸出
    - q_bAlignExtend=TRUE, q_bAlignRetract=FALSE
    - 等待: i_bAlignIsExtended=TRUE (FB_1011磁环确认伸出到位)

  步骤3: B侧阻挡气缸升起(阻挡)
    - q_bDischargeExtend=FALSE, q_bDischargeRetract=TRUE → 升起 = 阻挡
    - 等待: i_bDischargeIsRetracted=TRUE (FB_1011磁环确认升起到位)
    - 工艺: B侧升起配合A侧拍正+阻挡, 三面围住工件

  步骤4: A侧阻挡气缸保持抬起
    - q_bInfeedExtend=FALSE, q_bInfeedRetract=TRUE

  步骤5: 启动对齐延时
    - m_bAlignDelayIn=TRUE
    - 等待: tAlignDelay.Q=TRUE

  步骤6: 拍正确认
    - 条件: i_bAlignIsExtended=TRUE AND i_bDischargeIsRetracted=TRUE AND tAlignDelay.Q=TRUE
    - 拍正气缸伸出到位 + B侧升起到位 + 延时到, 物料已对齐

  步骤7: A侧阻挡气缸下降(不干涉工件)
    - q_bInfeedExtend=TRUE, q_bInfeedRetract=FALSE → 下降
    - 等待: i_bInfeedIsExtended=TRUE (FB_1011磁环确认下降到位)

  步骤8: B侧阻挡气缸下降(不干涉工件)
    - q_bDischargeExtend=TRUE, q_bDischargeRetract=FALSE → 下降
    - 等待: i_bDischargeIsExtended=TRUE (FB_1011磁环确认下降到位)

  步骤9: A侧拍正气缸收回
    - q_bAlignExtend=FALSE, q_bAlignRetract=TRUE → 收回
    - 等待: i_bAlignIsRetracted=TRUE (FB_1011磁环确认收回到位)

  步骤10: 转入加工
    - q_bInfeedActive=FALSE
    - m_bAlignDelayIn=FALSE

出口: i_bAlignIsRetracted=TRUE → S3(PROCESSING)
```

**拍正对齐工艺要点**:
- 拍正气缸为弹簧复位型, 电磁阀极性取反: 伸出=断电(弹簧力), 收回=通电(电磁力)
- 极性取反由OB1中FB_1011实例的i_bExtendPolarity=TRUE实现, FB_1014无需手动NOT
- B侧阻挡气缸在拍正时升起, **三面围住工件(A侧拍正+A侧阻挡+B侧阻挡)**, 防止拍正时工件偏移
- 对齐顺序: 拍正伸出确认 → B侧升起到位 → 延时拍正确认 → A侧下降确认 → B侧下降确认 → 拍正收回确认
- 拍正结束后两侧阻挡气缸下降, **不干涉工件**, 工件靠皮带静止保持位置
- 所有气缸到位确认均来自FB_1011 q_bIsExtended/q_bIsRetracted, 消除盲操

#### S3: PROCESSING (加工等待)

```
触发: 拍正对齐完成(磁环全确认)
动作:
  - 皮带: 停止 (q_bRevCmd=FALSE)
  - q_bInfeedExtend=TRUE, q_bInfeedRetract=FALSE → 下降(不干涉工件)
  - q_bAlignExtend=FALSE, q_bAlignRetract=TRUE → 收回
  - q_bDischargeExtend=TRUE, q_bDischargeRetract=FALSE → 下降(不干涉工件)
  - 确认标志: 全部清零 (为出料检测做准备)
  - q_bIntAlarmMem=FALSE
  - q_bReplyDownstream=TRUE (加工完成后置位)
出口: i_bProcessDone=TRUE → S4
```

**工艺要点**:
- 两侧阻挡气缸均处于下降位置, **不干涉工件加工**
- 工件仅靠皮带静止保持位置

#### S4: DISCHARGE (正转出料)

```
触发: 外部加工完成信号(i_bProcessDone=TRUE)
前置动作(加工完成准备):
  步骤1: A侧拍正气缸伸出就位
    - q_bAlignExtend=TRUE, q_bAlignRetract=FALSE
    - 等待: i_bAlignIsExtended=TRUE (FB_1011磁环确认伸出到位)
  步骤2: A侧阻挡气缸升起(阻挡屏障)
    - q_bInfeedExtend=FALSE, q_bInfeedRetract=TRUE → 升起 = 阻挡
    - 等待: i_bInfeedIsRetracted=TRUE (FB_1011磁环确认升起到位)
  步骤3: B侧阻挡气缸下降(出料)
    - q_bDischargeExtend=TRUE, q_bDischargeRetract=FALSE → 下降 = 开放出料口

出料动作:
  - 皮带: 正转 (q_bFwdCmd=TRUE)
  - q_bInfeedExtend=FALSE, q_bInfeedRetract=TRUE → 抬起 = A侧阻挡屏障
  - q_bAlignExtend=TRUE, q_bAlignRetract=FALSE → 伸出(就绪, 不干涉出料)
  - q_bDischargeExtend=TRUE, q_bDischargeRetract=FALSE → 放下 = B侧出料
  - 慢速: i_bSlowMode=TRUE时q_bSlowCmd=TRUE
  - 出料延时定时器启动
出口: tDischargeDelay.Q=TRUE → S5
```

**工艺要点**:
- 加工完成后, 拍正气缸先伸出就位, A侧阻挡升起形成A侧屏障, 确保出料时工件只向B侧移动
- B侧阻挡气缸下降开放出料口, 工件从B侧出料
- 拍正气缸在出料期间保持伸出, 不干涉工件(工件向B侧移动远离拍正)

#### S5: COMPLETE (完成计数)

```
触发: 出料延时到
动作:
  - 皮带: 停止 (q_bFwdCmd=FALSE)
  - q_bInfeedExtend=FALSE, q_bInfeedRetract=TRUE → 抬起(阻挡)
  - q_bAlignExtend=TRUE, q_bAlignRetract=FALSE → 伸出(默认就绪)
  - q_bDischargeExtend=FALSE, q_bDischargeRetract=TRUE → 抬起(阻挡)
  - q_bReplyDownstream=FALSE
  - q_bInfeedActive=FALSE
  - q_dwProductionCount := q_dwProductionCount + 1
  - q_bIntAlarmMem=FALSE
  - tDischargeDelay复位
出口: 无条件 → S0 (下一循环)
```

---

## 3. 功能切换工艺表 (Mode=1: B侧双向)

### 3.1 入料阶段功能映射

```
物理位置              标准功能         入料时功能          动作
───────────────────────────────────────────────────────────────────────
X420               入料开始光电      入料开始光电         触发慢速(不变)
X421               位置1光电        入料检测光电1        确认物料进入
X422               位置2光电        入料检测光电2        精定位确认
q_bInfeedExtend    A侧阻挡气缸      A侧阻挡(抬起)        阻止工件从A侧脱出
q_bAlignExtend     A侧拍正气缸      阻挡超位(伸出)       配合阻挡防止工件超位
q_bDischargeExtend B侧阻挡气缸      入料放行(放下)       允许物料从B侧进入
```

### 3.2 对齐阶段功能映射

```
物理位置              标准功能         对齐时功能            动作
───────────────────────────────────────────────────────────────────────
q_bAlignExtend     A侧拍正气缸      拍正气缸              Extend确认→Retract收回
q_bInfeedExtend    A侧阻挡气缸      先抬起(阻挡)→后下降    拍正时阻挡→拍正后不干涉
q_bDischargeExtend B侧阻挡气缸      先升起(阻挡)→后下降    三面围住拍正→拍正后不干涉
```

### 3.3 出料阶段功能映射

```
物理位置              标准功能         出料时功能          动作
───────────────────────────────────────────────────────────────────────
X420               入料开始光电      (不参与)             --
X421               位置1光电        出料检测光电1        确认物料离开
X422               位置2光电        出料检测光电2        离开确认
q_bInfeedExtend    A侧阻挡气缸      A侧屏障(抬起)        阻止工件向A侧移动
q_bAlignExtend     A侧拍正气缸      就绪(伸出)           不干涉出料, 为下次拍正就位
q_bDischargeExtend B侧阻挡气缸      出料放行(放下)       允许物料从B侧离开
```

---

## 4. 异常工艺流程

### 4.1 停止流程 (最高优先级)

```
触发: i_bStop = TRUE (任意时刻)
动作:
  1. 立即清零所有驱动输出:
     - q_bFwdCmd = FALSE
     - q_bRevCmd = FALSE
     - q_bSlowCmd = FALSE
     - q_bReplyUpstream = FALSE
     - q_bReplyDownstream = FALSE
     - q_bInfeedActive = FALSE
  2. 全部气缸安全态(Mode=1):
     - q_bInfeedExtend = FALSE, q_bInfeedRetract = TRUE → 抬起(阻挡)
     - q_bAlignExtend = TRUE, q_bAlignRetract = FALSE → 伸出(默认)
     - q_bDischargeExtend = FALSE, q_bDischargeRetract = TRUE → 抬起(阻挡)
  3. 状态 → ST_FAULT (8)
  4. RETURN (跳过后续所有逻辑)

恢复: i_bStop = FALSE → ST_IDLE (0)
注意: 产量计数(q_dwProductionCount)保持不变
```

### 4.2 VFD报警流程 (次高优先级)

```
触发: i_bVfdAlarm = TRUE (FB_1012 q_bVfdAlarm输出, 任意运行时刻)
动作:
  1. 停止电机命令:
     - q_bFwdCmd = FALSE
     - q_bRevCmd = FALSE
     - q_bSlowCmd = FALSE
  2. 全部气缸安全态(Mode=1):
     - q_bInfeedExtend = FALSE, q_bInfeedRetract = TRUE → 抬起(阻挡)
     - q_bAlignExtend = TRUE, q_bAlignRetract = FALSE → 伸出(默认)
     - q_bDischargeExtend = FALSE, q_bDischargeRetract = TRUE → 抬起(阻挡)
  3. 清零握手和标志:
     - q_bReplyUpstream = FALSE
     - q_bReplyDownstream = FALSE
     - q_bInfeedActive = FALSE
  4. 状态 → ST_FAULT (8)
  5. RETURN

恢复: i_bVfdAlarm = FALSE AND i_bStop = FALSE → ST_IDLE (0)
说明:
  - FB_1012在i_bVfdFault=TRUE时已自动切断q_bFwdOut/q_bRevOut/q_bSlowOut
  - FB_1014的VFD报警处理是状态机层面的响应, 确保编排逻辑进入安全态
  - VFD报警与Stop共用ST_FAULT状态, 恢复条件需同时满足i_bVfdAlarm=FALSE和i_bStop=FALSE
```

### 4.3 暂停流程 (第三优先级)

```
触发: i_bPause = TRUE (任意时刻, 非停止且非VFD报警状态)
动作:
  1. 保存当前状态: m_iPauseState := iState
  2. 停止马达:
     - q_bFwdCmd = FALSE
     - q_bRevCmd = FALSE
     - q_bSlowCmd = FALSE
  3. 状态 → ST_PAUSE (7)
  4. RETURN

恢复: i_bPause = FALSE → iState := m_iPauseState
注意: 气缸状态在PAUSE态不主动改变, 保持暂停前状态
      若暂停发生在ALIGN态, 拍正气缸保持当前位置(伸出或收回)
```

### 4.4 下游中断报警流程

```
触发条件:
  i_xInfeedStart = TRUE      (物料在输送中)
  AND i_bAutoMode = TRUE     (自动模式)
  AND i_bDownstreamReq = FALSE (下游无请求)
  AND q_bInfeedActive = TRUE  (进料进行中)

动作:
  q_bIntAlarmMem = TRUE (置位中断报警)

清除条件:
  - i_bDownstreamReq = TRUE (下游请求恢复)
  - 进入ST_PROCESSING态 (加工中自动清除)
```

### 4.5 手动模式切换流程

```
触发: i_bAutoMode = FALSE (任意时刻)
动作:
  1. 清零所有驱动输出
  2. 清零确认标志 (m_bStartConfirmed/m_bPos1Confirmed/m_bPos2Confirmed)
  3. 清零 m_bReplyUpOk
  4. 复位所有定时器 (IN=FALSE)
  5. 气缸安全态(Mode=1):
     - q_bInfeedExtend = FALSE, q_bInfeedRetract = TRUE → 抬起(阻挡)
     - q_bAlignExtend = TRUE, q_bAlignRetract = FALSE → 伸出(默认)
     - q_bDischargeExtend = FALSE, q_bDischargeRetract = TRUE → 抬起(阻挡)
  6. 状态 → ST_IDLE (0)

恢复: i_bAutoMode = TRUE → 需重新从IDLE开始
```

---

## 5. 优先级决策链

```
每个PLC扫描周期的执行顺序:

  ┌─────────────────────────────┐
  │ 1. 读取当前状态 iState      │
  └──────────┬──────────────────┘
             │
  ┌──────────▼──────────────────┐
  │ 2. i_bStop = TRUE?          │──YES──→ 清零所有输出+气缸安全态 → ST_FAULT → RETURN
  └──────────┬──────────────────┘
             │ NO
  ┌──────────▼──────────────────┐
  │ 3. i_bVfdAlarm = TRUE?      │──YES──→ 停电机+气缸安全态 → ST_FAULT → RETURN
  └──────────┬──────────────────┘
             │ NO
  ┌──────────▼──────────────────┐
  │ 4. i_bPause = TRUE?         │──YES──→ 保存状态 → 停马达 → ST_PAUSE → RETURN
  └──────────┬──────────────────┘
             │ NO
  ┌──────────▼──────────────────┐
  │ 5. 传感器去抖处理            │
  └──────────┬──────────────────┘
             │
  ┌──────────▼──────────────────┐
  │ 6. i_bAutoMode = FALSE?     │──YES──→ 清零所有+气缸安全态 → ST_IDLE → RETURN
  └──────────┬──────────────────┘
             │ NO
  ┌──────────▼──────────────────┐
  │ 7. 中断报警检测              │
  └──────────┬──────────────────┘
             │
  ┌──────────▼──────────────────┐
  │ 8. 上游回应逻辑              │
  └──────────┬──────────────────┘
             │
  ┌──────────▼──────────────────┐
  │ 9. 状态机 CASE 执行          │
  └──────────┬──────────────────┘
             │
  ┌──────────▼──────────────────┐
  │ 10. 更新 q_iState           │
  └──────────┬──────────────────┘
             │
  ┌──────────▼──────────────────┐
  │ 11. 下游恢复清除报警         │
  └─────────────────────────────┘
```

---

## 6. 状态转换图

```
                    ┌─────────┐
                    │  IDLE   │<──────────────────────────────┐
                    │  (0)    │                                │
                    └────┬────┘                                │
                         │ AutoMode + Selected                 │
                         ▼                                     │
                    ┌─────────┐                                │
              ┌────│  READY   │────┐                           │
              │    │  (1)     │    │                           │
              │    └────┬────┘    │                           │
              │         │ UpstreamReq                         │
              │         │ + ReplyUpOk                         │
              │         │ + Selected                          │
              │         ▼                                     │
              │    ┌─────────┐                                │
              │    │ INFEED  │◄─── 暂停恢复                    │
              │    │  (2)    │                                │
              │    └────┬────┘                                │
              │         │ AllConfirmed                        │
              │         │ + InfeedDelay                       │
              │         ▼                                     │
              │    ┌─────────┐                                │
              │    │  ALIGN  │◄─── 暂停恢复                    │
              │    │  (3)    │                                │
              │    └────┬────┘                                │
              │         │ FB_1011到位确认                      │
              │         │ (拍正伸出→B侧升起→延时→              │
              │         │  A侧下降→B侧下降→拍正收回)           │
              │         ▼                                     │
              │    ┌─────────┐                                │
              │    │PROCESSING│                               │
              │    │  (4)     │── ProcessDone ──┐              │
              │    └─────────┘                  │              │
              │                                 │ 拍正伸出+    │
              │                                 │ 阻挡升起     │
              │                                 ▼              │
              │                           ┌─────────┐         │
              │                           │DISCHARGE│◄── 暂停恢复
              │                           │  (5)    │         │
              │                           └────┬────┘         │
              │                                │ DischargeDelay│
              │                                ▼              │
              │                           ┌─────────┐         │
              │                           │COMPLETE │─────────┘
              │                           │  (6)    │  计数+1
              │                           └─────────┘
              │
              │  (任意状态)
              ├── i_bStop ──────→ ┌─────────┐
              │                   │  FAULT  │── Stop取消 ──→ IDLE
              │                   │  (8)    │
              │                   └─────────┘
              │                        ▲
              │  (运行状态)              │
              └── i_bVfdAlarm ──→ ┌────┘
                                  (VFD报警取消+Stop取消 → IDLE)

              │  (任意状态, 非Stop非VFD报警)
              └── i_bPause ──→ ┌─────────┐
                              │  PAUSE  │── Pause取消 ──→ 恢复原状态
                              │  (7)    │
                              └─────────┘
```

---

## 7. 关键时序参数

| 参数 | 变量 | 默认值 | 范围 | 说明 |
|------|------|--------|------|------|
| 光电去抖延时 | i_dDebounceMs | 200 ms | 50-2000 | 防止传感器误触发 |
| 入料到位延时 | i_dInfeedDelayMs | 1000 ms | 100-10000 | 物料到位后稳定等待 |
| 出料完成延时 | i_dDischargeDelayMs | 1000 ms | 100-10000 | 出料过程等待 |
| 拍正对齐延时 | i_dAlignDelayMs | 500 ms | 100-5000 | 拍正稳定等待, 确保物料对齐 |

### 7.1 入料时序 (Mode=1)

```
时间 ──────────────────────────────────────────────────>

X420(入料开始)  ──────╔════════════════════════╗
                      ║ 物料通过                ║

X421(入料检测1)  ────────────╔═════════════════════╗
                             ║ 物料通过             ║

X422(入料检测2)  ─────────────────────╔══════════════╗
                                      ║ 物料通过      ║

q_bSlowCmd      ──────────┐
                          └────────────────────── (慢速ON)

q_bRevCmd       ───────────────────────────────────── (反转ON)
                                                 │
InfeedDelay     ─────────────────────────────┐   │
                                               └───┘ (延时到)
                                                    │
状态切换         INFEED ──────────────────── ALIGN
```

### 7.2 对齐时序 (Mode=1)

```
时间 ──────────────────────────────────────────────────────────────────────────────>

q_bRevCmd       ─┐ (ALIGN开始即停止)
                 └────────────────────────────────────────────────────────────── (停止)

q_bAlignExtend  ════════════════════════════════════════════════════════════════
=TRUE           ║ 伸出(拍正)                                              (保持到收回)

i_bAlignIs      ─────────────────────────╔═════════════════════════════════════
Extended=TRUE                            ║到位(保持)

q_bDischargeRetract    ──────┐     ┌──────────────────────────────────────────
=TRUE(升起)                   │     │
                              └─────┘ (B侧升起=阻挡)

i_bDischargeIs                  ╔════╗
Retracted=TRUE                  ║到位║

tAlignDelay     ────────────────────────┐
                                        └───┘ (延时到)

q_bInfeedExtend                                ┌──────────────────────────────
=TRUE(下降)                                    │ 下降(不干涉工件)

i_bInfeedIs                                    ════════╔══════════════════════
Extended=TRUE                                          ║下降到位

q_bDischargeExtend                                            ┌──────────────
=TRUE(下降)                                                    │ 下降(不干涉)

i_bDischargeIs                                                ╔══════════════
Extended=TRUE                                                 ║下降到位

q_bAlignRetract                                                             ┌────
=TRUE                                                                        │收回

i_bAlignIs                                                                  ╔════
Retracted=TRUE                                                              ║到位

状态切换         ALIGN ─────────────────────────────────────────────── PROCESSING
```

### 7.3 出料时序 (Mode=1)

```
时间 ──────────────────────────────────────────────────────────────>

i_bProcessDone  ───────────────────────╔════════════╗
                                       ║ 加工完成    ║

q_bAlignExtend                  ┌──────────────────────────────────────
=TRUE(伸出就位)                  │ 伸出到位

i_bAlignIs                      ╔═════════════════════════════════════
Extended=TRUE                   ║到位(保持)

q_bInfeedRetract                        ┌──────────────────────────────
=TRUE(升起)                              │ 升起=阻挡屏障

i_bInfeedIs                              ╔════════════════════════════
Retracted=TRUE                           ║到位(保持)

q_bDischargeExtend                               ┌──────────────────────
=TRUE(放下)                                       │ 放下=出料

q_bFwdCmd                                         ────────────────────── (正转ON)
                                                                        │
DischargeDelay  ──────────────────────────────────────────────┐       │
                                                               └───────┘ (延时到)
                                                                        │
状态切换         PROCESSING ────── DISCHARGE ──────────────── COMPLETE ── IDLE
```

---

## 8. 气缸动作工艺表 (Mode=1: B侧双向)

| 工艺阶段 | q_bInfeedExtend | q_bAlignExtend | q_bDischargeExtend | 物理效果 |
|---------|:-:|:-:|:-:|------|
| IDLE | FALSE(抬起) | TRUE(伸出) | FALSE(抬起) | A侧阻挡+拍正就绪, B侧阻挡 |
| READY | FALSE(抬起) | TRUE(伸出) | FALSE(抬起) | A侧阻挡+拍正就绪, B侧阻挡 |
| INFEED | FALSE(抬起) | TRUE(伸出) | **TRUE(放下)** | B侧放行入料, A侧阻挡+拍正防超位 |
| ALIGN(拍正) | FALSE(抬起) | TRUE(伸出) | **FALSE(升起)** | 三面围住: A侧拍正+阻挡, B侧升起 |
| ALIGN(释放) | **TRUE(下降)** | TRUE→FALSE(收回) | **TRUE(下降)** | 两侧下降不干涉, 拍正收回 |
| PROCESSING | TRUE(下降) | FALSE(收回) | TRUE(下降) | 两侧不干涉工件, 工件靠静止保持 |
| DISCHARGE | FALSE(抬起) | TRUE(伸出) | TRUE(放下) | A侧屏障+拍正就绪, B侧出料 |
| COMPLETE | FALSE(抬起) | TRUE(伸出) | FALSE(抬起) | A侧阻挡+拍正就绪, B侧阻挡 |
| PAUSE | 保持 | 保持 | 保持 | 保持暂停前气缸状态 |
| FAULT | FALSE(抬起) | TRUE(伸出) | FALSE(抬起) | A侧阻挡+拍正就绪, B侧阻挡 |

**拍正气缸极性取反说明**:

拍正气缸为弹簧复位型, 伸出=断电(弹簧力), 收回=通电(电磁力). 极性取反由OB1中FB_1011实例配置实现:

| OB1配置 | 值 | 说明 |
|---------|-----|------|
| FB_1011 i_bExtendPolarity | TRUE | 启用极性取反 |

FB_1011内部极性取反逻辑:

| FB_1014命令 | q_bAlignExtend | q_bAlignRetract | FB_1011 i_bExtend | FB_1011 i_bRetract | FB_1011 q_bSolenoid | 物理动作 |
|:-----------:|:--------------:|:---------------:|:-----------------:|:------------------:|:-------------------:|----------|
| 伸出 | TRUE | FALSE | TRUE | FALSE | **FALSE**(断电) | 弹簧伸出(默认) |
| 收回 | FALSE | TRUE | FALSE | TRUE | **TRUE**(通电) | 电磁力收回 |

FB_1014只需输出q_bAlignExtend/q_bAlignRetract, 无需手动NOT. FB_1011在i_bExtendPolarity=TRUE时自动完成:
- 伸出命令(i_bExtend=TRUE) → q_bSolenoid = NOT i_bExtendPolarity = FALSE → 断电 → 弹簧伸出
- 收回命令(i_bRetract=TRUE) → q_bSolenoid = i_bExtendPolarity = TRUE → 通电 → 电磁收回
- 传感器映射: i_bExtendedPos(物理伸出位) → q_bIsRetracted(逻辑), i_bRetractedPos(物理收回位) → q_bIsExtended(逻辑)

---

## 9. 关联文档

| 文档 | 路径 | 版本 |
|------|------|:----:|
| PRD | 需求文档_PRD-FB1014-StationConveyor-V6.0.0.md | V6.0.0 |
| IFC | 接口文档_IFC-FB1014-StationConveyor-V6.0.0.md | V6.0.0 |
| DSN | 详细设计说明书_DSN-FB1014-StationConveyor-V6.0.0.md | V6.0.0 |
| FB_1011 | actuator/FB_1011_CylinderControl.scl | V9.0.0 |
| FB_1012_ConveyorMotor | actuator/FB_1012_ConveyorMotor.scl | V9.0.0 |
| LSP-905 | 905_SCL编程规范_LSP-V1.0.2.md | V1.0.2 |
| LSP-904 | 904_SCL注释规范_LSP-V1.2.0.md | V1.2.0 |
| LSP-903 | 903_定时器使用规范_LSP-V1.0.0.md | V1.0.0 |
