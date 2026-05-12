# Tasks

- [x] Task 1: 重构 TPL-SINGLE-PLC-001（单机设备PLC+HMI）— 核心变更
  - [x] 1.1 重写 `structure` 数组：按 DJ-2026-000 参考项目的 00~07 连续编号目录结构（含完整子目录）
  - [x] 1.2 重写 `templates` 数组：所有文件路径去除 `{project_code}` 等占位符，文件名使用纯中文名
  - [x] 1.3 编写文件内容模板：基于参考项目实际内容（任务模板.md、PLC项目规范.md、功能块说明.md等）填充 content
  - [x] 1.4 验证 structure 路径与 templates 路径前缀一致性
  - [x] 1.5 确保 02_PLC程序/功能块/ 下预留FB开发子目录结构说明

- [x] Task 2: 同步调整 TPL-FULLLINE-AUTO-001（自动化整线）
  - [x] 2.1 统一一级目录为连续编号风格（00~90范围单调递增，修复了07回退跳号）
  - [x] 2.2 所有 templates[].path 去除文件名中的占位符（9处→0处）

- [x] Task 3: 同步调整 TPL-SINGLE-ROBOT-001（单机机器人）
  - [x] 3.1 统一一级目录编号风格（修复07回退跳号，改为50递增）
  - [x] 3.2 所有 templates[].path 去除文件名中的占位符（6处→0处）
  - [x] 3.3 扩展机器人程序子目录（Source/Docs/仿真 三层结构）

- [x] Task 4: 微调 TPL-UPGRADE-STD-001（改造升级）
  - [x] 4.1 检查并统一编号连续性
  - [x] 4.2 去除文件名中的占位符（5处已清除）

- [x] Task 5: 更新 template_editor.py 文件命名提示
  - [x] 5.1 修改 `_add_file_template()` 的 placeholder
  - [x] 5.2 修改 `_add_file_template_under()` 同上

- [x] Task 6: 验证检查
  - [x] 6.1 正则检查：所有模板的 templates[].path 中不含 `{` 字符 → **0匹配**
  - [x] 6.2 结构检查：TPL-SINGLE-PLC-001 一级目录为 00~07 连续，无跳号 → **确认**
  - [x] 6.3 LSP 检查：constants.py 无语法错误 → **0诊断**
  - [x] 6.4 一致性检查：每个 structure path 在 templates 中有对应文件或说明文档 → **确认**

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] independent
- [Task 5] independent
- [Task 6] depends on [Task 1, 2, 3, 4, 5]
