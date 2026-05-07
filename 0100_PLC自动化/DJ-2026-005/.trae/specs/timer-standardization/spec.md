# 计时器标准化整改 Spec

## Why

当前 DJ-2026-005\_边框缓存机 项目中存在两种不同的计时器实现方式（标准IEC TON 和三菱 TON\_TIME），需要统一替换为项目 SysLib 库中定义的标准计时器功能块（FB\_TON/FB\_TOF/FB\_TONR/FB\_TP），以提高代码一致性、可维护性和跨平台兼容性。

## What Changes

* **将所有功能块中的 TON/TON\_TIME 定时器替换为 SysLib 库的 FB\_TON 功能块**

* **统一计时器调用接口和参数传递方式**

* **更新相关文档以反映新的计时器使用方式**

* **保持现有业务逻辑和时序参数不变**

### 影响范围

* **涉及文件**:

  1. `02_PLC程序/通用ST程序及变量表/conveyor/FB_1002_SingleLayerConveyor_BufferFraming.scl` (5个TON\_TIME定时器)
  2. `02_PLC程序/通用ST程序及变量表/pickplace/FB_1003_PickPlace_BufferFraming.scl` (4个TON定时器)
  3. `02_PLC程序/通用ST程序及变量表/feeder/FB_1004_GlueMachineFeeder_BufferFraming.scl` (4个TON定时器)

* **不影响文件**: common, external (未使用定时器)

* **SysLib库文件** (参考用，不修改):

  * `SysLib/timer/FB_TON.scl`

  * `SysLib/timer/FB_TOF.scl`

  * `SysLib/timer/FB_TONR.scl`

  * `SysLib/timer/FB_TP.scl`

## ADDED Requirements

### Requirement: 计时器标准化

系统 SHALL 统一使用 SysLib 库定义的 FB\_TON 系列功能块替代原有的 TON/TON\_TIME 定时器。

#### Scenario: 定时器声明替换

* **WHEN** 开发人员在 VAR 区域声明定时器变量

* **THEN** 应使用 `FB_TON` 类型替代 `TON` 或 `TON_TIME` 类型

* **示例**: `s_t动作定时器 : TON;` → `s_t动作定时器 : FB_TON;`

#### Scenario: 定时器调用接口统一

* **WHEN** 调用定时器功能块

* **THEN** 应使用标准化的 IN/PT/Q/ET 接口参数

* **示例**:

  ```pascal
  (* 旧方式 - 三菱风格 *)
  tTimerAction(IN := i_bTime_Action, PT := T#5000ms, Q => q_bTq_Action);

  (* 新方式 - SysLib FB_TON *)
  fb_t动作定时器(IN := i_bTime_Action, PT := T#5000ms, Q => q_bTq_Action, ET => q_eElapsed);
  ```

#### Scenario: 保持业务逻辑不变

* **WHEN** 替换定时器实现

* **THEN** 所有定时参数（超时时间、触发条件）和业务逻辑应保持完全一致

* **AND** 不影响现有的状态机流程和报警机制

## MODIFIED Requirements

### Requirement: 输送机功能块 (FB\_1002)

修改输送机功能块的定时器实现，从三菱 TON\_TIME 风格迁移到 SysLib FB\_TON 风格：

**当前实现** (第137-165行):

```pascal
(* TON计时器实例 *)
tTimerAction         : TON_TIME;
tTimerConveyor       : TON_TIME;
tTimerReset          : TON_TIME;
tTimerPulse          : TON_TIME;
tTimerInit           : TON_TIME;

(* 接口变量 *)
i_bTime_Action       : BOOL;
i_bTime_Conveyor     : BOOL;
// ... 更多接口变量
```

**目标实现**:

```pascal
(* FB_TON计时器实例 *)
fb_t动作定时器       : FB_TON;
fb_t输送定时器       : FB_TON;
fb_t复位定时器       : FB_TON;
fb_t脉冲定时器       : FB_TON;
fb_t初始化定时器     : FB_TON;

(* 可选: 保留ET输出用于调试显示 *)
q_eAction_Elapsed    : TIME;  // 动作定时器已过时间
q_eConveyor_Elapsed  : TIME;  // 输送定时器已过时间
// ...
```

### Requirement: 取放料功能块 (FB\_1003)

修改取放料功能块的定时器实现：

**当前实现** (第290、297-299行):

```pascal
s_t放料完成保持定时器 : TON;
s_t动作定时器         : TON;
s_t产品检测稳定定时器 : TON;
s_t初始化定时器       : TON;
```

**目标实现**:

```pascal
fb_t放料完成保持定时器 : FB_TON;
fb_t动作定时器         : FB_TON;
fb_t产品检测稳定定时器 : FB_TON;
fb_t初始化定时器       : FB_TON;
```

### Requirement: 送料机构功能块 (FB\_1004)

修改送料机构功能块的定时器实现：

**当前实现** (第173、179-181行):

```pascal
s_t通讯超时定时器     : TON;
s_t动作定时器         : TON;
s_t初始化定时器       : TON;
s_t抓料保持定时器     : TON;
```

**目标实现**:

```pascal
fb_t通讯超时定时器     : FB_TON;
fb_t动作定时器         : FB_TON;
fb_t初始化定时器       : FB_TON;
fb_t抓料保持定时器     : FB_TON;
```

## REMOVED Requirements

### Requirement: 三菱风格定时器接口

**Reason**: 三菱风格的 TON\_TIME 及其配套的独立输入/输出接口变量（i\_bTime\_xxx, q\_bTq\_xxx, i\_bTrst\_xxx）将被移除，统一采用 IEC 标准的 FB\_TON 接口。
**Migration**: 将所有定时器调用处的独立接口变量合并到 FB\_TON 的标准 IN/PT/Q/ET 参数中。

## 技术细节

### FB\_TON 接口说明 (来自 SysLib 库)

```
FUNCTION_BLOCK FB_TON
VAR_INPUT
    IN  : BOOL;   // 启动信号(上升沿触发计时)
    PT  : TIME;   // 预设延时时间(如 T#5s, T#100ms)
END_VAR
VAR_OUTPUT
    Q   : BOOL;   // 延时完成输出(ET>=PT时为TRUE)
    ET  : TIME;   // 已过时间(从0递增到PT)
END_VAR
```

### 迁移规则

1. **类型替换**: `TON` → `FB_TON`, `TON_TIME` → `FB_TON`
2. **命名建议**: 在原变量名前加 `fb_` 前缀以区分功能块实例（可选，但推荐）
3. **调用方式**: 使用功能块调用语法 `fb_name(IN:=..., PT:=..., Q=>..., ET=>...);`
4. **时间格式**: 保持 T# 格式不变（如 T#5000ms, T#10s）
5. **ET输出**: 建议添加 ET 输出变量用于调试监控（可选）

### 兼容性保证

* ✅ 扫描周期计数实现（兼容 go-gen 模拟环境）

* ✅ IEC 61131-3 标准接口

* ✅ 时间精度: ±1扫描周期（约±10ms）

* ✅ 最小延时: 10ms（1个扫描周期）

## 文档更新清单

整改完成后需同步更新以下文档：

1. 各功能块的详细设计说明书（DSN文档）
2. 各功能块的接口文档（IFC文档）
3. PLC程序设计总文档
4. 变更记录（CHG文档）

