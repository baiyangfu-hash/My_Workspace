# PLC 编程规范

## 文档标识

- **文档名称**：PLC 编程规范
- **版本号**：DEV-V1.0.4
- **最后变更时间**：2026-04-25
- **变更人**：Trae
- **审核人**：人工

## 变更记录

| 版本号 | 变更日期 | 变更类型 | 变更内容 | 变更人 | 审核人 |
| ------ | -------- | -------- | -------- | ------ | ------ |
| DEV-V1.0.4 | 2026-04-25 | 增强 | 补充§5.3 Region标记体系的使用示例代码(基于FB_1003实际应用)；完善§15检查清单的验证方法 | Trae | 人工 |
| DEV-V1.0.3 | 2026-04-25 | 增强 | 基于DJ-2026-005项目实践新增§5.3 Region标记编号体系总表(100~900完整定义)；新增§15代码审查检查清单(四维17项) | Trae | 人工 |
| DEV-V1.0.2 | 2026-04-25 | 增强 | 优化§7.1.4定时器命名推荐为tXxx简化版(减少50%长度)；新增§7.1.5计数器选型指南(含三菱FX5 COUNTER_FB_M的ST调用完整示例)；新增§7.1.6预处理与条件编译使用说明(5种方式+对比表) | Trae | 人工 |
| DEV-V1.0.2 | 2026-04-25 | 增强 | 基于FB_输送线控制程序实践反馈新增5个小节：§2.2.3 SCL注释子规范、§4.2.2外部依赖声明、§7.1.4定时器选型指南、§13.4多文件版本同步规范，完善实际程序场景覆盖 | Trae | 人工 |
| DEV-V1.0.1 | 2026-04-23 | 增强 | 基于 DJ-2026-005 项目实践重写 §11 文档规范并新增推荐架构模式 | Trae | 人工 |
| DEV-V1.0.0 | 2026-02-05 | 新增 | 创建 PLC 编程通用规则文档，包含程序结构、功能块设计、命名规范等内容 | Trae | 人工 |

---

## 1. 总则

### 1.1 目的

为了统一 PLC 编程规范，提高代码可读性、可维护性和可移植性，特制定本规范。

### 1.2 适用范围

本规范适用于所有 PLC 项目开发，包括但不限于：

- Autoshop 开发环境
- Work3 开发环境
- Codesys 开发环境
- 其他符合 IEC 61131-3 标准的开发环境

### 1.3 核心原则

1. **标准化**：遵循 IEC 61131-3 国际标准和行业最佳实践
2. **模块化**：采用功能块（FB）实现代码复用和解耦
3. **可读性**：代码结构清晰，注释完整，命名规范统一
4. **可维护性**：便于后续修改、扩展和故障排查
5. **安全性**：确保设备运行安全和人员安全

### 1.4 相关规范

| 规范编号 | 规范名称 | 版本号 | 说明 |
| -------- | -------- | ------ | ---- |
| 801 | [PLC 变量命名与功能块命名规范](../../../01_启动过程/02_基础规范/01_命名规范/801_PLC变量命名与功能块命名规范_DEV-V1.0.2.md) | DEV-V1.0.2 | 变量和 FB 命名详细规范 |
| 802 | [PLC 工作流命名规范](../../../01_启动过程/02_基础规范/01_命名规范/802_PLC工作流命名规范_DEV-V1.0.3.md) | DEV-V1.0.3 | 工作流编号和命名规范 |

---

## 2. 基础规范

### 2.1 编程语言选择

根据项目复杂度和团队技术栈，合理选择编程语言：

| 语言类型 | 适用场景 | 优先级 | 说明 |
| -------- | -------- | ------ | ---- |
| ST（结构化文本） | 复杂逻辑、算法、数据处理 | **首选** | 类似 Pascal，可读性强 |
| FBD（功能块图） | 简单逻辑、顺序控制 | 次选 | 图形化，直观易懂 |
| LD（梯形图） | 继电器逻辑替代 | 备选 | 传统电工易理解 |
| SFC（顺序功能图） | 步进流程、状态机 | 推荐 | 适合工站控制 |

### 2.2 注释规范

#### 2.2.1 文件头注释

每个程序单元（PRG/FB/FC）必须包含文件头注释：

```pascal
(* ================================================================= *)
(*  功能块名称：FB_1001_ConveyorControl_BeltConveyor                *)
(*  功能描述：皮带输送机启停控制                                     *)
(*  创建日期：2026-02-05                                             *)
(*  创建人：Trae                                                     *)
(*  版本号：V1.0.0                                                   *)
(*  修改记录：                                                        *)
(*    - V1.0.1 (2026-03-15) Trae: 新增急停处理逻辑                    *)
(* ================================================================= *)
```

#### 2.2.2 行内注释

- 关键逻辑必须添加行内注释
- 注释语言使用中文
- 注释应说明"为什么"，而非"是什么"

```pascal
(* 检测启动按钮上升沿，避免重复触发 *)
IF LDP_bStart THEN
    bMotorRun := TRUE;
END_IF;
```

#### 2.2.3 SCL (Structured Control Language) 注释子规范（DEV-V1.0.2 新增）

SCL 是西门子 TIA Portal 使用的类 Pascal 语言，注释规则如下：

**1. 支持的两种注释风格**：

| 风格 | 语法 | 适用场景 | 推荐度 |
|------|------|----------|--------|
| 块注释 | `(* *)` | 文件头、段落分隔、多行说明 | ⭐⭐⭐⭐⭐ **强制用于文件头** |
| 行注释 | `//` | 行内简短说明、变量注释 | ⭐⭐⭐⭐ **推荐用于行内** |

**2. 强制性注释要求**：

- ✅ **文件头必须使用 `(* *)` 块注释**，包含：功能块名称、功能描述、版本号、作者、变更记录
- ✅ **变量声明后必须添加注释**，格式：`i_bStart : BOOL; (* 启动信号 *)`
- ✅ **主要逻辑段必须使用段落分隔符**：
  ```pascal
  (* ==================== 模式切换段 ==================== *)
  CASE ... OF
  ...
  END_CASE;
  ```
- ✅ **复杂算法必须添加"为什么"的解释性注释**

**3. SCL 特有的注释最佳实践**：

```pascal
(* ================================================================= *)
(*  功能块：FB_1001_ConveyorControl_LineConveyor                   *)
(*  功能：输送线启停控制与速度调节                                  *)
(*  版本：V1.1.0                                                  *)
(*  作者：Trae                                                    *)
(* ================================================================= *)

FUNCTION_BLOCK FB_1001_ConveyorControl_LineConveyor
VAR_INPUT
    (* ----- 控制信号 ----- *)
    i_bStart : BOOL;           (* 启动信号（电平有效）*)
    i_bStop : BOOL;            (* 停止信号（优先级高于启动）*)

    (* ----- 传感器信号 ----- *)
    i_bPosition1Sensor : BOOL; (* 产品检测传感器 *)
END_VAR

VAR
    (* 状态字位定义：
     *   Bit 0: 模式错误
     *   Bit 1: 驱动报警
     *   Bit 2: 方向输入错误
     *)
    nStatusWord : INT := 0;
END_VAR

    (* ==================== 定时器调用段 ==================== *)
    TONR(IN := abTimerIn[0], PT := aiTimerPT[0], ...);

    (* ==================== 初始化段 ==================== *)
    IF NOT bMotorRunning THEN
        nSpeedMode := 0;  (* 电机停止时重置速度模式 *)
    END_IF;

    (* 报警激活时立即停止（安全优先级最高）*)
    IF bAlarmActive AND bMotorRunning THEN
        bMotorRunning := FALSE;
    END_IF;
```

#### 2.2.4 Region 标记注释格式规范（DEV-V1.0.4 新增）

**目的**: 为 ST 文件添加可折叠的代码大纲（Outline），提升导航效率。

**1. Region 标记基本语法**:

```st
//#region 编号_功能描述
    // ... 代码块 ...
//#endregion 编号_功能描述
```

**2. Region 内部注释格式要求（强制）**:

| 注释类型 | ✅ 正确格式 | ❌ 错误格式 | 说明 |
|----------|------------|------------|------|
| 段落分隔符 | `(* ============ *)` | `(* ============ --)` | `*` 必须成对出现 |
| 子段落标题 | `(*--- 标题 ---*)` | `(*--- 标题 ---)` | 禁止使用 `--` 单独结尾 |
| 多行说明 | `(* 说明内容 *)` | `(* 说明内容 --)` | 必须以 `*)` 结束 |

**⚠️ 常见错误示例**:

```st
// ❌ 错误：-- 结尾导致注释未关闭，后续代码被意外注释掉！
(*------------------------------------------------------------------------------
  3.1 执行器输出收集 (5类×4层) ← 各实例.o_xxx
 ------------------------------------------------------------------------------)

// ✅ 正确：* 成对出现，注释正确关闭
(*------------------------------------------------------------------------------
  3.1 执行器输出收集 (5类×4层) ← 各实例.o_xxx
 -----------------------------------------------------------------------------*)
```

**3. 编号体系规范（推荐）**:

| 前缀编号 | 功能类别 | 适用场景 | 示例 |
|----------|----------|----------|------|
| **1xx** | VAR_INPUT 输入变量 | 系统控制、手动操作、工艺参数、传感器、上游信号 | `110_系统控制信号`, `140_传感器输入` |
| **2xx** | VAR_OUTPUT 输出变量 | 执行器请求、下游信号、状态显示、报警输出 | `210_执行器请求`, `240_报警输出` |
| **3xx** | VAR 内部变量 | 状态机核心、定时器、系统变量 | `310_状态机核心`, `320_定时器` |
| **4xx** | VAR CONSTANT 常量 | 步序常量、报警码常量、定时参数 | `410_步序常量`, `420_报警码` |
| **5xx** | 主程序逻辑 | 使能处理、初始化流程、模式分发、状态汇总 | `500_使能处理`, `540_模式分发` |
| **6xx** | 自动模式状态机 | 入口检测、各步骤逻辑 | `600_自动入口`, `610_步骤1` |
| **7xx** | 手动模式控制 | 入口处理、伺服点动、气缸控制 | `700_手动入口`, `710_伺服点动` |
| **8xx** | 输入分发/预处理 | 公共信号、手动信号、传感器分发 | `810_公共信号分发` |
| **9xx** | 输出收集/后处理 | 执行器输出、下游信号、步序收集 | `910_执行器输出收集` |

**4. 实际应用示例（FB_1001 四层输送机）**:

```st
//#region 100_VAR_INPUT 输入变量定义
VAR_INPUT
    //#region 110_系统控制信号 来自主控HMI公共透传
    i_b使能   : BOOL;  // 总使能信号
    i_b自动模式 : BOOL;  // 自动运行模式选择
    //#endregion 110_系统控制信号
    
    //#region 120_工艺参数 来自HMI设定或配方
    i_r输送速度 : REAL;  // 输送带速度设定
    //#endregion 120_工艺参数
END_VAR
//#endregion 100_VAR_INPUT

//#region 900_第三部分 输出收集 将4个实例的输出汇聚为ARRAY和汇总信号
    //#region 910_执行器输出收集 5类x4层 各实例o_xxx
    (*------------------------------------------------------------------------------
      3.1 执行器输出收集 (5类×4层) ← 各实例.o_xxx
     -----------------------------------------------------------------------------*)
    o_b阻挡电磁阀[1] := fbLayer1.o_b阻挡电磁阀;
    //#endregion 910_执行器输出收集
//#endregion 900_第三部分 输出收集
```

### 2.3 缩进与格式

- 使用 **4 个空格**缩进（不使用 Tab）
- 运算符两侧添加空格
- 逗号后添加空格
- 代码块之间添加空行分隔

```pascal
IF bCondition1 AND bCondition2 THEN
    (* 执行逻辑 *)
    iResult := iValue1 + iValue2;
ELSIF bCondition3 THEN
    (* 备选逻辑 *)
    iResult := iValue3;
ELSE
    (* 默认逻辑 *)
    iResult := 0;
END_IF;
```

---

## 3. 程序结构规范

### 3.1 程序组织原则

PLC 程序 SHALL 遵循分层组织原则：

```
项目 (Project)
├── 主程序 (MAIN_PRG)
│   ├── Step 1: IO 映射层
│   ├── Step 2: 数据处理层
│   └── Step 3: FB 调用层
├── 功能块库 (FB_Lib)
│   ├── FB_100x: 基础控制 FB
│   ├── FB_200x: 主控 FB
│   └── FB_300x: 工具类 FB
├── 全局变量 (GVL)
│   ├── GVL_IO: IO 地址定义
│   ├── GVL_System: 系统全局变量
│   └── GVL_HMI: HMI 接口变量
└── 数据类型 (DUT)
    ├── DUT_IO: IO 结构体
    └── DUT_FB: FB 接口结构体
```

### 3.2 程序组织

#### 3.2.1 主程序结构

主程序（PROGRAM）SHALL 按照标准步骤组织：

