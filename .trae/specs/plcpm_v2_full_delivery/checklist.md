# Checklist - PLCPM v0.2.0 完整交付

## Task 1: 修复Bug + 版本统一
- [x] `src/core/app.py` 第16行导入为 `from .path_resolver import ...` ✅
- [x] `src/core/app.py` 第17行导入为 `from .config import config` ✅
- [x] `src/core/app.py` 第18行导入为 `from .logger import setup_logger` ✅
- [x] `src/__init__.py` 版本号为 "0.2.0" ✅
- [x] `config/app_config.json` 版本号为 "0.2.0" ✅
- [x] `src/cli/main.py` Click version 为 '0.2.0' ✅

## Task 2: 根目录启动器
- [x] 项目根目录存在 `main.py` 文件 ✅
- [x] `python main.py` 可启动GUI（默认模式）✅
- [x] `python main.py api` 可启动API服务 ✅
- [x] `python main.py cli --help` 显示CLI帮助（v0.2.0）✅
- [x] `python main.py console` 输出初始化信息 ✅
- [x] 包含 PyInstaller 打包兼容（sys.frozen 检查）✅
- [x] 缺少PyQt5时有友好错误提示 ✅

## Task 3: 使用文档
- [x] `docs/USER_GUIDE.md` 存在且使用中文编写 ✅
- [x] 包含快速开始章节（安装→首次启动）✅
- [x] 包含4种启动方式说明 ✅
- [x] 包含GUI操作手册（每个Tab的功能说明）✅
- [x] 包含CLI命令速查表 ✅
- [x] 包含FAQ至少10条 ✅

---
**状态**: 全部检查项通过 ✅ (3/3 Tasks, 19/19 Checkpoints)
