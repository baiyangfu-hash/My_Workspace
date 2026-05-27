# 工作空间健康度整改实施计划

> 创建日期: 2026-05-27
> 状态: Phase 1-3 已执行，Phase 4 待执行
> 关联: 工作空间全面健康度审查报告

---

## 整改总览

| 优先级 | 问题数 | 预计涉及文件 | 核心目标 |
|--------|--------|-------------|---------|
| P0 立即整改 | 4 | ~15 | 恢复规范体系可信度 |
| P1 近期整改 | 4 | ~30 | 提升工具集成度与项目管理覆盖 |
| P2 定期治理 | 5 | ~80 | 文档卫生与长期可维护性 |

---

## Phase 1: P0 立即整改（恢复规范体系可信度）

### Task 1.1: 修复 CODE-220 文件名版本漂移

**问题**: 文件名为 `220_Python项目打包规范_DEV-V2.1.0.md`，注册表版本为 `V2.2.0`

**步骤**:
1. 读取当前文件内容，确认内部版本号
2. 若文件内容版本为 V2.2.0 → 重命名文件为 `220_Python项目打包规范_DEV-V2.2.0.md`
3. 若文件内容版本为 V2.1.0 → 更新注册表中 version 为 `V2.1.0`（以文件实际内容为准）
4. 更新 `spec_registry.json` 中 `CODE-220` 的 `canonical_path` 字段
5. 更新 `00_INDEX_全局规范索引_V2.0.0.md` 中的链接
6. 更新 `规范元数据汇总报告.md` 和 `规范元数据汇总报告.json` 中的对应条目

**涉及文件**:
- `01_Project自动化项目管理/00_通用规范/Python开发/220_Python项目打包规范_DEV-V2.1.0.md`（重命名）
- `00_Obsidian_Base全局规范文件仓库/spec_registry.json`（更新路径）
- `00_Obsidian_Base全局规范文件仓库/00_INDEX_全局规范索引_V2.0.0.md`（更新链接）
- `00_Obsidian_Base全局规范文件仓库/规范元数据汇总报告.md`（更新条目）
- `00_Obsidian_Base全局规范文件仓库/规范元数据汇总报告.json`（更新条目）

**验证**: 运行 `specmgr check -w <workspace>` 确认无版本漂移告警

---

### Task 1.2: 修复 PM-045 文件名版本漂移

**问题**: 文件名为 `045_变更管理流程执行指南_PM-V1.0.0.md`，注册表版本为 `V1.1.0`

**步骤**:
1. 读取当前文件内容，确认内部版本号
2. 若文件内容版本为 V1.1.0 → 重命名文件为 `045_变更管理流程执行指南_PM-V1.1.0.md`
3. 若文件内容版本为 V1.0.0 → 更新注册表中 version 为 `V1.0.0`
4. 同步更新 spec_registry.json、索引文件、元数据报告

**涉及文件**:
- `00_Obsidian_Base全局规范文件仓库/01_项目管理域/04_变更管理/045_变更管理流程执行指南_PM-V1.0.0.md`（重命名）
- 同 Task 1.1 的注册表/索引/报告文件

**验证**: 同 Task 1.1

---

### Task 1.3: PLC域6个规范文件名合规化

**问题**: PLC域8个规范中6个文件名缺少类型前缀和版本号

**步骤**:
1. 逐个读取6个文件，确认内部版本号与注册表一致
2. 按以下映射重命名文件：

| 当前文件名 | 目标文件名 |
|-----------|-----------|
| `903_定时器使用规范.md` | `903_定时器使用规范_LSP-V1.0.0.md` |
| `904_SCL注释规范.md` | `904_SCL注释规范_LSP-V1.1.0.md` |
| `905_SCL编程规范.md` | `905_SCL编程规范_LSP-V1.0.1.md` |
| `906_错误预防规则.md` | `906_错误预防规则_LSP-V1.0.0.md` |
| `907_项目配置规范.md` | `907_项目配置规范_LSP-V1.0.0.md` |
| `908_Siemens_Language_Support_使用指南.md` | `908_Siemens_Language_Support_使用指南_TOOL-V1.0.0.md` |

3. 更新 `spec_registry.json` 中所有6条的 `canonical_path`
4. 更新索引文件和元数据报告
5. 搜索并更新所有引用这些文件路径的文档（包括 plc-rules.md、project-rule.md 等）

