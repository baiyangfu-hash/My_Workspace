# FB_1004_GlueMachineFeeder 语法错误修复计划

## 📋 问题分析

通过对 `FB_1004_GlueMachineFeeder_BufferFraming.scl` 文件的全面检查，发现以下 **4处语法错误**：

### 错误1: 定时器调用缺少Q参数变量
**位置**: 第298-301行
```scl
// ❌ 错误: Q参数缺少变量
fb_tActionTimer(IN := FALSE, PT := T#0ms, Q => , ET => q_eAction_Elapsed);
fb_tCommTimeoutTimer(IN := FALSE, PT := T#0ms, Q => , ET => q_eCommTimeout_Elapsed);
fb_tInitTimer(IN := FALSE, PT := T#0ms, Q => , ET => q_eInit_Elapsed);
fb_tPickupHoldTimer(IN := FALSE, PT := T#0ms, Q => , ET => q_ePickupHold_Elapsed);

// ✅ 正确: 需要提供Q参数变量
fb_tActionTimer(IN := FALSE, PT := T#0ms, Q => , ET => q_eAction_Elapsed);
```

### 错误2: 常量名不一致（中文残留）
**位置**: 第270、295行
```scl
// ❌ 错误: 使用了旧的中文常量名
s_iCurrentStep := STP_空闲;    // 应该是 STP_Idle
o_iCurrentState := STP_空闲;   // 应该是 STP_Idle

// ✅ 正确
s_iCurrentStep := STP_Idle;
o_iCurrentState := STP_Idle;
```

### 错误3: 缺少分号
**位置**: 第270行
```scl
// ❌ 错误: 缺少分号
s_iCurrentStep               := STP_空闲

// ✅ 正确
s_iCurrentStep := STP_Idle;
```

## 🔧 修复方案

### 修复步骤

**步骤1**: 添加定时器Q参数的内部变量声明
在VAR区域添加4个布尔变量用于存储定时器Q输出：
```scl
s_bActionTimer_Q          : BOOL;    // 动作定时器输出
s_bCommTimeoutTimer_Q     : BOOL;    // 通讯超时定时器输出
s_bInitTimer_Q            : BOOL;    // 初始化定时器输出
s_bPickupHoldTimer_Q      : BOOL;    // 抓料保持定时器输出
```

**步骤2**: 修复定时器调用语句（第298-301行）
```scl
fb_tActionTimer(IN := FALSE, PT := T#0ms, Q => s_bActionTimer_Q, ET => q_eAction_Elapsed);
fb_tCommTimeoutTimer(IN := FALSE, PT := T#0ms, Q => s_bCommTimeoutTimer_Q, ET => q_eCommTimeout_Elapsed);
fb_tInitTimer(IN := FALSE, PT := T#0ms, Q => s_bInitTimer_Q, ET => q_eInit_Elapsed);
fb_tPickupHoldTimer(IN := FALSE, PT := T#0ms, Q => s_bPickupHoldTimer_Q, ET => q_ePickupHold_Elapsed);
```

**步骤3**: 修复常量名和分号（第270、295行）
```scl
// 第270行
s_iCurrentStep := STP_Idle;  // 添加分号 + 常量名修正

// 第295行  
o_iCurrentState := STP_Idle; // 常量名修正
```

## 📁 涉及文件

| 文件路径 | 修改内容 | 修改行数 |
|---------|---------|---------|
| `feeder/FB_1004_GlueMachineFeeder_BufferFraming.scl` | 添加4个内部变量 + 修复4处语法错误 | 约8行 |

## ⏱️ 预计时间

| 任务 | 时间 |
|------|------|
| 读取文件 | 1分钟 |
| 添加变量声明 | 2分钟 |
| 修复定时器调用 | 2分钟 |
| 修复常量名 | 1分钟 |
| 验证修复 | 2分钟 |
| **总计** | **8分钟** |

## ✅ 验证标准

1. ✅ 所有红色错误波浪线消失
2. ✅ PLC编译器无错误提示（PS002错误消除）
3. ✅ 代码语法高亮正常
4. ✅ 所有变量名符合801命名规范

---

**计划版本**: V1.0  
**创建日期**: 2026-05-04  
**状态**: 待批准执行