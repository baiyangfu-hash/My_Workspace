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

## 工程实践规范

以下规范基于实战经验沉淀，执行软件域任务时**必须遵循**。

### Bug 诊断前置纪律

测试失败或遇到 bug 时，**禁止**凭代码阅读直接下结论，必须按以下顺序执行：

1. **完整证据获取**：
   - 测试失败必须用 `--tb=long`（或至少 `--tb=short`）获取完整 traceback
   - **禁止**用 `--tb=no` 隐藏错误详情
   - 必须读取完整的 WARNING/ERROR 日志行，不可只看断言失败信息

2. **诊断脚本先行**：
   - 读代码形成的假设，**必须**用最小诊断脚本（`python -c "..."`）验证后才能下结论
   - 诊断脚本应直接调用被测函数，打印实际返回值
   - 禁止"读了代码 → 推测根因 → 直接输出修复计划"的跳跃

3. **测试问题 vs 生产问题分离**：
   - 测试失败时，**先检查 fixture 是否完整**（项目标志文件、路径结构、mock 配置）
   - 再怀疑生产代码
   - 特别警惕"假通过"：`if x is not None:` 类条件断言会掩盖 fixture 缺陷

4. **未验证禁止回写**：
   - 诊断结论未经运行时验证，**禁止**写入 PM_SESSION §8/§9
   - 必须标注"已验证"或"待验证"，未验证的结论只能放在 `open_questions`

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

### 文件写入策略（VS Code buffer staleness）

1. **读取时**：Edit/Write 工具可能返回缓存内容与磁盘不一致，诊断时用 Python `read_text()` 直接读磁盘确认真实状态

2. **写入时**：
   - **必须**用 Edit/Write 工具（通过 VS Code API 修改可正确同步缓冲区）
   - **禁止**用 Python 脚本直接写磁盘修改项目文件（`Path.write_text()` 绕过 VS Code 文件监听，导致编辑器缓冲区陈旧、用户保存时冲突）

3. **Edit 失败处理**：
   - 若 Edit 工具 `old_string` 不匹配（因缓存），先 Read 重新读取最新内容，再重试 Edit
   - 若仍失败用 Write 工具整体覆盖

4. **降级方案**：仅当 Edit/Write 工具均连续失败时，才可用 Python 脚本写入，但**必须立即提醒用户**"文件已被外部脚本修改，请关闭后重新打开"

### 后台任务监控纪律

启动后台测试/构建任务后，**禁止**被动等待 system-reminder 通知：

1. 设置预期完成时间（全量回归 `--no-cov` 预期 3 分钟）
2. 用分段主动轮询（timeout=120s）
3. 超过预期时间未完成时立即读日志看进度百分比，进度停滞即停止并诊断根因
4. 给用户明确时间预期"预期 X 分钟，超时我会主动介入"

### 架构模式

1. **DTO/adapter 分层**：
   - UI 层**禁止**直接访问 raw dict/Service 返回值，必须通过 DTO 整形后再渲染
   - 命名约定：`render_dto()`（避免与 `QWidget.render()` 冲突）
   - Service 层单一入口原则（如 `ChangeService.update_change_request` 统一入口）

2. **测试动态断言**：
   - **禁止**硬编码检查项数量（如 `assert count == 7`），改为基于真实结果动态断言
   - 检查项增减时 UI 测试无需机械同步

## 成功标准

- 用户不需要判断该找"前端技能"还是"调试技能"
- 下次会话能通过 PM_SESSION 直接恢复到本次执行状态
