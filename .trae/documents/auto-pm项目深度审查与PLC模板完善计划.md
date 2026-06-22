# auto-pm 项目深度审查与 PLC 模板完善计划

> **审查日期**: 2026-06-23
> **审查对象**: SW-2026-008 auto-pm 自动化项目管理工具
> **审查范围**: 文档与代码深度解读 + PLC 专项功能审查（模板/初始化/创建/编辑/检查/修复）
> **参考基准**: 0100_PLC自动化 总库（DJ-2026-000/DJ-2026-005/SysLib）+ LSP-905/906/907 规范
> **任务性质**: 仅审查报告，不改代码

---

## 一、执行摘要

### 1.1 总体结论

auto-pm 项目（V0.2.1）**整体架构成熟、基座稳定**，已具备 CLI + GUI 双形态管理能力，875 测试通过、覆盖率 81%。但 **PLC 专项功能存在系统性缺陷**：模板与实际项目严重脱节、规范覆盖度仅 8%、CLI 层绕过 Service 层、SubstanceChecker 实现不规范。

### 1.2 落地可行性评估

| 维度 | 状态 | 评级 |
|------|------|------|
| Python 项目管理能力 | ✅ 完整可用 | A |
| 变更管理（12 状态机） | ✅ 完整可用 | A |
| GUI 桌面应用 | ✅ 可用（有 flaky 测试） | B+ |
| PLC 模板管理框架 | ⚠️ 框架完整但内容不完整 | C+ |
| PLC 检查/修复能力 | ⚠️ 仅覆盖 LSP-907 的 20% | D |
| PLC 项目初始化 | ❌ 模板生成的项目无法直接使用 | D- |

**结论**：auto-pm **可作为 Python 项目管理工具立即落地**；但 **PLC 专项功能需重大改进后方可落地**，当前用 `plc init` 创建的项目无法通过 `plc check`，且无法生成符合 LSP-907 规范的真实 PLC 项目结构。

### 1.3 关键阻塞问题（6 项 Critical）

1. **C-1**: 模板在根级生成 .plc.json（违反 LSP-907 §3.1）
2. **C-2**: `_minimal_plc_json` 硬编码 libraries 路径（对根级项目错误）
3. **C-3**: CLI 层完全绕过 PlcService 层（分层架构形同虚设）
4. **C-4**: SubstanceChecker 字数统计语义错误（`len()` 统计字符非字数）
5. **C-5**: 模板生成的文档全部触发实质化 WARN（新建即报警）
6. **C-6**: `plc init`/`plc repair`/`plc standardize` CLI 命令无测试覆盖

---

## 二、auto-pm 项目现状分析

### 2.1 项目定位

- **项目编号**: SW-2026-008
- **版本**: 0.2.1（V2.0 基座 + V2.0.1-A/C 修复 + V2.1 里程碑 27 迭代完成）
- **核心目标**: 统一 CLI + GUI 管理 PLC/Python 多技术栈项目的脚手架工具
- **整合策略**: 全量吸收 5 个源工具（SW-2026-001/004/005/006/007）

### 2.2 已实现能力清单

| 能力域 | 实现状态 | 关键文件 |
|--------|---------|---------|
| 项目 CRUD + 导入 | ✅ | [project.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/cli/project.py) |
| PLC 检查/修复/标准化 | ⚠️ 框架完整，覆盖不足 | [plc/](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/plc/) |
| 变更管理（12 状态机） | ✅ | [change/](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/change/) |
| Copier 模板管理 | ✅ 框架完整 | [template_service.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/core/template_service.py) |
| PySide6 GUI | ✅ 8 子模块 | [ui/](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/ui/) |
| SQLite 索引缓存 | ✅ WAL + 增量扫描 | [db/](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/db/) |

### 2.3 待办路线图

| 版本 | 内容 | 状态 |
|------|------|------|
| V2.0.1-B | plc check 文档实质化检查集成 | ⚠️ SubstanceChecker 已建，CLI 未暴露 |
| V2.0.1-D | 906/905/023 PLC 规范矛盾代码修复（41 片段） | ❌ 未开始 |
| V2.0.1-E | spec_registry.json 同步 | ❌ 未开始 |
| V2.2 | 规范中心完整整合（吸收 SW-2026-006） | ❌ 未开始 |
| V2.3 | 变量表解析整合（吸收 SW-2026-001） | ❌ 未开始 |
| V2.4 | 模板管理增强（CRUD/版本/插件） | ❌ 未开始 |
| V2.5 | 系统设置 + 用户管理 + PyInstaller 打包 | ❌ 未开始 |

### 2.4 文档与代码一致性

INT V2.0.1 已大量标注文档与代码偏差：

