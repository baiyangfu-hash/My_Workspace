"""Auto-PM 工业级 AI 研发工作台 - 根目录快捷启动入口

外部使用者在工作空间根目录运行 `python main.py`，即可一键拉起桌面驾驶舱。
本入口会自动动态定位工作空间根目录与核心包路径，不依赖任何写死的绝对路径。
"""

import os
import sys
from pathlib import Path

# 1. 动态定位当前工作空间根目录
WORKSPACE_ROOT = Path(__file__).parent.resolve()

# 2. 动态定位 auto-pm 核心工程路径
AUTO_PM_PROJECT_DIR = (
    WORKSPACE_ROOT
    / "01_Project自动化项目管理"
    / "Python自动化项目总库"
    / "02_在研项目"
    / "SW-2026-008_auto-pm_自动化项目管理工具"
)

if not AUTO_PM_PROJECT_DIR.exists():
    # 备选：如果直接是 flat 目录结构
    if (WORKSPACE_ROOT / "auto_pm").exists():
        AUTO_PM_PROJECT_DIR = WORKSPACE_ROOT

# 将核心工程加入 sys.path
if str(AUTO_PM_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(AUTO_PM_PROJECT_DIR))

# 3. 设置工作空间环境变量（确保底层自动寻根）
os.environ["AUTO_PM_WORKSPACE"] = str(WORKSPACE_ROOT)

if __name__ == "__main__":
    from auto_pm.ui.qml_main_window import run_qml_app

    # 启动桌面驾驶舱
    sys.exit(run_qml_app(workspace_root=str(WORKSPACE_ROOT)))
