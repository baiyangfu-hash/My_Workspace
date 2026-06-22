---
spec_id: REQ-FB1011
title: "FB_1011_CylinderControl需求分析文档"
version: "V13.0.0"
domain: plc
lifecycle: stable
canonical_path: "0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1011_CylinderControl/PRD/需求分析文档_REQ.md"
tags: ["气缸控制", "执行器", "PLC功能块", "电磁阀", "单线圈弹簧复位", "双线圈中封阀", "传感器消抖", "结构体"]
---

# 需求分析文档 FB_1011_CylinderControl

## 1. 文档基础信息

**文档标题**：FB_1011_CylinderControl需求分析文档
**文档版本**：V13.0.0
**编制日期**：2026-06-18
**编制人**：Trae
**审核人**：人工
**遵循规范**：REQ-020, LSP-905-V1.0.2, LSP-904-V1.2.0, LSP-903-V2.1.0

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 | 详细说明 |
|--------|----------|--------|----------|----------|
| V13.0.0 | Breaking Change: 重命名stCmd→i_stCmd, stSts→q_stSts, 对齐LSP-905 V1.0.2前缀规范 | Trae | 2026-06-18 | 仅重命名FB级引脚名, 结构体内部字段不变; 调用方需更新: stCmd:=→i_stCmd:=, stSts=>→q_stSts=> |
| V12.0.0 | 新增防呆锁存(s_iLatchedSolenoidType+s_iLatchedMode), 运动中参数不可变; 新增i_stCmd.Mode(0=手动/1=自动); 新增i_stCmd.ModeStatus(WORD); CASE分支改用锁存值; 手动模式跳过超时检测 | Trae | 2026-06-18 | 防呆: 运动期间锁存SolenoidType和Mode, 空闲时自动刷新; 手动模式跳过超时但保留传感器故障诊断; ModeStatus预留上层序列控制器使用 |
| V11.0.0 | Breaking Change: 扁平接口→结构体接口; i_stCmd:ST_CylinderCmd(CONSTANT)+q_stSts:ST_CylinderSts; q_aSolenoid[0..7]→SolenoidA/SolenoidB; FB引脚14→2; SolenoidType对齐实际场景: 0=两位三通单线圈弹簧复位(气缸阀/真空阀), 1=双线圈中封阀(失电中封保持); 真空阀纳入SolenoidType=0 | Trae | 2026-06-18 | 重构接口: VAR_INPUT CONSTANT i_stCmd:ST_CylinderCmd + VAR_OUTPUT q_stSts:ST_CylinderSts; 删除ARRAY输出改为两个独立BOOL; 调用方引脚数从14降为2, 支持结构体整体保存/传递/快照 |
| V10.0.0 | Breaking Change: 新增双线圈支持(SolenoidType=1); q_bSolenoid→q_aSolenoid[0..7] ARRAY输出; 新增RetractPolarity参数; 命令处理从IF/ELSIF改为CASE SolenoidType分支 | Trae | 2026-06-17 | 双线圈A/B互锁+无命令保持位+ELSE安全态 |
| V9.2.0 | P0定时器修复: 定时器调用对齐LSP-903 V2.1.0三段式; 消抖关闭时设IN=FALSE让TON自然复位; 超时检测移入命令分支内加s_bMoving防误报 | Trae | 2026-06-17 | 定时器调用从条件内联改为三段式+顶部无条件批量调用 |
| V9.0.0 | 移除ST_Cylinder结构体, 回归扁平接口; 新增传感器消抖; 极性取反完整实现 | Trae | 2026-05-30 | 8个VAR_INPUT+5个VAR_OUTPUT扁平接口; 命名对齐LSP-905(i_/q_前缀) |
| V8.1.0 | 明确电磁阀类型定义 | Trae | 2026-05-30 | 新增SolenoidType和ExtendPolarity参数 |
| V8.0.0 | 重构为VAR_IN_OUT ST_Cylinder结构 | Trae | 2026-05-30 | 参考FB_1003 VAR_IN_OUT模式 |
| V7.0.0 | 从FB_1002中独立拆分 | Trae | 2026-05-18 | 接口扁平化设计 |

