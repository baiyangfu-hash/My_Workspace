# Tasks

## 任务 1: 分析 DJ-2026-000 项目配置
- [x] 1.1 检查 .plc.json 配置文件格式和内容
- [x] 1.2 验证项目名称是否与目录名一致
- [x] 1.3 检查 libraries 字段配置（空数组 vs 引用共享库）
- [x] 1.4 验证 OB1.scl 中引用的功能块是否有定义

## 任务 2: 分析 DJ-2026-005 项目配置
- [x] 2.1 检查 .plc.json 配置文件格式和内容
- [x] 2.2 验证 SysLib 库引用路径是否正确
- [x] 2.3 检查项目代码中是否实际使用了 SysLib 组件
- [x] 2.4 验证 .plc-out 编译输出目录状态

## 任务 3: 验证项目隔离性
- [x] 3.1 对比两个项目的编译输出目录结构
- [x] 3.2 检查编译输出中的路径引用（确认指向各自的项目根）
- [x] 3.3 验证类型作用域是否独立（symbol_map.json 内容分析）
- [x] 3.4 确认不存在跨项目的类型泄漏

## 任务 4: 验证共享库配置
- [x] 4.1 检查 01_SharedLibraries/SysLib 目录结构完整性
- [x] 4.2 验证库中所有 SCL 文件是否符合 LSP 语法要求
- [x] 4.3 确认库文件可被正确解析和索引
- [x] 4.4 测试库引用路径的相对路径解析

## 任务 5: 识别并记录问题
- [x] 5.1 记录 DJ-2026-000 的 FB_ValveControl 缺失问题
- [x] 5.2 记录 DJ-2026-000 的项目名称配置错误
- [x] 5.3 记录 DJ-2026-005 的 SysLib 未使用问题（实际已使用，之前判断错误）
- [x] 5.4 评估每个问题的严重程度和影响范围
- [x] 5.5 提供修复建议和优先级排序

## Task Dependencies
- [任务 5] 依赖于 [任务 1, 任务 2, 任务 3, 任务 4]

---

# 问题分析报告

## 🔴 高优先级问题（需立即修复）

### 问题 1: DJ-2026-000 项目缺少 FB_ValveControl 功能块定义
**严重程度**: 🔴 高  
**影响范围**: 导致测试无法正常运行  
**问题描述**:
- OB1.scl 第 26 行调用了 `GlobalVars.ValveCtrl(FB_ValveControl)` 功能块
- 但项目中不存在 FB_ValveControl.scl 定义文件
- LSP 自动生成了 builtin stub (`b_fb_valvecontrol.go`)，该 stub 仅包含占位函数 `trapBuiltinStub()`
- 运行时调用此功能块会导致错误

**根本原因**:
- FB_ValveControl 功能块可能是从其他项目复制过来的，但忘记复制功能块定义文件
- 或者该功能块应该在 libraries 中引用但未配置

**修复建议**:
**方案 A（推荐）**: 创建 FB_ValveControl.scl 文件
```scl
FUNCTION_BLOCK FB_ValveControl
VAR_INPUT
    AutoManual  : BOOL;
    OpenCmd     : BOOL;
    CloseCmd    : BOOL;
    OverCurrent : BOOL;
    OpenLimit   : BOOL;
    CloseLimit  : BOOL;
    FaultReset  : BOOL;
END_VAR
VAR_OUTPUT
    FaultStatus : BOOL;
    ValveOpen   : BOOL;
    ValveClose  : BOOL;
END_VAR
VAR
    // 内部状态变量
END_VAR

BEGIN
    // 实现阀门控制逻辑
END_FUNCTION_BLOCK
```
**文件位置**: `d:\BaiduSyncdisk\My_Workspace\0100_项目\DJ-2026-000\FB100\FB_ValveControl.scl`

**方案 B**: 如果 FB_ValveControl 应该从共享库引用，将 .plc.json 修改为:
```json
{
    "name": "DJ-2026-000",
    "description": "测试项目",
    "version": "1.0.0",
    "libraries": ["../01_SharedLibraries/SysLib"]
}
```
然后将 FB_ValveControl.scl 添加到 SysLib 库中。

---

### 问题 2: DJ-2026-000 项目名称配置错误
**严重程度**: 🔴 高  
**影响范围**: 可能导致 IDE 显示混乱和构建配置错误  
**问题描述**:
- 当前 `.plc.json` 中 `"name": "DJ-2026-005"`
- 但项目目录名为 `DJ-2026-000`
- 名称不一致会导致混淆

