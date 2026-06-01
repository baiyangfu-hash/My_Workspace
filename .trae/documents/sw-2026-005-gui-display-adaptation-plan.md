# SW-2026-005 GUI显示排版诊断与固定目标机适配计划

## 1. 摘要

- 目标项目: `c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-005_PLC项目管理工具`
- 目标问题: GUI 显示排版不合理，需要先完成诊断，再针对用户当前固定目标机做定向适配。
- 目标显示环境: 固定目标机，主显示器上限分辨率为 `2880x1800`。不以通用多机兼容为第一优先级。
- 执行目标: 让 glm5.1 基于当前代码完成“诊断 -> 抽象 UI 尺寸策略 -> 改造主窗口/关键页面/关键对话框 -> 验证截图与回归”的一轮闭环。
- 成功标准:
  - 启动后主窗口在目标机上不出现明显拥挤、过疏、截断、空白浪费或比例失衡。
  - 左侧栏、顶部 Tab、仪表盘卡片、Dock 面板、设置对话框在目标机上形成统一视觉比例。
  - 不仅打开高 DPI 开关，还要把硬编码像素尺寸收敛到统一策略。
  - 至少保留 1 组自动化验证和 1 组人工截图验证证据。

## 2. 当前状态分析

### 2.1 已确认的技术事实

- GUI 技术栈为 `PyQt5`，入口文件为:
  - `03_主程序/01_主程序核心代码/main.py`
  - `03_主程序/01_主程序核心代码/src/ui/main_window.py`
- 当前已经做了基础高 DPI 开关:
  - `main.py` 中启用了 `Qt.AA_EnableHighDpiScaling`
  - `main.py` 中启用了 `Qt.AA_UseHighDpiPixmaps`
  - `main.py` 中尝试设置 `HighDpiScaleFactorRoundingPolicy.PassThrough`
- 当前主窗口已根据屏幕可用区域做了初始几何计算:
  - `main_window.py::_apply_initial_geometry()`
  - 逻辑为取 `screen.availableGeometry()` 的 `92%`

### 2.2 诊断结论

- 当前问题不是“完全没有 DPI 支持”，而是“只有启动级 DPI 开关，没有组件级比例体系”。
- 多个关键页面仍使用硬编码像素，且这些像素值彼此无统一来源，导致在高分辨率或高缩放环境下容易出现比例不协调。
- 目前缺少对目标机运行时显示参数的显式采样与日志记录，后续很难复盘“为什么在你的机器上排版不合理”。
- 当前没有单独的“UI 尺寸/密度配置层”，窗口、面板、按钮、卡片、Dock、对话框各自写死，后续维护成本高。

### 2.3 已定位的高风险硬编码点

#### 启动与主窗口

- `03_主程序/01_主程序核心代码/main.py`
  - 全局字体直接固定为 `StyleBuilder._resolve_chinese_font(10)`
- `03_主程序/01_主程序核心代码/src/ui/main_window.py`
  - `MIN_WIDTH = 1200`
  - `MIN_HEIGHT = 800`
  - `SIDEBAR_DEFAULT_WIDTH = 240`
  - `SIDEBAR_MIN_WIDTH = 180`
  - `SIDEBAR_MAX_WIDTH = 320`
  - 中央布局边距/间距固定为 `8`
  - 右侧区域默认剩余宽度最少固定 `800`

#### 仪表盘

- `03_主程序/01_主程序核心代码/src/ui/dashboard.py`
  - `StatCard` 高度固定 `80~100`
  - 多处 `16 / 12 / 8 / 6 / 150 / 20` 固定像素
  - 标题字号固定 `18`
  - 分区标题字号固定 `12`
  - 最近项目区域最大高度固定 `150`
  - 健康度区域使用横向硬排布，目标机上可能过宽或比例失衡

#### 右侧主面板与引导页

- `03_主程序/01_主程序核心代码/src/ui/builders/right_panel_builder.py`
  - 项目详情页边距固定 `12`
  - 描述框最大高度固定 `200`
  - 规范检查引导页边距固定 `40`
  - 引导按钮固定高度 `40`
  - 多个字号以 QSS/内联样式直接固定为 `16pt / 11pt / 10pt`

