"""python 子命令组 - Python 项目管理

Commands:
    init <ID> --name <NAME>   创建 Python 项目骨架（Copier python-tool 模板）
    check <ID>                检查 Python 项目规范（210/211/220）
"""

from __future__ import annotations

import json
import os
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from auto_pm.app_context import AppContext
from auto_pm.core.project_service import ProjectService
from auto_pm.core.template_service import TemplateService

console = Console()


# Python 项目规范必需文件（210 规范）
_REQUIRED_FILES = [
    "pyproject.toml",
    "README.md",
    ".copier-answers.yml",
    ".ruff.toml",
    ".pre-commit-config.yaml",
    "Taskfile.yml",
]

# Python 项目规范必需目录
_REQUIRED_DIRS = ["tests", "00_项目基础信息"]


@click.group(name="python")
@click.pass_context
def python_group(ctx: click.Context) -> None:
    """Python 项目管理 - 初始化/检查（210/211/220 规范）"""


@python_group.command(name="init")
@click.argument("project_id")
@click.option("--name", "project_name", required=True, help="项目名称")
@click.option("--desc", "description", default="", help="项目描述")
@click.option("--package", "package_name", default=None, help="Python 包名（默认从项目名生成）")
@click.option("--author", default="fubai", help="作者名")
@click.option("--dry-run", is_flag=True, help="仅预览，不实际创建")
@click.pass_context
def cmd_init(
    ctx: click.Context,
    project_id: str,
    project_name: str,
    description: str,
    package_name: str | None,
    author: str,
    dry_run: bool,
) -> None:
    """创建 Python 项目骨架（调用 Copier python-tool 模板）"""
    app_ctx: AppContext = ctx.obj

    # 推导 package_name 和 cli_command
    if package_name is None:
        package_name = project_name.replace(" ", "_").lower()
    cli_command = package_name.replace("_", "-")

    # 目标路径
    project_dir = f"{project_id}_{project_name}"
    dest_path = os.path.join(app_ctx.workspace_root, project_dir)

    if os.path.exists(dest_path):
        console.print(f"[red]错误: 目标路径已存在: {dest_path}[/red]")
        ctx.exit(1)

    if dry_run:
        console.print(f"[yellow][DRY-RUN] 将创建 Python 项目: {dest_path}[/yellow]")
        console.print("  模板: python-tool")
        console.print(f"  编号: {project_id}")
        console.print(f"  名称: {project_name}")
        console.print(f"  包名: {package_name}")
        console.print(f"  CLI 命令: {cli_command}")
        return

    # 调用 Copier 模板
    tpl_svc = TemplateService(app_ctx.templates_dir)
    data: dict[str, Any] = {
        "project_id": project_id,
        "project_name": project_name,
        "package_name": package_name,
        "cli_command": cli_command,
        "description": description or project_name,
        "author": author,
        "version": "0.1.0",
    }

    try:
        tpl_svc.copy_template("python-tool", dest_path, data)
        console.print(f"[green]Python 项目创建成功: {dest_path}[/green]")
        console.print(f"  项目编号: {project_id}")
        console.print(f"  项目名称: {project_name}")
        console.print(f"  包名: {package_name}")
        console.print(f"  CLI 命令: {cli_command}")
    except FileNotFoundError as e:
        console.print(f"[red]错误: 模板不存在 - {e}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]创建失败: {e}[/red]")
        ctx.exit(1)


