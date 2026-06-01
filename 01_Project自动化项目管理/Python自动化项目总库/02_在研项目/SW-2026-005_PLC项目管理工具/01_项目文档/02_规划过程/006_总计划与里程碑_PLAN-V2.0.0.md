# 总计划与里程碑 PLAN-V2.0.0

> **项目**: SW-2026-005 PLC项目管理工具  
> **版本**: V2.0.0  
> **日期**: 2026-05-31  
> **当前主线**: PLC项目库/工作空间支持  
> **产品形态**: Trae伴生工具

---

## 1. 总体目标

将 `SW-2026-005` 从“单项目管理工具”演进为 **Trae伴生式 PLC 工作空间治理工具**，形成以下能力闭环：
- 挂载 PLC 工作空间，而不是只打开单个项目目录
- 识别 DJ 项目、共享库、规范目录等多类子资产
- 以树状结构浏览整个项目库并进行跨项目治理
- 在 Trae 中继续完成 PLC 源码与文档主开发，工具侧负责索引、检查、文档与汇总

### 1.1 当前根因

当前代码链路只能识别：
- 根目录存在 `project.json` / `.plc_project.json` / `.plc.json`
- 或目录结构满足 DJ 单机项目三标记

因此当用户直接打开 `0100_PLC自动化/` 这类工作空间根目录时，会被误判为“不是项目”。

### 1.2 本轮目标

- 建立 `Workspace / Child Project / Shared Library / Spec Directory` 统一模型
- 支持工作空间根目录挂载与子项目聚合加载
- 明确 Trae 与 SW-2026-005 的职责分层
- 形成一套可直接交给 GLM5.1 开发的规划文档体系

### 1.3 非目标

- 不替代 Trae 作为 PLC 主开发环境
- 不将工作空间支持扩展为多人协同平台
- 不在本轮引入 SCL 语言服务器或 TIA 网关等未来能力

---

## 2. 版本主线

| 阶段 | 目标版本 | 目标说明 | 输出重点 |
|---|---|---|---|
| Phase 0 | 文档重整基线 | 统一规划主线，清理历史/储备混用 | 006~011 文档重构 |
| Phase 1 | Workspace Core ✅ | 扩展项目类型与识别规则 | `ProjectType` / `detect_project_type()` |
| Phase 2 | Workspace Load ✅ | 支持工作空间加载与树形展示 | `load_workspace_from_path()` / UI打开分支 |
| Phase 3 | Companion Flow ✅ | 固化 Trae伴生工作流与跳转边界 | 文档与交互口径统一 |
| Phase 4 | Library Governance ✅ | 共享库/规范目录识别与治理 | `PLC_LIBRARY` / 全库扫描入口 |
| Phase 5 | Workspace Governance ✅ | 跨项目检查、聚合报告与汇总视图 | 全库规范检查与统计面板 |

---

## 3. 分阶段实施建议

### 3.1 Phase 0: 文档重整基线

目标：
- 重建 `02_规划过程/` 目录作为唯一权威源
- 明确主线文档、历史资料、未来储备的边界

Done 标准：
- `README` 能正确导航到 `006~011`
- 历史 `011_V2.1开发规划...` 不再作为主线入口
- `012_V3.0开发规划...` 被显式标注为储备方向

### 3.2 Phase 1: Workspace Core ✅已完成

目标：
- 扩展 `ProjectType` 与项目识别规则
- 支持显式与隐式的工作空间判定

建议内容：
- 新增 `PLC_LIBRARY`
- 新增 `PLC_WORKSPACE`
- 识别 `workspace.json`
- 识别共享库目录 `.plc.json + 分类子目录`

实际实现：
- `ProjectType` 新增 `PLC_LIBRARY` / `PLC_WORKSPACE` 枚举值
- `BusinessLine` 新增 `LIBRARY` 枚举值
- `detect_project_type()` 实现5级优先级识别链：`workspace.json` → `.plc_project.json` → `.plc.json` + 子目录结构 → DJ三标记 → 兜底未知

Done 标准：
- 能区分 `DJ_SINGLE_MACHINE`、`PLC_LIBRARY`、`PLC_WORKSPACE` ✅
- 单一 DJ 项目不会被误判为工作空间 ✅

### 3.3 Phase 2: Workspace Load ✅已完成

目标：
- 从工作空间根目录聚合加载所有子项目
- 在 UI 中以工作空间模式展示

