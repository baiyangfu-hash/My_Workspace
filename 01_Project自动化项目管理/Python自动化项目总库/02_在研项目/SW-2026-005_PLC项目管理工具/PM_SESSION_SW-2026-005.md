# PM_SESSION_SW-2026-005

## 0. Meta
- project_id: SW-2026-005
- project_name: PLC项目管理工具
- project_root: c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-005_PLC项目管理工具
- last_updated: 2026-06-01 (文档全面更新: ARCH-V4.0.0+INT-V4.0.0+DES-V3.0.0+DEV-V3.0.0+版本台帐+RELEASE_NOTES+PRD+立项表+4个README)
- owners: Trae

## 1. Positioning（项目定位）
- one_liner: Trae伴生式 PLC 工作空间治理工具 — 聚焦工作空间挂载、共享库治理、规范检查与文档汇总
- users: PLC 工程师、项目管理者、需要跨项目治理的自动化开发者
- non_goals: 不替代 Trae 作为主编辑器；不做实时 PLC 通信；不在当前主线实现语言服务器/TIA网关

### 1.1 MVP V2.0 范围重定义（2026-05-22）

**核心功能（必须可用）**:
- ✅ 项目管理: 新建/打开/关闭项目、项目树浏览、项目元数据管理
- ✅ 文档生成: 10种模板一键生成、变量替换、文档CRUD、另存为
- ✅ 变更管理: 版本检查(sync)、CHG/IFC文档生成、同步报告（已集成GUI）
- ✅ 变更管理UI: 变更单列表/创建/审核/状态流转面板（V2.2新增）
- ✅ 规范检查: 6种检查器(命名/语法/注释/配置/定时器/变量)
- ✅ 诊断分析: 七维度健康度评估、LSP兼容性检查

**降级为占位符（V2.0不实现）**:
- ⏸ HMI变量映射: 保留Tab占位，显示"开发中"提示
- ⏸ IO分配表: 保留Tab占位，显示"开发中"提示
- ⏸ 测试运行器: 不创建Dock，V2.1+规划
- ⏸ ST编辑器增强: 保留基础编辑，不实现代码片段/高级高亮

**明确排除**:
- ❌ Git版本控制集成
- ❌ 多人协作/云端同步
- ❌ PLC在线连接/下载程序

## 2. Current Focus（当前焦点）
- current_focus: V4.2 功能对接完成 — 前端全量对接后端服务, IPCBridge 38个API端点, Mock默认关闭, 等待V4.3打包发布
- milestone: Phase 0-5 ✅ → V3.1 ✅ → V3.2 ✅ → V4.0 PyWebView ✅ → V4.1 IPC集成 ✅ → V4.1.1 BUG修复 ✅ → **V4.2 功能对接 ✅** → V4.3 打包发布
- acceptance: 所有按钮已绑定后端API | Mock默认关闭 | 仪表盘动态数据 | 项目CRUD闭环 | 变更管理闭环 | 设置保存/重置 | 自动修复/Excel导出视图 | 窗口控制按钮

### 2.1 未来迭代方向（储备方向，非当前工作）
- 📌 SCL语言服务器规划保留为储备方向，详见:
  - PRD §6.5 V3.0+未来展望
  - `01_项目文档/02_规划过程/012_V3.0开发规划_DEV-PLAN-V3.0.0.md`
- 📌 方向: Python核心语言服务 + C# TIA Portal网关(可选)
- 📌 路线: V3.0(SCL解析器) → V3.1(LSP服务器) → V3.2(项目作用域) → V4.0(TIA网关)
- ⚠️ 该方向不属于当前“工作空间支持”开发输入
- 📌 当前主线优先级: 先补齐 Workspace 模型和工作空间加载，再考虑语言服务等增强方向

## 3. Status Summary（当前状态摘要）
- in_progress:
  - V4.2 功能对接完成, 等待V4.3打包发布
  - GUI: PyWebView(Chromium)前端全量对接后端服务
  - 后端: IPCBridge 38个API端点就绪(Mock模式默认关闭)
- next_up:
  - V4.3 打包: PyInstaller --onefile 单exe发布
  - HTML模块化拆分: 当前单文件需拆分为多模块
  - 前端单元测试: HTML/JS交互逻辑自动化测试覆盖
- open_questions:
  - PyQt5回退路径: main_window.py的V3.2修改是否需要回退?
  - 打包体积优化: webview+Chromium Runtime预估60-85MB
  - HTML单文件维护性: index.html已超2100行, 需拆分模块化
- risks_dependencies:
  - pywebview安装在lib/目录(非全局), PyInstaller需--add-data lib
  - WebView2 Runtime依赖: Win10 1803+自带, Win7需单独安装
  - 前端无单元测试: HTML/JS交互逻辑缺乏自动化测试覆盖

## 4. Artifacts Index（文档索引）
- prd:
  - 00_项目基础信息/001_产品需求文档_PRD-V2.1.0.md (含§6.5 V3.0+未来展望)
- design:
  - 01_项目文档/02_规划过程/013_UI重设计规范_V3.1-DESIGN.md (UI视觉焕新+布局重组+7视图优化, 2026-06-01新增)
- plan:
  - 01_项目文档/02_规划过程/006_总计划与里程碑_PLAN-V2.0.0.md
- dev_plan:
  - 01_项目文档/02_规划过程/011_工作空间支持开发规划_DEV-PLAN-V1.0.0.md (当前主线直接开发入口)
- arch:
  - 01_项目文档/02_规划过程/007_架构设计文档_ARCH-V4.0.0.md (PyWebView架构+IPCBridge, 2026-06-01更新)
- des:
  - 01_项目文档/02_规划过程/008_详细设计文档_DES-V3.0.0.md (工作空间+IPCBridge设计, 2026-06-01更新)
- dev:
  - 01_项目文档/02_规划过程/010_代码结构说明_DEV-V3.0.0.md (12层架构+PyWebView文件, 2026-06-01更新)
- reserve:
  - 01_项目文档/02_规划过程/012_V3.0开发规划_DEV-PLAN-V3.0.0.md (未来研究/储备方向，不属于当前开发输入)
- api:
  - 01_项目文档/02_规划过程/009_API接口文档_INT-V4.0.0.md (Service接口+IPCBridge 38 API端点, 2026-06-01更新)
- src:
  - 03_主程序/01_主程序核心代码/src/
