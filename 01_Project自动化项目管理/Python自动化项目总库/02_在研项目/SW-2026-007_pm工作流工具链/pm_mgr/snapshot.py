"""Spec Snapshot operations: read registry, write to PM_SESSION."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path


SPEC_IDS = {
    "software": [
        "PROJ-016", "PRD-001", "DEV-031", "DEV-032",
        "DEV-210", "DEV-211", "DEV-220", "INT-215",
        "DEV-004", "CHG-040", "CHG-041", "PM-042",
    ],
    "plc": [
        "PROJ-016", "REQ-020", "LSP-905", "LSP-904", "LSP-903",
        "LSP-906", "LSP-907", "INT-815", "PLC-023",
        "DEV-004", "CHG-040", "CHG-041", "PM-042",
    ],
}


def read_spec_versions(workspace_root: str | Path) -> dict[str, str]:
    """Read spec versions from spec_registry.json.

    Returns dict of {spec_id: version}.
    """
    registry_path = Path(workspace_root) / "00_Obsidian_Base全局规范文件仓库" / "spec_registry.json"
    if not registry_path.is_file():
        return {}

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    versions = {}
    specs = registry.get("specs", {})
    # 动态读取所有 SPEC_IDS 中的 spec_id
    all_spec_ids = set()
    for ids in SPEC_IDS.values():
        all_spec_ids.update(ids)
    for spec_id in all_spec_ids:
        if spec_id in specs:
            versions[spec_id] = specs[spec_id].get("version", "未知")

    return versions


def fill_snapshot_in_content(content: str, project_type: str, workspace_root: str | Path) -> str:
    """Fill Spec Snapshot table in PM_SESSION content with actual versions.

    If the section exists but has placeholder versions, fill them.
    If the section does not exist, append it at the end.

    Returns modified content string.
    """
    versions = read_spec_versions(workspace_root)
    spec_ids = SPEC_IDS.get(project_type, [])
    today = date.today().isoformat()

    if has_spec_snapshot(content):
        # Section exists: replace "(待填充)" placeholders
        result = content
        for spec_id in spec_ids:
            version = versions.get(spec_id, "未知")
            result = re.sub(
                rf"\| {re.escape(spec_id)} \| \(待填充\) \|",
                f"| {spec_id} | {version} |",
                result
            )
        return result
    else:
        # Section missing: append at the end
        spec_descs = {
            "PROJ-016": "通用项目结构模板",
            "PRD-001": "产品需求文档模板",
            "DEV-031": "通用测试规范",
            "DEV-032": "GUI测试方案标准",
            "REQ-020": "通用需求分析文档模板",
            "LSP-905": "SCL编程规范",
            "DEV-210": "Python编程规范",
            "DEV-211": "Python代码审查规范",
            "DEV-220": "Python项目打包规范",
            "INT-215": "Python接口文档模板",
            "DEV-004": "通用项目文档版本管理与变更核心规范",
            "CHG-040": "通用变更单模板",
            "CHG-041": "通用版本变更台帐模板",
            "PM-042": "通用变更管理流程规范",
            "LSP-904": "SCL注释规范",
            "LSP-903": "定时器使用规范",
            "LSP-906": "PLC编程错误预防规则",
            "LSP-907": "PLC项目配置规范",
            "INT-815": "PLC接口文档模板",
            "PLC-023": "PLC程序设计文档模板",
        }
        lines = [
            "",
            "## Spec Snapshot（初始化时锁定，供后续版本漂移检测）",
            "",
            "> 以下版本号在项目初始化时从 `spec_registry.json` 读取并填入。",
            "> 本区块作为基线，后续 `specmgr check` 对比当前规范版本与快照，检测版本漂移。",
            "",
            "| spec_id | 版本 | 记录日期 | 说明 |",
            "|---------|------|---------|------|",
        ]
        for spec_id in spec_ids:
            version = versions.get(spec_id, "未知")
            desc = spec_descs.get(spec_id, "")
            lines.append(f"| {spec_id} | {version} | {today} | {desc} |")
        lines.append("")
        return content.rstrip("\n") + "\n" + "\n".join(lines)


def update_pm_session_snapshot(pm_session_path: str | Path, project_type: str, workspace_root: str | Path) -> bool:
    """Update Spec Snapshot in an existing PM_SESSION file.

    Returns True if changes were made.
    """
    pm_path = Path(pm_session_path)
    if not pm_path.is_file():
        return False

    content = pm_path.read_text(encoding="utf-8")
    new_content = fill_snapshot_in_content(content, project_type, workspace_root)

    if new_content != content:
        pm_path.write_text(new_content, encoding="utf-8")
        return True
    return False


def has_spec_snapshot(pm_session_content: str) -> bool:
    """Check if PM_SESSION content already has a Spec Snapshot section."""
    return "## Spec Snapshot" in pm_session_content
