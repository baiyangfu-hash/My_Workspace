# 技能协同通用规则（fullstack-engineer / plc-electrical-engineer 共享）

> **来源**：CHG-SCPT-2026-140 技能架构重构（2026-07-24）。pm-workflow 作为驾驶舱唯一入口和统筹者，fullstack/plc 变纯执行者；通用规则统一在此文件定义，避免 43% 重复内容。

## 1. Bug 诊断前置纪律

测试失败或遇到 bug 时，**禁止**凭代码阅读直接下结论，必须按以下顺序执行：

1. **完整证据获取**：
   - 测试失败必须用 `--tb=long`（或至少 `--tb=short`）获取完整 traceback
   - **禁止**用 `--tb=no` 隐藏错误详情
   - 必须读取完整的 WARNING/ERROR 日志行，不可只看断言失败信息

2. **诊断脚本先行**：
   - 读代码形成的假设，**必须**用最小诊断脚本（`python -c "..."`）验证后才能下结论
   - 诊断脚本应直接调用被测函数，打印实际返回值
   - 禁止"读了代码 → 推测根因 → 直接输出修复计划"的跳跃

3. **测试问题 vs 生产问题分离**：
   - 测试失败时，**先检查 fixture 是否完整**（项目标志文件、路径结构、mock 配置）
   - 再怀疑生产代码
   - 特别警惕"假通过"：`if x is not None:` 类条件断言会掩盖 fixture 缺陷

4. **fixture 健康检查清单**（测试失败时先查 fixture，再查生产代码）：
   - fixture 是否创建了项目标志文件？（PM_SESSION_*.md / .copier-answers.yml / .plc.json）
   - fixture 的路径结构是否与生产环境一致？（如 02_PLC程序/PLC_ST/ 目录层级）
   - fixture 的 mock 配置是否返回非 None 值？（打印 mock.return_value 确认）
   - 测试中是否有 `if x is not None:` 类条件断言？（改为 `assert x is not None` + `assert x.字段 == 期望值`）
   - fixture 的 scope 是否合理？（session 级 fixture 修改后会影响后续测试）

   **条件断言检测规则**（以下模式视为"假通过风险"，必须改为无条件断言）：
   - `if result is not None: assert ...` → `assert result is not None` + `assert result.xxx`
   - `if cr: assert ...` → `assert cr is not None` + `assert cr.xxx`
   - `try: assert ... except AssertionError: pass` → 删除 try/except，直接 assert

5. **未验证禁止回写**：
   - 诊断结论未经运行时验证，**禁止**写入 PM_SESSION §8/§9
   - 必须标注"已验证"或"待验证"，未验证的结论只能放在 `open_questions`

## 2. dogfooding 闭环质量门禁（变更/缺陷模式专用）

当走 dogfooding 闭环（CHG-*.md 状态流转到 closed）时，**必须**校验：

1. **CHG 章节完整性校验**：12 章节非空（§5 变更前后 / §6.1 五大约束 / §6.2 跨领域 / §6.3 传播链 / §7 实施计划 / §8.1 审批流程 / §8.2 审批结论 / §9 实施记录 / §10.1 验证项清单 / §10.2 跨领域联动验证 / §10.3 验证结论 / §11 版本详细变更说明 / §12 附录）
2. **闭环证据完整性**：代码 commit hash / 测试通过数 / 静态门禁结果 / 真实端到端验证
3. **状态流转合法性**：9 步流转顺序 `draft → submitted → under_review → approved → implementing → pending_acceptance → accepting → completed → closed`；`accepting → closed` 非法，必须经 `completed`
4. **`--verification-conclusion`** 必须包含"通过"且不包含"不通过"，否则流转到 completed 失败
5. **禁止**用 `--allow-partial-verification` 绕过章节完整性检查

## 3. 真源一致性前置校验（同步回 PM_SESSION 前必做）

1. **版本号一致性**：pyproject.toml == CHANGELOG 最新条目 == PM_SESSION §2 Current Focus == PM_SESSION §8 Handoff Notes
2. **测试数一致性**：PM_SESSION §3 Status Summary 测试通过数 == 实际 pytest 结果
3. **文档索引有效性**：PM_SESSION §4 Artifacts Index 中所有路径实际存在；无带版本号后缀的文件引用
4. **验证状态标注**：§8 Handoff Notes 诊断结论必须标注 `[已验证]` 或 `[待验证]`；未验证结论只能放在 `open_questions`
5. **读取时双向校验**：未标注验证状态 = 待验证 = 不可作为决策依据

## 4. 门禁实测强制检查（回写 PM_SESSION §3 前必做）

回写 §3 spec_compliance 或 §6 声明门禁状态前，**必须**实际运行并记录真实输出：

1. `ruff check auto_pm/`（或对应项目源码目录）— 记录 error 数
2. `mypy auto_pm/` — 记录 error 数和 source files 数
3. `pytest --no-cov -q`（或对应测试目录）— 记录 passed/failed/skipped 数

**禁止**基于以下来源声明门禁状态：上次审查报告的声明 / 代码阅读推断 / AI 记忆中的历史数据。

**例外**：纯文档/注释改动且无代码逻辑变更时，可只运行 ruff（mypy/pytest 跳过），但必须在 §3 标注"本次为文档改动，仅运行 ruff"。

