---
version: "V2.0.0"
status: "已批准"
created: "2026-06-21"
updated: "2026-08-22"
spec_id: "DEV-216"
domain: "Python开发"
title: "PySide6 + QML 工业上位机架构规范"
lifecycle: "active"
tags: ["PySide6", "QML", "上位机", "CleanArchitecture", "Bridge", "DTO"]
---

# PySide6 + QML 工业上位机架构规范

## 文档基础信息

| 项目 | 内容 |
|------|------|
| 文档名称 | PySide6 + QML 工业上位机架构规范 |
| 规范编号 | DEV-216 |
| 版本号 | V2.0.0 (QML 5层架构与异步线程模型全面升级) |
| 适用范围 | 所有使用 PySide6/QML 开发工业上位机与桌面驾驶舱的 Python 工程 |

---

## 1. 架构总览：5 层工业映射整洁分层

为实现 UI 交互与工控领域业务的彻底解耦，系统统一遵循 5 层架构：

```
┌─────────────────────────────────────────────────────────┐
│ 1. HMI 画面层 (QML Views & Components)                  │
│    auto_pm/ui/qml/views/ (主窗口、设置、检查、Modbus等)      │
└───────────────────────┬─────────────────────────────────┘
                        │ QML 通过 Signal/Slot 读写变量表
┌───────────────────────▼─────────────────────────────────┐
│ 2. HMI 变量桥接层 (PySide6 Bridges)                      │
│    auto_pm/ui/qml/bridges/*_bridge.py (@Slot & Signal)  │
└───────────────────────┬─────────────────────────────────┘
                        │ DTO 契约调用 (禁止裸 dict)
┌───────────────────────▼─────────────────────────────────┐
│ 3. FB 功能块应用门面 (Application Facades)               │
│    auto_pm/application/*_facade.py (用例编排与跨服务调度) │
└───────────────────────┬─────────────────────────────────┘
                        │ 纯同步 Service 调用
┌───────────────────────▼─────────────────────────────────┐
│ 4. SFB 核心服务层 (Core Services)                       │
│    auto_pm/domain/ 或 auto_pm/core/ (业务算法、解析、校验)│
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│ 5. DB/UDT 数据基础设施层 (SQLite & DTO Models)           │
│    auto_pm/infrastructure/db/ & auto_pm/models/         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 核心规约与开发模式

### 2.1 表现层：纯 QML 2.15 画面
- 视图统一存放在 `ui/qml/views/`，公共组件存放在 `ui/qml/components/`；
- 统一使用 `Theme.qml` 调色板与玻璃拟物微发光规范，严禁在 QML 视图中直接写死业务逻辑。

### 2.2 接口层：PySide6 Bridge 与 DTO 双源契约
- **Bridge 类命名**：`*Bridge`（如 `WorkbenchBridge`, `ChangeBridge`, `DeliveryBridge`）；
- **方法暴露**：仅使用 `@Slot(...)` 暴露给 QML；
- **数据回传**：统一使用 `@dataclass(frozen=True)` 定义不可变 DTO，Bridge 层使用 `dataclasses.asdict(dto)` 序列化提供给 QML，严禁跨层传递裸字典；
- **状态通知**：使用 `Signal` 触发 QML 属性变更与事件通知。

### 2.3 线程与异步模型 (QThreadPool + QRunnable)
- **绝对底线**：严禁在 UI 主线程执行任何文件 IO、网络通信、SQLite 查询或重度解析；
- **标准后台任务**：使用 `QThreadPool.globalInstance().start(WorkerRunnable)` 调度后台工作；
- **结果回传**：工作线程仅通过 Qt Signal 回到主线程更新 Bridge 属性，保证 UI 恒定 60 FPS 无卡顿。

### 2.4 文件系统防抖监听 (`FileWatcherBridge`)
- 外部 CLI 或编辑器直接修改磁盘文件时，必须通过 `QFileSystemWatcher` 结合 **1 秒防抖（Debounce）** 与后台线程比对，自动刷新 GUI 缓存。

### 2.5 高级渲染模式
- **结构化委托渲染**：对于 Markdown、日志等复杂文本，后端解析为 JSON 块，QML 使用 `ListView + Loader` 动态装配卡片组件；
- **零外部库依赖 PDF 导出**：导出文档直接使用 PySide6 内置的 `QTextDocument` 与 `QPrinter` 进行本地静默渲染，严禁引入重量级 `QtWebEngine` 或外部 GTK 包。

---

## 3. 反模式（严禁使用）

1. ❌ **严禁在 QML 体系中退化使用 QWidget 控件树**（如 `QVBoxLayout`, `QMainWindow`, `QSS`）；
2. ❌ **严禁跨层传递裸 `dict`**（必须有显式定义的 DTO 类）；
3. ❌ **严禁在 UI 线程执行阻塞式 IO**；
4. ❌ **严禁引入 `QtWebEngine`**（会导致客户端体积暴增 150MB+ 并破坏离线稳定性）。