建议内容：
- 新增 `ProjectService.load_workspace_from_path()`
- 在 `ProjectController.on_project_opened()` 中增加工作空间分支
- 工作空间根节点支持子项目树加载

实际实现：
- `ProjectService.load_workspace_from_path()` 实现工作空间根目录聚合加载
- `ProjectService._open_as_workspace()` 实现工作空间打开分支逻辑
- `project_tree.load_workspace()` 实现工作空间子项目树形加载与展示

Done 标准：
- 打开 `0100_PLC自动化/` 不再报"未找到项目配置文件" ✅
- 至少能加载 DJ 项目、共享库项目和 `.plc.json` 子项目 ✅

### 3.4 Phase 3: Companion Flow ✅已完成

目标：
- 把产品定位从"独立桌面主工具"收敛为"Trae伴生工具"

建议内容：
- 文档中统一声明 Trae 是主开发环境
- 工具只负责挂载、索引、治理、汇总
- 避免再新增重型编辑耦合设计

实际实现：
- `companion_service.py` 新增 CompanionService 服务，提供 `can_handle()` / `should_jump_to_ide()` / `jump_to_file()` / `_open_in_trae()` / `_open_with_system()` 方法，封装伴生跳转决策与执行逻辑
- `constants.py` 更新 DESCRIPTION 为"Trae伴生式PLC工作空间治理工具"，新增 `COMPANION_ROLE` / `COMPANION_PRIMARY_IDE` / `COMPANION_CAPABILITIES` / `COMPANION_NON_CAPABILITIES` / `TRAJUMP_SUPPORTED_EXTENSIONS` 常量，明确伴生角色定位与能力边界
- `event_bus.py` 新增 `companion_jump_request` 信号，支持伴生跳转事件总线通信
- `main_window.py` 重构 `_jump_to_source()`，优先尝试 CompanionService 跳转，回退到内部编辑器
- `project_tree.py` `_on_item_double_clicked()` 为文档/代码节点增加伴生跳转逻辑，新增工作空间节点处理分支
- `menu_manager.py` Edit 菜单将 undo/redo 替换为"在Trae中打开"（Ctrl+E），新增 `_on_open_in_trae()`，About 对话框更新为显示伴生角色信息
- `tests/test_companion.py` 编写 21 条测试用例，覆盖 TC-C01~TC-C09，全部通过

Done 标准：
- 文档与 README 中不再把产品描述为独立主开发平台 ✅
- 工作流说明与实际交互路径一致 ✅

### 3.5 Phase 4: Library Governance ✅已完成

目标：
- 识别共享库和规范目录
- 为后续全库治理打基础

建议内容：
- 共享库降级加载策略
- 规范目录纳入工作空间概览
- 为 `SysLib` 这类目录建立可浏览入口

实际实现：
- `library_service.py` 新增 LibraryService 服务，提供 `scan_library()` / `identify_spec_dirs()` / `get_library_summary()` / `_scan_category_dir()` / `_scan_spec_dir()` / `_scan_orphan_files()` / `_infer_artifact_type()` 方法，实现共享库全量扫描与规范目录识别
- `constants.py` 新增 `LibraryArtifactType` 枚举（FB / FC / DB / UDT / GVL / PROGRAM / SPEC / DOC / TEST），新增 `SPEC_DIR_MARKERS` / `LIBRARY_ST_EXTENSIONS` / `LIBRARY_SPEC_EXTENSIONS` 常量，定义库制品类型与文件扩展名映射
- `artifact_registry_service.py` 新增 `scan_library_artifacts()` 和 `identify_spec_dirs_in_library()` 方法，将库扫描能力接入制品注册体系
- `project_service.py` 的 `_create_library_project()` 现在调用 `LibraryService.scan_library()`，将 `library_scan` / `artifact_roots` / `spec_dirs` 附加到 `project.extra`
- `project_tree.py` 的 `_build_library_nodes()` 增强，支持 summary / category / spec_dirs / orphan_files 展示
- `tests/test_library_governance.py` 编写 14 条测试用例，覆盖 TC-L01~TC-L09，全部通过

Done 标准：
- 共享库节点能在工作空间中稳定出现 ✅
- 规范目录信息可在工作空间概览中展示 ✅

### 3.6 Phase 5: Workspace Governance ✅已完成

目标：
- 支持跨项目规范检查和聚合视图

建议内容：
- 工作空间级规范检查入口
- 聚合统计视图
- 子项目与共享库的汇总报告输出

