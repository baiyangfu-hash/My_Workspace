# 气缸控制FB接口文档

## 1. FB基本信息

| 项目 | 描述 |
|------|------|
| FB名称 | FB_CylinderControl_work3 |
| 标准 | IEC 61131-3 |
| 版本 | V2.0.0 [2026-01-16] |
| 功能 | 单线圈控制阀控制、传感器防抖、超时报警、阀门卡死检测 |
| 适用平台 | 三菱GX Works3 |

## 2. 输入变量表

| 序号 | 变量名 | 数据类型 | 描述 | 来源 | 地址映射 | 默认值 | 优先级 |
|------|--------|----------|------|------|----------|--------|--------|
| 1 | i_OriginSensor | BOOL | 原点传感器信号 | 本地 | X0 | OFF | 高 |
| 2 | i_EndSensor | BOOL | 终点传感器信号 | 本地 | X1 | OFF | 高 |
| 3 | i_ManualMode | BOOL | 手动模式 | 本地 | X2 | OFF | 中 |
| 4 | i_AutoMode | BOOL | 自动模式 | 本地 | X3 | OFF | 高 |
| 5 | i_ExtendCmd | BOOL | 手动伸出命令 | 本地 | X4 | OFF | 高 |
| 6 | i_RetractCmd | BOOL | 手动缩回命令 | 本地 | X5 | OFF | 高 |
| 7 | i_Start | BOOL | 自动运行启动 | 本地 | X6 | OFF | 高 |
| 8 | i_Stop | BOOL | 自动运行停止 | 本地 | X7 | OFF | 高 |
| 9 | i_AlarmReset | BOOL | 报警复位 | 本地 | X8 | OFF | 高 |
| 10 | i_ExtendTimeout | TIME | 伸出超时时间 | 本地 | - | T#2S | 高 |
| 11 | i_RetractTimeout | TIME | 缩回超时时间 | 本地 | - | T#2S | 高 |
| 12 | i_SensorDebounceTime | TIME | 传感器防抖时间 | 本地 | - | T#50MS | 高 |
| 13 | i_AlarmDelay | TIME | 报警延迟时间 | 本地 | - | T#100MS | 高 |

## 3. 输出变量表

| 序号 | 变量名 | 数据类型 | 描述 | 去向 | 地址映射 | 默认值 | 优先级 |
|------|--------|----------|------|------|----------|--------|--------|
| 1 | q_SolenoidOutput | BOOL | 电磁阀输出控制（单线圈） | 本地 | Y0 | OFF | 高 |
| 2 | q_OriginPosition | BOOL | 原点位置状态 | 本地 | Y1 | OFF | 高 |
| 3 | q_EndPosition | BOOL | 终点位置状态 | 本地 | Y2 | OFF | 高 |
| 4 | q_Extending | BOOL | 正在伸出状态 | 本地 | Y3 | OFF | 高 |
| 5 | q_Retracting | BOOL | 正在缩回状态 | 本地 | Y4 | OFF | 高 |
| 6 | q_AutoRunning | BOOL | 自动运行状态 | 本地 | Y5 | OFF | 高 |
| 7 | q_ManualRunning | BOOL | 手动运行状态 | 本地 | Y6 | OFF | 高 |
| 8 | q_Alarm | BOOL | 报警状态 | 本地 | Y7 | OFF | 高 |
| 9 | q_StateBits | ARRAY[0..9] OF BOOL | 气缸状态位数组 | 本地 | - | FALSE | 高 |

## 4. 内部变量表

| 序号 | 变量名 | 数据类型 | 描述 | 默认值 |
|------|--------|----------|------|--------|
| 1 | _tOriginDebounce | TIMER | 原点防抖定时器 | T100 |
| 2 | _tEndDebounce | TIMER | 终点防抖定时器 | T110 |
| 3 | _tExtendTimeout | TIMER | 伸出超时定时器 | T120 |
| 4 | _tRetractTimeout | TIMER | 缩回超时定时器 | T130 |
| 5 | _tAlarmDelay | TIMER | 报警延迟定时器 | T140 |
| 6 | _bStateIdle | BOOL | 空闲状态标志 | FALSE |
| 7 | _bStateExtending | BOOL | 正在伸出状态标志 | FALSE |
| 8 | _bStateExtended | BOOL | 伸出到位状态标志 | FALSE |
| 9 | _bStateRetracting | BOOL | 正在缩回状态标志 | FALSE |
| 10 | _bStateRetracted | BOOL | 缩回到位状态标志 | FALSE |
| 11 | _bStateAlarm | BOOL | 报警状态标志 | FALSE |
| 12 | _bAlarmLatch | BOOL | 报警锁存标志 | FALSE |
| 13 | _bAlarmExtendTimeout | BOOL | 伸出超时报警标志 | FALSE |
| 14 | _bAlarmRetractTimeout | BOOL | 缩回超时报警标志 | FALSE |
| 15 | _bAlarmSensorConflict | BOOL | 传感器冲突报警标志 | FALSE |
| 16 | _bAlarmValveStuck | BOOL | 阀门卡死报警标志 | FALSE |
| 17 | _bDebouncedOrigin | BOOL | 防抖后的原点状态 | FALSE |
| 18 | _bDebouncedEnd | BOOL | 防抖后的终点状态 | FALSE |
| 19 | _bExtendCmdLatch | BOOL | 伸出命令锁存 | FALSE |
| 20 | _bRetractCmdLatch | BOOL | 缩回命令锁存 | FALSE |
| 21 | _bStartLatch | BOOL | 启动命令锁存 | FALSE |
| 22 | _bManualModeActive | BOOL | 手动模式激活标志 | FALSE |
| 23 | _bAutoModeActive | BOOL | 自动模式激活标志 | FALSE |
| 24 | _bSensorConflictAlarmReq | BOOL | 传感器冲突报警请求 | FALSE |
| 25 | _bExtendingTimeoutReq | BOOL | 伸出超时请求 | FALSE |
| 26 | _bRetractingTimeoutReq | BOOL | 缩回超时请求 | FALSE |
| 27 | _bAlarmDelayQ | BOOL | 报警延迟定时器输出 | FALSE |
| 28 | _bExtendTimeoutQ | BOOL | 伸出超时定时器输出 | FALSE |
| 29 | _bRetractTimeoutQ | BOOL | 缩回超时定时器输出 | FALSE |
| 30 | _bLastSolenoidState | BOOL | 上一次电磁阀状态 | FALSE |