- v31_new:
  - src/checkers/fb_interface_checker.py (FB接口一致性检查, 6规则)
  - src/parsers/fb_call_parser.py (OB1调用语句解析)
  - src/parsers/fb_signature_builder.py (FB签名构建)
  - src/services/auto_fix_service.py (自动修复服务层)
  - src/fixers/comment_punctuation_fixer.py (中文标点修复)
  - src/fixers/naming_fixer.py (命名建议修复)
  - src/exporters/excel_exporter.py (Excel 9列导出)
  - src/exporters/fb_interface_template.py (FB接口数据模型)
  - src/scanners/syslib_scanner.py (SysLib扫描+全局索引)
  - src/ui/widgets/auto_fix_panel.py (🔧 自动修复面板)
  - src/ui/widgets/excel_export_panel.py (📊 Excel导出面板)
- test:
  - 03_主程序/01_主程序核心代码/tests/
- um:
  - 01_项目文档/03_执行过程/05_用户手册/012_用户操作手册_UM-V2.1.0.md
- release:
  - 01_项目文档/03_执行过程/04_发布说明/RELEASE_NOTES.md
- change_mgmt:
  - 01_项目文档/03_执行过程/02_变更管理/变更列表.md
  - 01_项目文档/03_执行过程/02_变更管理/版本变更台帐.md
- defect:
  - 01_项目文档/03_执行过程/01_测试报告/缺陷跟踪表.md
