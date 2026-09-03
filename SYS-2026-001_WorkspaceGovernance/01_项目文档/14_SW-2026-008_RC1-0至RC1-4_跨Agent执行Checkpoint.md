# SW-2026-008 RC1-0 至 RC1-12 收口 Checkpoint

> 状态：`TECHNICAL_CLOSURE_COMPLETE`。本文件是可独立验证的执行断点，不替代 PM_SESSION、CHG 或 ledger。
>
> RC1-0 至 RC1-11 已 PASS。RC1-12 的技术验收已于 `2026-09-03T14:34:45.3512749Z` 获用户通过，Git 提交决定仍保留给用户，故 RC1-12 为 `IN_PROGRESS`，不得自动提交。

## 1. 项目与范围

- 项目：`SW-2026-008` 驾驶舱强制闭环，运行真源为 `00_Infrastructure/auto_pm`。
- RC1 目标：让 PM resume、项目事实、execution lifecycle 和 PM 收口具备可复核、跨 AI 中立、不可伪造的闭环。
- 已批准并实施范围：C1 事实包/只读预检、C1R/C1S `pm-resume.v1`、C2a handoff lifecycle、RC1 质量基线、四份 result 的正式消费与 PM 落账。
- 明确未实施范围：C3 至 C7、业务 PLC/HMI、Obsidian 真源、全仓格式化、无依据全局 ignore、自动 Git commit。

## 2. 完整 WBS

| WBS | 工作包目标 | 完成标准 | 状态 | 已有证据 |
|---|---|---|---|---|
| RC1-0 | 冻结 Git、控制面、门禁和运行态基线。 | 分支、HEAD、工作树、resume、handoff 已记录。 | PASS | §3、§6。 |
| RC1-1 | 审计增量归属与禁止范围。 | 变更 owner/目的明确，无用户无关修改被覆盖。 | PASS | §3、§4。 |
| RC1-2 | 收敛 Pytest 基线。 | `pytest --no-cov -q` Exit Code 0。 | PASS | §5。 |
| RC1-3 | 收敛 Ruff 基线。 | `ruff check auto_pm tests` Exit Code 0。 | PASS | §5。 |
| RC1-4 | 收敛 Mypy 基线。 | `mypy auto_pm` Exit Code 0。 | PASS | §5。 |
| RC1-5 | Dogfood `pm-resume.v1`。 | 事实、预算、read_set 与拒绝路径可复核。 | PASS | `AI-20260903-C1R-C1S-EXEC` 已 consumed。 |
| RC1-6 | Dogfood C2a lifecycle。 | claim/start/heartbeat/result-submit 和拒绝路径实测。 | PASS | `AI-20260903-C2A-EXEC` 已 consumed。 |
| RC1-7 | 归并 stale/legacy execution request。 | 每条遗留 request 有生命周期结论。 | PASS | baseline `timeout -> requeue -> consumed`。 |
| RC1-8 | 验证 fact fingerprint、预算及跨 AI 中立。 | JSON 契约不依赖 IDE 私有状态。 | PASS | `RESUME-D9AA4B087DC8DD77`。 |
| RC1-9 | 验证 result/evidence 与 PM close 前置条件。 | 四份真实结果 preflight 通过。 | PASS | §6 四份 closure fingerprint。 |
| RC1-10 | 受控 PM 收口预演。 | 重复 preflight 不消费结果。 | PASS | 四次 `already_consumed=false` 预演。 |
| RC1-11 | 正式 PM 收口。 | request consumed、CHG、PM_SESSION、feedback、ledger 全部可复核。 | PASS | §4、§5、§6。 |
| RC1-12 | 独立验收、提交准备与发布/回退决策。 | 全量门禁、变更审计、用户验收和提交决策。 | IN_PROGRESS | 技术门禁 PASS；用户验收通过；等待明确提交决定。 |

## 3. 当前实际状态

```text
branch: feature/trae-pro-20260509
HEAD: 778c1dda1e043ac491c4d7af371e9e5701709fa9
git diff --stat: 132 files changed, 982 insertions(+), 304 deletions(-)
tracked entries: 132
untracked entries: 12
git diff --numstat SHA-256: afcdd4a331d6f65c14368c7d854f20ad25135728d9789ba905a706727c0622b0
```