#### 左侧栏

- `03_主程序/01_主程序核心代码/src/ui/builders/left_panel_builder.py`
  - `QToolBox` 固定最小/最大宽度 `180~320`
  - 页面边距固定 `8`
  - 间距固定 `6`
- 这些值在 `2880x1800` 目标机上大概率偏保守，容易显得偏窄或信息密度失衡。

#### Dock 面板

- `03_主程序/01_主程序核心代码/src/ui/builders/dock_panel_builder.py`
  - 诊断与规范检查 Dock 高度固定 `200~400`
- 在目标机上如果垂直空间富余，当前 Dock 可能显得偏矮，信息区拥挤。

#### 设置对话框

- `03_主程序/01_主程序核心代码/src/ui/dialogs/settings_dialog.py`
  - 对话框固定最小尺寸 `550x420`，初始尺寸 `600x450`
  - 底部按钮固定宽度 `70/80`
  - 多处按钮字体固定 `10pt`
- 当前没有显示相关配置项，无法手工微调排版密度。

### 2.4 当前测试状态

- 已存在 GUI 导航相关测试:
  - `03_主程序/01_主程序核心代码/tests/test_gui_navigation.py`
- 现有 GUI 测试重点是导航映射，不覆盖视觉比例、尺寸策略、目标机显示效果。
- 项目文档 `PM_SESSION_SW-2026-005.md` 与 `01_项目文档/03_执行过程/01_测试报告/GUI业务逻辑与功能域详细文档_V1.0.md` 没有提供“按固定目标显示器适配”的现成方案。

## 3. 方案决策

### 3.1 已锁定决策

- 适配策略选择: 固定目标机优先，不先做多屏和全分辨率泛化优化。
- 诊断方式: 先补足运行时显示参数采样，再根据目标机实测值调整 UI。
- 改造方式: 不零散手改单点像素，而是引入统一 UI 尺寸策略层，再批量替换关键页面。
- 验收方式: 自动化回归 + 目标机人工截图对比双轨执行。

### 3.2 关键假设

- 用户机器上 Windows 缩放比例未提前提供，因此执行阶段必须在程序启动时主动采集:
  - 屏幕分辨率
  - `availableGeometry`
  - 逻辑 DPI
  - 设备像素比
- 本轮仅要求适配当前用户主力显示器，不要求完美覆盖 1080P / 2K / 4K 多档。
- 本轮优先解决主窗口、仪表盘、左侧栏、Dock、设置对话框等最可见区域；更深层子面板若受影响，再按诊断结果追加。

## 4. 拟修改内容

### 4.1 新增统一显示适配层

- 建议新增文件:
  - `03_主程序/01_主程序核心代码/src/ui/ui_scale.py`
- 目的:
  - 统一封装显示信息采样、尺寸缩放、字号分级、间距分级、推荐窗口尺寸。
- 建议提供的能力:
  - `collect_screen_metrics(window_or_screen) -> dict`
  - `build_ui_scale_profile(metrics) -> profile`
  - `scale_px(value: int) -> int`
  - `font_pt(value: int) -> int`
  - 语义化尺寸常量，如:
    - `spacing_xs/sm/md/lg/xl`
    - `sidebar_min/default/max`
    - `dock_min/max`
    - `dialog_w/dialog_h`
    - `card_min_h/card_max_h`
- 设计要求:
  - 输入基于目标机实测屏幕参数
  - 输出基于语义尺寸，不再让业务页面直接写魔法数字

### 4.2 调整应用入口与主窗口

- 修改文件:
  - `03_主程序/01_主程序核心代码/main.py`
  - `03_主程序/01_主程序核心代码/src/ui/main_window.py`
- 修改目标:
  - 在创建 `QApplication` 后记录目标机显示指标日志
  - 主窗口初始化时加载统一 `ui_scale` 配置
  - 用统一策略替换以下硬编码:
    - 全局字体大小
    - 最小窗口尺寸
    - 初始窗口尺寸比例
    - splitter 左侧默认宽度与上下限
    - central layout 边距与间距
    - 右侧区域最小宽度