## 3. 项目背景

### 3.1 项目来源

输送机系统中多个执行器（阻挡气缸、分料气缸、真空阀等）需要标准化的双位置执行器控制功能。原有逻辑耦合在FB_1002中，可复用性差，接口数量多，维护困难。

### 3.2 项目目标

为SysLib提供一个通用、高内聚、低耦合的双位置执行器控制功能块，支持：
- 标准化的动点(Extend)/原点(Retract)控制
- 传感器消抖确认（防抖动误触发）
- 传感器冗余一致性检查
- 动作超时保护
- 可配置的超时参数与消抖参数
- 独立实例化，支持多执行器场景
- 支持多种电磁阀类型选择（单线圈弹簧复位+双线圈中封）
- 极性取反完整实现（电磁阀输出+传感器映射+状态输出均反转）
- 双线圈A/B互锁与失电中封保持
- 手动/自动运行模式切换
- 运动中参数防呆锁存

### 3.3 项目范围

**包含范围**：
- 单气缸伸出/收回控制
- 上下位传感器检测（含TON消抖）
- 传感器冗余一致性检查（基于消抖后信号）
- 动作超时计时与报警（自动模式）
- 命令优先级处理（Extend > Retract）
- 电磁阀类型参数化配置（单线圈弹簧复位+双线圈中封）
- 极性取反完整实现（电磁阀+传感器+状态）
- 传感器TON消抖功能
- 双线圈A/B互锁与失电中封保持
- 手动/自动模式（手动跳过超时，线圈直接输出）
- 运动中参数防呆锁存（SolenoidType+Mode）
- 结构体接口（1个VAR_INPUT CONSTANT + 1个VAR_OUTPUT）

**不包含范围**：
- 气缸动作时机的编排（由上级功能块决定）
- 物理IO地址映射（由OB1完成）
- 报警码编码（由上级功能块完成）
- 多气缸协同逻辑

## 4. 电磁阀类型定义

### 4.1 电磁阀类型对照表（SolenoidType）

| SolenoidType值 | 电磁阀类型 | 线圈数量 | 阀位数 | 输出信号 | 默认行为（无命令时） | 当前V13.0.0支持 |
|-----------|---------|---------|-------|---------|------------------|---------------|
| **0** | **两位三通单线圈弹簧复位** | 1个 | 2位 | q_stSts.SolenoidA | 弹簧复位（收回） | 支持（默认） |
| **1** | **双线圈中封阀** | 2个 | 2位 | q_stSts.SolenoidA, q_stSts.SolenoidB | 失电中封保持 | 支持 |
| 2 | 3位4通中封阀 | 2个 | 3位 | 2个BOOL | 保持位置（中封） | 预留扩展 |
| 3 | 3位4通中泄阀 | 2个 | 3位 | 2个BOOL | 泄压回油（中泄） | 预留扩展 |

### 4.2 当前V13.0.0的配置

**FB_1011 V13.0.0 支持：单线圈弹簧复位阀 + 双线圈中封阀**

#### 4.2.1 单线圈弹簧复位阀（SolenoidType=0，默认）
- 线圈：1个
- 输出：q_stSts.SolenoidA（SolenoidB始终FALSE）
- SolenoidA=TRUE → 得电动作（可通过ExtendPolarity取反）
- SolenoidA=FALSE → 失电复位（弹簧复位）
- 安全性：失电后执行器自动复位（弹簧复位）

#### 4.2.2 双线圈中封阀（SolenoidType=1）
- 线圈：2个（线圈A=动点方向，线圈B=原点方向）
- 输出：q_stSts.SolenoidA（动点方向），q_stSts.SolenoidB（原点方向）
  - A/B互锁：任意时刻最多一个ON，禁止同时ON
