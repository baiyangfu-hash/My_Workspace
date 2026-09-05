#!/usr/bin/env python3
"""Dual-slot deployment launcher skeleton (NG-WP-12, fail-closed).

Resolution-only stage of the stable container launcher: it validates the
container layout, reads the ``active_release.json`` pointer, checks the
release-id, enforces ``releases/`` containment and requires the release to be
listed in ``deployment_manifest.json``.  Real release execution is wired by a
later work package; until then the launcher exits non-zero before running any
release code, so this script can never silently start unverified content.

Exit codes:
    0  active release resolved and manifest-listed (resolution only)
    2  container layout invalid
    3  active pointer uninitialized or unreadable
    4  active release invalid, escaping releases/ or not manifest-listed
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import NoReturn

RELEASE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
MANIFEST_SCHEMA = "deployment_manifest.v1"
POINTER_SCHEMA = "release_pointer.v1"
ACTIVE_POINTER = "active_release.json"
MANIFEST_FILE = "deployment_manifest.json"
RELEASES_DIR = "releases"


def _fail(code: int, message: str) -> NoReturn:
    print(f"launcher: {message}", file=sys.stderr)
    raise SystemExit(code)


def _read_active_pointer(container: Path) -> str | None:
    path = container / ACTIVE_POINTER
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail(3, f"active pointer unreadable: {exc}")
    if not isinstance(raw, dict) or raw.get("schema_version") != POINTER_SCHEMA:
        _fail(3, "active pointer schema mismatch")
    release_id = raw.get("release_id")
    if release_id is None:
        return None
    if not isinstance(release_id, str):
        _fail(3, "active pointer release_id must be a string or null")
    return release_id


def _resolve_active(container: Path) -> Path:
    if not container.is_dir() or not (container / RELEASES_DIR).is_dir():
        _fail(2, f"container layout invalid: {container}")
    release_id = _read_active_pointer(container)
    if release_id is None:
        _fail(3, "active release not initialized (pointer is null)")
    if not RELEASE_ID_PATTERN.fullmatch(release_id):
        _fail(4, f"illegal release id: {release_id!r}")
    candidate = container / RELEASES_DIR / release_id
    resolved = candidate.resolve()
    releases_root = (container / RELEASES_DIR).resolve()
    if os.path.islink(candidate) or not resolved.is_relative_to(releases_root):
        _fail(4, f"release path escapes releases/: {release_id!r}")
    if not resolved.is_dir():
        _fail(4, f"release directory missing: {release_id!r}")
    try:
        manifest = json.loads((container / MANIFEST_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail(4, f"deployment manifest unreadable: {exc}")
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version") != MANIFEST_SCHEMA
        or not isinstance(manifest.get("releases"), dict)
        or release_id not in manifest["releases"]
    ):
        _fail(4, f"release not listed in deployment manifest: {release_id!r}")
    return resolved


def main() -> int:
    container = Path(__file__).resolve().parent.parent
    release_dir = _resolve_active(container)
    print(f"launcher: active release resolved: {release_dir}")
    print("launcher: skeleton mode - release execution is not wired yet (NG-WP-13/15)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