- 建议实现:
  - 在 `MainWindow` 内新增 `_ui_scale` 或 `_ui_profile`
  - `_apply_initial_geometry()` 改为“基于目标机 profile 计算”
  - `_build_central_widget()` 与 `_build_right_panel()` 改用 profile 值

### 4.3 仪表盘做重点适配

- 修改文件:
  - `03_主程序/01_主程序核心代码/src/ui/dashboard.py`
- 修改目标:
  - 统一卡片高度、内边距、标题字号、区块间距
  - 避免在目标机上出现“卡片太矮、文字偏小、留白碎裂”的问题
  - 让最近项目区与健康度区在大屏上更均衡
- 建议实现:
  - `DashboardPage` 和 `StatCard` 接收 scale/profile 参数
  - 把固定值 `80/100/16/12/8/6/150/20/18/12` 替换为语义化尺寸
  - 评估把健康度卡片区从固定横排改为:
    - 宽度足够时 5 列横排
    - 宽度不足时自动换行为 3+2 或 2 列网格
- 说明:
  - 即使本轮目标机较宽，也建议把健康度区改成可降级布局，避免未来再次返工

### 4.4 右侧主面板与引导页适配

- 修改文件:
  - `03_主程序/01_主程序核心代码/src/ui/builders/right_panel_builder.py`
- 修改目标:
  - 统一页面边距、标题字号、描述框高度、按钮高度
  - 让规范检查引导页在目标机上更自然，不出现元素偏小或上下过空
- 建议实现:
  - 项目详情页 `12` 边距改为 profile
  - 项目描述框最大高度 `200` 改为 profile
  - 引导页 `40` 边距、按钮高度 `40`、各处 `pt` 字号改为 profile
  - 尽量减少内联样式中的固定字号，统一从 `ui_scale` 输出

### 4.5 左侧栏与 Dock 适配

- 修改文件:
  - `03_主程序/01_主程序核心代码/src/ui/builders/left_panel_builder.py`
  - `03_主程序/01_主程序核心代码/src/ui/builders/dock_panel_builder.py`
- 修改目标:
  - 左侧栏宽度与按钮密度更匹配目标机
  - Dock 高度在目标机上不拥挤
- 建议实现:
  - 侧栏宽度从固定 `180~320` 调整为 profile 控制
  - 页面边距/间距使用统一 spacing
  - Dock `200~400` 高度调整为 profile 控制，必要时提高默认高度上限

### 4.6 设置对话框补充显示相关入口

- 修改文件:
  - `03_主程序/01_主程序核心代码/src/ui/dialogs/settings_dialog.py`
  - `03_主程序/01_主程序核心代码/src/core/settings.py`
- 修改目标:
  - 即便本轮以固定目标机为主，也保留最少量的显示调优入口，避免未来必须改代码才能微调。
- 建议最小新增项:
  - `ui_density` 或 `ui_scale_override`
  - 是否启用“目标机优化模式”标记
- 约束:
  - 不做复杂通用配置面板，避免把本轮需求扩展成产品级设置系统
  - 设置对话框自身也要套用新的尺寸策略

### 4.7 样式层收敛

- 修改文件:
  - `03_主程序/01_主程序核心代码/src/ui/builders/style_builder.py`
  - 如有必要同步检查 `resources/styles/material_light.qss`
  - 如有必要同步检查 `resources/styles/material_dark.qss`
- 修改目标:
  - 减少 Python 内联样式和 QSS 固定字号冲突
  - 保证字体大小和关键 padding 的来源尽量一致
- 注意:
  - 若 QSS 中也存在大量固定值，glm5.1 应优先梳理“哪些必须留在 QSS，哪些应由 Python 注入”

### 4.8 增补验证

- 建议新增或扩展测试文件:
  - 新增 `03_主程序/01_主程序核心代码/tests/test_ui_scale.py`
  - 视实现情况补充 `03_主程序/01_主程序核心代码/tests/test_gui_navigation.py`
- 自动化验证重点:
  - `ui_scale` 对目标机屏幕指标的计算输出是否稳定
  - `MainWindow` 初始尺寸、侧栏宽度、Dock 高度是否落入预期区间
  - `DashboardPage` 关键控件尺寸是否来自 profile，而不是散落的魔法数字

