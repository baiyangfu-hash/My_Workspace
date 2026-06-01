# 详细设计说明书 FB_1020_EquipmentHandshake

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1020 设备通讯握手详细设计 |
| **文档版本** | V2.0.0 |
| **关联源码** | communication/FB_1020_EquipmentHandshake.scl |
| **关联IFC** | 接口文档_IFC-FB1020-EquipmentHandshake-V2.0.0.md |
| **编制日期** | 2026-05-30 |
| **编制人** | Trae |
| **遵循规范** | LSP-905 V1.0.1, LSP-904 V1.2.0, LSP-903 V1.0.0 |
| **V2.0.0 变更** | Breaking Change: ST_ProductData GlassID 30 INT -> 16 WORD; ST_HandshakeCh 扁平字段 -> WriteProduct/ReadProduct 嵌入; [B1] Disable段不再清除Ready/DsReady/Reserved; [B2] 上游COMPLETE态增加Write.Complete回传; [B3] 产品数据改为MoveBusy上升沿一次性锁存; [D1] 新增q_stUpReceivedProduct/q_stDownReceivedProduct输出 |

## 1. 设计原则

1. **纯协议逻辑, 传输层无关**: FB只管理握手时序和状态转换, 不依赖任何具体通讯介质(ModbusTCP/Profinet/OPC-UA/硬线IO等). 信号通过VAR_IN_OUT结构体交换, 映射由调用方负责.
2. **双通道独立状态机**: 上游(UP-Stream)和下游(DOWN-Stream)各自5态状态机, 互不干扰, 可同时运行.
3. **参数化时序**: 延迟/心跳/超时/脉冲宽度全部通过VAR_INPUT可配置, 默认值来自协议定义(各設備交握-5.20.xlsx).
4. **心跳翻转检测**: 本机生成心跳方波, 同时监视对方心跳翻转. 超时未翻转则判定通讯中断.
5. **产品数据上升沿锁存**: MoveBusy上升沿一次性锁存产品数据到WriteProduct区, 避免传输过程中数据被覆盖. 使用bUpDataLatched/bDsDataLatched标志确保仅锁存一次.
6. **接收侧产品数据输出**: 对方Complete/TransportDone上升沿锁存ReadProduct到q_stReceivedProduct输出, 实现双向产品数据透传.
7. **故障冻结+手动恢复**: FAULT态冻结所有输出, 需手动Reset或心跳恢复才能回到IDLE.
8. **完成脉冲输出**: Complete状态输出固定宽度脉冲(默认500ms), 脉冲结束后自动回IDLE.
9. **Disable段职责边界**: Enable=FALSE时只清除FB管理的信号(Heartbeat/RequestOut/MoveBusy/Complete/RcvHeartbeat/RequestIn/DsMoveBusy/DsComplete), 不触碰外部写入字段(Ready/DsReady/Reserved1-6).
10. **LSP-904注释合规**: 变量行内注释使用`//`, 功能块头部和逻辑分支说明使用`(* *)`, 禁止嵌套注释, 禁止中文标点, 禁止注释内容含`(*`或`*)`标记字符串.

## 2. 状态定义表

### 2.1 上游通道状态机 (UpStream_SM)

| 状态值 | 名称 | 入口条件 | 入口动作 | 出口条件 | 出口目标 |
|:------:|------|----------|----------|----------|----------|
| 0 | IDLE | 初始/复位/完成脉冲结束 | 清除Write.RequestOut/MoveBusy/Complete; 清除bUpDataLatched | i_bRequestOut上升沿 AND q_bUpReady | REQ_OUT |
| 1 | REQ_OUT | IDLE出口条件满足 | Write.RequestOut:=TRUE; 启动tReqOutDelay | tReqOutDelay.Q | MOVE_BUSY |
| 2 | MOVE_BUSY | tReqOutDelay.Q | Write.MoveBusy:=TRUE; Write.RequestOut:=FALSE; MoveBusy上升沿锁存WriteProduct | Read.Complete上升沿(同时锁存ReadProduct到q_stUpReceivedProduct) | COMPLETE |
| 3 | COMPLETE | Read.Complete上升沿 | Write.MoveBusy:=FALSE; Write.Complete:=TRUE; q_bUpComplete:=TRUE; 启动脉冲定时器 | tCompletePulseUp.Q | IDLE |
| 4 | FAULT | 任何态HbTimeout | CommFault:=TRUE; 冻结输出 | i_bReset OR (NOT HbTimeout) | IDLE |