**涉及文件**:
- `0100_PLC自动化/00_通用规范/PLC编程/` 下6个文件（重命名）
- `00_Obsidian_Base全局规范文件仓库/spec_registry.json`
- `00_Obsidian_Base全局规范文件仓库/00_INDEX_全局规范索引_V2.0.0.md`
- `00_Obsidian_Base全局规范文件仓库/规范元数据汇总报告.md`
- `00_Obsidian_Base全局规范文件仓库/规范元数据汇总报告.json`
- `0100_PLC自动化/.trae/rules/plc-rules.md`（可能引用旧路径）
- `.trae/rules/project-rule.md`（可能引用旧路径）

**验证**: 
- 运行 `specmgr check -w <workspace>` 确认无命名不合规告警
- 全文搜索旧文件名确认无残留引用

---

### Task 1.4: 为 SW-2026-004 创建 PM_SESSION

**问题**: SW-2026-004 是最大的工具项目，但缺少 PM_SESSION 会话管理文件

**步骤**:
1. 读取 SW-2026-004 的项目文档，提取项目定位、当前版本、里程碑信息
2. 读取最新交付清单（`02_发布说明/01_交付清单_DEL-V2.5.2.md`）确定当前版本
3. 按 PM_WORKFLOW Skill 模板创建 `PM_SESSION_SW-2026-004.md`
4. 填充以下关键信息：
   - project_id: SW-2026-004
   - project_name: Python项目管理工具
   - project_root: 绝对路径
   - current_focus: 当前迭代目标
   - milestone: 当前里程碑版本
   - artifacts_index: 已有文档索引

**涉及文件**:
- `01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/PM_SESSION_SW-2026-004.md`（新建）

**验证**: 确认 PM_SESSION 文件格式符合 PM_WORKFLOW Skill 规范

---

## Phase 2: P1 近期整改（提升工具集成度）

### Task 2.1: SW-2026-004 散装脚本归位（19个）

**问题**: 19个诊断/修复/测试脚本散落在项目根目录

**步骤**:

**A. 诊断脚本集成（4个）**:
1. 审查 `diagnose_rootpath.py`、`diagnose_deep.py`、`diagnose_library.py`、`diagnose_template_manager.py` 的功能
2. 将通用诊断逻辑提取为 `src/services/diagnostic_service.py` 的子命令或方法
3. 在主程序CLI中注册 `--diagnose` 选项
4. 删除原始散装脚本

**B. 修复脚本集成（3个）**:
1. 审查 `fix_category_id.py`、`repair_categories.py`、`repair_library_projects.py`
2. 将修复逻辑封装为 `src/services/repair_service.py`
3. 在CLI中注册 `--repair` 选项
4. 删除原始散装脚本

**C. 临时测试归位（5个）**:
1. 审查 `test_new_templates.py`、`test_refresh.py`、`test_templates.py`、`test_count_by_status.py`、`test_template_fix.py`
2. 有价值的测试 → 移入 `tests/` 目录并适配 pytest 规范
3. 一次性验证脚本 → 删除
4. 更新 `tests/` 目录的 `__init__.py`

**D. 验证/检查脚本（3个）**:
1. `verify_change_management_fix.py`、`check_templates.py`、`regression_test.py`
2. 通用验证逻辑 → 移入 `tests/`
3. 一次性验证 → 删除

**E. 构建/打包脚本（2个）**:
1. `build.py`、`package.py` → 移至 `scripts/` 目录（如不存在则创建）
2. 更新构建文档中的引用

**F. 旧目录清理**:
1. 确认 `01_主程序核心_code/` 下的 `diagnose_deep.py` 和 `_test_eplan_mech.py` 与主目录版本一致
2. 确认后删除整个 `01_主程序核心_code/` 目录

**涉及文件**: SW-2026-004 项目下约 19+2 个文件

**验证**: 项目根目录除 `main.py`、`config.py` 外无散装 .py 文件；`pytest` 可正常运行

---

### Task 2.2: SW-2026-005 散装脚本归位（6个）

**问题**: 6个散装脚本 + 1个旧目录残留

