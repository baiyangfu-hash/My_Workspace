# 详细设计说明书 FB_1020_EquipmentHandshake

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1020 设备通讯握手详细设计 |
| **文档版本** | V1.1.0 |
| **关联源码** | communication/FB_1020_EquipmentHandshake.scl |
| **关联IFC** | 接口文档_IFC-FB1020-EquipmentHandshake-V1.1.0.md |
| **编制日期** | 2026-05-29 |
| **编制人** | Trae |
| **遵循规范** | LSP-905 V1.0.1, LSP-904 V1.2.0, LSP-903 V1.0.0 |

## 1. 设计原则

1. **纯协议逻辑, 传输层无关**: FB只管理握手时序和状态转换, 不依赖任何具体通讯介质(ModbusTCP/Profinet/OPC-UA/硬线IO等). 信号通过VAR_IN_OUT结构体交换, 映射由调用方负责.
2. **双通道独立状态机**: 上游(UP-Stream)和下游(DOWN-Stream)各自5态状态机, 互不干扰, 可同时运行.
3. **参数化时序**: 延迟/心跳/超时/脉冲宽度全部通过VAR_INPUT可配置, 默认值来自协议定义(各設備交握-5.20.xlsx).
4. **心跳翻转检测**: 本机生成心跳方波, 同时监视对方心跳翻转. 超时未翻转则判定通讯中断.
5. **产品数据锁存**: MoveBusy上升沿一次性锁存产品数据(GlassID/Speed/Quality/Grade)到写区, 避免传输过程中数据被覆盖.
6. **故障冻结+手动恢复**: FAULT态冻结所有输出, 需手动Reset或心跳恢复才能回到IDLE.
7. **完成脉冲输出**: Complete状态输出固定宽度脉冲(默认500ms), 脉冲结束后自动回IDLE.
8. **LSP-904注释合规**: 变量行内注释使用`//`, 功能块头部和逻辑分支说明使用`(* *)`, 禁止嵌套注释, 禁止中文标点, 禁止注释内容含`(*`或`*)`标记字符串.

## 2. 状态定义表

### 2.1 上游通道状态机 (UpStream_SM)

| 状态值 | 名称 | 入口条件 | 入口动作 | 出口条件 | 出口目标 |
|:------:|------|----------|----------|----------|----------|
| 0 | IDLE | 初始/复位/完成脉冲结束 | 清除Write.RequestOut/MoveBusy/Complete | i_bRequestOut上升沿 AND q_bUpReady | REQ_OUT |
| 1 | REQ_OUT | IDLE出口条件满足 | Write.RequestOut:=TRUE; 启动tReqOutDelay | tReqOutDelay.Q | MOVE_BUSY |
| 2 | MOVE_BUSY | tReqOutDelay.Q | Write.MoveBusy:=TRUE; Write.RequestOut:=FALSE; 锁存产品数据 | Read.Complete上升沿 | COMPLETE |
| 3 | COMPLETE | Read.Complete上升沿 | Write.MoveBusy:=FALSE; q_bUpComplete:=TRUE; 启动脉冲定时器 | tCompletePulseUp.Q | IDLE |
| 4 | FAULT | 任何态HbTimeout | CommFault:=TRUE; 冻结输出 | i_bReset OR (NOT HbTimeout) | IDLE |

### 2.2 下游通道状态机 (DownStream_SM)

| 状态值 | 名称 | 入口条件 | 入口动作 | 出口条件 | 出口目标 |
|:------:|------|----------|----------|----------|----------|
| 0 | IDLE | 初始/复位/完成脉冲结束 | 清除Write.RequestIn/DsMoveBusy/DsComplete | Read.RequestIn上升沿 AND i_bAllowDischarge AND q_bDownReady | REQ_IN |
| 1 | REQ_IN | IDLE出口条件满足 | 启动tReqInDelay | tReqInDelay.Q | MOVE_BUSY |
| 2 | MOVE_BUSY | tReqInDelay.Q | Write.DsMoveBusy:=TRUE; 锁存产品数据 | i_bTransportDone上升沿 OR Read.DsComplete上升沿 | COMPLETE |
| 3 | COMPLETE | 完成条件满足 | Write.DsMoveBusy:=FALSE; Write.DsComplete:=TRUE; q_bDownComplete:=TRUE; 启动脉冲定时器 | tCompletePulseDs.Q | IDLE |
| 4 | FAULT | 任何态HbTimeout | CommFault:=TRUE; 冻结输出 | i_bReset OR (NOT HbTimeout) | IDLE |