## 5. 台账对账检查（每次 CHG 闭环后必做）

CHG 状态流转到 closed 后，**必须**执行：

```powershell
auto-pm -w "<工作空间根>" ledger reconcile <项目ID>
```

- 缺失 0 / 孤儿 0 / 状态不一致 0 → 正常，继续
- 有差异 → **必须修复后才能进入下一个 CHG**

**全量对账时机**：每个迭代结束时（版本号升级前），执行 `ledger reconcile <项目ID> --auto-fix`。

## 6. 审查报告验证模式（收到外部 AI 审查报告时触发）

外部审查报告（Claude/deepseek/其他 AI 产出）中的每一项声明，**必须**按以下分类验证：

| 声明类型 | 验证方式 |
|----------|----------|
| 门禁声明（ruff/mypy/pytest 结果） | 必须运行时实测（见 §4） |
| 文件存在性声明（"文件 X 不存在"/"文件 Y 有 Z 行"） | 必须用 Glob/Read 验证 |
| 代码行为声明（"函数 X 做了 Y"） | 必须 Read 源码验证 |
| 依赖声明（"pyproject.toml 包含 X 依赖"） | 必须 Read pyproject.toml 验证 |

**验证结果标注**：✅ 已验证为真 / ❌ 已验证为假（失真）/ ⚠️ 部分失真（声明部分正确）

**失真度记录**：验证完成后，在 PM_SESSION §6 记录审查报告失真度（严重失真 X% + 部分失真 Y% + 仍真实存在 Z%）。

## 7. retrofit 模式（先实施后补单）

**适用场景**：紧急修复（P0 Bug 需立即修复）/ 历史遗漏（发现已有提交缺变更单）/ 架构文档化（零代码改动的文档/注释补单）

**操作方式**：
```powershell
auto-pm -w "<工作空间根>" change create --retrofit --pid <项目ID> --domain <D> --nature <N> --scope <S> --applicant <A> --background <B> --necessity <N>
```

**特点**：变更单直接创建为 closed 状态（跳过 9 步状态流转）/ 台账自动补建 / 仍需填写 §5-§12 完整章节 / §9 实施记录填写实际已完成的变更内容。

**注意**：retrofit 是**例外流程**，不应成为常态；每个 retrofit 补单后必须执行 `ledger reconcile` 确认台账一致；若 retrofit 补单数量超过总 CHG 的 20%，需反思流程是否前置不足。

## 8. 文件命名规范（强制）

项目文档文件名（.md/.html 等）**禁止**追加版本号后缀：

- **禁止**：`GUI原型设计-V2.0.md`、`V2.0-全功能自动化测试计划.md`、`PRD_V0.5.0.md`
- **正确**：`GUI原型设计.md`（版本通过 frontmatter 或正文标题标识）、`PRD.md`
- 版本演进通过文档头部 frontmatter（`version: "V2.1"`）或正文标题（`# GUI 原型设计 V2.1`）标识

**例外**：`00_项目管理/03_执行过程/` 下的历史执行过程文件可保留日期前缀（如 `2026-06-29_V0.4.2-未来6周滚动计划.md`）；`09_整改项/archive/` 下的归档文件保留原名。

## 9. 文件写入策略（VS Code buffer staleness）

1. **写入时**：**必须**用 Edit/Write 工具（通过 VS Code API 修改可正确同步缓冲区）；**禁止**用 Python 脚本直接写磁盘修改项目文件（`Path.write_text()` 绕过 VS Code 文件监听，导致编辑器缓冲区陈旧、用户保存时冲突）
2. **Edit 失败处理**：若 Edit 工具 `old_string` 不匹配（因缓存），先 Read 重新读取最新内容，再重试 Edit；若仍失败用 Write 工具整体覆盖
3. **降级方案**：仅当 Edit/Write 工具均连续失败时，才可用 Python 脚本写入，但**必须立即提醒用户**"文件已被外部脚本修改，请关闭后重新打开"

## 10. PM_SESSION 双层结构归档规则

PM_SESSION 主文件保持 ≤150 行，超过即触发归档到历史目录 `00_项目管理/06_PM_SESSION历史/YYYY-MM-DD_Vx.x.x.md`。

**归档触发机制（自动化，不走 CHG 闭环）**：
- **版本发布时归档**：每次版本号升级（pyproject.toml 版本号变化），将本轮迭代的 §5/§6/§8 完整记录归档
- **主文件超 150 行时归档**：将早期 §3 completed/§5/§6/§8 条目归档到历史目录，主文件只保留快照
- **不创建 CHG**：归档是基础设施维护操作，不是功能变更，**不需要**走 dogfooding 闭环

## 11. 引用规则

本文件为通用规则单一真源。各执行者技能（fullstack-engineer / plc-electrical-engineer）通过相对路径引用本文件，避免重复维护。

**版本演进**：本文件由 pm-workflow 维护。修改本文件需创建 CHG-SCPT 变更单挂靠 SW-2026-008 项目（遵循 [CST-SKILL-001] 约束）。

**冲突处理**：当本文件与具体技能 SKILL.md 冲突时，以本文件为准（本文件为通用规则单一真源）；当本文件与项目级规则冲突时，以项目级规则为准。
