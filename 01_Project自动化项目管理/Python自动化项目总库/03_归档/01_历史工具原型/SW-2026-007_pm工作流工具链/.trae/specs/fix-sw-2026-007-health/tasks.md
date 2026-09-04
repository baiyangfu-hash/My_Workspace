# Tasks

- [x] Task 1: 创建 SW-2026-007 的 PM_SESSION
  - [x] SubTask 1.1: 创建 PM_SESSION_SW-2026-007.md，包含 §0-§9 完整章节
  - [x] SubTask 1.2: 填入 Spec Snapshot（从 spec_registry.json 读取版本号）
  - [x] SubTask 1.3: 创建 .github/hooks/ 和 .trae/handoffs/ 目录（项目自身也需合规）

- [x] Task 2: 注册 SW-2026-007 到 spec_registry.json
  - [x] SubTask 2.1: 在 spec_registry.json 的 specs 中新增 SW-2026-007 条目（domain=cross-domain, lifecycle=stable）

- [x] Task 3: 修复 pm_mgr/detect.py 搜索深度问题
  - [x] SubTask 3.1: 将 rglob 替换为带深度限制的递归搜索（max_depth=3）
  - [x] SubTask 3.2: 为 detect 添加超时保护（5秒内返回结果）

- [x] Task 4: 修复 pm_mgr/snapshot.py 规范列表不完整问题
  - [x] SubTask 4.1: 扩展 SPEC_IDS 字典，software 增加 DEV-210/211/220/INT-215/DEV-004/CHG-040/CHG-041/PM-042，plc 增加 LSP-904/903/906/907/INT-815/PLC-023/DEV-004/CHG-040/CHG-041/PM-042
  - [x] SubTask 4.2: 修复 read_spec_versions 从 SPEC_IDS 动态读取 spec_id 列表，而非硬编码6个
  - [x] SubTask 4.3: 扩展 spec_descs 字典，补充新增规范的中文说明

- [x] Task 5: 修复 pm_mgr/check.py 检查项不完整问题
  - [x] SubTask 5.1: 新增 PM_SESSION 章节完整性检查（§0-§9 是否齐全）
  - [x] SubTask 5.2: 新增检查项：项目目录下是否有 .gitignore（安全红线提示）

- [x] Task 6: 修复 pm_mgr/bootstrap.py software 目录结构不完整问题
  - [x] SubTask 6.1: 在 SW_DIRS 中补充 01_项目文档/01_启动过程, 01_项目文档/04_监控和控制, 01_项目文档/05_收尾过程
  - [x] SubTask 6.2: 在 SW_TEMPLATES 中补充 REQ/DES 等核心文档模板映射

- [x] Task 7: 升级 PM-004 规范至 V1.2.0
  - [x] SubTask 7.1: 在 PM-004 中新增 §9 pm-mgr 工具使用说明
  - [x] SubTask 7.2: 在 PM-004 中新增 §10 PM_SESSION 完整模板结构定义
  - [x] SubTask 7.3: 在 PM-004 §3 中新增 Event F/G/H 三种事件类型
  - [x] SubTask 7.4: 更新 PM-004 frontmatter version 为 V1.2.0
  - [x] SubTask 7.5: 更新 spec_registry.json 中 PM-004 版本为 V1.2.0

- [x] Task 8: 修复 python-rules.md 文件名引用格式
  - [x] SubTask 8.1: 移除4个规范文件名中的版本后缀（如 DEV-V1.1.0.md → DEV.md）

- [x] Task 9: 修复 plc-rules.md 版本号和文件名引用
  - [x] SubTask 9.1: 更新 LSP-903 版本号 V1.0.0 → V2.1.0
  - [x] SubTask 9.2: 更新 LSP-904 版本号 V1.1.0 → V1.2.0
  - [x] SubTask 9.3: 移除所有规范文件名中的版本后缀

# Task Dependencies

- [Task 1] 无依赖，可立即开始
- [Task 2] 无依赖，可立即开始
- [Task 3] 无依赖，可立即开始
- [Task 4] 无依赖，可立即开始
- [Task 5] 无依赖，可立即开始
- [Task 6] 无依赖，可立即开始
- [Task 7] 依赖 [Task 4]（PM-004 中 pm-mgr 说明需与 snapshot 修复后的 SPEC_IDS 一致）
- [Task 8] 无依赖，可立即开始
- [Task 9] 无依赖，可立即开始
- Task 1-6, 8-9 可并行执行；Task 7 需等 Task 4 完成后执行
