# 输送线控制FB接口文档

## 1. FB基本信息

| 项目 | 描述 |
|------|------|
| FB名称 | FB_ConveyorLineControl_work3 |
| 标准 | IEC 61131-3 |
| 版本 | V2.0.0 [2026-01-16] |
| 功能 | 双位置检测、气缸伸缩控制、上游进料禁止、上下游交互 |
| 上游设备 | 输送线 |
| 下游设备 | 机械手 |
| 适用平台 | 三菱GX Works3 |

## 2. 输入变量表

| 序号 | 变量名 | 数据类型 | 描述 | 来源 | 地址映射 | 默认值 | 优先级 |
|------|--------|----------|------|------|----------|--------|--------|
| 1 | i_Sensor1 | BOOL | 一号位置传感器 | 本地 | X0 | OFF | 高 |
| 2 | i_Sensor2 | BOOL | 二号位置传感器 | 本地 | X1 | OFF | 高 |
| 3 | i_AutoMode | BOOL | 自动模式 | 本地 | X2 | OFF | 高 |
| 4 | i_ManualMode | BOOL | 手动模式 | 本地 | X3 | OFF | 中 |
| 5 | i_Reset | BOOL | 复位信号 | 本地 | X4 | OFF | 高 |
| 6 | i_CylinderExtendCmd | BOOL | 气缸伸出命令 | 本地 | X5 | OFF | 高 |
| 7 | i_CylinderRetractCmd | BOOL | 气缸缩回命令 | 本地 | X6 | OFF | 高 |
| 8 | i_AllowIn | BOOL | 允许进料（主控→工位） | 主控→工位 | M20 | OFF | 高 |
| 9 | i_AllowOut | BOOL | 允许出料（主控→工位） | 主控→工位 | M21 | OFF | 高 |
| 10 | i_SysAutoMode | BOOL | 系统自动模式（主控→所有设备） | 主控→所有设备 | M100 | OFF | 高 |
| 11 | i_SysResetRequest | BOOL | 系统复位请求（操作员→主控） | 操作员→主控 | X1 | OFF | 高 |
| 12 | i_Robot_CurrentStation | INT | 机械手当前所在工位 | 机械手→工位 | D101 | 0 | 高 |
| 13 | i_Robot_Carrying | BOOL | 机械手是否携带产品 | 机械手→工位 | M200 | OFF | 高 |
| 14 | i_Robot_TaskAck | BOOL | 机械手任务完成确认 | 机械手→工位 | M201 | OFF | 高 |

## 3. 输出变量表

| 序号 | 变量名 | 数据类型 | 描述 | 去向 | 地址映射 | 默认值 | 优先级 |
|------|--------|----------|------|------|----------|--------|--------|
| 1 | q_CylinderExtend | BOOL | 气缸伸出输出 | 本地 | Y0 | OFF | 高 |
| 2 | q_CylinderRetract | BOOL | 气缸缩回输出 | 本地 | Y1 | OFF | 高 |
| 3 | q_FeedBlock | BOOL | 上游进料禁止 | 工位→输送线 | Y2 | OFF | 高 |
| 4 | q_IsReady | BOOL | 工位就绪 | 本地 | Y3 | OFF | 高 |
| 5 | q_HasPart | BOOL | 有料检测 | 本地 | Y4 | OFF | 高 |
| 6 | q_ErrorActive | BOOL | 故障报警 | 本地 | Y5 | OFF | 高 |
| 7 | q_ErrorCode | INT | 错误代码 | 本地 | D100 | 0 | 高 |
| 8 | q_RequestPick | BOOL | 请求取料（工位→主控） | 工位→主控 | M30 | OFF | 高 |
| 9 | q_RequestPlace | BOOL | 请求放料（工位→主控） | 工位→主控 | M31 | OFF | 高 |
| 10 | q_ProcessDone | BOOL | 加工完成（工位→主控） | 工位→主控 | M32 | OFF | 高 |
| 11 | q_SysConveyorReady | BOOL | 输送线就绪（输送线→主控） | 输送线→主控 | M201 | OFF | 高 |
| 12 | q_ConveyorReady | BOOL | 输送线就绪（输送线→主控） | 输送线→主控 | M202 | OFF | 高 |

