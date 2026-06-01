# 工作空间支持开发规划 DEV-PLAN-V1.0.0

> **项目**: SW-2026-005 PLC项目管理工具  
> **日期**: 2026-05-31  
> **适用范围**: 当前主线开发计划  
> **执行对象**: GLM5.1

---

## 1. 开发背景

当前工具只能稳定打开单个 PLC 项目，无法把 `0100_PLC自动化/` 这类真实项目库作为工作空间挂载。

这会直接导致：
- 无法以树状结构浏览整个 PLC 项目库
- 无法把 `SysLib` 这类共享库纳入统一治理
- 无法对多个项目做跨项目检查与汇总
- 继续维持“单项目心智”，产品会不断堆叠补丁

本轮目标是从根上补齐 `Workspace` 层，而不是做一次短期兼容。

---

## 2. 目标与非目标

### 2.1 目标

- 支持工作空间根目录识别
- 支持工作空间聚合加载多个子项目
- 支持共享库识别与降级加载
- 让工具成为 Trae 伴生式治理工具
- 保持文档与实现同步更新

### 2.2 非目标

- 不实现语言服务器
- 不实现 TIA Portal 网关
- 不改造为新的主编辑器
- 不做无边界的大型架构重写

---

## 3. 代码改动清单

| 序号 | 文件 | 改动重点 |
|---|---|---|
| 1 | `src/core/constants.py` | 新增 `PLC_LIBRARY`、`PLC_WORKSPACE` 等枚举 |
| 2 | `src/services/artifact_registry_service.py` | 新增工作空间/共享库检测逻辑 |
| 3 | `src/services/project_service.py` | 新增 `load_workspace_from_path()` |
| 4 | `src/ui/controllers/project_controller.py` | 在 `on_project_opened()` 中增加工作空间分支 |
| 5 | `tests/` | 新增工作空间识别、加载、UI分支测试 |

---

## 4. 实施顺序

### Phase 1: 核心识别 ✅ 已完成

目标：
- 扩展 `ProjectType`
- 完成 `detect_project_type()` 工作空间识别

实施点：
- `workspace.json` 显式优先
- DJ 三标记保持兼容
- 共享库通过 `.plc.json + 分类目录` 识别
- 2 个及以上可识别子项目支持隐式工作空间判定

**实现备注**：
- `constants.py`：`ProjectType` 枚举新增 `PLC_LIBRARY` 和 `PLC_WORKSPACE`；`BusinessLine` 枚举新增 `LIBRARY`；新增常量 `WORKSPACE_IGNORED_DIRS` 和 `PLC_LIBRARY_CATEGORY_DIRS`；更新描述映射
- `artifact_registry_service.py`：`detect_project_type()` 实现 5 级优先级判定（workspace.json → DJ三标记 → .plc.json+分类目录 → ≥2子项目 → GENERIC）；新增方法 `_is_plc_library()`、`_count_identifiable_subprojects()`、`_is_dj_project()`、`_has_project_config()`、`scan_workspace_subprojects()`、`_classify_subproject()`

### Phase 2: 工作空间加载 ✅ 已完成

目标：
- 完成 `load_workspace_from_path()`

实施点：
- 一层遍历工作空间子目录
- 忽略 `.trae/.git/__pycache__/_archive/node_modules/.venvs`
- 支持 DJ 项目、共享库、普通 `.plc.json` 子项目
- 共享库缺少标准配置时降级构造 `Project`

**实现备注**：
- `project_service.py`：新增 `load_workspace_from_path()`、`_load_subproject()`、`_create_library_project()`、`_create_fallback_project()`；工作空间加载支持 DJ/lib/generic 三类子项目，共享库缺少配置时通过 `_create_library_project()` 降级构造，其他不可识别子目录通过 `_create_fallback_project()` 兜底

### Phase 3: UI 集成 ✅ 已完成

目标：
- 打通"打开工作空间"入口

实施点：
- `ProjectController.on_project_opened()` 新增分支
- 新增 `_open_as_workspace()`
- 项目树支持批量加载子项目
- 状态栏反馈工作空间加载结果

**实现备注**：
- `project_controller.py`：`on_project_opened()` 新增 `PLC_WORKSPACE` 分支，调用 `_open_as_workspace()` 方法
- `project_tree.py`：新增 `load_workspace()` 方法实现批量加载；新增 `_build_library_nodes()` 构建共享库节点；`load_project()` 增加 `plc_library` 类型处理

