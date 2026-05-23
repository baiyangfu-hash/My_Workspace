# SysLib/types/ - 通用结构体类型库

## 概述

本目录包含跨项目复用的通用数据结构体类型定义（UDT），用于统一PLC项目中执行机构、传感器、外部设备等变量的组织方式。

**版本**: V3.0.0
**创建日期**: 2026-05-20
**设计原则**: 高内聚、低耦合、按功能块分组、≤3层嵌套

---

## 结构体清单

### 伺服轴控制（1文件 = 10个TYPE，嵌套组合）

| 文件名 | 主结构体 | 子TYPE列表 | 总字段数 | 用途 |
|--------|----------|-----------|:-------:|------|
| `ST_ServoAxis.scl` | **ST_ServoAxis** | ST_SvPower, ST_SvHome, ST_SvAbs, ST_SvJog, ST_SvStop, ST_SvHalt, ST_SvRel, ST_SvReset, ST_Sensor | **74** | 伺服轴完整控制 (按SV_*功能块分组嵌套, PLCopen MC Part 1标准) |

#### ST_ServoAxis 内部结构 (V3.0 嵌套式)

```
ST_ServoAxis
├── stPower   : ST_SvPower   (6字段)  ← SV_Power  轴使能/励磁  (MC_Power)
├── stHome    : ST_SvHome    (8字段)  ← SV_Home   回原点        (MC_Home)
├── stAbs     : ST_SvAbs     (12字段) ← SV_ABS    绝对定位      (MC_MoveAbsolute)
├── stJog     : ST_SvJog     (11字段) ← SV_Jog    点动          (MC_MoveVelocity)
├── stStop    : ST_SvStop    (7字段)  ← SV_Stop   急停          (MC_Stop)
├── stHalt    : ST_SvHalt    (7字段)  ← SV_Halt   减速暂停      (MC_Halt)
├── stRel     : ST_SvRel     (12字段) ← SV_Rel    相对定位      (MC_MoveRelative)
├── stReset   : ST_SvReset   (5字段)  ← SV_Reset  错误复位      (MC_Reset)
├── stSensor  : ST_Sensor    (5字段)  ← 共享传感器 (限位/原点/ALM)
└── rCurrentPos: REAL        (1字段)  ← 当前位置反馈 mm
```

### 基础类型（0层嵌套，无子结构体）

| 文件名 | 结构体名 | 字段数 | 用途 |
|--------|----------|:------:|------|
| `ST_Cylinder.scl` | ST_Cylinder | 10 | 双线圈气缸 (伸出/收回+超时+冗余) |
| `ST_ConveyorMotor.scl` | ST_ConveyorMotor | 11 | 输送电机 (正/反/慢速+VFD互锁) |
| `ST_DualSensor.scl` | ST_DualSensor | 4 | 双传感器冗余 (一致性校验) |
| `ST_ProductSensors.scl` | ST_ProductSensors | 6 | 产品检测传感器阵列 (长边/短边) |
| `ST_ExternalDevice.scl` | ST_ExternalDevice | 12 | 外部设备接口 (组框机/打胶机/机器人) |

### 组合类型（1层嵌套，引用基础类型）

| 文件名 | 结构体名 | 嵌套引用 | 最大访问深度 |
|--------|----------|----------|:-----------:|
| `ST_ConveyorLayer.scl` | ST_ConveyorLayer | ST_DualSensor ×1, ST_Cylinder ×2, ST_ConveyorMotor ×1 | 3层 |

---

## 使用方式

### 1. 在 .plc.json 中引用

```json
{
  "name": "YourProject",
  "libraries": [
    "../01_SharedLibraries/SysLib"
  ]
}
```

### 2. 在 GlobalVars.db 中实例化

```pascal
DATA_BLOCK GlobalVars
VAR
    // 伺服轴数组 (3轴: Z/X1/X2)
    astServoAxis[1..3] : ARRAY[1..3] OF ST_ServoAxis;
    
    // 4层输送机
    astConveyorLayer[1..4] : ARRAY[1..4] OF ST_ConveyorLayer;
    
    // 取放料机构
    stLiftCylinder  : ST_Cylinder;
    stFrontClamp    : ST_Cylinder;
    stProductDetect : ST_ProductSensors;
END_VAR
END_DATA_BLOCK
```

### 3. 在 OB1/FC 中访问 (V3.0 嵌套式)

```pascal
(* === 常量索引推荐 === *)
CONST
    Z_AXIS  : INT := 1;    // Z轴(升降)
    X1_AXIS : INT := 2;    // X1轴(取放料横移)
    X2_AXIS : INT := 3;    // X2轴(打胶机送料)
END_CONST;

(* === 3层访问: 数组.功能块.字段 === *)

(* --- SV_Power: 使能轴 --- *)
astServoAxis[Z_AXIS].stPower.Enable := TRUE;
IF astServoAxis[Z_AXIS].stPower.Status THEN
    (* 轴已就绪，可以发运动命令 *)
END_IF;

(* --- SV_ABS: 绝对定位到150mm --- *)
astServoAxis[Z_AXIS].stAbs.Execute   := TRUE;
astServoAxis[Z_AXIS].stAbs.Position := 150.0;
astServoAxis[Z_AXIS].stAbs.Velocity := 500.0;

(* --- SV_Jog: 独立设置Jog参数(不与ABS冲突) --- *)
astServoAxis[X1_AXIS].stJog.Forward  := TRUE;
astServoAxis[X1_AXIS].stJog.Velocity := 200.0;

(* --- 状态查询: 每个FB有独立的Done/Busy/Error --- *)
IF astServoAxis[Z_AXIS].stAbs.Done THEN
    astServoAxis[Z_AXIS].stAbs.Execute := FALSE;
ELSIF astServoAxis[Z_AXIS].stAbs.Error THEN
    (* ABS出错，检查ErrorID后复位 *)
    astServoAxis[Z_AXIS].stReset.Execute := TRUE;
END_IF;

(* --- SV_Stop: 急停 --- *)
astServoAxis[Z_AXIS].stStop.Execute := TRUE;

(* --- 传感器读取 --- *)
IF NOT astServoAxis[Z_AXIS].stSensor.FwdLimit THEN
    (* 未触发正向限位，允许正方向运动 *)
END_IF;

(* --- 当前位置 --- *)
rZPos := astServoAxis[Z_AXIS].rCurrentPos;
```