- 伸出命令：q_stSts.SolenoidA=TRUE, q_stSts.SolenoidB=FALSE
- 收回命令：q_stSts.SolenoidA=FALSE, q_stSts.SolenoidB=TRUE
- 无命令时：保持当前位（失电中封保持，非弹簧复位）
- ELSE分支（无命令且非保持态）：SolenoidA=FALSE, SolenoidB=FALSE（全OFF安全态）
- 安全性：双线圈为双作用执行器，失电后中封保持最后位置

### 4.3 极性取反完整实现

#### 4.3.1 单线圈极性取反（ExtendPolarity）

| ExtendPolarity值 | 说明 | SolenoidA=TRUE | SolenoidA=FALSE | 传感器映射 | 状态输出 |
|---------------------|------|---------------------|---------------------|-----------|---------|
| FALSE (默认) | 正常极性 | 动点方向 | 原点方向 | ExtendedPos→IsExtended, RetractedPos→IsRetracted | 正常 |
| TRUE | 极性取反 | 原点方向 | 动点方向 | ExtendedPos→IsRetracted, RetractedPos→IsExtended | 反转 |

#### 4.3.2 双线圈极性取反（V10.0.0新增）

双线圈中封阀有两个独立极性参数：
- **ExtendPolarity**：控制线圈A（动点方向）极性
- **RetractPolarity**：控制线圈B（原点方向）极性

| ExtendPolarity | RetractPolarity | 伸出命令 | 收回命令 | 说明 |
|-------------------|-------------------|---------|---------|------|
| FALSE (默认) | FALSE (默认) | A=TRUE,B=FALSE | A=FALSE,B=TRUE | 正常极性 |
| TRUE | FALSE | A=FALSE,B=TRUE | A=TRUE,B=FALSE | 仅A极性取反 |
| FALSE | TRUE | A=TRUE,B=FALSE | A=FALSE,B=TRUE | 仅B极性取反 |
| TRUE | TRUE | A=FALSE,B=TRUE | A=TRUE,B=FALSE | A/B均取反 |

## 5. 需求概述

### 5.1 功能需求

| 需求编号 | 需求描述 | 优先级 | 备注 |
|---------|----------|--------|------|
| FR-001 | 接收动点命令，驱动电磁阀动作 | P0 | 核心功能; V11.0.0: 结构体接口i_stCmd:ST_CylinderCmd+q_stSts:ST_CylinderSts |
| FR-002 | 接收原点命令，驱动电磁阀复位 | P0 | 核心功能; 同上 |
| FR-003 | 检测动点到位传感器，反馈到位状态 | P0 | 核心功能 |
| FR-004 | 检测原点到位传感器，反馈到位状态 | P0 | 核心功能 |
| FR-005 | 传感器冗余一致性检查（两点同时ON检测） | P1 | 诊断功能 |
| FR-006 | 动作超时计时与报警（自动模式） | P1 | 安全功能; V12.0.0: 手动模式跳过超时 |
| FR-007 | 可配置超时时间 | P1 | 灵活配置 |
| FR-008 | 命令优先级处理（Extend > Retract） | P1 | 防冲突 |
| FR-009 | 电磁阀类型参数化配置 | P1 | 通用性需求 |
| FR-010 | 极性取反完整实现（电磁阀+传感器映射+状态输出均反转） | P1 | |
| FR-011 | 磁环传感器TON消抖 | P1 | |
| FR-012 | 定时器调用方式对齐LSP-903 V2.1.0三段式+顶部无条件批量调用 | P0 | |
| FR-013 | 双线圈中封阀控制（A/B互锁、中封保持、CASE分支） | P0 | |
| FR-014 | 双线圈极性取反（RetractPolarity独立控制线圈B极性） | P1 | |
| FR-015 | 手动/自动运行模式 | P1 | V12.0.0新增; Mode=0手动跳过超时, Mode=1自动全保护 |
| FR-016 | 运动中参数防呆锁存 | P1 | V12.0.0新增; SolenoidType+Mode运动中锁存, 空闲时刷新 |
| FR-017 | 结构体接口（1入1出） | P0 | V11.0.0; i_stCmd:ST_CylinderCmd(CONSTANT)+q_stSts:ST_CylinderSts |
| FR-018 | FB引脚重命名对齐LSP-905前缀规范 | P0 | V13.0.0; stCmd:=→i_stCmd:=, stSts=>→q_stSts=> |

