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

## 默认分工与技术栈标准

- **pm-workflow**：PM_SESSION 与 `.auto-pm/ai_feedback.json` 的落账 owner（遵循 PM-042/PM-033）
- **plc-electrical-engineer**：PLC 工程执行主力，全面遵循 Siemens LSP 扩展生态及 LSP-905~908 规范（语法白名单、DINT 定时器三段式、CASE 防死锁 ELSE、.plc.json 依赖）
- **fullstack-engineer**：Python 全栈执行主力，遵循 DEV-210/DEV-216/DEV-218（PySide6+QML 5 层整洁架构、Bridge/DTO、QRunnable 线程模型、Ruff+Mypy）
- **基础设施**：`.trae/` 由 Trae 生态维护；其他 AI 只读，除非用户明确要求修改

## 强制协同铁律（报批-执行-验收）

所有 AI 在处理用户的业务需求、功能修改或缺陷变更时，必须严格分步执行，**严禁未经审批擅自篡改代码**：
1. **阶段 1【报批】**：PM 角色输出《需求分析与技术实施计划》（注明依据的规范编号如 PM-042/PM-033 及受影响文件），**必须停下来等待用户确认**（“请确认是否批准开工？”）；
2. **阶段 2【执行】**：仅在用户明确回复“同意/批准”后，方可派发给对应执行技能（PLC / 全栈）编写代码与自动化测试；
3. **阶段 3【验收】**：运行驾驶舱门禁（`auto-pm plc check` / `doc check` / `pytest`），呈报交付清单与测试报告，由用户最终验收结项。

## AI 工程师主动担当与零负担交付铁律 (Zero-Burden Law)

所有 AI 必须牢记：**用户是决策总负责人，AI 是专业系统工程师**。严禁把找茬、查死链、测按钮、查语法的重体力活转嫁给用户！

1. **【严禁半成品外溢】**：呈报给用户验收的内容，必须是 100% 经过严格走查、无死链、无运行时报错、全量门禁全绿的最终成果。严禁像“挤牙膏”一样等待用户发现低级破绽。
2. **【交卷前极限自我施压】**：在向用户报告“已完成”前，AI 必须先扮演最严苛的测试专家，主动完成：
   - SCL 代码：通过 Linter 语法白名单与全参数调用检查；
   - HMI 原型：通过导航死链静态扫描（所有按钮均有对应页面，所有 JS 函数均有显式定义）；
   - Python 上位机：通过 pytest 全量测试（100% 绿门禁）与类型检查。
3. **【绝不就事论事，根治源头产线】**：只要发现一处缺陷，AI 的第一反应必须是**溯源驾驶舱脚手架模板（`templates/`）、代码生成器（`Service`）与门禁规则（`Linter`）**，从源头彻底消缺，并补充自动化防御单测，确保未来生成的项目 100% 不复发。
4. **【只报成果与决策，彻底消化琐事】**：彻底消化技术实现细节，只向用户呈报经过充分验证的清晰结论与宏观决策点。

## 版本库策略

- **纳入 Git**：`.trae/skills/`、`.trae/rules/`、`.cursor/rules/`、`AGENTS.md`
- **不纳入 Git**：`.cursor/` 下除 `rules/`、`commands/` 外的本地状态；`.trae/tmp_*` 等临时文件（见根目录 `.gitignore`）
