"""Obsidian 规范库死链扫描器 (DeadLinkChecker)

基于 CHG-SPEC-2026-001 终验口径下沉：
- 严格冷热隔离 (Spec-Isolation-001)：Archive_Cold 与 .trae 判定为冷区，仅登记不阻断
- 剔除代码块与行内代码误报
- 识别 Wiki 链接 [[...]] 与 Markdown 链接 [...](...)
- 校验同页锚点与跨页锚点是否存在于目标文件的真实标题中
- 活跃区死链数为 0 时判定 PASS
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

FENCE_RE = re.compile(r"```[\s\S]*?```")
INLINE_RE = re.compile(r"`[^`\n]*`")
WIKI_RE = re.compile(r"\[\[([^\]|#]+)(?:[^\]]*)\]\]")
MDLINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEAD_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
V2_TOKENS = (
    "02_规划过程",
    "01_启动过程",
    "03_执行过程",
    "04_监控和控制",
    "05_收尾过程",
    "0100_PLC自动化",
)


def norm_anchor(s: str) -> str:
    """规范化锚点字符串：去除空格转连字符，去除特殊标点，小写。"""
    s = s.strip().lower()
    s = re.sub(r"[\s\u3000]+", "-", s)
    s = re.sub(r"[^\w\u4e00-\u9fff\-]", "", s)
    return s


def headings_of(text: str) -> list[str]:
    """提取 Markdown 文本中所有标题内容。"""
    out: list[str] = []
    for line in text.splitlines():
        m = HEAD_RE.match(line)
        if m:
            out.append(m.group(2))
    return out


@dataclass(frozen=True)
class DeadLinkItem:
    src: str
    zone: str  # "active" | "cold"
    kind: str  # "wiki" | "md"
    target: str
    error_class: str


@dataclass
class DeadLinkScanReport:
    total_scanned_files: int
    active_deadlinks: list[DeadLinkItem] = field(default_factory=list)
    cold_deadlinks: list[DeadLinkItem] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.active_deadlinks) == 0


class DeadLinkChecker:
    """Obsidian 规范库死链扫描器。"""

    def __init__(self, lib_dir: Path | str) -> None:
        self.lib_dir = Path(lib_dir)

    def scan(self) -> DeadLinkScanReport:
        if not self.lib_dir.is_dir():
            return DeadLinkScanReport(total_scanned_files=0)

        md_files: dict[str, Path] = {}
        for root, dirs, files in os.walk(self.lib_dir):
            dirs[:] = [d for d in dirs if d not in (".git", ".obsidian", ".pytest_cache")]
            for fn in files:
                if fn.lower().endswith(".md"):
                    full = Path(root) / fn
                    try:
                        rel = full.relative_to(self.lib_dir).as_posix()
                    except ValueError:
                        rel = str(full)
                    md_files[rel] = full

        texts: dict[str, str] = {}
        for rel, full in md_files.items():
            try:
                texts[rel] = full.read_text(encoding="utf-8", errors="replace")
            except OSError:
                texts[rel] = ""

        basename_map: dict[str, list[str]] = {}
        for rel in md_files:
            stem = Path(rel).stem
            basename_map.setdefault(stem, []).append(rel)

        heading_anchor_index: dict[str, set[str]] = {}
        for rel, t in texts.items():
            heading_anchor_index[rel] = {norm_anchor(h) for h in headings_of(t)}

        def resolve_wiki(tgt: str, src_rel: str) -> str | None:
            t = tgt.strip()
            t2 = t[:-3] if t.endswith(".md") else t
            if t2 in basename_map:
                cands = basename_map[t2]
                if len(cands) == 1:
                    return cands[0]
                src_dir = os.path.dirname(src_rel)
                for c in cands:
                    if os.path.dirname(c) == src_dir:
                        return c
                return cands[0]
            hits = [r for r in md_files if r.endswith("/" + t2 + ".md")]
            if len(hits) == 1:
                return hits[0]
            return None

        def resolve_md(tgt: str, src_rel: str) -> str | None:
            path_part, _, _ = tgt.partition("#")
            if not path_part:
                return "SELF"
            p = path_part.replace("%20", " ")
            if re.match(r"^[a-zA-Z]+://", p) or p.startswith("mailto:"):
                return "URL"
            norm = os.path.normpath(os.path.join(os.path.dirname(src_rel), p)).replace("\\", "/")
            if norm in md_files:
                return norm
            return None

        def md_path_stale(tgt: str) -> bool:
            path_part = tgt.split("#")[0]
            if not path_part:
                return False
            stem = Path(path_part).stem
            return stem in basename_map

        def classify(target: str, resolved_rel: str | None, anchor: str, stale_path: bool = False) -> str:
            if stale_path:
                return "stale-path"
            if resolved_rel is not None and anchor:
                want = norm_anchor(anchor)
                if want and want in heading_anchor_index.get(resolved_rel, set()):
                    return "ok"
                return "anchor-missing"
            if resolved_rel is None:
                if any(tok in target for tok in V2_TOKENS):
                    return "v2-path"
                stem = Path(target).stem
                if (
                    re.match(r"^[123]-", stem)
                    or re.search(r"-V\d", target)
                    or re.search(r"_V\d+\.\d+\.\d+\.md", target)
                ):
                    return "version-snapshot"
                if target.endswith((".png", ".mmd", ".svg", ".jpg")):
                    return "missing-asset"
                if "CHG-XXX" in target or "相对路径" in target or "图表名称" in target or "XXX" in target:
                    return "example-placeholder"
                if target.startswith("#"):
                    return "anchor-missing"
                return "unresolved"
            return "ok"

        active_deadlinks: list[DeadLinkItem] = []
        cold_deadlinks: list[DeadLinkItem] = []

        for rel in sorted(md_files):
            zone = "cold" if ("Archive_Cold" in rel or rel.startswith(".trae/")) else "active"
            raw_text = texts[rel]
            body = FENCE_RE.sub("", raw_text)
            body = INLINE_RE.sub("", body)

            # 1. 扫描 WikiLink
            for m in WIKI_RE.finditer(body):
                tgt = m.group(1).strip()
                r = resolve_wiki(tgt, rel)
                if r is None:
                    cls = classify(tgt, None, "")
                    item = DeadLinkItem(src=rel, zone=zone, kind="wiki", target=tgt, error_class=cls)
                    if zone == "active":
                        active_deadlinks.append(item)
                    else:
                        cold_deadlinks.append(item)

            # 2. 扫描 MD 链接
            for m in MDLINK_RE.finditer(body):
                tgt = m.group(1).strip()
                if re.match(r"^[a-zA-Z]+://", tgt) or tgt.startswith("mailto:"):
                    continue
                path_part, _, anchor = tgt.partition("#")
                r = resolve_md(tgt, rel)
                if r == "URL":
                    continue
                stale = (r is None) and md_path_stale(tgt)
                if r == "SELF":
                    r = rel
                cls = classify(path_part or ("#" + anchor), r, anchor, stale_path=stale)
                if cls != "ok":
                    item = DeadLinkItem(src=rel, zone=zone, kind="md", target=tgt, error_class=cls)
                    if zone == "active":
                        active_deadlinks.append(item)
                    else:
                        cold_deadlinks.append(item)

        return DeadLinkScanReport(
            total_scanned_files=len(md_files),
            active_deadlinks=active_deadlinks,
            cold_deadlinks=cold_deadlinks,
        )
