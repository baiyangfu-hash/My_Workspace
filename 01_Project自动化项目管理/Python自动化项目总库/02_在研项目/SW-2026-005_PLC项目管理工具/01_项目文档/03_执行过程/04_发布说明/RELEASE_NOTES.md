# RELEASE NOTES

> 项目: SW-2026-005 PLC项目管理工具  
> 维护范围: 执行阶段发布清单与变更摘要

## V2.2.1（2026-05-23）

### 修复

- **BUG-OPEN-001 Critical**: 无法打开现有DJ项目（如DJ-2026-005）— Controller前置检查只识别`project.json`和`.plc_project.json`两种格式，不支持PLC工程标准配置文件`.plc.json`，且未利用Service层的DJ项目目录结构智能识别能力，导致所有非工具创建的现有PLC项目均无法打开

### 变更明细

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `src/ui/controllers/project_controller.py` | 修改 | 扩展`SUPPORTED_PROJECT_FILES`白名单新增`.plc.json`；增加DJ项目目录结构智能检测降级策略（根目录无配置文件时通过`ArtifactRegistryService.detect_project_type()`识别DJ标记目录） |
| `src/services/project_service.py` | 修改 | `import_dj_project()`从硬编码单一`.plc_project.json`改为按优先级遍历`DJ_CANDIDATE_META_FILES`（`.plc_project.json`→`.plc.json`→`project.json`）；加载失败自动尝试下一个候选文件 |
| `tests/test_bug_open_001.py` | 新增 | BUG-OPEN-001专项测试套件，19个用例覆盖白名单/检测逻辑/多格式加载/降级处理/真实项目集成 |

### 技术细节

**根因**: UI层`ProjectController.on_project_opened()`在调用Service层之前执行了硬编码的前置文件检查，只允许`project.json`和`.plc_project.json`两种格式通过。而实际DJ项目中PLC工程标准配置文件为`.plc.json`（与ST程序同目录），且该文件可能位于子目录而非项目根目录。Controller的前置检查阻断了Service层已有的DJ项目智能识别逻辑。

**修复策略**: 
1. 白名单扩展：新增`.plc.json`为第三种支持的配置文件格式
2. 智能降级：当根目录无配置文件时，通过`ArtifactRegistryService.detect_project_type()`检测DJ标记目录（`00_项目管理`/`02_PLC程序`/`03_HMI设计`），识别为DJ项目则放行给Service层处理
3. Service层多格式加载：`import_dj_project()`按优先级遍历3种候选配置文件，加载失败自动降级尝试下一个，均无则创建虚拟Project对象

### 测试结论

#### 专项测试（19/19 PASS）

| 分类 | 用例数 | 通过 | 覆盖范围 |
|------|--------|------|----------|
| Controller白名单 | 2 | 2 | 3种格式完整性检查 |
| Controller检测逻辑 | 6 | 6 | 有配置放行/无配置DJ放行/空目录拦截/非DJ拦截 |
| Service多格式加载 | 4 | 4 | .plc_project.json/.plc.json/project.json/无配置降级 |
| Service路径加载 | 2 | 2 | DJ自动识别/通用项目需project.json |
| ArtifactRegistry检测 | 3 | 3 | 完整DJ标记/无标记/部分标记 |
| 真实项目集成 | 1 | 1 | DJ-2026-005端到端加载（85项资产） |
| 边界/异常 | 1 | 1 | 配置文件损坏时降级创建虚拟Project |

#### 关联模块回归（89/91 PASS，97.8%）

| 测试文件 | 通过 | 失败 | 备注 |
|----------|------|------|------|
| test_bug_open_001.py | 19 | 0 | 本次新增 |
| test_change_service.py | 10 | 0 | — |
| test_document_service.py | 12 | 0 | — |
| test_sync_engine.py | 13 | 0 | — |
| test_chg_ifc_generator.py | 10 | 0 | — |
| test_template_service.py | 7 | 2 | 预存失败，非本次引入 |
| test_integration.py | 18+ | 0 | — |

#### 全量回归（443 PASS / 56 FAIL / 16 SKIP）

