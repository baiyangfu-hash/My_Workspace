"""Bootstrap: template rendering, directory generation, skeleton files."""

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path


# Directory structures
SW_DIRS = [
    "00_项目基础信息",
    "01_项目文档/01_启动过程",
    "01_项目文档/01_需求",
    "01_项目文档/02_规划过程",
    "01_项目文档/03_执行过程",
    "01_项目文档/04_监控和控制",
    "01_项目文档/05_收尾过程",
    "03_主程序/01_主程序核心代码/src",
    "03_主程序/01_主程序核心代码/tests",
    "resources/fonts",
    "resources/icons",
    "resources/styles",
]

PLC_DIRS = [
    "00_项目管理/01_立项与需求",
    "00_项目管理/04_变更管理/01_变更单/CHG-PLC",
    "00_项目管理/04_变更管理/01_变更单/CHG-ELEC",
    "00_项目管理/04_变更管理/01_变更单/CHG-DOCU",
    "00_项目管理/04_变更管理/04_变更记录",
    "01_需求与设计",
    "02_PLC程序/程序文档",
    "02_PLC程序/通用ST程序及变量表/DB1",
    "02_PLC程序/通用ST程序及变量表/OB1",
    "02_PLC程序/通用ST程序及变量表/common",
    "02_PLC程序/通用ST程序及变量表/conveyor",
    "02_PLC程序/通用ST程序及变量表/pickplace",
    "02_PLC程序/通用ST程序及变量表/feeder",
    "02_PLC程序/通用ST程序及变量表/external",
    "02_PLC程序/通用ST程序及变量表/Test",
    "02_PLC程序/通用ST程序及变量表/PRD-SRC",
    "03_HMI设计",
    "04_现场调试",
    "05_测试与验证",
    "06_文档与交付/05_交付资源",
    "06_文档与交付/操作手册",
    "07_技术支持",
    "08_备件管理",
    "09_项目总结",
    "10_知识库",
    "export",
]

SYS_DIRS = [
    "00_项目基础信息",
    "01_项目文档",
]

# Template mapping: source_name -> destination_path
SW_TEMPLATES = {
    "00_立项表.md": "00_项目基础信息/立项表.md",
    "01_PRD.md": "01_项目文档/01_需求/PRD.md",
    "02_REQ.md": "01_项目文档/02_规划过程/需求规格说明书.md",
    "03_DES.md": "01_项目文档/02_规划过程/详细设计说明书.md",
    "04_测试计划.md": "01_项目文档/03_执行过程/测试计划.md",
}

PLC_TEMPLATES = {
    "00_立项表.md": "00_项目管理/01_立项与需求/立项表.md",
    "01_需求分析.md": "01_需求与设计/需求分析.md",
    "02_IO分配表.md": "02_PLC程序/程序文档/IO分配表.md",
    "03_PLC设计总文档.md": "02_PLC程序/程序文档/PLC设计总文档.md",
    "04_调试计划.md": "04_现场调试/调试计划.md",
    "05_问题跟踪.md": "05_测试与验证/问题跟踪.md",
}

SYS_TEMPLATES: dict[str, str] = {}