**步骤**:
1. `test_bug_fix_001.py` → 移入 `tests/` 或删除（一次性bug验证）
2. `test_ui_buttons.py` → 移入 `tests/`
3. `test_import.py` → 移入 `tests/` 或删除
4. `verify_modules.py` → 移入 `tests/` 或删除
5. `config.py`（根目录）→ 确认与 `src/core/config.py` 的关系，若重复则删除
6. `_verify_cleanup.py`（旧目录）→ 删除
7. 删除 `01_主程序核心_code/` 目录

**涉及文件**: SW-2026-005 项目下约 6+1 个文件

**验证**: 项目根目录整洁；`pytest` 可正常运行

---

### Task 2.3: SpecMgr 功能扩展规划

**问题**: SpecMgr 未覆盖诊断/修复功能，散装脚本中的能力未被工具化

**步骤**:
1. 调研 SW-2026-004 和 SW-2026-005 中诊断/修复脚本的功能清单
2. 设计 SpecMgr 新子命令：
   - `specmgr diagnose` — 工作空间诊断（路径、配置、结构检查）
   - `specmgr fix` — 自动修复（版本漂移、命名不合规、frontmatter缺失）
3. 编写 PRD/技术方案（按规范流程）
4. 迭代开发

**注意**: 此任务为规划阶段，实际开发需单独立项迭代

---

### Task 2.4: 为 SW-2026-001 创建 PM_SESSION

**问题**: SW-2026-001 缺少 PM_SESSION

**步骤**:
1. 读取项目立项表和需求文档
2. 按 PM_WORKFLOW 模板创建 `PM_SESSION_SW-2026-001.md`
3. 同时清理 `src/` 目录下的8个散装 `test_*.py`（移入 `tests/` 或删除）

**涉及文件**:
- `01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-001_PLC变量表解析工具/PM_SESSION_SW-2026-001.md`（新建）
- `src/` 下8个 test_*.py（归位或删除）

---

## Phase 3: P2 定期治理（文档卫生）

### Task 3.1: .trae/documents 计划文档清理

**问题**: 57个计划文档堆积

**步骤**:
1. 按项目分组审查 `.trae/documents/` 下29个活跃文档
2. 判断标准：
   - 对应版本已发布 → 归档至 `_archive/`
   - 内容已被规范/文档替代 → 删除
   - 仍为当前工作计划 → 保留
3. 对 `_archive/` 下28个文件：
   - 超过30天且无引用 → 删除
   - 有参考价值 → 保留但标注归档日期
4. 工作空间根 `.trae/documents/_archive/` 下40+文件同理处理

**预计保留**: 活跃文档 ≤ 10个，归档 ≤ 15个，删除 ≥ 30个

---

### Task 3.2: SW-2026-004 发布说明归档

**问题**: 20个发布说明堆积，PS1脚本混入

**步骤**:
1. 在 `02_发布说明/` 下创建 `_archive/` 目录
2. V2.4.x 系列的6个文件 → 移入 `_archive/`
3. `fix_project_complete.ps1` 和 `fix_project_names.ps1` → 移至 `scripts/`
4. 保留 V2.5.x 系列在当前目录

---

### Task 3.3: 多版本文档并存清理

**问题**: 多个项目存在旧版本文档与最新版并存

**步骤**:
1. SW-2026-004:
   - `01_项目总结报告_SUM-V1.0.3.md` → 归档，保留 `SUM-V1.1.0.md`
   - `全局规范一致性诊断报告_CHK-V1.0.6.md` → 归档，保留 `CHK-V1.1.0.md`
2. SW-2026-005:
   - `001_产品需求文档_PRD-V1.0.0.md` → 归档，保留 `PRD-V2.1.0.md`
   - `007_架构设计文档_ARCH-V2.0.0.md` → 归档，保留 `ARCH-V3.0.0.md`
   - `009_API接口文档_INT-V2.0.0.md` → 归档，保留 `INT-V3.0.0.md`
3. 每个项目下创建 `_archive/` 目录存放旧版本

---

### Task 3.4: 索引文件补充废弃规范展示

**问题**: 索引文件声称废弃/归档0个，实际有4个

**步骤**:
1. 更新 SpecMgr 的 `index_svc.py`，在索引中增加「已废弃/已归档」区块
2. 重新运行 `specmgr index -w <workspace>` 生成索引
3. 确认索引中展示 DEV-801、DEV-802、DEV-810、LSP-903-OLD

---

