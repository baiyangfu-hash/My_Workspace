"""结构化 Bug 记录器

测试失败时自动记录 Bug，关联截图，生成 JSON + Markdown 双格式报告。
测试成功的项目保留，测试失败的项目在 session 结束后清理。
"""

from __future__ import annotations

import json
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


@dataclass
class BugRecord:
    """单条 Bug 记录"""

    bug_id: str
    test_name: str
    step: str
    expected: str
    actual: str
    severity: str  # critical / major / minor
    screenshot_path: str = ""
    traceback: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class BugRecorder:
    """Bug 记录器，session 级单例"""

    def __init__(self, report_dir: Path) -> None:
        self.report_dir = report_dir
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir = self.report_dir / "bug_screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.bugs: list[BugRecord] = []
        self._counter = 0
        self._failed_projects: set[str] = set()

    def record(
        self,
        test_name: str,
        step: str,
        expected: str,
        actual: str,
        severity: str = "major",
        exc: BaseException | None = None,
        widget: "QWidget | None" = None,
    ) -> BugRecord:
        """记录一条 Bug 并关联截图"""
        self._counter += 1
        bug_id = f"BUG-{self._counter:03d}"
        screenshot_path = ""
        if widget is not None:
            try:
                screenshot_path = str(self.screenshot_dir / f"{bug_id}.png")
                widget.grab().save(screenshot_path)
            except Exception:
                screenshot_path = ""
        tb = ""
        if exc is not None:
            tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        bug = BugRecord(
            bug_id=bug_id,
            test_name=test_name,
            step=step,
            expected=expected,
            actual=actual,
            severity=severity,
            screenshot_path=screenshot_path,
            traceback=tb,
        )
        self.bugs.append(bug)
        return bug

    def mark_project_failed(self, project_id: str) -> None:
        """标记测试失败的项目，session 结束后清理"""
        self._failed_projects.add(project_id)

    @property
    def failed_projects(self) -> set[str]:
        return set(self._failed_projects)

    def dump_report(self) -> tuple[Path, Path]:
        """生成 JSON + Markdown 双格式报告，返回 (json_path, md_path)"""
        json_path = self.report_dir / "bugs.json"
        md_path = self.report_dir / "bug_report.md"

        # JSON 报告
        data = {
            "test_session": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_bugs": len(self.bugs),
            "by_severity": {
                "critical": sum(1 for b in self.bugs if b["severity"] == "critical"),
                "major": sum(1 for b in self.bugs if b["severity"] == "major"),
                "minor": sum(1 for b in self.bugs if b["severity"] == "minor"),
            },
            "failed_projects": sorted(self._failed_projects),
            "bugs": [asdict(b) for b in self.bugs],
        }
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        # Markdown 报告
        lines = [
            "# GUI 全功能测试 - Bug 报告",
            "",
            f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Bug 总数**: {len(self.bugs)}",
            f"- 严重: {data['by_severity']['critical']}",
            f"- 主要: {data['by_severity']['major']}",
            f"- 次要: {data['by_severity']['minor']}",
            "",
        ]
        if self._failed_projects:
            lines.append(f"**测试失败的项目（已清理）**: {', '.join(sorted(self._failed_projects))}")
            lines.append("")
        if not self.bugs:
            lines.append("未发现 Bug！")
        else:
            for bug in self.bugs:
                lines.append(f"## {bug.bug_id} [{bug.severity}]")
                lines.append(f"- **测试**: `{bug.test_name}`")
                lines.append(f"- **步骤**: {bug.step}")
                lines.append(f"- **预期**: {bug.expected}")
                lines.append(f"- **实际**: {bug.actual}")
                lines.append(f"- **时间**: {bug.timestamp}")
                if bug.screenshot_path:
                    lines.append(f"- **截图**: {bug.screenshot_path}")
                if bug.traceback:
                    lines.append("- **堆栈**:")
                    lines.append("  ```")
                    for line in bug.traceback.splitlines():
                        lines.append(f"  {line}")
                    lines.append("  ```")
                lines.append("")
        md_path.write_text("\n".join(lines), encoding="utf-8")
        return json_path, md_path