### 2.3 状态码编码 (q_wStatusCode)

| 位段 | 含义 | 编码 |
|------|------|------|
| 高字节(Bits 15..8) | 上游状态 | 0=IDLE, 1=REQ_OUT, 2=MOVE_BUSY, 3=COMPLETE, 4=FAULT |
| 低字节(Bits 7..0) | 下游状态 | 0=IDLE, 1=REQ_IN, 2=MOVE_BUSY, 3=COMPLETE, 4=FAULT |

## 3. 详细伪代码

### 3.0 前置处理

```pascal
(* ==================== 使能关闭处理 ==================== *)
IF NOT i_bEnable THEN
    io_stUpStream.Write := ST_HandshakeBits#();
    io_stDownStream.Write := ST_HandshakeBits#();
    q_bUpReady := FALSE;  q_bDownReady := FALSE;
    q_bUpComplete := FALSE;  q_bDownComplete := FALSE;
    q_bAlarm := FALSE;  q_wStatusCode := 16#0000;
    q_iUpState := 0;  q_iDownState := 0;
    iUpState := 0;  iDownState := 0;
    RETURN;
END_IF;

q_iUpState := iUpState;
q_iDownState := iDownState;
```

### 3.1 心跳生成

```pascal
(* 方波发生器: 周期=i_dHbToggleMs, 占空比50% *)
tHbToggle(IN := NOT tHbToggle.Q, PT := i_dHbToggleMs,
          Q => tHbToggle.Q, ET => tHbToggle.ET);

(* 上游通道: 写入本机送料心跳 *)
io_stUpStream.Write.Heartbeat := tHbToggle.Q;

(* 下游通道: 写入本机接料心跳 *)
io_stDownStream.Write.RcvHeartbeat := tHbToggle.Q;
```

### 3.2 心跳超时监视

```pascal
(* 上游通道: 检测对方心跳翻转 *)
(* 原理: 对方会在Heartbeat和RcvHeartbeat之间交替翻转 *)
(*       如果两者持续相等超过i_dHbTimeoutMs, 判定通讯中断 *)
IF io_stUpStream.Read.Heartbeat <> io_stUpStream.Read.RcvHeartbeat THEN
    (* 对方有翻转, 重置超时 *)
    tHbUpTimeout(IN := FALSE, PT := i_dHbTimeoutMs, Q => ..., ET => ...);
    tHbUpTimeout.IN := TRUE;
    io_stUpStream.HbTimeout := FALSE;
ELSE
    IF NOT tHbUpTimeout.IN THEN
        tHbUpTimeout(IN := TRUE, PT := i_dHbTimeoutMs, Q => ..., ET => ...);
    END_IF;
    IF tHbUpTimeout.Q THEN
        io_stUpStream.HbTimeout := TRUE;
    END_IF;
END_IF;

(* 下游通道: 同理 *)
IF io_stDownStream.Read.RcvHeartbeat <> io_stDownStream.Read.Heartbeat THEN
    tHbDsTimeout(IN := FALSE, ...);
    tHbDsTimeout.IN := TRUE;
    io_stDownStream.HbTimeout := FALSE;
ELSE
    ... (* 同上游 *)
END_IF;
```

### 3.3 就绪综合信号

