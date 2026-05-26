# SW-2026-005 GUI 自适应分辨率与 DPI 方案（Plan）

## Summary

为 SW-2026-005 的 PyQt5 GUI 增加“跨分辨率自适应 + 高 DPI 兼容”的窗口策略，解决不同分辨率电脑下窗口过大/过小、控件挤压、内容不可见等问题。用户偏好为：

- 窗口尺寸：总是自适应屏幕（每次启动按当前屏幕可用区域设置，不依赖上次窗口大小）
- DPI：启用 Qt 高 DPI 适配（跟随系统缩放）

## Current State Analysis

### 入口与 DPI

- 入口文件为 [main.py](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/01_Project%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86/Python%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E6%80%BB%E5%BA%93/02_%E5%9C%A8%E7%A0%94%E9%A1%B9%E7%9B%AE/SW-2026-005_PLC%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86%E5%B7%A5%E5%85%B7/03_%E4%B8%BB%E7%A8%8B%E5%BA%8F/01_%E4%B8%BB%E7%A8%8B%E5%BA%8F%E6%A0%B8%E5%BF%83%E4%BB%A3%E7%A0%81/main.py)
- 目前 `QApplication` 创建前未设置任何高 DPI 属性；在高分屏/系统缩放场景下，可能出现字体/布局比例不一致或模糊。

### 主窗口尺寸与布局

- 主窗口 [main_window.py](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/01_Project%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86/Python%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E6%80%BB%E5%BA%93/02_%E5%9C%A8%E7%A0%94%E9%A1%B9%E7%9B%AE/SW-2026-005_PLC%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86%E5%B7%A5%E5%85%B7/03_%E4%B8%BB%E7%A8%8B%E5%BA%8F/01_%E4%B8%BB%E7%A8%8B%E5%BA%8F%E6%A0%B8%E5%BF%83%E4%BB%A3%E7%A0%81/src/ui/main_window.py)
  - `setMinimumSize(1400, 900)` 且 `resize(1500, 950)`；在 1366×768 等小屏会导致窗口无法完整显示或强制超出屏幕。
  - `QSplitter.setSizes([220, 1200])` 也是固定值，易在不同分辨率下比例不合理。
  - DockWidget 的最小尺寸（如 600×400、700×450）在小屏下会更容易挤压主体布局（尽管默认 hide，但用户打开后仍可能出现体验问题）。

### 页面内容可视性

- 仪表盘 [dashboard.py](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/01_Project%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86/Python%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E6%80%BB%E5%BA%93/02_%E5%9C%A8%E7%A0%94%E9%A1%B9%E7%9B%AE/SW-2026-005_PLC%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86%E5%B7%A5%E5%85%B7/03_%E4%B8%BB%E7%A8%8B%E5%BA%8F/01_%E4%B8%BB%E7%A8%8B%E5%BA%8F%E6%A0%B8%E5%BF%83%E4%BB%A3%E7%A0%81/src/ui/dashboard.py)
  - 页面整体不在 `QScrollArea` 内；当窗口高度不足时，底部内容可能不可见且无法滚动。

### SettingsManager 可复用点

- [settings.py](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/01_Project%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86/Python%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E6%80%BB%E5%BA%93/02_%E5%9C%A8%E7%A0%94%E9%A1%B9%E7%9B%AE/SW-2026-005_PLC%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86%E5%B7%A5%E5%85%B7/03_%E4%B8%BB%E7%A8%8B%E5%BA%8F/01_%E4%B8%BB%E7%A8%8B%E5%BA%8F%E6%A0%B8%E5%BF%83%E4%BB%A3%E7%A0%81/src/core/settings.py) 已包含 `window_geometry/window_state/sidebar_width` 等字段，但主窗口暂未使用。

## Proposed Changes

### Change 00：启用 Qt 高 DPI（入口层）

**修改文件**
- [main.py](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/01_Project%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86/Python%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E6%80%BB%E5%BA%93/02_%E5%9C%A8%E7%A0%94%E9%A1%B9%E7%9B%AE/SW-2026-005_PLC%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86%E5%B7%A5%E5%85%B7/03_%E4%B8%BB%E7%A8%8B%E5%BA%8F/01_%E4%B8%BB%E7%A8%8B%E5%BA%8F%E6%A0%B8%E5%BF%83%E4%BB%A3%E7%A0%81/main.py)

**做什么**
- 在创建 `QApplication` 之前设置：
  - `Qt.AA_EnableHighDpiScaling`
  - `Qt.AA_UseHighDpiPixmaps`
- 尝试设置 `QGuiApplication.setHighDpiScaleFactorRoundingPolicy(...)`（兼容性处理：不存在则跳过）。

**为什么**
- 让 Qt 按系统缩放因子正确计算像素与字体，减少 2K/4K/125%-200% 缩放下的布局异常。

### Change 01：主窗口“总是自适应屏幕”尺寸策略