### Task 3.5: .trae/specs 归档清理

**问题**: 20个已完成的spec目录未清理

**步骤**:
1. 审查 `.trae/specs/_archive/` 下20个spec目录
2. 超过60天且任务已完成的 → 保留 `spec.md` 作为历史记录，删除 `checklist.md`/`tasks.md`
3. SW-2026-004 的15个spec目录同理处理

---

## 执行顺序与依赖关系

```
Phase 1 (P0) — 无外部依赖，可立即执行
  Task 1.1 (CODE-220版本修复)
  Task 1.2 (PM-045版本修复)     ─┐
  Task 1.3 (PLC域命名合规化)     ─┤─ 可并行
  Task 1.4 (SW-2026-004 PM_SESSION)─┘
  ↓
  运行 specmgr check 验证
  ↓
Phase 2 (P1) — 依赖 Phase 1 完成
  Task 2.1 (SW-2026-004 散装脚本) ── 最复杂，需仔细审查
  Task 2.2 (SW-2026-005 散装脚本) ─┐
  Task 2.4 (SW-2026-001 PM_SESSION)─┤─ 可并行
  Task 2.3 (SpecMgr扩展规划)      ─┘─ 仅规划，不实施
  ↓
Phase 3 (P2) — 可穿插执行
  Task 3.1~3.5 可并行，无严格依赖
```

## 风险与注意事项

1. **文件重命名后Git历史断裂**: 重命名规范文件时，Git可能无法自动追踪。建议每次重命名单独提交，提交信息标注原文件名
2. **散装脚本可能被其他脚本import**: 删除前需全文搜索引用关系
3. **spec_registry.json 是单一真源**: 所有修改必须同步更新，否则会引入新的不一致
4. **SW-2026-004 的散装脚本量大**: 建议分批处理，先处理诊断/修复类，再处理测试类
5. **旧目录 `01_主程序核心_code/`**: 必须先确认与 `01_主程序核心代码/` 无依赖关系再删除

---

## Phase 4: 待后续跟进（深度治理与工具化）

> Phase 1-3 已完成的核心整改：8个规范文件重命名、27个散装脚本删除、2个旧目录清理、143个过时文件清理、2个PM_SESSION创建、注册表/索引/rules同步更新。
> 以下为需要后续迭代完成的深度治理任务。

---

### Task 4.1: Git 原子性提交

**问题**: 本次整改涉及大量文件变更（重命名、删除、新建、更新），需要按逻辑分组提交，保证Git历史可追溯

**步骤**:
1. 提交1 — 规范文件重命名（8个文件 + spec_registry.json + frontmatter更新）
   ```
   fix(spec_registry): 修复CODE-220和PM-045版本漂移，PLC域6个规范文件名合规化

   - CODE-220: DEV-V2.1.0 → DEV-V2.2.0
   - PM-045: PM-V1.0.0 → PM-V1.1.0
   - PLC域903~908: 补充类型前缀和版本号
   - 同步更新spec_registry.json canonical_path
   - 同步更新各文件frontmatter canonical_path
   - 同步更新plc-rules.md和python-rules.md引用

   Ref: workspace-health-remediation
   ```
2. 提交2 — 散装脚本清理
   ```
   chore(SW-004): 清理15个散装脚本和旧目录01_主程序核心_code

   Ref: workspace-health-remediation
   ```
3. 提交3 — SW-2026-005 散装脚本清理
   ```
   chore(SW-005): 清理4个散装脚本和旧目录01_主程序核心_code

   Ref: workspace-health-remediation
   ```
4. 提交4 — SW-2026-001 散装测试清理
   ```
   chore(SW-001): 清理src/下8个散装test脚本

   Ref: workspace-health-remediation
   ```
5. 提交5 — PM_SESSION创建
   ```
   docs(SW-004): 新增PM_SESSION_SW-2026-004会话管理文件
   docs(SW-001): 新增PM_SESSION_SW-2026-001会话管理文件

   Ref: workspace-health-remediation
   ```
6. 提交6 — 文档归档与清理
   ```
   docs(release-notes): V2.4.x发布说明归档，PS1脚本移至scripts/
   docs(SW-004): 旧版本文档归档(SUM-V1.0.3, CHK-V1.0.6)
   docs(SW-005): 旧版本文档归档(PRD-V1.0.0, ARCH-V2.0.0, INT-V2.0.0)

   Ref: workspace-health-remediation
   ```
