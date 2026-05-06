# SysLib 标准库补充与文档完善计划

## 一、项目概述

### 1.1 背景

基于对 GitHub `Siemens-SCL-Source-Files` 仓库的分析，结合边框缓存机项目的实际需求，本计划旨在：

* 筛选可借鉴的组件并整合到 `SysLib`

* 为 `SysLib` 中的所有 FB/FC 补充完整文档

### 1.2 目标范围

| 模块                | 当前状态   | 目标状态         |
| ----------------- | ------ | ------------ |
| `SysLib/timer/`   | 基础功能实现 | 添加完整文档       |
| `SysLib/counter/` | 基础功能实现 | 添加完整文档       |
| `SysLib/convert/` | 基础功能实现 | 添加完整文档       |
| `SysLib/edge/`    | 未创建    | 新增边沿检测组件     |
| `SysLib/math/`    | 未创建    | 新增数学运算组件（可选） |

***

## 二、西门子开源库组件分析

### 2.1 组件筛选结果

| 组件                | 文件                    | 可借鉴性  | 建议操作    | 备注                           |
| ----------------- | --------------------- | ----- | ------- | ---------------------------- |
| **EdgeDetection** | EdgeDetection.scl     | ⭐⭐⭐⭐⭐ | 强烈推荐采纳  | 边沿检测功能通用                     |
| **TaktGenerator** | FB\_Taktgenerator.scl | ⭐⭐⭐⭐  | 推荐采纳    | 脉冲发生器，可用于定时任务                |
| **DoorLock**      | DoorLock.scl          | ⭐⭐    | 选择性采纳   | 门锁控制，项目中已有类似逻辑               |
| **valveControl**  | valveControl.scl      | ⭐⭐⭐   | 可参考接口设计 | 阀门控制，项目中已有 `FB_ValveControl` |
| **LogMsg**        | LogMsg.scl            | ⭐⭐⭐⭐  | 推荐采纳    | 日志消息处理                       |
| **Meldungen**     | Meldungen.scl         | ⭐⭐⭐   | 可参考     | 报警消息管理                       |
| **Buffer**        | Buffer.scl            | ⭐     | 不推荐直接使用 | 架构差异大，仅思想可借鉴                 |
| **PSE200U**       | fb\_PSE200U.scl       | ⭐     | 不推荐     | 特定设备驱动，项目不适用                 |

### 2.2 推荐新增组件

#### (1) EdgeDetection - 边沿检测

**用途**：检测信号的上升沿/下降沿，用于触发一次性动作

#### (2) TaktGenerator - 脉冲发生器

**用途**：生成固定频率的脉冲信号（10Hz\~0.2Hz）

#### (3) LogMsg - 日志消息

**用途**：统一的日志消息管理和输出

***

## 三、文件修改计划

### 3.1 新增文件清单

| 文件路径                                | 说明       | 来源                       |
| ----------------------------------- | -------- | ------------------------ |
| `SysLib/edge/FB_R_TRIG.scl`         | 上升沿检测 FB | 基于 EdgeDetection.scl     |
| `SysLib/edge/FB_F_TRIG.scl`         | 下降沿检测 FB | 基于 EdgeDetection.scl     |
| `SysLib/pulse/FB_TaktGenerator.scl` | 脉冲发生器 FB | 基于 FB\_Taktgenerator.scl |
| `SysLib/log/FC_LogMsg.scl`          | 日志消息函数   | 基于 LogMsg.scl            |

### 3.2 需要完善文档的现有文件

| 文件路径                                 | 需要补充                   |
| ------------------------------------ | ---------------------- |
| `SysLib/timer/FB_TON.scl`            | 使用文档、设计说明、接口文档、注释、变更记录 |
| `SysLib/timer/FB_TOF.scl`            | 使用文档、设计说明、接口文档、注释、变更记录 |
| `SysLib/timer/FB_TP.scl`             | 使用文档、设计说明、接口文档、注释、变更记录 |
| `SysLib/timer/FB_TONR.scl`           | 使用文档、设计说明、接口文档、注释、变更记录 |
| `SysLib/counter/FB_CTU.scl`          | 使用文档、设计说明、接口文档、注释、变更记录 |
| `SysLib/counter/FB_CTD.scl`          | 使用文档、设计说明、接口文档、注释、变更记录 |
| `SysLib/counter/FB_CTUD.scl`         | 使用文档、设计说明、接口文档、注释、变更记录 |
| `SysLib/convert/FC_INT_TO_TIME.scl`  | 使用文档、设计说明、接口文档、注释、变更记录 |
| `SysLib/convert/FC_TIME_TO_INT.scl`  | 使用文档、设计说明、接口文档、注释、变更记录 |
| `SysLib/convert/FC_DINT_TO_TIME.scl` | 使用文档、设计说明、接口文档、注释、变更记录 |
| `SysLib/convert/FC_TIME_TO_DINT.scl` | 使用文档、设计说明、接口文档、注释、变更记录 |

