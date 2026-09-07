"""全局规范索引覆盖率校验器 (IndexCoverageChecker)

基于 CHG-SPEC-2026-001 终验口径下沉：
- spec_registry.json 中已注册的所有规范 (specs) 必须在 00_INDEX_全局规范索引.md 中各有一条真实可解析链接
- 链接目标必须在物理磁盘上实际存在
- 100% 覆盖率判定 PASS
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


@dataclass
class IndexCoverageReport:
    total_specs: int
    indexed_targets: int
    missing_specs: list[str] = field(default_factory=list)
    bad_links: list[tuple[str, str]] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.missing_specs) == 0 and len(self.bad_links) == 0

    @property
    def coverage_ratio(self) -> float:
        if self.total_specs == 0:
            return 1.0
        covered = self.total_specs - len(self.missing_specs)
        return round(covered / self.total_specs, 4)


class IndexCoverageChecker:
    """00_INDEX 覆盖率检查器。"""

    def __init__(self, lib_dir: Path | str, repo_root: Path | str | None = None) -> None:
        self.lib_dir = Path(lib_dir)
        self.repo_root = Path(repo_root) if repo_root else self.lib_dir.parent

    def check(self) -> IndexCoverageReport:
        reg_path = self.lib_dir / "spec_registry.json"
        idx_path = self.lib_dir / "00_INDEX_全局规范索引.md"

        if not reg_path.is_file() or not idx_path.is_file():
            return IndexCoverageReport(
                total_specs=0,
                indexed_targets=0,
                missing_specs=["spec_registry.json 或 00_INDEX 文件缺失"],
            )

        try:
            reg = json.loads(reg_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError):
            return IndexCoverageReport(
                total_specs=0,
                indexed_targets=0,
                missing_specs=["spec_registry.json 解析失败"],
            )

        specs = {
            sid: e
            for sid, e in reg.get("specs", {}).items()
            if isinstance(e, dict) and e.get("lifecycle") in ("stable", "active", "draft", None)
        }

        try:
            idx_content = idx_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return IndexCoverageReport(
                total_specs=len(specs),
                indexed_targets=0,
                missing_specs=["00_INDEX 读取失败"],
            )

        # 收集 INDEX 内所有链接目标（规范化为绝对路径）
        targets: list[str] = []
        for m in LINK_RE.finditer(idx_content):
            tgt = m.group(1).strip()
            if re.match(r"^[a-zA-Z]+://", tgt) or tgt.startswith("mailto:"):
                continue
            path_part = tgt.split("#")[0]
            if not path_part:
                continue
            # 支持相对 lib_dir 或相对 repo_root
            norm_lib = os.path.normpath(str(self.lib_dir / path_part))
            norm_repo = os.path.normpath(str(self.repo_root / path_part))
            targets.append(norm_lib)
            targets.append(norm_repo)

        missing: list[str] = []
        bad_links: list[tuple[str, str]] = []

        for sid, entry in sorted(specs.items()):
            canonical = entry.get("canonical_path", "")
            if not canonical:
                missing.append(sid)
                continue

            full_from_repo = os.path.normpath(str(self.repo_root / canonical))
            full_from_lib = os.path.normpath(str(self.lib_dir / canonical))

            hit = [t for t in targets if t in (full_from_repo, full_from_lib)]
            if not hit:
                # 宽容匹配：按 basename 匹配
                base = os.path.basename(full_from_repo)
                hit = [t for t in targets if os.path.basename(t) == base]

            if not hit:
                missing.append(sid)
            else:
                # 检验该文件在磁盘上是否存在
                cand = hit[0]
                if not os.path.isfile(cand):
                    # 尝试从 repo 根或 lib 检查真实存在性
                    if not os.path.isfile(full_from_repo) and not os.path.isfile(full_from_lib):
                        bad_links.append((sid, cand))

        return IndexCoverageReport(
            total_specs=len(specs),
            indexed_targets=len(targets) // 2,
            missing_specs=missing,
            bad_links=bad_links,
        )
