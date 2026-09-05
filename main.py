"""Auto-PM 工业级 AI 研发工作台 - 根目录快捷启动入口（平铺源码运行态）

CHG-SCPT-2026-018 回退态：恢复稳定部署平铺源码作为运行入口（双槽 release 运行
暂缓，等待 CHG-SCPT-2026-018 项下的针对性修复后按新方案重新切流）。

本入口动态定位工作空间根目录与核心包路径，不依赖 editable/.pth/永久 PYTHONPATH；
双槽 bootstrap 解析器（launcher/bootstrap.py）保留在容器内，供后续方案复用。
"""

import os
import sys
from pathlib import Path

# 1. 动态定位当前工作空间根目录
WORKSPACE_ROOT = Path(__file__).parent.resolve()

# 2. 动态定位 auto-pm 核心工程路径：优先使用工作空间级基础设施运行位
AUTO_PM_INFRA_DIR = WORKSPACE_ROOT / "00_Infrastructure" / "auto_pm"
AUTO_PM_LEGACY_PROJECT_DIR = (
    WORKSPACE_ROOT
    / "01_Project自动化项目管理"
    / "Python自动化项目总库"
    / "02_在研项目"
    / "SW-2026-008_auto-pm_自动化项目管理工具"
)

AUTO_PM_PROJECT_DIR = AUTO_PM_INFRA_DIR
if not AUTO_PM_PROJECT_DIR.exists():
    AUTO_PM_PROJECT_DIR = AUTO_PM_LEGACY_PROJECT_DIR

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
    # 注意：稳定平铺源码的 QML 入口函数是 run_qml_gui（无 run_qml_app）
    from auto_pm.ui.qml_main_window import run_qml_gui

    # 启动桌面驾驶舱
    sys.exit(run_qml_gui(workspace_root=str(WORKSPACE_ROOT)))