### 3.3 文档模板（所有 FB/FC 统一格式）

```scl
(* ============================================================================
 功能块名称: FB_XXX
 功能描述: [简要描述功能]
 所属模块: SysLib/timer
 ============================================================================ *)
(*
 * 项目: DJ-2026-005 边框缓存机
 * 版本: V1.0.0
 * 创建日期: 2026-05-01
 * 编制人: [待填写]
 * 审核人: [待填写]
 *
 * 遵循规范:
 *   - 801_PLC变量命名与功能块命名规范_DEV-V1.0.5
 *   - 810_PLC编程规范_DEV-V1.0.3
 *   - IEC 61131-3 标准
 *
 * 功能说明:
 *   [详细功能描述，包括输入输出行为、状态转换等]
 *
 * 接口说明:
 *   INPUT:
 *     IN_NAME : TYPE - 说明
 *   OUTPUT:
 *     OUT_NAME : TYPE - 说明
 *
 * 使用示例:
 *   VAR
 *     myInstance : FB_XXX;
 *   END_VAR
 *   myInstance(IN := xxx, OUT => yyy);
 *
 * 架构特点:
 *   - 特点1
 *   - 特点2
 *
 * 变更记录:
 *   V1.0.0 (2026-05-01): 初始版本
 *          - 实现基本功能
 *)
```

***

## 四、执行步骤

### 步骤 1: 创建边沿检测组件

* 创建 `FB_R_TRIG.scl`（上升沿检测）

* 创建 `FB_F_TRIG.scl`（下降沿检测）

### 步骤 2: 创建脉冲发生器组件

* 创建 `FB_TaktGenerator.scl`

### 步骤 3: 创建日志消息函数

* 创建 `FC_LogMsg.scl`

### 步骤 4: 完善定时器文档

* 更新 `FB_TON.scl`

* 更新 `FB_TOF.scl`

* 更新 `FB_TP.scl`

* 更新 `FB_TONR.scl`

### 步骤 5: 完善计数器文档

* 更新 `FB_CTU.scl`

* 更新 `FB_CTD.scl`

* 更新 `FB_CTUD.scl`

### 步骤 6: 完善转换函数文档

* 更新 `FC_INT_TO_TIME.scl`

* 更新 `FC_TIME_TO_INT.scl`

* 更新 `FC_DINT_TO_TIME.scl`

* 更新 `FC_TIME_TO_DINT.scl`

### 步骤 7: 更新 .plc.json

* 添加新增的库目录

***

## 五、风险评估

| 风险           | 概率 | 影响 | 应对措施                |
| ------------ | -- | -- | ------------------- |
| 新增组件与现有逻辑冲突  | 低  | 中  | 采用独立命名空间，不修改现有代码    |
| go-gen 兼容性问题 | 中  | 高  | 避免使用系统函数，使用纯 SCL 实现 |
| 文档格式不一致      | 低  | 低  | 严格遵循统一模板            |

***

## 六、输出交付物

| 交付物                    | 描述            |
| ---------------------- | ------------- |
| `SysLib/edge/`         | 边沿检测组件（2个FB）  |
| `SysLib/pulse/`        | 脉冲发生器组件（1个FB） |
| `SysLib/log/`          | 日志消息组件（1个FC）  |
| 更新后的 `SysLib/timer/`   | 带完整文档的定时器FB   |
| 更新后的 `SysLib/counter/` | 带完整文档的计数器FB   |
| 更新后的 `SysLib/convert/` | 带完整文档的转换FC    |
| 更新后的 `.plc.json`       | 包含所有库目录       |