| 文档声明 | 实际实现 | 严重度 |
|---------|---------|--------|
| SVC-06 `ProjectService.import_project()` | 由 CLI 层 shutil + retrofit 实现 | 中 |
| SVC-07 `ProjectService.classify_project()` | 由 `extract_business_line()` 函数实现 | 中 |
| SVC-08 `ProjectService.search_projects()` | 由 `list_projects_filtered()` 实现 | 中 |
| CLI-20 `gui --role` | V2.0 已删除角色系统 | 低 |
| DSN §9.1 `ui/models/role.py` | 文件不存在，Role 在 models/enums.py | 低 |

---

## 三、PLC 总库参考分析

### 3.1 总库三层架构

```
0100_PLC自动化/
├── 00_通用规范/PLC编程/          # 规范权威（8 份核心规范）
├── 01_SharedLibraries/SysLib/    # 共享库（所有项目共用）
├── DJ-2026-000/                  # 简化项目示例（扁平结构）
└── DJ-2026-005/                  # 完整工程示例（11 标准目录）
```

### 3.2 三种项目模式（用户确认的目标模式）

| 模式 | 参考项目 | 结构特征 | 适用场景 |
|------|---------|---------|---------|
| **公共库** | SysLib | actuator/communication/convert/counter/edge/log/pulse/timer/types 模块化 | 新建共享函数库 |
| **公共库验证** | DJ-2026-000 | 扁平结构（DB1/OB1/Test/PRD） | 测试套件、小型验证项目 |
| **标准单机项目** | DJ-2026-005 | 11 标准目录 + TPL-SINGLE-PLC-M001 | 中大型单机设备工程 |

### 3.3 关键规范要点

| 规范 | 版本 | 核心要求 |
|------|------|---------|
| LSP-905 | V1.0.3 | SCL 命名前缀（i_/o_/q_/s_/fb_）、语法白名单、METHOD 限制 |
| LSP-907 | V1.2.1 | .plc.json 配置、标准目录布局、新建项目检查清单 |
| LSP-906 | V1.0.0 | FB_TON PT/ET 为 DINT、定时器三段式调用、.plc-out 保护 |
| LSP-904 | V1.2.0 | 注释格式（// 或单层 (* *)）、禁止嵌套 |
| PLC-023 | V2.0.0 | 程序设计文档模板（三层架构/Region/FB 文件头） |
| INT-815 | V1.1.0 | 接口文档模板（IO 映射表/FB 接口） |

### 3.4 .plc.json 配置规则（LSP-907 §1）

```json
{
  "name": "DJ-2026-005",
  "description": "边框缓存机 PLC 控制系统",
  "version": "V6.0.0",
  "libraries": ["../../../01_SharedLibraries/SysLib"]
}
```

**关键规则**：
- 字段名必须是 `libraries`（非 `libraryDirectories`）
- 路径相对于 `.plc.json` 所在目录计算
- 使用正斜杠 `/`，禁止绝对路径
- `libraries` 为条件必填（引用共享库时必须配置）

---

## 四、PLC 专项功能深度审查（六维度）

### 4.1 模板维度

#### 4.1.1 模板模块组成

| 组件 | 路径 | 状态 |
|------|------|------|
| TemplateService | [template_service.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/core/template_service.py) | ✅ 完成（198 行） |
| CLI template 命令 | [cli/template.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/cli/template.py) | ✅ 完成（77 行） |
| GUI 模板管理页 | [template_page.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/ui/global_pages/template_page.py) | ✅ 完成（358 行） |
| plc-standard 模板 | [templates/plc-standard/](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/templates/plc-standard/) | ⚠️ 框架完整，内容不完整 |
| python-tool 模板 | [templates/python-tool/](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/templates/python-tool/) | ✅ 完成 |

#### 4.1.2 plc-standard 模板与实际项目差距清单

**模板生成的结构**：
```
{{project_id}}_{{project_name}}/
├── 02_PLC程序/通用ST程序及变量表/.plc.json.jinja
├── 03_HMI设计/.gitkeep
├── 04_变更管理/.gitkeep          # ⚠️ 位置错误，应在 00_项目管理/下
├── 04_现场调试/.gitkeep
├── PRD/（4 份 Jinja2 文档）
├── .copier-answers.yml.jinja
├── .plc.json.jinja               # ❌ 错误：根级不应有 .plc.json
└── PM_SESSION_{{ project_id }}.md.jinja
```