### 5.2 非功能需求

| 需求编号 | 需求描述 | 优先级 | 备注 |
|---------|----------|--------|------|
| NFR-001 | 响应时间≤1ms（PLC扫描周期） | P0 | 实时性 |
| NFR-002 | 传感器一致性检查基于消抖后信号 | P1 | |
| NFR-003 | 超时仅报警不强制复位，保持输出 | P1 | 安全策略 |
| NFR-004 | 同一FB可实例化≥4个气缸 | P2 | 可复用性 |
| NFR-005 | 遵循LSP-904注释规范，使用英文半角标点 | P1 | 规范符合性 |
| NFR-006 | 预留3位阀扩展接口 | P2 | 双线圈已实现, 仅3位阀预留 |
| NFR-007 | 定时器实例每周期必须无条件调用()，禁止条件分支内调用 | P0 | LSP-903 V2.1.0 §3.4 |
| NFR-008 | 结构体接口支持整体保存/传递/快照 | P1 | V11.0.0新增 |

### 5.3 数据需求

| 需求编号 | 需求描述 | 优先级 | 备注 |
|---------|----------|--------|------|
| DR-001 | 通过结构体VAR_INPUT CONSTANT/VAR_OUTPUT传递所有命令、传感器、参数、状态 | P0 | V11.0.0变更 |
| DR-002 | 超时时间支持0~60000ms配置 | P1 | |
| DR-003 | 超时故障锁存，直到新命令清除 | P1 | |
| DR-004 | SolenoidType整数类型参数 | P1 | |
| DR-005 | ExtendPolarity布尔取反参数 | P1 | |
| DR-006 | 传感器消抖时间参数DebounceMs | P1 | |
| DR-007 | 双线圈原点方向极性取反参数RetractPolarity | P1 | |
| DR-008 | 电磁阀独立BOOL输出SolenoidA/SolenoidB | P0 | V11.0.0变更; 替代原q_aSolenoid ARRAY |
| DR-009 | 运行模式参数Mode（0=手动/1=自动） | P1 | V12.0.0新增 |
| DR-010 | 模式状态字ModeStatus（WORD） | P2 | V12.0.0新增; 预留上层序列控制器使用 |

## 6. 详细需求分析

### 6.1 接口定义（V13.0.0）

**VAR_INPUT CONSTANT**（1个结构体）：

| 变量名 | 类型 | 说明 |
|--------|------|------|
| i_stCmd | ST_CylinderCmd | 命令+传感器+参数结构体, CONSTANT禁止FB内部篡改 |

**ST_CylinderCmd字段**（V3.1.0）：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| Extend | BOOL | FALSE | 动点命令: 伸出/真空ON/夹紧/下降 |
| Retract | BOOL | FALSE | 原点命令: 收回/破真空/松开/上升 |
| ExtendedPos | BOOL | FALSE | 动点到位传感器 |
| RetractedPos | BOOL | FALSE | 原点到位传感器 |
| TimeoutMs | DINT | 5000 | 超时时间(ms), 0=关闭 |
| DebounceMs | DINT | 0 | 传感器消抖时间(ms), 0=关闭 |
| SolenoidType | INT | 0 | 电磁阀类型: 0=单线圈弹簧复位, 1=双线圈中封阀 |
| ExtendPolarity | BOOL | FALSE | 线圈A极性取反 |
| RetractPolarity | BOOL | FALSE | 线圈B极性取反（仅双线圈生效） |
| Mode | INT | 1 | 运行模式: 0=手动, 1=自动; 默认自动安全态 |
| ModeStatus | WORD | 16#0000 | 模式状态字, 预留 |