7. 提交7 — .trae文档清理
   ```
   chore(archive): 清理143个过时的.trae/documents和specs归档文件

   Ref: workspace-health-remediation
   ```

**验证**: `git log --oneline -7` 确认7次提交均符合commit message规范

---

### Task 4.2: SpecMgr 索引服务增强 — 废弃规范展示

**问题**: 索引文件 `00_INDEX_全局规范索引_V2.0.0.md` 声称废弃/归档0个，实际有4个（DEV-801, DEV-802, DEV-810, LSP-903-OLD）

**步骤**:
1. 读取 SpecMgr 的 `index_svc.py` 源码，定位索引生成逻辑
2. 在索引模板中增加「已废弃规范」和「已归档规范」区块：
   ```markdown
   ## 已废弃规范（Deprecated）
   > 以下规范已被替代，仅供历史参考

   | spec_id | 标题 | 替代规范 | 废弃日期 |
   |---------|------|---------|---------|
   | DEV-801 | PLC变量命名与功能块命名规范 | → DEV-801-V2 | 2026-04-25 |
   | ... | ... | ... | ... |

   ## 已归档规范（Archived）
   > 以下规范已从活跃目录移除

   | spec_id | 标题 | 归档路径 | 归档日期 |
   |---------|------|---------|---------|
   | ... | ... | ... | ... |
   ```
3. 修改 `index_svc.py` 中的过滤逻辑，将 `status: deprecated` 和 `status: archived` 的规范纳入索引
4. 运行 `specmgr index -w <workspace>` 重新生成索引
5. 确认索引中展示4个废弃/归档规范

**涉及文件**:
- `01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-006_规范管理工具/02_源代码/src/services/index_svc.py`
- `00_Obsidian_Base全局规范文件仓库/00_INDEX_全局规范索引_V2.0.0.md`（重新生成）

**验证**: 索引文件包含「已废弃规范」区块，展示4条记录

---

### Task 4.3: SpecMgr 新增 diagnose 子命令

**问题**: 散装脚本中的诊断能力（路径检查、配置检查、结构检查）未被工具化，未来还会产生新的散装脚本

**步骤**:
1. **调研阶段**（0.5天）:
   - 回顾已删除的4个诊断脚本功能：
     - `diagnose_rootpath.py` — 工作空间根路径检测
     - `diagnose_deep.py` — 深层配置/数据库诊断
     - `diagnose_library.py` — 规范库结构诊断
     - `diagnose_template_manager.py` — 模板管理器诊断
   - 提取通用诊断模式
2. **设计阶段**（0.5天）:
   - 设计CLI接口：
     ```
     specmgr diagnose -w <workspace>              # 全量诊断
     specmgr diagnose -w <workspace> --check path  # 仅路径检查
     specmgr diagnose -w <workspace> --check config # 仅配置检查
     specmgr diagnose -w <workspace> --check structure # 仅结构检查
     ```
   - 设计输出格式（表格/JSON）
3. **开发阶段**（1-2天）:
   - 在 `src/services/` 下新建 `diagnose_svc.py`
   - 在 `src/cli.py` 中注册 `diagnose` 子命令
   - 实现核心诊断逻辑
4. **测试阶段**（0.5天）:
   - 编写 pytest 测试用例
   - 在工作空间上运行验证

**涉及文件**:
- `SW-2026-006/02_源代码/src/services/diagnose_svc.py`（新建）
- `SW-2026-006/02_源代码/src/cli.py`（修改）
- `SW-2026-006/02_源代码/tests/test_diagnose.py`（新建）

**验收标准**:
- `specmgr diagnose -w <workspace>` 输出结构化诊断报告
- 覆盖路径/配置/结构三类检查
- 无散装诊断脚本残留

---

### Task 4.4: SpecMgr 新增 fix 子命令

**问题**: 版本漂移、命名不合规、frontmatter缺失等问题需要手动修复，效率低且易出错

**步骤**:
1. **调研阶段**（0.5天）:
   - 回顾已删除的3个修复脚本功能：
     - `fix_category_id.py` — 修复分类ID
     - `repair_categories.py` — 修复分类结构
     - `repair_library_projects.py` — 修复库项目关联
   - 结合本次整改中手动执行的修复操作（重命名、路径更新、frontmatter更新）