### 2.2 下游通道状态机 (DownStream_SM)

| 状态值 | 名称 | 入口条件 | 入口动作 | 出口条件 | 出口目标 |
|:------:|------|----------|----------|----------|----------|
| 0 | IDLE | 初始/复位/完成脉冲结束 | 清除Write.RequestIn/DsMoveBusy/DsComplete; 清除bDsDataLatched | Read.RequestIn上升沿 AND i_bAllowDischarge AND q_bDownReady | REQ_IN |
| 1 | REQ_IN | IDLE出口条件满足 | 启动tReqInDelay | tReqInDelay.Q | MOVE_BUSY |
| 2 | MOVE_BUSY | tReqInDelay.Q | Write.DsMoveBusy:=TRUE; DsMoveBusy上升沿锁存WriteProduct | i_bTransportDone上升沿 OR Read.DsComplete上升沿(同时锁存ReadProduct到q_stDownReceivedProduct) | COMPLETE |
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
(* [B1] 只清除FB管理的信号, 不触碰外部写入字段 *)
IF NOT i_bEnable THEN
    io_stUpStream.Write.Heartbeat    := FALSE;
    io_stUpStream.Write.RequestOut   := FALSE;
    io_stUpStream.Write.MoveBusy     := FALSE;
    io_stUpStream.Write.Complete     := FALSE;
    io_stUpStream.Write.RcvHeartbeat := FALSE;
    io_stUpStream.Write.RequestIn    := FALSE;
    io_stUpStream.Write.DsMoveBusy   := FALSE;
    io_stUpStream.Write.DsComplete   := FALSE;
    // 不清除 Write.Ready / Write.DsReady / Write.Reserved1-6

    io_stDownStream.Write.Heartbeat    := FALSE;
    io_stDownStream.Write.RequestOut   := FALSE;
    io_stDownStream.Write.MoveBusy     := FALSE;
    io_stDownStream.Write.Complete     := FALSE;
    io_stDownStream.Write.RcvHeartbeat := FALSE;
    io_stDownStream.Write.RequestIn    := FALSE;
    io_stDownStream.Write.DsMoveBusy   := FALSE;
    io_stDownStream.Write.DsComplete   := FALSE;

    q_bUpReady := FALSE;  q_bDownReady := FALSE;
    q_bUpComplete := FALSE;  q_bDownComplete := FALSE;
    q_bAlarm := FALSE;  q_wStatusCode := 16#0000;
    q_iUpState := 0;  q_iDownState := 0;
    iUpState := 0;  iDownState := 0;

    (* 定时器复位 *)
    tReqOutDelay.IN := FALSE; tReqInDelay.IN := FALSE;
    tHbUpTimeout.IN := FALSE; tHbDsTimeout.IN := FALSE;
    tHbToggle.IN := FALSE;
    tCompletePulseUp.IN := FALSE; tCompletePulseDs.IN := FALSE;
ELSE
    q_iUpState := iUpState;
    q_iDownState := iDownState;
END_IF;
```

### 3.1 心跳生成

```pascal
(* 方波发生器: 周期=i_dHbToggleMs, 占空比50% *)
tHbToggle.IN := NOT tHbToggle.Q;
tHbToggle.PT := i_dHbToggleMs;

(* 上游通道: 写入本机送料心跳 *)
io_stUpStream.Write.Heartbeat := tHbToggle.Q;

(* 下游通道: 写入本机接料心跳 *)
io_stDownStream.Write.RcvHeartbeat := tHbToggle.Q;
```

### 3.2 心跳超时监视

```pascal
(* 上游通道: 检测对方心跳翻转 *)
(* 原理: 记忆上周期Read.Heartbeat和Read.RcvHeartbeat的值 *)
(*       本周期与上周期比较, 任一变化即为翻转 *)
bUpHbChanged := (io_stUpStream.Read.Heartbeat <> bLastUpHbA)
             OR (io_stUpStream.Read.RcvHeartbeat <> bLastUpHbB);
