---
spec_id: DEV-300
title: 高级语言与工业上位机系统 Google SRE 工程可靠性规范
number: 300
canonical_path: 00_Obsidian_Base全局规范文件仓库/04_驾驶舱与全栈域/300_高级语言与工业上位机系统_Google_SRE工程可靠性规范_DEV.md
version: V1.0.0
type_prefix: DEV
domain: cross-domain
sub_domain: 驾驶舱与全栈工程
lifecycle: stable
tags:
  - SRE
  - Google_SRE
  - 可靠性
  - 驾驶舱
  - 工业上位机
  - Python
  - C#
  - C++
  - TypeScript
  - 质量门禁
last_updated: 2026-08-23
author: Antigravity & auto-pm team
---

# DEV-300: 高级语言与工业上位机系统 Google SRE 工程可靠性规范

> **规范定位**：工作空间内所有高级语言开发项目（包括但不限于 Python 桌面驾驶舱、C# WPF 工业上位机、C++ 驱动/通信库、TypeScript/Web 组态监控前端）必须共同遵守的最高工程可靠性与质量审查准则。
> **核心哲学**：将可靠性视为软件工程问题，用代码、量化指标（SLO）与自动化门禁替代主观臆测与人工侥幸。

---

## 1. SRE 四大黄金信号 (Golden Signals) 与系统 SLO

所有工业上位机、辅助工具与后端服务，必须建立明确的 **服务等级目标 (Service Level Objectives, SLO)**，并由自动化测试与运行时探针持续度量：

### 1.1 延迟 (Latency) — 响应时间预算
- **CLI 命令响应**：任何交互式 CLI 指令冷启动并完成执行的时间必须 $\le 300\text{ms}$（超过 1 秒的操作必须输出进度条或 spinner 动画）。
- **GUI 交互流畅度**：上位机主界面（PySide6/QML 或 WPF）渲染必须保持 $\ge 60\text{fps}$，严禁在 UI 线程执行任何阻塞性 I/O（如 Modbus 轮询、文件遍历、大文档解析），耗时任务必须派发至后台工作线程池（如 `QRunnable` / `Task` / `std::jthread`）。
- **页面与弹窗切换**：界面切换与弹窗遮罩弹出延迟必须 $\le 100\text{ms}$，无闪烁与渲染撕裂。

### 1.2 吞吐 (Traffic) — 数据吞吐与密集处理能力
- **批量变量抽取 (ETL)**：逆向工程抽取 3,000+ 工业变量并完成标准化输出耗时 $\le 3.0\text{s}$。
- **并发通信扫描**：100 个寄存器区间的并发探测与活跃通道标识耗时 $\le 5.0\text{s}$。

### 1.3 错误率 (Errors) — 零不可控异常 SLO
- **运行时崩溃率 (Crash Rate)**：**0 致命崩溃 (0 Unhandled Exceptions)**。严禁出现 `NameError`、`AttributeError`、`UnboundLocalError`、`NullReferenceException` 或内存段错误（Segmentation Fault）。
- **静态检查违规率**：所有工程必须达成 **0 Lint 错误 (Clean Exit)** 与 **0 编译器/类型检查报错**。
- **异常静默吞噬率 (Silent Failures)**：**0 静默吞噬**。所有 `try-except` 或 `catch` 块严禁写出空的 `pass` 或仅打印空行，必须接入结构化日志记录堆栈（IEC 62443 可审计性）。

### 1.4 饱和度 (Saturation) — 资源防泄漏与环境纯净
- **内存与句柄**：长周期工业轮询（24h 压力测试）内存波动 $\le 5\%$，定时器与 Socket 句柄在断开时必须显式销毁（`deleteLater()` / `Dispose()` / `close()`）。
- **工作区纯净守卫 (DEV-TMP-001)**：自动化测试与构建运行产生的临时文件（`.coverage`, `tmp_*`, `__pycache__`）必须在退出时自销毁，禁止裸露扩散到代码根目录。

---

## 2. Google SRE 五大工程支柱

### 2.1 消除苦工 (Eliminating Toil)
- 任何需要人工重复操作 3 次以上的排查工作（如检查 QML 死链、检查 SCL 语法白名单、验证规范注册表一致性、清理游离日志），必须编写专用命令行工具或门禁脚本实现 **一键自动化**。
- 严禁将测试、查语法、验证按钮的工作转嫁给最终用户（Zero-Burden Law）。

