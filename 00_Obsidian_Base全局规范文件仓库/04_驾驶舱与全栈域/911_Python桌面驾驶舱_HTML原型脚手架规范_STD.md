---
id: STD-911
name: Python桌面驾驶舱_HTML原型脚手架规范
version: 1.0.0
domain: 驾驶舱与全栈域
type: STD
status: active
author: Antigravity
created_at: 2026-08-17
updated_at: 2026-08-17
description: 规范 Python 桌面工具、上位机控制台与自动化管理工具的 HTML 交互原型标准、Glassmorphism 设计体系与前端-后端 Bridge 数据契约。
---

# 911 Python 桌面驾驶舱 HTML 原型脚手架规范 (STD-911)

## 1. 概述与适用场景

本规范定义了 **Python 桌面应用程序、PLC 上位机控制台、产线中控看板与自动化工具**（如 `SW-2026-008`、SCADA 上位机）的 HTML 交互原型设计规范。

### 1.1 适用范围
- Python 桌面 GUI 应用（PySide6 / PyQt6 / QML）
- 工业自动化 PLC 上位机（Modbus 监控、数据采集与配方管理系统）
- 项目管理驾驶舱与自动化分析平台

### 1.2 与 STD-910（工业触摸屏 HMI）的边界与协同
| 维度 | STD-910 工业触摸屏 HMI | STD-911 Python 桌面驾驶舱 |
| :--- | :--- | :--- |
| **典型载体** | 现场工业平板 / 触摸屏（西门子 Smart/Comfort） | 工程师 PC / 工控机上位机 / 监控中控台 |
| **视口机制** | 1280×800 固定分辨率，`fitToScreen` 等比居中缩放 | 100vw × 100vh 弹性全屏自适应（Flex / Grid） |
| **视觉风格** | 工控深灰蓝，粗大物理按钮与状态灯 | 暗色玻璃拟态（Glassmorphism）、环境光晕（Ambient Orb） |
| **底层映射** | `hmi_tag_mapping.json`（对齐 PLC SCL DB / Modbus 寄存器） | `app_bridge_mapping.json`（对齐 Python 槽函数 / 状态信号 / REST API） |

---

## 2. 脚手架目录规范

Python 项目的原型脚手架标准路径为：
```
<项目根目录>/02_规划/Html原型预览/
├── index.html                  # 驾驶舱主界面结构
├── styles.css                  # 视觉系统与 Design Tokens
├── script.js                   # 路由导航与 Mock 数据驱动逻辑
└── app_bridge_mapping.json     # Python/QML 桥接接口契约
```

---

## 3. 视觉与 Design Tokens 规范（对齐 Theme.qml）

原型必须采用与桌面 UI（如 PySide6 `Theme.qml`）1:1 对应的 CSS 变量系统：

```css
:root {
    /* 背景体系 */
    --bg-base: #020617;          /* 极深蓝黑底色 (Slate-950) */
    --surface: #0f172a;          /* 侧边栏与核心卡片底色 (Slate-900) */
    --surface-elevated: #1e293b; /* 浮动弹窗与悬停卡片 (Slate-800) */
    --surface-glass: rgba(15, 23, 42, 0.75);

    /* 品牌与强调色 */
    --primary: #6366f1;          /* Cyber Indigo 品牌主色 */
    --primary-glow: rgba(99, 102, 241, 0.35);
    --secondary: #38bdf8;        /* Sky Blue 辅助色 */
    --secondary-glow: rgba(56, 189, 248, 0.3);

    /* 状态语义色 */
    --success: #10b981;          /* 翡翠绿 (正常/就绪/通过) */
    --warning: #f59e0b;          /* 琥珀黄 (警告/审核中) */
    --error: #ef4444;            /* 珊瑚红 (错误/离线/报警) */

    /* 玻璃拟态边框与高光 */
    --glass-bg: rgba(255, 255, 255, 0.03);
    --glass-border: rgba(255, 255, 255, 0.08);
    --glass-highlight: rgba(255, 255, 255, 0.05);

    /* 文字色阶 */
    --text-primary: #f1f5f9;
    --text-secondary: #cbd5e1;
    --text-muted: #94a3b8;

    /* 字体体系 */
    --font-sans: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;

    /* 布局尺寸 */
    --sidebar-width: 280px;
    --header-height: 72px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
}
```

---

## 4. 经典“五区驾驶舱”布局体系

HTML 结构必须包含以下五个功能区：

1. **光晕背景层 (`.ambient-layer`)**：模拟 `AmbientOrb.qml`，包含 Indigo 与 Cyan 柔和径向渐变，赋予界面呼吸感；
2. **左侧导航栏 (`.sidebar`)**：
   - 顶部品牌 Logo 与应用版本（如 `auto-pm V1.1.0`）；
   - 工作空间/当前活跃项目切换下拉框；
   - 主功能视图切换菜单项（工作区 / 状态机看板 / 变更中心 / 规范中心 / Modbus 工具等）。
3. **顶部操作栏 (`.header`)**：
   - 当前页面标题与项目路径面包屑；
   - 全局搜索框；
   - 核心状态指示灯（环境就绪、门禁状态）与操作按钮（运行/刷新/导出）。
4. **主内容区 (`.main-content`)**：
   - 多视图容器（StackLayout 模式切换）；
   - 卡片网格（Card Grid）、状态机流转进度条（9 步节点）、数据表格与指标 KPI 徽标。
5. **控制台抽屉 (`.console-drawer`)**：
   - 底部/右侧折叠终端，模拟后端 Python 日志输出与 CLI 命令交互。

---

## 5. 前后端 Bridge 数据契约 (`app_bridge_mapping.json`)

每个 Python 驾驶舱原型必须配套 `app_bridge_mapping.json`，声明前端 QML/HTML 需要绑定的 Python 业务服务：

```json
{
  "project_id": "SW-2026-008",
  "project_name": "auto-pm 自动化项目管理工具",
  "bridges": {
    "workbenchBridge": {
      "signals": ["projectsChanged", "projectSelected"],
      "slots": ["listProjects", "getProjectById", "refreshProjects", "hasHmiPrototype", "openHmiPrototype"]
    },
    "changeBridge": {
      "signals": ["statusChanged"],
      "slots": ["getChangeRequest", "transitionChange", "listChanges"]
    },
    "modbusBridge": {
      "signals": ["dataReceived", "connectionChanged"],
      "slots": ["connectPlc", "readHoldingRegisters", "writeRegister"]
    }
  },
  "views": [
    {"id": "workspace", "title": "项目工作区", "icon": "ph-folder"},
    {"id": "platformDashboard", "title": "状态机看板", "icon": "ph-chart-pie-slice"},
    {"id": "changeCenter", "title": "变更中心", "icon": "ph-git-commit"},
    {"id": "specCenter", "title": "规范中心", "icon": "ph-book-open"},
    {"id": "modbusTool", "title": "Modbus 工具", "icon": "ph-cpu"}
  ]
}
```

---

## 6. CLI 工具链支持

```powershell
# 1. 一键初始化 Python 驾驶舱原型脚手架
python -m auto_pm prototype init --pid <项目编号> --template python-cockpit

# 2. 原型健康检查
python -m auto_pm prototype check --pid <项目编号>

# 3. 打包为单文件发布包
python -m auto_pm prototype bundle --pid <项目编号> --version V1.0.0
```
