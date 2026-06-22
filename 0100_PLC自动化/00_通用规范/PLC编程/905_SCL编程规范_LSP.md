---
spec_id: LSP-905
title: "SCL编程规范"
version: "V1.0.3"
domain: plc
lifecycle: stable
canonical_path: "0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范_LSP.md"
replaces: [DEV-801, DEV-810]
tags: ["SCL", "编程", "核心规范", "LSP"]
---

# SCL 编程规范 (Siemens LSP 兼容版)

> 版本：V1.0.3
> 状态：已验证
> 更新日期：2026-06-21
> 适用环境：Siemens LSP (VS Code)、TIA Portal、CODESYS、GX Works

---

## 1. 核心规则概览

| 规则类别 | 核心要求 | 状态 |
|----------|----------|------|
| **语法白名单** | **除本规范明确列出的语法外，禁止使用任何其他SCL/IEC语法特性**（含GOTO、标签、REPEAT、指针等未列出项） | ❌ 禁止 |
| METHOD支持 | **Siemens LSP插件不支持METHOD语法**，需改用普通代码块 | ⚠️ 限制 |
| 变量命名 | 小驼峰命名，英文为主 | ✅ 强制 |
| 注释格式 | 使用 `//` 或单层 `(* *)` | ✅ 强制 |
| 标点符号 | 必须使用英文半角标点 | ✅ 强制 |
| 定时器调用 | 必须包含完整参数(IN/PT/Q/ET)，Q参数不能为空 | ✅ 强制 |
| VAR_TEMP位置 | 必须在VAR块中定义，不能在程序中间定义 | ✅ 强制 |
| GOTO/标签 | **Siemens LSP不支持GOTO和标签语法**，必须用IF-ELSE替代 | ❌ 禁止 |

---

## 2. METHOD 定义与调用规范

### 2.1 METHOD 定义规则

**✅ 正确格式**
```scl
METHOD AutoModeStateMachine : VOID
    // 方法实现...
END_METHOD

METHOD ManualModeControl : VOID
    // 方法实现...
END_METHOD
```

**❌ 错误格式**
```scl
// 错误：METHOD名称不应使用 CALL_ 前缀
METHOD CALL_AutoModeStateMachine : VOID
    // 方法实现...
END_METHOD
```

### 2.2 METHOD 调用规则

**✅ 正确格式**
```scl
// 直接调用方法，无需 CALL 关键字
AutoModeStateMachine();
ManualModeControl();
```

**❌ 错误格式**
```scl
// 错误：不需要 CALL_ 前缀
CALL_AutoModeStateMachine();
```

### 2.3 METHOD 返回值处理

```scl
// 带返回值的方法定义
METHOD CalculateSpeed : REAL
    // 计算逻辑...
    CalculateSpeed := 100.0;
END_METHOD

// 调用并接收返回值
rCurrentSpeed := CalculateSpeed();
```

---

## 3. 变量命名规范

### 3.1 命名约定

| 前缀 | 含义 | 示例 |
|------|------|------|
| `i_` | Input - 输入变量 | `i_bStart`, `i_rSpeed` |
| `o_` | Output - 输出变量 | `o_bRunning`, `o_iStatus` |
| `q_` | Query - 查询变量（只读输出） | `q_eElapsedTime`, `q_bIsReady` |
| `s_` | Static/Internal - 内部静态变量 | `s_bRunning`, `s_iCurrentStep` |
| `fb_` | Function Block - 功能块实例 | `fb_tActionTimer`, `fb_ValveControl` |
| `CONST_` | Constant - 常量 | `CONST_MAX_SPEED`, `CONST_TIMEOUT` |

### 3.2 命名规则