## 4. 内部变量表

| 序号 | 变量名 | 数据类型 | 描述 | 默认值 |
|------|--------|----------|------|--------|
| 1 | tmp_nState | INT | 状态机当前状态 | 0 |
| 2 | tmp_Timer1 | TON | 计时器1 | - |
| 3 | tmp_Timer2 | TON | 计时器2 | - |
| 4 | tmp_bLastSensor1 | BOOL | 上一次一号传感器状态 | OFF |
| 5 | tmp_bLastSensor2 | BOOL | 上一次二号传感器状态 | OFF |
| 6 | tmp_bProductID | STRING[20] | 产品ID | "" |
| 7 | tmp_nProcessStep | INT | 当前工艺步骤 | 0 |
| 8 | tmp_bSysEmergencyStop | BOOL | 系统急停信号 | OFF |
| 9 | In_tTimer1 | BOOL | 计时器1触发输入 | OFF |
| 10 | In_tTimer2 | BOOL | 计时器2触发输入 | OFF |
| 11 | Q_tTimer1 | BOOL | 计时器1输出 | OFF |
| 12 | Q_tTimer2 | BOOL | 计时器2输出 | OFF |
| 13 | PT_tTimer1 | TIME | 计时器1设定值 | T#1s |
| 14 | PT_tTimer2 | TIME | 计时器2设定值 | T#1s |
| 15 | ET_tTimer1 | TIME | 计时器1经过时间 | T#0s |
| 16 | ET_tTimer2 | TIME | 计时器2经过时间 | T#0s |
| 17 | tmp_nTimerPreset | INT | 计时器预设值 | 0 |
| 18 | tmp_bSystemReady | BOOL | 系统就绪标志 | OFF |
| 19 | tmp_bCycleComplete | BOOL | 周期完成标志 | OFF |

## 5. FB调用示例

### 5.1 变量定义

```scl
// FB实例化变量定义
VAR
    fbConveyor : FB_ConveyorLineControl_work3;
END_VAR
```

### 5.2 完整调用示例

```scl
// FB块调用
fbConveyor(
    // 输入变量
    i_Sensor1 := X0,                    // 一号位置传感器
    i_Sensor2 := X1,                    // 二号位置传感器
    i_AutoMode := X2,                   // 自动模式
    i_ManualMode := X3,                 // 手动模式
    i_Reset := X4,                      // 复位信号
    i_CylinderExtendCmd := X5,          // 气缸伸出命令
    i_CylinderRetractCmd := X6,         // 气缸缩回命令
    i_AllowIn := M20,                   // 允许进料（主控→工位）
    i_AllowOut := M21,                  // 允许出料（主控→工位）
    i_SysAutoMode := M100,              // 系统自动模式（主控→所有设备）
    i_SysResetRequest := X1,            // 系统复位请求（操作员→主控）
    i_Robot_CurrentStation := D101,     // 机械手当前所在工位
    i_Robot_Carrying := M200,           // 机械手是否携带产品
    i_Robot_TaskAck := M201,            // 机械手任务完成确认
    // 输出变量
    q_CylinderExtend => Y0,             // 气缸伸出输出
    q_CylinderRetract => Y1,            // 气缸缩回输出
    q_FeedBlock => Y2,                  // 上游进料禁止
    q_IsReady => Y3,                    // 工位就绪
    q_HasPart => Y4,                    // 有料检测
    q_ErrorActive => Y5,                // 故障报警
    q_ErrorCode => D100,                // 错误代码
    q_RequestPick => M30,               // 请求取料（工位→主控）
    q_RequestPlace => M31,              // 请求放料（工位→主控）
    q_ProcessDone => M32,               // 加工完成（工位→主控）
    q_SysConveyorReady => M201,         // 输送线就绪（输送线→主控）
    q_ConveyorReady => M202             // 输送线就绪（输送线→主控）
);
```