def ensure_dir(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def replace_tokens(content: str, tokens: dict[str, str]) -> str:
    """Replace __PLACEHOLDER__ tokens in template content."""
    result = content
    for key, value in tokens.items():
        result = result.replace(key, value)
    return result


def init_project(
    project_root: str | Path,
    project_type: str,
    project_id: str,
    project_name: str,
    workspace_root: str | Path,
    owner: str = "Pending",
    one_liner: str = "Pending",
    force: bool = False,
) -> list[str]:
    """Initialize a new project from templates.

    Returns list of created/modified file paths.
    """
    root = Path(project_root).resolve()
    ws_root = Path(workspace_root).resolve()
    template_root = ws_root / ".trae" / "project-bootstrap" / project_type

    if not template_root.is_dir():
        raise FileNotFoundError(f"模板目录不存在: {template_root}")

    # Auto-create root directory if it doesn't exist
    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)

    from .detect import is_empty_dir
    if not force and not is_empty_dir(root, ignore_patterns=[".plc-out", ".git", "__pycache__", ".pytest_cache"]):
        raise FileExistsError(
            f"目录非空: {root}\n"
            f"  使用 --force 强制初始化（不会覆盖现有文件）"
        )

    created: list[str] = []
    today = date.today().isoformat()

    tokens = {
        "__PROJECT_ID__": project_id,
        "__PROJECT_NAME__": project_name,
        "__PROJECT_ROOT__": str(root),
        "__DATE__": today,
        "__OWNERS__": owner,
        "__ONE_LINER__": one_liner,
        "__USERS__": "Pending",
        "__NON_GOALS__": "Pending",
        "__KEY_PRINCIPLE__": "Pending",
    }

    # 1. PM_SESSION
    pm_template_path = template_root / "PM_SESSION_TEMPLATE.md"
    if pm_template_path.is_file():
        content = pm_template_path.read_text(encoding="utf-8")
        content = replace_tokens(content, tokens)

        from .snapshot import fill_snapshot_in_content
        content = fill_snapshot_in_content(content, project_type, ws_root)

        pm_session_path = root / f"PM_SESSION_{project_id}.md"
        if not pm_session_path.exists() or force:
            pm_session_path.write_text(content, encoding="utf-8")
            created.append(str(pm_session_path))

    # 2. Copy hooks
    hooks_src = template_root / "hooks"
    hooks_dst = root / ".github" / "hooks"
    if hooks_src.is_dir() and not hooks_dst.exists():
        shutil.copytree(hooks_src, hooks_dst)
        created.append(str(hooks_dst))

    # 3. Create handoffs dir
    handoffs_dir = root / ".trae" / "handoffs"
    if not handoffs_dir.exists():
        ensure_dir(handoffs_dir)
        created.append(str(handoffs_dir))

    # 4. Create directory structure
    if project_type == "software":
        dirs = SW_DIRS
    elif project_type == "plc":
        dirs = PLC_DIRS
    elif project_type == "sys":
        dirs = SYS_DIRS
    else:
        raise ValueError(f"Unsupported project_type: {project_type}")
    for d in dirs:
        dir_path = root / d
        if not dir_path.exists():
            ensure_dir(dir_path)
            created.append(str(dir_path))

    # 5. Generate skeleton files
    created.extend(_gen_skeleton_files(root, project_type, project_id, project_name, owner, one_liner, today, tokens, force, ws_root))

    # 6. Copy document templates
    if project_type == "software":
        templates_map = SW_TEMPLATES
    elif project_type == "plc":
        templates_map = PLC_TEMPLATES
    elif project_type == "sys":
        templates_map = SYS_TEMPLATES
    else:
        raise ValueError(f"Unsupported project_type: {project_type}")
    templates_src = template_root / "templates"
    for src_name, dst_rel in templates_map.items():
        src_path = templates_src / src_name
        dst_path = root / dst_rel
        if src_path.is_file() and (not dst_path.exists() or force):
            tpl_content = src_path.read_text(encoding="utf-8")
            tpl_content = replace_tokens(tpl_content, tokens)
            ensure_dir(dst_path.parent)
            dst_path.write_text(tpl_content, encoding="utf-8")
            created.append(str(dst_path))

    return created


def _gen_skeleton_files(
    root: Path,
    project_type: str,
    project_id: str,
    project_name: str,
    owner: str,
    one_liner: str,
    today: str,
    tokens: dict[str, str],
    force: bool,
    workspace_root: Path,
) -> list[str]:
    """Generate skeleton files (README, pyproject.toml, .plc.json, etc.)."""
    created: list[str] = []

    # README
    readme_path = root / "README.md"
    if not readme_path.exists() or force:
        from .snapshot import read_spec_versions
        versions = read_spec_versions(workspace_root)
        _write_readme(readme_path, project_type, project_id, project_name, owner, one_liner, today, versions)
        created.append(str(readme_path))

    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists() or force:
        gitignore_path.write_text(".venv/\n__pycache__/\n.pytest_cache/\n.DS_Store\n", encoding="utf-8")
        created.append(str(gitignore_path))

    if project_type == "software":
        created.extend(_gen_software_skeleton(root, project_id, one_liner, force))
    elif project_type == "plc":
        created.extend(_gen_plc_skeleton(root, project_id, project_name, owner, one_liner, today, force))
    elif project_type == "sys":
        created.extend(_gen_sys_skeleton(root, project_id, project_name, owner, one_liner, today, force))
    else:
        raise ValueError(f"Unsupported project_type: {project_type}")

    return created


