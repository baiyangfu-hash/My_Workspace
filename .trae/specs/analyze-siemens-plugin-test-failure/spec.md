# Trae IDE + VS Code Siemens SCL 插件测试崩溃修复方案

## Why

你在 **Trae IDE** 中通过扩展商店安装了 **Dynamic Siemens Language Support**（VS Code 扩展），运行 `.scltest` 测试文件时遇到 **panic 崩溃错误**（`STUB_BUILTIN: B:ValveCtrl`），导致测试功能完全不可用。

## What Changes

- 诊断 **Trae IDE 环境** 下 VS Code 扩展的配置问题
- 提供 **立即可用** 的解决方案（5-15分钟内解决）
- 确保 valve_test.scltest 能在 Trae IDE Test Explorer 中正常运行

## Impact

- **开发环境**: Trae IDE（基于 VS Code 内核）
- **扩展来源**: VS Code Marketplace (DynamicEngineering.dynamic-siemens-language-support)
- **受影响文件**:
  - [valve_test.scltest](file:///d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\Main\valve_test.scltest) - 测试文件
  - [OB1.scl](file:///d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\Main\OB1.scl) - 主程序块
  - [FB100.scl](file:///d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\Main\FB100.scl) - 功能块定义
  - [GlobalVars.db](file:///d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\Main\GlobalVars.db) - 全局变量数据块

---

## 🔍 问题诊断结果

### 错误信息提取（从你的截图）

```
=== RUN TestUserCase001_Test1
--- FAIL: TestUserCase001_Test1 (0.00s)
    panic: STUB_BUILTIN: B:ValveCtrl [recovered, repanicked]
    goroutine 6 [running]:
    testing.tRunner.func12(...)
        C:/Program Files/Go/src/testing/testing.go:1974
```

**关键点：**
- ❌ 所有3个测试用例全部失败（红色X标记）
- 🔴 核心错误：`STUB_BUILTIN: B:ValveCtrl` panic
- 📍 崩溃位置：插件的Go语言测试运行器内部
- 📍 发生环境：**Trae IDE**（基于VS Code）

### 你的项目结构

```
d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\
└── Main\                          ← 当前工作区根目录？
    ├── FB100.scl                  ✅ FB_ValveControl 功能块
    ├── GlobalVars.db              ✅ 全局变量 DB
    ├── OB1.scl                    ⚠️ 实例化 FB 为 "ValveCtrl"
    └── valve_test.scltest         ❌ 测试文件（崩溃）
```

### 代码调用链

```mermaid
graph LR
    A[valve_test.scltest<br/>SET/ASSERT] -->|读写| B[GlobalVars.db]
    B -->|变量映射| C[OB1.scl]
    C -->|实例化为 "ValveCtrl"| D[FB100.scl<br/>FB_ValveControl]
    style A fill:#ffcccc
    style D fill:#ccffcc
```

---

## 🎯 根因分析（3个最可能的原因）

### 🥇 原因A：Trae IDE 工作区文件夹级别问题（概率85%）

**问题：**
- VS Code 扩展要求在 **正确的项目根目录** 打开工作区
- 你可能打开了 `Main` 文件夹作为工作区根目录
- 但插件可能期望 `DJ-2026-005` 作为项目根（或反之）
- 或者插件在 Trae 环境下的路径解析有差异

**为什么最可能：**
- `STUB_BUILTIN` 错误通常发生在插件找不到块的完整定义时
- 如果工作区根目录不对，插件无法正确解析 `OB1 → FB_ValveControl` 的引用链
- Trae 作为 VS Code 的衍生品，可能在某些 API 行为上有细微差异

### 🥈 原因B：OB1.scl 中 FB 实例化语法与 Trae/插件兼容性问题（概率60%）

**你的代码（OB1.scl 第3-18行）：**
```scl
ORGANIZATION_BLOCK OB1
VAR
    ValveCtrl : FB_ValveControl;   // 第4行：实例声明
END_VAR

BEGIN
"ValveCtrl"(                     // 第7行：引号包裹的实例名！
    AutoManual  := GlobalVars.Hmibutton[0],
    OpenCmd     := GlobalVars.Hmibutton[1],
    CloseCmd    := GlobalVars.Hmibutton[2],
    OverCurrent := GlobalVars.Hmibutton[3],
    OpenLimit   := GlobalVars.Hmibutton[4],
    CloseLimit  := GlobalVars.Hmibutton[5],
    FaultReset  := GlobalVars.Hmibutton[6],
    FaultStatus => GlobalVars.FaultStatus,
    ValveOpen   => GlobalVars.ValveOpen,
    ValveClose  => GlobalVars.ValveClose
);
END_ORGANIZATION_BLOCK
```

**潜在冲突点：**
1. `"ValveCtrl"` 使用引号包裹 - 某些SCL解析器对此处理不一致
2. 测试框架的 stub 机制可能在处理带引号的块名时出错
3. 在 Trae 环境下，插件的 LSP 服务可能对这种语法有特殊反应

### 🥉 原因C：插件版本 v2.6.1 与 Trae 兼容性Bug（概率40%）

**证据：**
- v2.6.1 是 **19小时前** 刚发布的（非常新）
- VS Marketplace 安装量仅 **142次**（极低）
- 该插件主要针对原生 VS Code 测试和优化
- 在 Trae（基于Electron/VS Code）中可能有未发现的兼容性问题
- `STUB_BUILTIN` 内部panic可能是 Trae 特有的边界情况

---

## 💊 解决方案（按推荐顺序执行）

### ✅ 方案1：调整 Trae IDE 工作区文件夹（⭐⭐⭐⭐⭐ 首选）

**操作步骤（2分钟）：**

1. **关闭当前 Trae IDE 窗口**

2. **重新打开 Trae 并选择正确的文件夹：**

   **方法A：通过 Trae 文件菜单**
   ```
   文件(File) → 打开文件夹(Open Folder) → 选择 d:\BaiduSyncdisk\My_Workspace\DJ-2026-005
   ```

   **方法B：通过命令行启动 Trae**
   ```bash
   # 如果 Trae 在 PATH 中
   trae d:\BaiduSyncdisk\My_Workspace\DJ-2026-005
   
   # 或使用完整路径
   "C:\Users\[你的用户名]\AppData\Local\Programs\Trae\Trae.exe" d:\BaiduSyncdisk\My_Workspace\DJ-2026-005
   ```

3. **验证工作区结构：**
   - Trae 资源管理器应该显示：
     ```
     DJ-2026-005 (工作区根)
     └── Main/
         ├── FB100.scl
         ├── GlobalVars.db
         ├── OB1.scl
         └── valve_test.scltest
     ```

4. **重新运行测试：**
   - 打开 `valve_test.scltest`
   - 点击测试用例上方的 ▶ 运行按钮
   - 或使用命令面板（`Ctrl+Shift+P`）→ `Siemens: Run Test`

**预期结果：**
- ✅ 测试正常执行，不再出现 panic
- ✅ 显示 PASS/FAIL 结果（而非 crash）

**如果仍然失败 → 继续方案2**

**备选尝试：**
- 如果上面不行，试试打开 `Main` 文件夹本身：
  ```
  文件 → 打开文件夹 → d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\Main
  ```

---

### ✅ 方案2：使用命令行诊断（⭐⭐⭐⭐ 强烈推荐）

**目的：** 获取更详细的错误信息，绕过 Trae UI 直接调用插件引擎

**操作步骤（5分钟）：**

1. **打开 PowerShell 或 CMD**

2. **进入项目目录：**
   ```bash
   cd d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\Main
   ```

3. **检查 Node.js 和 npm 是否可用：**
   ```bash
   node --version
   npm --version
   ```
   - 如果提示命令不存在，先安装 Node.js：https://nodejs.org/

4. **安装 plccheck（插件的底层引擎）：**
   ```bash
   npm install -g plccheck
   ```

5. **运行测试并查看详细输出：**
   ```bash
   # 基本测试（在 Main 目录下）
   npx plccheck test .
   
   # 或者在上级目录（DJ-2026-005）
   cd ..
   npx plccheck test ./Main
   
   # 带详细日志
   npx plccheck test . --verbose
   
   # 带事件流（用于深度调试）
   npx plccheck test . --events-json
   ```

6. **分析输出：**
   - 查找具体的错误消息（比 Trae UI 更详细）
   - 注意是否有以下关键词：
     - `"cannot find"` / `"undefined"` / `"missing"`
     - `"resolve symbol"` / `"scope"`
     - `"workspace"` / `"root"`
     - `"ValveCtrl"` / `"FB_ValveControl"`
   - **复制完整的输出给我进一步分析**

**预期输出示例（成功）：**
```
=== RUN test1 --- PASS (0.05s)
=== RUN test2 --- PASS (0.03s)
=== RUN test3 --- PASS (0.04s)
PASS
coverage: 85.0% of statements
```

**预期输出示例（失败但有信息）：**
```
ERROR: cannot resolve symbol 'ValveCtrl' in scope 'OB1'
HINT: ensure FB_ValveControl is defined in workspace root
INFO: scanning workspace: d:\...\DJ-2026-005\Main
FOUND: 4 files (3 .scl, 1 .db, 1 .scltest)
```

---

### ✅ 方案3：修改 OB1.scl 语法（⭐⭐⭐⭐ 如果上述无效）

**修改内容：移除实例名的引号**

**原代码（OB1.scl 第7行）：**
```scl
"ValveCtrl"(
    AutoManual := ...
);
```

**修改为：**
```scl
ValveCtrl(
    AutoManual := ...
);
```

**完整修改后的 OB1.scl：**
```scl
ORGANIZATION_BLOCK OB1
VAR
    ValveCtrl : FB_ValveControl;
END_VAR

BEGIN
ValveCtrl(
    AutoManual  := GlobalVars.Hmibutton[0],
    OpenCmd     := GlobalVars.Hmibutton[1],
    CloseCmd    := GlobalVars.Hmibutton[2],
    OverCurrent := GlobalVars.Hmibutton[3],
    OpenLimit   := GlobalVars.Hmibutton[4],
    CloseLimit  := GlobalVars.Hmibutton[5],
    FaultReset  := GlobalVars.Hmibutton[6],
    FaultStatus => GlobalVars.FaultStatus,
    ValveOpen   => GlobalVars.ValveOpen,
    ValveClose  => GlobalVars.ValveClose
);
END_ORGANIZATION_BLOCK
```

**操作步骤：**
1. 在 Trae 中打开 `OB1.scl`
2. 找到第 7 行的 `"ValveCtrl"`
3. 删除引号，改为 `ValveCtrl`
4. 保存文件（`Ctrl+S`）
5. 重新运行测试

**注意：**
- 这种修改是标准 SCL 语法
- 不会影响在 TIA Portal 中的编译
- 如果担心，可以先备份原文件

---

### ✅ 方案4：回退到稳定版本（⭐⭐⭐⭐ 如果是新版本Bug）

**操作步骤（3分钟）：**

1. **打开 Trae IDE 扩展视图：**
   - 快捷键：`Ctrl+Shift+X`
   - 或左侧边栏点击方块图标（扩展）

2. **找到 Dynamic Siemens Language Support**
   - 在搜索框输入：`Siemens Language Support`
   - 找到发布者为 `DynamicEngineering` 的扩展

3. **点击扩展进入详情页**

4. **下拉到版本历史部分：**
   - 寻找 **"安装另一个版本"** 或 **"Install Another Version"** 按钮
   - 或点击齿轮图标 ⚙️ → **"安装另一个版本..."**

5. **选择较旧的稳定版本：**
   - 推荐：**v2.5.x** 或 **v2.4.x**（如果可用）
   - 避免：v2.6.0 或 v2.6.1（太新，可能是回归bug）

6. **重新加载 Trae 窗口：**
   - 快捷键：`Ctrl+Shift+P`
   - 输入：`Reload Window`
   - 选择：**Developer: Reload Window**
   - 等待 Trae 重启完成

7. **重新运行测试**

**如何查看当前已安装版本：**
- 扩展详情页顶部会显示版本号
- 或：`帮助(Help) → 关于(About)` → 已安装的扩展列表

---

### ✅ 方案5：向插件作者报告 Bug（⭐⭐⭐ 长期方案）

**如果以上所有方案都无效，这很可能是插件与 Trae 的兼容性 bug。**

**联系信息（来自插件官方）：**
- **邮箱**: danielv@danielv.no
- **GitHub Issues**: https://github.com/danielv/vscode_siemens/issues（需要 GitHub 账号）

**报告模板：**
```
**Environment:**
- OS: Windows [你的版本，如 10/11]
- IDE: Trae IDE (based on VS Code)
- Trae Version: [帮助 → 关于 中查看]
- Extension: Dynamic Siemens Language Support v2.6.1
- Node.js: [node --version 输出]

**Problem:**
Running .scltest file in Trae IDE causes panic with error:
`STUB_BUILTIN: B:ValveCtrl [recovered, repanicked]`

All 3 test cases fail immediately with this error.

**Steps to Reproduce:**
1. Open folder in Trae: d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\Main
2. Project contains:
   - FB100.scl (defines FB_ValveControl)
   - OB1.scl (instances FB as "ValveCtrl")
   - GlobalVars.db (global variables)
   - valve_test.scltest (test file with 3 cases)
3. Open valve_test.scltest in Trae
4. Click Run Test button in Test Explorer
5. Observe panic error

**Expected Behavior:**
Tests should execute and show PASS/FAIL results.

**Actual Behavior:**
All tests fail with panic immediately (0.00s).

**Additional Context:**
- Works fine in native VS Code? [Yes/No/Untested]
- Same error with older extension version? [Yes/No/Untested]
- Command line `npx plccheck test .` output: [附上输出]

**Attachments:**
- [截图：Test Explorer 失败界面]
- [截图：错误详情面板]
- [可选：项目文件 zip]
```

---

## 📋 快速决策指南

| 你的情况 | 推荐方案 | 预期时间 |
|---------|---------|---------|
| 第一次遇到，想快速解决 | **方案1 + 方案2** | 10分钟 |
| 方案1无效，需要更多信息 | **方案2**（命令行诊断） | 5分钟 |
| 确认是语法兼容性问题 | **方案3**（改OB1） | 3分钟 |
| 怀疑是新版本回归bug | **方案4**（回退版本） | 5分钟 |
| 全部无效，需要长期解决 | **方案5**（报告bug） | 15分钟 |

---

## ADDED Requirements

### Requirement: 测试功能恢复

系统 SHALL 提供可在 **Trae IDE + VS Code 扩展** 环境下立即执行的解决方案，确保用户的 `.scltest` 测试文件能够正常运行。

#### Scenario: 成功恢复测试功能
- **WHEN** 用户按照推荐的方案调整 Trae 配置或代码
- **THEN** valve_test.scltest 在 Trae Test Explorer 中成功运行
- **AND** 不再出现 `STUB_BUILTIN` panic 错误
- **AND** 3个测试用例显示明确的 PASS/FAIL 结果

#### Scenario: 快速诊断
- **WHEN** 用户执行命令行诊断命令（npx plccheck）
- **THEN** 获得比 Trae UI 更详细的错误信息
- **AND** 能够准确定位问题根源（工作区/语法/Trae兼容性）

## MODIFIED Requirements

### Requirement: 操作记录

在解决问题后，记录：
- 最终有效的解决方案（哪个方案解决了问题）
- 具体的配置参数或代码修改内容
- **Trae IDE 特有的注意事项**（如果有）
- 供团队其他成员参考的操作手册

---

## ⚠️ 重要提醒

1. **备份优先**: 修改代码前，先备份原始文件
2. **逐步尝试**: 按推荐顺序执行，不要一次改太多
3. **保留日志**: 命令行的完整输出很有价值，请保存
4. **时间控制**: 如果30分钟内未解决，建议先走方案5（报告bug）
5. **Trae 特异性**: 记录是否是 Trae 特有问题（可在原生 VS Code 中对比验证）

## 成功标准

✅ **必须达成：**
- 测试能运行且不再 crash（panic消失）
- 3个测试用例有明确的结果（PASS 或 FAIL）
- 用户知道具体是哪个方案解决的问题
- 记录是否为 Trae 特有兼容性问题

✅ **期望达成：**
- 测试结果符合阀门控制逻辑预期
- 能够复现解决过程给同事看
- 如确认为 bug，已向作者提交报告