```pascal
PROGRAM MAIN_PRG
VAR
    (* Step 1: DI 输入映射变量 *)
    i_bStartButton AT %IX0.0 : BOOL;
    i_bStopButton AT %IX0.1 : BOOL;
    i_bEmergencyStop AT %IX0.2 : BOOL;

    (* Step 2: 远程 DI 映射变量 *)
    i_bRemoteSensor AT %IX1.0 : BOOL;

    (* Step 3: M 区/HMI 辅助变量 *)
    i_bLxAutoMode : BOOL;

    (* Step 4: DO 输出变量 *)
    q_bMotorRun AT %QX0.0 : BOOL;
    q_bAlarmLight AT %QX0.1 : BOOL;

    (* Step 5: FB 实例 *)
    fbConveyor : FB_1001_ConveyorControl_BeltConveyor;
END_VAR

(* ========== Step 1: DI 输入映射 ==========
 * 将物理输入地址映射到逻辑变量
 * ============================================ *)
(* 映射逻辑 *)

(* ========== Step 2: 远程 DI 映射 ==========
 * 远程模块输入映射
 * ============================================ *)
(* 映射逻辑 *)

(* ========== Step 3: M 区/HMI 辅助映射 ==========
 * M 区信号和 HMI 辅助信号缓存
 * ============================================ *)
(* 缓存逻辑 *)

(* ========== Step 4: D 区数据映射 ==========
 * 数据区读取
 * ============================================ *)
(* 数据映射逻辑 *)

(* ========== Step 5: 系统状态计算 ==========
 * 计算系统状态（步序/使能/模式）
 * ============================================ *)
(* 状态计算逻辑 *)

(* ========== Step 6~N-2: FB 功能块调用 ==========
 * 调用各功能块完成业务逻辑
 * ============================================ *)
fbConveyor(
    i_bStart := i_bStartButton,
    i_bStop := i_bStopButton,
    i_bEmergencyStop := i_bEmergencyStop,
    q_bRun => q_bMotorRun,
    q_bAlarm => q_bAlarmLight
);

(* ========== Step N-1: DO 输出准备 ==========
 * 准备输出缓冲
 * ============================================ *)
(* 输出准备逻辑 *)

(* ========== Step N: DO 输出映射 ==========
 * 将输出缓冲写入物理地址
 * ============================================ *)
(* 输出映射逻辑 *)
```

#### 3.2.2 全局变量文件组织

全局变量文件（GVL）SHALL 按功能分类：

**GVL_IO.gvl** - IO 地址定义：
```pascal
VAR_GLOBAL
    (* ===== 数字量输入 DI ===== *)
    g_i_bStartButton AT %IX0.0 : BOOL;      (* 启动按钮 *)
    g_i_bStopButton AT %IX0.1 : BOOL;       (* 停止按钮 *)
    g_i_bEmergencyStop AT %IX0.2 : BOOL;    (* 急停按钮 *)

    (* ===== 数字量输出 DO ===== *)
    g_q_bMotorRun AT %QX0.0 : BOOL;         (* 电机运行 *)
    g_q_bAlarmLight AT %QX0.1 : BOOL;       (* 报警灯 *)

    (* ===== 模拟量输入 AI ===== *)
    g_i_rTemperature AT %IW0 : REAL;        (* 温度传感器 *)

    (* ===== 模拟量输出 AO ===== *)
    g_q_rSpeedRef AT %QW0 : REAL;           (* 速度给定 *)
END_VAR
```

**GVL_System.gvl** - 系统全局变量：
```pascal
VAR_GLOBAL
    (* ===== 系统模式 ===== *)
    g_bAutoMode : BOOL;                     (* 自动模式标志 *)
    g_bManualMode : BOOL;                   (* 手动模式标志 *)
    g_bDebugMode : BOOL;                    (* 调试模式标志 *)

    (* ===== 系统状态 ===== *)
    g_iSystemStep : INT;                    (* 系统步序 *)
    g_bSystemReady : BOOL;                  (* 系统就绪 *)
    g_bSystemError : BOOL;                  (* 系统故障 *)

    (* ===== 系统参数 ===== *)
    g_iCycleTime : TIME := T#100MS;         (* 循环周期 *)
END_VAR
```

### 3.3 推荐架构模式：纯逻辑功能块 + 集中式 IO 映射

基于多项目实践经验验证，推荐以下分层架构模式（适用于中大型单机设备 PLC 项目）：

#### 架构层次

```
┌─────────────────────────────────────────────┐
│              主程序 (PROGRAM)                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ Step 1  │ │ Step 2  │ │ Step 3  │ ...    │
│  │ DI映射  │ │ M区映射 │ │ DO映射  │        │
│  └────┬────┘ └────┬────┘ └────┬────┘        │
│       │           │           │              │
│  ┌────▼───────────▼───────────▼────────┐    │
│  │      Step N: FB 调用层               │    │
│  │  fb输送机()  fb取放料()  fb报警()    │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
         ↕ 纯逻辑接口（无物理地址）
┌─────────────────────────────────────────────┐
│         功能块层 (FUNCTION_BLOCK)             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ FB_1001  │ │ FB_1003  │ │ FB_2001  │     │
│  │ 纯逻辑   │ │ 纯逻辑   │ │ 纯逻辑   │     │
│  │ 无IO地址 │ │ 无IO地址 │ │ 无IO地址 │     │
│  └──────────┘ └──────────┘ └──────────┘     │
└─────────────────────────────────────────────┘
```

#### 核心原则

1. **功能块纯逻辑化**：FB 内部不包含任何物理 IO 地址（%IX/%QX/%MW/%MD），仅通过 VAR_INPUT/VAR_OUTPUT 接口与外部交互
2. **集中式 IO 映射**：所有物理地址的读写集中在主程序（PROGRAM）中完成
3. **单向数据流**：DI → 主程序变量 → FB 输入 → FB 处理 → FB 输出 → 主程序变量 → DO
4. **高可测试性**：纯逻辑 FB 可脱离硬件进行仿真测试

#### 主程序标准步骤模板

| 步骤 | 内容 | 说明 |
|------|------|------|
| Step 1 | DI 输入映射 | `%IX0..N` → `i_bXxx` 变量 |
| Step 2 | 远程 DI 映射 | 远程模块输入 → 变量 |
| Step 3 | M 区/HMI 辅助映射 | `%MXxx` → `i_bLxXxx` 缓存变量 |
| Step 4 | D 区数据映射 | `%MDxx` → 数据变量 |
| Step 5 | 系统状态计算 | 步序/使能/模式判断 |
| Step 6~N-2 | FB 功能块调用 | 传递输入参数，接收输出结果 |
| Step N-1 | DO 输出准备 | 变量 → 输出缓冲 |
| Step N | DO 输出映射 | 输出缓冲 → `%QX0..N` |

#### 适用场景

- 中大型单机设备（IO 点数 > 64）
- 多工站协作设备（≥ 2 个独立功能单元）
- 需要高可维护性和可测试性的项目
- 团队协作开发场景

---

## 4. 功能块设计规范

### 4.1 功能块设计原则

#### 4.1.1 单一职责原则

每个功能块 SHOULD 只负责一个明确的功能：

```pascal
(* ✅ 正确：单一职责 *)
FUNCTION_BLOCK FB_1001_ConveyorControl_BeltConveyor
    (* 只负责输送机的启停控制 *)
END_FUNCTION_BLOCK

(* ❌ 错误：职责过多 *)
FUNCTION_BLOCK FB_1001_ConveyorAndAlarmAndHMI
    (* 同时负责输送机、报警、HMI - 违反单一职责 *)
END_FUNCTION_BLOCK
```

#### 4.1.2 接口最小化原则

功能块接口 SHOULD 只暴露必要的输入输出：

```pascal
(* ✅ 正确：最小化接口 *)
FUNCTION_BLOCK FB_1001_ConveyorControl
VAR_INPUT
    i_bStart : BOOL;           (* 启动信号 *)
    i_bStop : BOOL;            (* 停止信号 *)
    i_bEnable : BOOL;          (* 使能信号 *)
    i_rSpeedRef : REAL;        (* 速度给定 *)
END_VAR
VAR_OUTPUT
    q_bRunning : BOOL;         (* 运行状态 *)
    q_rActualSpeed : REAL;     (* 实际速度 *)
    q_bError : BOOL;           (* 故障标志 *)
    q_iErrorCode : INT;        (* 错误码 *)
END_VAR
```

#### 4.1.3 纯逻辑原则

FB 内部 **禁止** 直接访问物理 IO 地址：

```pascal
(* ❌ 错误：直接访问物理地址 *)
FUNCTION_BLOCK FB_1001_BadExample
VAR
    bInput AT %IX0.0 : BOOL;   (* 禁止！物理地址不应出现在 FB 内部 *)
END_VAR
END_FUNCTION_BLOCK

(* ✅ 正确：通过接口传递 *)
FUNCTION_BLOCK FB_1001_GoodExample
VAR_INPUT
    i_bInput : BOOL;           (* 通过输入接口接收 *)
END_VAR
    (* 内部只使用逻辑变量 *)
END_FUNCTION_BLOCK
```

### 4.2 功能块内部结构

#### 4.2.1 标准结构模板

```pascal
FUNCTION_BLOCK FB_1001_ConveyorControl_BeltConveyor
(* ================================================================= *)
(*  功能描述：皮带输送机启停控制                                      *)
(*  输入信号：启动、停止、使能、速度给定                              *)
(*  输出信号：运行状态、实际速度、故障标志                            *)
(* ================================================================= *)

VAR_INPUT
    (* ----- 控制信号 ----- *)
    i_bStart : BOOL;               (* 启动信号（上升沿有效）*)
    i_bStop : BOOL;                (* 停止信号（下降沿有效）*)
    i_bEnable : BOOL;              (* 使能信号 *)
    i_bReset : BOOL;               (* 复位信号 *)
    i_bEmergencyStop : BOOL;       (* 急停信号 *)

    (* ----- 参数设定 ----- *)
    i_rSpeedRef : REAL;            (* 速度给定 (m/s) *)
    i_rAccelTime : REAL := 3.0;    (* 加速时间 (s) *)
    i_rDecelTime : REAL := 3.0;    (* 减速时间 (s) *)
END_VAR

VAR_OUTPUT
    (* ----- 状态输出 ----- *)
    q_bRunning : BOOL;             (* 运行状态 *)
    q_bReady : BOOL;               (* 就绪状态 *)
    q_bError : BOOL;               (* 故障标志 *)
    q_iErrorCode : INT;            (* 错误码 *)
    q_rActualSpeed : REAL;         (* 实际速度 (m/s) *)
END_VAR

VAR
    (* ----- 内部状态 ----- *)
    (* 状态机状态 *)
    internal_eState : INT := 0;    (* 0=停止 1=启动中 2=运行 3=停止中 4=故障 *)

    (* 边沿检测 *)
    internal_LDP_bStart : BOOL;    (* 启动上升沿 *)
    internal_LDF_bStop : BOOL;     (* 停止下降沿 *)

    (* 定时器 *)
    internal_tonAccel : TON;       (* 加速定时器 *)
    internal_tonDecel : TON;       (* 减速定时器 *)

    (* 内部计算 *)
    internal_rSpeedRamp : REAL;    (* 速度斜坡值 *)
END_VAR


(* ==================== 状态机主逻辑 ==================== *)

(* 边沿检测 *)
internal_LDP_bStart := i_bStart AND NOT internal_LDP_bStart_Mem;
internal_LDP_bStart_Mem := i_bStart;
internal_LDF_bStop := NOT i_bStop AND internal_LDF_bStop_Mem;
internal_LDF_bStop_Mem := i_bStop;

(* 状态机：停止态 -> 启动 -> 运行 -> 停止 -> 停止态 *)
CASE internal_eState OF
    0:  (* 停止态 *)
        IF i_bEnable AND internal_LDP_bStart AND NOT i_bEmergencyStop THEN
            internal_eState := 1;  (* 转到启动中 *)
            internal_tonAccel(IN:=TRUE, PT:=T#REAL_TO_TIME(i_rAccelTime*1000));
        END_IF
        q_bRunning := FALSE;
        q_bReady := TRUE;
        internal_rSpeedRamp := 0.0;

    1:  (* 启动中 - 加速过程 *)
        q_bRunning := TRUE;
        q_bReady := FALSE;
        (* 速度斜坡计算 *)
        IF internal_tonAccel.Q THEN
            internal_eState := 2;  (* 转到运行态 *)
            internal_rSpeedRamp := i_rSpeedRef;
        ELSE
            internal_rSpeedRamp := i_rSpeedRef * (TON_ELAPSED_TIME(internal_tonAccel) / (i_rAccelTime * 1000));
        END_IF

    2:  (* 运行态 *)
        q_bRunning := TRUE;
        q_bReady := TRUE;
        internal_rSpeedRamp := i_rSpeedRef;
        IF internal_LDF_bStop OR i_bEmergencyStop OR NOT i_bEnable THEN
            internal_eState := 3;  (* 转到停止中 *)
            internal_tonDecel(IN:=TRUE, PT:=T#REAL_TO_TIME(i_rDecelTime*1000));
        END_IF

    3:  (* 停止中 - 减速过程 *)
        q_bRunning := TRUE;
        q_bReady := FALSE;
        IF internal_tonDecel.Q THEN
            internal_eState := 0;  (* 回到停止态 *)
            internal_rSpeedRamp := 0.0;
        ELSE
            internal_rSpeedRamp := i_rSpeedRef * (1.0 - TON_ELAPSED_TIME(internal_tonDecel) / (i_rDecelTime * 1000));
        END_IF

    4:  (* 故障态 *)
        q_bRunning := FALSE;
        q_bReady := FALSE;
        q_bError := TRUE;
        IF i_bReset THEN
            internal_eState := 0;  (* 复位回停止态 *)
            q_bError := FALSE;
            q_iErrorCode := 0;
        END_IF
END_CASE

(* 急停处理 - 最高优先级 *)
IF i_bEmergencyStop THEN
    internal_eState := 4;
    q_iErrorCode := 1;  (* 急停错误码 *)
END_IF

(* 输出赋值 *)
q_rActualSpeed := internal_rSpeedRamp;

END_FUNCTION_BLOCK
```

#### 4.2.2 外部变量依赖声明规范（DEV-V1.0.2 新增）