56个失败均为预存问题，**本次修改未引入任何新增回归失败**。预存失败分布：test_lsp_diagnostic(10)、test_timer_checker(8)、test_health_analyzer(6)、test_naming_checker(4)、test_comment_checker(4)、test_variable_checker(4)、test_config_checker(3)、test_checker_framework(3)、test_gui_navigation(3)、test_st_parser(2)、test_template_service(2)、test_scltest_parser(2)、test_integration(1)。

### 已知限制

- DJ项目检测依赖3个标记目录（`00_项目管理`/`02_PLC程序`/`03_HMI设计`）全部存在，缺少任一则为GENERIC类型
- 子目录中的`.plc.json`（如`02_PLC程序/通用ST程序及变量表/.plc.json`）由Service层`import_dj_project()`在无根目录配置时创建虚拟Project对象处理，暂不解析子目录配置文件内容
- 多配置文件共存时按白名单顺序优先使用（project.json > .plc_project.json > .plc.json）

## V2.0-R2（2026-05-22）

### 修复
- **C-05 Critical**: QSS文件QSplitter::handle:hover缺闭合括号→半数样式失效
- **C-06 Critical**: ToolBox(6页)↔TabWidget(5Tab)索引不匹配→导航越界
- **H-09**: 内联样式与QSS文件严重冲突→主题切换无效
- **H-10**: Dashboard StatCard用findChild查找数值→找到图标标签
- **H-11**: 侧边栏ToolBox页面全是文字按钮列表→视觉"1大坨"
- **M-13~M-17**: 字体去重/Controller接口化/枚举映射/菜单修复/EventBus
- SpecCheck Dock面板未创建→WARN
- QLayout重复布局(new_project_dialog)→WARN
- 退出时Windows fatal exception(0x80010108/0x80010012)→cleanup架构

### 重构
- Controller模式: 创建3个Controller(project/sync/dashboard)，MainWindow 1293→926行(-28.3%)
- cleanup架构: DiagnosticPanel/SpecCheckPanel/ScoreRingWidget/BarChartWidget统一cleanup()
- 侧边栏: SIDEBAR_ACTION_MAP枚举映射替代中文字符串匹配
- 主题系统: 内联样式迁移到QSS属性选择器

### 验证
- test_ui_buttons.py: 62项测试，57 PASS / 0 CRASH / 0 ERROR / 0 WARN / 5 NOOP
- 退出异常消除: exit_code=0，无COM异常

## V2.0-R1（2026-05-22）

### 修复
- **S-05 Critical**: _project_data从未赋值→变更管理3按钮完全不可用
- **C-01~C-04 Critical**: QConicalGradient未导入/TestWorker双重信号/线程不安全/词法状态丢失
- **H-01/H-04/H-08**: 硬编码路径/主线程sleep/跨组件私有属性访问
- **M-01/M-02/M-09/M-10/M-12**: 规范检查空操作/缺另存为/配置路径错误/职责重叠

### 重构
- 死代码清理: 删除7个模块(~1500行)
- FB映射表统一: fb_registry.py替代三重复制
- sync GUI集成: 规范中心3按钮(版本检查/CHG/IFC)
- HMI/IO/测试运行器降级为占位符(V2.0范围重定义)
- 字体修复: 动态检测9种中文字体候选

### 降级占位(V2.1+规划)
- H-02: 测试运行器只执行第一个匹配suite
- H-06: HMI映射按钮信号未连接
- H-07: IO分配表导入不解析
- M-03/M-05/M-11: 测试运行器设置/勾选状态/HMI占位符

## V1.4.0（2026-05-21）

### 新增
- sync/ Phase D: sync_report全量同步报告生成器(5段式Markdown)

## V1.3.0（2026-05-21）

### 新增
- sync/ Phase A: version_extractor + version_checker + sync_engine + sync_cli
- sync/ Phase B: db_parser + ifc_generator
- sync/ Phase C: session_parser + chg_generator

## V1.1.0（2026-05-10）

- DocumentService：补齐文档模板体系
- 执行过程：建立测试计划、变更列表与版本台账骨架
- 测试：pytest 已通过
