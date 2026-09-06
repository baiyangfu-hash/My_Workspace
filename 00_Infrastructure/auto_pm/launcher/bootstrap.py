"""Stdlib-only, fail-closed release resolution and exact-tree verification."""
from __future__ import annotations

import hashlib
import json
import re
import stat
from pathlib import Path

RELEASE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
POINTER_SCHEMA = "release_pointer.v1"
MANIFEST_SCHEMA = "deployment_manifest.v1"
ACTIVE_POINTER = "active_release.json"
PREVIOUS_POINTER = "previous_release.json"
MANIFEST_FILE = "deployment_manifest.json"
RELEASES_DIR = "releases"
_FILE_ATTRIBUTE_REPARSE_POINT = 0x0400

EXIT_CONTAINER_INVALID = 2
EXIT_POINTER_INVALID = 3
EXIT_RELEASE_INVALID = 4


class BootstrapError(Exception):
    """Resolution failure carrying a fail-closed process exit code."""

    def __init__(self, exit_code: int, message: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def _is_link_or_reparse(path: Path) -> bool:
    """Identify a symlink or Windows reparse point without following it."""
    try:
        info = path.lstat()
    except OSError:
        return True
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & _FILE_ATTRIBUTE_REPARSE_POINT
    )


def _read_pointer_release_id(container: Path, name: str) -> str | None:
    path = container / name
    if _is_link_or_reparse(path):
        raise BootstrapError(EXIT_POINTER_INVALID, f"{name} 不允许链接或重解析点")
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BootstrapError(EXIT_POINTER_INVALID, f"{name} 无法读取: {exc}") from exc
    if not isinstance(raw, dict) or raw.get("schema_version") != POINTER_SCHEMA:
        raise BootstrapError(EXIT_POINTER_INVALID, f"{name} schema 不符")
    release_id = raw.get("release_id")
    if release_id is None:
        return None
    if not isinstance(release_id, str):
        raise BootstrapError(EXIT_POINTER_INVALID, f"{name} release_id 必须是字符串或 null")
    return release_id


def _manifest_files(container: Path, release_id: str) -> dict[str, str]:
    manifest_path = container / MANIFEST_FILE
    if _is_link_or_reparse(manifest_path):
        raise BootstrapError(EXIT_RELEASE_INVALID, "deployment manifest 不允许链接或重解析点")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BootstrapError(EXIT_RELEASE_INVALID, f"deployment manifest 无法读取: {exc}") from exc
    releases = manifest.get("releases") if isinstance(manifest, dict) else None
    entry = releases.get(release_id) if isinstance(releases, dict) else None
    files = entry.get("files") if isinstance(entry, dict) else None
    if not isinstance(manifest, dict) or manifest.get("schema_version") != MANIFEST_SCHEMA or not isinstance(files, dict):
        raise BootstrapError(EXIT_RELEASE_INVALID, f"release 未登记于 manifest: {release_id!r}")
    parsed: dict[str, str] = {}
    for raw_path, digest in files.items():
        if not isinstance(raw_path, str) or not isinstance(digest, str):
            raise BootstrapError(EXIT_RELEASE_INVALID, "manifest files 必须为字符串映射")
        requested = Path(raw_path)
        if requested.is_absolute() or requested == Path(".") or ".." in requested.parts:
            raise BootstrapError(EXIT_RELEASE_INVALID, f"manifest 路径越界: {raw_path!r}")
        normalized = requested.as_posix()
        if normalized in parsed or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise BootstrapError(EXIT_RELEASE_INVALID, f"manifest 条目无效: {raw_path!r}")
        parsed[normalized] = digest
    return parsed


