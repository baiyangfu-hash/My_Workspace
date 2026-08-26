# process_gates.md — 过程质量门禁规程

> 本文档是 pm-workflow 的按需参考文档，仅在执行 Bug 诊断、变更闭环或 retrofit 时读取。

## 1. Bug 诊断强制流程（变更/缺陷模式专用）

**顺序执行，禁止跳过：**

1. **完整证据获取**：测试失败必须用 `--tb=long` 获取完整 traceback；禁止用 `--tb=no`
2. **诊断脚本先行**：形成假设后，用 `python -c "..."` 最小脚本验证，禁止"读代码→推测→直接修复"
3. **测试 vs 生产分离**：先检查 fixture 是否完整（PM_SESSION_*.md / .plc.json 标志文件），再怀疑生产代码
4. **未验证禁止回写**：诊断结论未经运行时验证，禁止写入 PM_SESSION §8/§9

## 2. dogfooding 闭环门禁（CHG 流转到 closed 前必做）

**CHG 章节完整性**（12 章节全部非空）：
§5变更前后 / §6.1五大约束 / §6.2跨领域 / §6.3传播链 / §7实施计划 / §8.1审批流程 / §8.2审批结论 / §9实施记录 / §10.1验证清单 / §10.2跨领域验证 / §10.3验证结论 / §11版本说明 / §12附录

**状态流转合法性**（严格 9 步顺序）：
`draft → submitted → under_review → approved → implementing → pending_acceptance → accepting → completed → closed`

`accepting → closed` **非法**，必须经 `completed`。

**门禁实测强制检查**（回写 §3 前必做）：
```powershell
# 运行以下命令并记录真实输出，禁止凭记忆声明"全绿"
ruff check auto_pm/
mypy auto_pm/
pytest --no-cov -q
```

## 3. retrofit 模式（先实施后补单）

**适用场景**：紧急修复（P0 Bug）、历史遗漏补单、零代码改动的文档补单

```powershell
python -m auto_pm -w "<工作空间根>" change create --retrofit \
  --pid <项目ID> --domain <D> --nature <N> --scope <S>
```

**特点**：变更单直接创建为 closed 状态，台账自动补建，仍需填写 §5-§12。

**注意**：retrofit 是例外流程，不应成为常态。每次补单后必须执行 `ledger reconcile`。

## 4. 审查报告验证规则（收到外部 AI 审查报告时）

| 声明类型 | 验证方式 |
|:---|:---|
| 门禁声明（ruff/mypy/pytest 结果） | 必须运行时实测 |
| 文件存在性声明 | 必须用工具验证 |
| 代码行为声明 | 必须读源码验证 |

- ✅ 已验证为真 / ❌ 已验证为假 / ⚠️ 部分失真
- **禁止**直接采信外部审查报告结论进行修复，必须先验证。