### Phase 4: 测试与回归 ✅ 已完成

目标：
- 证明工作空间支持未破坏现有单项目能力

实施点：
- 识别测试
- 加载测试
- UI分支测试
- 单一 DJ 项目回归验证

**实现备注**：
- `tests/test_workspace.py`：共 20 个测试用例，覆盖 TC-W01~TC-W09 及回归测试，全部通过
- 测试内容包括：workspace.json 识别、多DJ子目录识别、DJ+SysLib 混合识别、单一DJ项目不误判、共享库识别、空目录返回GENERIC、工作空间聚合加载、忽略目录过滤、UI打开分支、单项目回归验证

### Phase 5: 文档同步

目标：
- 让规划文档继续与代码一致

实施点：
- 同步更新 `006~010`
- 如实现细节变化，反向修订本文件

### Phase 6: 伴生工作流固化 ✅ 已完成

目标：
- 把产品定位从"独立桌面主工具"收敛为"Trae伴生工具"

实施点：
- 新建 CompanionService 集中管理 Trae 交互边界
- 重构 `_jump_to_source()` 为伴生跳转模式
- 编辑菜单替换撤销/重做为"在Trae中打开"
- 产品描述更新为伴生定位
- 关于对话框体现伴生角色

**实现备注**：
- `companion_service.py`：新建，含 `can_handle`/`should_jump_to_ide`/`jump_to_file`/`_open_in_trae`/`_open_with_system`/`get_role_description`/`get_jump_summary`
- `constants.py`：`DESCRIPTION` 更新，新增 `COMPANION_ROLE`/`COMPANION_PRIMARY_IDE`/`COMPANION_CAPABILITIES`/`COMPANION_NON_CAPABILITIES`/`TRAJUMP_SUPPORTED_EXTENSIONS`
- `event_bus.py`：新增 `companion_jump_request` 信号
- `main_window.py`：`_jump_to_source()` 重构为伴生优先+降级，`_on_excel_file_open()` 委托 CompanionService
- `project_tree.py`：`_on_item_double_clicked()` 新增伴生跳转，workspace 节点处理
- `menu_manager.py`：编辑菜单伴生化，新增 `_on_open_in_trae()`，关于对话框更新
- `tests/test_companion.py`：21 个测试用例，覆盖 TC-C01~TC-C09，全部通过

### Phase 7: 共享库与规范目录识别治理 ✅ 已完成

目标：
- 实现共享库目录的深度扫描与治理能力

实施点：
- 新建 LibraryService 实现共享库扫描、分类、统计
- 新增 LibraryArtifactType 枚举定义资产类型
- 新增 SPEC_DIR_MARKERS 标识规范目录
- 新增 LIBRARY_ST_EXTENSIONS / LIBRARY_SPEC_EXTENSIONS 定义文件扩展名
- 实现 _infer_artifact_type() 分类目录到资产类型的推断
- ArtifactRegistryService 扩展共享库资产扫描方法
- 编写 TC-L01~TC-L09 测试用例

**实现备注**：
- `constants.py`：新增 `LibraryArtifactType` 枚举（FB/FC/DB/UDT/GVL/PROGRAM/SPEC/DOC/TEST）、`SPEC_DIR_MARKERS`（`00_通用规范`/`01_编程规范`/`02_设计规范`/`00_规范`/`spec`/`specs`/`standards`）、`LIBRARY_ST_EXTENSIONS`（`.scl`/`.st`/`.plc`）、`LIBRARY_SPEC_EXTENSIONS`（`.md`/`.yaml`/`.yml`/`.json`）、`LIBRARY_ARTIFACT_TYPE_DESC` 描述映射
- `library_service.py`：新建，含 `scan_library`/`identify_spec_dirs`/`get_library_summary`/`_scan_category_dir`/`_scan_spec_dir`/`_scan_unknown_dir`/`_scan_orphan_files`/`_infer_artifact_type`；数据类 `LibraryArtifact`/`LibraryScanResult`
- `artifact_registry_service.py`：新增 `scan_library_artifacts()`/`identify_spec_dirs_in_library()`
- `tests/test_library_governance.py`：14 个测试用例，覆盖 TC-L01~TC-L09，全部通过

### Phase 8: 工作空间治理 ✅ 已完成

目标：
- 实现工作空间级跨项目检查、聚合报告、汇总统计和命名冲突检测