2. **设计阶段**（0.5天）:
   - 设计CLI接口：
     ```
     specmgr fix -w <workspace> --dry-run          # 预览修复项
     specmgr fix -w <workspace>                     # 执行修复
     specmgr fix -w <workspace> --fix version-drift # 仅修复版本漂移
     specmgr fix -w <workspace> --fix naming        # 仅修复命名不合规
     specmgr fix -w <workspace> --fix frontmatter   # 仅补全frontmatter
     specmgr fix -w <workspace> --fix path-sync     # 仅同步canonical_path
     ```
   - 设计安全机制：dry-run模式、备份机制、回滚能力
3. **开发阶段**（2-3天）:
   - 在 `src/services/` 下新建 `fix_svc.py`
   - 在 `src/cli.py` 中注册 `fix` 子命令
   - 实现核心修复逻辑
4. **测试阶段**（0.5天）:
   - 编写 pytest 测试用例
   - 在测试工作空间上验证修复效果

**涉及文件**:
- `SW-2026-006/02_源代码/src/services/fix_svc.py`（新建）
- `SW-2026-006/02_源代码/src/cli.py`（修改）
- `SW-2026-006/02_源代码/tests/test_fix.py`（新建）

**验收标准**:
- `specmgr fix --dry-run` 能检测到版本漂移/命名不合规/frontmatter缺失
- `specmgr fix` 能自动修复以上问题并同步更新注册表
- 修复前自动备份，支持 `--rollback`

---

### Task 4.5: SW-2026-004 构建/打包脚本归位

**问题**: `build.py` 和 `package.py` 仍留在 `01_主程序核心代码/` 根目录，应移至 `scripts/` 目录

**步骤**:
1. 确认 `build.py` 和 `package.py` 的调用方式（是否被 main.py 或 CI 引用）
2. 在 SW-2026-004 项目下创建 `scripts/` 目录（如不存在）
3. 移动 `build.py` 和 `package.py` 到 `scripts/`
4. 更新项目文档中的引用路径
5. 如果 `main.py` 或其他代码 import 了这两个脚本，更新 import 路径

**涉及文件**:
- `SW-2026-004/03_主程序/01_主程序核心代码/build.py` → `scripts/build.py`
- `SW-2026-004/03_主程序/01_主程序核心代码/package.py` → `scripts/package.py`

**验证**: 项目根目录除 `main.py` 外无散装 .py 文件

---

### Task 4.6: 规范元数据汇总报告重新生成

**问题**: 本次整改重命名了8个规范文件，但 `规范元数据汇总报告.md` 和 `规范元数据汇总报告.json` 尚未重新生成，仍包含旧路径

**步骤**:
1. 运行 `specmgr report -w <workspace> --format json` 重新生成 JSON 报告
2. 运行 `specmgr report -w <workspace>` 重新生成 Markdown 报告
3. 确认报告中8个重命名规范的路径已更新

**涉及文件**:
- `00_Obsidian_Base全局规范文件仓库/规范元数据汇总报告.json`（重新生成）
- `00_Obsidian_Base全局规范文件仓库/规范元数据汇总报告.md`（重新生成）

**验证**: 报告中搜索旧文件名确认无残留

---

### Task 4.7: 索引文件重新生成

**问题**: `00_INDEX_全局规范索引_V2.0.0.md` 中的文件链接仍指向旧文件名

**步骤**:
1. 先完成 Task 4.2（索引服务增强）
2. 运行 `specmgr index -w <workspace>` 重新生成索引
3. 确认索引中8个重命名规范的链接已更新
4. 确认索引中包含「已废弃规范」区块

**涉及文件**:
- `00_Obsidian_Base全局规范文件仓库/00_INDEX_全局规范索引_V2.0.0.md`（重新生成）

**验证**: 索引中搜索旧文件名确认无残留

---

### Task 4.8: SpecMgr check 命令验证

**问题**: 整改后需要验证规范体系是否健康

**步骤**:
1. 运行 `specmgr check -w <workspace>` 全量检查
2. 确认以下问题已修复：
   - ✅ 无版本漂移告警（CODE-220、PM-045已修复）
   - ✅ 无命名不合规告警（PLC域6个已修复）
   - ✅ 无 canonical_path 不一致告警