工作树刻意保持脏状态，禁止用 reset、restore、checkout 或清理操作伪造 clean。无已知用户无关变更；历史 `ruff check --fix auto_pm tests` 产生的 90 余个测试格式差异仍是已知 review 噪声，提交前必须按归属复核。

未跟踪文件包括四份 RC1 result 输入、`.auto-pm/ai_feedback.json`、pm-resume 新源码和测试、本 checkpoint，以及 `PM_SESSION_SYS-2026-001.md.bak_archive`。后者由 PM_SESSION archive 自动创建，是回退证据，不能删除。`.auto-pm/WBSC1-BASELINE-result.json` 是历史被拒绝的输入草稿，不是已消费证据。

## 4. 已完成工作

- C1/C1R/C1S：实现并 Dogfood `project-fact.v1`、真正只读的 project preflight 与受预算控制的 `pm-resume.v1`。read_set 最多 3 项、输出最多 12 KiB，适用于 Codex、Gemini、Cursor、Trae 与 Antigravity。
- C2a：实现并 Dogfood `pending -> claimed -> in_progress -> completed/failed/expired -> consumed`，包括 lease、heartbeat、wrong-owner、expiry、requeue、result-submit；`manual` adapter 仅表示可人工领取，绝不启动 IDE。
- RC1-7：baseline request 保留 `timeout -> requeue -> resubmit` 审计链，没有绕过 `chg_updates` 安全拒绝。
- RC1-11：四份 completed result 经最终 preflight 后由 `pm-workflow` 逐项 `handoff close`；CHG、控制面 PM_SESSION、feedback、ledger 已同批落账。
- 收口期间发现并根治 ChangeService 缺陷：生成器使用 H2 (`##`) 主章节、检查器仅接受 H3 (`###`) 且错误把 H3 子章节视为 H2 父章节的结束。检查器现兼容 H2/H3，并按当前标题层级确定章节边界；新增两项回归测试，防止合法模板无法关闭。
- PM_SESSION 曾为 158 行，超过 150 行健康阈值；通过 `pm-session archive --section 5 --keep-recent 16` 归档早期日志，保留最新记录和回退备份，现为 147 行。

## 5. 最终质量门禁

```text
pytest --no-cov -q --color=no
Exit Code: 0
Summary: full suite passed; baseline 1779 passed + 2 new regression tests, 15 skipped.

pytest --no-cov -q tests/change/test_change_service.py
Exit Code: 0
Summary: 39 passed in 4.19s.

ruff check auto_pm tests
Exit Code: 0
Summary: All checks passed!

mypy auto_pm
Exit Code: 0
Summary: Success: no issues found in 188 source files.

auto-pm pm-session check --project-root .\SYS-2026-001_WorkspaceGovernance --project-id SYS-2026-001
Exit Code: 0
Summary: 147/150 lines; 0 required sections missing; 0 archived-section regressions.

auto-pm change verify SW-2026-008 --ledger-check
Exit Code: 0
Summary: 0 missing ledger rows, 0 orphan rows, 0 status mismatches.

auto-pm doc check
Exit Code: 0
Summary: DOC-001 and DOC-004 PASS.

git diff --check
Exit Code: 0
Summary: no whitespace errors.
```

`ledger reconcile` and `change verify` emit historical structural warnings for `CHG-SCPT-2026-161` to `164`, but both return Exit Code 0 with no ledger difference. These archived historical defects are not silently changed by RC1.

## 6. 当前运行态

```text
evidence_id: RESUME-D9AA4B087DC8DD77
fact_evidence_id: FACT-B81275149AC95386
control_project_id: SYS-2026-001
control PM_SESSION sha256: c918749a7e546e287ac4d80be8f90a9a158082fa8acc193a903dfdffeae71f88
active_handoffs: []
next_legal_action: 阶段 0：基于事实包完成影响分析，再进入阶段 1 报批。
```

