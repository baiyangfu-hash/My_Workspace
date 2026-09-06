"""NG-WP-15 isolated release-entry acceptance tests."""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

import pytest

LAUNCHER_DIR = Path(__file__).resolve().parents[1] / "00_Infrastructure" / "auto_pm" / "launcher"
sys.path.insert(0, str(LAUNCHER_DIR))
from bootstrap import (
    ACTIVE_POINTER,
    EXIT_POINTER_INVALID,
    EXIT_RELEASE_INVALID,
    MANIFEST_FILE,
    MANIFEST_SCHEMA,
    POINTER_SCHEMA,
    PREVIOUS_POINTER,
    RELEASES_DIR,
    BootstrapError,
    resolve_with_fallback,
)
from launch import main as launcher_main


def _pointer(release_id: str | None) -> dict[str, object]:
    return {"schema_version": POINTER_SCHEMA, "slot": "", "release_id": release_id}


def _write_pointer(root: Path, name: str, release_id: str | None) -> None:
    payload = _pointer(release_id)
    payload["slot"] = name
    (root / name).write_text(json.dumps(payload), encoding="utf-8")


def _add_release(root: Path, release_id: str, *, marker_program: bool = False) -> dict[str, str]:
    release = root / RELEASES_DIR / release_id
    package = release / "auto_pm"
    package.mkdir(parents=True, exist_ok=True)
    (package / "__init__.py").write_text("__version__ = 'test'\n", encoding="utf-8")
    if marker_program:
        program = (
            "import os\nfrom pathlib import Path\n"
            "Path(os.environ['AUTO_PM_TEST_MARKER']).write_text(str(Path(__file__).resolve()), encoding='utf-8')\n"
        )
    else:
        program = "raise SystemExit(0)\n"
    (package / "__main__.py").write_text(program, encoding="utf-8")
    files: dict[str, str] = {}
    for path in release.rglob("*"):
        if path.is_file():
            files[path.relative_to(release).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def _container(tmp_path: Path, active: str | None = "active", previous: str | None = None) -> tuple[Path, dict[str, dict[str, str]]]:
    root = tmp_path / "container"
    (root / RELEASES_DIR).mkdir(parents=True)
    releases = {"active": _add_release(root, "active"), "previous": _add_release(root, "previous")}
    (root / MANIFEST_FILE).write_text(
        json.dumps({"schema_version": MANIFEST_SCHEMA, "releases": {key: {"files": value} for key, value in releases.items()}}),
        encoding="utf-8",
    )
    _write_pointer(root, ACTIVE_POINTER, active)
    _write_pointer(root, PREVIOUS_POINTER, previous)
    return root, releases


def test_valid_release_executes_only_from_verified_release(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, releases = _container(tmp_path)
    releases["active"] = _add_release(root, "active", marker_program=True)
    (root / MANIFEST_FILE).write_text(
        json.dumps({"schema_version": MANIFEST_SCHEMA, "releases": {key: {"files": value} for key, value in releases.items()}}),
        encoding="utf-8",
    )
    marker = tmp_path / "provenance.txt"
    monkeypatch.setenv("AUTO_PM_TEST_MARKER", str(marker))
    monkeypatch.setenv("PYTHONPATH", str(tmp_path / "untrusted"))
    assert launcher_main([], container=root) == 0
    assert marker.read_text(encoding="utf-8") == str((root / RELEASES_DIR / "active" / "auto_pm" / "__main__.py").resolve())
    assert not list((root / RELEASES_DIR / "active").rglob("__pycache__"))


def test_tampered_active_release_fails_closed(tmp_path: Path) -> None:
    root, _ = _container(tmp_path, previous=None)
    (root / RELEASES_DIR / "active" / "auto_pm" / "__init__.py").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(BootstrapError, match="SHA-256 不匹配") as error:
        resolve_with_fallback(root)
    assert error.value.exit_code == EXIT_RELEASE_INVALID


def test_extra_payload_node_fails_closed(tmp_path: Path) -> None:
    root, _ = _container(tmp_path, previous=None)
    (root / RELEASES_DIR / "active" / "unexpected.txt").write_text("extra", encoding="utf-8")
    with pytest.raises(BootstrapError, match="未登记文件") as error:
        resolve_with_fallback(root)
    assert error.value.exit_code == EXIT_RELEASE_INVALID


def test_null_pointers_fail_closed(tmp_path: Path) -> None:
    root, _ = _container(tmp_path, active=None, previous=None)
    with pytest.raises(BootstrapError, match="未初始化") as error:
        resolve_with_fallback(root)
    assert error.value.exit_code == EXIT_POINTER_INVALID


def test_invalid_active_falls_back_to_exact_verified_previous(tmp_path: Path) -> None:
    root, _ = _container(tmp_path, active="active", previous="previous")
    (root / RELEASES_DIR / "active" / "extra.txt").write_text("extra", encoding="utf-8")
    release, slot = resolve_with_fallback(root)
    assert slot == PREVIOUS_POINTER
    assert release == (root / RELEASES_DIR / "previous").resolve()


def test_payload_symlink_or_reparse_fails_closed(tmp_path: Path) -> None:
    root, _ = _container(tmp_path, previous=None)
    link = root / RELEASES_DIR / "active" / "payload-link"
    try:
        link.symlink_to(root / RELEASES_DIR / "active" / "auto_pm", target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"host disallows symlink creation: {exc}")
    with pytest.raises(BootstrapError, match="链接或重解析点"):
        resolve_with_fallback(root)


def test_root_entry_has_no_parent_auto_pm_import() -> None:
    root_entry = Path(__file__).resolve().parents[1] / "main.py"
    tree = ast.parse(root_entry.read_text(encoding="utf-8"))
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_modules.update(
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    )
    assert not any(name == "auto_pm" or name.startswith("auto_pm.") for name in imported_modules)