```pascal
(* 就绪 = 对方Ready AND 无通讯故障 AND 无心跳超时 *)
q_bUpReady := io_stUpStream.Read.Ready
              AND (NOT io_stUpStream.CommFault)
              AND (NOT io_stUpStream.HbTimeout);

q_bDownReady := io_stDownStream.Read.DsReady
               AND (NOT io_stDownStream.CommFault)
               AND (NOT io_stDownStream.HbTimeout);
```

### 3.4 边沿检测

```pascal
(* 7路边沿检测, 使用FB_R_TRIG + 上周期值记忆 *)
rTrigRequestOut  := R_TRIG(i_bRequestOut);       (* 上游要料请求 *)
rTrigRequestIn   := R_TRIG(Read.RequestIn);       (* 下游进料请求 *)
rTrigUpComplete  := R_TRIG(Read.Complete);        (* 上游完成确认 *)
rTrigDsComplete  := R_TRIG(Read.DsComplete);      (* 下游完成确认 *)
rTrigMoveBusyUp  := R_TRIG(Write.MoveBusy);       (* 上游MoveBusy写入沿 *)
rTrigMoveBusyDs  := R_TRIG(Write.DsMoveBusy);     (* 下游MoveBusy写入沿 *)
rTrigTransport   := R_TRIG(i_bTransportDone);     (* 物理搬运完成 *)
```

### 3.5 上游状态机

```pascal
CASE iUpState OF
    0: (* IDLE *)
        Write.RequestOut := FALSE;
        Write.MoveBusy := FALSE;
        Write.Complete := FALSE;
        tReqOutDelay.IN := FALSE;
        tCompletePulseUp.IN := FALSE;

        IF rTrigRequestOut.Q AND q_bUpReady THEN
            iUpState := 1;
        END_IF;
        IF HbTimeout THEN iUpState := 4; CommFault := TRUE; END_IF;

    1: (* REQ_OUT *)
        Write.RequestOut := TRUE;
        tReqOutDelay(IN := TRUE, PT := i_dReqDelayMs, ...);

        IF tReqOutDelay.Q THEN
            iUpState := 2;
            tReqOutDelay.IN := FALSE;
        END_IF;
        IF i_bReset OR HbTimeout THEN
            iUpState := 0;
            Write.RequestOut := FALSE;
            tReqOutDelay.IN := FALSE;
            IF HbTimeout THEN CommFault := TRUE; END_IF;
        END_IF;

    2: (* MOVE_BUSY_UP *)
        Write.MoveBusy := TRUE;
        Write.RequestOut := FALSE;

        (* MoveBusy上升沿: 锁存产品数据 *)
        IF rTrigMoveBusyUp.Q THEN
            WriteGlassID := i_stProductData.GlassID;
            WriteSpeed   := i_stProductData.TransferSpeed;
            WriteQuality := i_stProductData.Quality;
            WriteGrade   := i_stProductData.Grade;
        END_IF;

        IF rTrigUpComplete.Q THEN iUpState := 3; END_IF;
        IF i_bReset OR HbTimeout THEN
            iUpState := 0;
            Write.MoveBusy := FALSE;
            IF HbTimeout THEN CommFault := TRUE; END_IF;
        END_IF;

    3: (* COMPLETE_UP *)
        Write.MoveBusy := FALSE;
        q_bUpComplete := TRUE;
        tCompletePulseUp(IN := TRUE, PT := i_dCompleteMs, ...);

        IF tCompletePulseUp.Q THEN
            q_bUpComplete := FALSE;
            tCompletePulseUp.IN := FALSE;
            iUpState := 0;
        END_IF;

    4: (* FAULT_UP *)
        CommFault := TRUE;
        IF i_bReset OR (NOT HbTimeout) THEN
            CommFault := FALSE;
            Write.RequestOut := FALSE;
            Write.MoveBusy := FALSE;
            Write.Complete := FALSE;
            iUpState := 0;
        END_IF;
ELSE
    iUpState := 0;
END_CASE;
```

### 3.6 下游状态机

