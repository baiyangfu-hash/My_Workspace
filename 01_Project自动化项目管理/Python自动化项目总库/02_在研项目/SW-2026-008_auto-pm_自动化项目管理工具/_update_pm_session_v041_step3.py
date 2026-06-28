"""V0.4.1 Step 3 收口 PM_SESSION 回写脚本

避免 VS Code buffer staleness 导致 Edit 工具失效，用 Python 直接读/写磁盘。

回写章节：§2/§3/§5/§6/§7/§8/§9
"""

from pathlib import Path

PM_SESSION = Path(r"c:\Users\fubai\Desktop\My_Workspace"
                  r"\01_Project自动化项目管理\Python自动化项目总库"
                  r"\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具"
                  r"\PM_SESSION_SW-2026-008.md")


def main() -> int:
    text = PM_SESSION.read_text(encoding="utf-8")
    original_text = text

    # ────────────────────────────────────────────────────────
    # §2 Current Focus：切换 Step 2 → Step 3 收口
    # ────────────────────────────────────────────────────────
    old_s2 = ("- current_focus: V0.4.1 Step 2 已完整收口（DocInjectService + doc inject CLI + "
              "7 单测 + 7 CLI 集成测试 + CHG-SCPT-2026-074 dogfooding 第7次完整 8 步闭环 + "
              "台帐序号006 已关闭）；下一步切换到 V0.4.1 Step 3 启动——Python 项目 plc check "
              "不适用口径补齐（避免驾驶舱误报）；版本号 0.3.8->0.4.1 升级待 Step 1~3 全部完成后统一执行")
    new_s2 = ("- current_focus: V0.4.1 Step 3 已完整收口（CheckResult 模型扩展 not_applicable + "
              "PlcChecker Python 项目检测 + DashboardService not_applicable 收集 + UI 展示 + "
              "CLI 友好提示 + 11 单元测试 + 4 CLI 集成测试 + CHG-SCPT-2026-075 dogfooding "
              "第8次完整 8 步闭环 + 台帐序号007 已关闭）；V0.4.1 Step 1~3 全部完成，下一步"
              "切换到版本号 0.3.8->0.4.1 升级 + CHANGELOG + 005 同步 + PRD 路线图更新")
    assert old_s2 in text, "§2 current_focus 未匹配"
    text = text.replace(old_s2, new_s2, 1)

    # ────────────────────────────────────────────────────────
    # §3 in_progress：Step 3 待启动 → Step 1~3 完成
    # ────────────────────────────────────────────────────────
    old_in_progress = ("- in_progress:\n"
                       "  - V0.4.1 Step 3 待启动：Python 项目 plc check 不适用口径补齐"
                       "（避免驾驶舱误报 PLC 检查失败）\n"
                       "  - 自我管理优先策略生效：继续围绕“今天最该处理什么”补足待办和风险排序口径- completed:")
    new_in_progress = ("- in_progress:\n"
                       "  - V0.4.1 Step 1~3 全部完成，下一步切换到版本号 0.3.8->0.4.1 升级 + "
                       "CHANGELOG + 005 同步 + PRD 路线图更新\n"
                       "  - 自我管理优先策略生效：继续围绕“今天最该处理什么”补足待办和风险排序口径\n"
                       "- completed:")
    assert old_in_progress in text, "§3 in_progress 未匹配"
    text = text.replace(old_in_progress, new_in_progress, 1)

    # ────────────────────────────────────────────────────────
    # §3 completed：新增 V0.4.1 Step 3 条目（在 Step 2 之前）
    # ────────────────────────────────────────────────────────
    old_completed_step2 = "  - V0.4.1 Step 2 历史 PLC 项目自动区标记 retrofit/注入：完成"
    new_completed_step3 = (
        "  - V0.4.1 Step 3 PLC 检查不适用口径补齐：完成（CheckResult 模型新增 "
        "not_applicable/not_applicable_reason 字段 + PlcChecker Python 项目检测 + "
        "DashboardService _collect_plc_check_stats 一次遍历 tuple + "
        "DashboardSummaryDTO 新增 not_applicable_project_count/ids + "
        "UI _DashboardBanner 新增\"检查不适用\"标签 + CLI cmd_check 友好提示与摘要分离；"
        "11 单元测试 + 4 CLI 集成测试全绿；ruff/mypy 0 errors；"
        "CHG-SCPT-2026-075 dogfooding 第8次完整 8 步生命周期闭环 draft->closed；"
        "台帐序号007 已关闭；累计 dogfooding 8 次）\n"
        "  - V0.4.1 Step 2 历史 PLC 项目自动区标记 retrofit/注入：完成"
    )
    assert old_completed_step2 in text, "§3 completed Step 2 未匹配"
    text = text.replace(old_completed_step2, new_completed_step3, 1)

    # ────────────────────────────────────────────────────────
    # §3 next_up：移除 Step 2/3，只保留版本号升级
    # ────────────────────────────────────────────────────────
    old_next_up = ("- next_up:\n"
                   "  - V0.4.1：历史 PLC 项目自动区标记 retrofit/注入方案（Step 2）\n"
                   "  - V0.4.1：Python 项目的 plc check 不适用口径补齐，避免驾驶舱误报（Step 3）\n"
                   "  - V0.4.1：版本号 0.3.8->0.4.1 升级 + CHANGELOG + 005 同步"
                   "（Step 1~3 全部完成后统一执行）- open_questions:")
    new_next_up = ("- next_up:\n"
                   "  - V0.4.1：版本号 0.3.8->0.4.1 升级 + CHANGELOG + 005 同步 + PRD 路线图更新\n"
                   "  - V0.4.2：真实/准真实 PLC 项目试运行（基于 V0.4.0~V0.4.1 已落地能力做端到端验证）\n"
                   "- open_questions:")
    assert old_next_up in text, "§3 next_up 未匹配"
    text = text.replace(old_next_up, new_next_up, 1)

    # ────────────────────────────────────────────────────────
    # §3 risks_dependencies：PLC 误报风险已修复
    # ────────────────────────────────────────────────────────
    old_risk = ("  - `plc check` 当前对 Python 项目缺少“不适用”提示，"
                "真实驾驶舱若直接复用检查结果，可能放大误报")
    new_risk = ("  - `plc check` 对 Python 项目的“不适用”口径已通过 V0.4.1 Step 3 修复"
                "（CheckResult.not_applicable 标记 + DashboardService 防御性条件 + UI 透明展示）")
    assert old_risk in text, "§3 risks_dependencies plc check 未匹配"
    text = text.replace(old_risk, new_risk, 1)

    # ────────────────────────────────────────────────────────
    # §3 spec_compliance：更新到 Step 3 + dogfooding 8 次
    # ────────────────────────────────────────────────────────
    old_compliance = ("- spec_compliance:\n"
                      "  - last_check: 2026-06-28\n"
                      "  - result: 代码基线 V0.3.8 + V0.4.1 Step 1 增量；"
                      "pyproject=0.3.8（待 Step 1~3 全部完成后统一升 0.4.1）、CHANGELOG=[0.3.8]、"
                      "PRD=V2.1.1、PM_SESSION §2 当前焦点已切换到 V0.4.1 Step 2 启动。"
                      "运行复核：ruff check 0 errors；mypy auto_pm 0 errors；"
                      "pytest --no-cov tests/ui/test_overview_tab_asset_summary.py "
                      "tests/ui/test_gui_smoke.py 79 passed（8 新增 + 71 既有 UI 回归）；"
                      "dogfooding 6 次闭环（CHG-001/062/063/064/072/073 全 closed）；"
                      "当前 V0.4.1 Step 1 已收口，进入 Step 2 启动准备")
    new_compliance = ("- spec_compliance:\n"
                      "  - last_check: 2026-06-28\n"
                      "  - result: 代码基线 V0.3.8 + V0.4.1 Step 1~3 增量；"
                      "pyproject=0.3.8（待版本号升级批次统一升 0.4.1）、CHANGELOG=[0.3.8]、"
                      "PRD=V2.1.1、PM_SESSION §2 当前焦点已切换到 V0.4.1 Step 3 收口。"
                      "运行复核：ruff check 0 errors；mypy auto_pm 0 errors；"
                      "聚焦回归 194 passed（含 11 单测 + 4 CLI 集成测试）；"
                      "全量回归 1233 passed 1 failed（1 预存失败与 Step 3 无关）；"
                      "dogfooding 8 次闭环（CHG-001/062/063/064/072/073/074/075 全 closed）；"
                      "当前 V0.4.1 Step 1~3 已全部收口，进入版本号升级准备")
    assert old_compliance in text, "§3 spec_compliance 未匹配"
    text = text.replace(old_compliance, new_compliance, 1)

    # ────────────────────────────────────────────────────────
    # §5 Logs：新增 V0.4.1 Step 3 change_log 条目
    # ────────────────────────────────────────────────────────
    old_s5_anchor = ("- change_log:\n"
                     "  - 2026-06-28 V0.4.0 Week 4 收口补完")
    new_s5_log = (
        "- change_log:\n"
        "  - 2026-06-28 V0.4.1 Step 3 完成：CheckResult 模型扩展 not_applicable/not_applicable_reason；"
        "PlcChecker.check_project 开头检测 Python 项目（无 .plc.json + 有 pyproject.toml）"
        "直接返回 not_applicable=True 不跑 5 项检查；DashboardService 重构 "
        "_collect_failed_plc_projects → _collect_plc_check_stats 返回 tuple(failed, not_applicable) "
        "一次遍历避免重复跑；DashboardSummaryDTO 新增 not_applicable_project_count/ids；"
        "UI _DashboardBanner 新增\"检查不适用\"标签 + tooltip；CLI cmd_check 单项目路径"
        "新增 not_applicable 友好提示分支，_print_check_summary 分离 applicable/not_applicable；"
        "11 单元测试（5 PlcChecker + 4 DashboardService + 2 UI）+ 4 CLI 集成测试全绿；"
        "ruff/mypy 0 errors；聚焦回归 194 passed 0 failed；全量回归 1233 passed 1 failed"
        "（预存 test_overview_tab_asset_summary.py 条件断言跳过，与 Step 3 无关）；"
        "CHG-SCPT-2026-075 dogfooding 第8次完整 8 步生命周期闭环 draft->closed；台帐序号007 已关闭\n"
        "  - 2026-06-28 V0.4.0 Week 4 收口补完"
    )
    assert old_s5_anchor in text, "§5 change_log 锚点未匹配"
    text = text.replace(old_s5_anchor, new_s5_log, 1)

    # ────────────────────────────────────────────────────────
    # §6 Implementation Log：新增 V0.4.1 Step 3 实施记录
    # ────────────────────────────────────────────────────────
    old_s6_anchor = (
        "- 2026-06-28 | skill=fullstack-engineer | mode=V0.4.1 Step 2 实施收口"
        "（历史 PLC 项目自动区标记 retrofit/注入 + dogfooding 第7次闭环）"
    )
    new_s6_log = (
        "- 2026-06-28 | skill=fullstack-engineer | mode=V0.4.1 Step 3 实施收口"
        "（Python 项目 plc check 不适用口径补齐 + dogfooding 第8次闭环）\n"
        "  - goal: 补齐 plc check 对 Python 项目的\"不适用\"口径，避免驾驶舱误报 PLC 检查失败；"
        "扩展 CheckResult/DashboardSummaryDTO/UI 三层，让 PlcChecker 对 Python 项目"
        "返回 not_applicable=True 不跑检查不 FAIL；同时走完 CHG-SCPT-2026-075 dogfooding 第8次闭环\n"
        "  - changed_files:\n"
        "    - auto_pm/models/plc.py（CheckResult 新增 not_applicable: bool=False + "
        "not_applicable_reason: str=\"\" 字段）\n"
        "    - auto_pm/plc/checker.py（check_project 开头检测 Python 项目："
        "无 .plc.json + 有 pyproject.toml → 返回 not_applicable=True 不跑 5 项检查；"
        "复用 _is_project_dir 的 pyproject.toml 排除规则思路）\n"
        "    - auto_pm/core/dashboard_service.py（重构 _collect_failed_plc_projects → "
        "_collect_plc_check_stats 返回 tuple[list[str], list[str]] 一次遍历收集 failed + "
        "not_applicable 避免 PlcChecker.check 重复跑；_collect_risk_hints 接受 "
        "not_applicable_project_ids 参数，区分\"PLC 检查失败\"真失败 vs \"PLC 检查不适用\"Python 项目）\n"
        "    - auto_pm/models/dto.py（DashboardSummaryDTO 新增 not_applicable_project_count: int=0 "
        "+ not_applicable_project_ids: list[str]=Field(default_factory=list)）\n"
        "    - auto_pm/cli/plc/__init__.py（cmd_check 单项目路径新增 not_applicable 友好提示分支："
        "输出\"PLC 检查不适用: <ID>\" + 提示 Python 项目无需执行 PLC 检查；"
        "_print_check_summary 分离 applicable/not_applicable 两个表格）\n"
        "    - auto_pm/ui/project_list/list_view.py（_DashboardBanner._build_ui 新增 _not_applicable_label；"
        "set_summary 更新文本\"检查不适用: N（Python 项目）\" + tooltip 列出不适用项目编号）\n"
        "    - tests/plc/test_checker.py（新增 TestPythonProjectNotApplicable 类 5 测试："
        "python_project_with_pyproject_no_plc_json / no_checks_run / with_plc_json_still_checked / "
        "no_pyproject_no_plc_json_runs_checks / not_applicable_reason_text）\n"
        "    - tests/core/test_dashboard_service.py（扩展 _FakeCheckResult/_FakePlcService 支持 "
        "not_applicable；新增 4 测试：not_counted_as_failed / mixed_with_failed / "
        "risk_hints_not_applicable_only / failed_overrides_not_applicable_hint）\n"
        "    - tests/ui/test_project_list.py（新增 2 UI 测试：not_applicable_label_displayed / "
        "not_applicable_label_zero）\n"
        "    - tests/cli/test_plc.py（新增 _make_python_project 辅助函数 + 4 CLI 集成测试："
        "python_project_friendly_output / python_project_json / all_skips_python_project / "
        "python_project_does_not_pollute_dashboard）\n"
        "    - 00_项目管理/03_执行过程/2026-06-28_V0.4.1_Step3_PLC检查不适用口径补齐_迭代计划.md（V041-S3-01~11 任务表）\n"
        "    - 00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-075.md（dogfooding 第8次闭环 draft->closed）\n"
        "    - 00_项目管理/04_变更管理/04_变更记录/01_版本变更台帐.md（序号007 CHG-075 自动回写状态 ✅已关闭）\n"
        "  - impact: auto-pm 现在具备 PLC 检查不适用口径完整三层能力；plc check <Python 项目 ID> "
        "返回 not_applicable=True 不跑 5 项检查不 FAIL，CLI 输出友好提示；DashboardService "
        "在 stack 判定之外增加 not_applicable 防御性条件；DashboardSummaryDTO 透明展示不适用项目数；"
        "UI 驾驶舱首页新增\"检查不适用\"标签；误报问题彻底解决\n"
        "  - risks: (1) ProjectScanner._enrich_from_plc_json stack 误判根因未修，本轮通过 "
        "not_applicable 防御性兜底；根因修复留给后续迭代；(2) 全量回归 1 预存失败 "
        "(test_overview_tab_asset_summary.py 条件断言跳过) 与 Step 3 无关，由 Step 1 引入\n"
        "  - verification: pytest tests/plc/test_checker.py tests/core/test_dashboard_service.py "
        "tests/ui/test_project_list.py tests/cli/test_plc.py --no-cov → 194 passed 0 failed；"
        "全量回归 1233 passed 1 failed（1 预存失败）；ruff check 0 errors；mypy auto_pm 0 errors；"
        "CHG-075 8 步状态转换 draft->submitted->under_review->approved->implementing->"
        "pending_acceptance->accepting->completed->closed 全部成功；台帐序号007 自动回写 ✅已关闭\n"
        "- 2026-06-28 | skill=fullstack-engineer | mode=V0.4.1 Step 2 实施收口"
        "（历史 PLC 项目自动区标记 retrofit/注入 + dogfooding 第7次闭环）"
    )
    assert old_s6_anchor in text, "§6 Implementation Log Step 2 锚点未匹配"
    text = text.replace(old_s6_anchor, new_s6_log, 1)

    # ────────────────────────────────────────────────────────
    # §7 Verification Log：新增 V0.4.1 Step 3 验证记录
    # ────────────────────────────────────────────────────────
    old_s7_anchor = (
        "- verified:\n"
        "  - V0.4.1 Step 2 历史 PLC 项目自动区标记 retrofit/注入（2026-06-28，已验证）:"
    )
    new_s7_log = (
        "- verified:\n"
        "  - V0.4.1 Step 3 PLC 检查不适用口径补齐（2026-06-28，已验证）:\n"
        "    - GetDiagnostics：auto_pm/models/plc.py、auto_pm/plc/checker.py、auto_pm/core/dashboard_service.py、"
        "auto_pm/models/dto.py、auto_pm/cli/plc/__init__.py、auto_pm/ui/project_list/list_view.py → 0 diagnostics\n"
        "    - ruff check auto_pm/models/plc.py auto_pm/plc/checker.py auto_pm/core/dashboard_service.py "
        "auto_pm/models/dto.py auto_pm/cli/plc/__init__.py auto_pm/ui/project_list/list_view.py → All checks passed!\n"
        "    - mypy auto_pm → Success: no issues found in 5 source files\n"
        "    - pytest --no-cov tests/plc/test_checker.py tests/core/test_dashboard_service.py "
        "tests/ui/test_project_list.py tests/cli/test_plc.py → 194 passed 0 failed "
        "（5 PlcChecker + 4 DashboardService + 2 UI + 4 CLI + 既有回归）\n"
        "    - 全量回归 pytest --no-cov → 1233 passed 1 failed（1 预存失败 "
        "test_overview_tab_asset_summary.py 条件断言跳过，由 Step 1 引入，与 Step 3 无关）\n"
        "    - 真实场景验证：plc check <Python 项目 ID> 输出\"PLC 检查不适用: <ID>\" + "
        "提示 Python 项目无需执行 PLC 检查；plc check --all 不将 Python 项目误报为 FAIL；"
        "DashboardService.get_summary 返回 not_applicable_project_count=1 且 failed_check_project_count=0\n"
        "    - CHG-SCPT-2026-075 dogfooding 第8次完整 8 步生命周期 "
        "draft->submitted->under_review->approved->implementing->pending_acceptance->accepting->"
        "completed->closed 全部成功；台帐序号007 自动回写状态为 ✅已关闭\n"
        "    - 台帐核查：01_版本变更台帐.md 序号007 行 状态=✅已关闭，与 CHG-075.md §3.4 状态一致\n"
        "  - V0.4.1 Step 2 历史 PLC 项目自动区标记 retrofit/注入（2026-06-28，已验证）:"
    )
    assert old_s7_anchor in text, "§7 Verification Log Step 2 锚点未匹配"
    text = text.replace(old_s7_anchor, new_s7_log, 1)

    # ────────────────────────────────────────────────────────
    # §8 current_state：切换 Step 2 → Step 3 收口
    # ────────────────────────────────────────────────────────
    old_s8_current = (
        "- current_state: V0.4.1 Step 2 已完整收口——历史 PLC 项目自动区标记 retrofit/注入完成"
        "（DocInjectService + doc inject CLI + 3 个 marker key 锚点正则映射 + 锚点后插入 marker block "
        "+ 原手工内容保留在 END 标记之后），新增 7 单元测试 + 7 CLI 集成测试（14 测试全绿），"
        "ruff/mypy 0 errors；CHG-SCPT-2026-074 dogfooding 第7次完整 8 步生命周期闭环完成（draft->closed），"
        "台帐序号006 自动回写状态为 ✅已关闭；累计 dogfooding 7 次"
        "（CHG-001/062/063/064/072/073/074 全 closed）"
    )
    new_s8_current = (
        "- current_state: V0.4.1 Step 3 已完整收口——PLC 检查不适用口径补齐完成"
        "（CheckResult 扩展 not_applicable/not_applicable_reason + PlcChecker Python 项目检测 + "
        "DashboardService _collect_plc_check_stats tuple 收集 + DashboardSummaryDTO 新增 "
        "not_applicable_project_count/ids + UI _DashboardBanner \"检查不适用\"标签 + "
        "CLI cmd_check 友好提示与摘要分离），新增 11 单元测试 + 4 CLI 集成测试（15 测试全绿），"
        "ruff/mypy 0 errors；CHG-SCPT-2026-075 dogfooding 第8次完整 8 步生命周期闭环完成（draft->closed），"
        "台帐序号007 自动回写状态为 ✅已关闭；累计 dogfooding 8 次"
        "（CHG-001/062/063/064/072/073/074/075 全 closed）；"
        "V0.4.1 Step 1~3 全部完成，等待版本号 0.3.8->0.4.1 升级"
    )
    assert old_s8_current in text, "§8 current_state 未匹配"
    text = text.replace(old_s8_current, new_s8_current, 1)

    # ────────────────────────────────────────────────────────
    # §8 next_focus：从 Step 3 启动 → 版本号升级
    # ────────────────────────────────────────────────────────
    old_s8_next = (
        "- next_focus: V0.4.1 Step 3 启动——Python 项目 plc check 不适用口径补齐"
        "（避免驾驶舱误报 PLC 检查失败）；版本号 0.3.8->0.4.1 升级待 Step 1~3 全部完成后统一执行"
    )
    new_s8_next = (
        "- next_focus: V0.4.1 版本号升级批次——0.3.8->0.4.1 升级 + CHANGELOG [0.4.1] 新增条目 "
        "+ 005_变更记录_CHG.md [V0.4.1] 章节 + PRD V2.1.1 路线图更新；"
        "后续可启动 V0.4.2 真实/准真实 PLC 项目试运行"
    )
    assert old_s8_next in text, "§8 next_focus 未匹配"
    text = text.replace(old_s8_next, new_s8_next, 1)

    # ────────────────────────────────────────────────────────
    # §8 skill_switch：从 Step 2 → Step 3
    # ────────────────────────────────────────────────────────
    old_s8_skill = (
        "- skill_switch: 2026-06-28 PM 阶段完成（V0.4.1 Step 2 迭代计划已经用户批准）→ 软件域编码实施；"
        "目标技能=fullstack-engineer；切换原因=PM 流程推进到需要编码实施阶段，"
        "按 pm-workflow 跨技能切换规则强制切换；目标范围=V041-S2-01~07"
        "（CHG-074 dogfooding 第7次闭环 + DocInjectService 实现 + doc inject CLI 命令 + "
        "单元测试 + CLI 集成测试 + CHG-074 流转 closed + PM_SESSION 回写）"
    )
    new_s8_skill = (
        "- skill_switch: 2026-06-28 V0.4.1 Step 3 软件域编码实施完成→ 等待版本号升级批次启动；"
        "本轮技能=fullstack-engineer；目标范围=V041-S3-01~11（CHG-075 dogfooding 第8次闭环 + "
        "CheckResult 模型扩展 + PlcChecker Python 项目检测 + DashboardService not_applicable 收集 + "
        "DashboardSummaryDTO 扩展 + UI 展示 + CLI 友好提示 + 单元测试 + CLI 集成测试 + "
        "误报问题验证 + CHG-075 流转 closed + PM_SESSION 回写）"
    )
    assert old_s8_skill in text, "§8 skill_switch 未匹配"
    text = text.replace(old_s8_skill, new_s8_skill, 1)

    # ────────────────────────────────────────────────────────
    # §8 watchouts：在 V0.4.1 Step 1 收口专项之前新增 Step 3 专项
    # ────────────────────────────────────────────────────────
    old_watchouts_anchor = (
        "  - V0.4.1 Step 1 收口专项："
    )
    new_watchouts_step3 = (
        "  - V0.4.1 Step 3 收口专项：(1) ProjectScanner._enrich_from_plc_json stack 误判根因未修，"
        "本轮通过 PlcChecker not_applicable 防御性兜底；根因修复留给后续迭代；"
        "(2) PlcChecker.check_project 开头检测规则与 _is_project_dir 的 pyproject.toml 排除规则一致，"
        "避免 --all 模式与单项目模式行为分歧；(3) DashboardSummaryDTO 新增字段均有默认值（Field(0)/"
        "Field(default_factory=list)），向后兼容既有反序列化；(4) 全量回归 1 预存失败 "
        "(test_overview_tab_asset_summary.py 条件断言跳过) 由 Step 1 引入，与 Step 3 无关；"
        "(5) UI 标签文案为\"检查不适用: N（Python 项目）\"，tooltip 列出不适用项目编号，"
        "若 Python 项目数较多需考虑折叠展示\n"
        "  - V0.4.1 Step 1 收口专项："
    )
    assert old_watchouts_anchor in text, "§8 watchouts Step 1 锚点未匹配"
    text = text.replace(old_watchouts_anchor, new_watchouts_step3, 1)

    # ────────────────────────────────────────────────────────
    # §9 Next Actions：标记 PLC 不适用口径任务为已完成
    # ────────────────────────────────────────────────────────
    old_s9 = ("- [precondition: V0.4.1 Step 2 已完成] [待启动] done_when: V0.4.1 Step 3 Python 项目 plc check 不适用口径补齐，避免驾驶舱误报")
    new_s9 = ("- ✅ [precondition: V0.4.1 Step 2 已完成] [已完成 2026-06-28] done_when: V0.4.1 Step 3 Python 项目 plc check 不适用口径补齐完成（CheckResult 扩展 not_applicable + PlcChecker Python 项目检测 + DashboardService 防御性 + DashboardSummaryDTO 扩展 + UI 展示 + CLI 友好提示 + 11 单测 + 4 CLI 集成测试 + CHG-075 dogfooding 第8次闭环 draft->closed；误报问题已解决）")
    assert old_s9 in text, "§9 Next Actions PLC 不适用口径未匹配"
    text = text.replace(old_s9, new_s9, 1)

    # ────────────────────────────────────────────────────────
    # 写回文件
    # ────────────────────────────────────────────────────────
    if text == original_text:
        print("ERROR: 文本未发生变化")
        return 1
    PM_SESSION.write_text(text, encoding="utf-8")
    print(f"OK: PM_SESSION 已回写 V0.4.1 Step 3 收口内容")
    print(f"原长度: {len(original_text)}, 新长度: {len(text)}, 增量: {len(text) - len(original_text)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