**实际 DJ-2026-005 结构**（参考基准）：
```
DJ-2026-005/
├── 00_项目管理/01_立项与需求/003_项目立项表_PROJ.md
├── 00_项目管理/04_变更管理/
├── 01_需求与设计/13_软件方案/
├── 02_PLC程序/02_PLC程序/.plc.json + DB1/OB1/common/conveyor/...
├── 02_PLC程序/程序文档/（6 份核心文档）
├── 03_HMI设计/
├── 04_现场调试/
├── 04_驱动器与设备/
├── 05_测试与验证/
├── 06_文档与交付/
├── 07_技术支持/
├── 08_备件管理/
├── 09_项目总结/
├── 10_知识库/
├── PRD/
├── .github/hooks/（Agent 会话钩子）
├── .trae/specs/
├── PM_SESSION_DJ-2026-005.md
└── .gitignore
```

**逐项差距**：

| 序号 | 项目 | 模板 | 实际 DJ-2026-005 | 严重度 |
|------|------|------|------------------|--------|
| 1 | .plc.json 位置 | 根级 + 02_PLC程序/通用ST程序及变量表/ | 仅 02_PLC程序/02_PLC程序/ | **严重** |
| 2 | PLC 程序目录名 | `通用ST程序及变量表` | `02_PLC程序`（嵌套） | 高 |
| 3 | 00_项目管理/ | ❌ 缺失 | ✅ 存在 | 高 |
| 4 | 01_需求与设计/ | ❌ 缺失 | ✅ 存在 | 高 |
| 5 | 04_变更管理/ 位置 | 根级 | 00_项目管理/04_变更管理/ | 高 |
| 6 | 04_驱动器与设备/ | ❌ 缺失 | ✅ 存在 | 中 |
| 7 | 05_测试与验证/ | ❌ 缺失 | ✅ 存在 | 中 |
| 8 | 06_文档与交付/ | ❌ 缺失 | ✅ 存在 | 中 |
| 9 | 07_技术支持/ | ❌ 缺失 | ✅ 存在 | 低 |
| 10 | 08_备件管理/ | ❌ 缺失 | ✅ 存在 | 低 |
| 11 | 09_项目总结/ | ❌ 缺失 | ✅ 存在 | 低 |
| 12 | 10_知识库/ | ❌ 缺失 | ✅ 存在 | 低 |
| 13 | DB1/ 目录 | ❌ 缺失 | ✅ 存在 | **高** |
| 14 | OB1/ 目录 | ❌ 缺失 | ✅ 存在 | **高** |
| 15 | common/conveyor/external/feeder/pickplace/ | ❌ 缺失 | ✅ 存在 | 中 |
| 16 | Test/ 目录 | ❌ 缺失 | ✅ 存在 | 中 |
| 17 | 程序文档/（6 份） | ❌ 缺失 | ✅ 存在 | 中 |
| 18 | 项目立项表 | ❌ 缺失 | ✅ 存在 | 高 |
| 19 | .github/hooks/ | ❌ 缺失 | ✅ 存在 | 中 |
| 20 | .gitignore | ❌ 缺失 | ✅ 存在 | 中 |
| 21 | GlobalVars.db | ❌ 缺失 | ✅ 存在 | **高** |
| 22 | 根级 .plc.json | ✅ 错误生成 | ❌ 不应存在 | **严重** |

#### 4.1.3 模板文档质量问题

| 文档 | 字符数（约） | 占位符数 | SubstanceChecker 结果 |
|------|------------|---------|---------------------|
| 需求分析文档_REQ.md.jinja | ~300 | 11 个"待定义" | WARN（字数不足）+ WARN（占位符） |
| 接口文档_INT.md.jinja | ~400 | 8 个"待定义" | WARN + WARN |
| 详细设计说明书_DSN.md.jinja | ~450 | 2 个"待补充" | WARN |
| 技术方案文档_TEC.md.jinja | ~450 | 7 个"待定义" | WARN + WARN |
| PM_SESSION.md.jinja | ~500 | 5 个"待填写" | WARN |

**结论**：所有模板生成的文档都会触发 SubstanceChecker 的 WARN，新建项目立即检查即报警。

### 4.2 初始化维度

#### 4.2.1 两条初始化路径

| 路径 | 命令 | 实现 | 问题 |
|------|------|------|------|
| 路径 1 | `plc init <ID> --name NAME` | [cli/plc/__init__.py:36-70](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/cli/plc/__init__.py) | 硬编码 "plc-standard"，无业务线校验，无 dry-run |
| 路径 2 | `project create --stack plc` | [cli/project.py:138-210](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/cli/project.py) | 通过 `get_template_name(stack)`，有业务线校验 + dry-run |

**关键问题**：两条路径功能重复，违反 DRY 原则，且 `plc init` 能力弱于 `project create`。

#### 4.2.2 创建后处理缺失

LSP-907 §4 新建项目检查清单合规性：