**VAR_OUTPUT**（1个结构体）：

| 变量名 | 类型 | 说明 |
|--------|------|------|
| q_stSts | ST_CylinderSts | 线圈输出+到位状态+诊断结构体 |

**ST_CylinderSts字段**（V3.0.0）：

| 字段 | 类型 | 说明 |
|------|------|------|
| SolenoidA | BOOL | 线圈A输出: 动点方向; 单线圈仅用此输出 |
| SolenoidB | BOOL | 线圈B输出: 原点方向; 单线圈时始终FALSE |
| IsExtended | BOOL | 已到动点（极性映射后） |
| IsRetracted | BOOL | 已到原点（极性映射后） |
| Timeout | BOOL | 动作超时报警（自动模式） |
| SensorFault | BOOL | 传感器冗余故障 |

### 6.2 防呆锁存机制（V12.0.0）

```
IF NOT s_bMoving THEN
    s_iLatchedSolenoidType := i_stCmd.SolenoidType;
    s_iLatchedMode := i_stCmd.Mode;
END_IF;
```

- 运动中（s_bMoving=TRUE）：SolenoidType和Mode锁存不变，防止参数跳变
- 空闲时（s_bMoving=FALSE）：自动刷新锁存值，下次动作时生效
- CASE分支使用锁存值 `s_iLatchedSolenoidType`，而非直接读 `i_stCmd.SolenoidType`

### 6.3 手动/自动模式（V12.0.0）

| 模式 | Mode值 | 超时检测 | 传感器故障检测 | 线圈输出 |
|------|--------|---------|--------------|---------|
| 手动 | 0 | 跳过 | 仍检测 | 直接输出到位 |
| 自动 | 1（默认） | 全保护 | 检测 | 正常逻辑 |

### 6.4 命令处理（CASE s_iLatchedSolenoidType分支）

- SolenoidType=0：单线圈弹簧复位逻辑
- SolenoidType=1：双线圈中封逻辑（A/B互锁）
- ELSE：安全态兜底（SolenoidA=FALSE, SolenoidB=FALSE）

## 7. 验收标准

### 7.1 功能验收（V13.0.0更新）

| 验收编号 | 验收项 | 验收标准 |
|---------|--------|----------|
| AC-001 | 伸出控制 | i_stCmd.Extend=TRUE时SolenoidA输出正确, 到位后IsExtended=TRUE |
| AC-002 | 收回控制 | i_stCmd.Retract=TRUE时输出正确, 到位后IsRetracted=TRUE |
| AC-003 | 超时保护 | 超时后Timeout=TRUE（自动模式） |
| AC-004 | 传感器冗余 | 消抖后两点同时ON时SensorFault=TRUE |
| AC-005 | 命令优先级 | Extend和Retract同时TRUE时, Extend优先 |
| AC-006 | 极性取反 | ExtendPolarity=TRUE时, 电磁阀+传感器+状态均反转 |
| AC-007 | 消抖功能 | DebounceMs>0时, 传感器抖动不触发误判 |
| AC-008 | 双线圈互锁 | SolenoidType=1时, SolenoidA和SolenoidB任意时刻最多一个ON |
| AC-009 | 双线圈保持位 | SolenoidType=1时, 无命令期间保持中封; CASE ELSE时全OFF |
| AC-010 | 结构体接口 | i_stCmd:ST_CylinderCmd + q_stSts:ST_CylinderSts, 引脚数=2 |
| AC-011 | 防呆锁存 | 运动中修改SolenoidType/Mode不影响输出, 空闲后刷新生效 |
| AC-012 | 手动模式 | Mode=0时跳过超时检测, 线圈直接输出; 传感器故障仍检测 |
| AC-013 | 引脚重命名 | stCmd:=→i_stCmd:=, stSts=>→q_stSts=> |

### 7.2 非功能验收