bLastUpHbA := io_stUpStream.Read.Heartbeat;
bLastUpHbB := io_stUpStream.Read.RcvHeartbeat;

IF bUpHbChanged THEN
    tHbUpTimeout.IN := FALSE;
    io_stUpStream.HbTimeout := FALSE;
ELSE
    tHbUpTimeout.IN := TRUE;
END_IF;
tHbUpTimeout.PT := i_dHbTimeoutMs;

IF tHbUpTimeout.Q THEN
    io_stUpStream.HbTimeout := TRUE;
END_IF;

(* 下游通道: 同理 *)
bDsHbChanged := (io_stDownStream.Read.RcvHeartbeat <> bLastDsHbA)
             OR (io_stDownStream.Read.Heartbeat <> bLastDsHbB);
bLastDsHbA := io_stDownStream.Read.RcvHeartbeat;
bLastDsHbB := io_stDownStream.Read.Heartbeat;

IF bDsHbChanged THEN
    tHbDsTimeout.IN := FALSE;
    io_stDownStream.HbTimeout := FALSE;
ELSE
    tHbDsTimeout.IN := TRUE;
END_IF;
tHbDsTimeout.PT := i_dHbTimeoutMs;

IF tHbDsTimeout.Q THEN
    io_stDownStream.HbTimeout := TRUE;
END_IF;
```

### 3.3 就绪综合信号

```pascal
q_bUpReady := io_stUpStream.Read.Ready
              AND (NOT io_stUpStream.CommFault)
              AND (NOT io_stUpStream.HbTimeout);

q_bDownReady := io_stDownStream.Read.DsReady
               AND (NOT io_stDownStream.CommFault)
               AND (NOT io_stDownStream.HbTimeout);
```

### 3.4 边沿检测

```pascal
rTrigRequestOut(IN := i_bRequestOut, Q => ...);
rTrigRequestIn(IN := io_stDownStream.Read.RequestIn, Q => ...);
rTrigUpComplete(IN := io_stUpStream.Read.Complete, Q => ...);
rTrigDsComplete(IN := io_stDownStream.Read.DsComplete, Q => ...);
rTrigTransport(IN := i_bTransportDone, Q => ...);
rTrigMoveBusyUp(IN := io_stUpStream.Write.MoveBusy, Q => ...);    (* V2.0.0: 产品数据锁存触发 *)
rTrigMoveBusyDs(IN := io_stDownStream.Write.DsMoveBusy, Q => ...); (* V2.0.0: 产品数据锁存触发 *)
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
        bUpDataLatched := FALSE;

        IF rTrigRequestOut.Q AND q_bUpReady THEN iUpState := 1; END_IF;
        IF HbTimeout THEN iUpState := 4; CommFault := TRUE; END_IF;

    1: (* REQ_OUT *)
        Write.RequestOut := TRUE;
        tReqOutDelay(IN := TRUE, PT := i_dReqDelayMs, ...);

        IF tReqOutDelay.Q THEN iUpState := 2; tReqOutDelay.IN := FALSE; END_IF;
        IF i_bReset OR HbTimeout THEN
            iUpState := 0;
            Write.RequestOut := FALSE;
            tReqOutDelay.IN := FALSE;
            IF HbTimeout THEN CommFault := TRUE; END_IF;
        END_IF;

    2: (* MOVE_BUSY_UP *)
        Write.MoveBusy := TRUE;
        Write.RequestOut := FALSE;

        (* [B3] MoveBusy上升沿一次性锁存产品数据 *)
        IF rTrigMoveBusyUp.Q AND (NOT bUpDataLatched) THEN
            WriteProduct := i_stProductData;
            bUpDataLatched := TRUE;
        END_IF;

        (* [D1] 上游Complete时锁存接收到的产品数据 *)
        IF rTrigUpComplete.Q THEN
            q_stUpReceivedProduct := ReadProduct;
            iUpState := 3;
        END_IF;

        IF i_bReset OR HbTimeout THEN
            iUpState := 0;
            Write.MoveBusy := FALSE;
            IF HbTimeout THEN CommFault := TRUE; END_IF;
        END_IF;

    3: (* COMPLETE_UP - [B2] 回传Complete *)
        Write.MoveBusy := FALSE;
        Write.Complete := TRUE;
        q_bUpComplete := TRUE;
        tCompletePulseUp(IN := TRUE, PT := i_dCompleteMs, ...);

        IF tCompletePulseUp.Q THEN
            q_bUpComplete := FALSE;
            Write.Complete := FALSE;
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
        bDsDataLatched := FALSE;

        IF rTrigRequestIn.Q AND i_bAllowDischarge AND q_bDownReady THEN
            iDownState := 1;
        END_IF;
        IF HbTimeout THEN iDownState := 4; CommFault := TRUE; END_IF;

    1: (* REQ_IN *)
        tReqInDelay(IN := TRUE, PT := i_dReqDelayMs, ...);

        IF tReqInDelay.Q THEN iDownState := 2; tReqInDelay.IN := FALSE; END_IF;
        IF i_bReset OR HbTimeout OR (NOT Read.RequestIn) THEN
            iDownState := 0;
            tReqInDelay.IN := FALSE;
            IF HbTimeout THEN CommFault := TRUE; END_IF;
        END_IF;

    2: (* MOVE_BUSY_DS *)
        Write.DsMoveBusy := TRUE;

        (* [B3] DsMoveBusy上升沿一次性锁存产品数据 *)
        IF rTrigMoveBusyDs.Q AND (NOT bDsDataLatched) THEN
            WriteProduct := i_stProductData;
            bDsDataLatched := TRUE;
        END_IF;

        (* 完成条件: 物理传输完成 OR 对方确认完成 *)
        IF rTrigTransport.Q OR rTrigDsComplete.Q THEN
            q_stDownReceivedProduct := ReadProduct;
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

