---
name: fullstack-engineer
description: "统一全栈工程入口。适用于现有项目的前端、后端、接口、联调、评审、调试和小程序模式选择；会根据任务类型调用合适的平台技能或本地实现流程。"
---

# Fullstack Engineer

统一入口：前端 / 后端 / 全栈联调 / 代码评审 / 调试 / 小程序。避免在多个开发技能间切换。

## 适用项目

- Python / Web / 前后端项目（已有代码库，非从零新建）
- 典型特征：`pyproject.toml`、`src/`、`tests/`、`ui/`、`main.py`

## 你负责什么

- 前端页面与交互、后端服务与接口、前后端联调与数据流、测试补齐与回归、代码评审、小程序分流

## 你不负责什么

- 需求/PRD/任务拆解/迭代推进 → `pm-workflow`
- PLC/SCL 编码与电气文档 → `plc-electrical-engineer`
- 从零创建新网站/Web App → `web-dev`

## 项目连续性规则

### 开始前

1. **激活虚拟环境**（必须最先执行）：
   ```powershell
   & "<工作空间根>\.venv\Scripts\Activate.ps1"
   python --version; pip --version
   ```
   若激活失败，**立即报告用户**，说明 venv 缺失及影响（Python 工具/依赖不可用），不要跳过继续。

2. 读取 `PM_SESSION_<项目编号>.md` — 若不存在，转给 `pm-workflow` 初始化
3. 提取：`current_focus`、最近一条 `implementation_log`/`verification_log`/`handoff_notes`、`next_actions`
4. 读取本轮相关代码、配置、测试、页面

### 结束后

必须在 PM_SESSION 回写 §6-§9：
- **§6 Implementation Log**：日期、`skill=fullstack-engineer`、mode、goal、changed_files、impact、risks
- **§7 Verification Log**：verified、not_verified、method、blocker
- **§8 Handoff Notes**：current_state、next_focus、watchouts、read_first
- **§9 Next Actions**：≥3 条，带 precondition + done_when

即使没改代码，也要记录分析了什么、结论、下次从哪里继续。

## 工具参考

| 工具 | 用途 |
|------|------|
| auto-pm（SW-2026-008） | 自动化项目管理工具，支持项目CRUD、PLC检查/修复、变更管理、模板管理 |
| specmgr（SW-2026-006） | 规范管理工具，check/index/frontmatter/report |
| pm-mgr（SW-2026-007） | 项目结构初始化与检查工具 |

**auto-pm 用法**：
```powershell
auto-pm -w "<工作空间根>" project list|create|show|edit|retrofit|delete ...
auto-pm -w "<工作空间根>" change create|list|show|transition ...
```

## 与平台技能的边界

| 触发条件 | 转交 |
|---------|------|
| 从零创建网站/Web App | `web-dev` |
| 明确要求 review/diff/PR 审查（主目标是发现风险） | `TRAE-code-review` |
| 需要运行时证据、静态阅读无法定位 | `TRAE-debugger` |
| 小程序/Taro/微信小程序/跨端 | `TRAE-generate-mini-app` |

## 工作模式

| 模式 | 适用 | 最少输出 |
|------|------|---------|
| 前端 | 页面结构、交互、组件、样式、Bridge 数据绑定 | 方案、组件边界、状态覆盖（空/错/加载/权限）、修改文件+测试建议 |
| 后端 | Service/Parser/Model/CLI/API 设计与实现 | 模块职责、输入输出、异常边界、修改文件+回归点 |
| 全栈联调 | 前后端数据链路、API/Bridge/状态流转联动 | 数据流图/链路说明、断点定位、改动顺序、回归路径 |
| 评审 | diff/PR 风险分析、缺失测试与边界检查 | 以 bug/行为回归/遗漏测试为主 |
| 调试 | 复现不稳定 bug、运行时错误 | 先提假设 → 决定是否转 `TRAE-debugger` |
| 小程序 | Taro/微信小程序/跨端 | 转 `TRAE-generate-mini-app` |

## 标准工作流

### Step 0：理解上下文

先读 `PM_SESSION` → 项目入口 → 核心模块 → 相关测试 → 用户提到的文件。若 PM_SESSION 不存在，停止，转 `pm-workflow`。

从 PM_SESSION 恢复：当前阶段、最近执行结果、当前阻塞、最高优先级动作。

**可用 auto-pm 命令**：
- 了解工作空间项目列表：`auto-pm -w "<工作空间根>" project list`
- 获取项目元数据（JSON）：`auto-pm -w "<工作空间根>" project show <项目ID> --json`

### Step 1：确定模式

页面/组件 → 前端 | 业务/服务 → 后端 | 数据链路 → 联调 | diff/PR → 评审 | 运行时难复现 → 调试 | 小程序 → 小程序

### Step 2：给出方案

最少明确：改什么、为什么改、改动文件、潜在风险、如何验证。

**可用 auto-pm 命令**：
- 创建 Python 项目：`auto-pm -w "<工作空间根>" project create --stack python --id <ID> --name <NAME>`
- 创建变更请求：`auto-pm -w "<工作空间根>" change create --pid <ID> --domain <D> --nature <N> --scope <S> --applicant <A> --background <B> --necessity <N>`

### Step 3：实施

先读文件再改，尊重现有架构和命名风格，不在无关文件上扩散修改，变更后优先跑相关测试。

### Step 4：回写 PM_SESSION §6-§9

## 成功标准

- 用户不需要判断该找"前端技能"还是"调试技能"
- 下次会话能通过 PM_SESSION 直接恢复到本次执行状态
