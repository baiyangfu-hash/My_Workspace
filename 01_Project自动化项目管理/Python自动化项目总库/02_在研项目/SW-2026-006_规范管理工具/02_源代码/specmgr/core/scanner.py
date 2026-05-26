from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml

from .config import WorkspaceConfig, DEFAULT_SPEC_DIRS


_SPEC_NUMBER_RE = re.compile(r"^(?:SW|PM|PLC|PY|CODE|LSP|INT)-\d{3,4}(?:-\d{3})?")


class SpecScanner:
    def __init__(
        self,
        workspace: Path,
        config: WorkspaceConfig | None = None,
    ) -> None:
        self.workspace = workspace
        self.config = config or WorkspaceConfig(workspace=workspace)

    def _spec_dirs(self) -> list[Path]:
        return self.config.full_spec_dirs

    def _collect_md_files(self, directory: Path) -> list[Path]:
        if not directory.exists():
            return []
        return sorted(directory.rglob("*.md"))

    def _extract_spec_number(self, file_path: Path) -> Optional[str]:
        name = file_path.stem
        match = _SPEC_NUMBER_RE.match(name)
        if match:
            return match.group(0)
        return None

    def scan_all(self) -> dict[str, list[Path]]:
        result: dict[str, list[Path]] = {}
        for spec_dir in self._spec_dirs():
            for md_file in self._collect_md_files(spec_dir):
                spec_num = self._extract_spec_number(md_file)
                if spec_num:
                    result.setdefault(spec_num, []).append(md_file)
        return result

    def scan_by_domain(self, domain: str) -> list[Path]:
        domain_dir = self.workspace / domain
        return self._collect_md_files(domain_dir)

    def extract_version(self, file_path: Path) -> Optional[str]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                head = f.read(500)
        except (OSError, UnicodeDecodeError):
            return None
        ver_match = re.search(
            r"(?:版本|version|v)\s*[:：]?\s*(\d+(?:\.\d+)+)",
            head,
            re.IGNORECASE,
        )
        if ver_match:
            return ver_match.group(1)
        return None

    def extract_frontmatter(self, file_path: Path) -> Optional[dict]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            return None
        if not content.startswith("---"):
            return None
        end = content.find("---", 3)
        if end == -1:
            return None
        fm_text = content[3:end].strip()
        try:
            return yaml.safe_load(fm_text)
        except yaml.YAMLError:
            return None

    def find_duplicates(self) -> dict[str, list[Path]]:
        all_specs = self.scan_all()
        duplicates: dict[str, list[Path]] = {}
        for spec_num, paths in all_specs.items():
            if len(paths) > 1:
                duplicates[spec_num] = paths
        return duplicates