```pascal
CASE iDownState OF
    0: (* IDLE *)
        Write.RequestIn := FALSE;
        Write.DsMoveBusy := FALSE;
        Write.DsComplete := FALSE;
        tReqInDelay.IN := FALSE;
        tCompletePulseDs.IN := FALSE;

        IF rTrigRequestIn.Q AND i_bAllowDischarge AND q_bDownReady THEN
            iDownState := 1;
        END_IF;
        IF HbTimeout THEN iDownState := 4; CommFault := TRUE; END_IF;

    1: (* REQ_IN *)
        tReqInDelay(IN := TRUE, PT := i_dReqDelayMs, ...);

        IF tReqInDelay.Q THEN
            iDownState := 2;
            tReqInDelay.IN := FALSE;
        END_IF;
        IF i_bReset OR HbTimeout OR (NOT Read.RequestIn) THEN
            iDownState := 0;
            tReqInDelay.IN := FALSE;
            IF HbTimeout THEN CommFault := TRUE; END_IF;
        END_IF;

    2: (* MOVE_BUSY_DS *)
        Write.DsMoveBusy := TRUE;

        (* DsMoveBusy上升沿: 锁存产品数据 *)
        IF rTrigMoveBusyDs.Q THEN
            WriteGlassID := i_stProductData.GlassID;
            WriteSpeed   := i_stProductData.TransferSpeed;
            WriteQuality := i_stProductData.Quality;
            WriteGrade   := i_stProductData.Grade;
        END_IF;

        (* 完成条件: 物理传输完成 OR 对方确认完成 *)
        IF rTrigTransport.Q OR rTrigDsComplete.Q THEN
            iDownState := 3;
        END_IF;
        IF i_bReset OR HbTimeout THEN
            iDownState := 0;
            Write.DsMoveBusy := FALSE;
            IF HbTimeout THEN CommFault := TRUE; END_IF;
        END_IF;

    3: (* COMPLETE_DS *)
        Write.DsMoveBusy := FALSE;
        Write.DsComplete := TRUE;
        q_bDownComplete := TRUE;
        tCompletePulseDs(IN := TRUE, PT := i_dCompleteMs, ...);

        IF tCompletePulseDs.Q THEN
            q_bDownComplete := FALSE;
            Write.DsComplete := FALSE;
            tCompletePulseDs.IN := FALSE;
            iDownState := 0;
        END_IF;

    4: (* FAULT_DS *)
        CommFault := TRUE;
        IF i_bReset OR (NOT HbTimeout) THEN
            CommFault := FALSE;
            Write.RequestIn := FALSE;
            Write.DsMoveBusy := FALSE;
            Write.DsComplete := FALSE;
            iDownState := 0;
        END_IF;
ELSE
    iDownState := 0;
END_CASE;
```

### 3.7 后处理

```pascal
(* 综合报警 *)
q_bAlarm := io_stUpStream.CommFault OR io_stDownStream.CommFault
           OR io_stUpStream.HbTimeout OR io_stDownStream.HbTimeout;

(* 状态码 *)
q_wStatusCode := SHL(INT_TO_WORD(iUpState), 8) OR INT_TO_WORD(iDownState);
```

## 4. 时序图

### 4.1 上游送出完整流程

```
时间轴 →

i_bRequestOut   ─────┐
                      └────────────────────────────────────── (保持)

Up.Write.RequestOut   ───────────┐
                                  └────────────────────────── (1sec后清除)

tReqOutDelay                     ┌── 1000ms ──┐
                                              └→ Q

Up.Write.MoveBusy                             ────────────┐
                                                          └── (到Complete)

Up.Write.RequestOut                            ─────────── (FALSE)

产品数据锁存                                   ┌┐ (MoveBusy上升沿)
                                              └┘

Up.Read.Complete                                            ─────┐
                                                                 └── (对方确认)

q_bUpComplete                                                    ─────┐
                                                                      └── 500ms脉冲

Up.Write.MoveBusy                                                 ───── (FALSE)

iUpState         0(IDLE) → 1(REQ_OUT) → 2(MOVE_BUSY) → 3(COMPLETE) → 0(IDLE)
```

