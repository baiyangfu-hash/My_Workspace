# Tasks - PLCPM v0.2.0 完整交付（简化版）

## Task 1: 修复 app.py 致命导入Bug + 统一版本号

- [x] Task 1.1: 修复 `src/core/app.py` 的3处错误相对导入
  - [x] 第16行: `from .core.path_resolver` → `from .path_resolver`
  - [x] 第17行: `from .core.config` → `from .config`
  - [x] 第18行: `from .core.logger` → `from .logger`
  - [x] 第20行: `from ..services.seed_service` 保持不变

- [x] Task 1.2: 统一版本号到 v0.2.0
  - [x] `src/__init__.py`: `__version__ = "0.2.0"`
  - [x] `config/app_config.json`: `"version": "0.2.0"`
  - [x] `src/cli/main.py`: `version='0.2.0'`

## Task 2: 创建根目录启动器 main.py（对标参考项目）

- [x] Task 2.1: 创建项目根目录 `main.py`
  - [x] 实现 `setup_paths()` 函数（将 src/ 和根目录加入 sys.path）
  - [x] 实现 `run_gui()` — 启动PyQt5 GUI窗口
  - [x] 实现 `run_api()` — 启动Flask API服务
  - [x] 实现 `run_cli()` — 启动Click CLI
  - [x] 实现 `run_console()` — 控制台初始化输出
  - [x] 实现 `main()` — argparse分发：默认GUI / --mode参数 / 子命令自动检测
  - [x] 兼容 PyInstaller 打包模式（sys.frozen 检测）
  - [x] 缺少依赖时给出友好提示

## Task 3: 编写中文使用文档 USER_GUIDE.md

- [x] Task 3.1: 创建 `docs/USER_GUIDE.md`，包含以下章节：
  - [x] **第一章 快速开始**: Python安装 → 虚拟环境 → 安装依赖 → 首次启动
  - [x] **第二章 启动方式**: 4种模式的完整命令和预期输出
  - [x] **第三章 GUI操作手册**:
    - [x] 主界面布局总览（ASCII图）
    - [x] 项目列表Tab（新建/编辑/删除/搜索/筛选）
    - [x] 模板管理Tab（浏览/详情/目录树预览）
    - [x] 变更记录Tab（颜色编码含义/筛选）
    - [x] 菜单栏和工具栏说明
  - [x] **第四章 CLI命令速查**: 所有子命令的参数和示例
  - [x] **第五章 常见问题FAQ**: 至少10条（路径/数据库/导入错误/模板等）
  - [x] **第六章 数据目录说明**: data/logs/config各目录的作用

# Task Dependencies
- [Task 2] 依赖 [Task 1] ✅
- [Task 3] 无依赖，可与 [Task 1] 并行 ✅

# Parallelizable Groups
- **Group A**: Task 1, Task 3 ✅
- **Group B** (依赖A): Task 2 ✅

---
**状态**: 全部任务完成 ✅