**适用场景**：当 FB 的 VAR 声明不在 FB 内部，而是在调用方主程序（PROGRAM）或全局变量文件（GVL）中定义时。

**问题背景**：
在某些项目实践中（特别是从编译器导出或改造的程序），FB 的变量可能在外部声明，导致 FB 代码本身不包含 VAR 区域。这种情况下必须添加清晰的依赖声明注释。

**标准模板**：

```pascal
FUNCTION_BLOCK FB_1001_ConveyorControl_LineConveyor
(* ================================================================= *)
(*  ⚠️ 外部变量依赖声明                                            *)
(*  本FB的VAR声明位于调用方主程序（PROGRAM）中                      *)
(*  调用前请确保以下变量已正确定义：                                *)
(*                                                                  *)
(*  输入接口 (VAR_INPUT):                                           *)
(*    i_bStart, i_bStop, i_bReset, i_bPosition1Sensor,             *)
(*    i_bDriveAlarm, i_iMainControlMode, i_iMotorDirection,         *)
(*    i_iSlowDelayTime, i_rSpeedFrequency                           *)
(*                                                                  *)
(*  输出接口 (VAR_OUTPUT):                                          *)
(*    q_bMotorRunning, q_bMotorFault, q_iMotorDirection,            *)
(*    q_bProductInPlaceDone, q_rSpeedOutput, q_iStatusWord         *)
(*                                                                  *)
(*  内部状态 (VAR):                                                 *)
(*    bManualMode, bAutoMode, bMotorRunning, bMotorFault,           *)
(*    nSpeedMode, nCurrentMotorDirection, bPosition1Detected,       *)
(*    bAutoSequenceActive, bProductInPlaceDone, nCurrentMode,       *)
(*    bModeError, nStatusWord, bAlarmActive, bAlarmReadyForReset,   *)
(*    bStartRequested, bStopRequested, rCurrentSpeed, rSpeedInput   *)
(*                                                                  *)
(*  定时器数组 (VAR):                                               *)
(*    abTimerIn[0..2], abTimerQ[0..2], abTimerR[0..2],              *)
(*    aiTimerPT[0..2], aiTimerET[0..2]                              *)
(*                                                                  *)
(*  变量定义参考：[文件路径/位置]                                    *)
(*  最后更新：2026-04-25                                             *)
(* ================================================================= *)

    (* FB逻辑代码直接使用上述外部变量 ... *)
```

**强制要求**：

| 要求 | 说明 | 违规后果 |
|------|------|----------|
| 必须在 FB 头部添加 | 紧跟 FUNCTION_BLOCK 声明之后 | ❌ 无法理解变量来源 |
| 分类列出所有变量 | 按 INPUT/OUTPUT/VAR 分组 | ❌ 遗漏关键变量 |
| 标注变量定义位置 | 指明在哪个文件中声明 | ❌ 维护困难 |
| 包含更新日期 | 方便追踪同步状态 | ❌ 版本不一致 |

**推荐做法**（优先级从高到低）：

1. ⭐⭐⭐⭐⭐ **最佳实践**：将 VAR 声明移入 FB 内部（纯逻辑化）
2. ⭐⭐⭐⭐ **可接受**：VAR 在外部但添加完整的依赖声明
3. ⭐⭐ **不推荐**：VAR 在外部且无任何声明（仅限遗留代码快速修复）

### 4.3 功能块实例化规范

在主程序中实例化功能块时，SHALL 遵循以下规范：

```pascal
PROGRAM MAIN_PRG
VAR
    (* 功能块实例 - 使用有意义的实例名 *)
    fbConveyor_Main : FB_1001_ConveyorControl_BeltConveyor;  (* 主输送线 *)
    fbConveyor_Sub : FB_1001_ConveyorControl_BeltConveyor;   (* 副输送线 *)
    fbGripper_Robot : FB_1001_GraspControl_EndEffectorGripper;  (* 机器人夹爪 *)
END_VAR
```

---

## 5. 变量声明规范

### 5.1 变量声明位置

| 变量类型 | 声明位置 | 作用域 | 示例 |
| -------- | -------- | ------ | ---- |
| VAR_INPUT | FB/FC 接口 | 输入参数 | `i_bStart` |
| VAR_OUTPUT | FB/FC 接口 | 输出参数 | `q_bRun` |
| VAR_IN_OUT | FB/FC 接口 | 双向参数 | `iq_bData` |
| VAR | FB/FC/PRG 内部 | 局部变量 | `bTemp` |
| VAR_GLOBAL | GVL 文件 | 全局变量 | `g_bSysMode` |
| VAR_TEMP | FB/FC 内部 | 临时变量 | `temp_iCnt` |
| VAR_CONSTANT | 任意位置 | 常量 | `MAX_SPEED` |

### 5.2 变量命名示例

```pascal
VAR_INPUT
    (* 布尔型输入 - i_b 前缀 *)
    i_bStart : BOOL;                 (* 启动信号 *)
    i_bSensor1 : BOOL;               (* 传感器 1 *)

    (* 整数型输入 - i_i 前缀 *)
    i_iSetPoint : INT;               (* 设定值 *)
    i_iCount : INT;                  (* 计数值 *)

    (* 实数型输入 - i_r 前缀 *)
    i_rTemperature : REAL;           (* 温度值 *)
    i_rPressure : REAL;              (* 压力值 *)
END_VAR

VAR_OUTPUT
    (* 布尔型输出 - q_b 前缀 *)
    q_bRunning : BOOL;               (* 运行状态 *)
    q_bAlarm : BOOL;                 (* 报警标志 *)

    (* 整数型输出 - q_i 前缀 *)
    q_iPosition : INT;               (* 位置值 *)
    q_iStatus : INT;                 (* 状态码 *)
END_VAR

VAR
    (* 内部布尔变量 - b 前缀 *)
    bFlag1 : BOOL;                   (* 标志 1 *)
    bLdpStart : BOOL;                (* 启动上升沿 *)

    (* 内部整数变量 - i 前缀 *)
    iCounter : INT;                  (* 计数器 *)
    iIndex : INT;                    (* 索引 *)

    (* 内部实数变量 - r 前缀 *)
    rCalcResult : REAL;              (* 计算结果 *)
    rFilterValue : REAL;             (* 滤波值 *)
END_VAR
```

### 5.3 初始值规范

- 所有变量 SHOULD 明确指定初始值
- 布尔型默认为 `FALSE`
- 数值型默认为 `0`
- 字符串默认为空字符串 `''`

```pascal
VAR
    (* ✅ 正确：明确初始值 *)
    bInitialized : BOOL := FALSE;
    iRetryCount : INT := 0;
    rMaxPressure : REAL := 100.0;
    sDeviceName : STRING := '';

    (* ⚠️ 不推荐：依赖系统默认值 *)
    bUnknown : BOOL;                (* 初始值不确定 *)
END_VAR
```

### 5.4 Region标记编号体系 (DEV-V1.0.3 新增)

#### 5.4.1 编号规则总表

| 编号段 | 区域名称 | 用途说明 | 适用位置 | 典型内容 |
|:-----:|---------|---------|---------|----------|
| **100** | VAR_INPUT | 输入变量声明 | PRG/FB顶部 | 系统控制、工艺参数、传感器输入 |
| **200** | VAR_OUTPUT | 输出变量声明 | PRG/FB顶部 | 执行器请求、下游信号、状态显示 |
| **300** | VAR | 内部变量/静态变量 | PRG/FB内部 | 状态机核心、定时器、系统变量 |
| **400** | VAR_CONSTANT | 常量定义 | PRG/FB顶部 | 步序常量、报警码常量、定时参数 |
| **500** | 主程序逻辑 | 调度与主流程 | PRG_Main | 使能处理、初始化、模式分发、状态汇总 |
| **600** | 自动状态机 | CASE自动运行逻辑 | 业务FB内部 | 各步骤的状态转换与动作输出 |
| **700** | 手动控制 | JOG/手动操作逻辑 | 业务FB内部 | 伺服点动、气缸手动操作 |
| **800** | 输入分发 | IO→FB映射 | PRG_Main | 公共信号、手动操作、传感器信号分发 |
| **900** | 输出收集 | FB→IO映射 | PRG_Main | 执行器输出、下游信号、步序收集 |

#### 5.4.2 使用示例 (ST语言，基于FB_1003边框缓存机实际应用)

以下示例展示完整的Region标记使用方法，涵盖100~700编号段的典型应用场景：

