---
name: fullstack-engineer
description: "统一全栈工程入口。适用于现有项目的前端、后端、接口、联调、评审、调试和小程序模式选择；会根据任务类型调用合适的平台技能或本地实现流程。"
---

# Fullstack Engineer

统一入口：前端 / 后端 / 全栈联调 / 代码评审 / 调试 / 小程序。避免在多个开发技能间切换。

> **架构定位**（CHG-SCPT-2026-140 / CHG-SCPT-2026-152 / CHG-SCPT-2026-156）：本技能为**纯执行者**。pm-workflow 是驾驶舱唯一入口和统筹者，负责 venv 激活、cockpit 上下文桥接、PM_SESSION 读取与回写、HTML 原型产出。本技能接收 pm-workflow 的 `skill_context` 后执行领域工作；若被用户独立触发，则只写临时交接包 `.auto-pm/handoffs/<request_id>.json` 或返回同结构 `handoff_result`，由 pm-workflow 统一收口。
>
> **通用规则单一真源**：以下规则统一在 [../shared/refs/skill_coordination.md](../shared/refs/skill_coordination.md) 中定义，本技能不重复维护：
> - Bug 诊断前置纪律（§1）
> - dogfooding 闭环质量门禁（§2）
> - 真源一致性前置校验（§3）
> - 门禁实测强制检查（§4）
> - 台账对账检查（§5）
> - 审查报告验证模式（§6）
> - retrofit 模式（§7）
> - 文件命名规范（§8）
> - 文件写入策略（§9）
> - PM_SESSION 双层结构归档规则（§10）

## 适用项目

- Python / Web / 前后端项目（已有代码库，非从零新建）
- 典型特征：`pyproject.toml`、`src/`、`tests/`、`ui/`、`main.py`

## 你负责什么

- 前端页面与交互、后端服务与接口、前后端联调与数据流、测试补齐与回归、代码评审、小程序分流

## 你不负责什么

- 需求/PRD/任务拆解/迭代推进 → `pm-workflow`
- PLC/SCL 编码与电气文档 → `plc-electrical-engineer`
- 从零创建新网站/Web App → `web-dev`
- venv 激活 / cockpit 上下文桥接 / PM_SESSION 读取与回写入口 → `pm-workflow`（本技能仅接收上下文并返回交接结果）

## 本地规范索引（必须遵循，输出前应读取确认版本）

- `00_Obsidian_Base全局规范文件仓库/00_INDEX_全局规范索引.md`
- `00_Obsidian_Base全局规范文件仓库/02_Python开发域/210_Python编程规范_DEV.md`
- `00_Obsidian_Base全局规范文件仓库/02_Python开发域/211_Python代码审查规范_DEV.md`
- `00_Obsidian_Base全局规范文件仓库/02_Python开发域/216_PySide6_GUI开发规范_DEV.md`
- `00_Obsidian_Base全局规范文件仓库/02_Python开发域/220_Python项目打包规范_DEV.md`
- `00_Obsidian_Base全局规范文件仓库/04_驾驶舱与全栈域/301_驾驶舱UI与交互规范_DEV.md`

## 项目连续性规则

### 开始前

1. **准备 Python 运行环境**（优先使用绝对/相对定位之 python，唤起 `python -m` 指令）：
   ```powershell
   # 推荐使用路径安全的 python 机制（即使移动 venv 也支持直接运行）
   python -m auto_pm doctor
   python --version; pip --version
   ```
   若 Python 解释器或环境失效，**立即报告用户**，说明 venv 缺失及影响（Python 工具/依赖不可用），不要跳过继续。

2. **接收上下文**：
   - 若从 pm-workflow 调用，从 prompt 中提取 skill_context（项目 ID、变更单、模式、pm_summary）
   - 若独立触发（无 pm-workflow），读取 PM_SESSION 走原有完整流程
   - **不再**直接读取 ai_context.json（入口统一由 pm-workflow 管理）

3. **接收原型**（若 pm-workflow 已产出）：
   - 检查 `PRD/原型/` 目录是否存在 HTML 原型文件
   - 若存在：读取原型作为 UI 实现参考
   - 若不存在：自行从 PRD/需求文档推导界面

4. 读取本轮相关代码、配置、测试、页面

### 结束后

必须输出结构化 `handoff_result` 给 `pm-workflow`，至少包含：
- `request_id`
- `executor_skill`
- `summary`
- `changed_files`
- `verification`（含 `lint_result` / `test_result` / `other_checks` / `not_run`）
- `risks`
- `next_actions`
- `watchouts`
- `read_first`
- `artifacts`
- `chg_updates`
- `product_impact`
- `pm_closure`

即使没改代码，也要返回分析了什么、结论、下次从哪里继续。**不得**直接回写 PM_SESSION；**不得**直接写 `.auto-pm/ai_feedback.json`；独立触发时也只能产出临时 handoff，不得把 handoff 视为第二套项目账本。

