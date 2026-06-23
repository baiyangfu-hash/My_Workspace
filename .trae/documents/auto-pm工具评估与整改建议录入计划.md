# auto-pm 工具评估与整改建议录入计划

## 任务背景

以电气工程师+项目经理的双重身份，使用 `auto-pm`（SW-2026-008 v0.2.1）工具实际管理 `0100_PLC自动化` 项目库，基于真实使用体验提出工具改进建议，并将建议录入到工具自身的 `09_整改项` 目录。

**约束**：不修改已有项目，仅通过工具新建/复制项目来测试工具能力边界，测试后需检查新建项目。

---

## 当前状态分析（Phase 1 探索 + 只读体验结论）

### 工具能力概览
- 入口：`python -m auto_pm -w <workspace> <subcommand>`（venv 内）
- 6 个子命令组：project / plc / python / change / template / gui
- PLC 检查遵循 LSP-907 规范，3 套 PLC 模板（standard-project / shared-library / test-suite）
- 工作空间现有 11 个项目被识别

### 已通过只读命令发现的问题（7 项）

| # | 问题 | 严重度 | 复现 |
|---|------|--------|------|
| P1 | `plc check --all` 未按技术栈过滤，把 6 个 Python 项目（SW-2026-001/004/005/006/007/008）当 PLC 检查，全部 fail=14 | 高 | `plc check --all` |
| P2 | 项目重复识别：DJ-2026-005 同时被 `plc_json` 和 `pm_session` 两个来源识别为两条记录 | 高 | `project list` |
| P3 | `project show DJ-2026-005` 来源优先级错误：返回元数据缺失的 pm_session 来源（stack=unknown），而非元数据完整的 plc_json 来源 | 高 | `project show DJ-2026-005` |
| P4 | `change list DJ-2026-005` 报"项目不存在"，但 `project list` 显示存在 —— ChangeService 与 ProjectService 项目查找逻辑不一致 | 高 | `change list DJ-2026-005` |
| P5 | PlcChecker 只在项目根目录查 `.plc.json`，不查子目录；DJ-2026-005 的 `.plc.json` 在 `02_PLC程序\02_PLC程序\` 嵌套目录，被误报"缺少 .plc.json" | 高 | `plc check DJ-2026-005` |
| P6 | SysLib 是 shared-library，却被当 standard 类型检查，要求 00_项目管理~10_知识库 等标准项目目录，导致 fail=12 | 中 | `plc check SysLib` |
| P7 | venv 激活后 `auto-pm` 命令仍指向全局 Python（`C:\Users\fubai\AppData\Local\Programs\Python\Python311\Scripts\auto-pm.exe`），需用 `python -m auto_pm` 或完整路径调用 | 中 | 激活 venv 后 `auto-pm --version` |

### 需通过写操作验证的问题（待测试）
- 新建项目能否通过 `plc check`（即模板生成的骨架是否合规）
- `plc repair` 对新建项目的修复行为
- `plc standardize` 的命名标准化效果
- `change create` 变更单创建流程是否顺畅
- `project retrofit` 补全元数据的效果
- 新建项目的实际文件结构是否符合 LSP-907

---

## 执行步骤

### 步骤 1：新建 standard-project 模式 PLC 测试项目
**目的**：测试标准项目模板生成 + 验证骨架合规性

```
python -m auto_pm -w <workspace> project create \
  --stack plc --mode standard-project \
  --id DJ-2026-099 --name "auto-pm测试标准项目" \
  --desc "用于评估auto-pm工具的测试项目" --business-line DJ
```

**检查项**：
- 创建是否成功，生成的目录结构
- `.copier-answers.yml` / `.plc.json` / `PM_SESSION_*.md` 是否生成
- `plc check DJ-2026-099` 是否全 PASS
- `project show DJ-2026-099` 元数据是否完整
- `project list` 是否正确识别（不重复）

### 步骤 2：新建 shared-library 模式 PLC 测试项目
**目的**：测试共享库模板 + 验证 P6（SysLib 类型识别问题）是否为通病

```
python -m auto_pm -w <workspace> project create \
  --stack plc --mode shared-library \
  --id DJ-2026-098 --name "auto-pm测试共享库" \
  --desc "用于评估shared-library模板的测试项目" --business-line DJ
```

**检查项**：
- 共享库模板生成的目录结构（是否包含 actuator/timer/counter 等模块）
- `plc check DJ-2026-098` 是否按 shared-library 类型检查（而非 standard）
- 对比 SysLib 的检查结果，确认 P6 是否为类型识别通病

### 步骤 3：新建 test-suite 模式 PLC 测试项目
**目的**：测试测试套件模板

```
python -m auto_pm -w <workspace> project create \
  --stack plc --mode test-suite \
  --id DJ-2026-097 --name "auto-pm测试套件项目" \
  --desc "用于评估test-suite模板的测试项目" --business-line DJ