| 验收编号 | 验收项 | 验收标准 |
|---------|--------|----------|
| AC-014 | 响应时间 | 输入变化后，输出在1个扫描周期内更新 |
| AC-015 | 定时器规范 | 3个定时器()调用集中在FB顶部无条件批量调用区 |
| AC-016 | 可复用性 | 4个实例同时运行，互不干扰 |

## 8. 风险评估

| 风险编号 | 风险名称 | 风险描述 | 严重程度 | 发生概率 | 应对措施 |
|---------|---------|---------|---------|---------|---------|
| RA-001 | 结构体接口迁移 | V11.0.0从扁平→结构体, 所有调用方需重构 | 高 | 已发生 | 提供迁移指南; 调用方引脚数从14降为2 |
| RA-002 | 超时策略争议 | 超时后是否强制复位存在不同意见 | 中 | 中 | 保持当前策略（仅报警不复位），由上级决定 |
| RA-003 | V13.0.0引脚重命名 | stCmd→i_stCmd, stSts→q_stSts, 调用方需更新 | 中 | 已发生 | 仅重命名引脚名, 结构体字段不变; 提供迁移指南 |
| RA-004 | 防呆锁存延迟生效 | 运动中修改参数不会立即生效, 需等空闲 | 低 | 低 | 设计意图如此, 文档说明即可 |
| RA-005 | 手动模式安全 | 手动模式跳过超时可能导致线圈持续输出 | 中 | 低 | 手动模式仍保留传感器故障检测; 由上层保障安全 |

## 9. 版本详细变更说明

### V13.0.0 版本详细变更

1. **Breaking Change: FB引脚重命名**: stCmd:=→i_stCmd:=, stSts=>→q_stSts=>, 对齐LSP-905 V1.0.2 §3.1前缀规范
2. 结构体内部字段名不变, 仅FB级引脚名变更
3. 新增FR-018: FB引脚重命名对齐LSP-905前缀规范
4. 更新AC-013: 引脚重命名验收

### V12.0.0 版本详细变更

1. **新增防呆锁存**: s_iLatchedSolenoidType + s_iLatchedMode, 运动中参数不可变, 空闲时自动刷新
2. **新增运行模式**: i_stCmd.Mode（0=手动/1=自动）, 手动模式跳过超时检测, 线圈直接输出
3. **新增模式状态字**: i_stCmd.ModeStatus（WORD）, 预留上层序列控制器使用
4. **CASE分支改用锁存值**: CASE s_iLatchedSolenoidType, 不再直接读i_stCmd.SolenoidType
5. 新增FR-015: 手动/自动运行模式
6. 新增FR-016: 运动中参数防呆锁存
7. 新增DR-009: Mode参数
8. 新增DR-010: ModeStatus参数
9. 新增AC-011: 防呆锁存验收
10. 新增AC-012: 手动模式验收
11. 新增RA-004: 防呆锁存延迟生效风险
12. 新增RA-005: 手动模式安全风险

### V11.0.0 版本详细变更

1. **Breaking Change: 扁平→结构体接口**: VAR_INPUT CONSTANT i_stCmd:ST_CylinderCmd + VAR_OUTPUT q_stSts:ST_CylinderSts
2. **删除ARRAY输出**: q_aSolenoid[0..7] → q_stSts.SolenoidA/SolenoidB 两个独立BOOL
3. **FB引脚数**: 14个引脚(9入5出) → 2个引脚(1入1出)
4. **SolenoidType注释对齐实际场景**: 0=两位三通单线圈弹簧复位(气缸阀/真空阀), 1=双线圈中封阀(失电中封保持)
5. **真空阀纳入SolenoidType=0**
6. 新增FR-017: 结构体接口
7. 新增NFR-008: 结构体接口支持整体保存/传递/快照
8. 更新DR-001: 从扁平→结构体
9. 更新DR-008: 从ARRAY→独立BOOL
10. 新增RA-001: 结构体接口迁移风险

## 10. 附录