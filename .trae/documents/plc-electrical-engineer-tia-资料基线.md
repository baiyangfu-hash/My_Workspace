# `plc-electrical-engineer` TIA 适配资料基线

## 1. 目的

本文档用于在重构 `plc-electrical-engineer` 技能前，锁定当前本地规范、示例功能块与文档之间的真实关系，避免后续技能设计再次混淆：

- TIA 平台事实
- 本地 LSP 规范
- 项目示例实现
- 文档与代码不一致项

## 2. 本次阅读范围

### 2.1 PLC 规范目录

- `0100_PLC自动化/00_通用规范/PLC编程/903_定时器使用规范_LSP.md`
- `0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范_LSP.md`
- `0100_PLC自动化/00_通用规范/PLC编程/906_错误预防规则_LSP.md`

### 2.2 示例功能块目录

- `0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1011_CylinderControl/FB_1011_CylinderControl.scl`
- `0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1011_CylinderControl/PRD/详细设计说明书_DSN-FB1011-CylinderControl-V9.0.0.md`
- `0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1011_CylinderControl/PRD/接口文档_IFC-FB1011-CylinderControl-V9.0.0.md`

## 3. 规范基线

### 3.1 `903_定时器使用规范_LSP.md` 的关键约束

当前本地定时器规范把 `FB_TON / FB_TONR` 定义为 SysLib 共享库定时器，并约束为：

1. `PT / ET` 类型为 `DINT`
2. 时间单位表述为“扫描周期（显式，DINT=毫秒等效值）”
3. 调用遵循三段式：
   - 预赋值
   - 全参数调用
   - 读输出
4. `V2.1.0` 明确要求：
   - 所有定时器 `()` 调用放在 FB 顶部无条件批量调用区
   - 禁止把定时器调用放到 `IF / ELSIF / CASE` 分支内
   - 禁止裸调用 `fb_tXxx()`

### 3.2 `905_SCL编程规范_LSP.md` 的关键约束

当前本地 SCL 编程规范强调：

1. 小驼峰 + 前缀命名
2. 禁止 GOTO / 标签 / 指针等白名单外语法
3. 定时器调用必须包含完整参数
4. 注释使用 `//` 或单层 `(* *)`

### 3.3 `906_错误预防规则_LSP.md` 的关键约束

当前错误预防规则强调：

1. `FB_TON` 的 `PT / ET` 是 `DINT`，不是 `TIME`
2. 定时器调用时 `Q` 不能为空
3. 不应修改 `.plc-out` 自动生成文件
4. 修改代码前必须先核对定时器规范与项目配置

## 4. `FB_1011_CylinderControl` 示例基线

### 4.1 当前源码的接口定位

当前 [FB_1011_CylinderControl.scl](file:///C:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1011_CylinderControl/FB_1011_CylinderControl.scl) 已经被通用化表述为“双位置电磁阀通用控制”，适用于：

- 气缸
- 真空阀
- 夹具
- 其他双位置执行机构

其主接口仍保持气缸语义：

- `i_bExtend`
- `i_bRetract`
- `i_bExtendedPos`
- `i_bRetractedPos`
- `i_dTimeoutMs`
- `i_dDebounceMs`
- `i_iSolenoidType`
- `i_bExtendPolarity`

### 4.2 当前源码里的实现特征

当前源码采用如下实现方式：

1. 传感器消抖在 `IF i_dDebounceMs > 0 THEN` 分支内完成
2. 在分支内先给实例赋值，再执行：
   - `fb_tDebounceExt()`
   - `fb_tDebounceRet()`
3. 超时定时器在命令处理后统一执行：
   - `fb_tTimeout()`
4. 当前源码注释把 `i_dTimeoutMs` / `i_dDebounceMs` 表述为“毫秒”

## 5. 已识别的不一致项

这一节非常重要，后续技能设计必须把这些“冲突事实”建模进去，而不是简单断言谁对谁错。

### 5.1 本地定时器规范 vs 当前 `FB_1011` 源码

冲突点：

1. `903_定时器使用规范_LSP.md` 要求：
   - 全参数调用
   - 顶部无条件批量调用
   - 禁止裸调用
2. 当前 `FB_1011_CylinderControl.scl` 实现为：
   - 在分支内调用
   - 裸调用 `fb_tDebounceExt()` / `fb_tDebounceRet()` / `fb_tTimeout()`

结论：

- 这不是单纯的“平台事实”问题，而是 **本地规范与当前示例实现发生了偏离**。
- 技能后续必须能明确说出：
  - 这是“本地规范偏差”
  - 不是自动等同于“TIA 平台不允许”

### 5.2 `FB_1011` 文档 vs 当前源码

`DSN / IFC` 中仍保留了旧版定时器调用口径：

1. 文档仍描述为：
   - 全参数调用
   - 顶部统一调用
2. 当前源码已经变成：
   - 分支内赋值 + 裸调用

结论：

- 当前 `FB_1011` 存在“**文档与代码不同步**”问题。
- 技能后续必须具备识别“源码 / IFC / DSN 三方不一致”的能力。

### 5.3 时间单位表述不一致

已读资料中存在三种表述：

1. `903`：扫描周期（DINT=毫秒等效值）
2. `IFC`：`i_dTimeoutMs` 是 `ms`，`i_dDebounceMs` 一处写“扫描周期”
3. 当前源码：`i_dTimeoutMs` / `i_dDebounceMs` 注释都写“毫秒”

结论：

- 当前项目对“DINT 时间值”的语义表达不统一。
- 技能后续应把这类问题识别为“**项目语义不一致**”，不能直接当作平台事实裁定。

## 6. 对技能重构的直接启示

### 6.1 技能必须先分层

后续技能必须先判断结论属于哪一类：

1. `TIA 平台事实`
2. `本地规范约定`
3. `项目实现偏差`
4. `文档与代码不同步`

### 6.2 技能必须具备“源程序-文档交叉审查”能力

不能只读 `.scl` 就给结论，也不能只看规范就给结论。至少要能交叉对照：

- 源码
- IFC
- DSN
- 本地规范

### 6.3 技能必须先看工艺边界

从 `FB_1011` 资料中可以确认，真正重要的问题不是只有语法，而是：

- 动点/原点语义
- 极性映射
- 单线圈两位阀默认行为
- 传感器消抖
- 超时
- 传感器缺失场景

这决定了技能必须先从工艺对象出发，而不是先做纯语法审查。

## 7. 编程前结论

在继续增强 `plc-electrical-engineer` 技能之前，必须把以下事实作为基线写入设计：

1. 技能必须面向 TIA Portal / S7-1200 / S7-1500 / SCL 主场景
2. 技能必须区分平台事实、本地规范、项目实现
3. 技能必须能识别规范与示例代码冲突
4. 技能必须能识别源码、IFC、DSN 不同步
5. 技能必须先看工艺，再看实现，再看规范