实施点：
- 新建 WorkspaceService 实现跨项目检查、聚合报告、汇总统计
- 实现命名冲突检测（跨项目FB/FC同名检测）
- 新增 WorkspaceCheckItem/NamingConflict/WorkspaceReport 数据类
- ProjectService 新增 get_workspace_summary()/generate_workspace_report() 编排方法
- ProjectController 新增 check_workspace()/generate_workspace_report() UI入口
- ProjectTree 新增工作空间统计展示
- 编写 TC-G01~TC-G09 测试用例

**实现备注**：
- `workspace_service.py`：新建，含 `generate_report`/`detect_naming_conflicts`/`check_workspace`/`get_workspace_statistics`/`_count_project_files`；数据类 `WorkspaceCheckItem`/`NamingConflict`/`WorkspaceReport`
- `project_service.py`：新增 `get_workspace_summary()`/`generate_workspace_report()` 编排方法，委托 WorkspaceService 执行
- `project_controller.py`：新增 `check_workspace()`/`generate_workspace_report()` UI入口方法
- `project_tree.py`：`load_workspace()` 中新增汇总统计节点展示
- `tests/test_workspace_governance.py`：11 个测试用例，覆盖 TC-G01~TC-G09，全部通过

---

## 5. 接口与行为要求

### 5.1 识别优先级

1. `workspace.json` -> `PLC_WORKSPACE`
2. DJ 三标记 -> `DJ_SINGLE_MACHINE`
3. `.plc.json + 分类目录` -> `PLC_LIBRARY`
4. >=2 个可识别子项目 -> `PLC_WORKSPACE`
5. 其他 -> `GENERIC`

### 5.2 工作空间打开行为

- 选择工作空间根目录后，不应再提示“未找到项目配置文件”
- 若工作空间中无任何可管理子项目，应提示工作空间打开失败
- 成功加载后，应能在项目树看到多个子项目节点

### 5.3 Trae伴生约束

- 工具负责查看、治理、汇总
- PLC 主编辑仍在 Trae 完成
- 不向本轮设计中添加新的重型编辑器逻辑

---

## 6. 测试清单

| 编号 | 测试内容 | 验收点 | 测试结果 |
|---|---|---|---|
| TC-W01 | 显式 `workspace.json` | 正确识别 `PLC_WORKSPACE` | ✅ 通过 |
| TC-W02 | 多 DJ 子目录 | 正确识别 `PLC_WORKSPACE` | ✅ 通过 |
| TC-W03 | DJ + SysLib | 正确识别 `PLC_WORKSPACE` | ✅ 通过 |
| TC-W04 | 单一 DJ 项目 | 不误判工作空间 | ✅ 通过 |
| TC-W05 | 共享库目录 | 正确识别 `PLC_LIBRARY` | ✅ 通过 |
| TC-W06 | 空目录 | 返回 `GENERIC` | ✅ 通过 |
| TC-W07 | 工作空间聚合加载 | 返回所有可管理子项目 | ✅ 通过 |
| TC-W08 | 忽略目录 | `.trae` 等不影响结果 | ✅ 通过 |
| TC-W09 | UI 打开分支 | 工作空间成功打开，不弹旧错误框 | ✅ 通过 |
| TC-C01 | CompanionService 基本能力 | can_handle 正确判断文件类型 | ✅ 通过 |
| TC-C02 | 伴生跳转决策 | should_jump_to_ide 按扩展名和IDE可用性决策 | ✅ 通过 |
| TC-C03 | Trae跳转执行 | jump_to_file 优先调用Trae打开文件 | ✅ 通过 |
| TC-C04 | 系统降级打开 | Trae不可用时降级为系统默认打开 | ✅ 通过 |
| TC-C05 | 伴生角色描述 | get_role_description 返回伴生定位文案 | ✅ 通过 |
| TC-C06 | 跳转摘要 | get_jump_summary 返回跳转结果摘要 | ✅ 通过 |
| TC-C07 | 编辑菜单伴生化 | 撤销/重做替换为"在Trae中打开" | ✅ 通过 |
| TC-C08 | 关于对话框 | 体现伴生角色与定位 | ✅ 通过 |
| TC-C09 | 项目树双击跳转 | 双击文件节点触发伴生跳转 | ✅ 通过 |
| TC-L01 | 标准共享库扫描 | 识别分类目录和规范目录，ST/规范文件计数正确 | ✅ 通过 |
| TC-L02 | 分类目录文件计数 | ST源码和规范文件分别计数正确 | ✅ 通过 |
| TC-L03 | 规范目录识别 | `00_通用规范`/`specs` 等正确识别为规范目录 | ✅ 通过 |
| TC-L04 | 根目录孤立文件检测 | 根目录下的 `.scl`/`.md` 文件识别为孤立文件 | ✅ 通过 |
| TC-L05 | 空共享库 | 返回零ST计数，分类列表为空 | ✅ 通过 |
| TC-L06 | 资产类型推断 | 分类目录名正确映射到 `LibraryArtifactType` | ✅ 通过 |
| TC-L07 | `identify_spec_dirs()` | 正确识别规范目录，排除分类目录 | ✅ 通过 |
| TC-L08 | `get_library_summary()` | 返回完整摘要信息 | ✅ 通过 |
| TC-L09 | `scan_library_artifacts()` | ArtifactRegistryService 正确分类资产目录 | ✅ 通过 |
| TC-G01 | 工作空间统计 | `get_workspace_statistics()` 返回完整统计信息 | ✅ 通过 |
| TC-G02 | 项目类型分布 | 统计中包含各项目类型分布 | ✅ 通过 |
| TC-G03 | 命名冲突计数 | 无冲突时 `naming_conflicts` 为 0 | ✅ 通过 |
| TC-G04 | 跨项目FB冲突检测 | 同名FB出现在多个子项目中时检测为冲突 | ✅ 通过 |
| TC-G05 | 不同名称无冲突 | 不同名称的FB不产生冲突 | ✅ 通过 |
| TC-G06 | 存在项目检查 | 存在的项目返回 `ok` 状态 | ✅ 通过 |
| TC-G07 | 缺失项目检查 | 不存在的项目目录返回 `error` 状态 | ✅ 通过 |
| TC-G08 | 聚合报告生成 | 报告包含完整信息（名称/项目数/文件数/时间） | ✅ 通过 |
| TC-G09 | 报告序列化 | `to_dict()` 返回所有必需字段 | ✅ 通过 |