## 5. FB调用示例

### 5.1 变量定义

```st
// FB实例化变量定义
VAR
    fbCylinder1 : FB_CylinderControl_work3;
END_VAR
```

### 5.2 完整调用示例

```st
// FB块调用
fbCylinder1(
    // 输入变量
    i_OriginSensor := 原点传感器,
    i_EndSensor := 动点传感器,
    i_ManualMode := HMI气缸手动,
    i_AutoMode := Auto气缸自动,
    i_ExtendCmd := 手动伸出按钮,
    i_RetractCmd := 手动缩回按钮,
    i_Start := 自动启动命令,
    i_Stop := 自动停止命令,
    i_AlarmReset := 报警复位,
    i_ExtendTimeout := T#2S,
    i_RetractTimeout := T#2S,
    i_SensorDebounceTime := T#50MS,
    i_AlarmDelay := T#100MS,
    // 输出变量
    q_SolenoidOutput => 气缸动点动作,
    q_OriginPosition => 原点到位状态,
    q_EndPosition => 终点到位状态,
    q_Extending => 正在伸出,
    q_Retracting => 正在缩回,
    q_AutoRunning => 自动运行中,
    q_ManualRunning => 手动运行中,
    q_Alarm => 气缸报警,
    q_StateBits => 气缸状态位
);
```

## 6. 状态码定义

### 6.1 状态机状态码

| 状态码 | 状态名称 | 描述 |
|--------|----------|------|
| 0 | 空闲状态 | 系统复位后的初始状态 |
| 1 | 正在伸出状态 | 气缸正在伸出过程中 |
| 2 | 伸出到位状态 | 气缸已到达终点位置 |
| 3 | 正在缩回状态 | 气缸正在缩回过程中 |
| 4 | 缩回到位状态 | 气缸已到达原点位置 |
| 5 | 报警状态 | 系统检测到故障 |

### 6.2 错误代码

| 错误代码 | 错误类型 | 描述 |
|----------|----------|------|
| 0 | 无错误 | 系统正常运行 |
| 1 | 传感器冲突 | 原点和终点传感器同时触发 |
| 2 | 伸出超时 | 气缸伸出超时 |
| 3 | 缩回超时 | 气缸缩回超时 |
| 4 | 阀门卡死 | 电磁阀状态改变但气缸未动作 |

## 7. 注意事项

1. **互锁关系**：
   - 手动模式和自动模式互斥，同一时间只能设置一种模式
   - 电磁阀输出为单线圈控制，通电伸出，断电缩回

2. **初始化要求**：
   - 首次运行前必须执行复位操作（i_AlarmReset=TRUE）
   - 初始化完成后，FB会自动进入适当的状态

3. **故障处理**：
   - 当检测到故障时，会设置q_Alarm=TRUE并保持报警状态
   - 故障状态需要通过复位操作（i_AlarmReset=TRUE）清除

4. **传感器防抖**：
   - 内置传感器防抖功能，通过i_SensorDebounceTime设置防抖时间
   - 防抖后的传感器状态用于状态机判断

## 8. 版本兼容性

| FB版本 | 兼容PLC型号 | 兼容GX Works3版本 | 备注 |
|--------|--------------|-------------------|------|
| V2.0.0 | FX5U, RCPU | V1.0及以上 | 推荐版本 |
| V1.0.0 | FX5U | V1.0 | 初始版本 |

## 9. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| V2.0.0 | 2026-01-16 | 基于实际代码更新接口文档，调整变量命名和功能描述 |
| V1.0.0 | 2026-01-15 | 初始版本，基于模板创建 |