实际实现：
- `workspace_service.py` 新增 WorkspaceService 服务，提供 `generate_report()` / `detect_naming_conflicts()` / `check_workspace()` / `get_workspace_statistics()` / `_count_project_files()` 方法，并定义 `WorkspaceCheckItem` / `NamingConflict` / `WorkspaceReport` 数据类，实现工作空间级跨项目检查、命名冲突检测与聚合报告生成
- `project_service.py` 新增 `get_workspace_summary()` 和 `generate_workspace_report()` 方法，将工作空间治理能力接入 ProjectService 接口层
- `project_controller.py` 新增 `check_workspace()` 和 `generate_workspace_report()` 方法，提供工作空间检查与报告生成的 UI 入口
- `project_tree.py` 工作空间根节点增强，展示聚合统计信息（项目数量、ST文件数、规范文件数、命名冲突数）
- `tests/test_workspace_governance.py` 编写 11 条测试用例，覆盖 TC-G01~TC-G09，全部通过

Done 标准：
- 能对工作空间内多个子项目做统一检查 ✅
- 汇总结果可回溯到具体子项目与目录 ✅

---

## 4. GLM5.1 执行顺序

1. 阅读 `011_工作空间支持开发规划_DEV-PLAN-V1.0.0.md`
2. 按 `008_详细设计文档_DES-V2.0.0.md` 实现核心设计
3. 按 `009_API接口文档_INT-V3.0.0.md` 对齐接口签名与返回语义
4. 参考 `010_代码结构说明_DEV-V2.0.0.md` 快速定位改动目录
5. 完成实现后，反向更新 `006~010` 中受影响段落

---

## 5. 风险与控制

| 风险 | 等级 | 说明 | 控制措施 |
|---|---|---|---|
| 继续沿用单项目心智 | 高 | 实现会退化成补丁式兼容 | 先按 Workspace 模型重写文档与枚举 |
| 文档继续版本漂移 | 高 | GLM5.1 可能按错误入口开发 | 统一入口索引，只保留主线导航 |
| UI层承担过多业务逻辑 | 中 | 容易再次形成屎山 | 工作空间逻辑优先沉到 Service 层 |
| 共享库误判 | 中 | 影响工作空间识别准确性 | 显式 `workspace.json` 优先，隐式规则兜底 |
| 未来方向混入当前开发 | 中 | 稀释本轮目标 | `012` 降级为储备文档 |

---

## 6. 验收口径

本轮规划文档重整完成后，应满足：
- 任何开发者从 `02_规划过程/README.md` 进入，都能直接找到当前主线文档
- 从 `006` 能看清当前为什么做工作空间支持、阶段怎么推进、当前不做什么
- 文档整体表达与用户目标一致：**Trae 主开发，SW-2026-005 做工作空间治理**

### 已达标阶段

- **Phase 1 验收达标** ✅：`ProjectType.PLC_LIBRARY` / `PLC_WORKSPACE`、`BusinessLine.LIBRARY`、`detect_project_type()` 5级优先级识别链均已实现，能正确区分 DJ 单机项目、共享库与工作空间
- **Phase 2 验收达标** ✅：`load_workspace_from_path()`、`_open_as_workspace()`、`project_tree.load_workspace()` 均已实现，打开工作空间根目录不再报错，子项目树形加载正常
- **Phase 3 验收达标** ✅：产品描述已体现伴生定位（"Trae伴生式PLC工作空间治理工具"），能力边界通过 `COMPANION_CAPABILITIES` / `COMPANION_NON_CAPABILITIES` 常量明确界定，跳转逻辑优先 Trae 并保留内部编辑器回退，Edit 菜单不再暗示独立编辑器（undo/redo 已替换为"在Trae中打开"）
- **Phase 4 验收达标** ✅：LibraryService 全库扫描正确识别分类目录与规范目录，文件计数准确，规范目录标记（SPEC_DIR_MARKERS）被正确识别，孤立文件（orphan files）可被检测，库摘要（library summary）信息完整，14 条测试用例（TC-L01~TC-L09）全部通过
- **Phase 5 验收达标** ✅：工作空间统计信息完整（项目数量、ST文件数、规范文件数），命名冲突检测正常工作，跨项目检查可识别错误与警告，聚合报告包含所有必需字段（WorkspaceReport/WorkspaceCheckItem/NamingConflict 数据类），ProjectService API（`get_workspace_summary()` / `generate_workspace_report()`）功能正常，11 条测试用例（TC-G01~TC-G09）全部通过

---

*文档版本: PLAN-V2.0.0 | 最后更新: 2026-05-31*