## 5. glm5.1 执行步骤

### 阶段 A: 运行时诊断与基线采样

1. 启动当前 GUI，记录目标机的:
   - 主屏幕分辨率
   - 可用区域
   - 缩放比
   - 逻辑 DPI
   - DPR
2. 对以下界面留截图:
   - 主窗口首页
   - 左侧栏 + 顶部 Tab
   - 仪表盘
   - 规范检查引导页
   - 底部 Dock
   - 设置对话框
3. 输出问题清单，按以下标签分类:
   - 太小
   - 太密
   - 太空
   - 截断
   - 比例失衡

### 阶段 B: 引入统一尺寸策略

1. 新增 `ui_scale.py`
2. 在 `main.py` / `main_window.py` 接入 profile
3. 保证窗口、字体、边距、sidebar、dock 先跑通

### 阶段 C: 关键界面改造

1. 先改 `dashboard.py`
2. 再改 `right_panel_builder.py`
3. 再改 `left_panel_builder.py`
4. 再改 `dock_panel_builder.py`
5. 最后改 `settings_dialog.py`

### 阶段 D: 样式收口

1. 盘点 QSS 与 Python 内联样式冲突点
2. 优先清理固定字号和固定高度
3. 保证 light/dark 至少不因本次改动失真

### 阶段 E: 验证与交付

1. 运行相关测试
2. 补充新测试
3. 在目标机再次截图
4. 输出“改造前/改造后”对比结论

## 6. 验证步骤

### 6.1 自动化验证

- 建议执行:
  - `tests/test_gui_navigation.py`
  - 新增的 `tests/test_ui_scale.py`
  - 与本轮改动直接相关的 GUI/widget 测试
- 验证点:
  - 主窗口初始化不报错
  - splitter 尺寸设置合法
  - Dock 可正常创建
  - 仪表盘控件不会因为尺寸调整失去可见性

### 6.2 人工验证

- 在目标机上验证以下页面:
  - 启动首页
  - 仪表盘卡片区
  - 最近项目区
  - 健康度区
  - 项目详情页
  - 规范检查引导页
  - 设置对话框
  - 底部诊断 Dock / 规范检查 Dock
- 验收标准:
  - 无控件文字裁切
  - 无主要按钮过小难点
  - 页面不显得“局部很挤、局部很空”
  - 左右区比例协调
  - Dock 高度足以承载内容预览

### 6.3 诊断证据要求

- 必须保留:
  - 目标机显示参数日志
  - 改造前截图
  - 改造后截图
  - 自动化测试结果

## 7. 风险与边界

- 风险 1: 仅知道分辨率上限 `2880x1800`，未知 Windows 缩放比例，因此必须依赖运行时采样，不能只靠静态猜测。
- 风险 2: 某些子面板可能在本轮改造后暴露新的比例问题，尤其是 `AutoFixPanel`、`ExcelExportPanel`、`DiagnosticPanel`、`SpecCheckPanel`。
- 风险 3: Python 内联样式与 QSS 共存，若只改一边，可能出现主题切换后的尺寸不一致。
- 边界 1: 本轮不要求实现完整多屏自适应系统。
- 边界 2: 本轮不要求把所有历史 GUI 页面全部做成响应式布局。
- 边界 3: 本轮聚焦“当前目标机体验可用且协调”，不是“视觉重设计”。

## 8. 给 glm5.1 的执行提示

- 不要只改 `main.py` 的 DPI 开关；当前核心问题是大量硬编码尺寸缺少统一比例层。
- 不要分散地逐文件随意放大字号；优先建立 `ui_scale` 统一入口。
- 第一优先级文件顺序:
  - `src/ui/main_window.py`
  - `src/ui/dashboard.py`
  - `src/ui/builders/right_panel_builder.py`
  - `src/ui/builders/left_panel_builder.py`
  - `src/ui/builders/dock_panel_builder.py`
  - `src/ui/dialogs/settings_dialog.py`
  - `src/core/settings.py`
  - `src/ui/builders/style_builder.py`
- 完成后必须在目标机上重新采样并截图，否则无法证明“已按你的显示器适配”。