> **测试执行摘要**：`tests/test_workspace.py` 共 20 个测试用例，覆盖 TC-W01~TC-W09 及回归测试，全部通过（2026-05-31）。`tests/test_companion.py` 共 21 个测试用例，覆盖 TC-C01~TC-C09，全部通过（2026-05-31）。`tests/test_library_governance.py` 共 14 个测试用例，覆盖 TC-L01~TC-L09，全部通过（2026-05-31）。`tests/test_workspace_governance.py` 共 11 个测试用例，覆盖 TC-G01~TC-G09，全部通过（2026-05-31）。

---

## 7. GLM5.1 执行要求

- 严格按 `constants -> artifact_registry_service -> project_service -> project_controller -> tests` 的顺序实现
- 每完成一个阶段，都同步修正受影响文档
- 不允许把工作空间识别规则散落到 UI 层
- 不允许为了快而引入新的硬编码和耦合链路

---

## 8. 完成定义

满足以下条件，视为本轮工作空间支持开发完成：

- ✅ 能正确识别工作空间、共享库和单项目（Phase 1 已完成，5 级优先级判定已实现）
- ✅ 能从工作空间根目录成功加载多个子项目（Phase 2 已完成，支持 DJ/lib/generic 三类子项目及降级构造）
- ✅ 单项目打开逻辑无回归（Phase 4 已完成，20 个测试用例全部通过）
- ✅ 测试用例覆盖 `TC-W01 ~ TC-W09`（Phase 4 已完成，TC-W01~TC-W09 全部通过）
- ✅ 产品定位收敛为 Trae 伴生工具（Phase 6 已完成，CompanionService 集中管理交互边界）
- ✅ 伴生跳转与降级机制已实现（Phase 6 已完成，Trae 优先 + 系统降级）
- ✅ 编辑菜单与关于对话框体现伴生角色（Phase 6 已完成）
- ✅ 测试用例覆盖 `TC-C01 ~ TC-C09`（Phase 6 已完成，21 个测试用例全部通过）
- ✅ 共享库深度扫描与治理能力已实现（Phase 7 已完成，LibraryService 扫描/分类/统计/推断）
- ✅ 规范目录识别能力已实现（Phase 7 已完成，SPEC_DIR_MARKERS 标识 + identify_spec_dirs）
- ✅ 资产类型推断能力已实现（Phase 7 已完成，LibraryArtifactType + _infer_artifact_type）
- ✅ 测试用例覆盖 `TC-L01 ~ TC-L09`（Phase 7 已完成，14 个测试用例全部通过）
- ✅ 工作空间治理能力已实现（Phase 8 已完成，WorkspaceService 跨项目检查/聚合报告/汇总统计/命名冲突检测）
- ✅ 命名冲突检测能力已实现（Phase 8 已完成，detect_naming_conflicts 跨项目FB/FC同名检测）
- ✅ 聚合报告生成能力已实现（Phase 8 已完成，WorkspaceReport 数据类 + generate_report）
- ✅ 测试用例覆盖 `TC-G01 ~ TC-G09`（Phase 8 已完成，11 个测试用例全部通过）
- ✅ 文档与代码保持一致（Phase 5 已完成，006~011 已同步更新）