### 2.2 全链路可观测性与现场诊断 (Observability & Error Mapping)
- **白盒日志记录**：后台服务与 Bridge 层在捕获异常时，必须使用 `logger.warning(..., exc_info=True)` 记录包含时间戳、线程号、异常类型与完整堆栈的结构化日志。
- **工业异常友好转译**：向操作工与电气工程师展示的报错，严禁直接抛出裸露的底层代码异常（如 `WinError 10061`、`NRE`），必须经过 `IndustrialErrorMapper` 统一转译为包含 **【故障原因】+【排障动作指引】** 的中文诊断文本。

### 2.3 故障隔离与优雅降级 (Fault Isolation & Graceful Degradation)
- 外部依赖（PLC 网线被拔掉、串口被占用、目标文件被锁定、JSON 损坏）属于工控现场的 **常态预期故障**，绝不允许演变为整个软件的闪退崩溃。
- 系统必须具备降级容错机制：
  - 通信断开 ➡️ 切换指示灯为红色，保持界面可操作，启动指数退避重连；
  - 模板或配置损坏 ➡️ 渲染红字警告降级页面，阻止破坏性写入。

### 2.4 事后剖析与源头消缺 (Postmortem & Root Cause Elimination)
- 任何在生产或测试中暴露的 Bug，不得仅做“就事论事”的代码修补。
- 必须遵循 **根治三步法**：
  1. 修复具体业务逻辑；
  2. 溯源脚手架生成器（Templates/Services）与检查门禁（Linters），从源头切断复发可能；
  3. 补充针对该缺陷模式的自动化回归单测。

### 2.5 架构整洁与边界隔离 (Clean Architecture & Boundary Protection)
- 严格遵循 Clean Architecture 5 层物理架构划分（`contracts` ➡️ `domain` ➡️ `infrastructure` ➡️ `application` ➡️ `ui`）。
- 表现层（UI / CLI / QML）只能依赖应用层门面（Facade）和契约（DTO/Commands），严禁越权直接穿透导入领域核心业务逻辑。

---

## 3. 多高级语言技术栈对齐矩阵

各语言技术栈在执行 DEV-300 审查时，底层对应的工具链与门禁命令映射如下：

| SRE 审查维度 | Python (auto-pm / 上位机) | C# / .NET (WPF / 组态) | C++ (实时驱动 / 通信) | TypeScript / Web (HMI组态) |
| :--- | :--- | :--- | :--- | :--- |
| **静态质量 (0 Lint)** | `ruff check --config pyproject.toml` | `dotnet build /p:TreatWarningsAsErrors=true` | `clang-tidy` + `cppcheck` | `npm run lint` (ESLint/Biome) |
| **类型安全 (0 Type Err)** | `mypy --ignore-missing-imports` | C# Roslyn 静态类型检查器 | C++ 编译器警告 `/W4` 或 `-Wall -Werror` | `tsc --noEmit --strict` |
| **自动化测试安全网** | `pytest tests/ -v` (100% 通过) | `dotnet test` (xUnit/NUnit) | `ctest` / `GoogleTest` | `npm test` (Vitest/Playwright) |
| **可观测性 (0 吞噬)** | `logging` + `IndustrialErrorMapper` | `Serilog` / `NLog` + 异常转译 | `spdlog` + MiniDump 崩溃捕获 | `Pino` + ErrorBoundary |
| **并发与多线程安全** | `QThreadPool` / `QRunnable` | `Task` / `Channel<T>` | `std::jthread` / 无锁队列 | Web Worker / Promise 异步流 |
| **环境纯净守卫** | `auto-pm doctor` (DEV-TMP-001) | `dotnet clean` + bin/obj 守卫 | CMake 独立 build 目录守卫 | node_modules / dist 隔离守卫 |

---

## 4. 驾驶舱与上位机自动化自审验收规程 (Self-Auditing Pipeline)

任何高级语言工程在向用户呈报或发布新版本前，必须按顺序执行并通过以下标准流水线：

```bash
# 1. 静态质量检查 (必须 0 告警，Clean Exit)
python -m ruff check --config pyproject.toml auto_pm

# 2. 类型安全检查 (必须 0 错误)
python -m mypy auto_pm --ignore-missing-imports

# 3. 自动化测试安全网回归 (必须 100% Pass)
python -m pytest tests/ -v --no-cov

# 4. 环境与工作空间纯净度诊断 (必须全部 PASS)
python -m auto_pm doctor
```

---

## 5. 版本演进与生效记录

| 版本号 | 生效日期 | 变更说明 | 责任人 |
| :--- | :--- | :--- | :--- |
| **V1.0.0** | 2026-08-23 | 首次正式发布，确立 Google SRE 作为跨高级语言与上位机基座的最高工程可靠性准则 | Antigravity & auto-pm team |
