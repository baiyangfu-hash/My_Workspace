# SW-2026-007 pm-mgr 工具链健康修复 Spec

## Why

SW-2026-007 (pm-mgr) 是 pm-workflow 技能的核心工具依赖，但当前项目自身存在严重的治理缺失：无 PM_SESSION、未注册到规范体系、代码存在多个功能缺陷和与 pm-workflow 技能定义不一致的问题。作为"项目管理工作流工具链"，自身必须首先符合规范才能管理其他项目。

## What Changes

### A. 项目治理（自身合规）
- 创建 PM_SESSION_SW-2026-007.md（完整 §0-§9 + Spec Snapshot）
- 注册 SW-2026-007 到 spec_registry.json（cross-domain 域）

### B. 代码功能修复
- 修复 `detect.py`：rglob 无深度限制导致大目录扫描极慢，需限制搜索深度
- 修复 `snapshot.py`：SPEC_IDS 硬编码且不完整，缺少 Python 域规范（DEV-210/211/220）和变更管理域规范（DEV-004/CHG-040/CHG-041/PM-042）
- 修复 `snapshot.py`：`read_spec_versions` 只读6个固定 spec_id，应动态从 SPEC_IDS 读取
- 修复 `check.py`：检查项不完整，缺少 PM_SESSION 章节完整性检查（§0-§9 是否齐全）
- 修复 `bootstrap.py`：software 项目目录结构缺少 `01_项目文档/02_规划过程` 子目录和 `01_项目文档/04_监控和控制` 等标准 PM 目录
- 修复 `bootstrap.py`：software 模板映射 SW_TEMPLATES 只有3个模板，缺少 REQ/DES/变更管理等核心文档模板

### C. 与 pm-workflow 技能对齐
- PM-004 规范需升级至 V1.2.0：补充 pm-mgr 工具使用说明、PM_SESSION 完整模板结构（§0-§9）、新增3种模式（规范/初始化/补完）
- python-rules.md 文件名引用格式修正（移除版本后缀）
- plc-rules.md 版本号更新（LSP-903 V1.0.0→V2.1.0, LSP-904 V1.1.0→V1.2.0）+ 文件名引用格式修正

## Impact

- Affected specs: PM-004 (升级V1.2.0), python-rules.md, plc-rules.md, spec_registry.json
- Affected code: pm_mgr/detect.py, pm_mgr/snapshot.py, pm_mgr/check.py, pm_mgr/bootstrap.py
- Affected projects: SW-2026-007 自身（创建PM_SESSION）, 所有使用 pm-mgr 的项目

## ADDED Requirements

### Requirement: PM_SESSION 创建

系统 SHALL 为 SW-2026-007 项目创建完整的 PM_SESSION_SW-2026-007.md，包含 §0-§9 全部章节和 Spec Snapshot。

#### Scenario: PM_SESSION 完整性
- **WHEN** 检查 SW-2026-007 项目健康状态
- **THEN** PM_SESSION 包含 §0 Meta / §1 Positioning / §2 Current Focus / §3 Status Summary / §4 Artifacts Index / §5 Logs / §6 Implementation Log / §7 Verification Log / §8 Handoff Notes / §9 Next Actions / Spec Snapshot

### Requirement: 规范注册

系统 SHALL 将 SW-2026-007 注册到 spec_registry.json 的 cross-domain 域。

#### Scenario: 注册表查询
- **WHEN** 查询 spec_registry.json 中 SW-2026-007
- **THEN** 返回包含 title/canonical_path/version/domain=lifecycle=stable 的完整条目

### Requirement: detect 搜索深度限制

pm-mgr detect 命令 SHALL 限制 rglob 搜索深度为3层，避免在大目录中扫描过深导致性能问题。

#### Scenario: 大目录扫描
- **WHEN** 对包含深层嵌套目录的项目执行 detect
- **THEN** 搜索深度不超过3层，且在5秒内返回结果

### Requirement: snapshot 动态规范列表

pm-mgr snapshot 命令 SHALL 支持按项目类型动态读取完整的相关规范列表，而非硬编码6个固定 spec_id。

#### Scenario: software 项目 Spec Snapshot
- **WHEN** 对 software 类型项目执行 snapshot
- **THEN** Spec Snapshot 包含 PROJ-016, PRD-001, DEV-031, DEV-032, DEV-210, DEV-211, DEV-220, INT-215, DEV-004, CHG-040, CHG-041, PM-042

#### Scenario: plc 项目 Spec Snapshot
- **WHEN** 对 plc 类型项目执行 snapshot
- **THEN** Spec Snapshot 包含 PROJ-016, REQ-020, LSP-905, LSP-904, LSP-903, LSP-906, LSP-907, INT-815, PLC-023, DEV-004, CHG-040, CHG-041, PM-042

### Requirement: PM_SESSION 章节完整性检查

pm-mgr check 命令 SHALL 检查 PM_SESSION 是否包含 §0-§9 全部必要章节。

#### Scenario: 缺失章节检测
- **WHEN** PM_SESSION 缺少 §6 Implementation Log 或 §9 Next Actions
- **THEN** check 报告中显示 FAIL 并指出缺失的章节名称

### Requirement: software 项目目录结构补全

pm-mgr init 命令为 software 类型项目创建的目录结构 SHALL 包含完整的 PM 流程目录。

#### Scenario: 初始化 software 项目
- **WHEN** 执行 pm-mgr init 创建 software 项目
- **THEN** 创建的目录包含 01_项目文档/01_启动过程, 01_项目文档/02_规划过程, 01_项目文档/03_执行过程, 01_项目文档/04_监控和控制, 01_项目文档/05_收尾过程

## MODIFIED Requirements

### Requirement: PM-004 规范升级至 V1.2.0

PM-004 规范 SHALL 补充以下内容：
1. §9 pm-mgr 工具使用说明（5个子命令的接口和行为描述）
2. §10 PM_SESSION 完整模板结构定义（§0-§9 各章节的必填/选填字段说明）
3. §3.3 新增3种事件类型：Event F 规范巡检、Event G 项目初始化、Event H 旧项目补完

### Requirement: python-rules.md 文件名引用修正

python-rules.md 中规范文件引用 SHALL 使用不带版本后缀的实际文件名。

### Requirement: plc-rules.md 版本号更新

plc-rules.md 中 LSP-903 版本 SHALL 从 V1.0.0 更新为 V2.1.0，LSP-904 版本 SHALL 从 V1.1.0 更新为 V1.2.0，文件名引用 SHALL 使用不带版本后缀的实际文件名。