---

*文档版本: DEV-PLAN-V1.0.0 | 最后更新: 2026-05-31*

---

## 附录：实现记录

> 以下记录 Phase 1~4 的实际实现情况，供后续文档同步（Phase 5）参考。

### A. 代码改动实际清单

| 序号 | 文件 | 实际改动 |
|---|---|---|
| 1 | `src/core/constants.py` | `ProjectType` 新增 `PLC_LIBRARY`、`PLC_WORKSPACE`；`BusinessLine` 新增 `LIBRARY`；新增 `WORKSPACE_IGNORED_DIRS`、`PLC_LIBRARY_CATEGORY_DIRS` 常量；更新描述映射；新增 `LibraryArtifactType` 枚举、`SPEC_DIR_MARKERS`、`LIBRARY_ST_EXTENSIONS`、`LIBRARY_SPEC_EXTENSIONS`、`LIBRARY_ARTIFACT_TYPE_DESC` |
| 2 | `src/services/artifact_registry_service.py` | `detect_project_type()` 实现 5 级优先级判定；新增 `_is_plc_library()`、`_count_identifiable_subprojects()`、`_is_dj_project()`、`_has_project_config()`、`scan_workspace_subprojects()`、`_classify_subproject()`；新增 `scan_library_artifacts()`、`identify_spec_dirs_in_library()` |
| 3 | `src/services/project_service.py` | 新增 `load_workspace_from_path()`、`_load_subproject()`、`_create_library_project()`、`_create_fallback_project()` |
| 4 | `src/ui/controllers/project_controller.py` | `on_project_opened()` 新增 `PLC_WORKSPACE` 分支；新增 `_open_as_workspace()` |
| 5 | `src/ui/project_tree.py` | 新增 `load_workspace()`、`_build_library_nodes()`；`load_project()` 增加 `plc_library` 处理 |
| 6 | `src/services/library_service.py` | 新建共享库治理服务；`scan_library`/`identify_spec_dirs`/`get_library_summary`/`_scan_category_dir`/`_scan_spec_dir`/`_scan_unknown_dir`/`_scan_orphan_files`/`_infer_artifact_type`；数据类 `LibraryArtifact`/`LibraryScanResult` |
| 7 | `tests/test_workspace.py` | 20 个测试用例，覆盖 TC-W01~TC-W09 及回归测试，全部通过 |
| 8 | `tests/test_library_governance.py` | 14 个测试用例，覆盖 TC-L01~TC-L09，全部通过 |
| 9 | `src/services/workspace_service.py` | 新建工作空间治理服务；`generate_report`/`detect_naming_conflicts`/`check_workspace`/`get_workspace_statistics`/`_count_project_files`；数据类 `WorkspaceCheckItem`/`NamingConflict`/`WorkspaceReport` |
| 10 | `src/services/project_service.py`（扩展） | 新增 `get_workspace_summary()`/`generate_workspace_report()` 编排方法 |
| 11 | `src/ui/controllers/project_controller.py`（扩展） | 新增 `check_workspace()`/`generate_workspace_report()` UI入口方法 |
| 12 | `src/ui/widgets/project_tree.py`（扩展） | `load_workspace()` 中新增汇总统计节点展示 |
| 13 | `tests/test_workspace_governance.py` | 11 个测试用例，覆盖 TC-G01~TC-G09，全部通过 |

### B. 与原始规划的偏差

无重大偏差。实际实现与规划一致，仅 `project_tree.py` 未在原始改动清单中单独列出（原清单第 5 项为 `tests/`），现补充记录。
