"""Health check: verify project continuity mechanisms are complete."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CheckResult:
    """Result of a single check item."""
    name: str
    passed: bool
    message: str = ""


@dataclass
class CheckReport:
    """Aggregated health check report."""
    project_path: str
    results: list[CheckResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failed(self) -> list[CheckResult]:
        return [r for r in self.results if not r.passed]

    def format(self) -> str:
        lines = [f"项目健康检查: {self.project_path}", "=" * 50]
        for r in self.results:
            icon = "PASS" if r.passed else "FAIL"
            lines.append(f"  [{icon}] {r.name}")
            if r.message:
                lines.append(f"         {r.message}")
        lines.append("=" * 50)
        if self.all_passed:
            lines.append("结果: 全部通过")
        else:
            lines.append(f"结果: {len(self.failed)} 项未通过")
        return "\n".join(lines)


def check_project(project_root: str | Path) -> CheckReport:
    """Run health checks on a project.

    Checks:
    - PM_SESSION exists
    - hooks/ complete (4 scripts + hooks.json)
    - handoffs/ exists
    """
    root = Path(project_root).resolve()
    report = CheckReport(project_path=str(root))

    # Check 1: PM_SESSION
    pm_sessions = list(root.glob("PM_SESSION*.md"))
    if not pm_sessions:
        report.results.append(CheckResult(
            "PM_SESSION", False,
            "未找到 PM_SESSION*.md 文件"
        ))
    else:
        report.results.append(CheckResult(
            "PM_SESSION", True,
            f"找到: {pm_sessions[0].name}"
        ))

    # Check 2: hooks
    hooks_dir = root / ".github" / "hooks"
    required_hooks = ["session-start.ps1", "session-end.ps1", "agent-stop.ps1", "apply-handoff.ps1"]
    if not (hooks_dir / "hooks.json").is_file():
        report.results.append(CheckResult(
            "hooks", False,
            "缺少 .github/hooks/hooks.json"
        ))
    else:
        missing = [h for h in required_hooks if not (hooks_dir / "scripts" / h).is_file()]
        if missing:
            report.results.append(CheckResult(
                "hooks", False,
                f"缺少脚本: {', '.join(missing)}"
            ))
        else:
            report.results.append(CheckResult(
                "hooks", True,
                "所有 4 个 hooks 脚本就绪"
            ))

    # Check 3: handoffs
    handoffs_dir = root / ".trae" / "handoffs"
    if not handoffs_dir.is_dir():
        report.results.append(CheckResult(
            "handoffs", False,
            "缺少 .trae/handoffs/ 目录"
        ))
    else:
        report.results.append(CheckResult(
            "handoffs", True,
            "handoffs 目录就绪"
        ))

    # Check 4: Spec Snapshot (if PM_SESSION exists)
    if pm_sessions:
        content = pm_sessions[0].read_text(encoding="utf-8")
        from .snapshot import has_spec_snapshot
        if has_spec_snapshot(content):
            report.results.append(CheckResult(
                "Spec Snapshop", True,
                "Spec Snapshot 区块存在"
            ))
        else:
            report.results.append(CheckResult(
                "Spec Snapshot", False,
                "PM_SESSION 中缺少 Spec Snapshot 区块"
            ))

    # Check 5: PM_SESSION sections completeness
    if pm_sessions:
        content = pm_sessions[0].read_text(encoding="utf-8")
        required_sections = [
            ("## 0. Meta", "§0 Meta"),
            ("## 1. Positioning", "§1 Positioning"),
            ("## 2. Current Focus", "§2 Current Focus"),
            ("## 3. Status Summary", "§3 Status Summary"),
            ("## 4. Artifacts Index", "§4 Artifacts Index"),
            ("## 5. Logs", "§5 Logs"),
            ("## 6. Implementation Log", "§6 Implementation Log"),
            ("## 7. Verification Log", "§7 Verification Log"),
            ("## 8. Handoff Notes", "§8 Handoff Notes"),
            ("## 9. Next Actions", "§9 Next Actions"),
        ]
        missing_sections = [label for marker, label in required_sections if marker not in content]
        if missing_sections:
            report.results.append(CheckResult(
                "PM_SESSION章节完整性", False,
                f"缺少: {', '.join(missing_sections)}"
            ))
        else:
            report.results.append(CheckResult(
                "PM_SESSION章节完整性", True,
                "§0-§9 全部章节齐全"
            ))

    # Check 6: .gitignore (security warning)
    gitignore = root / ".gitignore"
    if not gitignore.is_file():
        report.results.append(CheckResult(
            ".gitignore", False,
            "缺少 .gitignore 文件（安全红线：防止敏感信息提交）"
        ))
    else:
        report.results.append(CheckResult(
            ".gitignore", True,
            ".gitignore 文件存在"
        ))

    return report