**修改文件**
- [main_window.py](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/01_Project%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86/Python%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E6%80%BB%E5%BA%93/02_%E5%9C%A8%E7%A0%94%E9%A1%B9%E7%9B%AE/SW-2026-005_PLC%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86%E5%B7%A5%E5%85%B7/03_%E4%B8%BB%E7%A8%8B%E5%BA%8F/01_%E4%B8%BB%E7%A8%8B%E5%BA%8F%E6%A0%B8%E5%BF%83%E4%BB%A3%E7%A0%81/src/ui/main_window.py)

**做什么**
- 移除/降低硬编码 `MIN_WIDTH=1400、MIN_HEIGHT=900` 与固定 `resize(1500, 950)` 的依赖。
- 新增“按屏幕可用区域”计算初始尺寸的逻辑：
  - 使用 `QGuiApplication.primaryScreen().availableGeometry()`（或 `self.screen().availableGeometry()`）获取可用区域
  - 目标尺寸：例如 `0.92 * availableWidth/Height`，并设定最小下限（如 1024×720）与最大上限（不超过可用区域）
  - 居中显示（计算 x/y）
- 分割器尺寸改为按比例设置：
  - sidebar 初始宽度来自 `SettingsManager.get("sidebar_width")`，并按合理范围 clamp
  - right 面板宽度由剩余空间计算，不再固定 1200
- DockWidget 的最小尺寸改为更保守值（避免小屏打开后挤压主区域），并可根据屏幕尺寸动态调整。

**为什么**
- 解决小分辨率无法完整显示、不同屏幕比例显示不一致的问题。
- 用 `sidebar_width` 记忆左侧栏比例，不与“窗口总是自适应屏幕”的策略冲突。

### Change 02：窗口变化时同步 sidebar 宽度到设置（可选但推荐）

**修改文件**
- [main_window.py](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/01_Project%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86/Python%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E6%80%BB%E5%BA%93/02_%E5%9C%A8%E7%A0%94%E9%A1%B9%E7%9B%AE/SW-2026-005_PLC%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86%E5%B7%A5%E5%85%B7/03_%E4%B8%BB%E7%A8%8B%E5%BA%8F/01_%E4%B8%BB%E7%A8%8B%E5%BA%8F%E6%A0%B8%E5%BF%83%E4%BB%A3%E7%A0%81/src/ui/main_window.py)

**做什么**
- 监听 `QSplitter.splitterMoved`，把左侧面板实际宽度写入 `SettingsManager.set("sidebar_width", width)` 并在适当时机 `save()`。

**为什么**
- 即使窗口每次自适应屏幕，仍能保持用户习惯的导航栏宽度。

### Change 03：仪表盘页面加入整体滚动（提升小屏可用性）

**修改文件**
- [dashboard.py](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/01_Project%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86/Python%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE%E6%80%BB%E5%BA%93/02_%E5%9C%A8%E7%A0%94%E9%A1%B9%E7%9B%AE/SW-2026-005_PLC%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86%E5%B7%A5%E5%85%B7/03_%E4%B8%BB%E7%A8%8B%E5%BA%8F/01_%E4%B8%BB%E7%A8%8B%E5%BA%8F%E6%A0%B8%E5%BF%83%E4%BB%A3%E7%A0%81/src/ui/dashboard.py)

**做什么**
- 让 DashboardPage 的整体内容放入 `QScrollArea`，在高度不足时可滚动查看下方区域。
- 保持现有卡片/按钮布局不变，仅改变容器层级与 sizePolicy，避免影响业务逻辑。

**为什么**
- 小屏或窗口非最大化时，避免下方内容“消失且无法触达”的体验问题。

## Assumptions & Decisions

- 不引入新的第三方 UI 框架（继续使用 PyQt5 + 现有 QSS）。
- 不做“用户可配置缩放倍率”的额外功能；优先采用 Qt 原生高 DPI 支持。
- 窗口大小策略按用户选择：每次启动按屏幕可用区域自适应（不恢复上次窗口大小/停靠状态）。
- sidebar 宽度作为轻量偏好仍会保存（不与窗口策略冲突）。

## Verification

### 1) DPI 与启动验证
- 启动应用，确认无异常日志与崩溃
- 在不同系统缩放（100%/125%/150%）下观察：
  - 字体不出现明显糊/过小
  - 图标不明显失真（高 DPI pixmap 生效）

### 2) 分辨率验证（手动验收）
- 1366×768：窗口初始尺寸不超过屏幕，可完整看到主菜单/标签页；仪表盘可滚动查看下方区域
- 1920×1080：窗口初始尺寸接近屏幕（约 90%），布局比例正常
- 2K/4K + 150%：布局不挤压、文字与控件尺寸合理

### 3) 交互验证
- 拖动分割器调整左侧栏宽度，重启后保持左侧栏宽度偏好（仅 sidebar_width）
- 打开/隐藏 DockWidget 时不导致主区域不可用