| 检查项 | 模板生成 | 创建后验证 | 状态 |
|--------|---------|-----------|------|
| .plc.json 含 name/description/version | ✅ | ❌ | ⚠️ |
| libraries 指向有效 SysLib | ✅ 硬编码 | ❌ | ⚠️ |
| 相对路径有效性 | ❌ | ❌ | ❌ |
| SysLib/timer/FB_TON.scl 可解析 | ❌ | ❌ | ❌ |
| 目录结构符合 §3.1 | ⚠️ 部分 | ❌ | ❌ |
| GlobalVars.db | ❌ | ❌ | ❌ |
| DB 同步 | ❌ | ❌ | ❌ |

### 4.3 创建维度

#### 4.3.1 创建流程问题

1. **无创建后验证**：创建完成后不运行 `PlcChecker.check_project()` 验证
2. **无 DB 同步**：创建后不调用 `ProjectService.sync_to_cache()`
3. **无 libraries 路径智能推断**：硬编码路径，对不同位置的项目错误
4. **无立项表生成**：不生成 `003_<项目编号>_项目立项表_PROJ.md`
5. **无 Agent 钩子配置**：不生成 `.github/hooks/`

### 4.4 编辑维度

#### 4.4.1 现状

`project edit` 命令主要编辑项目元数据（名称、描述、阶段、业务线），但：

1. **不支持编辑 .plc.json**：无法通过 CLI 编辑 libraries 字段
2. **不支持批量编辑**：无 `--batch` 选项
3. **无编辑后验证**：不检查 .plc.json 格式有效性

### 4.5 检查维度

#### 4.5.1 PlcChecker 实现分析

**已实现检查项**（[checker.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/plc/checker.py)）：
1. .plc.json 存在性 + 必填字段（L116-172）
2. PM_SESSION_*.md 存在性 + 命名匹配（L174-198）
3. PRD 目录 + 4 个标准文档存在性（L200-229）
4. 标准目录结构（L231-238）

#### 4.5.2 规范覆盖度矩阵

| 规范 | 总条款 | 已覆盖 | 部分覆盖 | 未覆盖 | 覆盖率 |
|------|--------|--------|---------|--------|--------|
| LSP-907（项目配置） | 10 | 2 | 3 | 5 | 20% |
| LSP-905（SCL 编程） | 6 | 0 | 0 | 6 | 0% |
| LSP-906（错误预防） | 6 | 0 | 0 | 6 | 0% |
| LSP-904（注释规范） | 1 | 0 | 0 | 1 | 0% |
| PLC-023（文档模板） | 1 | 0 | 0 | 1 | 0% |
| INT-815（接口模板） | 1 | 0 | 0 | 1 | 0% |
| **合计** | 25 | 2 | 3 | 20 | **8%** |

**关键缺失**：
- ❌ 不检查 SCL 代码（.scl 文件）的命名/语法/注释规范
- ❌ 不检查 FB_TON 调用规范（PT/ET 为 DINT、三段式调用）
- ❌ 不检查 libraries 路径有效性（只检查目录存在，不检查 SysLib 关键文件）
- ❌ 不检查 .plc-out 保护
- ❌ 不检查 launch.json 配置

#### 4.5.3 SubstanceChecker 问题（V2.0.1-B）

| 严重度 | 行号 | 问题 |
|--------|------|------|
| 严重 | L140 | `len(content)` 统计字符数非字数，中文 500 字符约 300 词 |
| 高 | L155 | 章节正则 `^##\s+` 要求 ## 后有空格，漏检 `##标题` |
| 高 | L176-180 | 占位符检查只报 WARN 不报 FAIL，与 PRD P0-002 要求"占位符>70% 报 FAIL"不符 |
| 中 | L24-33 | 占位符检查过于简单，不计算密度 |
| 中 | L170-182 | 未考虑代码块中的 TODO 注释会被误判 |

### 4.6 修复维度

#### 4.6.1 PlcRepairer 修复能力

| 修复场景 | 能力 | 说明 |
|---------|------|------|
| 缺少 .plc.json | ✅ | 但 libraries 路径硬编码错误 |
| .plc.json 缺字段 | ✅ | 补全 name/description/version |
| 缺少 PM_SESSION | ✅ | 创建最小骨架 |
| 缺少 PRD 目录/文档 | ✅ | 创建空目录 + 最小文档（触发实质化 WARN） |
| 缺少标准目录 | ⚠️ | 仅创建 STD_DIRS 中的 5 个，缺少 00_项目管理 等 |
| PRD 文档命名不规范 | ✅ | 重命名（需 --rename/--apply） |
| libraries 路径错误 | ❌ | 不修复 |
| SCL 代码不规范 | ❌ | 不检查不修复 |
| GlobalVars.db 缺失 | ❌ | 不创建 |
| launch.json 配置错误 | ❌ | 不检查不修复 |

#### 4.6.2 修复器关键问题