```

**检查项**：
- test-suite 模板生成的结构
- `plc check` 结果

### 步骤 4：对新建项目执行 plc repair 和 plc standardize
**目的**：测试修复和标准化能力

```
python -m auto_pm -w <workspace> plc repair DJ-2026-099 --dry-run
python -m auto_pm -w <workspace> plc standardize DJ-2026-099
python -m auto_pm -w <workspace> plc standardize DJ-2026-099 --apply
```

**检查项**：
- dry-run 预览输出是否清晰
- standardize 预览 vs apply 效果
- 修复后 `plc check` 是否仍 PASS

### 步骤 5：测试变更管理流程
**目的**：验证 P4（change list 项目查找问题）+ 测试完整变更流程

```
python -m auto_pm -w <workspace> change create \
  --pid DJ-2026-099 --domain PLC --nature REQ \
  --scope MODULE --applicant "电气工程师" \
  --background "测试变更管理流程" --necessity "验证auto-pm变更管理能力"
python -m auto_pm -w <workspace> change list DJ-2026-099
python -m auto_pm -w <workspace> change transition <CHG-NUM> --to submitted
```

**检查项**：
- 变更单是否成功创建（生成 CHG-*.md + 台帐更新）
- `change list DJ-2026-099` 是否能正常列出（对比 P4 的 DJ-2026-005 问题）
- 状态流转是否顺畅

### 步骤 6：测试 project retrofit 和 project edit
**目的**：测试元数据补全和编辑能力

```
python -m auto_pm -w <workspace> project retrofit DJ-2026-099
python -m auto_pm -w <workspace> project edit DJ-2026-099 --phase developing --version 1.0.0
python -m auto_pm -w <workspace> project show DJ-2026-099
```

**检查项**：
- retrofit 是否补全 `.copier-answers.yml`
- edit 是否正确更新 phase/version
- show 是否反映最新元数据

### 步骤 7：检查新建项目的实际文件结构
**目的**：验证模板生成内容是否符合 LSP-907 规范

对 DJ-2026-099 / DJ-2026-098 / DJ-2026-097 三个新建项目：
- 用 LS/Read 检查目录结构和关键文件内容
- 对比 907 规范要求，记录偏差
- 检查 `.plc.json` 字段完整性
- 检查 PRD 文档是否为空壳/占位符

### 步骤 8：清理测试项目
**目的**：测试 project delete + 保持工作空间整洁

```
python -m auto_pm -w <workspace> project delete DJ-2026-099 --confirm
python -m auto_pm -w <workspace> project delete DJ-2026-098 --confirm
python -m auto_pm -w <workspace> project delete DJ-2026-097 --confirm
```

**检查项**：
- delete 是否干净（目录、DB缓存是否同步删除）
- 删除后 `project list` 是否不再显示

### 步骤 9：整理建议并录入 09_整改项
**目的**：将所有发现录入工具自身的整改流程

**录入位置**：`01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具\09_整改项\`

**录入文件**：`V0.2.1-电气工程师评估整改清单.md`（参考现有 `V2.0-GUI-验证整改清单.md` 格式）

**内容结构**：
1. 评估背景与方法（角色、测试范围、测试命令）
2. 问题清单（按严重度分级：Bug / 体验问题 / 功能增强建议）
   - 每项含：编号、问题描述、复现步骤、期望行为、实际行为、严重度、建议修复方向
3. 亮点（工具做得好的地方，客观评价）
4. 优先级建议（P0/P1/P2）

---

## 假设与决策

1. **测试项目编号**：使用 DJ-2026-099 / 098 / 097 作为临时测试项目，避免与现有项目冲突，测试后删除
2. **不修改已有项目**：严格约束，所有写操作仅针对新建的测试项目
3. **venv 调用方式**：统一使用 `<venv>\Scripts\python.exe -m auto_pm` 方式调用，规避 P7
4. **建议录入格式**：参考现有 `09_整改项` 的 Markdown 格式，保持风格一致
5. **评估视角**：以电气工程师（PLC技术栈使用者）+ 项目经理（项目管理流程使用者）双重身份评估

---

## 验证步骤

1. **步骤 1-3 验证**：新建项目后 `plc check <ID>` 应全 PASS（证明模板合规）；`project list` 无重复
2. **步骤 4 验证**：repair/standardize 后 `plc check` 仍 PASS，无破坏性变更
3. **步骤 5 验证**：change create 成功生成文件，change list 正常列出（验证 P4 在新项目上是否复现）
4. **步骤 6 验证**：retrofit/edit 后 `project show` 元数据完整
5. **步骤 7 验证**：新建项目结构符合 LSP-907，记录任何偏差
6. **步骤 8 验证**：delete 后 `project list` 不再显示测试项目，文件系统干净
7. **步骤 9 验证**：整改清单文件已创建，内容完整，格式与现有文档一致

---

## 预期交付物

1. 3 个新建测试项目的完整生命周期测试结果（创建→检查→修复→变更→删除）
2. `09_整改项/V0.2.1-电气工程师评估整改清单.md` —— 结构化的问题与建议清单
3. 对话中向用户汇报核心发现和建议优先级
