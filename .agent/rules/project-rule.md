---
description: "跨 AI 协作、统一技能真源与零负担执行铁律 (Antigravity / Codex / Trae / Cursor)"
alwaysApply: true
---

# 工作空间 AI 统一协作准则 (Multi-AI Universal Directive)

本工作空间由多个 AI 协作开发（Antigravity、Codex、Trae、Cursor）。**所有 AI 严格遵循同一套工作流真源与规范**。

## 1. 核心真源映射 (Single Source of Truth)

| 用途 | 绝对路径 |
|:---|:---|
| **PM 主工作流** | `.agent/skills/pm-workflow/SKILL.md` (或 `.trae/skills/pm-workflow/SKILL.md`) |
| **PLC 电气工程** | `.agent/skills/plc-electrical-engineer/SKILL.md` (或 `.trae/skills/plc-electrical-engineer/SKILL.md`) |
| **全栈高级语言** | `.agent/skills/fullstack-engineer/SKILL.md` (或 `.trae/skills/fullstack-engineer/SKILL.md`) |
| **Obsidian 规范注册表** | `00_Obsidian_Base全局规范文件仓库/spec_registry.json` |
| **全局项目规则** | `AGENTS.md` & `.trae/rules/project-rule.md` |

---

## 2. 强制协同铁律（所有 AI 无论接收到什么指令，必须严格遵循）

1. **【阶段 0：需求澄清与输入门禁】**：
   - 严禁脑补需求！收到非标自动化或重大功能变更诉求时，PM 角色首先核查 3 必备要素：① 机械 CAD/3D/实机梯形图、② 轴系与动力源、③ 动作时序与工艺参数；
   - 关键要素缺失时，**必须先发起《需求澄清提问清单》向用户提问**。
2. **【阶段 1：报批】**：
   - PM 角色输出《需求分析与技术实施计划》（注明依据规范与受影响文件），**必须显式停下来等待用户确认（“请确认是否批准开工？”）**。
3. **【阶段 2：执行】**：
   - 用户明确批准后，派发给对应执行技能（PLC / 全栈）编写代码与测试：
     - **PLC 6 大底线**：LSP-905 语法白名单、命名前缀（`i_`/`o_`/`s_`/`io_`）、三段式 DINT 毫秒定时器、状态机 CASE ELSE 防死锁、结构体整块传递（`VAR_IN_OUT io_st<Device>`）、STD-840 设备对象化解耦；
     - **全栈 5 大底线**：Google SRE 零崩溃、QML 5 层整洁架构、黄金信号、白盒日志、100% pytest 绿门禁。
4. **【阶段 3：验收】**：
   - 运行驾驶舱门禁：`auto-pm plc check <PID>` / `auto-pm doc check` / `pytest`；
   - 只有全量门禁 **Pass=100%, Warn=0, Fail=0** 才能呈报交付。

---

## 3. 跨终端驾驶舱 CLI 规范

系统已配置开发态全局直连，所有 AI 与开发者在任何终端均可直接执行：
- `auto-pm plc check <PID>`：PLC 静态合规门禁扫描
- `auto-pm doc check`：全系统文档与版本锁门禁
- `auto-pm plc repair <PID> --auto-fix`：SCL 标点与格式一键自愈
- `pytest tests/`：全栈自动化测试套件