```st
FUNCTION_BLOCK FB_1003_BufferMachine_BorderFrameCache
(* ================================================================= *)
(*  功能块名称：FB_1003_BufferMachine_BorderFrameCache               *)
(*  功能描述：边框缓存机主控功能块（DJ-2026-005项目）                *)
(*  创建日期：2026-04-25                                             *)
(*  创建人：Trae                                                     *)
(*  版本号：V1.0.0                                                   *)
(* ================================================================= *)

//#region 100_VAR_INPUT 输入变量声明
VAR_INPUT
    //#region 110_系统控制信号 来自主控HMI公共透传
    i_b使能       : BOOL;   (* 总使能信号 *)
    i_b自动模式     : BOOL;   (* 自动运行模式选择 *)
    i_b复位       : BOOL;   (* 复位信号（上升沿有效）*)
    //#endregion 110_系统控制信号

    //#region 120_工艺参数 来自HMI设定或配方
    i_r缓存速度     : REAL;   (* 缓存输送带速度设定 m/s *)
    i_i边框数量上限   : INT;    (* 单次缓存边框数量限制 *)
    //#endregion 120_工艺参数

    //#region 130_传感器输入 来自现场传感器
    i_b入口检测     : BOOL;   (* 入口光电传感器 *)
    i_b出口检测     : BOOL;   (* 出口光电传感器 *)
    i_b满料检测     : BOOL;   (* 满料检测传感器 *)
    //#endregion 130_传感器输入

    //#region 140_上游信号 来自上游工站或主控
    i_b上游就绪     : BOOL;   (* 上游工站就绪信号 *)
    i_b下游请求     : BOOL;   (* 下游工站取料请求 *)
    //#endregion 140_上游信号
END_VAR
//#endregion 100_VAR_INPUT

//#region 200_VAR_OUTPUT 输出变量声明
VAR_OUTPUT
    //#region 210_执行器请求 送往输出收集层(900)
    o_b输送运行     : BOOL;   (* 缓存输送带运行请求 *)
    o_b阻挡升       : BOOL;   (* 阻挡气缸上升请求 *)
    o_b阻挡降       : BOOL;   (* 阻挡气缸下降请求 *)
    //#endregion 210_执行器请求

    //#region 220_下游信号 送往下游工站或主控
    o_b本站就绪     : BOOL;   (* 本站就绪信号 *)
    o_b有料可取     : BOOL;   (* 有边框可供下游取出 *)
    o_i当前缓存数    : INT;    (* 当前缓存数量 *)
    //#endregion 220_下游信号

    //#region 230_状态显示 送往HMI显示
    o_b运行中      : BOOL;   (* 自动运行中标志 *)
    o_b故障       : BOOL;   (* 故障标志 *)
    o_i故障码      : INT;    (* 故障代码 *)
    o_i当前步序     : INT;    (* 当前自动步序 *)
    //#endregion 230_状态显示
END_VAR
//#endregion 200_VAR_OUTPUT

//#region 300_VAR 内部变量声明
VAR
    //#region 310_状态机核心变量
    eAutoStep      : INT := 0;  (* 自动状态机当前步序 *)
    eAutoStepNext   : INT := 0;  (* 自动状态机下一步序 *)
    bAutoActive    : BOOL;      (* 自动运行激活标志 *)
    //#endregion 310_状态机核心变量

    //#region 320_边沿检测变量
    trig复位       : R_TRIG;   (* 复位按钮上升沿 *)
    trig入口检测     : R_TRIG;   (* 入口检测上升沿 *)
    trig出口检测     : R_TRIG;   (* 出口检测上升沿 *)
    //#endregion 320_边沿检测变量

    //#region 330_定时器实例
    t输送延时      : TON;      (* 输送到位延时 *)
    t阻挡动作      : TON;      (* 阻挡气缸动作时间 *)
    //#endregion 330_定时器实例

    //#region 340_内部计算变量
    iCurrentCount   : INT := 0;  (* 当前计数 *)
    bEntryFlag     : BOOL;      (* 入口标志 *)
    //#endregion 340_内部计算变量
END_VAR
//#endregion 300_VAR

//#region 400_VAR_CONSTANT 常量定义
VAR CONSTANT
    //#region 410_步序常量定义
    STEP_IDLE      : INT := 0;   (* 空闲等待步 *)
    STEP_ENTRY_DETECT : INT := 10; (* 入口检测步 *)
    STEP_CONVEY_IN  : INT := 20;  (* 输送入库步 *)
    STEP_COUNT_CHECK : INT := 30; (* 计数检查步 *)
    STEP_FULL_WAIT  : INT := 40;  (* 满料等待步 *)
    STEP_ERROR     : INT := 90;  (* 错误处理步 *)
    //#endregion 410_步序常量定义

    //#region 420_报警码常量定义
    ALM_NONE      : INT := 0;    (* 无报警 *)
    ALM_SENSOR_ERR  : INT := 3001; (* 传感器故障 *)
    ALM_TIMEOUT    : INT := 3002; (* 超时报警 *)
    ALM_FULL_OVERFLOW : INT := 3003; (* 满料溢出 *)
    //#endregion 420_报警码常量定义

    //#region 430_定时参数常量
    TIME_CONVEY_POS : TIME := T#3S;  (* 输送定位时间 *)
    TIME_CYLINDER   : TIME := T#500MS; (* 气缸动作时间 *)
    //#endregion 430_定时参数常量
END_VAR
//#endregion 400_VAR_CONSTANT

//#region 500_主程序逻辑 使能处理与初始化
    (*------------------------------------------------------------------------------
      5.1 使能判断与初始化
     -----------------------------------------------------------------------------*)
    IF NOT i_b使能 THEN
        (* 未使能时重置所有输出 *)
        o_b输送运行 := FALSE;
        o_b阻挡升 := FALSE;
        o_b阻挡降 := FALSE;
        o_b运行中 := FALSE;
        eAutoStep := STEP_IDLE;
        RETURN;  (* 退出本次扫描 *)
    END_IF;

    (*------------------------------------------------------------------------------
      5.2 边沿检测
     -----------------------------------------------------------------------------*)
    trig复位(CLK := i_b复位);
    trig入口检测(CLK := i_b入口检测);
    trig出口检测(CLK := i_b出口检测);

    (*------------------------------------------------------------------------------
      5.3 模式分发
     -----------------------------------------------------------------------------*)
    IF i_b自动模式 THEN
        o_b运行中 := TRUE;
        bAutoActive := TRUE;
    ELSE
        o_b运行中 := FALSE;
        bAutoActive := FALSE;
        (* 手动模式时清除状态机 *)
        eAutoStep := STEP_IDLE;
    END_IF;
//#endregion 500_主程序逻辑

//#region 600_自动状态机 CASE自动运行逻辑
IF bAutoActive THEN
    CASE eAutoStep OF
        //#region 610_STEP_IDLE 空闲等待
        STEP_IDLE:
            o_b本站就绪 := TRUE;
            IF trig入口检测.Q AND i_b上游就绪 THEN
                eAutoStep := STEP_ENTRY_DETECT;
            END_IF;
        //#endregion 610_STEP_IDLE

        //#region 620_STEP_ENTRY_DETECT 入口检测确认
        STEP_ENTRY_DETECT:
            (* 延时确认防抖动 *)
            t输送延时(IN := TRUE, PT := T#200MS);
            IF t输送延时.Q AND i_b入口检测 THEN
                iCurrentCount := iCurrentCount + 1;
                bEntryFlag := TRUE;
                t输送延时(IN := FALSE);
                eAutoStep := STEP_CONVEY_IN;
            ELSIF NOT i_b入口检测 THEN
                t输送延时(IN := FALSE);  (* 误触发，重置 *)
            END_IF;
        //#endregion 620_STEP_ENTRY_DETECT

        //#region 630_STEP_CONVEY_IN 输送入库
        STEP_CONVEY_IN:
            o_b输送运行 := TRUE;
            o_b阻挡降 := TRUE;  (* 降下阻挡放行 *)
            t输送延时(IN := TRUE, PT := TIME_CONVEY_POS);
            IF t输送延时.Q THEN
                o_b输送运行 := FALSE;
                o_b阻挡降 := FALSE;
                t输送延时(IN := FALSE);
                eAutoStep := STEP_COUNT_CHECK;
            END_IF;
        //#endregion 630_STEP_CONVEY_IN

        //#region 640_STEP_COUNT_CHECK 计数判断
        STEP_COUNT_CHECK:
            IF iCurrentCount >= i_i边框数量上限 OR i_b满料检测 THEN
                (* 已达上限或检测到满料 *)
                o_b有料可取 := TRUE;
                eAutoStep := STEP_FULL_WAIT;
            ELSE
                (* 继续接收 *)
                eAutoStep := STEP_IDLE;
            END_IF;
        //#endregion 640_STEP_COUNT_CHECK

        //#region 650_STEP_FULL_WAIT 满料等待取料
        STEP_FULL_WAIT:
            o_b阻挡升 := TRUE;  (* 升起阻挡 *)
            IF i_b下游请求 AND trig出口检测.Q THEN
                (* 下游取走一个 *)
                iCurrentCount := iCurrentCount - 1;
                o_b阻挡升 := FALSE;
                IF iCurrentCount = 0 THEN
                    o_b有料可取 := FALSE;
                END_IF;
                eAutoStep := STEP_IDLE;
            END_IF;
        //#endregion 650_STEP_FULL_WAIT

        //#region 690_STEP_ERROR 错误处理
        STEP_ERROR:
            o_b故障 := TRUE;
            o_i故障码 := ALM_NONE;
            IF trig复位.Q THEN
                (* 故障复位 *)
                o_b故障 := FALSE;
                o_i故障码 := ALM_NONE;
                iCurrentCount := 0;
                eAutoStep := STEP_IDLE;
            END_IF;
        //#endregion 690_STEP_ERROR

        ELSE
            (* 未知步序 → 错误处理 *)
            eAutoStep := STEP_ERROR;
            o_i故障码 := ALM_SENSOR_ERR;
    END_CASE;

    (* 步序切换 *)
    eAutoStep := eAutoStepNext;
    eAutoStepNext := eAutoStep;  (* 默认保持当前步 *)
END_IF;
//#endregion 600_自动状态机

//#region 700_手动控制 JOG/手动操作逻辑
IF NOT i_b自动模式 AND i_b使能 THEN
    (*------------------------------------------------------------------------------
      7.1 手动模式下允许的操作
     -----------------------------------------------------------------------------*)
    (* 注意：手动操作的具体实现通常在PRG层的800区域进行，
       此处仅预留接口和基本安全互锁 *)

    (* 手动模式下确保状态机不运行 *)
    bAutoActive := FALSE;

    (* 手动模式下的安全输出复位 *)
    o_b输送运行 := FALSE;
    o_b阻挡升 := FALSE;
    o_b阻挡降 := FALSE;
END_IF;
//#endregion 700_手动控制

END_FUNCTION_BLOCK
```

**在主程序(PRG)中的800/900区域使用示例**：

```st
PROGRAM PRG_Main_BufferMachine
VAR
    //#region 810_输入分发 IO→FB映射
    (* 将物理IO和HMI信号分发到FB实例的输入接口 *)
    //#endregion 810_输入分发

    //#region 910_输出收集 FB→IO映射
    (* 将FB实例的输出汇聚到物理IO和HMI显示 *)
    //#endregion 910_输出收集
END_VAR

//#region 800_输入分发层
//#region 810_公共信号分发
fbBuffer.i_b使能 := g_bSystemEnable;
fbBuffer.i_b自动模式 := g_bAutoMode;
fbBuffer.i_b复位 := g_bResetBtn;
//#endregion 810_公共信号分发

//#region 820_传感器信号分发
fbBuffer.i_b入口检测 := g_i_bSensor_Entry;
fbBuffer.i_b出口检测 := g_i_bSensor_Exit;
fbBuffer.i_b满料检测 := g_i_bSensor_Full;
//#endregion 820_传感器信号分发
//#endregion 800_输入分发层

//#region 900_输出收集层
//#region 910_执行器输出收集
g_q_bConveyorRun := fbBuffer.o_b输送运行;
g_q_bCylinderUp := fbBuffer.o_b阻挡升;
g_q_bCylinderDown := fbBuffer.o_b阻挡降;
//#endregion 910_执行器输出收集

//#region 920_HMI状态显示收集
g_qHmi_Ready := fbBuffer.o_b本站就绪;
g_qHmi_Running := fbBuffer.o_b运行中;
g_qHmi_Error := fbBuffer.o_b故障;
g_qHmi_Step := fbBuffer.o_i当前步序;
g_qHmi_AlarmCode := fbBuffer.o_i故障码;
//#endregion 920_HMI状态显示收集
//#endregion 900_输出收集层
```

> **使用要点说明**：
> - **100~400区域**位于FB/PRG顶部的VAR声明段内，用于组织变量分组
> - **500~700区域**位于FB内部的逻辑代码段，用于组织功能模块
> - **800~900区域**仅在PRG主程序中使用，用于IO映射和解耦
> - Region标记必须配对出现：`#region` 与 `#endregion`
> - 编号后跟下划线和简短的功能描述，便于IDE折叠导航

---

## 6. 程序流程控制规范

### 6.1 条件判断

#### 6.1.1 IF-ELSIF-ELSE 结构

```pascal
(* 标准 IF 结构 *)
IF condition1 THEN
    (* 处理逻辑 1 *)
ELSIF condition2 THEN
    (* 处理逻辑 2 *)
ELSIF condition3 THEN
    (* 处理逻辑 3 *)
ELSE
    (* 默认处理 *)
END_IF;
```

#### 6.1.2 CASE 结构（状态机）

```pascal
(* 状态机实现 *)
CASE iCurrentStep OF
    0:  (* 初始化步 *)
        (* 初始化逻辑 *)
        IF bInitComplete THEN
            iNextStep := 10;
        END_IF

    10: (* 等待步 *)
        (* 等待条件判断 *)
        IF bStartCondition THEN
            iNextStep := 20;
        ELSIF bTimeout THEN
            iNextStep := 90;  (* 超时错误步 *)
        END_IF

    20: (* 执行步 *)
        (* 执行逻辑 *)
        IF bComplete THEN
            iNextStep := 30;
        END_IF

    90: (* 错误处理步 *)
        (* 错误处理 *)
        IF bReset THEN
            iNextStep := 0;  (* 复位回初始化 *)
        END_IF

ELSE
    (* 未知状态处理 *)
    iNextStep := 0;
END_CASE

(* 步序切换 *)
iCurrentStep := iNextStep;
```

### 6.2 循环结构

#### 6.2.1 FOR 循环

```pascal
(* 标准 FOR 循环 *)
FOR iIndex := 1 TO MAX_COUNT DO
    (* 循环体 *)
    aData[iIndex] := iIndex * 2;
END_FOR;

(* 带步长的 FOR 循环 *)
FOR iIndex := 0 TO 100 BY 5 DO
    (* 步长为 5 *)
END_FOR;
```

#### 6.2.2 WHILE 循环

```pascal
(* WHILE 循环 - 注意防止死循环 *)
iIndex := 0;
WHILE iIndex < MAX_COUNT AND NOT bExitFlag DO
    (* 循环体 *)
    iIndex := iIndex + 1;

    (* 安全退出条件 *)
    IF iIndex > MAX_SAFE_LIMIT THEN
        EXIT;  (* 强制退出 *)
    END_IF
END_WHILE;
```

#### 6.2.3 REPEAT 循环

```pascal
(* REPEAT 循环 - 至少执行一次 *)
REPEAT
    (* 循环体 *)
    iIndex := iIndex + 1;
UNTIL iIndex >= MAX_COUNT OR bComplete
END_REPEAT;
```

### 6.3 跳转语句

```pascal
(* EXIT - 退出循环 *)
FOR i := 1 TO 100 DO
    IF bFound THEN
        EXIT;  (* 找到目标，立即退出 *)
    END_IF
END_FOR;

(* RETURN - 退出函数/功能块 *)
FUNCTION CheckValue : BOOL
VAR_INPUT
    iValue : INT;
END_VAR
    IF iValue < 0 THEN
        CheckValue := FALSE;
        RETURN;  (* 提前返回 *)
    END_IF

    CheckValue := (iValue > 0);
END_FUNCTION
```

---

## 7. 常用功能块库规范

### 7.1 标准功能块使用

#### 7.1.1 定时器

```pascal
VAR
    tonDelay : TON;      (* 通电延时 *)
    tofDelay : TOF;      (* 断电延时 *)
    tpPulse : TP;        (* 单脉冲 *)
    tonrAccum : TONR;    (* 累加计时器 *)
END_VAR

(* 通电延时 - 延时 3 秒后输出 ON *)
tonDelay(
    IN := bStartSignal,
    PT := T#3S
);
bDelayedOutput := tonDelay.Q;

(* 单脉冲 - 输入 ON 时输出 500ms 脉冲 *)
tpPulse(
    IN := bTrigger,
    PT := T#500MS
);
bPulseOutput := tpPulse.Q;
```

#### 7.1.2 计数器

```pascal
VAR
    ctuUp : CTU;         (* 加计数器 *)
    ctdDown : CTD;       (* 减计数器 *)
    ctudUpDown : CTUD;   (* 加减计数器 *)
END_VAR

(* 加计数器 - 计数到 100 后输出 ON *)
ctuUp(
    CU := bCountPulse,
    R := bReset,
    PV := 100
);
iCurrentValue := ctuUp.CV;
bCountDone := ctuUp.Q;
```

#### 7.1.3 边沿检测

```pascal
VAR
    (* 上升沿检测 - 使用 R_TRIG *)
    trigRise : R_TRIG;
    (* 下降沿检测 - 使用 F_TRIG *)
    trigFall : F_TRIG;
END_VAR

(* 上升沿检测 *)
trigRise(CLK := bInput);
bRisingEdge := trigRise.Q;

(* 下降沿检测 *)
trigFall(CLK := bInput);
bFallingEdge := trigFall.Q;
```

#### 7.1.4 定时器使用选型指南（DEV-V1.0.2 新增）

**选型决策树**：

```
FB 内需要使用定时器？
│
├─ 定时器数量 ≤ 3 个？
│   ├─ 是 → 使用独立定时器实例（推荐）
│   │   ✅ 命名清晰：tonDelay, toffDelay, tpPulse
│   │   ✅ 调试方便：可单独监控每个定时器状态
│   │   ✅ 代码直观：一目了然每个定时器的用途
│   │
│   └─ 否 → 继续判断
│
├─ 定时器数量 ≥ 4 个 且 功能相似？
│   ├─ 是 → 使用定时器数组（推荐）
│   │   ✅ 节省代码行数
│   │   ✅ 统一管理，便于批量操作
│   │   ⚠️ 必须添加索引说明注释
│   │
│   └─ 否 → 混合使用（独立+数组）
```