## 工具参考

| 工具 | 用途 |
|------|------|
| auto-pm（SW-2026-008） | 自动化项目管理工具，支持项目CRUD、PLC检查/修复、变更管理、模板管理、规范检查（吸收原 specmgr）、台账对账 |

**auto-pm 用法**：
```powershell
python -m auto_pm -w "<工作空间根>" project list|create|show|edit|retrofit|delete ...
python -m auto_pm -w "<工作空间根>" change create|list|show|transition ...
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

优先读取 `skill_context`；若为独立触发且无 `skill_context`，可读取 `PM_SESSION` 恢复上下文。若 PM_SESSION 不存在，停止，转 `pm-workflow`。

从 `skill_context` / PM_SESSION 恢复：当前阶段、最近执行结果、当前阻塞、最高优先级动作。

**可用 auto-pm 命令**：
- 了解工作空间项目列表：`python -m auto_pm -w "<工作空间根>" project list`
- 获取项目元数据（JSON）：`python -m auto_pm -w "<工作空间根>" project show <项目ID> --json`

### Step 1：确定模式

页面/组件 → 前端 | 业务/服务 → 后端 | 数据链路 → 联调 | diff/PR → 评审 | 运行时难复现 → 调试 | 小程序 → 小程序

### Step 2：给出方案

最少明确：改什么、为什么改、改动文件、潜在风险、如何验证。

**可用 auto-pm 命令**：
- 创建 Python 项目：`python -m auto_pm -w "<工作空间根>" project create --stack python --id <ID> --name <NAME>`
- 创建变更请求：`python -m auto_pm -w "<工作空间根>" change create --pid <ID> --domain <D> --nature <N> --scope <S> --applicant <A> --background <B> --necessity <N>`

### Step 3：实施

先读文件再改，尊重现有架构和命名风格，不在无关文件上扩散修改，变更后优先跑相关测试。

### Step 4：输出 `handoff_result`（含门禁实测前置检查）

对外声明门禁状态前（若本轮有代码改动），必须实际运行 `python -m ruff` / `python -m mypy` / `python -m pytest` 并记录真实输出，禁止基于推断声明门禁状态。详见 [../shared/refs/skill_coordination.md](../shared/refs/skill_coordination.md) §4 门禁实测强制检查。

将本轮实施摘要、改动文件、验证结果、风险、下一步整理为 `handoff_result` 返回给 `pm-workflow`，由 `pm-workflow` 统一回写 PM_SESSION 与 cockpit 反馈。

## 工程实践规范

以下规范为 fullstack-engineer **领域特定**内容（通用规则见 [../shared/refs/skill_coordination.md](../shared/refs/skill_coordination.md)）。

### GUI 测试基础设施规范

涉及 PySide6/Qt GUI 测试时，必须遵循：

1. **qapp fixture 单一定位原则**：
   - `qapp` fixture 只在 `tests/conftest.py` 定义一次（session 级）
   - **禁止**在子目录 conftest 或测试文件内重新定义 qapp
   - 若需 Qt 会话，直接 `def test_xxx(qapp):` 即可

2. **测试隔离规范**：
   - GUI 测试必须用 `tmp_path` 隔离，**禁止**在真实工作空间创建项目
   - 测试专用工作空间（如 DJ-2026-998）禁止再写入残留数据
   - 需清理测试残留时，autouse fixture 的 `except` 必须用 `logging.warning` 暴露失败，**禁止** `except Exception: pass` 静默吞错

3. **GUI 测试默认可见模式**：
   - 正常 GUI 测试**禁止**使用 offscreen 模式，必须使用可见窗口模式（`GUI_VISIBLE=1` 或不设置 `QT_QPA_PLATFORM=offscreen`）
   - 仅当用户特别要求时才使用 offscreen 模式（如 CI 无显示器环境、批量回归）
   - 理由：offscreen 模式无法验证真实字体渲染/DPI 缩放/多显示器场景，且会掩盖部分交互问题

4. **flaky test 诊断顺序**：
   - 先验证生产代码（如缓存同步、信号连接），再怀疑测试基础设施
   - 测试不稳定时，先确认是否为 fixture 污染（如 session 级状态残留），再怀疑 Qt 会话管理

5. **GUI 测试隔离检查清单**（编写/修改 GUI 测试前必查）：
   - □ 是否使用 tmp_path 隔离？（禁止在真实工作空间创建项目）
   - □ autouse fixture 的 except 是否用 logging.warning 暴露失败？（禁止 except Exception: pass）
   - □ 是否有 session 级状态残留？（检查 conftest.py 中 session 级 fixture 的清理逻辑）
   - □ 测试结束后是否清理了创建的项目/变更单？（检查 _cleanup_test_changes 是否被调用）
   - □ 是否在测试专用工作空间（如 DJ-2026-998）中残留了数据？（测试后检查并清理）

6. **全量回归卡住诊断流程**（全量 pytest 卡住时，进度停滞 >2 分钟）：
   1. 是否是 GUI 测试卡住？（检查是否最后执行的 tests/qml/ 或 tests/gui/）
   2. 是否是 session 级 fixture 污染？（检查 conftest.py session 级 fixture）
   3. 是否是 Qt 事件循环阻塞？（检查是否有 QEventLoop.exec() 或 QTest.qWait 未超时）
   4. 临时方案：分批执行 pytest（spec/change/app/core 一批 + qml 一批 + 其他一批）

### mypy 类型标注陷阱速查表

mypy 类型标注时易踩的坑，修改测试或生产代码前先查阅：

| 陷阱 | 说明 | 解决方案 |
|------|------|----------|
| Literal 窄化 | `assert model.editable is False` 将 bool 窄化为 `Literal[False]`，后续调用副作用方法（如 `set_editable(True)`）mypy 不追踪副作用，导致后续 `assert ... is True` 判定为 unreachable | 改用方法调用（如 `isEnabled()`）做断言，避免对 bool 属性做 Literal 窄化 |
| `bool()` 包装打破 narrowing | `if obj.attr:` 后 `obj.attr` 被 narrow 为非 None，但 `if bool(obj.attr):` 不触发 narrowing | 直接用 `if obj.attr:` 或 `assert obj.attr is not None` |
| Generator 返回类型 | Generator 函数需标注 `Generator[YieldType, SendType, ReturnType]` 或 `Iterator[YieldType]` | 缺少返回类型标注会报 `no-untyped-def` |
| Callable 逆变 | `Callable[[Any], None]` 的参数类型是逆变的，不能赋值给需要更具体参数类型的 Callable | 用 `Callable[[Any], None]` 或 `TYPE_CHECKING` 替代 |
| PySide6 枚举完整路径 | `Qt.UserRole` 在新版本 PySide6 中需写完整路径 `Qt.ItemDataRole.UserRole` | 使用完整枚举路径避免 attr-defined 错误 |
| `type:ignore` 评估 | 不是所有 `type:ignore` 都该保留 | 保留 PySide6 信号/槽限制导致的合理 ignore；修复可用 `cast`/`TYPE_CHECKING` 替代的 ignore；补精确错误码（如 `type:ignore[method-assign]`）|

### CLI 输出安全规范

涉及 rich/click CLI 输出时，必须遵循：

1. **rich markup escape 模式**：
   - CLI 输出含变量文本时，**禁止** `console.print(f"[yellow]{var}[/yellow]")`
   - `var` 中若含 `[xxx]` 会被 rich 当作未知 markup 标签吞噬
   - **必须**用 `console.print(escape(var), style="yellow")`：`escape()` 转义字面 `[`/`]`，`style=` 保留颜色

2. **Windows GBK 终端兼容**：
   - emoji 输出前用 `_supports_unicode_output()` 判断 `sys.stdout.encoding`
   - 不支持 unicode 时用 ASCII 替代字符（`[OK]`/`[FAIL]`/`[WARN]`/`[WRITE]`）
   - 不引入新依赖

3. **Rich Table 防截断**：
   - `expand=True` + `overflow="fold"` + `wide_console(width=200)` 避免长字段截断
   - 短列 `min_width` + `no_wrap`，标题列 `ratio=1` 吸收剩余空间

### 后台任务监控纪律

启动后台测试/构建任务后，**禁止**被动等待 system-reminder 通知：

1. 设置预期完成时间（全量回归 `--no-cov` 预期 3 分钟）
2. 用分段主动轮询（timeout=120s）
3. 超过预期时间未完成时立即读日志看进度百分比，进度停滞即停止并诊断根因
4. 给用户明确时间预期"预期 X 分钟，超时我会主动介入"

### 008 驾驶舱治理与工作区纯净度约束

1. **日志重定向严禁污染根目录**：
   - 调试/测试/诊断时，**严禁**直接将日志重定向到工作区根目录（如 `pytest > pytest_full_run.log` 或 `mypy > mypy_output.txt`）。
   - 所有测试输出或重定向必须指定到 `.auto-pm/logs/` 或 `.auto-pm/scratch/` 目录中。
   - 严禁在工作区根目录或项目根目录抛下 `.tmp_*.py` 散装测试脚本。

2. **清扫与自动自检**：
   - 测试或调试结束后，必须调用 `auto-pm clean`（自动清扫编译缓存与游离临时文件）。
   - 提交前运行 `auto-pm doctor`，确保工作空间纯净度检查通过。

## 成功标准

- 用户不需要判断该找"前端技能"还是"调试技能"
- 下次会话能通过 PM_SESSION 直接恢复到本次执行状态