def _verify_exact_tree(release_dir: Path, files: dict[str, str]) -> None:
    """Require every payload node to match the manifest-derived exact tree."""
    expected_files = set(files)
    expected_dirs: set[str] = set()
    for raw_path, expected_digest in files.items():
        requested = Path(raw_path)
        target = release_dir / requested
        if _is_link_or_reparse(target):
            raise BootstrapError(EXIT_RELEASE_INVALID, f"release 节点不允许链接或重解析点: {raw_path}")
        try:
            info = target.lstat()
        except OSError as exc:
            raise BootstrapError(EXIT_RELEASE_INVALID, f"release 文件缺失: {raw_path}") from exc
        if not stat.S_ISREG(info.st_mode):
            raise BootstrapError(EXIT_RELEASE_INVALID, f"release 节点不是普通文件: {raw_path}")
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected_digest:
            raise BootstrapError(EXIT_RELEASE_INVALID, f"release SHA-256 不匹配: {raw_path}")
        parent = requested.parent
        while parent != Path("."):
            expected_dirs.add(parent.as_posix())
            parent = parent.parent

    pending = [release_dir]
    while pending:
        directory = pending.pop()
        try:
            children = list(directory.iterdir())
        except OSError as exc:
            raise BootstrapError(EXIT_RELEASE_INVALID, f"release 目录无法枚举: {directory}") from exc
        for child in children:
            relative = child.relative_to(release_dir).as_posix()
            if _is_link_or_reparse(child):
                raise BootstrapError(EXIT_RELEASE_INVALID, f"release 节点不允许链接或重解析点: {relative}")
            try:
                mode = child.lstat().st_mode
            except OSError as exc:
                raise BootstrapError(EXIT_RELEASE_INVALID, f"release 节点无法读取: {relative}") from exc
            if stat.S_ISDIR(mode):
                if relative not in expected_dirs:
                    raise BootstrapError(EXIT_RELEASE_INVALID, f"release 存在未登记目录: {relative}")
                pending.append(child)
            elif stat.S_ISREG(mode):
                if relative not in expected_files:
                    raise BootstrapError(EXIT_RELEASE_INVALID, f"release 存在未登记文件: {relative}")
            else:
                raise BootstrapError(EXIT_RELEASE_INVALID, f"release 存在非普通节点: {relative}")


def _resolve_slot(container: Path, slot: str, release_id: str) -> Path:
    if not RELEASE_ID_PATTERN.fullmatch(release_id):
        raise BootstrapError(EXIT_RELEASE_INVALID, f"{slot} 非法 release-id: {release_id!r}")
    releases_root = container / RELEASES_DIR
    if _is_link_or_reparse(releases_root):
        raise BootstrapError(EXIT_CONTAINER_INVALID, "releases 目录不允许链接或重解析点")
    candidate = releases_root / release_id
    if _is_link_or_reparse(candidate):
        raise BootstrapError(EXIT_RELEASE_INVALID, f"{slot} release 不允许链接或重解析点")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(releases_root.resolve())
    except ValueError as exc:
        raise BootstrapError(EXIT_RELEASE_INVALID, f"{slot} release 路径越界: {release_id!r}") from exc
    if not resolved.is_dir():
        raise BootstrapError(EXIT_RELEASE_INVALID, f"{slot} release 目录缺失: {release_id!r}")
    _verify_exact_tree(resolved, _manifest_files(container, release_id))
    return resolved


def resolve_slot(container: Path, slot: str) -> tuple[Path, str]:
    if slot not in (ACTIVE_POINTER, PREVIOUS_POINTER):
        raise BootstrapError(EXIT_POINTER_INVALID, f"未知指针: {slot!r}")
    if _is_link_or_reparse(container) or not container.is_dir():
        raise BootstrapError(EXIT_CONTAINER_INVALID, f"容器布局无效: {container}")
    release_id = _read_pointer_release_id(container, slot)
    if release_id is None:
        raise BootstrapError(EXIT_POINTER_INVALID, f"{slot} 未初始化（release_id 为 null）")
    return _resolve_slot(container, slot, release_id), slot


def resolve_with_fallback(container: Path) -> tuple[Path, str]:
    """Resolve active then previous; every resolved release is exact-verified."""
    failures: list[tuple[int, str]] = []
    for slot in (ACTIVE_POINTER, PREVIOUS_POINTER):
        try:
            return resolve_slot(container, slot)
        except BootstrapError as exc:
            failures.append((exc.exit_code, f"[{slot}] {exc}"))
    worst = max(code for code, _ in failures)
    raise BootstrapError(worst, "双槽均无效: " + " | ".join(message for _, message in failures))