3. 记录任何新发现的问题

**验证**: `specmgr check` 输出0个严重告警

---

### Task 4.9: SW-2026-004 剩余 .trae/documents 活跃文档审查

**问题**: `.trae/documents/` 下仍有约29个活跃计划文档（SW-2026-004占14个），部分可能已过时

**步骤**:
1. 逐个审查 SW-2026-004 的14个活跃文档：
   - `v2_5_9_*` 系列 — 检查V2.5.9是否已发布，若已发布则归档
   - `v2_5_8_*` 系列 — 检查V2.5.8是否已发布，若已发布则归档
   - `v2_5_7_*` 系列 — 同上
   - `plan_*` 系列 — 检查计划是否已执行完毕
   - `crash_diagnosis_report.md` / `full_project_audit_report.md` — 一次性报告，归档
2. 判断标准：
   - 版本已发布 → 归档
   - 计划已执行 → 归档
   - 仍为当前工作 → 保留
3. 预计保留 ≤ 5个活跃文档

**涉及文件**: `SW-2026-004/.trae/documents/` 下约14个 .md 文件

---

### Task 4.10: PLC域规范分类归属调整

**问题**: TOOL-902（Git使用指南）放在PLC域但标注为跨域，TOOL-908（Siemens LSP使用指南）分类有歧义

**步骤**:
1. 评估 TOOL-902 是否应移至全局规范仓库的跨域通用目录：
   - 若Git使用指南适用于所有技术栈 → 移至 `00_Obsidian_Base全局规范文件仓库/03_执行过程/01_代码开发/02_工具使用规范/`
   - 若仅限PLC项目使用 → 保留在PLC域，更新注册表域为 `plc`
2. 评估 TOOL-908 的分类：
   - 当前注册表标注 `classification_issue: true`
   - 决定是归入 `plc` 域工具链分类还是 `cross-domain` 工具分类
3. 更新 spec_registry.json 中的 `domain` 和 `canonical_path`

**涉及文件**:
- `0100_PLC自动化/00_通用规范/PLC编程/902_Git使用指南.md`（可能移动）
- `00_Obsidian_Base全局规范文件仓库/spec_registry.json`（更新分类）

---

## Phase 4 执行顺序与依赖关系

```
Task 4.1 (Git提交) ── 最先执行，锁定Phase 1-3的变更
  ↓
Task 4.6 (元数据报告重新生成) ─┐
Task 4.8 (specmgr check验证)  ─┤─ 可并行
  ↓                             │
Task 4.2 (索引服务增强)        ─┘
  ↓
Task 4.7 (索引文件重新生成) ── 依赖4.2完成
  ↓
Task 4.5 (build/package归位) ─┐
Task 4.9 (活跃文档审查)      ─┤─ 可并行
Task 4.10 (分类归属调整)     ─┘
  ↓
Task 4.3 (specmgr diagnose) ── 独立迭代，需PRD
Task 4.4 (specmgr fix)      ── 独立迭代，需PRD
```

## Phase 4 预计工作量

| 任务 | 类型 | 复杂度 | 说明 |
|------|------|--------|------|
| 4.1 Git提交 | 运维 | 低 | 纯提交操作 |
| 4.2 索引服务增强 | 开发 | 中 | 修改SpecMgr源码 |
| 4.3 diagnose子命令 | 开发 | 高 | 需PRD+设计+开发+测试 |
| 4.4 fix子命令 | 开发 | 高 | 需PRD+设计+开发+测试 |
| 4.5 build/package归位 | 运维 | 低 | 移动文件+更新引用 |
| 4.6 元数据报告重新生成 | 运维 | 低 | 运行specmgr report |
| 4.7 索引文件重新生成 | 运维 | 低 | 依赖4.2完成后运行 |
| 4.8 specmgr check验证 | 运维 | 低 | 运行验证命令 |
| 4.9 活跃文档审查 | 运维 | 中 | 需逐个判断 |
| 4.10 分类归属调整 | 运维 | 中 | 需决策+移动+更新 |

**建议执行节奏**:
- **本周内**: 4.1 → 4.6 → 4.8 → 4.5 → 4.9 → 4.10（运维类，低风险）
- **下周**: 4.2 → 4.7（索引增强，中风险）
- **下个迭代**: 4.3 → 4.4（新功能开发，需单独立项）