```scl
// ✅ 正确 - 小驼峰命名
VAR_INPUT
    i_bStart : BOOL;           // 启动信号
    i_rSpeedSetpoint : REAL;   // 速度设定值
    i_iMaxCycle : INT;         // 最大循环次数
END_VAR

VAR_OUTPUT
    o_bRunning : BOOL;         // 运行状态
    o_iErrorCode : INT;        // 错误代码
END_VAR

VAR
    s_bInitialized : BOOL;     // 初始化标志
    s_iCurrentStep : INT;      // 当前步序
    fb_tActionTimer : FB_TON;  // 动作定时器
END_VAR
```

### 3.3 禁止使用的命名方式

```scl
// ❌ 错误 - 中文变量名
VAR
    运行标志 : BOOL;           // 禁止：中文变量名
    当前步骤 : INT;            // 禁止：中文变量名
END_VAR

// ❌ 错误 - 下划线命名（除前缀外）
VAR
    i_b_start : BOOL;          // 禁止：多余下划线
    o_i_error_code : INT;      // 禁止：多余下划线
END_VAR
```

---

## 4. 语法规则速查

> **⚠️ 语法白名单原则**：本节列出的语法为**唯一允许使用的SCL语法集合**。凡未在本规范中明确列出的语法特性（包括但不限于 GOTO/标签、REPEAT、指针运算 `^` / `ADR` / `REF_TO`、联合体 UNION、变体 VARIANT 等），一律禁止使用。如需使用新语法，必须先更新本规范并获得评审通过。

### 4.1 块结构

```scl
// FUNCTION_BLOCK 结构
FUNCTION_BLOCK FB_Example
VAR_INPUT
    // 输入变量声明
END_VAR
VAR_OUTPUT
    // 输出变量声明
END_VAR
VAR
    // 内部变量声明
END_VAR
VAR_TEMP
    // 临时变量声明（每次扫描复位）
END_VAR
METHODS
    // 方法声明
    METHOD MethodName : VOID;
END_METHODS
BEGIN
    // 主程序逻辑
    MethodName();
END_FUNCTION_BLOCK

// METHOD 实现（在 FUNCTION_BLOCK 外部或内部）
METHOD FB_Example.MethodName : VOID
    // 方法逻辑
END_METHOD
```

### 4.2 控制结构

```scl
// IF-THEN-ELSE
IF Condition THEN
    // 逻辑1
ELSIF AnotherCondition THEN
    // 逻辑2
ELSE
    // 逻辑3
END_IF;

// CASE 语句
CASE iValue OF
    0:  // 分支0
    1:  // 分支1
    2:  // 分支2
ELSE
    // 默认分支
END_CASE;

// FOR 循环
FOR i := 0 TO 10 BY 1 DO
    // 循环体
END_FOR;

// WHILE 循环
WHILE Condition DO
    // 循环体
END_WHILE;
```

### 4.3 定时器调用规范

```scl
// ✅ 正确 - 完整参数调用, PT 使用 DINT 类型(扫描周期数)
fb_tActionTimer.IN := FALSE;
fb_tActionTimer.PT := 500;
fb_tActionTimer(IN := fb_tActionTimer.IN, PT := fb_tActionTimer.PT,
                 Q => s_bTimer_Q, ET => q_eElapsed);

// ❌ 错误 - 使用 TIME 字面量(LSP 不支持 TIME 类型)
fb_tActionTimer(IN := FALSE, PT := T#500ms, Q => s_bTimer_Q, ET => q_eElapsed);

// ❌ 错误 - 缺少 Q 参数
fb_tActionTimer(IN := FALSE, PT := 500, Q => , ET => q_eElapsed);
```

> **重要**：定时器调用必须包含所有参数（IN、PT、Q、ET），Q 参数不能省略。PT 参数必须使用 DINT 类型（扫描周期数），禁止使用 TIME 字面量（如 `T#500ms`）。详见 903_定时器使用规范。

---

## 5. Siemens LSP 插件使用指南

### 5.1 插件配置

在 VS Code 中配置 `.vscode/settings.json`：