产品数据锁存                                   ┌┐ (MoveBusy上升沿, bUpDataLatched)
                                              └┘

Up.Read.Complete                                            ─────┐
                                                                 └── (对方确认)

Up.Write.Complete                                           ─────┐  ← V2.0.0: 回传对方
                                                                 └── (脉冲宽度)

q_stUpReceivedProduct                                       ─────┐  ← V2.0.0: 锁存ReadProduct
                                                                 └── (保持到下次)

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

产品数据锁存                           ┌┐ (DsMoveBusy上升沿, bDsDataLatched)
                                      └┘

i_bTransportDone                                     ─────┐
                                                           └── (输送到位)

q_stDownReceivedProduct                               ─────┐  ← V2.0.0: 锁存ReadProduct
                                                           └── (保持到下次)

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
| io_stUpStream.HbTimeout | BOOL | 上游心跳超时(i_dHbTimeoutMs内无翻转) | 心跳翻转时自动清除 |
| io_stDownStream.HbTimeout | BOOL | 下游心跳超时 | 心跳翻转时自动清除 |
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
| rTrigMoveBusyUp | FB_R_TRIG | -- | Write.MoveBusy上升沿(V2.0.0新增) |
| rTrigMoveBusyDs | FB_R_TRIG | -- | Write.DsMoveBusy上升沿(V2.0.0新增) |
| rTrigTransport | FB_R_TRIG | -- | i_bTransportDone上升沿 |
| bLastUpHbA | BOOL | FALSE | 上周期上游Read.Heartbeat |
| bLastUpHbB | BOOL | FALSE | 上周期上游Read.RcvHeartbeat |
| bLastDsHbA | BOOL | FALSE | 上周期下游Read.RcvHeartbeat |
| bLastDsHbB | BOOL | FALSE | 上周期下游Read.Heartbeat |
| bUpHbChanged | BOOL | FALSE | 上游心跳翻转标志 |
| bDsHbChanged | BOOL | FALSE | 下游心跳翻转标志 |
| bUpDataLatched | BOOL | FALSE | 上游产品数据已锁存标志(V2.0.0新增) |
| bDsDataLatched | BOOL | FALSE | 下游产品数据已锁存标志(V2.0.0新增) |

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
| Write.Complete | W(清) | - | - | W(TRUE) | - | 完成信号(V2.0.0: 回传对方) |
| Write.Ready | - | - | - | - | - | 本机就绪(外部写入, FB不触碰) |
| Write.RcvHeartbeat | W | W | W | W | W | 持续写入接料心跳 |
| Write.RequestIn | W(清) | - | - | - | - | 下游进料请求(预留) |
| Write.DsMoveBusy | W(清) | - | W(TRUE) | W(FALSE) | - | 下游搬运中 |
| Write.DsComplete | W(清) | - | - | W(TRUE) | - | 下游完成 |
| Write.DsReady | - | - | - | - | - | 本机就绪(外部写入, FB不触碰) |
| Write.Reserved1~6 | - | - | - | - | - | 预留(FB不触碰) |
| WriteProduct | - | - | W(锁存) | - | - | MoveBusy上升沿写入, bUpDataLatched保护 |
| Read.* | R | R | R | R | R | 全态只读 |
| ReadProduct | R | R | R(锁存) | R | R | Complete/TransportDone上升沿锁存到输出 |
| CommFault | R | R | R | R | W(TRUE) | FAULT态置位 |
| HbTimeout | R/W | R/W | R/W | R/W | R/W | 心跳监视写入 |

