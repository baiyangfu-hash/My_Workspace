# 工作空间 AI 协作入口

本仓库由多个 AI 共用（Trae、Cursor、Codex、Antigravity 等）。**规则真源不重复维护**，各工具读取同一路径。

## 真源索引

| 用途 | 路径 |
|------|------|
| 跨 AI 共存与路由 | `.cursor/rules/workspace-ai-coexistence.mdc` |
| 全局开发规则 | `.trae/rules/project-rule.md` |
| 跨技能公共契约 | `.trae/skills/shared/refs/skill_coordination.md` |
| PM 主入口 | `.trae/skills/pm-workflow/SKILL.md` |
| 全栈执行 | `.trae/skills/fullstack-engineer/SKILL.md` |
| PLC 执行 | `.trae/skills/plc-electrical-engineer/SKILL.md` |
| 规范注册表 | `00_Obsidian_Base全局规范文件仓库/spec_registry.json` |

## 默认分工

- **pm-workflow**：PM_SESSION 与 `.auto-pm/ai_feedback.json` 的落账 owner（除非用户指定其他 AI 承担）
- **执行技能**（fullstack / plc）：改代码、跑测试、产出 `handoff_result` 或 `.auto-pm/handoffs/<request_id>.json`
- **基础设施**：`.trae/` 由 Trae 生态维护；其他 AI 只读，除非用户明确要求修改

## 版本库策略

- **纳入 Git**：`.trae/skills/`、`.trae/rules/`、`.cursor/rules/`、`AGENTS.md`
- **不纳入 Git**：`.cursor/` 下除 `rules/`、`commands/` 外的本地状态；`.trae/tmp_*` 等临时文件（见根目录 `.gitignore`）
