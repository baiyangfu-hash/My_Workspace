# PLCPM v0.2.0 完整交付 Spec（简化版）

## Why

用户反馈：参考项目 SW-2026-004 的结构是模块化的，应该很容易才对，为什么现在这么复杂？

**根本原因分析**：
1. 参考项目的启动模式非常简单——**根目录一个 `main.py` 搞定所有入口**
2. 参考项目用 `setup_paths()` 将 `src/` 加入 sys.path 后全部使用**绝对导入**（`from src.core.config import Config`）
3. 我们的 PLCPM 项目错误地使用了复杂的相对导入（`.core.path_resolver`），还写错了导致崩溃
4. 缺少根目录启动脚本，用户不知道怎么运行

**解决方案**：对齐参考项目的成熟模式，简化到极致。

## What Changes

### 核心改动（对标参考项目 main.py）

1. **新建 `main.py`** — 项目根目录唯一启动入口（对标参考项目的 main.py）
   - `python main.py` → 默认启动GUI
   - `python main.py --mode api` → 启动API
   - `python main.py gui/api/cli/console` → 子命令模式
   - 内置 `setup_paths()` 兼容PyInstaller打包

2. **修复 `src/core/app.py` 导入Bug** — 3处 `.core.xxx` 改为 `.xxx`

3. **统一版本号 v0.2.0** — 4处文件同步更新

4. **编写使用文档 `docs/USER_GUIDE.md`** — 中文操作手册

## Impact

- 新建: `main.py`, `docs/USER_GUIDE.md`
- 修改: `src/core/app.py`(修复), `src/__init__.py`, `config/app_config.json`, `src/cli/main.py`
- 不修改任何业务逻辑代码

---

## ADDED Requirements

### Requirement: 根目录启动器 main.py

系统 SHALL 提供项目根目录的 `main.py` 作为唯一启动入口：

```python
# 对标参考项目 SW-2026-004 的 main.py 模式
def setup_paths():
    base = Path(__file__).parent
    sys.path.insert(0, str(base / "src"))
    sys.path.insert(0, str(base))

# 启动方式:
# python main.py          → GUI模式（默认）
# python main.py gui       → GUI模式
# python main.py api       → API服务 127.0.0.1:5000
# python main.py cli       → CLI命令行 (--help)
# python main.py console   → 控制台初始化输出
```

#### Scenario: 默认启动GUI
- **WHEN** 用户在项目根目录执行 `python main.py`
- **THEN** PyQt5窗口打开，显示4个Tab页，内置模板已加载

#### Scenario: API模式
- **WHEN** 用户执行 `python main.py api`
- **THEN** Flask在5000端口启动，GET /api/projects 返回JSON

#### Scenario: CLI帮助
- **WHEN** 用户执行 `python main.py cli --help`
- **THEN** 显示PLCPM v0.2.0 命令行帮助

### Requirement: 使用文档 USER_GUIDE.md

系统 SHALL 提供中文使用文档包含：
1. 环境安装步骤（Python 3.9+ / pip install -r requirements.txt）
2. 首次启动指南（从零到看到界面的完整步骤）
3. GUI界面操作手册（每个Tab的功能+截图描述）
4. CLI命令速查表
5. FAQ（至少10条）

## MODIFIED Requirements

### Requirement: app.py 导入修正

`src/core/app.py` 的导入语句 SHALL 修正为：
```python
from .path_resolver import PathResolver, project_root   # 不是 .core.path_resolver
from .config import config                               # 不是 .core.config  
from .logger import setup_logger                          # 不是 .core.logger
```

### Requirement: 版本一致性

以下位置版本号 SHALL 统一为 "0.2.0"：
- `src/__init__.py`: `__version__`
- `config/app_config.json`: `app.version`
- `src/cli/main.py`: Click version_option