| 严重度 | 行号 | 问题 |
|--------|------|------|
| 严重 | [repairer.py:508](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/plc/repairer.py) | `_minimal_plc_json` 硬编码 `"../../../01_SharedLibraries/SysLib"`，对根级项目错误 |
| 高 | L66 | 访问 checker 私有方法 `_resolve_project_id`，破坏封装 |
| 高 | L410 | `_repair_rename` 通过正则解析消息文本提取文件名，极度脆弱 |
| 中 | L568-586 | `_minimal_prd_doc` 生成的文档过于简陋，触发实质化 WARN |

---

## 五、架构层面问题

### 5.1 CLI 层绕过 Service 层（C-3）

**设计意图**（[service.py:1-11](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/plc/service.py)）：
> "UI/CLI 层通过 PlcService 操作 PLC 项目，不直接访问 PlcChecker/PlcRepairer"

**实际实现**（[cli/plc/__init__.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/cli/plc/__init__.py)）：
- `cmd_check` (L83) 直接 `PlcChecker(app_ctx.workspace_root)`
- `cmd_repair` (L134) 直接 `PlcRepairer(app_ctx.workspace_root)`
- `cmd_standardize` (L158) 直接 `PlcRepairer(app_ctx.workspace_root)`
- `cmd_init` (L54) 直接 `TemplateService(app_ctx.templates_dir)`

**后果**：
- PlcService 的 `check(fix=True)` 自动修复能力无法通过 CLI 使用
- PlcService 的 `check_substance`（V2.0.1-B）无法通过 CLI 访问
- PlcService 成为只有 UI 层使用的"半死代码"
- 违反 [protocols.py:176-192](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/core/protocols.py) 定义的 PlcServiceProtocol 契约

### 5.2 STD_DIRS 与实际项目不符（H-1）

[plc/models.py:25-31](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/plc/models.py) 定义的 STD_DIRS：
```python
STD_DIRS = ["02_PLC程序", "03_HMI设计", "04_变更管理", "04_现场调试", "PRD"]
```

实际 DJ-2026-005 的标准目录（11 个）：
```
00_项目管理/、01_需求与设计/、02_PLC程序/、03_HMI设计/、04_现场调试/、
04_驱动器与设备/、05_测试与验证/、06_文档与交付/、07_技术支持/、
08_备件管理/、09_项目总结/、10_知识库/
```

**差距**：缺少 7 个标准目录，且 `04_变更管理` 位置错误（应在 `00_项目管理/` 下）。

---

## 六、测试覆盖分析

### 6.1 PLC 功能测试清单

| 测试文件 | 用例数 | 覆盖范围 |
|---------|--------|---------|
| [tests/plc/test_checker.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/tests/plc/test_checker.py) | 14 | PlcChecker 单元测试 |
| [tests/plc/test_repairer.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/tests/plc/test_repairer.py) | 14 | PlcRepairer 单元测试 |
| [tests/plc/test_service.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/tests/plc/test_service.py) | 6 | PlcService 封装测试 |
| [tests/cli/test_plc.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/tests/cli/test_plc.py) | 4 | PLC CLI 命令测试 |

### 6.2 测试关键问题

| 严重度 | 文件:行号 | 问题 |
|--------|---------|------|
| 严重 | test_plc.py | 无 `plc init` 命令测试 |
| 严重 | test_plc.py | 无 `plc repair` 命令测试 |
| 严重 | test_plc.py | 无 `plc standardize` 命令测试 |
| 高 | test_service.py:84,107 | 断言 `or True` 永远通过，测试无效 |
| 高 | - | 无端到端 PLC 项目创建测试（init → check → repair → check） |
| 中 | test_checker.py:52 | fixture 返回 tmp_path 而非项目目录 |

### 6.3 测试覆盖盲区

1. **端到端流程未测试**：`plc init` → `plc check` → `plc repair` → `plc check`
2. **模板生成正确性未测试**：未验证模板生成的项目能否通过 PlcChecker
3. **SubstanceChecker 边界测试缺失**：字数阈值边界（499/500/501）
4. **多项目工作空间测试不足**
5. **libraries 路径有效性测试缺失**

---

## 七、关键问题清单（按严重度排序）

### 7.1 Critical（6 项）