**场景A：独立定时器实例（≤3个）**

```pascal
VAR
    (* 独立定时器 - 每个有明确的语义名称 *)
    tonProductDetect : TON;     (* 产品检测延时 (3s) *)
    toffSlowRun : TOF;          (* 慢速保持 (1s) *)
    tpAlarmPulse : TP;          (* 报警脉冲 (500ms) *)
END_VAR

(* 使用示例 - 清晰明了 *)
tonProductDetect(IN := bSensor, PT := T#3S);
IF tonProductDetect.Q THEN
    bProductDetected := TRUE;
END_IF;
```

**场景B：定时器数组（≥4个，功能相似）**

```pascal
VAR
    (* 定时器数组 [索引说明必须注释] *)
    (* [0]: 产品到位复位 (固定3s) *)
    (* [1]: 慢速运行延时 (可配置) *)
    (* [2]: 报警持续时间 (固定5s) *)
    (* [3]: 通信超时检测 (固定2s) *)
    abTimerIn  : ARRAY [0..3] OF BOOL;   (* 输入信号 *)
    abTimerQ  : ARRAY [0..3] OF BOOL;   (* 输出信号 *)
    abTimerR  : ARRAY [0..3] OF BOOL;   (* 复位信号 *)
    aiTimerPT : ARRAY [0..3] OF DINT;  (* 预设值 ms *)
    aiTimerET : ARRAY [0..3] OF DINT;  (* 当前值 ms *)
END_VAR

(* 循环调用所有定时器 *)
FOR iIndex := 0 TO 3 DO
    TONR(
        IN  := abTimerIn[iIndex],
        PT  := aiTimerPT[iIndex],
        R   := abTimerR[iIndex],
        Q   => abTimerQ[iIndex],
        ET  => aiTimerET[iIndex]
    );
END_FOR;

(* 使用时通过索引访问，需配合注释理解 *)
IF abTimerQ[0] THEN
    (* 定时器[0]触发：产品到位复位 *)
    bProductInPlace := FALSE;
END_IF;
```

**命名规范对比**：

| 方式 | 输入数组 | 输出数组 | 复位数组 | 预设值数组 | 当前值数组 |
|------|----------|----------|----------|------------|------------|
| **⭐推荐（V1.0.3简化版）** | **`tIn`** | **`tQ`** | **`tR`** | **`tPt`** | **`tEt`** |
| 旧版兼容 | `abTimerIn` | `abTimerQ` | `abTimerR` | `aiTimerPT` | `aiTimerET` |
| ❌ 不推荐 | `In_tTimer1` | `Q_tTimer1` | `R_tTimer1` | `PT_tTimer1` | `ET_tTimer1` |

> **V1.0.3更新**：推荐使用简化的 `tXxx` 命名（4~5字符），比旧版 `abTimerXx`(9~12字符) 减少50%+长度，详见801规范§4.3.3

**强制要求（使用数组时）**：
- ✅ 必须在 VAR 声明上方添加索引功能说明注释
- ✅ 每个索引必须有明确的功能描述和预设值说明
- ✅ 数组大小应与实际使用的数量匹配（避免浪费）
- ✅ 预设值应在逻辑段中集中更新（便于维护）

#### 7.1.5 计数器使用选型指南（DEV-V1.0.3 新增）

**适用范围**：IEC 61131-3 标准计数器 (CTU/CTD/CTUD) 及厂商扩展计数器FB（如三菱FX5系列 COUNTER_FB）

**选型决策树**：

```
需要使用计数功能？
│
├─ 计数方向？
│   ├─ 仅递增 → CTU (Count Up)
│   │   适用：产品计数、循环次数统计、脉冲计数
│   │
│   ├─ 仅递减 → CTD (Count Down)
│   │   适用：倒计时、库存扣减、剩余次数
│   │
│   └─ 双向（可增可减）→ CTUD (Count Up/Down)
│       适用：双向计数、进出平衡统计
│
├─ 使用方式？
│   ├─ 单个独立计数器 → 独立实例（推荐≤3个时）
│   └─ 多个同类计数器 → 数组方式（推荐≥4个时）
│
└─ 厂商特殊需求？
    └─ 三菱FX5系列 → 使用封装FB: COUNTER_FB_M / COUNTER_FB_S
        （见下方ST调用示例）
```

**场景A：标准IEC计数器实例（西门子/通用）**

```pascal
VAR
    (* 独立计数器 - 产品计数示例 *)
    ctProductCount : CTU;       (* 递增计数器：统计通过的产品数 *)
    ctCycleCount : CTUD;         (* 双向计数器：统计设备循环次数 *)
END_VAR

(* 递增计数器使用 - 每检测到一个产品加1 *)
ctProductCount(CU := bProductDetected, RESET := bResetCounter, PV := 1000);
nTotalProducts := ctProductCount.CV;  (* 当前计数值 *)
bCountDone := ctProductCount.Q;      (* 达到设定值标志 *)

(* 双向计数器使用 - 进出平衡统计 *)
ctCycleCount(CU := bEntrySensor, CD := bExitSensor, RESET := bReset, PV := 50);
nNetCount := ctCycleCount.CV;        (* 净计数值 (入-出) *)
```

**场景B：三菱FX5系列计数器FB（用户提供的图片示例）**

根据您提供的 FX5S/FX5UJ/FX5U/FX5UC 系列文档：

```st
(* ================================================================= *)
(* 三菱FX5系列 - 计数器FB在ST中的标准调用方式                      *)
(* 功能块: COUNTER_FB_M (16位有符号增计数器)                       *)
(* 执行条件成立时，执行增计数                                      *)
(* ================================================================= *)

VAR
    (* 计数器变量 - 遵循801规范§4.3.3 c前缀命名 *)
    cCoil   : BOOL;          (* s1: 执行条件 TRUE=执行, FALSE=停止 *)
    cPreset : INT;           (* s2: 计数器设定值 *)
    cValueIn : INT;           (* s3: 计数器初始值 *)
    cValueOut : DINT;         (* d1: 计数器当前值 (ANY16类型) *)
    cStatus  : BOOL;          (* d2: 输出状态 (达到设定值=TRUE) *)
END_VAR

(* 参数赋值 *)
cCoil := bCountEnable;              (* 外部使能信号 *)
cPreset := 1000;                   (* 目标计数值：1000个 *)
cValueIn := 0;                     (* 从0开始计数 *)

(* FB调用 - 标准ST语法 *)
COUNTER_FB_M_1(
    Coil    := cCoil,               (* 执行条件输入 *)
    Preset  := cPreset,             (* 设定值输入 *)
    ValueIn := cValueIn,            (* 初始值输入 *)
    ValueOut=> cValueOut,           (* 当前值输出 (=>表示输出参数) *)
    Status  => cStatus              (* 状态输出：达到设定值时为TRUE *)
);

(* 应用示例：产品计数完成判断 *)
IF cStatus THEN
    (* 计数达到设定值，执行相应操作 *)
    bCountComplete := TRUE;
    cCoil := FALSE;                 (* 停止计数 *)
END_IF;
```

**三菱FX5计数器FB接口对照表**（来自您的图片）：

| 梯形图端子 | ST参数名 | 变量类型 | 数据类型 | 功能说明 |
|------------|----------|----------|----------|----------|
| s1 (Coil) | `Coil` | 输入变量 | BOOL | 执行条件 (TRUE=执行计数, FALSE=停止) |
| s2 (Preset) | `Preset` | 输入变量 | INT | 计数器目标设定值 |
| s3 (ValueIn) | `ValueIn` | 输入变量 | INT | 计数器初始值 |
| d1 (ValueOut) | `ValueOut` | 输出变量 | ANY16/DINT | 计数器当前值 |
| d2 (Status) | `Status` | 输出变量 | BOOL | 输出状态 (达到PV时置TRUE) |

**计数器数组命名规范**（多计数器场景）：

```pascal
VAR
    (* 计数器数组 [索引说明必须注释] *)
    (* [0]: 产品A计数  [1]: 产品B计数  [2]: 故障次数统计 *)
    cCoil   : ARRAY [0..2] OF BOOL;   (* 执行条件 *)
    cPreset : ARRAY [0..2] OF INT;    (* 设定值 *)
    cValueIn : ARRAY [0..2] OF INT;    (* 初始值 *)
    cValueOut : ARRAY [0..2] OF DINT;  (* 当前值 *)
    cStatus : ARRAY [0..2] OF BOOL;    (* 完成状态 *)
END_VAR

(* 循环调用多个计数器 *)
FOR iIdx := 0 TO 2 DO
    COUNTER_FB_M_1(
        Coil    => cCoil[iIdx],
        Preset  => cPreset[iIdx],
        ValueIn => cValueIn[iIdx],
        ValueOut=> cValueOut[iIdx],
        Status  => cStatus[iIdx]
    );
END_FOR;
```

#### 7.1.6 预处理与条件编译在ST中的使用（DEV-V1.0.3 新增）

**背景说明**：
PLC编程中的"预处理"概念不同于C语言的 `#define` 宏定义。在 IEC 61131-3 ST 语言中，主要通过以下方式实现类似预处理的功能：

**方式1：常量定义替代宏（推荐）**

```pascal
VAR CONSTANT
    (* 设备相关常量 - 相当于预定义宏 *)
    MAX_SPEED     : REAL := 100.0;    (* 最大速度 HZ *)
    DEFAULT_DELAY : DINT := 1000;     (* 默认延时 ms *)
    ALARM_TIMEOUT : TIME := T#5S;     (* 报警超时时间 *)
    
    (* 硬件配置常量 - 便于移植时修改 *)
    CONVEYOR_COUNT : INT := 3;        (* 输送线数量 *)
    SENSOR_COUNT   : INT := 8;        (* 传感器数量 *)
END_VAR
```

**方式2：条件执行（IF语句实现运行时分支）**

```pascal
(* 运行时条件选择 - 根据模式选择不同逻辑 *)
CASE nSystemMode OF
    0: (* 调试模式 - 启用详细诊断 *)
        bDebugMode := TRUE;
        nLogLevel := 3;  (* 详细日志 *)
        
    1: (* 正常生产模式 - 优化性能 *)
        bDebugMode := FALSE;
        nLogLevel := 1;  (* 仅错误日志 *)
        
    2: (* 维护模式 - 全功能启用 *)
        bDebugMode := TRUE;
        nLogLevel := 2;  (* 警告+错误 *)
END_CASE;
```