def _write_readme(
    path: Path,
    project_type: str,
    project_id: str,
    project_name: str,
    owner: str,
    one_liner: str,
    today: str,
    spec_versions: dict[str, str],
) -> None:
    """Write README.md skeleton."""
    if project_type == "software":
        type_label = "软件/产品化项目"
        tree = """```
├── 00_项目基础信息/     # 立项表、项目章程
├── 01_项目文档/         # PRD、DES、API、测试文档
├── 03_主程序/           # 源代码、测试
├── resources/           # 字体、图标、样式
├── .github/hooks/       # 协作自动化
└── PM_SESSION_*.md      # 项目状态单一真源
```"""
        specs = f"- `PROJ-016` 通用项目结构模板 (V{spec_versions.get('PROJ-016', '?')})\n- `PRD-001` 产品需求文档模板 (V{spec_versions.get('PRD-001', '?')})\n- `DEV-031` 通用测试规范 (V{spec_versions.get('DEV-031', '?')})\n- `DEV-032` GUI测试方案标准 (V{spec_versions.get('DEV-032', '?')})"
    elif project_type == "plc":
        type_label = "PLC/电气交付项目"
        tree = """```
├── 00_项目管理/         # 立项、需求、变更管理
├── 01_需求与设计/       # 需求规格、方案设计
├── 02_PLC程序/          # PLC源码、程序文档
├── 03_HMI设计/          # HMI源程序与文档
├── 04_现场调试/         # 调试计划、问题跟踪
├── 05_测试与验证/       # 测试报告
├── 06_文档与交付/       # 操作手册、交付清单
├── .github/hooks/       # 协作自动化
└── PM_SESSION_*.md      # 项目状态单一真源
```"""
        specs = f"- `PROJ-016` 通用项目结构模板 (V{spec_versions.get('PROJ-016', '?')})\n- `REQ-020` 通用需求分析文档模板 (V{spec_versions.get('REQ-020', '?')})\n- PLC编程规范 (参考 `0100_PLC自动化/00_通用规范/`)"
    elif project_type == "sys":
        type_label = "系统级治理项目"
        tree = """```
├── 00_项目基础信息/     # 项目章程、基本信息
├── 01_项目文档/         # 方案、路线图、风险、准入规则
├── .github/hooks/       # 协作自动化
├── .trae/handoffs/      # 会话交接草稿
└── PM_SESSION_*.md      # 项目状态单一真源
```"""
        specs = (
            f"- `DEV-001` 通用项目名称命名规范 (V{spec_versions.get('DEV-001', '?')})\n"
            f"- `DEV-002` 通用项目工作流命名规范 (V{spec_versions.get('DEV-002', '?')})\n"
            f"- `DEV-003` 跨资源库命名统一规范 (V{spec_versions.get('DEV-003', '?')})\n"
            f"- `PM-004` PM_WORKFLOW总控Skill使用说明 (V{spec_versions.get('PM-004', '?')})\n"
            f"- `PROJ-016` 通用项目结构模板 (V{spec_versions.get('PROJ-016', '?')})"
        )
    else:
        raise ValueError(f"Unsupported project_type: {project_type}")

    content = f"""# {project_name}

- **项目编号**: {project_id}
- **项目类型**: {type_label}
- **创建日期**: {today}
- **负责人**: {owner}

## 项目简介

{one_liner}

## 目录结构

{tree}

## 参考规范

{specs}
"""
    path.write_text(content, encoding="utf-8")


def _gen_software_skeleton(root: Path, project_id: str, one_liner: str, force: bool) -> list[str]:
    """Generate software project skeleton files."""
    created: list[str] = []
    py_dir = root / "03_主程序" / "01_主程序核心代码"

    # pyproject.toml
    pyproject_path = py_dir / "pyproject.toml"
    if not pyproject_path.exists() or force:
        content = f"""[project]
name = "{project_id}"
version = "0.1.0"
description = "{one_liner}"
requires-python = ">=3.11"

[project.scripts]
# TODO: 添加入口脚本

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
        pyproject_path.write_text(content, encoding="utf-8")
        created.append(str(pyproject_path))

    # __init__.py
    for sub in ["src", "tests"]:
        init_path = py_dir / sub / "__init__.py"
        if not init_path.exists() or force:
            init_path.write_text(f"# {project_id}\n", encoding="utf-8")
            created.append(str(init_path))

    # .gitkeep
    for sub in ["fonts", "icons"]:
        gk = root / "resources" / sub / ".gitkeep"
        if not gk.exists():
            gk.touch()
            created.append(str(gk))

    return created


def _gen_plc_skeleton(root: Path, project_id: str, project_name: str, owner: str, one_liner: str, today: str, force: bool) -> list[str]:
    """Generate PLC project skeleton files."""
    created: list[str] = []

    # .plc.json
    plc_json_path = root / "02_PLC程序" / "通用ST程序及变量表" / ".plc.json"
    if not plc_json_path.exists() or force:
        content = f"""{{
  "project_id": "{project_id}",
  "project_name": "{project_name}",
  "version": "0.1.0",
  "plc_model": "待确认",
  "description": "{one_liner}"
}}
"""
        plc_json_path.write_text(content, encoding="utf-8")
        created.append(str(plc_json_path))

    # 版本变更台帐
    ledger_dir = root / "00_项目管理" / "04_变更管理" / "04_变更记录"
    ledger_path = ledger_dir / "00_版本变更台帐.md"
    if not ledger_path.exists() or force:
        content = f"""# 版本变更台帐

| 序号 | 变更单号 | 日期 | 变更类型 | 变更原因 | 变更内容 | 版本 | 变更人员 |
|------|---------|------|----------|----------|----------|------|----------|
| 1 | | {today} | 初始创建 | 项目初始化 | 创建项目骨架 | V0.1.0 | {owner} |
"""
        ledger_path.write_text(content, encoding="utf-8")
        created.append(str(ledger_path))

    return created


def _gen_sys_skeleton(root: Path, project_id: str, project_name: str, owner: str, one_liner: str, today: str, force: bool) -> list[str]:
    created: list[str] = []
    charter_path = root / "00_项目基础信息" / "01_项目章程_PM.md"
    if not charter_path.exists() or force:
        content = f"""# {project_name} 项目章程

| 字段 | 内容 |
|------|------|
| 项目编号 | {project_id} |
| 项目名称 | {project_name} |
| 启动日期 | {today} |
| 负责人 | {owner} |

## 项目简介

{one_liner}
"""
        ensure_dir(charter_path.parent)
        charter_path.write_text(content, encoding="utf-8")
        created.append(str(charter_path))
    return created