@python_group.command(name="check")
@click.argument("project_id", required=False)
@click.option("--all", "check_all", is_flag=True, help="检查工作空间所有 Python 项目")
@click.option("--json", "output_json", is_flag=True, help="以JSON格式输出结果")
@click.pass_context
def cmd_check(
    ctx: click.Context,
    project_id: str | None,
    check_all: bool,
    output_json: bool,
) -> None:
    """检查 Python 项目规范（210/211/220）"""
    app_ctx: AppContext = ctx.obj
    svc = ProjectService(app_ctx.workspace_root)

    # 确定检查目标
    if check_all:
        all_projects = svc.list_projects()
        targets = [p for p in all_projects if p.stack == "python"]
        if not targets:
            console.print("[yellow]未发现 Python 项目[/yellow]")
            return
    elif project_id:
        proj = svc.get_project(project_id)
        if proj is None:
            console.print(f"[red]错误: 项目不存在: {project_id}[/red]")
            ctx.exit(1)
        if proj.stack != "python":
            console.print(
                f"[red]错误: 项目 {project_id} 不是 Python 项目（stack={proj.stack}）[/red]"
            )
            ctx.exit(1)
        targets = [proj]
    else:
        console.print("[red]错误: 请指定项目编号或使用 --all[/red]")
        ctx.exit(1)

    results: list[dict[str, Any]] = []
    for proj in targets:
        result = _check_python_project(proj.path, proj.project_id)
        results.append(result)

    if output_json:
        click.echo(json.dumps(results, ensure_ascii=False, indent=2))
        return

    # 表格输出
    for result in results:
        table = Table(title=f"Python 项目检查: {result['project_id']}")
        table.add_column("检查项", style="cyan")
        table.add_column("状态", style="white")
        table.add_column("说明", style="dim")

        for item in result["checks"]:
            status = "[green]✓[/green]" if item["ok"] else "[red]✗[/red]"
            table.add_row(item["name"], status, item.get("detail", ""))

        console.print(table)
        console.print()


def _check_python_project(project_path: str, project_id: str) -> dict[str, Any]:
    """检查单个 Python 项目规范"""
    checks: list[dict[str, Any]] = []

    # 1. 必需文件检查
    for fname in _REQUIRED_FILES:
        fpath = os.path.join(project_path, fname)
        ok = os.path.isfile(fpath)
        checks.append({
            "name": f"文件: {fname}",
            "ok": ok,
            "detail": "" if ok else "文件不存在",
        })

    # 2. 必需目录检查
    for dname in _REQUIRED_DIRS:
        dpath = os.path.join(project_path, dname)
        ok = os.path.isdir(dpath)
        checks.append({
            "name": f"目录: {dname}",
            "ok": ok,
            "detail": "" if ok else "目录不存在",
        })

    # 3. pyproject.toml 基本字段检查
    pyproject_path = os.path.join(project_path, "pyproject.toml")
    if os.path.isfile(pyproject_path):
        try:
            with open(pyproject_path, encoding="utf-8") as f:
                content = f.read()
            has_name = "name" in content
            has_version = "version" in content
            has_python = "requires-python" in content
            checks.append({
                "name": "pyproject.toml: name 字段",
                "ok": has_name,
                "detail": "" if has_name else "缺少 name 字段",
            })
            checks.append({
                "name": "pyproject.toml: version 字段",
                "ok": has_version,
                "detail": "" if has_version else "缺少 version 字段",
            })
            checks.append({
                "name": "pyproject.toml: requires-python 字段",
                "ok": has_python,
                "detail": "" if has_python else "缺少 requires-python 字段",
            })
        except OSError:
            checks.append({
                "name": "pyproject.toml 读取",
                "ok": False,
                "detail": "读取失败",
            })

    # 4. tests/ 目录检查
    tests_dir = os.path.join(project_path, "tests")
    if os.path.isdir(tests_dir):
        has_conftest = os.path.isfile(os.path.join(tests_dir, "conftest.py"))
        checks.append({
            "name": "tests/conftest.py",
            "ok": has_conftest,
            "detail": "" if has_conftest else "缺少 conftest.py",
        })

    # 5. PM_SESSION 文件检查
    pm_session_found = False
    try:
        for entry in os.listdir(project_path):
            if entry.startswith("PM_SESSION_") and entry.endswith(".md"):
                pm_session_found = True
                break
    except OSError:
        pass
    checks.append({
        "name": "PM_SESSION 文件",
        "ok": pm_session_found,
        "detail": "" if pm_session_found else "缺少 PM_SESSION_*.md",
    })

    passed = sum(1 for c in checks if c["ok"])
    total = len(checks)

    return {
        "project_id": project_id,
        "path": project_path,
        "passed": passed,
        "total": total,
        "all_ok": passed == total,
        "checks": checks,
    }
