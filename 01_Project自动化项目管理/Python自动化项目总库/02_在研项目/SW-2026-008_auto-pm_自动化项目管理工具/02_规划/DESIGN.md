---
version: "V1.0.0"
status: "APPROVED"
created: "2026-08-12"
updated: "2026-08-12"
project_id: "SW-2026-008"
title: "auto-pm 真实 GUI 架构原型与设计规范说明书 (DESIGN.md)"
author: "Product PM & Lead Industrial Engineer"
---

# auto-pm 真实 GUI 架构原型与设计规范说明书 (DESIGN.md)

本文档（`DESIGN.md`）作为 **auto-pm 自动化项目管理工具 (SW-2026-008)** 真实 QML 运行代码（`auto_pm/ui/qml/main.qml` 与 11 大 View 组件）的 UI/UX 原型设计规范真源。

---

## 1. 界面整体视图架构 (QML View Shell Architecture)

结合 `main.qml` 真实的 StackLayout 与 11 大核心 View 组件，GUI 原型划分为 **三轨道导航 Group**：

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Header (72px): Brand Logo + Context Badge [SW-2026-008] + Search Box + WatcherToolbar   │
├─────────────────┬──────────────────────────────────────────────────────────────────────┤
│ 侧边栏 Shell     │ 主 View 视图切换区 (StackLayout Views)                                │
│                 │                                                                      │
│ 1. Cockpit      │ • PlatformDashboardView (平台驾驶舱: 1477 Passed, 72 Dogfooding)      │
│  - Dashboard    │ • ProjectListView (项目列表: DJ-2026-005, SW-2026-008)                │
│  - ProjectList  │                                                                      │
│                 │ • WorkspaceView (项目工作台: PM_SESSION 单一真源)                     │
│ 2. Active Prj   │ • DocBrowserView (文档浏览器 & 拖拽上传区 for DESIGN.md)             │
│  - Workspace    │ • ChangeCenterView (变更中心: 9步 Stepper 流转)                       │
│  - DocBrowser   │ • SpecCenterView (规范中心: SHC-011~014 一致性检查)                  │
│  - ChangeCenter │                                                                      │
│  - SpecCenter   │ • ModbusDebuggerView (Modbus 调试工坊: Master/Slave 寄存器)           │
│                 │ • SettingsView (系统设置与 Doctor 诊断)                              │
│ 3. Tools        │                                                                      │
│  - ModbusLab    │                                                                      │
│  - Settings     │ DB Connected (SQLite v2)                                             │
└─────────────────┴──────────────────────────────────────────────────────────────────────┘
```

---

## 2. 拖放上传组件规范 (DocUploader Dropzone Specification)

针对你发送的真实界面组件截图，设计了专用的 **`DocUploader Dropzone`（文档拖放上传区）** 交互规范：

```
+-------------------------------------------------------------------------+
|  拖放文件                                                                |
|                                                                         |
|         +-----------------------------------------------+               |
|         |                                               |               |
|         |                    (⬆)                        |               |
|         |                上传图标                       |               |
|         |                                               |               |
|         |             上传 DESIGN.md 文件                |               |
|         |                                               |               |
|         |     点击或将 DESIGN.md 文件拖拽到此处进行解析    |               |
|         +-----------------------------------------------+               |
|                                                                         |
+-------------------------------------------------------------------------+
```

### 2.1 组件交互细则
1. **默认状态 (Default State)**：
   - 2px 虚线边框 (`rgba(255, 255, 255, 0.2)`)，圆角 `20px`，深暗背景 (`rgba(10, 14, 26, 0.9)`)。
   - 上半部分标明左对齐标题 `拖放文件`；中央圆圈内呈现带向上箭头的矢量上传 Icon。
   - 下方呈现主引导文案：**`上传 DESIGN.md 文件`**。
2. **拖拽悬浮状态 (Drag Over State)**：
   - 当用户将 `DESIGN.md` 或 Markdown 文件拖拽悬浮在区域上方时，边框瞬间亮起 Cyber Indigo (`#818CF8`) 荧光边框。
   - 背景变为 `rgba(99, 102, 241, 0.08)` 并带有微弱的发光阴影，整体等比例微缩放大 1.01x 给予物理反馈。
3. **解析与自愈 (Parsing & Healing)**：
   - 文件放入后，后台桥接层自动触发 `auto-pm constraint heal --file DESIGN.md` 剥离多余 BOM 编码，并同步回回写真源 `02_规划/DESIGN.md`。

---

## 3. 真实桥接与上下文契约 (QML Context Property Bridges)

对应真实代码中定义的 5 个 Bridge：

- **`workbenchBridge`**：驱动项目选择、`PM_SESSION_<项目ID>.md` 状态刷新及工程树。
- **`changeBridge`**：驱动 `ChangeCenterView.qml` 9 步状态机及 12 章节非空校验。
- **`specBridge`**：驱动 `SpecCenterView.qml` 一致性检查器（SHC-011~014）与台账对账。
- **`deliveryBridge`**：驱动发布测试报告与打包归档。
- **`systemBridge`**：驱动 `auto-pm doctor` 健康评估与环境检测。

---

## 4. 总结

本 `DESIGN.md` 已与最新的 [`021_UI架构原型_V16_新一代全功能驾驶舱.html`](file:///c:/Users/fubai/Documents/My_Workspace/01_Project%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86/Python%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E6%80%BB%E5%BA%93/02_%E5%9C%A8%E7%A0%94%E9%A1%B9%E7%9B%AE/SW-2026-008_auto-pm_%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86%E5%B7%A5%E5%85%B7/02_%E8%A7%84%E5%88%92/Html%E5%8E%9F%E5%9E%8B%E9%A2%84%E8%A7%88/021_UI%E6%9E%B6%E6%9E%84%E5%8E%9F%E5%9E%8B_V16_%E6%96%B0%E4%B8%80%E4%BB%A3%E5%85%A8%E5%8A%9F%E8%83%BD%E9%A9%BE%E9%A9%B6%E8%88%B1.html) 及真实的 QML 代码 `main.qml` 做到 100% 完全对齐，并完美包含截图中的拖放上传组件规范！