### 4.2 下游接收完整流程

```
时间轴 →

Down.Read.RequestIn  ─────┐
                         └────────────────────────────────── (保持)

tReqInDelay              ┌── 1000ms ──┐
                                       └→ Q

Down.Write.DsMoveBusy                  ────────────┐
                                                    └── (到Complete)

产品数据锁存                           ┌┐ (DsMoveBusy上升沿)
                                      └┘

i_bTransportDone                                     ─────┐
                                                           └── (输送到位)

q_bDownComplete                                           ─────┐
                                                                └── 500ms脉冲

Down.Write.DsComplete                                       ─────┐
                                                                  └── 500ms

iDownState        0(IDLE) → 1(REQ_IN) → 2(MOVE_BUSY) → 3(COMPLETE) → 0(IDLE)
```

### 4.3 心跳超时场景

```
时间轴 →

对方Heartbeat     ──┐ ┌─┐ ┌─┐ ┌─┐          (停止翻转)
                    └─┘ └─┘ └─┘ └─┘

tHbUpTimeout                              ┌── 3000ms ──┐
                                                        └→ Q

HbTimeout                                               ─────────── TRUE

CommFault                                               ─────────── TRUE

q_bAlarm                                                ─────────── TRUE

iUpState           0/1/2/3                               → 4(FAULT)
```

### 4.4 复位恢复场景

```
时间轴 →

i_bReset          ───────────────────────────┐
                                            └── (脉冲)

CommFault         ───────────────────────────┐
                                            └── FALSE

HbTimeout         ───────────────────────────┐
                                            └── FALSE

iUpState          4(FAULT)                    → 0(IDLE)

Write信号          ─────────────────────────── 全部FALSE
```

## 5. 报警/诊断映射表

| 诊断信号 | 类型 | 触发条件 | 恢复方式 |
|----------|------|----------|----------|
| io_stUpStream.HbTimeout | BOOL | 上游心跳超时(i_dHbTimeoutMs内无翻转) | 心跳恢复自动清除 |
| io_stDownStream.HbTimeout | BOOL | 下游心跳超时 | 心跳恢复自动清除 |
| io_stUpStream.CommFault | BOOL | HbTimeout触发进入FAULT态 | i_bReset 或 心跳恢复 |
| io_stDownStream.CommFault | BOOL | HbTimeout触发进入FAULT态 | i_bReset 或 心跳恢复 |
| q_bAlarm | BOOL | 任一CommFault或HbTimeout | 所有故障源清除 |

## 6. 变量定义详情

### 6.1 VAR (内部变量)

| 变量 | 类型 | 初始值 | 说明 |
|------|------|:------:|------|
| iUpState | INT | 0 | 上游状态机当前状态(0~4) |
| iDownState | INT | 0 | 下游状态机当前状态(0~4) |
| tReqOutDelay | FB_TON | -- | RequestOut->MoveBusy延迟定时器 |
| tReqInDelay | FB_TON | -- | RequestIn->响应延迟定时器 |
| tHbUpTimeout | FB_TON | -- | 上游心跳超时定时器 |
| tHbDsTimeout | FB_TON | -- | 下游心跳超时定时器 |
| tHbToggle | FB_TON | -- | 心跳翻转周期定时器 |
| tCompletePulseUp | FB_TON | -- | 上游完成脉冲宽度定时器 |
| tCompletePulseDs | FB_TON | -- | 下游完成脉冲宽度定时器 |
| rTrigRequestOut | FB_R_TRIG | -- | i_bRequestOut上升沿 |
| rTrigRequestIn | FB_R_TRIG | -- | Read.RequestIn上升沿 |
| rTrigUpComplete | FB_R_TRIG | -- | Read.Complete上升沿 |
| rTrigDsComplete | FB_R_TRIG | -- | Read.DsComplete上升沿 |
| rTrigMoveBusyUp | FB_R_TRIG | -- | Write.MoveBusy上升沿 |
| rTrigMoveBusyDs | FB_R_TRIG | -- | Write.DsMoveBusy上升沿 |
| rTrigTransport | FB_R_TRIG | -- | i_bTransportDone上升沿 |
| bLastRequestOut | BOOL | FALSE | 上周期i_bRequestOut值 |
| bLastRequestIn | BOOL | FALSE | 上周期Read.RequestIn值 |
| bLastUpComplete | BOOL | FALSE | 上周期Read.Complete值 |
| bLastDsComplete | BOOL | FALSE | 上周期Read.DsComplete值 |
| bLastMoveBusyUpW | BOOL | FALSE | 上周期Write.MoveBusy值 |
| bLastMoveBusyDsW | BOOL | FALSE | 上周期Write.DsMoveBusy值 |
| bLastTransport | BOOL | FALSE | 上周期i_bTransportDone值 |