| ID | 问题 | 文件:行号 | 影响 |
|----|------|---------|------|
| C-1 | 模板在根级生成 .plc.json | templates/plc-standard/template/.plc.json.jinja | 违反 LSP-907 §3.1 |
| C-2 | _minimal_plc_json 硬编码 libraries 路径 | repairer.py:508 | 对根级项目错误 |
| C-3 | CLI 层完全绕过 PlcService 层 | cli/plc/__init__.py:83,134,158 | 分层架构形同虚设 |
| C-4 | SubstanceChecker 字数统计语义错误 | substance_checker.py:140 | len() 统计字符非字数 |
| C-5 | 模板生成的文档全部触发实质化 WARN | templates/plc-standard/template/PRD/*.jinja | 新建即报警 |
| C-6 | plc init/repair/standardize CLI 无测试 | tests/cli/test_plc.py | 命令无测试覆盖 |

### 7.2 Major（10 项）

| ID | 问题 | 文件:行号 | 影响 |
|----|------|---------|------|
| H-1 | STD_DIRS 与实际项目结构不符 | plc/models.py:25-31 | 缺少 7 个标准目录 |
| H-2 | plc init 与 project create --stack plc 功能重复 | cli/plc/__init__.py:36 + cli/project.py:138 | 违反 DRY |
| H-3 | 模板缺少 DB1/OB1/common 等业务子目录 | templates/plc-standard/template/02_PLC程序/ | 需手动补全 |
| H-4 | PlcRepairer 访问 checker 私有方法 | repairer.py:66 | 破坏封装 |
| H-5 | _repair_rename 通过正则解析消息文本 | repairer.py:410 | 极度脆弱 |
| H-6 | SubstanceChecker 章节正则要求 ## 后有空格 | substance_checker.py:155 | 漏检无空格标题 |
| H-7 | 占位符检查只报 WARN 不报 FAIL | substance_checker.py:176-180 | 与 PRD P0-002 不符 |
| H-8 | retrofit 命令只补 .copier-answers.yml | cli/project.py:336-343 | 不补全 PLC 标志文件 |
| H-9 | test_service.py 断言 or True 永远通过 | test_service.py:84,107 | 测试无效 |
| H-10 | libraries 路径只检查目录存在 | checker.py:165 | 无法发现指向错误目录 |

### 7.3 Minor（8 项）

| ID | 问题 | 文件:行号 |
|----|------|---------|
| M-1 | PRD 文档前缀匹配与 NAMING_RULES 不一致 | checker.py:220-228 |
| M-2 | REQUIRED_PLC_JSON_FIELDS 未含条件必填的 libraries | plc/models.py:42 |
| M-3 | ProjectType 枚举缺少 substance_check | models/enums.py:61 |
| M-4 | INT 文档错误声明 import_project 不存在 | INT.md:322 |
| M-5 | retrofit _commit: "HEAD" 非真实 commit | cli/project.py:337 |
| M-6 | 模板缺少 .gitignore | templates/plc-standard/template/ |
| M-7 | 模板缺少 GlobalVars.db | templates/plc-standard/template/ |
| M-8 | fixture 返回 tmp_path 而非项目目录 | test_checker.py:52 |

---

## 八、改进建议与路线图

### 8.1 三种项目模式的设计建议

基于用户确认的目标模式，建议重构模板为 3 套：

#### 模式 1: plc-shared-library（公共库）

**参考**: SysLib
**结构**:
```
{{library_name}}/
├── actuator/           # 执行器 FB
├── communication/      # 通信 FB
├── convert/            # 类型转换 FC
├── counter/            # 计数器 FB
├── edge/               # 边沿检测 FB
├── log/                # 日志 FC
├── pulse/              # 脉冲生成 FB
├── timer/              # 定时器 FB
├── types/              # 结构体定义 ST_*.scl
├── PRD/                # 库级文档（REQ/TEC/DSN/INT）
├── .github/hooks/      # Agent 钩子
├── .plc.json           # libraries: []
├── PM_SESSION_{{library_name}}.md
├── README.md           # 多平台兼容性指南
└── .gitignore
```

#### 模式 2: plc-test-suite（公共库验证）

**参考**: DJ-2026-000
**结构**:
```
{{project_id}}_{{project_name}}/
├── DB1/GlobalVars.db
├── FB{{xxx}}/{{FB_name}}.scl
├── OB1/OB1.scl
├── Test/*.scltest
├── PRD/（4 份标准文档）
├── .github/hooks/
├── .plc.json           # libraries: ["../01_SharedLibraries/SysLib"]
├── PM_SESSION_{{project_id}}.md
└── .gitignore
```

#### 模式 3: plc-standard-project（标准单机项目）

**参考**: DJ-2026-005（TPL-SINGLE-PLC-M001）
**结构**:
```
{{project_id}}_{{project_name}}/
├── 00_项目管理/
│   ├── 01_立项与需求/003_{{project_id}}_项目立项表_PROJ.md
│   └── 04_变更管理/
├── 01_需求与设计/13_软件方案/
├── 02_PLC程序/
│   └── 02_PLC程序/
│       ├── .plc.json   # libraries: ["../../../01_SharedLibraries/SysLib"]
│       ├── DB1/GlobalVars.db
│       ├── OB1/OB1.scl
│       ├── common/、conveyor/、external/、feeder/、pickplace/
│       ├── PRD/（FB 级文档）
│       └── Test/
├── 02_PLC程序/程序文档/（6 份核心文档）
├── 03_HMI设计/
├── 04_现场调试/
├── 04_驱动器与设备/
├── 05_测试与验证/
├── 06_文档与交付/
├── 07_技术支持/
├── 08_备件管理/
├── 09_项目总结/
├── 10_知识库/
├── PRD/（4 份标准文档）
├── .github/hooks/
├── .trae/specs/
├── PM_SESSION_{{project_id}}.md
└── .gitignore
```

### 8.2 六维度改进建议

#### 模板维度

1. **重构为 3 套模板**：plc-shared-library / plc-test-suite / plc-standard-project
2. **修正 .plc.json 位置**：删除根级 .plc.json.jinja，仅保留 02_PLC程序/子目录
3. **对齐实际项目目录结构**：参考 DJ-2026-005 添加 11 个标准目录
4. **添加 DB1/OB1/Test/ 等业务子目录骨架**：含 .gitkeep
5. **添加 GlobalVars.db 空文件**：满足 LSP-907 §4
6. **添加 .gitignore 模板**：忽略 .plc-out/、*.bak 等
7. **添加 .github/hooks/ 模板**：Agent 会话钩子
8. **充实 PRD 文档模板内容**：字数提升至 800+，减少占位符
9. **添加项目立项表模板**：基于 903_PLC工程项目立项表
10. **添加程序文档模板**：6 份核心文档（ARC/DSN/FLOW/VAR/IO/PLC）

#### 初始化维度

1. **统一 init 入口**：废弃 `plc init`，统一使用 `project create --stack plc`，或让 `plc init` 内部调用 `project create`
2. **添加创建后验证**：创建完成后自动运行 `PlcChecker.check_project()`
3. **添加 DB 同步**：创建后调用 `ProjectService.sync_to_cache()`
4. **添加 libraries 路径智能推断**：根据项目位置自动计算 SysLib 相对路径
5. **支持 --business-line 选项**：与 `project create` 对齐
6. **支持 --mode 选项**：选择 shared-library / test-suite / standard-project

#### 创建维度

1. **添加创建后钩子**：支持创建后自动执行 `plc check`、生成立项表
2. **支持 dry-run 详细预览**：显示将生成的完整目录树
3. **添加模板版本记录**：在 .copier-answers.yml 中记录模板版本

#### 编辑维度

1. **支持编辑 .plc.json**：`project edit` 应能编辑 libraries 字段
2. **支持批量编辑**：`project edit --batch`
3. **添加 edit 后验证**：编辑后自动检查 .plc.json 格式有效性

#### 检查维度

1. **CLI 层改用 PlcService**：`plc check` 调用 `PlcService.check()` 而非直接 `PlcChecker`
2. **添加 `plc check --substance` 选项**：暴露 SubstanceChecker 能力
3. **添加 `plc check --fix` 选项**：暴露 PlcService.check(fix=True) 能力
4. **扩展检查器覆盖 LSP-905/LSP-906**：添加 SCL 代码检查能力（扫描 .scl 文件）
5. **修正 STD_DIRS**：对齐 LSP-907 §3.1 和实际项目结构
6. **修正 SubstanceChecker 字数统计**：中文按字数，英文按词数；阈值调整为 800/1000
7. **修正章节正则**：`^##\s*` 允许无空格
8. **占位符密度检查**：实现 PRD P0-002 要求的"占位符>70% 报 FAIL"
9. **libraries 路径深度校验**：检查 SysLib/timer/FB_TON.scl 等关键文件

#### 修复维度

1. **修正 _minimal_plc_json libraries 路径**：根据项目位置动态计算
2. **重构 _repair_rename**：不通过正则解析消息，改为 checker 返回结构化信息
3. **扩展修复能力**：支持创建 GlobalVars.db、修正 libraries 路径、补全缺失的 00_项目管理 等目录
4. **retrofit 增强**：对 PLC 项目，retrofit 应调用 PlcRepairer 补全 .plc.json/PM_SESSION/PRD
5. **修复 PlcRepairer 访问 checker 私有方法**：将 `_resolve_project_id` 提升为公共方法
6. **添加修复后验证**：修复后自动运行 SubstanceChecker

### 8.3 建议的修复优先级

#### P0（阻塞落地，必须修复）

1. C-1: 修正 .plc.json 位置（删除根级 .plc.json.jinja）
2. C-2: 修正 _minimal_plc_json libraries 路径硬编码
3. C-3: CLI 层改用 PlcService
4. H-1: 修正 STD_DIRS 对齐实际项目
5. H-2: 统一 init 入口

#### P1（影响可用性）

1. C-4: 修正 SubstanceChecker 字数统计
2. C-5: 充实模板文档内容，避免触发实质化 WARN
3. H-3: 模板添加 DB1/OB1/Test 等业务子目录
4. H-7: 占位符检查实现 FAIL 级别
5. H-8: retrofit 增强 PLC 项目补全

#### P2（提升质量）

1. C-6: 补全 PLC CLI 命令测试
2. H-9: 修复 test_service.py 无效断言
3. 扩展 LSP-905/906 SCL 代码检查能力
4. 重构为 3 套模板（shared-library/test-suite/standard-project）

---

## 九、落地时间评估

### 9.1 当前可落地能力

| 能力 | 立即可用 | 说明 |
|------|---------|------|
| Python 项目管理 | ✅ | 完整可用 |
| 变更管理 | ✅ | 完整可用 |
| GUI 桌面应用 | ✅ | 可用（有 flaky 测试） |
| PLC 项目创建 | ⚠️ | 可创建但不合规，需手动补全 |
| PLC 项目检查 | ⚠️ | 仅覆盖 LSP-907 的 20% |
| PLC 项目修复 | ⚠️ | 能力有限，libraries 路径错误 |

### 9.2 落地里程碑建议

| 里程碑 | 内容 | 产出 |
|--------|------|------|
| M1: P0 修复 | 修复 C-1/C-2/C-3/H-1/H-2 | PLC 基础架构合规 |
| M2: 模板重构 | 重构为 3 套模板 + 充实内容 | 模板可生成合规项目 |
| M3: 检查器增强 | 扩展 LSP-905/906 覆盖 + SubstanceChecker 修复 | 检查覆盖度提升至 60%+ |
| M4: 测试补全 | 补全 CLI 测试 + 端到端测试 | 测试覆盖完整 |
| M5: V2.0.1 收尾 | 完成 B/D/E + 6 个 UI 测试阻塞 + mypy strict | V2.0.1 正式发布 |

**建议**：完成 M1+M2 后，PLC 专项功能可初步落地；完成 M3+M4 后，可正式发布 V2.1。

---

## 十、假设与决策

### 10.1 本次审查的假设

1. **任务范围**：仅审查报告，不改代码（用户明确确认）
2. **目标模式**：3 种项目模式（公共库/公共库验证/标准单机项目），用户明确确认
3. **SysLib 处理**：仅引用不复制（用户明确确认）
4. **参考基准**：以 DJ-2026-005（完整工程）+ DJ-2026-000（简化项目）+ SysLib（共享库）为参考
5. **规范依据**：LSP-905/906/907/904 + PLC-023 + INT-815

### 10.2 待用户决策的事项

1. **模板重构时机**：是立即重构 3 套模板，还是先修复 P0 问题再重构？
2. **SCL 代码检查优先级**：是优先扩展 LSP-905/906 覆盖，还是优先完善模板内容？
3. **旧 plc init 命令处理**：是废弃还是保留为 `project create --stack plc` 的别名？

---

## 十一、验证步骤（审查报告本身）

本审查报告基于以下验证：

1. **代码阅读**：完整阅读了 auto-pm 的 PLC 相关代码（cli/plc、plc/、templates/plc-standard/）
2. **规范对比**：对比了 LSP-905/906/907 规范条款与检查器实现
3. **项目对比**：逐项对比了模板与 DJ-2026-000/DJ-2026-005/SysLib 的结构
4. **测试分析**：分析了 tests/plc/ 和 tests/cli/test_plc.py 的覆盖情况
5. **文档核对**：核对了 PRD/INT/DSN/PM_SESSION 文档与代码的一致性

**审查覆盖的文件清单**（核心）：
- auto_pm/cli/plc/__init__.py
- auto_pm/plc/service.py / checker.py / repairer.py / substance_checker.py / models.py
- auto_pm/models/plc.py / enums.py
- auto_pm/cli/project.py
- auto_pm/core/template_service.py / project_service.py / protocols.py / constants.py
- templates/plc-standard/（全部文件）
- tests/plc/（全部测试文件）
- tests/cli/test_plc.py
- 00_项目基础信息/001_产品需求文档_PRD.md / 002_接口文档_INT.md
- 0100_PLC自动化/00_通用规范/PLC编程/905/906/907 规范
- 0100_PLC自动化/DJ-2026-000/ / DJ-2026-005/ / 01_SharedLibraries/SysLib/

---

**报告完成**。本审查覆盖了 auto-pm 项目的文档与代码深度解读、PLC 专项功能六维度审查（模板/初始化/创建/编辑/检查/修复）、关键问题清单（6 Critical + 10 Major + 8 Minor）、改进建议与路线图，以及三种项目模式的设计建议。