**方式3：编译期条件（{#IF} 编译指示符，部分IDE支持）**

```pascal
(* 编译期条件 - 仅在支持的IDE中有效（如Codesys, TwinCAT）*)
{#IF defined(SIMULATION_MODE)}
    (* 仿真模式专用代码 - 编译时选择 *)
    bSimActive := TRUE;
    nCycleTime := 100;  (* 仿真加速 *)
{#ELSE}
    (* 真实硬件代码 *)
    bSimActive := FALSE;
    nCycleTime := 10;   (* 实际扫描周期 *)
{#END_IF}
```

**方式4：功能块封装实现平台抽象（最佳实践）**

```pascal
(* ================================================================= *)
(* 平台抽象层 - 通过FB封装屏蔽底层差异                           *)
(* 类似于面向对象的多态，但用FB接口实现                            *)
(* ================================================================= *)

FUNCTION_BLOCK FB_PlatformAbstract_Timer
VAR_INPUT
    bEnable : BOOL;            (* 使能 *)
    tPreset : TIME;            (* 预设时间 *)
END_VAR
VAR_OUTPUT
    bDone : BOOL;              (* 完成 *)
    tElapsed : TIME;           (* 已用时间 *)
END_VAR

(* 内部根据平台自动选择实现 - 此处为伪代码示意 *)
{#IF defined(SIEMENS_TIA)}
    (* 西门子TON实现 *)
    tonInternal(IN := bEnable, PT := tPreset, Q => bDone, ET => tElapsed);
{#ELSIF defined(MITSUBISHI_FX5)}
    (* 三菱FX5定时器FB实现 *)
    TIMER_FB_M_1(...);  (* 调用三菱封装FB *)
{#ELSE}
    (* 标准IEC实现 *)
    tonInternal(IN := bEnable, PT := tPreset, Q => bDone, ET => tElapsed);
{#END_IF}

END_FUNCTION_BLOCK
```

**方式5：配置驱动的条件逻辑（推荐用于项目实践）**

```pascal
VAR
    (* 功能开关配置 - 通过HMI或GVL设置，实现"软预处理"*)
    bFeature_ProductCounting : BOOL := TRUE;   (* 产品计数功能开关 *)
    bFeature_DataLogging     : BOOL := FALSE;  (* 数据记录功能开关 *)
    bFeature_RemoteDiagnosis : BOOL := FALSE;  (* 远程诊断功能开关 *)
    
    (* 硬件版本适配 *)
    nHardwareVersion : INT := 2;                (* 1=旧版, 2=新版 *)
END_VAR

(* 基于配置的功能裁剪 *)
IF bFeature_ProductCounting THEN
    (* 产品计数逻辑 - 可选功能 *)
    COUNTER_FB_M_1(...);
END_IF;

IF nHardwareVersion >= 2 THEN
    (* 新版硬件专属功能 *)
    ReadAdvancedSensor();
END_IF;
```

**预处理使用建议总结**：

| 方式 | 适用场景 | 优点 | 缺点 | 推荐度 |
|------|----------|------|------|--------|
| 常量定义 | 魔法数字消除、配置参数 | 简单通用 | 无法条件编译 | ⭐⭐⭐⭐⭐ |
| IF/CASE分支 | 运行时模式切换 | 所有IDE支持 | 占用运行资源 | ⭐⭐⭐⭐⭐ |
| {#IF}编译指示 | 平台差异代码 | 零运行开销 | 非所有IDE支持 | ⭐⭐⭐ |
| FB封装抽象 | 跨平台移植 | 高内聚低耦合 | 开发工作量大 | ⭐⭐⭐⭐ |
| 配置驱动 | 功能裁剪 | 灵活可控 | 需要初始化配置 | ⭐⭐⭐⭐ |

### 7.2 自定义工具功能块

#### 7.2.1 滤波器功能块

```pascal
FUNCTION_BLOCK FB_Filter_FirstOrder
(* 一阶低通滤波器 *)
VAR_INPUT
    i_rRawValue : REAL;           (* 原始值 *)
    i_rFilterTime : REAL := 1.0;  (* 滤波时间常数 (s) *)
    i_rCycleTime : REAL := 0.1;   (* 采样周期 (s) *)
END_VAR
VAR_OUTPUT
    q_rFilteredValue : REAL;      (* 滤波后的值 *)
END_VAR
VAR
    rLastOutput : REAL := 0.0;    (* 上一次输出值 *)
END_VAR

    (* 一阶滤波公式: Y(n) = α*X(n) + (1-α)*Y(n-1) *)
    (* 其中 α = T / (T + τ), T 为采样周期, τ 为滤波时间常数 *)
    VAR
        rAlpha : REAL;
    END_VAR

    rAlpha := i_rCycleTime / (i_rCycleTime + i_rFilterTime);
    q_rFilteredValue := rAlpha * i_rRawValue + (1.0 - rAlpha) * rLastOutput;
    rLastOutput := q_rFilteredValue;

END_FUNCTION_BLOCK
```

#### 7.2.2 斜坡发生器功能块

```pascal
FUNCTION_BLOCK FB_RampGenerator
(* 斜坡发生器 - 平滑过渡 *)
VAR_INPUT
    i_rTargetValue : REAL;         (* 目标值 *)
    i_rRampRate : REAL := 1.0;     (* 斜坡速率 (单位/s) *)
    i_bEnable : BOOL;              (* 使能 *)
    i_bReset : BOOL;               (* 复位 *)
END_VAR
VAR_OUTPUT
    q_rOutputValue : REAL;         (* 输出值 *)
    q_bReached : BOOL;             (* 到达目标 *)
END_VAR
VAR
    rCurrentValue : REAL := 0.0;   (* 当前值 *)
END_VAR

    IF i_bReset THEN
        rCurrentValue := 0.0;
        q_bReached := FALSE;
    ELSIF i_bEnable THEN
        IF rCurrentValue < i_rTargetValue THEN
            (* 上升斜坡 *)
            rCurrentValue := rCurrentValue + i_rRampRate * 0.1;  (* 假设 100ms 周期 *)
            IF rCurrentValue >= i_rTargetValue THEN
                rCurrentValue := i_rTargetValue;
                q_bReached := TRUE;
            ELSE
                q_bReached := FALSE;
            END_IF
        ELSIF rCurrentValue > i_rTargetValue THEN
            (* 下降斜坡 *)
            rCurrentValue := rCurrentValue - i_rRampRate * 0.1;
            IF rCurrentValue <= i_rTargetValue THEN
                rCurrentValue := i_rTargetValue;
                q_bReached := TRUE;
            ELSE
                q_bReached := FALSE;
            END_IF
        ELSE
            q_bReached := TRUE;
        END_IF
    END_IF

    q_rOutputValue := rCurrentValue;

END_FUNCTION_BLOCK
```

---

## 8. 故障处理规范

### 8.1 故障分类

| 故障级别 | 名称 | 处理方式 | 示例 |
| -------- | ---- | -------- | ---- |
| 1 | 提示性故障 | 继续运行，记录日志 | 传感器偏差警告 |
| 2 | 一般故障 | 停止当前动作，保持安全状态 | 通信超时 |
| 3 | 严重故障 | 立即急停，需人工复位 | 急停按下、过载 |
| 4 | 致命故障 | 系统锁定，需检修后重启 | 硬件损坏、安全回路断开 |

### 8.2 故障处理机制

#### 8.2.1 故障检测

```pascal
(* 故障检测示例 *)
VAR
    (* 故障标志 *)
    bFault_CommTimeout : BOOL;     (* 通信超时故障 *)
    bFault_Overload : BOOL;        (* 过载故障 *)
    bFault_Emergency : BOOL;       (* 急停故障 *)
    bFault_SensorError : BOOL;     (* 传感器故障 *)

    (* 故障码 *)
    iFaultCode : INT := 0;         (* 当前故障码 *)
END_VAR

(* 通信超时检测 - 3秒无响应则报 fault *)
IF NOT bCommAlive THEN
    IF tCommTimeout.Q THEN
        bFault_CommTimeout := TRUE;
        iFaultCode := 1001;  (* 通信超时故障码 *)
    END_IF
ELSE
    tCommTimeout(IN:=FALSE, PT:=T#3S);
    bFault_CommTimeout := FALSE;
END_IF
```

#### 8.2.2 故障响应

```pascal
(* 故障响应 - 根据严重程度采取不同措施 *)
CASE iFaultLevel OF
    1:  (* 提示性故障 *)
        (* 记录日志，继续运行 *)
        bLogFault := TRUE;
        q_bAlarmLight := TRUE;  (* 报警灯闪烁 *)

    2:  (* 一般故障 *)
        (* 停止当前动作 *)
        fbConveyor.i_bStop := TRUE;
        q_bAlarmLight := TRUE;
        q_bError := TRUE;

    3:  (* 严重故障 *)
        (* 立即急停 *)
        q_bEmergencyOutput := TRUE;
        q_bAlarmLight := TRUE;
        q_bError := TRUE;
        bNeedReset := TRUE;

    4:  (* 致命故障 *)
        (* 系统锁定 *)
        q_bSystemLockout := TRUE;
        q_bAlarmLight := TRUE;
        q_bError := TRUE;
        (* 需要人工检修并上电复位 *)
END_CASE
```

#### 8.2.3 故障恢复

```pascal
(* 故障恢复流程 *)
IF bResetButton AND bNeedReset THEN
    (* 1. 检查故障是否已消除 *)
    IF NOT bFault_CommTimeout AND NOT bFault_Overload AND NOT bFault_Emergency THEN
        (* 2. 清除故障标志 *)
        bFault_CommTimeout := FALSE;
        bFault_Overload := FALSE;
        bFault_Emergency := FALSE;
        iFaultCode := 0;

        (* 3. 清除输出 *)
        q_bAlarmLight := FALSE;
        q_bError := FALSE;
        bNeedReset := FALSE;

        (* 4. 系统回到初始状态 *)
        eSystemState := STATE_INIT;
    END_IF
END_IF
```

### 8.3 报警管理

#### 8.3.1 报警码定义规范

报警码 SHOULD 遵循统一的编码规则：

| 报警码范围 | 含义 | 示例 |
| ---------- | ---- | ---- |
| 0001-0099 | 系统级报警 | 0001=系统初始化失败 |
| 0100-0199 | 通信报警 | 0101=Modbus 通信超时 |
| 0200-0299 | IO 模块报警 | 0201=DI 模块断线 |
| 0300-0399 | 伺服/变频报警 | 0301=伺服过载 |
| 0400-0499 | 传感器报警 | 0401=光电传感器异常 |
| 0500-0599 | 安全回路报警 | 0501=安全门打开 |
| 0600-0699 | 工艺过程报警 | 0601=温度超限 |

#### 8.3.2 报警触发与清除

```pascal
(* 报警触发 *)
IF rTemperature > rTempLimit THEN
    bAlarm_Active[1] := TRUE;  (* 温度超限报警 *)
    iAlarmCode := 601;
    tAlarmDelay(IN:=TRUE, PT:=T#2S);  (* 延迟 2 秒确认，防止抖动 *)
    IF tAlarmDelay.Q THEN
        (* 确认报警 - 记录并响应 *)
        LogAlarm(601, '温度超限');
    END_IF
ELSE
    tAlarmDelay(IN:=FALSE, PT:=T#2S);
    IF rTemperature < rTempLimit - rTempHysteresis THEN
        bAlarm_Active[1] := FALSE;  (* 滞后清除，防止频繁触发 *)
        IF iAlarmCode = 601 THEN
            iAlarmCode := 0;
        END_IF
    END_IF
END_IF
```

---

## 9. 安全编程规范

### 9.1 安全设计原则

1. **故障导向安全**（Fail-Safe）：任何故障状态下，系统应进入安全状态
2. **冗余设计**：关键安全信号应采用双重确认
3. **独立性**：安全逻辑应独立于正常控制逻辑
4. **可测试性**：安全功能应能被定期测试验证

### 9.2 急停处理

```pascal
(* 急停处理 - 最高优先级 *)
VAR
    bEmergencyStop_Active : BOOL;   (* 急停激活标志 *)
    bEmergencyStop_Latch : BOOL;    (* 急停自锁 *)
END_VAR

(* 急停信号采集 - 双通道确认 *)
IF (NOT g_i_bEmergencyStop_CH1) AND (NOT g_i_bEmergencyStop_CH2) THEN
    (* 双通道都检测到急停 - 确认急停 *)
    bEmergencyStop_Active := TRUE;
    bEmergencyStop_Latch := TRUE;

    (* 立即执行安全动作 *)
    (* 1. 切断所有危险输出 *)
    q_bAllMotorEnable := FALSE;
    q_bValveOpen := FALSE;

    (* 2. 激活报警 *)
    q_bAlarmBuzzer := TRUE;
    q_bAlarmLight := TRUE;

    (* 3. 记录急停事件 *)
    LogEvent(EVENT_EMERGENCY_STOP, '急停按下');

    (* 4. 设置系统状态 *)
    eSystemState := STATE_EMERGENCY;
END_IF

(* 急停复位 - 需要先释放急停按钮，再按复位 *)
IF bEmergencyStop_Latch THEN
    IF g_i_bEmergencyStop_CH1 AND g_i_bEmergencyStop_CH2 THEN
        (* 急停按钮已释放 *)
        IF bResetButton THEN
            (* 按下复位按钮 *)
            bEmergencyStop_Latch := FALSE;
            bEmergencyStop_Active := FALSE;
            eSystemState := STATE_INIT;  (* 回到初始化状态 *)
        END_IF
    END_IF
END_IF
```

### 9.3 安全门/光幕处理

```pascal
(* 安全门监控 *)
IF NOT g_i_bSafetyDoorClosed THEN
    (* 安全门打开 *)
    (* 立即停止危险区域内的所有运动 *)
    q_bDangerZone_Enable := FALSE;

    (* 如果在自动模式下打开安全门，触发故障 *)
    IF g_bAutoMode THEN
        bSafetyFault := TRUE;
        iFaultCode := 501;  (* 安全门报警 *)
    END_IF
ELSE
    (* 安全门关闭 - 检查互锁条件后才允许启动 *)
    IF bStartCondition AND NOT bSafetyFault THEN
        q_bDangerZone_Enable := TRUE;
    END_IF
END_IF
```

### 9.4 冗余校验

```pascal
(* 关键信号冗余校验 *)
VAR
    bPosition1_Sensor1 : BOOL;   (* 位置传感器 1 *)
    bPosition1_Sensor2 : BOOL;   (* 位置传感器 2 - 冗余 *)
    bPosition_Valid : BOOL;      (* 位置信号有效 *)
END_VAR

(* 双传感器一致性检查 *)
IF bPosition1_Sensor1 = bPosition1_Sensor2 THEN
    bPosition_Valid := TRUE;
    bSensorFault := FALSE;
ELSE
    (* 传感器不一致 - 可能传感器故障 *)
    bPosition_Valid := FALSE;
    bSensorFault := TRUE;
    iFaultCode := 401;  (* 传感器冲突故障 *)
END_IF
```

---

## 10. HMI 接口规范

### 10.1 HMI 变量映射

#### 10.1.1 M 区分配规划

| M 区范围 | 用途 | 前缀 | 示例 |
| -------- | ---- | ---- | ---- |
| %M0 - %M99 | 系统状态 | g_b | g_bAutoMode |
| %M100 - %M199 | 设备状态 | g_bDev | g_bDev1Running |
| %M200 - %M299 | 报警标志 | g_bAlm | g_bAlm001 |
| %M300 - %M399 | HMI 操作 | g_bOp | g_bOpStart |
| %M400 - %M499 | HMI 显示 | g_bDisp | g_bDispPage1 |

#### 10.1.2 HMI 接口变量定义

```pascal
(* HMI 接口变量定义 *)
VAR
    (* HMI -> PLC 操作信号 *)
    g_bHmi_AutoMode AT %M0.0 : BOOL;      (* HMI: 自动模式选择 *)
    g_bHmi_ManualMode AT %M0.1 : BOOL;     (* HMI: 手动模式选择 *)
    g_bHmi_Start AT %M0.2 : BOOL;          (* HMI: 启动按钮 *)
    g_bHmi_Stop AT %M0.3 : BOOL;           (* HMI: 停止按钮 *)
    g_bHmi_Reset AT %M0.4 : BOOL;          (* HMI: 复位按钮 *)

    (* PLC -> HMI 状态显示 *)
    g_qHmi_SystemReady AT %M10.0 : BOOL;   (* PLC->HMI: 系统就绪 *)
    g_qHmi_Running AT %M10.1 : BOOL;       (* PLC->HMI: 运行中 *)
    g_qHmi_Error AT %M10.2 : BOOL;         (* PLC->HMI: 故障 *)
    g_qHmi_Alm_Code AT %MW12 : INT;        (* PLC->HMI: 报警码 *)
END_VAR
```

### 10.2 HMI 操作规范

#### 10.2.1 按钮信号处理

```pascal
(* HMI 按钮信号处理 - 使用脉冲方式 *)
VAR
    trigHmiStart : R_TRIG;     (* HMI 启动按钮上升沿 *)
    trigHmiStop : R_TRIG;      (* HMI 停止按钮上升沿 *)
    trigHmiReset : R_TRIG;     (* HMI 复位按钮上升沿 *)
END_VAR

(* 边沿检测，将电平信号转换为脉冲信号 *)
trigHmiStart(CLK := g_bHmi_Start);
trigHmiStop(CLK := g_bHmi_Stop);
trigHmiReset(CLK := g_bHmi_Reset);

(* 使用脉冲信号触发操作 *)
IF trigHmiStart.Q THEN
    (* 执行启动 *)
END_IF

IF trigHmiStop.Q THEN
    (* 执行停止 *)
END_IF
```

#### 10.2.2 模式切换

```pascal
(* 模式切换逻辑 - 互锁 *)
IF trigHmiStart.Q AND g_bHmi_AutoMode THEN
    (* 自动模式启动 *)
    IF NOT g_bRunning AND NOT g_bError THEN
        g_bAutoMode := TRUE;
        g_bManualMode := FALSE;
        eSystemState := STATE_AUTO_RUN;
    END_IF
ELSIF g_bHmi_ManualMode THEN
    (* 切换到手动模式 *)
    g_bAutoMode := FALSE;
    g_bManualMode := TRUE;
    (* 先停止自动运行 *)
    g_bRunning := FALSE;
    eSystemState := STATE_MANUAL;
END_IF
```

### 10.3 数据显示规范

```pascal
(* PLC -> HMI 数据刷新 *)
(* 模拟量数据 - 需要缩放处理 *)

(* 温度显示: ADC 值 (0-27648) -> 实际温度 (0-100°C) *)
g_qHmi_TempDisplay := SCALE_VALUE(
    iInput := g_i_rTempADC,
    iMin := 0,
    iMax := 27648,
    rOutMin := 0.0,
    rOutMax := 100.0
);

(* 速度显示: 实际速度 (m/s) -> 显示值 (保留1位小数) *)
g_qHmi_SpeedDisplay := ROUND(g_rActualSpeed * 10) / 10;
```

---

## 11. 文档规范

### 11.1 文档结构要求

PLC 项目文档 SHALL 遵循 [050_模板结构规范_TPL-V1.0.1](../../../02_规划过程/02_技术规划/05_文档模板规范/050_模板结构规范_TPL-V1.0.1.md) 的统一结构要求，包括：

- **文档基础信息**：标题、版本、日期、编制人、审核人、遵循规范
- **版本变更记录**：标准五列格式（版本号/内容/人/日期/说明）
- **核心内容**：按文档类型遵循对应模板

### 11.2 PLC 项目必选文档清单

| 序号 | 文档类型 | 前缀 | 必选性 | 对应 050 模板 | 说明 |
| ---- | -------- | ---- | ------ | -------------- | ---- |
| 1 | PLC 变量定义文档 | VAR | **必选** | 自定义(PLC专用) | 完整 IO 分配表 + FB 接口说明 |
| 2 | 程序架构文档 | ARC | **必选** | 4.1 技术文档 | Mermaid 架构图 + 组件清单 |
| 3 | 详细设计说明书 | DSN | **必选** | 021 详细设计 | 各工站状态机 + 接口定义 |
| 4 | 报警码定义 | ALM | **必选** | 自定义(PLC专用) | 报警码表 + 触发条件 + 数据流 |
| 5 | FBD 使用说明 | FBD | 每个 FB 一份 | 自定义(PLC专用) | ASCII 接口图 + 针脚表 + 调用示例 |
| 6 | PLC 设计总文档 | PLC | 推荐 | 自定义 | 汇总以上所有文档的概览版 |

### 11.3 文档命名规范

文档文件名 SHALL 遵循 [004_通用项目文档版本管理与变更核心规范_DEV-V1.1.1](../../../01_启动过程/02_基础规范/02_版本规范/004_通用项目文档版本管理与变更核心规范_DEV-V1.1.1.md) 的命名规则：

**格式**：`[文档名称]_[前缀码]-[版本号].md`

**示例**：
- `PLC变量定义文档_VAR-DJ-2026-005-V4.0.0.md`
- `程序架构文档_ARC-DJ-2026-005-V4.0.0.md`
- `报警码定义_ALM-DJ-2026-005-V4.0.0.md`

### 11.4 文档与代码同步要求

1. **变量名一致**：文档中的变量名必须与 ST 代码 VAR 声明完全一致（遵循 801_PLC变量命名与功能块命名规范）
2. **FB 名一致**：文档中的功能块名必须与 ST 代码声明完全一致（`FB_编号_英文功能描述_设备对象` 格式）
3. **物理地址准确**：IO 文档中标注的物理地址（%IX/%QX/M/D 区）必须与实际接线一致
4. **交叉引用有效**：文档间超链接必须指向正确的文件路径（含版本号后缀）
5. **迭代同步**：每次代码迭代完成后，必须同步更新所有相关文档

---

## 12. 测试与调试规范

### 12.1 仿真测试

#### 12.1.1 单元测试

对每个功能块进行独立的仿真测试：

```pascal
(* FB_1001 单元测试用例 *)
PROGRAM TEST_FB_1001
VAR
    fbTest : FB_1001_ConveyorControl_BeltConveyor;
    bTestStart : BOOL;
    bTestStop : BOOL;
    bTestEnable : BOOL;
    bTestReset : BOOL;
    bTestEstop : BOOL;
END_VAR

(* 测试用例 1: 正常启停 *)
(* 前置条件: Enable=TRUE, EStop=FALSE *)
(* 步骤 1: 发送 Start 脉冲 *)
(* 预期结果: Running=TRUE, Ready=TRUE *)
(* 步骤 2: 发送 Stop 脉冲 *)
(* 预期结果: Running=FALSE, Ready=TRUE *)

(* 测试用例 2: 急停测试 *)
(* 前置条件: Running=TRUE *)
(* 步骤: 发送 EStop=TRUE *)
(* 预期结果: Running=FALSE, Error=TRUE, ErrorCode=1 *)
```

#### 12.1.2 集成测试

在主程序中进行集成测试，验证各模块协作：

```pascal
(* 集成测试清单 *)
(*
 * 1. IO 映射正确性测试
 *    - 验证所有 DI/DO 地址映射正确
 *    - 验证远程 IO 通信正常
 *
 * 2. FB 调用链路测试
 *    - 验证数据流向正确
 *    - 验证接口参数匹配
 *
 * 3. 状态机转换测试
 *    - 验证所有状态转换路径
 *    - 验证边界条件和异常处理
 *
 * 4. 安全功能测试
 *    - 验证急停响应时间
 *    - 验证安全门互锁
 *    - 验证故障恢复流程
 *)
```

### 12.2 在线调试

#### 12.2.1 监控变量

```pascal
(* 调试期间使用的监控变量 *)
VAR
    (* 调试开关 *)
    bDebugMode AT %M100.0 : BOOL;     (* 调试模式开关 *)

    (* 调试信息 *)
    iDebug_Step AT %MW100 : INT;       (* 当前步序 *)
    iDebug_State AT %MW102 : INT;      (* 当前状态 *)
    iDebug_Error AT %MW104 : INT;      (* 错误码 *)
    rDebug_Value AT %MW106 : REAL;     (* 调试用模拟值 *)
END_VAR

IF bDebugMode THEN
    (* 输出调试信息 *)
    iDebug_Step := eSystemState;
    iDebug_State := fbConveyor.internal_eState;
    iDebug_Error := iFaultCode;
END_IF
```

#### 12.2.2 强制变量

**警告**：强制变量操作应谨慎使用，仅在调试阶段使用！

```pascal
(* 强制操作规范 *)
(*
 * 1. 生产环境禁止强制操作
 * 2. 强制前必须确认安全
 * 3. 强制完成后及时取消强制
 * 4. 记录所有强制操作
 *
 * 允许强制的场景:
 * - 传感器故障时的临时替代
 * - 输出测试验证
 * - 故障排查
 *)
```

### 12.3 测试报告

每次测试完成后，SHALL 输出测试报告，包含：

| 项目 | 内容 |
| ---- | ---- |
| 测试环境 | 硬件配置、软件版本、固件版本 |
| 测试用例 | 测试项、输入条件、预期结果、实际结果 |
| 测试结果 | 通过/失败、截图、波形 |
| 问题记录 | 发现的问题、严重程度、处理建议 |
| 结论 | 是否满足发布条件 |

---

## 13. 版本管理与发布规范

### 13.1 版本号规则

| 类型 | 格式 | 示例 | 说明 |
| ---- | ---- | ---- | ---- |
| 主版本 | V X . 0 . 0 | V 2 . 0 . 0 | 架构变更、重大功能增减 |
| 次版本 | V x . Y . 0 | V 1 . 1 . 0 | 新增功能、重要改进 |
| 修订版 | V x . y . Z | V 1 . 0 . 1 | Bug 修复、小改动 |

### 13.2 变更记录规范

每次代码变更 MUST 记录变更内容：

```pascal
(* ================================================================= *)
(*  变更记录                                                        *)
(* ---------------------------------------------------------------- *)
(*  V1.0.1 (2026-03-15) Trae                                       *)
(*  - 新增: 急停双通道确认逻辑                                      *)
(*  - 修改: 优化状态机转换条件                                      *)
(*  - 修复: 修复计数器溢出问题 (#123)                               *)
(*                                                                   *)
(*  V1.0.0 (2026-02-05) Trae                                       *)
(*  - 初始版本创建                                                  *)
(* ================================================================= *)
```

### 13.3 发布检查清单

发布前 MUST 完成以下检查：

- [ ] 代码审查通过
- [ ] 单元测试全部通过
- [ ] 集成测试全部通过
- [ ] 安全功能测试通过
- [ ] 文档已同步更新
- [ ] 变更记录已完成
- [ ] 版本号已更新
- [ ] 备份已完成

### 13.4 多文件版本号同步规范（DEV-V1.0.2 新增）

**适用场景**：当项目包含多个关联文件时（程序+文档+模板），版本号必须保持同步一致。

#### 13.4.1 版本号一致性原则

| 文件类型 | 版本号位置 | 同步要求 |
|----------|------------|----------|
| 程序文件 (.scl/.st) | 文件名 + 注释头变更记录 | ✅ **必须完全一致** |
| 接口文档 (IFC) | 文件名 + 文档标识 | ✅ 必须与程序版本匹配 |
| 设计文档 (DSN) | 文件名 + 文档标识 | ✅ 必须与程序版本匹配 |
| 使用说明 (UM) | 文件名 + 文档标识 | ✅ 必须与程序版本匹配 |
| 变更记录 (CHG) | 文件内容 | ✅ 必须包含当前版本条目 |
| 模板库副本 | 文件名 + 注释 | ⚠️ 可独立演进，需注明基线版本 |

**示例**：
```
程序文件：FB_1001_ConveyorControl_LineConveyor_V1.1.0.scl
接口文档：IFC-FB1001-ConveyorControl-V1.1.0.md
设计文档：DSN-FB1001-ConveyorControl-V1.1.0.md
```

#### 13.4.2 版本冲突解决策略

**冲突场景1：文件名版本 ≠ 注释头版本**
```
❌ 错误：
  文件名：FB_xxx_V1.0.0.scl
  注释头：(* 版本号：V4.8.1 *)

✅ 正确：
  以文件名版本为准 → 更新注释头为 V1.0.0
  或重命名文件为 V4.8.1（如果注释头版本正确）
```

**冲突场景2：程序版本 > 文档版本**
```
❌ 错误：
  程序：V1.1.0（已修改变量命名）
  文档：V1.0.0（仍使用旧变量名）

✅ 正确：
  立即同步更新所有关联文档至 V1.1.0
  在文档变更记录中注明："同步程序V1.1.0变量命名修订"
```

**冲突场景3：模板库版本与项目版本分离**
```
✅ 允许的情况：
  项目程序：FB_1001_xxx_V1.1.0.scl（基于模板定制修改）
  模板库：FB_1001_xxx_V4.8.1.scl（原始模板，未修改）

  要求：
  - 项目程序注释头必须注明"基于版本：V4.8.1"
  - 模板库版本可独立演进，不影响项目版本
```

#### 13.4.3 版本升级检查清单

每次修改程序后发布新版本前，必须完成：

```
□ 1. 更新程序文件名版本号（如 V1.0.0 → V1.1.0）
□ 2. 更新程序注释头版本号（与文件名一致）
□ 3. 在程序变更记录中添加新版本条目
□ 4. 更新所有关联文档的文件名版本号
□ 5. 更新所有关联文档内部的版本引用
□ 6. 在各文档的变更记录中添加同步条目
□ 7. 如有模板库副本，评估是否需要同步更新
□ 8. 验证所有文件的交叉引用链接有效
```

**版本号格式规则**（遵循 004_通用项目文档版本管理与变更核心规范）：

| 变更类型 | 版本升级方式 | 示例 |
|----------|--------------|------|
| Bug修复 | 修订版 +1 | V1.0.0 → V1.0.1 |
| 小功能新增 | 次版本 +1，修订版归零 | V1.0.1 → V1.1.0 |
| 架构重构/重大变更 | 主版本 +1，其余归零 | V1.1.0 → V2.0.0 |
| 规范化修订（仅命名/注释） | 次版本 +1 | V1.0.0 → V1.1.0 |

---

## 附录 A：快速参考卡

### A.1 常用数据类型

| 类型 | 大小 | 范围 | 示例 |
| ---- | ---- | ---- | ---- |
| BOOL | 1 bit | TRUE/FALSE | `bFlag` |
| BYTE | 8 bit | 0~255 | `byData` |
| WORD | 16 bit | 0~65535 | `wData` |
| DWORD | 32 bit | 0~4294967295 | `dwData` |
| SINT | 8 bit | -128~127 | `siValue` |
| USINT | 8 bit | 0~255 | `usiValue` |
| INT | 16 bit | -32768~32767 | `iValue` |
| UINT | 16 bit | 0~65535 | `uiValue` |
| DINT | 32 bit | -2147483648~2147483647 | `diValue` |
| UDINT | 32 bit | 0~4294967295 | `udiValue` |
| REAL | 32 bit | ±3.4e±38 | `rValue` |
| LREAL | 64 bit | ±1.7e±308 | `lrValue` |
| TIME | 32 bit | T#-24.8d~+24.8d | `tTimer` |
| DATE | 32 bit | D#1970-01-01~2106-02-06 | `dtDate` |
| TOD | 32 bit | TOD#00:00:00~23:59:59.999 | `todTime` |
| STRING | 可变 | 字符串 | `sText` |

### A.2 常用运算符

| 类别 | 运算符 | 说明 | 示例 |
| ---- | ------ | ---- | ---- |
| 算术 | + | 加法 | `a + b` |
| 算术 | - | 减法 | `a - b` |
| 算术 | * | 乘法 | `a * b` |
| 算术 | / | 除法 | `a / b` |
| 算术 | MOD | 取模 | `a MOD b` |
| 比较 | = | 等于 | `a = b` |
| 比较 | <> | 不等于 | `a <> b` |
| 比较 | > | 大于 | `a > b` |
| 比较 | < | 小于 | `a < b` |
| 比较 | >= | 大于等于 | `a >= b` |
| 比较 | <= | 小于等于 | `a <= b` |
| 逻辑 | AND | 与 | `a AND b` |
| 逻辑 | OR | 或 | `a OR b` |
| 逻辑 | XOR | 异或 | `a XOR b` |
| 逻辑 | NOT | 非 | `NOT a` |

### A.3 常用标准函数

| 函数类别 | 函数名 | 说明 | 示例 |
| -------- | ------ | ---- | ---- |
| 类型转换 | INT_TO_REAL | 整数转实数 | `r := INT_TO_REAL(i)` |
| 类型转换 | REAL_TO_INT | 实数转整数 | `i := REAL_TO_INT(r)` |
| 类型转换 | BOOL_TO_INT | 布尔转整数 | `i := BOOL_TO_INT(b)` |
| 数学函数 | ABS | 绝对值 | `r := ABS(x)` |
| 数学函数 | SQRT | 平方根 | `r := SQRT(x)` |
| 数学函数 | SIN/COS/TAN | 三角函数 | `r := SIN(angle)` |
| 数学函数 | LN/LOG/EXP | 对数/指数 | `r := LN(x)` |
| 数学函数 | MIN/MAX | 最小/最大值 | `r := MIN(a, b)` |
| 字符串 | LEN | 字符串长度 | `i := LEN(s)` |
| 字符串 | CONCAT | 字符串连接 | `s := CONCAT(s1, s2)` |
| 字符串 | FIND | 查找子串 | `i := FIND(s1, s2)` |
| 字符串 | REPLACE | 替换子串 | `s := REPLACE(s1, pos, len, s2)` |
| 位操作 | SHL/SHR | 左移/右移 | `i := SHL(i, n)` |
| 位操作 | ROL/ROR | 循环左移/右移 | `i := ROL(i, n)` |
| 位操作 | AND/OR/XOR | 按位运算 | `i := i1 AND i2` |
| 选择 | SEL | 二选一 | `r := SEL(b, r1, r2)` |
| 选择 | LIMIT | 限幅 | `r := LIMIT(min, val, max)` |
| 选择 | MUX | 多路选择 | `r := MUX(k, r1, r2, r3...)` |
| 边沿 | R_TRIG | 上升沿检测 | 见第 7 章 |
| 边沿 | F_TRIG | 下降沿检测 | 见第 7 章 |

---

## 附录 B：常见问题与解决方案

### B.1 编译错误

| 错误信息 | 原因 | 解决方案 |
| -------- | ---- | -------- |
| "Unknown variable" | 变量未声明或拼写错误 | 检查变量声明和拼写 |
| "Type mismatch" | 类型不匹配 | 检查数据类型是否一致 |
| "Duplicate declaration" | 重复声明 | 检查是否有同名变量 |
| "Syntax error" | 语法错误 | 检查语法是否符合 IEC 61131-3 |
| "Overflow" | 数值溢出 | 检查数值范围，使用更大类型 |

### B.2 运行时问题

| 问题现象 | 可能原因 | 解决方案 |
| -------- | -------- | -------- |
| 程序不执行 | 未调用 PRG 或 FB | 在主程序中正确调用 |
| 输出不变化 | 输出未刷新或被覆盖 | 检查输出逻辑和扫描顺序 |
| 通信超时 | 网络问题或配置错误 | 检查网络连接和通信配置 |
| 周期时间过长 | 程序过于复杂或死循环 | 优化代码，检查循环条件 |
| 数据丢失 | 变量作用域错误 | 检查变量声明位置 |

### B.3 最佳实践总结

1. **先设计后编码**：充分设计后再开始编写代码
2. **模块化开发**：将复杂功能分解为小的功能块
3. **充分注释**：代码即文档，保持注释更新
4. **版本控制**：使用 Git 等工具管理代码版本
5. **持续测试**：编写测试用例，持续验证功能
6. **文档同步**：代码变更后及时更新文档
7. **代码审查**：定期进行代码审查，保证质量
8. **学习分享**：团队成员间分享经验和最佳实践

---

## 15. 代码审查检查清单 (DEV-V1.0.3 新增)

### 概述

本检查清单用于PLC代码的系统性审查，涵盖**架构层面、编码规范、安全性、可维护性**四个维度共17项检查点。所有标记为"必须通过"的项目为强制性要求，"推荐通过"的项目为最佳实践建议。

### 15.1 架构层面检查（必须全部通过）

| 序号 | 检查项 | 标准 | 通过条件 | 验证方法 |
|:---:|-------|------|---------|----------|
| A1 | **IO解耦** | FB禁止引用X/Y/M/D地址 | 搜索无`%IX`/`%QX`/`%IW`/`%QW`/`%MX`/`%MD`等物理地址前缀 | 使用IDE的全局搜索功能，在所有FB文件中搜索上述关键字 |
| A2 | **IO映射集中** | 映射在PRG_800/900区域 | 所有物理IO赋值语句位于主控PRG中 | 审查PRG主程序，确认所有AT%声明和物理地址读写集中在Step 800/900 |
| A3 | **无循环依赖** | FB调用无环路 | 调用关系图无环 | 绘制FB调用关系图（可用Mermaid或手绘），确认无A→B→C→A环路 |
| A4 | **复杂度控制** | 单个FB≤500行 | 统计行数符合 | 使用IDE统计功能或脚本计数，超限需拆分 |

### 15.2 编码规范检查（必须全部通过）

| 序号 | 检查项 | 标准 | 验证方法 |
|:---:|-------|------|----------|
| C1 | **文件头完整** | 标准`(* *)`块注释 | 文件开头有标准格式注释（含功能块名称、描述、版本、作者） | 打开每个PRG/FB/FC文件，检查前10行是否包含完整文件头 |
| C2 | **Region标记配对** | 100~900编号配对正确 | `#region`与`#endregion`数量一致且编号匹配 | 使用正则表达式搜索统计：`\#region` 和 `\#endregion` 出现次数应相等 |
| C3 | **变量命名规范** | `i_`/`o_`/`s_`/`m_`/`c_`前缀正确使用 | 无违规命名（详见801规范§4） | 审查VAR_INPUT/VAR_OUTPUT/VAR区域，确认所有变量符合前缀规则 |
| C4 | **定时器命名规范** | `t`+功能描述，成员名`tIn/tQ/tPt/tEt` | 无冗长或纯数字编号命名 | 搜索定时器实例名，确认以`t`开头且有语义；数组命名为`tIn/tQ/tPt/tEt` |
| C5 | **注释成对性** | `(* *)`成对出现 | 搜索无`--+\)`模式（未关闭注释） | 使用正则搜索 `\(\*[^*]*--` 或手动审查，确认无未闭合注释 |

### 15.3 安全性检查（必须全部通过）

| 序号 | 检查项 | 标准 | 验证方法 |
|:---:|-------|------|----------|
| S1 | **急停优先级最高** | 急停信号独立于状态机，无条件执行 | 急停处理逻辑位于CASE语句之后或使用独立IF块，不受步序影响 | 审查急停处理代码位置，确认其在每次扫描周期最后执行且无条件 |
| S2 | **输出互锁** | 互斥输出有互锁逻辑 | 如气缸升/降、电机正/反转不能同时为TRUE | 搜索互斥输出对，确认存在互锁逻辑（如`NOT o_b升 OR o_b降`） |
| S3 | **模式切换安全** | 自动→手动切换时安全过渡 | 切换时清除自动运行标志、复位状态机、停止危险动作 | 审查模式切换逻辑，确认包含状态重置和安全输出复位 |
| S4 | **故障安全态** | 故障时输出进入已知安全状态 | 所有故障分支明确设置输出值（非依赖默认值） | 审查CASE的ERROR分支和IF故障处理，确认显式赋值所有关键输出 |

### 15.4 可维护性检查（推荐通过）

| 序号 | 检查项 | 标准 | 验证方法 |
|:---:|-------|------|----------|
| M1 | **状态机完整性** | CASE覆盖所有定义的步序常量 | 无遗漏步序、ELSE分支有默认处理 | 对照VAR_CONSTANT中的步序定义，逐一确认CASE中有对应分支 |
| M2 | **报警码唯一性** | 报警码不重复 | 全项目范围内报警码唯一 | 提取所有ALM_xxx常量，排序后检查重复项 |
| M3 | **常量替代魔法数** | 无裸数字（0/1/FALSE/TRUE除外） | 工艺参数、步序号、报警码均使用常量 | 搜索CASE OF后的数字、IF比较中的数字，确认均为常量引用 |
| M4 | **关键算法注释** | 复杂计算有"为什么"的解释 | 非显而易见的逻辑有说明性注释 | 审查斜坡计算、滤波公式、位置转换等算法段，确认有解释性注释 |
| M5 | **文档同步** | 代码与文档一致 | 变量名、FB名、接口与设计文档匹配 | 抽样对比代码VAR声明与VAR/ARC/DSN文档，确认一致性 |

### 15.5 审查流程建议

```
代码编写完成
    ↓
【自检】开发者按清单逐项自查（预计30分钟）
    ↓
【互检】同事交叉审查（预计45分钟）
    ↓
【问题记录】填写《代码审查问题跟踪表》
    ↓
【修复验证】修改后重新验证相关项
    ↓
【审核通过】签署《代码审查通过确认单》
    ↓
【入库】合并至版本控制主干
```

### 15.6 常见问题速查表

| 问题现象 | 可能原因 | 对应检查项 | 修复建议 |
|---------|---------|-----------|---------|
| FB编译报错"Unknown variable" | 变量未声明或拼写错误 | C3 | 检查801规范命名规则，统一前缀 |
| 状态机卡在某一步 | 缺少步序转换条件 | M1 | 补全CASE分支，确保每步有出口 |
| 急停按下但设备未停止 | 急停处理被状态机覆盖 | S1 | 将急停逻辑移到CASE之后，无条件执行 |
| 气缸同时升降 | 缺少互锁逻辑 | S2 | 添加`IF o_b升 THEN o_b降 := FALSE; END_IF` |
| 代码难以理解 | 缺少注释或魔法数 | M3/M4 | 提取常量并添加解释性注释 |
| IO改动导致多处修改 | IO分散在各FB中 | A1/A2 | 将IO集中到PRG的800/900区域 |

> **审查工具推荐**：
> - **文本搜索**：VS Code全局搜索（支持正则）
> - **静态分析**：Codesys/TwinCAT内置语法检查
> - **可视化**：Mermaid绘制调用关系图
> - **版本比对**：Git diff查看变更范围

---

## 参考资料

| 资料名称 | 版本 | 来源 | 说明 |
| -------- | ---- | ---- | ---- |
| IEC 61131-3 标准 | 第 3 版 | 国际电工委员会 | PLC 编程国际标准 |
| [801_PLC 变量命名与功能块命名规范](../../../01_启动过程/02_基础规范/01_命名规范/801_PLC变量命名与功能块命名规范_DEV-V1.0.2.md) | DEV-V1.0.2 | 内部文档 | 变量和 FB 命名规范 |
| [802_PLC 工作流命名规范](../../../01_启动过程/02_基础规范/01_命名规范/802_PLC工作流命名规范_DEV-V1.0.3.md) | DEV-V1.0.3 | 内部文档 | 工作流编号规范 |
| Codesys 编程指南 | V3.5 | Codesys GmbH | Codesys 开发指南 |
| Autoshop 用户手册 | V2.0 | 内部文档 | Autoshop 开发环境手册 |
| Structured Text 规范 | - | PLCopen | ST 语言最佳实践 |

---

**文档版本**: DEV-V1.0.4
**编制日期**: 2026-04-25
**编制人**: Trae
**审核人**: 人工
**来源项目**: DJ-2026-005 边框缓存机
**更新内容**: 新增§5.4 Region标记编号体系总表(100~900完整定义)及FB_1003实际应用示例；新增§15代码审查检查清单(四维17项+验证方法+流程建议+问题速查表)
