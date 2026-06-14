#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workspace Venv Setup Script
Usage: python setup_venv.py
"""
import subprocess
import sys
import os
import json
import shutil
import stat
import time

VENV_PATH = r"c:\Users\fubai\Desktop\My_Workspace\.venv"
WORKSPACE = r"c:\Users\fubai\Desktop\My_Workspace"
VSCODE_DIR = os.path.join(WORKSPACE, ".vscode")

def pip_install(python_exe, args, timeout=300):
    """Run pip install with timeout and no cache"""
    cmd = [python_exe, "-m", "pip", "install", "--no-cache-dir"] + args
    print(f"  Running: {' '.join(cmd[:6])}{'...' if len(cmd) > 6 else ''}")
    try:
        result = subprocess.run(cmd, timeout=timeout,
                              capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        if result.stdout:
            # Only print last few lines to reduce noise
            lines = result.stdout.strip().splitlines()
            for line in lines[-5:]:
                print(f"    {line}")
        if result.returncode != 0 and result.stderr:
            print(f"    ERROR: {result.stderr.strip()[:200]}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT after {timeout}s, skipping...")
        return False

def step(num, title):
    print(f"\n=== [{num}/7] {title} ===")

def force_remove_venv(path):
    """Force remove venv directory, handling locked .pyd files on Windows"""
    def on_rm_error(func, path_on_error, exc_info):
        os.chmod(path_on_error, stat.S_IWRITE)
        try:
            func(path_on_error)
        except Exception:
            pass
    for attempt in range(3):
        try:
            shutil.rmtree(path, onerror=on_rm_error)
            return True
        except Exception as e:
            if attempt < 2:
                print(f"  Retry {attempt+1}/3 after error: {e}")
                time.sleep(2)
            else:
                print(f"  WARNING: Could not fully remove {path}")
                print(f"  Please close any programs using .venv and re-run")
                return False

# Step 1: Create venv
step(1, "Create virtual environment")
if os.path.exists(VENV_PATH):
    print(".venv exists, removing and recreating...")
    if not force_remove_venv(VENV_PATH):
        sys.exit(1)
subprocess.run([sys.executable, "-m", "venv", VENV_PATH], check=True)
python_exe = os.path.join(VENV_PATH, "Scripts", "python.exe")
if not os.path.exists(python_exe):
    print("ERROR: venv creation failed!")
    sys.exit(1)
print(".venv created")

# Step 2: Upgrade pip
step(2, "Upgrade pip")
subprocess.run([python_exe, "-m", "pip", "install", "--no-cache-dir",
                "--upgrade", "pip"], check=True, timeout=120)

# Step 3: Install CLI tools (editable mode, with timeout)
step(3, "Install CLI tools")
cli_tools = [
    ("pm-mgr (SW-2026-007)", os.path.join(WORKSPACE,
     "01_Project自动化项目管理", "Python自动化项目总库", "02_在研项目",
     "SW-2026-007_pm工作流工具链")),
    ("specmgr (SW-2026-006)", os.path.join(WORKSPACE,
     "01_Project自动化项目管理", "Python自动化项目总库", "02_在研项目",
     "SW-2026-006_规范管理工具", "02_源代码")),
    ("plc-project-mgr (SW-2026-005)", os.path.join(WORKSPACE,
     "01_Project自动化项目管理", "Python自动化项目总库", "02_在研项目",
     "SW-2026-005_PLC项目管理工具", "03_主程序", "01_主程序核心代码")),
    ("python-project-manager (SW-2026-004)", os.path.join(WORKSPACE,
     "01_Project自动化项目管理", "Python自动化项目总库", "02_在研项目",
     "SW-2026-004_Python项目管理工具", "03_主程序", "01_主程序核心代码")),
]
for name, path in cli_tools:
    print(f"  {name}...")
    if os.path.exists(path):
        pip_install(python_exe, ["-e", path], timeout=180)
    else:
        print(f"    SKIP: path not found - {path}")

# Step 4: SW-2026-001 dependencies
step(4, "Install SW-2026-001 dependencies")
pip_install(python_exe, ["chardet>=5.0.0"])

# Step 5: SW-2026-004 dependencies
step(5, "Install SW-2026-004 dependencies")
sw004_deps = [
    "PyQt5==5.15.10", "Flask==3.0.2", "SQLAlchemy==2.0.27",
    "python-dotenv==1.0.1", "requests==2.31.0", "python-dateutil==2.8.2",
    "markdown==3.5.2", "pyinstaller==6.4.0", "networkx==3.2.1",
    "bcrypt==4.1.2", "pydantic==2.6.3", "pydantic-settings==2.2.1",
    "dependency-injector==4.41.0", "alembic==1.13.1",
]
pip_install(python_exe, sw004_deps, timeout=600)

# Step 6: Dev tools
step(6, "Install dev tools and test frameworks")
dev_deps = [
    "pytest>=8.0.1", "pytest-cov>=4.1.0", "pytest-asyncio==0.23.5",
    "pytest-qt>=4.0", "mypy==1.9.0", "flake8==7.0.0", "black==24.2.0",
    "ruff>=0.5.0", "pywebview>=5.0",
]
pip_install(python_exe, dev_deps, timeout=600)

# Step 7: Configure editor auto-binding
step(7, "Configure editor auto-binding")
os.makedirs(VSCODE_DIR, exist_ok=True)
settings = {
    "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
    "python.terminal.activateEnvironment": True,
    "python.testing.pytestEnabled": True,
    "python.testing.pytestPath": "${workspaceFolder}\\.venv\\Scripts\\pytest.exe",
    "python.linting.enabled": True,
    "python.linting.flake8Path": "${workspaceFolder}\\.venv\\Scripts\\flake8.exe",
    "python.linting.mypyPath": "${workspaceFolder}\\.venv\\Scripts\\mypy.exe",
    "python.formatting.provider": "black",
    "python.formatting.blackPath": "${workspaceFolder}\\.venv\\Scripts\\black.exe",
    "terminal.integrated.env.windows": {
        "PYTHONPATH": "${workspaceFolder}"
    },
    "files.exclude": {
        ".venv": False,
        ".venvs": True
    }
}
settings_path = os.path.join(VSCODE_DIR, "settings.json")
with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=4, ensure_ascii=False)
print(".vscode/settings.json configured")

# Verify
print("\n" + "=" * 50)
print("  Verify Installation")
print("=" * 50)
subprocess.run([python_exe, "--version"])
subprocess.run([python_exe, "-m", "pip", "--version"])

print("\nCLI tools:")
for cmd in ["pm-mgr", "specmgr"]:
    cmd_exe = os.path.join(VENV_PATH, "Scripts", cmd + ".exe")
    if os.path.exists(cmd_exe):
        subprocess.run([cmd_exe, "--version"])
    else:
        print(f"  {cmd}: not found")

print("\nGUI libraries (should only have PyQt5):")
result = subprocess.run([python_exe, "-m", "pip", "list"],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
if result.stdout:
    for line in result.stdout.splitlines():
        low = line.lower()
        if "pyqt" in low or "pyside" in low or "shiboken" in low:
            print(f"  {line}")

print("\nKey packages:")
keywords = ["Flask", "SQLAlchemy", "pytest", "chardet",
            "pywebview", "pydantic", "black", "ruff"]
if result.stdout:
    for line in result.stdout.splitlines():
        if any(kw.lower() in line.lower() for kw in keywords):
            print(f"  {line}")

# Done
print("\n" + "=" * 50)
print("  Setup Complete!")
print("=" * 50)
print(f"\nVenv:   {VENV_PATH}")
subprocess.run([python_exe, "--version"])
print("\nEditor auto-binding configured:")
print("  VS Code / Trae CN / Trae Intl")
print("  Auto uses .venv interpreter on workspace open")
print("\nTo activate venv later:")
print(f"  . {os.path.join(VENV_PATH, 'Scripts', 'Activate.ps1')}")
print("\nTo rebuild, just re-run: python setup_venv.py")