### 5.3 简化调用示例（仅自动模式）

```scl
// 简化的FB块调用（仅使用自动模式）
fbConveyor(
    // 必要输入变量
    i_Sensor1 := X0,
    i_Sensor2 := X1,
    i_AutoMode := X2,
    i_Reset := X4,
    i_AllowIn := M20,
    i_AllowOut := M21,
    i_Robot_CurrentStation := D101,
    i_Robot_Carrying := M200,
    i_Robot_TaskAck := M201,
    // 输出变量
    q_CylinderExtend => Y0,
    q_CylinderRetract => Y1,
    q_FeedBlock => Y2,
    q_IsReady => Y3,
    q_HasPart => Y4,
    q_ErrorActive => Y5,
    q_ErrorCode => D100,
    q_RequestPick => M30,
    q_RequestPlace => M31,
    q_ProcessDone => M32
);
```

## 6. 状态码定义

### 6.1 状态机状态码

| 状态码 | 状态名称 | 描述 |
|--------|----------|------|
| 0 | 初始化状态 | 系统复位后的初始状态 |
| 1 | 等待产品状态 | 等待上游输送线送来产品 |
| 2 | 一号位置有产品状态 | 上游产品进入一号位置 |
| 3 | 二号位置有产品状态 | 上游产品进入二号位置 |
| 4 | 两个位置都有产品状态 | 两个位置传感器都检测到产品 |

### 6.2 错误代码

| 错误代码 | 错误类型 | 描述 |
|----------|----------|------|
| 0 | 无错误 | 系统正常运行 |
| 1001 | 系统急停 | 系统检测到急停信号 |

## 7. 接口时序图

### 7.1 自动模式下的典型工作流程

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ 上游输送线     │     │ 输送线控制FB   │     │ 下游机械手     │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        │ i_AllowIn=TRUE      │                     │
        ├────────────────────────►│                     │
        │                     │                     │
        │                     │ q_CylinderExtend=TRUE│
        │                     │                     │
        │                     │ 产品进入i_Sensor1   │
        │                     │                     │
        │                     │ q_RequestPick=TRUE  │
        │                     ├────────────────────────►│
        │                     │                     │
        │                     │ i_Robot_TaskAck=TRUE│
        │                     │◄────────────────────────┘
        │                     │                     │
        │                     │ 产品离开i_Sensor1   │
        │                     │                     │
        │                     │ q_RequestPick=FALSE │
        │                     │                     │
```

## 8. 注意事项

1. **互锁关系**：
   - 手动模式和自动模式互斥，同一时间只能设置一种模式
   - 气缸伸出和缩回命令互斥，同一时间只能有一个方向有效

2. **初始化要求**：
   - 首次运行前必须执行复位操作（i_Reset=TRUE）
   - 初始化完成后，FB会自动进入适当的状态

3. **上游交互**：
   - 只有当主控允许进料时，才会允许上游进料
   - 当两个位置都有产品时，会禁止上游进料

4. **下游交互**：
   - 当机械手到达当前工位且携带产品时，请求放料
   - 当产品被取走后，会更新工位状态

5. **故障处理**：
   - 当检测到故障时，会设置q_ErrorActive=TRUE并更新q_ErrorCode
   - 故障状态需要通过复位操作（i_Reset=TRUE）清除

## 9. 版本兼容性

| FB版本 | 兼容PLC型号 | 兼容GX Works3版本 | 备注 |
|--------|--------------|-------------------|------|
| V2.0.0 | FX5U, Q系列 | V1.0及以上 | 推荐版本 |
| V1.0.0 | FX5U | V1.0 | 初始版本 |

## 10. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| V2.0.0 | 2026-01-16 | 完善上下游交互逻辑，添加完整的输送线与机械手交互功能 |
| V1.0.0 | 2026-01-14 | 初始版本，实现基本功能 |

## 11. 技术支持

| 支持方式 | 联系方式 |
|----------|----------|
| 技术文档 | 项目文档目录 |
| 邮件支持 | support@example.com |
| 电话支持 | 400-123-4567 |