- test_plan:
  - 01_项目文档/03_执行过程/01_测试报告/测试计划.md

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-06-01 文档全面更新: ARCH-V3→V4.0.0(PyWebView架构+IPCBridge)+INT-V3→V4.0.0(38 API端点)+DES-V2→V3.0.0(IPCBridge设计+双模式入口)+DEV-V2→V3.0.0(12层架构)+版本台帐V3.0-V4.2+RELEASE_NOTES V3.0-V4.2+PRD V4.0.0+立项表V1.3.0+4个README索引 | 影响: 全部项目文档 | ✅已完成
  - 2026-05-28 未来迭代方向规划: 完成SCL语言服务器可行性分析(Python核心+C#可选网关)，更新PRD§6.5+ARCH§8+创建DEV-PLAN-V3.0.0作为未来迭代方向文档。⚠️这是未来方向，当前工作仍为V2.5缺陷修复→V3.0-RC发布候选 | 影响: PRD+ARCH+DEV-PLAN+PM_SESSION | ✅已完成
  - 2026-05-27 V2.4 EventBus信号治理: 修复2个断路信号(spec_check_request→_show_spec_check_dock, variable_check_request→导航PLC工具Tab+状态栏提示); 清理6个死信号(project_selected/document_saved/document_created/st_file_open_request/fb_doc_generate_request+规范事件分类); 删除Application死代码(app.py); menu_manager移除冗余QMessageBox | 影响: event_bus.py+main_window.py+menu_manager.py+删除app.py | ✅已完成
  - 2026-05-23 全方位PM审查: 输出开发进度+方案目标差距+问题点风险+V2.3→V3.0路线图 | 影响: 项目管理 | ✅已完成
  - 2026-05-23 V2.2变更: P0缺陷修复(main.py启动+ANALYZING死胡同)+变更管理UI面板+CHG/IFC异步生成+sync测试覆盖+技术债清理 | 影响: 8文件修改+4文件新增 | ✅已完成
  - 2026-05-22 范围重定义: 聚焦项目管理+文档生成+变更管理，HMI/IO/测试运行器降级为占位符 | 影响: 全局 | 已完成
  - 2026-05-22 Phase 3完成: HMI/IO/测试运行器降级为占位符UI + sync GUI集成(规范中心3按钮) + PLCService废弃重定向DiagnosticService + 文档编辑器另存为 | 影响: main_window.py + plc_service.py + document_editor.py + sync_engine.py | 已完成
- iteration_log:
  - 2026-06-01 V4.2功能对接迭代: Epic1(IPCBridge补全15组新API+Mock默认关闭)→Epic2(前端状态管理+30个ipc函数+辅助函数)→Epic3(仪表盘动态数据+项目CRUD闭环)→Epic4(文档编辑器+变更管理CRUD闭环)→Epic5(规范检查动态结果+设置保存/重置+自动修复视图+Excel导出视图)→Epic6(窗口控制按钮+初始化数据加载+侧边栏事件绑定) | 2文件修改(webview_window.py+index.html), IPCBridge 22→38 API, 前端0→100%按钮绑定 | 220测试通过 | ✅已完成
  - 2026-05-31 工作空间治理迭代: Phase 5(Workspace Governance: WorkspaceService+跨项目检查+命名冲突检测+聚合报告+汇总统计) | 3文件修改+2文件新增, 11个测试全通过 | ✅已完成
  - 2026-05-31 共享库治理迭代: Phase 4(Library Governance: LibraryService+LibraryArtifactType+规范目录识别+库资产扫描+分类统计+孤立文件检测) | 4文件修改+2文件新增, 14个测试全通过 | ✅已完成
  - 2026-05-31 伴生工作流迭代: Phase 3(Companion Flow: CompanionService+能力边界+跳转逻辑+编辑菜单伴生化+产品定位更新) | 7文件修改+2文件新增, 21个测试全通过 | ✅已完成
  - 2026-05-31 工作空间支持迭代: Phase 1(Workspace Core: ProjectType扩展+5级识别)→Phase 2(Workspace Load: load_workspace_from_path+_open_as_workspace+project_tree.load_workspace) | 6文件修改+1文件新增, 20个测试全通过 | ✅已完成
  - 2026-05-31 V3.1迭代完成: Epic A(FB接口一致性检查:fb_call_parser+fb_signature_builder+fb_interface_checker/6规则)→Epic B(自动批量修复:auto_fix_service+comment_punctuation_fixer+naming_fixer)→Epic C(Excel接口变量表导出9列精确格式:excel_exporter+fb_interface_template)→Epic D(SysLib公共库扫描:syslib_scanner+st_parser增强+spec_checker_service扩展) | 14个新文件, ~2500行代码 | 集成测试ALL PASSED(8个FB调用解析/23变量签名/453违规检测/3处标点修复/20库文件扫描/Excel导出) | ✅已完成
  - 2026-05-23 V2.3迭代完成: 文档同步+接口对齐 — 创建ARCH-V3.0.0(修正模块计数/接口描述/EventBus信号)+确认INT-V3.0.0已对齐 | 33个sync测试全PASS | ✅已完成
  - 2026-05-23 V2.2迭代执行: Epic1(P0修复:main.py+ANALYZING+approve校验)→Epic2(变更管理UI:ChangeManagementPanel+审核+CHG/IFC异步)→Epic3(sync测试:33个用例全PASS)→Epic4(技术债:StyleBuilder路径+ChangeRequest枚举+print→logger) | ✅代码完成
  - 2026-05-22 V2.1迭代完成: Epic2(变更管理闭环:SyncResultDialog+回写+审核状态)→Epic1(瘦身823→292行:5Builder+NavigationController)→Epic3(SpecCheck单实例引导页)→Epic4(诊断异步化+右键菜单+设置验证) | 62项UI测试全PASS | ✅已完成
  - 2026-05-22 V2.1迭代启动: Epic2优先(变更管理闭环) → Epic1(瘦身823→<400) → Epic3(SpecCheck单实例/引导页) → Epic4(遗留项) | 基准: main_window 823行, 62项UI测试全PASS | ✅已完成
  - 2026-05-22 文档同步迭代: 11份文档修订/版本更新/缺失补充 | ✅已完成
  - 2026-05-22 Sprint 0 M0: 全面审查 + 范围重定义 + Phase 1-3修复 | 已完成
  - 2026-05-21 Sprint 8-12: Phase A-D + GUI布局重构 | 已完成
- bug_log:
  - 2026-06-01 BUG-IPC-001: IPC调用返回null — pywebview 6.x API调用路径错误, 前端使用window.pywebview.xxx()但6.x版本要求window.pywebview.api.xxx() → 修正_pyapi()函数中的属性路径 → Ping返回pong验证通过 | 优先级: Critical | ✅已修复
  - 2026-06-01 BUG-GUI-002: 启动出现两个窗口 — webview_window.py模块顶层import webview + main()函数被意外触发(或create_window重复调用) → 删除webview_window.py的main()函数和__main__入口, 仅保留create_window()供main.py调用 | 优先级: High | ✅已修复
  - 2026-05-31 全模块诊断测试: 56个历史测试失败全部修复 — P0:NavigationController.navigate_to_tab映射错误(3失败) | P1:DiagnosticReport.total_issues未更新(9失败)+健康度空路径0分(6失败)+定时器检查器正则/逻辑错误(9失败)+命名检查器CONST_/注释/NameError(4失败)+变量解析器AT语法/关键字跳过(4失败) | P2:注释状态机/分隔符(4失败)+配置Path.sep(3失败)+SpecDoc正则(3失败)+集成序列化(1失败)+SCLTest未闭合/语法(2失败)+ST解析器注释/全局变量(2失败)+模板列表格式(2失败)+GUI信号测试(2失败→直接调用handler) | 优先级: Critical/High/Medium | ✅已修复(565通过+16跳过+0失败)
  - 2026-05-23 BUG-OPEN-001: 无法打开现有DJ项目(DJ-2026-005)→Controller只认project.json/.plc_project.json,不支持.plc_json且未识别DJ目录结构 | 优先级: Critical | ✅已修复(扩展白名单+DJ智能检测+Service多格式加载)
  - 2026-05-23 P0-1: main.py调用MainWindow._resolve_chinese_font→应用无法启动 | 优先级: Critical | ✅已修复(改为StyleBuilder._resolve_chinese_font)
  - 2026-05-23 P0-2: ChangeStatus.ANALYZING在valid_transitions中无定义→死胡同状态 | 优先级: Critical | ✅已修复(APPROVED→ANALYZING+ANALYZING→IN_PROGRESS)
  - 2026-05-23 P1-3: approve_change_request绕过valid_transitions校验 | 优先级: High | ✅已修复(改用valid_transitions校验)
  - 2026-05-23 GUI-001: TAB_CHANGE_MGMT(3)错误映射到TOOL_SPEC(4)→点击变更管理Tab显示规范中心 | 优先级: Critical | ✅已修复(方案B结构重构:新增独立变更管理ToolBox页面+重写映射表)
  - 2026-05-23 GUI-002~004: HMI工具映射冲突/规范中心与变更管理共享页面/架构不对称 | 优先级: High/Medium | ✅已修复(移除HMI页面+建立一一对应映射)
  - 2026-05-22 C-05: QSS文件QSplitter::handle:hover缺闭合括号→半数样式失效 | 优先级: Critical | ✅已修复
  - 2026-05-22 C-06: ToolBox(6页)↔TabWidget(5Tab)索引不匹配→导航越界 | 优先级: Critical | ✅已修复(映射表+blockSignals)
  - 2026-05-22 H-09: 内联样式与QSS文件严重冲突→主题切换无效 | 优先级: High | ✅已修复(迁移到QSS属性选择器)
  - 2026-05-22 H-10: Dashboard StatCard用findChild(QLabel)查找数值→找到图标标签 | 优先级: High | ✅已修复(直接引用_value_label)
  - 2026-05-22 H-11: 侧边栏ToolBox页面全是文字按钮列表→视觉"1大坨" | 优先级: High | ✅已修复(添加图标+分隔线+QSS属性)
  - 2026-05-22 M-13: 字体检测逻辑在main.py和main_window.py重复 | 优先级: Medium | ✅已修复
  - 2026-05-22 M-14~M-17: Controller接口化/枚举映射/菜单修复/EventBus | 优先级: Medium | ✅已修复
  - 2026-05-22 S-05: main_window._project_data从未赋值→变更管理3按钮完全不可用 | 优先级: Critical | ✅已修复
  - 2026-05-22 C-01~C-04: 诊断/测试/词法分析器Critical问题 | 优先级: Critical | ✅已修复
  - 2026-05-22 H-01/H-04/H-08: 硬编码路径/主线程sleep/跨组件私有属性 | 优先级: High | ✅已修复
  - 2026-05-22 H-02/H-06/H-07: 测试运行器/HMI/IO占位问题 | 优先级: High | 降级占位
  - 2026-05-22 M-01/M-02/M-09/M-10/M-12: 规范检查/文档编辑/配置路径/职责 | 优先级: Medium | ✅已修复
  - 2026-05-22 F-01: 左侧ToolBox侧边栏中文乱码 | 优先级: Critical | ✅已修复
  - 2026-05-31 GUI-FONT-001: GUI全局中文乱码→QSS全局font-family声明"Microsoft YaHei"(系统未安装)导致Qt回退到不支持中文的字体；系统仅安装"Microsoft YaHei UI"（注意UI后缀）| 影响: material_dark.qss+material_light.qss+style_builder.py+right_panel_builder.py+diagnostic_panel.py+document_editor.py+spec_check_panel.py (7文件14处字体声明) | 优先级: Critical | ✅已修复(全部更正为"Microsoft YaHei UI")
- refactor_log:
  - 2026-06-01 V4.2功能对接(Event B迭代): 前端全量对接后端服务 — webview_window.py新增15组API(close_project/get_project_detail/save_project_info/list_change_requests/create_change_request/update_change_status/approve_change_request/read_document/save_document/get_available_fixers/scan_fixes/fix_project/export_excel_single/export_excel_batch/get_dashboard_stats+3窗口控制), Mock默认值从"1"改为"0" | index.html: state对象扩展10个字段+30个ipc便捷函数+辅助函数(_statusBadgeHtml/_escHtml/ipcLoadDashboard)+6个render函数重写(renderDashboard/renderProjectDetail/renderDocumentEditor/renderChangeList/renderSpecCheck/renderSettings)+2个新render函数(renderAutoFix/renderExcelExport)+25个事件处理函数+__ipc_recv事件扩展+窗口控制绑定+初始化数据加载 | 影响: 2文件修改 | ✅已完成(220测试通过, 0回归)
  - 2026-06-01 架构迁移V4.0(Event C+技术栈变更): PyQt5→PyWebView(Chromium) — 动因: V3.2 FramelessWindow回归(系统标题栏未去除/文字重叠乱码/DPI缩放问题), QSS系统性限制导致无法还原HTML原型视觉效果 → 决策: 放弃PyQt GUI重写路线, 改用pywebview 6.2.1直接运行index.html原型 → 新增webview_window.py(IPCBridge类: 20个expose API覆盖项目管理/文档/同步/规范检查/诊断/设置/文件对话框) + create_window()函数(Chromium引擎+url直接加载+js_api桥接) → main.py重写(双模式入口: 默认PyWebView, PLC_GUI_MODE=pyqt回退PyQt5, lib/目录自动注入sys.path) → index.html添加IPC Bridge层(window.__ipc_recv事件分发 + _pyapi()异步调用封装 + 12个ipc*便捷函数 + updateStatusBarProject状态更新) | 影响: 2文件新增(webview_window.py+lib/) + 2文件修改(main.py+index.html) | ✅已完成(PyWebView启动+Chromium渲染+IPC注入验证通过)
  - 2026-06-01 GUI重构V3.2(Event C): 根据原型全面对齐GUI → 新增title_bar.py(自定义TitleBar: logo+标题+最小化/最大化/关闭按钮+拖拽移动+双击最大化+还原时鼠标位置比例计算) → main_window.py集成FramelessWindowHint+TitleBar信号连接+增强StatusBar(5项信息: 就绪/项目/规范/警告/编码/分辨率)+_toggle_maximize/changeEvent/update_status_*方法 → ide_dark.qss添加TitleBar样式(深色背景#151515+关闭按钮hover红色#F44747)+StatusBarItem属性样式+StatCard图标色块4色+QuickAction双属性+SectionTitle双属性+QMainWindow边框 → material_dark.qss同步添加TitleBar/StatusBarItem/QMainWindow边框 → material_light.qss同步添加浅色版TitleBar(#F3F3F3背景+关闭按钮hover#E81123)/StatusBarItem/QMainWindow边框 | 影响: 1文件新增+5文件修改 | ✅已完成(py_compile+运行验证通过)
  - 2026-06-01 UI重设计V3.1实施完成(Event A+C): 4Phase全部落地 → Phase A: material_dark.qss(+192行)+material_light.qss(+192行)升级ActivityBar橙条/Tab底线/StatusBar蓝底/全局圆角2→4px/8种Badge组件/Sidebar样式增强/StatCard图标色块/BottomPanel增强 → Phase B: dashboard.py完全重写(Hero标题28px+4业务StatCard图标色块+6QuickActions flex+最近项目图标路径) → Phase C1: main_window.py _create_project_tab()重写(Header60px+6字段表单+3操作按钮Primary/Secondary/Danger+5辅助方法) → Phase C2: change_management_panel.py重构(Toolbar 3按钮+搜索框+表格6列+状态Badge pill setCellWidget+行Hover#2A2D2E+表头橙色下划线, +282行65%) → Phase C3: spec_check_panel.py CheckerCard卡片式重构(新增CheckerCard类172行+CHECKERS数据定义7检查器+3列Grid toggle+引擎Badge Trae/Python/Hybrid+操作按钮行动态N/M+结果面板, 总1095行) → Phase C4: main_window.py _create_settings_tab()完整实现(3组设置Group+FormLabel+QComboBox/SpinBox/QCheckBox/QLineEdit+保存/恢复默认/浏览路径, +170行) | 影响: 6文件修改 | ✅实施完成(5/5 py_compile通过)
  - 2026-06-01 UI重设计V3.1规范(Event A+C): 全面差距分析(原型index.html 1979行 vs Qt实现6大组件) → 识别Top5关键差距(Sidebar非上下文切换🔴/Dashboard指标错误🔴/视觉扁平无精致度🔠/缺TitleBar🔠/规范中心无卡片toggle🔠) → 输出完整设计规范013_UI重设计规范_V3.1-DESIGN.md含8章(设计目标/全局令牌/五区布局重组/7视图详细设计/QSS升级规范/4Phase实施优先级/14项验收标准/4项风险) → 覆盖视觉焕新+布局重组+单页交互优化三大范围 | 影响: 全局UI层 | 🔄等待评审
  - 2026-06-01 UI重新设计原型: 采用IDE布局(Trae风格) — Activity Bar(48px图标栏+橙色激活指示) + 可折叠Siderbar(260px+可折叠Section+数字Badge) + Multi-Tab工作区 + Bottom Panel(输出/问题/终端三Tab) + Status Bar(蓝色); 7大视图: Dashboard(统计卡片+快速操作+最近项目) / 项目管理(树形浏览+表单详情) / 文档管理(代码编辑器+模板变量面板) / 变更管理(工具栏+数据表格+状态Badge) / PLC工具(ST编辑器+IO表+变量检查) / 规范中心(6检查器卡片+结果表格+操作按钮) / 设置(分组表单+主题切换)。产出: [ui_prototype/index.html](file:///c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-005_PLC项目管理工具\03_主程序\01_主程序核心代码\ui_prototype\index.html) (完整交互原型, 点击可切换视图) | ✅已完成 (初次原型)
  - 2026-06-01 规范中心重构(Event A+C): 检查器从"全量运行"改为"可选勾选+Trae引擎集成" — 7个检查器卡片(语法/注释→Trae插件引擎, 命名/配置/定时器→Python内置引擎, 变量/FB接口→混合引擎) 支持独立toggle+默认选中5项+全选/取消全选+开始检查按钮动态显示N/M, 侧边栏增加引擎Badge标签(Trae/混合), 侧边栏"全部检查"→"选择检查器"+新增FB接口调用入口 | 影响: index.html(CSS+JS+HTML) | 🔄等待评审
  - 2026-06-01 UI高DPI适配修复: Phase1(UIProfile参数优化: scale_factor上限1.25→1.65+dpi_factor上限1.30→2.0+密度乘数提升+基础字体10→11pt+间距全面增加) → Phase2(QSS主题样式升级: material_dark.qss 15处9pt→10pt/11pt+padding/min-height/字体全面优化) → Phase3(material_light.qss同步优化: 38处9pt→10pt+尺寸参数统一) → Phase4(MainWindow常量更新: 窗口/侧边栏尺寸同步UIProfile) → Phase5(验证测试: 2880*1800@200%缩放下scale_factor=1.32+base_font=15pt+GUI正常启动无报错) | 影响: 4文件修改(ui_scale.py+material_dark.qss+material_light.qss+main_window.py) | ✅已完成
  - 2026-05-31 GUI工业风格重构: Phase1(QSS主题系统: material_light.qss+material_dark.qss) → Phase2(StyleBuilder路径修复+主题加载) → Phase3(内联样式消除: 15+文件100+处setStyleSheet→setProperty属性选择器) → Phase4(IndustrialSidebar替换QToolBox: 可折叠区段+橙色指示条+深色面板) → Phase5(Tab精简8→6: 自动修复/Excel导出不再独立Tab) → Phase6(Dashboard工业风改造) | 影响: 15+文件修改+3文件新增(resources/styles/*+industrial_sidebar.py) | ✅已完成
  - 2026-05-23 V2.2重构: 新增ChangeManagementPanel(变更单列表+审核+状态流转) + CHG/IFC生成异步化(_GenerateDocWorker) + StyleBuilder路径遍历改用循环查找 + ChangeRequest.status改用ChangeStatus.DRAFT.value + SyncEngine print→logger | 影响: 8文件修改+1文件新增 | ✅已完成
  - 2026-05-22 V2.1重构: MainWindow 823→292行(-66%) — 5Builder+NavigationController+SyncResultDialog+回写+审核+SpecCheck单实例+诊断异步化+右键菜单+设置验证 | ✅已完成
  - 2026-05-22 Event B完成: UI Controller模式重构 — 3Controller + main_window 1205→982行 | ✅已完成
  - 2026-05-22 Event D完成: S-01 FB映射表统一fb_registry.py | ✅已完成
  - 2026-05-22 Phase 0死代码清理: 删除7个模块(~1500行) | ✅已完成
- release_log:
  - 2026-05-23 V2.2.1 发布: BUG-OPEN-001修复(无法打开现有DJ项目) — Controller白名单扩展+.plc.json支持+DJ智能检测+Service多格式加载 | 19/19专项测试通过+0新增回归 | ✅已发布
  - 2026-05-23 V2.2.0 开发中: P0修复+变更管理UI+sync测试+技术债

## 6. 审查问题清单（2026-05-23 V2.2更新）

### V2.2新增修复 (3项)
| ID | 问题 | 优先级 | 状态 |
|----|------|--------|------|
| P0-1 | main.py调用MainWindow._resolve_chinese_font→应用无法启动 | Critical | ✅已修复 |
| P0-2 | ChangeStatus.ANALYZING在valid_transitions中无定义→死胡同 | Critical | ✅已修复 |
| P1-3 | approve_change_request绕过valid_transitions校验 | High | ✅已修复 |

### 累计修复统计
- ✅ 已修复: 19项 (6 Critical + 7 High + 6 Medium) — V2.2新增3项
- ⏸ 降级占位: 6项 (H-02, H-06, H-07, M-03, M-05, M-11)
- 🔄 后续迭代: 4项 (M-07, M-08, L-01~08)
- 📊 总计: 35项 → 19修复 + 6降级 + 4+8后续

## 7. V2.2 文件变更清单

### 新增文件
| 文件 | 用途 | 行数 |
|------|------|------|
| src/ui/widgets/change_management_panel.py | 变更管理面板(列表+审核+状态流转) | ~280 |
| tests/test_change_service.py | ChangeService单元测试(10用例) | ~150 |
| tests/test_sync_engine.py | SyncEngine单元测试(13用例) | ~200 |
| tests/test_chg_ifc_generator.py | CHG/IFC生成器单元测试(10用例) | ~180 |

### 修改文件
| 文件 | 变更 |
|------|------|
| main.py | 修复StyleBuilder._resolve_chinese_font引用 |
| src/core/constants.py | ANALYZING状态转换规则补全 |
| src/services/change_service.py | approve_change_request改用valid_transitions校验 |
| src/ui/builders/right_panel_builder.py | 新增变更管理Tab |
| src/ui/builders/left_panel_builder.py | 侧边栏新增变更管理入口+Tab索引更新 |
| src/ui/controllers/navigation_controller.py | 新增TAB_CHANGE_MGMT映射 |
| src/ui/controllers/sync_controller.py | CHG/IFC生成异步化(_GenerateDocWorker) |
| src/ui/main_window.py | 集成变更管理面板+Tab索引更新 |
| src/ui/builders/style_builder.py | QSS路径遍历改用循环查找 |
| src/models/change_request.py | status默认值改用ChangeStatus.DRAFT.value |
| src/sync/sync_engine.py | print→logger |

## 8. 功能完成度（V2.2更新）

| # | 功能域 | V2.1完成度 | V2.2完成度 |
|---|--------|-----------|-----------|
| F01 | 项目管理(向导/模板/树/CRUD) | 90% | 90% |
| F02 | 文档生成(10模板/变量替换/另存为) | 95% | 95% |
| F03 | 变更管理-Sync(版本检查/CHG/IFC/报告/回写/审核) | 95% | 98% (+异步生成) |
| F04 | 规范检查(7检查器:可选勾选+Trae插件/Python内置/混合3引擎) | 95% | 95% → 重构中(UI已完成) |
| F05 | 诊断分析(七维度/LSP兼容性/Dock面板) | 85% | 85% |
| F06 | ST编辑器基础版(语法高亮) | 70% | 70% |
| F07 | 仪表盘(统计卡片/最近项目) | 85% | 85% |
| F08 | 变更管理-变更单(列表/创建/审核/状态流转UI) | 80% | 95% (+ChangeManagementPanel) |
| F09 | FB接口一致性检查(OB1调用参数vs FB定义:缺参/多参/类型/输出接出/IN_OUT/DB对齐) | 0% | 85% (+V3.1) |
| F10 | 自动批量修复(中文标点→英文半角/命名建议/.bak备份/dry_run预览) | 0% | 80% (+V3.1) |
| F11 | Excel接口变量表导出(9列精确格式/批量导出/检查报告/openpyxl) | 0% | 85% (+V3.1) |
| F12 | SysLib公共库扫描(递归扫描/全局FB-FC索引/版本提取/库引用一致性) | 0% | 85% (+V3.1) |

## 9. 深度审查报告（2026-05-23）

### 9.1 审查范围
- 主程序核心代码逻辑（main.py + app.py）
- 功能模块设计与模块间接口（11个Service + 4个Controller + 4个Builder + 2个Manager）
- GUI接口与功能模块对应关系（7个Widget + 5个Dialog + DashboardPage）
- 接口文档与实际代码对齐度（INT-V2.0.0 + ARCH-V2.0.0）

### 9.2 API接口文档与代码差异（INT-V2.0.0 → 实际代码）

#### 9.2.1 严重不匹配（方法名/签名完全不同）

| 文档API | 实际代码 | 差异类型 |
|---------|---------|---------|
| `ProjectService.open_project(path)` | `ProjectService.load_project_from_path(path)` → `(Project, error)` | 方法名+返回值不同 |
| `ProjectService.close_project()` | 不存在 | 文档虚构 |
| `DiagnosticService.run_diagnosis(path)` → report | `DiagnosticService().run_full_diagnostic(path)` → `(report, metrics)` | 方法名+返回值不同 |
| `DiagnosticService.run_lsp_check(path)` → lsp_result | 不存在独立方法，内嵌于run_full_diagnostic | 文档虚构 |
| `DocumentService.get_template_types()` | 不存在 | 文档虚构 |
| `DocumentService.generate_document(...)` | `DocumentService.create_document(...)` / `create_or_update_document(...)` | 方法名+参数不同 |
| `SpecCheckerService.get_available_rules()` | `SpecCheckerService().get_enabled_checkers()` | 方法名+返回类型不同 |
| `SpecCheckerService.run_checks(path, rule_ids)` | `SpecCheckerService().check_project(path)` / `check_file(path)` | 方法名+参数不同 |
| `SyncEngine.run_version_check(path)` | `SyncEngine.run_check(path)` | 方法名不同 |
| `ProjectController.create_project(parent)` | 不存在 | 文档虚构 |
| `ProjectController.open_project(parent)` | 不存在 | 文档虚构 |
| `ProjectController.save_project()` | 不存在 | 文档虚构 |
| `ProjectController.load_project_to_tree(path)` | 不存在 | 文档虚构 |
| `SyncController.run_version_check(path)` | `SyncController.on_sync_version_check()` | 方法名+参数不同 |
| `SyncController.run_generate_chg(path)` | `SyncController.on_sync_generate_chg()` | 方法名+参数不同 |
| `SyncController.run_generate_ifc(path)` | `SyncController.on_sync_generate_ifc()` | 方法名+参数不同 |
| `DashboardController.update_stats()` | `DashboardController.refresh_dashboard_data()` | 方法名不同 |
| `DashboardController.refresh_recent_projects()` | 不存在独立方法 | 文档虚构 |
| `SettingsManager.load(path)` | `SettingsManager.initialize(settings_dir)` | 方法名+参数不同 |

#### 9.2.2 文档缺失（实际存在但未记录）

| 模块 | 缺失的API |
|------|----------|
| ChangeService | `list_change_requests()`, `create_change_request()`, `update_status()`, `approve_change_request()` — 整个服务未记录 |
| NavigationController | `connect()`, `navigate_to_tab()`, `on_sidebar_action()`, `on_project_tree_navigate()` — 整个控制器未记录 |
| ArtifactRegistryService | `detect_project_type()`, `scan_project_assets()`, `summarize_assets()`, `get_artifact_roots()` — 整个服务未记录 |
| WorkflowService | `build_checkpoints()` — 整个服务未记录 |
| TemplateService | `initialize_builtin_templates()`, `get_template()`, `get_all_templates()`, `apply_template()` — 仅提及未详细记录 |
| SyncEngine | `run_full_report()`, `run_generate_chg()`, `run_generate_ifc()`, `writeback_to_project()`, `format_version_report_html()` |
| SettingsManager | `initialize()`, `reset_to_defaults()`, `get_all()` |
| ChangeManagementPanel | `set_project_path()`, `refresh()`, `cleanup()` — 整个Widget未记录 |
| SyncResultDialog | `get_action()`, `get_file_path()`, `get_doc_type()` — 整个Dialog未记录 |

#### 9.2.3 EventBus信号差异

| 文档记录的信号 | 实际代码 | 状态 |
|--------------|---------|------|
| `project_selected(str)` | ✅ 存在但从未连接 | ⚠️ 死信号 |
| `project_created(str)` | ✅ 存在且已连接 | ✅ |
| `project_opened(str)` | ✅ 存在且已连接 | ✅ |
| `project_closed()` | ❌ 不存在 | 文档虚构 |
| `document_open_request(str)` | ✅ 存在但处理为空 | ⚠️ 空处理 |
| `document_saved(str)` | ✅ 存在但从未发射 | ⚠️ 死信号 |
| `document_created(str)` | ✅ 存在但从未发射 | ⚠️ 死信号 |
| `check_started()` | ❌ 不存在 | 文档虚构 |
| `check_completed(object)` | ❌ 不存在 | 文档虚构 |
| `diagnostic_started()` | ❌ 不存在 | 文档虚构 |
| `diagnostic_completed(object)` | ❌ 不存在 | 文档虚构 |
| `st_file_open_request(str)` | ✅ 存在但从未连接 | ⚠️ 死信号 |
| `variable_check_request()` | ✅ 存在，MenuManager发射但无处理 | ⚠️ 断路信号 |
| `fb_doc_generate_request(str)` | ✅ 存在但从未发射/连接 | ⚠️ 死信号 |
| `spec_check_request(dict)` | ✅ 存在，ToolBarManager发射但无处理 | ⚠️ 断路信号 |
| `theme_changed(str)` | ✅ 存在且已连接 | ✅ |
| `settings_changed()` | ✅ 存在且已连接 | ✅ |
| `sync_*_requested` (文档V2.0-R2) | ❌ 不存在 | 文档虚构 |

### 9.3 架构文档与代码差异（ARCH-V2.0.0 → 实际代码）

| 维度 | 文档描述 | 实际代码 | 差异 |
|------|---------|---------|------|
| Widget数量 | 5个 | 7个(V2.2) | 9个(+AutoFixPanel, ExcelExportPanel) | ❌ |
| Dialog数量 | 4个 | 5个(+SyncResultDialog) | ❌ |
| Controller数量 | 3个 | 4个(+NavigationController) | ❌ |
| Service数量 | 9个 | 11个(+WorkflowService, ChangeService) | ❌ |
| Model数量 | 8个 | 13个(+ChangeRequest, CheckResult, ProjectArtifact, WorkflowCheckpoint等) | ❌ |
| Application类 | 有_run_cli()+shutdown() | 无CLI模式，无shutdown() | ❌ |
| Dashboard统计 | FB数/变量数/文档数/测试数 | 项目总数/进行中/已完成/已归档 | ❌ |
| MainWindow方法 | _build_menu_bar/_build_toolbar等 | 委托给MenuManager/ToolBarManager | ❌ |
| EventBus信号 | project_closed/check_started/completed等 | 不存在这些信号 | ❌ |
| SettingsManager | load(path) | initialize(settings_dir) | ❌ |

### 9.4 GUI与功能模块对应关系审查

#### 9.4.1 左侧ToolBox → 右侧Tab映射（✅ 正确）

| ToolBox页面 | 索引 | Tab页面 | 索引 | 状态 |
|------------|------|---------|------|------|
| 项目管理 | 0 | 仪表盘 | 0 | ✅ |
| 文档管理 | 1 | 项目 | 1 | ✅ |
| PLC工具 | 2 | 文档 | 2 | ✅ |
| HMI工具 | 3 | 变更管理 | 3 | ⚠️ 映射到TAB_SPEC_CHECK(5) |
| 规范中心 | 4 | PLC工具 | 4 | ✅ |
| 系统设置 | 5 | 规范检查 | 5 | ✅ |
| 自动修复 | 6 | 自动修复(TAB_AUTO_FIX=6) | 6 | ✅ V3.1新增 |
| Excel导出 | 7 | Excel导出(TAB_EXCEL_EXPORT=7) | 7 | ✅ V3.1新增 |

#### 9.4.2 GUI功能入口 → 服务层调用链（✅ 基本完整）

| GUI入口 | 触发方式 | Controller | Service | 状态 |
|---------|---------|-----------|---------|------|
| 新建项目 | 菜单/工具栏/仪表盘 | MenuManager→EventBus | ProjectService.create_new_project() | ✅ |
| 打开项目 | 菜单/工具栏/仪表盘 | MenuManager→EventBus | ProjectService.load_project_from_path() | ✅ |
| 项目树浏览 | 左侧面板 | ProjectController | ProjectService | ✅ |
| 项目信息更新 | 项目树双击 | ProjectController.update_project_info() | — | ✅ |
| 新建文档 | 侧边栏/项目树右键 | ProjectTreeWidget | DocumentService.create_document() | ✅ |
| 文档编辑 | 文档Tab | DocumentEditor | — (直接文件I/O) | ✅ |
| 另存为 | 文档编辑器工具栏 | DocumentEditor.save_file_as() | — | ✅ |
| 规范检查 | 菜单F5/侧边栏/Dock | SpecCheckPanel.start_check() | SpecCheckerService.check_project() | ✅ |
| 深度诊断 | 菜单F6/Dock | DiagnosticPanel.run_diagnostic() | DiagnosticService.run_full_diagnostic() | ✅ |
| 版本检查 | 侧边栏规范中心 | SyncController.on_sync_version_check() | SyncEngine.run_check() | ✅ |
| 生成CHG | 侧边栏规范中心 | SyncController.on_sync_generate_chg() | SyncEngine.run_generate_chg() | ✅ |
| 生成IFC | 侧边栏规范中心 | SyncController.on_sync_generate_ifc() | SyncEngine.run_generate_ifc() | ✅ |
| 变更单列表 | 变更管理Tab | ChangeManagementPanel.refresh() | ChangeService.list_change_requests() | ✅ |
| 创建变更单 | 变更管理Tab按钮 | ChangeManagementPanel._on_create() | ChangeService.create_change_request() | ✅ |
| 审核变更单 | 变更管理Tab按钮 | ChangeManagementPanel._on_approve() | ChangeService.approve_change_request() | ✅ |
| 推进状态 | 变更管理Tab按钮 | ChangeManagementPanel._on_advance() | ChangeService.update_status() | ✅ |
| 主题切换 | 菜单/侧边栏 | MenuManager→EventBus | StyleBuilder.apply() | ✅ |
| 设置 | 菜单/侧边栏 | MenuManager→SettingsDialog | SettingsManager | ✅ |
| ST编辑器 | PLC工具Tab | STEditor.open_file() | — (直接文件I/O) | ✅ |
| 源码跳转 | 诊断/规范检查面板 | MainWindow._jump_to_source() | STEditor.open_file() | ✅ |
| FB接口检查 | 规范检查Dock工具栏🔗按钮 | SpecCheckPanel._on_fb_ifc_check() | FBInterfaceChecker.check() | ✅ V3.1新增 |
| 自动修复 | 自动修复Tab | AutoFixPanel._on_scan() / _on_preview() / _on_execute() | AutoFixService.scan_project() / fix_project() | ✅ V3.1新增 |
| Excel导出单个FB | Excel导出Tab | ExcelExportPanel._on_export_single() | ExcelExporter.export_fb_from_file() | ✅ V3.1新增 |
| Excel批量导出 | Excel导出Tab | ExcelExportPanel._on_export_batch() | ExcelExporter.export_all_fbs() | ✅ V3.1新增 |
| 打开Excel文件 | Excel导出面板双击 | MainWindow._on_excel_file_open() | os.startfile() | ✅ V3.1新增 |

#### 9.4.3 GUI功能入口 → 断路/死信号（❌ 需修复）

| GUI入口 | 问题 | 严重度 |
|---------|------|--------|
| 工具栏"规范检查"按钮 | 发射spec_check_request但MainWindow未连接处理 | High |
| 菜单"变量检查" | 发射variable_check_request但MainWindow未连接处理 | Medium |
| HMI工具侧边栏页面 | 3个按钮(变量映射/报警配置/画面关联)映射到TAB_SPEC_CHECK | Medium |
| EventBus.project_selected | 定义但从未连接任何处理 | Low |
| EventBus.document_saved | 定义但从未发射 | Low |
| EventBus.document_created | 定义但从未发射 | Low |
| EventBus.st_file_open_request | 定义但从未发射/连接 | Low |
| EventBus.fb_doc_generate_request | 定义但从未发射/连接 | Low |

### 9.5 代码逻辑问题

| ID | 问题 | 严重度 | 建议 |
|----|------|--------|------|
| L-01 | Application类存在但main.py未使用，直接调用run_gui() | Medium | 删除Application类或重构main.py使用它 |
| L-02 | SpecService全部空实现(3个方法返回默认值) | Low | V2.3+实现或删除 |
| L-03 | VariableService全部空实现(2个方法返回默认值) | Low | V2.3+实现或删除 |
| L-04 | FBDocumentDialog仅占位标签+关闭按钮 | Low | V2.3+实现 |
| L-05 | _build_central_widget创建splitter但未加入layout(由_build_right_panel补上) | Low | 代码可读性优化 |
| L-06 | HMI工具页面3个按钮映射到TAB_SPEC_CHECK而非独立Tab | Medium | 改为占位提示或移除 |
| L-07 | SyncEngine.format_version_report_html引用entry.is_consistent，需确认VersionGapReport属性名 | High | 验证并修复 |

### 9.6 实际接口清单（代码真实API，用于更新INT-V3.0.0）

#### SettingsManager
```
initialize(settings_dir: Optional[Path] = None) → None
get(key: str, default: Any = None) → Any
set(key: str, value: Any) → None
save() → None
add_recent_project(project_path: str, project_name: str) → None
get_recent_projects() → List[Dict[str, str]]
reset_to_defaults() → None
get_all() → Dict[str, Any]
```

#### ProjectService (全部@classmethod)
```
create_project(name, business_line, template_id, manager, description, plc_brand, hmi_brand, custom_path) → (Optional[Project], Optional[str])
get_project(project_id) → Optional[Project]
get_all_projects() → List[Project]
load_project_from_path(project_path) → (Optional[Project], Optional[str])
delete_project(project_id) → (bool, Optional[str])
scan_projects_directory(directory) → List[Project]
create_new_project(project_info: Dict) → (Optional[Path], Optional[str])
import_dj_project(project_path) → (Optional[Project], Optional[str])
```

#### DiagnosticService (实例方法)
```
__init__(config: Optional[Dict] = None)
run_full_diagnostic(project_path) → (Any, Any)
get_last_diagnostics() → (Optional[Any], Optional[Any])
get_timing_statistics() → Dict[str, float]
is_healthy() → bool
reset() → None
```

#### DocumentService (全部@classmethod)
```
create_document(project_path, doc_type, doc_name, version, author, content) → (Optional[str], Optional[str])
create_or_update_document(project_path, doc_type, doc_name, version, author, content) → (Optional[str], Optional[str])
find_authoritative_document(project_path, doc_type) → Optional[str]
read_document(file_path) → (Optional[str], Optional[str])
save_document(file_path, content) → (bool, Optional[str])
list_documents(project_path) → List[Dict]
```

#### SpecCheckerService (实例方法)
```
__init__(config: Optional[Dict] = None)
check_project(project_path) → Any (CheckReport)
check_file(file_path) → Any (CheckResult)
get_enabled_checkers() → List[Any]
load_project_rules(project_path) → bool
clear_cache() → None
get_statistics() → Dict[str, int]
reset_statistics() → None
```

#### ChangeService (全部@classmethod)
```
list_change_requests(project_path) → List[ChangeRequest]
create_change_request(project_path, category, title, description) → (Optional[ChangeRequest], Optional[str])
update_status(project_path, change_id, new_status) → bool
approve_change_request(project_path, change_id, approver) → bool
```

#### SyncEngine (全部@classmethod)
```
run_check(project_path) → VersionGapReport
run_full_report(project_path, output_dir) → str
run_generate_chg(project_path, output_dir) → str
run_generate_ifc(project_path, output_dir) → str
writeback_to_project(source_path, project_path, doc_type) → List[str]
format_version_report_html(report) → str
```

#### TemplateService (全部@classmethod)
```
initialize_builtin_templates() → None
get_template(template_id) → Optional[Dict]
get_all_templates() → List[Dict]
get_template_metadata() → List[Dict]
apply_template(template_id, target_path, variables) → tuple
```

#### ArtifactRegistryService (全部@classmethod)
```
detect_project_type(project_path) → ProjectType
scan_project_assets(project_path) → List[ProjectArtifact]
summarize_assets(assets) → Dict[str, int]
get_artifact_roots(assets) → List[Dict[str, str]]
```

#### WorkflowService (全部@classmethod)
```
build_checkpoints(artifact_summary: dict) → List[WorkflowCheckpoint]
```

#### ProjectController
```
__init__(main_window)
on_project_created(path: str) → None
on_project_opened(path: str) → None
update_project_info(context: dict) → None
```

#### SyncController
```
__init__(main_window)
on_sync_version_check() → None
on_sync_generate_chg() → None
on_sync_generate_ifc() → None
```

#### DashboardController
```
__init__(main_window)
on_dashboard_action(action_id: str) → None
refresh_dashboard_data() → None
```

#### NavigationController
```
__init__(tool_box, tab_widget, menu_manager, sync_handler, project_info_handler)
connect() → None
navigate_to_tab(tab_index: int) → None
on_sidebar_action(action_text: str) → None
on_project_tree_navigate(tab_index: int, context: dict) → None
```

#### EventBus 信号（实际定义）
```
project_selected(str)       — ⚠️ 未连接
project_created(str)        — ✅ 已连接
project_opened(str)         — ✅ 已连接
document_open_request(str)  — ✅ 已连接(空处理)
document_saved(str)         — ⚠️ 未发射
document_created(str)       — ⚠️ 未发射
st_file_open_request(str)   — ⚠️ 未连接
variable_check_request()    — ⚠️ 发射但无处理
fb_doc_generate_request(str)— ⚠️ 未连接
spec_check_request(dict)    — ⚠️ 发射但无处理
theme_changed(str)          — ✅ 已连接
settings_changed()          — ✅ 已连接
```

### 9.7 审查结论与行动建议

**结论**: 代码架构设计合理（薄壳+Controller+Builder+EventBus），功能模块与GUI基本对应完整。主要问题是**文档严重滞后于代码**，22处API不匹配+6个死信号+架构文档计数错误。

**优先行动项**:

| 优先级 | 行动 | 影响范围 |
|--------|------|---------|
| P0 | 更新API接口文档INT-V3.0.0，对齐9.6节实际接口清单 | 009_API接口文档 |
| P0 | 更新架构文档ARCH-V3.0.0，修正模块计数和接口描述 | 007_架构设计文档 |
| P1 | 连接spec_check_request信号到SpecCheckPanel.start_check() | main_window.py |
| P1 | 连接variable_check_request信号到规范检查或提示 | main_window.py |
| P1 | 修复HMI工具页面映射(改为占位提示) | left_panel_builder.py |
| P2 | 清理EventBus死信号(删除或实现) | event_bus.py |
| P2 | 删除或重构Application类(当前为死代码) | app.py + main.py |
| P2 | 验证SyncEngine.format_version_report_html属性引用 | sync_engine.py |