## 8. 边界条件处理

| 场景 | 行为 |
|------|------|
| Enable=FALSE | 只清除FB管理的Write信号, 不触碰Ready/DsReady/Reserved1-6, 状态归IDLE, 输出清零 |
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
| 产品数据在MOVE_BUSY期间变化 | 不影响, 已锁存, bUpDataLatched/bDsDataLatched保护 |

## 9. 调用方集成指南

### 9.1 典型OB1接线模式

```pascal
(* 声明实例 *)
fbHandshake : FB_1020_EquipmentHandshake;

(* 信号映射: 通讯层 -> 结构体 *)
(* 上游写区: 本机发给上游 *)
stUpStream.Write.Ready := bLocalReady;    (* V2.0.0: FB不触碰, 由外部写入 *)
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

(* V2.0.0: 使用接收到的产品数据 *)
stReceivedFromUp   := fbHandshake.q_stUpReceivedProduct;
stReceivedFromDown := fbHandshake.q_stDownReceivedProduct;
```

### 9.2 通讯层映射职责

| 职责 | 说明 | 由谁负责 |
|------|------|----------|
| stUpStream.Read.* 的填充 | 从通讯介质读取对方信号写入Read区 | OB1/通讯FB |
| stUpStream.ReadProduct 的填充 | 从通讯介质读取对方产品数据 | OB1/通讯FB |
| stUpStream.Write.* 的发送 | 将Write区信号通过通讯介质发出 | OB1/通讯FB |
| stUpStream.WriteProduct 的发送 | 将Write区产品数据通过通讯介质发出 | OB1/通讯FB |
| stDownStream 同上 | 同上游 | OB1/通讯FB |
| Write.Ready/DsReady | 本机就绪信号, 由外部逻辑写入 | OB1/编排器 |
| 心跳/握手信号 | 由FB_1020自动管理 | FB_1020 |
| 产品数据锁存 | MoveBusy上升沿一次性锁存 | FB_1020 |

## 10. 关联文档

| 文档 | 路径 | 版本 |
|------|------|:----:|
| IFC | 接口文档_IFC-FB1020-EquipmentHandshake-V2.0.0.md | V2.0.0 |
| ST_HandshakeBits | ../types/ST_HandshakeBits.scl | V1.1.0 |
| ST_HandshakeCh | ../types/ST_HandshakeCh.scl | V2.0.0 |
| ST_ProductData | ../types/ST_ProductData.scl | V2.0.0 |
| LSP-905 | 905_SCL编程规范_LSP-V1.0.1.md | V1.0.1 |
| LSP-904 | 904_SCL注释规范_LSP-V1.2.0.md | V1.2.0 |
| LSP-903 | 903_定时器使用规范_LSP-V1.0.0.md | V1.0.0 |