---

## 设计规范

### 功能块分组嵌套式（V3.0, 对齐 PLCopen MC Part 1）

每个 SV_* 功能块对应一个独立子结构体，包含自己的命令输入和PLCopen标准状态输出：

```
TYPE ST_SvXxx :
STRUCT
    (* 命令输入区 *)    Execute/Enable/Position/Velocity/Acceleration/...
    (* 标准状态输出 *)  Done / Busy / CommandAborted / Active / Error / ErrorID
END_STRUCT;
END_TYPE
```

#### PLCopen 标准状态字段含义

| 字段 | 类型 | 含义 |
|------|------|------|
| `Done` | BOOL | 命令执行完成 |
| `Busy` | BOOL | 正在执行中 |
| `CommandAborted` | BOOL | 被新命令或急停中止 |
| `Active` | BOOL | 正在执行运动(仅运动类FB) |
| `Error` | BOOL | 有错误 |
| `ErrorID` | INT | 错误代码 |

#### 各SV功能块与PLCopen对应关系

| 子结构体 | PLCopen标准 | 核心命令 | 核心状态 |
|----------|-------------|----------|----------|
| ST_SvPower | MC_Power | Enable, StopMode | Status, Busy, Error |
| ST_SvHome | MC_Home | Execute, HomeMode, Position | Done, Busy, CommandAborted |
| ST_SvAbs | MC_MoveAbsolute | Execute, Position, Velocity, Acc, Dec, Jerk | Done, Busy, Active, CommandAborted |
| ST_SvJog | MC_MoveVelocity | Forward, Backward, Velocity, Acc, Dec, Jerk | Done, Busy, Active, CommandAborted |
| ST_SvStop | MC_Stop | Execute, Deceleration, Jerk | Done, Busy, CommandAborted |
| ST_SvHalt | MC_Halt | Execute, Deceleration, Jerk | Done, Busy, CommandAborted |
| ST_SvRel | MC_MoveRelative | Execute, Distance, Velocity, Acc, Dec, Jerk | Done, Busy, Active, CommandAborted |
| ST_SvReset | MC_Reset | Execute | Done, Busy, Error |

### 嵌套约束

- **最大嵌套深度**: ≤3层 (`astServoAxis[i].stXxx.Field`)
- **单文件定义**: 所有相关TYPE定义在同一 `.scl` 文件内（对齐 GlobalVars.db 风格）
- **避免**: 超过3层的链式引用

### 命名约定

| 前缀 | 含义 | 示例 |
|------|------|------|
| `ST_` | Structure Type | ST_ServoAxis, ST_SvPower |
| `ST_Sv` | Servo Function Block Type (伺服功能块) | ST_SvAbs, ST_SvJog, ST_SvStop |
| `st` | 结构体实例 | stPower, stAbs, stJog |
| `ast` | Array of Struct | astServoAxis |

### 命名防歧义规则

- **BOOL传感器** 必须用 `Sensor`/`Switch`/`Alarm` 后缀，禁止用 `Pos`/`Value` 等易混淆为数值的名称
- 例: `HomeSensor`(BOOL) ✅ vs `HomePos`(BOOL) ❌ → 易误解为位置值(REAL)
- **SV前缀** = 伺服控制功能块域 (如 ST_SvPower 中的 Sv 表示 Servo)

---

## 兼容性

| 平台 | 支持情况 | 说明 |
|------|----------|------|
| Siemens LSP (Dynamic) | ✅ | 单文件多TYPE原生支持，IntelliSense完整 |
| TIA Portal | ✅ | 作为 UDT (User Defined Type) 导入 |
| CODESYS | ✅ | 支持 TYPE...END_TYPE 语法 |
| GX Works3 | ⚠️ | 需转换为结构化标签格式 |

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| **V3.0.0** | **2026-05-20** | **ST_ServoAxis重大重构**: 扁平25字段四段式→按8个SV功能块分组嵌套(74字段), 单文件10个TYPE定义, 对齐PLCopen MC Part 1完整标准(每FB独立Done/Busy/CommandAborted/Error), 新增SV_Halt/SV_Rel/SV_Reset三个功能块, 新增Jerk(S型曲线)支持, 传感器独立ST_Sensor结构体 |
| V2.0.0 | 2026-05-20 | ST_ServoAxis重构: 对齐PLCopen五图标准(SV_Power/Jog/Home/Stop/ABS), 21→25字段, 四段式分区, 新增ExecuteStop/CurveType/Done/Status, 修复HomePos命名歧义→HomeSensor |
| V1.0.0 | 2026-05-20 | 初始版本，7个通用结构体