### 6.2 定时器参数汇总

| 定时器 | PT来源 | 默认值(ms) | 用途 |
|--------|--------|:----------:|------|
| tReqOutDelay | i_dReqDelayMs | 1000 | 请求->搬运延迟 |
| tReqInDelay | i_dReqDelayMs | 1000 | 请求->响应延迟 |
| tHbToggle | i_dHbToggleMs | 500 | 心跳翻转周期 |
| tHbUpTimeout | i_dHbTimeoutMs | 3000 | 上游心跳超时 |
| tHbDsTimeout | i_dHbTimeoutMs | 3000 | 下游心跳超时 |
| tCompletePulseUp | i_dCompleteMs | 500 | 上游完成脉冲宽度 |
| tCompletePulseDs | i_dCompleteMs | 500 | 下游完成脉冲宽度 |

## 7. VAR_IN_OUT 结构体使用约定

### 7.1 ST_HandshakeCh 字段读写权限矩阵

| 字段 | IDLE | REQ_OUT | MOVE_BUSY | COMPLETE | FAULT | 说明 |
|------|:----:|:-------:|:---------:|:--------:|:-----:|------|
| Write.Heartbeat | W | W | W | W | W | 持续写入心跳方波 |
| Write.RequestOut | W(清) | W(TRUE) | W(FALSE) | - | - | 上游送料请求 |
| Write.MoveBusy | W(清) | - | W(TRUE) | W(FALSE) | - | 搬运中信号 |
| Write.Complete | W(清) | - | - | - | - | 完成信号(预留) |
| Write.Ready | - | - | - | - | - | 本机就绪(外部写入) |
| Write.RcvHeartbeat | W | W | W | W | W | 持续写入接料心跳 |
| Write.RequestIn | W(清) | - | - | - | - | 下游进料请求(预留) |
| Write.DsMoveBusy | W(清) | - | W(TRUE) | W(FALSE) | - | 下游搬运中 |
| Write.DsComplete | W(清) | - | - | W(TRUE) | - | 下游完成 |
| Write.DsReady | - | - | - | - | - | 本机就绪(外部写入) |
| WriteSpeed | - | - | W(锁存) | - | - | MoveBusy上升沿写入 |
| WriteQuality | - | - | W(锁存) | - | - | MoveBusy上升沿写入 |
| WriteGrade | - | - | W(锁存) | - | - | MoveBusy上升沿写入 |
| WriteGlassID | - | - | W(锁存) | - | - | MoveBusy上升沿写入 |
| Read.* | R | R | R | R | R | 全态只读 |
| CommFault | R | R | R | R | W(TRUE) | FAULT态置位 |
| HbTimeout | R/W | R/W | R/W | R/W | R/W | 心跳监视写入 |

## 8. 边界条件处理