| request_id | 最终状态 | consumed_at (UTC) | closure fingerprint |
|---|---|---|---|
| `AI-20260903-C1R-C1S-EXEC` | consumed | `2026-09-03T14:16:07.736717+00:00` | `3d6236215fe60bad9470674ec1eb025970496a18f88deb38668a457c5acfcda9` |
| `AI-20260903-C2A-EXEC` | consumed | `2026-09-03T14:16:08.500362+00:00` | `d84747cb06f9d484fd4f34fd6f7ce0e932cfe3bcc31e12f4d87fe51e1c8e91dd` |
| `AI-20260902-WBSC1-EXEC` | consumed | `2026-09-03T14:16:09.261211+00:00` | `3ff15d1eb2ff5df38e11810b1ed249a6e68f2ec7aea662fd7c8ca50624639b90` |
| `AI-20260902-WBSC1-BASELINE-EXEC` | consumed | `2026-09-03T14:16:10.034420+00:00` | `052443254f221fe95bb85a7512663c0a4056097b9705927a5261c90335aaba6f` |

`CHG-SCPT-2026-156` 当前状态为 `closed`。`.auto-pm/ai_feedback.json` 是 PM-only feedback，已记录用户验收通过；下一动作仅是明确的 Git 提交或保留工作树决定。

## 7. 后续约束

- 正式阶段 0/1 必须重新运行 `pm resume SW-2026-008 --json`，只消费其 3 项 read_set；fact fingerprint、Git 或 PM_SESSION 漂移时不得复用本 checkpoint 的 evidence。
- C3 至 C7 是新批次，必须重新阶段 0、阶段 1 报批；不能因为 RC1 成功、closed CHG 或 zero active handoffs 自动启动。
- 不得 Mock 核心逻辑、Hardcode 骗绿、使用无依据全局 ignore，或再次执行全仓 Ruff 自动修复。
- PM 是 PM_SESSION、CHG、ledger 和 `ai_feedback.json` 的唯一落账 owner；execution result 只是一次性消息，不是第二套项目账本。

## 8. 风险与已知问题

- 工作树仍有 132 项跟踪改动，尤其是历史 Ruff 噪声；提交必须由用户决定并先 review。
- Git 仍可能对历史 CRLF 文件给出信息提示；`git diff --check` 已通过。
- `CHG-SCPT-2026-161` 至 `164` 保留历史结构告警，不属于 RC1 的篡改范围。
- C3 至 C7 尚未开始，不能将 RC1 的 C1/C2a 收口扩大解释为全部驾驶舱强制闭环完成。

## 9. 继任恢复协议与最小读取集

先进入 `READ-ONLY VERIFY`：禁止编辑、格式化、提交、创建/claim/start/close request，直到用户批准新业务范围。

```powershell
git rev-parse HEAD
git status --short
git diff --stat
& '.\.venv\Scripts\python.exe' -m auto_pm -w . pm resume SW-2026-008 --json
& '.\.venv\Scripts\python.exe' -m auto_pm -w . handoff list --pid SW-2026-008 --json-output
```

若 HEAD、工作树摘要、fingerprint 和 active_handoffs 与本文件一致，标记 `CHECKPOINT_VALID`；否则标记 `BASELINE_CONFLICT` 并停止写操作。最小读取集按优先级为：本 checkpoint、`AGENTS.md`、`PM_SESSION_SYS-2026-001.md`、`pm_resume_service.py`、`pm_resume_context.py`、`ai_handoff_service.py`、`handoff.py`、四份 RC1 result JSON、`test_pm_resume.py`、`test_handoff.py`、`test_change_service.py`。

## 10. Checkpoint 完整性

```text
checkpoint_timestamp_utc: 2026-09-03T14:26:51.1517072Z
HEAD_SHA: 778c1dda1e043ac491c4d7af371e9e5701709fa9
WORKING_TREE_FINGERPRINT: afcdd4a331d6f65c14368c7d854f20ad25135728d9789ba905a706727c0622b0
WORKING_TREE_SUMMARY: 132 tracked entries; 982 insertions; 304 deletions; 12 untracked entries
PM_RESUME_EVIDENCE: RESUME-D9AA4B087DC8DD77
FACT_EVIDENCE: FACT-B81275149AC95386
WBS_STATUS: RC1-0..RC1-11 PASS; RC1-12 IN_PROGRESS (user acceptance PASS; awaiting Git commit decision)
NEXT_LEGAL_ACTION: explicit Git commit/retain-worktree decision; thereafter C3-C7 requires a fresh Stage 0.
RECOMMENDED_NEXT_EXECUTION_MODEL: Gemini 3.8 Flash Medium
```

完成本 checkpoint 后停止。不得自动提交或启动 C3 至 C7。