```json
{
    "siemens-lsp.enable": true,
    "siemens-lsp.language": "scl",
    "siemens-lsp.maxNumberOfProblems": 100,
    "files.associations": {
        "*.scl": "scl",
        "*.st": "scl",
        "*.db": "scl"
    }
}
```

### 5.2 常见错误及解决

| 错误代码 | 错误信息 | 原因 | 解决方法 |
|----------|----------|------|----------|
| PS001 | `unexpected token "CALL_XXX" in Statement` | METHOD定义使用了CALL_前缀 | 移除CALL_前缀 |
| PS002 | `missing Q parameter in TON call` | 定时器调用缺少Q参数 | 添加Q参数变量 |
| LX003 | `unexpected token ，` | 使用了中文标点 | 替换为英文标点 |
| TC100 | `cannot assign INT to TIME` | INT直接赋值给TIME | 使用DINT存储毫秒值 |

### 5.3 代码检查命令

```bash
# 在项目根目录运行代码检查
plccheck .

# 检查特定文件
plccheck feeder/FB_1004_GlueMachineFeeder_BufferFraming.scl

# 输出详细错误信息
plccheck --verbose .
```

---

## 6. 注释规范

### 6.1 注释格式

```scl
// ✅ 推荐 - 单行注释
// 功能块: 打胶机送料机构
// 描述: 控制X2轴取料和返回动作

(* ✅ 允许 - 多行注释（不嵌套）
 ============================================================================
 功能块名称: FB_1004_GlueMachineFeeder_BufferFraming
 描述: 打胶机送料机构 - 边框缓存机项目专用
 版本: V1.0.0
 ============================================================================
*)

// ❌ 禁止 - 嵌套注释
(* 外层注释
   (* 内层注释 *)   // 错误：嵌套
*)
```

### 6.2 注释密度要求

| 代码位置 | 注释要求 |
|----------|----------|
| 文件头部 | 必须有功能描述和版本信息 |
| 变量声明 | 每个I/O变量必须有注释 |
| 函数/METHOD | 必须有功能说明 |
| 关键逻辑 | IF/CASE分支必须有注释 |
| 复杂计算 | 计算前后必须有注释 |

---

## 7. 代码审查检查清单

| 检查项 | 说明 |
|--------|------|
| [ ] METHOD定义无CALL_前缀 | `METHOD Name : VOID` ✅ |
| [ ] METHOD调用无CALL_前缀 | `Name()` ✅ |
| [ ] 变量名符合命名规范 | 前缀正确，小驼峰 |
| [ ] 无中文变量名 | 全部使用英文 |
| [ ] 定时器调用完整 | IN、PT、Q、ET参数齐全 |
| [ ] 标点符号正确 | 使用英文半角标点 |
| [ ] 注释格式正确 | 无嵌套注释 |
| [ ] 无GOTO/标签语法 | LSP不支持，必须用IF-ELSE替代 |
| [ ] 语法白名单合规 | 仅使用§4明确列出的语法，无未列出的语法特性 |
| [ ] 语法检查通过 | `plccheck`无错误 |

---

## 8. 版本历史

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| V1.0.3 | 2026-06-21 | AI Assistant | 修正§4.3定时器示例: PT参数从TIME字面量(T#500ms)改为DINT类型(500), 与903/906对齐(C-01) |
| V1.0.0 | 2026-05-04 | AI Assistant | 初始版本，基于DJ-2026-005项目验证 |
| V1.0.2 | 2026-05-29 | AI Assistant | 新增§4.3跳转语句规范(禁止GOTO+标签)；新增§4语法白名单原则(除列出项外一律禁止)；修复FB_1020中GOTO重构为IF-ELSE |

---

## 9. 相关文档

- [903_Siemens-LSP_Go-Gen_定时器使用规范_DEV.md](./903_Siemens-LSP_Go-Gen_定时器使用规范_DEV.md)
- [904_SCL注释规范_LSP.md](./904_SCL注释规范_LSP.md)
- IEC 61131-3 编程规范