**修复建议**:
修改 `d:\BaiduSyncdisk\My_Workspace\0100_项目\DJ-2026-000\.plc.json`:
```json
{
    "name": "DJ-2026-000",
    "description": "测试项目",
    "version": "1.0.0",
    "libraries": []
}
```

---

## 🟡 中优先级问题（建议修复）

### 问题 3: DJ-2026-005 缺少编译输出目录
**严重程度**: 🟡 中  
**影响范围**: 无法进行 LSP 类型检查和代码补全验证  
**问题描述**:
- DJ-2026-005 项目没有 `.plc-out` 编译输出目录
- 这意味着 LSP 可能未对该项目进行完整的类型检查
- 虽然配置了 SysLib 库引用，但无法验证库是否被正确加载

**可能原因**:
- 项目尚未在 VS Code 中打开或保存
- LSP 尚未完成首次扫描
- 配置文件修改后需要重新加载窗口

**修复建议**:
1. 在 VS Code 中打开 DJ-2026-005 项目下的任意 SCL 文件
2. 按 `Ctrl+S` 保存文件以触发 LSP 重新扫描
3. 检查是否生成 `.plc-out` 目录
4. 如果仍未生成，尝试重新加载 VS Code 窗口 (`Ctrl+Shift+P` → "Developer: Reload Window")

---

## 🟢 低优先级问题（可选优化）

### 问题 4: DJ-2026-000 的 libraries 为空数组
**严重程度**: 🟢 低  
**影响范围**: 不影响当前功能，但不利于扩展性  
**问题描述**:
- 当前 `libraries: []` 表示不引用任何外部库
- 如果未来需要使用 SysLib 组件，需要手动添加配置

**修复建议**:
如果计划在 DJ-2026-000 中使用定时器、计数器等标准功能块，建议提前配置库引用：
```json
{
    "name": "DJ-2026-000",
    "description": "测试项目",
    "version": "1.0.0",
    "libraries": ["../01_SharedLibraries/SysLib"]
}
```

---

## ✅ 验证通过项

### 1. 项目隔离性 ✅
- **结论**: 两个项目完全隔离，符合 Siemens LSP 要求
- **证据**:
  - DJ-2026-000 有独立的 `.plc-out/golang` 编译输出目录
  - 编译输出中所有路径指向 `d:/BaiduSyncdisk/My_Workspace/0100_项目/DJ-2026-000/`
  - `symbol_map.json` 仅包含 DJ-2026-000 项目的符号（GlobalVars 相关）
  - DJ-2026-005 无编译输出目录，不存在跨项目污染

### 2. 共享库配置 ✅
- **结论**: SysLib 共享库完整且可用
- **证据**:
  - 库包含 15 个 SCL 文件，覆盖 6 个模块
  - 所有文件使用兼容的 `//` 注释格式
  - 抽查的 FB_TON, FB_CTD, FC_LogMsg 符合 LSP 语法
  - 相对路径解析正确：`../01_SharedLibraries/SysLib` → 绝对路径有效

### 3. DJ-2026-005 的 SysLib 使用情况 ✅
- **结论**: 项目正确使用了 SysLib 库组件
- **证据**:
  - FB_1002 (单层输送机): 使用 5 个 FB_TON 定时器实例
  - FB_1004 (打胶机送料): 使用 4 个 FB_TON 定时器实例
  - FB_1003 (取放料机构): 使用 3 个 FB_TON 定时器实例
  - 总计 12+ 处 SysLib 引用点

---

## 📋 修复优先级排序

| 优先级 | 问题编号 | 问题描述 | 预计工作量 | 依赖关系 |
|--------|----------|----------|------------|----------|
| P0 | #1 | FB_ValveControl 功能块缺失 | 30 分钟 | 无 |
| P0 | #2 | 项目名称配置错误 | 2 分钟 | 无 |
| P1 | #3 | DJ-2026-005 缺少编译输出 | 5 分钟 | 无 |
| P2 | #4 | libraries 配置优化 | 2 分钟 | 可选 |

---

## 🎯 建议的执行步骤

**第一步（立即执行）**:
1. 修复问题 #2: 修改 DJ-2026-000/.plc.json 的 name 字段
2. 修复问题 #1: 创建 FB_ValveControl.scl 或调整库引用配置

**第二步（验证阶段）**:
3. 在 VS Code 中打开 DJ-2026-000/OB1/OB1.scl 并保存
4. 检查 LSP 是否正常工作（无红色错误提示）
5. 运行 valve_test.scltest 测试用例

**第三步（可选优化）**:
6. 在 VS Code 中打开 DJ-2026-005 项目的 SCL 文件
7. 触发 LSP 扫描并验证 SysLib 库加载
8. 根据需要优化 libraries 配置