| 场景 | 行为 |
|------|------|
| Enable=FALSE | 所有Write清零, 状态归IDLE, 输出清零, RETURN |
| i_bRequestOut在REQ_OUT/MOVE_BUSY期间撤销 | 不影响, 一旦进入状态机则按协议走完 |
| i_bAllowDischarge=FALSE时收到RequestIn | 拒绝进入REQ_IN, 保持在IDLE |
| i_bTransportDone和DsComplete同时到达 | 优先响应, 任一即可触发COMPLETE |
| 下游取消请求(RequestIn=FALSE)在REQ_IN期间 | 回退到IDLE |
| 心跳超时在REQ_OUT期间 | 立即回IDLE + 置CommFault |
| 心跳超时在MOVE_BUSY期间 | 立即回IDLE + 置CommFault, MoveBusy清零 |
| 心跳超时在COMPLETE期间 | 不处理, 等脉冲结束后回IDLE再检测 |
| Reset在MOVE_BUSY期间 | 立即回IDLE, MoveBusy清零 |
| Reset在FAULT期间 | 清CommFault + 回IDLE |
| 所有时序参数=0 | 延迟为0ms(立即转换), 心跳超时=0ms(立即超时), 需合理配置 |
| 上下游同时触发 | 双通道独立, 可同时运行 |
| q_bUpComplete/q_bDownComplete脉冲期间又来请求 | 脉冲期间状态机在COMPLETE态, 不会响应新请求 |

## 9. 调用方集成指南

### 9.1 典型OB1接线模式

```pascal
(* 声明实例 *)
fbHandshake : FB_1020_EquipmentHandshake;

(* 信号映射: 通讯层 -> 结构体 *)
(* 上游写区: 本机发给上游 *)
stUpStream.Write.Ready := bLocalReady;
stUpStream.Write.Heartbeat := (* FB内部自动写入 *);
(* 上游读区: 从上游收到 *)
(* stUpStream.Read.* 由通讯层(MB_CLIENT等)自动更新 *)

(* 调用FB *)
fbHandshake(
    i_bEnable         := bAutoMode,
    i_bRequestOut     := bNeedMaterial,
    i_bAllowDischarge := bCanOutput,
    i_bReset          := bResetCmd,
    i_bTransportDone  := bConveyorFinished,
    i_stProductData   := stCurrentProduct,
    i_dReqDelayMs     := 1000,
    i_dHbToggleMs     := 500,
    i_dHbTimeoutMs    := 3000,
    i_dCompleteMs     := 500,
    io_stUpStream     := stUpStream,
    io_stDownStream   := stDownStream
);

(* 使用输出 *)
bUpReady    := fbHandshake.q_bUpReady;
bDownReady  := fbHandshake.q_bDownReady;
bUpDone     := fbHandshake.q_bUpComplete;
bDownDone   := fbHandshake.q_bDownComplete;
bAlarm      := fbHandshake.q_bAlarm;
```

### 9.2 通讯层映射职责

| 职责 | 说明 | 由谁负责 |
|------|------|----------|
| stUpStream.Read.* 的填充 | 从通讯介质读取对方信号写入Read区 | OB1/通讯FB |
| stUpStream.Write.* 的发送 | 将Write区信号通过通讯介质发出 | OB1/通讯FB |
| stDownStream 同上 | 同上游 | OB1/通讯FB |
| Write.Ready/DsReady | 本机就绪信号, 由外部逻辑写入 | OB1/编排器 |
| 心跳/握手信号 | 由FB_1020自动管理 | FB_1020 |

## 10. 关联文档

| 文档 | 路径 | 版本 |
|------|------|:----:|
| IFC | 接口文档_IFC-FB1020-EquipmentHandshake-V1.1.0.md | V1.1.0 |
| ST_HandshakeBits | ../types/ST_HandshakeBits.scl | V1.0.0 |
| ST_HandshakeCh | ../types/ST_HandshakeCh.scl | V1.0.0 |
| ST_ProductData | ../types/ST_ProductData.scl | V1.0.0 |
| LSP-905 | 905_SCL编程规范_LSP-V1.0.1.md | V1.0.1 |
| LSP-904 | 904_SCL注释规范_LSP-V1.2.0.md | V1.2.0 |
| LSP-903 | 903_定时器使用规范_LSP-V1.0.0.md | V1.0.0 |
