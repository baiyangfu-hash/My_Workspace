# Tasks - Trae IDE + Siemens SCL 插件修复

## 阶段一：规范文档准备（已完成 ✅）
- [x] Task 1: 完成问题诊断分析
  - [x] 1.1 提取错误信息（`STUB_BUILTIN: B:ValveCtrl` panic）
  - [x] 1.2 分析项目结构（OB1 → FB_ValveControl 调用链）
  - [x] 1.3 调研插件背景（plccheck v2.6.1, Go语言, VS Code扩展）
  - [x] 1.4 明确环境：**Trae IDE**（基于VS Code）+ **VS Code Marketplace 扩展**
  - [x] 1.5 提出3个根因假设（工作区/语法/Trae兼容性）

- [x] Task 2: 制定解决方案
  - [x] 2.1 方案1：调整 Trae IDE 工作区文件夹
  - [x] 2.2 方案2：使用命令行诊断（npx plccheck test）
  - [x] 2.3 方案3：修改 OB1.scl 语法（移除引号）
  - [x] 2.4 方案4：回退插件版本
  - [x] 2.5 方案5：向作者报告bug（强调 Trae 兼容性）

- [x] Task 3: 编写规范文档
  - [x] 3.1 完成 spec.md（问题分析 + 5套解决方案，针对 Trae 环境）
  - [x] 3.2 完成 tasks.md（任务分解）
  - [x] 3.3 完成 checklist.md（验证清单）

## 阶段二：用户确认与方案选择（已完成 ✅）
- [x] Task 4: 用户审核并批准规范文档
  - [x] 4.1 用户审阅 spec.md 内容
  - [x] 4.2 确认环境：Trae IDE + VS Code 扩展
  - [x] 4.3 用户批准开始执行

## 阶段三：方案执行（已完成 ✅）
- [x] Task 5: 执行诊断和修复尝试
  - [x] 5.1 ✅ 检查 Node.js/npm 环境（v24.12.0 + 11.6.2）
  - [x] 5.2 ✅ 运行 `npx plccheck test . --list-cases --events-json`
  - [x] 5.3 ✅ 获取详细错误堆栈，定位到 OB1.scl:7
  - [x] 5.4 ✅ 尝试方案3：移除 OB1.scl 第7行的引号
  - [x] 5.5 ❌ 重新测试，问题仍然存在
  - [x] 5.6 ✅ 分析生成的临时 Go 代码文件
  - [x] 5.7 🎯 **发现真正的根因：插件代码生成器 bug**

### 🔬 关键发现详情

**问题确认：**
- **位置**: `blocks_ob_autogen.go` 第12行
- **错误代码**: `_ = builtins.B_ValveCtrl(...)` （调用 panic stub）
- **正确代码应该是**: `FB_FB_ValveControl(mem, &db_ValveCtrl)` （调用完整FB实现）
- **根因**: 插件的 OB 代码生成器在处理 FB 实例化时，错误地生成了对 builtin stub 的调用

**证据链：**
1. `blocks_fb_autogen.go` 包含完整的 `FB_FB_ValveControl()` 实现 ✅
2. `builtins/b_valvectrl.go` 是一个故意的 panic stub ❌
3. `blocks_ob_autogen.go` 错误地调用了 builtin 而非实际 FB ❌

## 阶段四：结论与建议（当前阶段）
- [x] Task 6: 最终诊断结论
  - [x] 6.1 ✅ 确认这是 **Dynamic Siemens Language Support v2.6.1 的代码生成器 bug**
  - [x] 6.2 ✅ 不是用户代码问题（OB1.scl / FB100.scl / GlobalVars.db 均正确）
  - [x] 6.3 ✅ 不是 Trae IDE 特有问题（原生 VS Code 也会有此问题）
  - [x] 6.4 ✅ 问题出在插件的 "OB → FB 实例化" 的 Go 代码生成逻辑

- [ ] Task 7: 后续行动建议（供用户选择）
  - [ ] 7.1 **方案A（推荐）**: 向插件作者报告此 bug
      - 邮箱：danielv@danielv.no
      - GitHub Issues：https://github.com/danielv/vscode_siemens/issues
      - 提供完整的复现材料和诊断日志
  - [ ] 7.2 **方案B**: 尝试回退到旧版本（v2.5.x 或 v2.4.x）
      - 可能在旧版本中此 bug 不存在
  - [ ] 7.3 **方案C（临时workaround）**: 手动修改生成的 Go 代码
      - 修改临时文件中的 `B_ValveCtrl` 调用为 `FB_FB_ValveControl`
      - ⚠️ 每次重新测试都会重新生成，不实用
  - [ ] 7.4 **方案D**: 等待插件作者修复
      - 关注 GitHub releases 或 npm 更新

# Task Dependencies
- [Task 5] depends on [Task 4] - 用户批准后执行 ✅
- [Task 6] depends on [Task 5] - 诊断完成后得出结论 ✅
- [Task 7] depends on [Task 6] - 基于结论提供后续选项 ⏳
