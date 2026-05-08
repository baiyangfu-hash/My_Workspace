# Trae CN 问题清单与后续建议（SW-2026-005 + Docker + PyQt5）

## 00. 当前结论（已验证）

- 容器：`plc-python-dev-env` 正常运行（`healthy`）
- 容器内运行环境：`/workspace`、`Python 3.11.4`
- PyQt5 可导入：`python3 -c "import PyQt5"`
- Qt 无头模式可初始化：`QT_QPA_PLATFORM=offscreen` 可创建 `QApplication`

## 01. 已修复问题

### 1.1 NameError: QCloseEvent 未定义

- 现象：启动导入 `src/ui/main_window.py` 时，在类定义阶段报错：
  - `NameError: name 'QCloseEvent' is not defined`
- 根因：`QCloseEvent` 仅在 `TYPE_CHECKING` 分支导入，运行时并不存在该名字，但函数注解会在运行时解析。
- 修复：改为运行时直接导入 `QCloseEvent`。

## 02. 仍存在/可复现的问题（待 Trae CN 分析）

### 2.1 Qt 平台插件 xcb 无法初始化（GUI 无法直接弹窗）

- 现象（容器内）：创建 `QApplication` 时失败：
  - `qt.qpa.plugin: Could not load the Qt platform plugin "xcb" ...`
  - `This application failed to start because no Qt platform plugin could be initialized.`
- 备注：插件列表中包含 `xcb`，说明并非“未安装 PyQt5”，更像是“没有可用显示链路/环境变量/依赖组合”导致初始化失败。

### 2.2 XDG_RUNTIME_DIR 警告

- 现象：
  - `QStandardPaths: XDG_RUNTIME_DIR not set, defaulting to '/tmp/runtime-vscode'`
- 影响评估：一般不致命，可忽略；若需要更干净的运行环境可设置。

### 2.3 PowerShell + docker exec 的引号/转义易踩坑

- 现象：在 PowerShell 里嵌套 `bash -lc` + `python3 -c` 时，容易因为引号层级导致命令被截断，表现为 `SyntaxError: invalid syntax` 等。
- 建议：优先使用 `docker exec -w ... <cmd>` 或把 Python 命令放到脚本文件里再执行。

### 2.4 仓库“脏”与忽略规则不同步

- 现象：CN 侧使用全局忽略（global gitignore），GitHub 不会同步，导致其他机器看到大量未跟踪文件。
- 处理方向：把通用忽略规则落到仓库根目录 `.gitignore` 并提交同步。
- 注意：`.gitignore` 只影响“未跟踪文件”；对于已被 Git 跟踪的生成物（例如部分 `.plc-out`），仍会继续显示为修改，需要另行决策是否移出版本控制。

## 03. 建议的后续处理（按优先级）

### 3.1 先保证“可运行且可测试”（无头模式）

- 目标：在没有 GUI 显示链路的情况下，先让程序能完成导入/启动关键逻辑。
- 推荐命令（容器内无头验证）：
  - `docker exec -e QT_QPA_PLATFORM=offscreen -w "<SW-2026-005主程序目录>" plc-python-dev-env python3 -c "from PyQt5.QtWidgets import QApplication; import sys; app=QApplication(sys.argv); print('Qt offscreen OK')"`

### 3.2 真正需要弹窗时的两条路线（二选一）

- 路线 A（推荐稳定）：容器内 VNC/noVNC
  - 优点：跨平台稳定、与 IDE 无强耦合
  - 缺点：需要额外服务与端口
- 路线 B（Windows 11）：WSLg + X11/Wayland 显示链路
  - 优点：体验接近本地
  - 缺点：环境组合复杂，排障成本较高

### 3.3 为降低引号问题，统一命令形态

- 推荐优先使用：
  - `docker exec -w "<workdir>" plc-python-dev-env python3 -c "<code>"`
- 避免在 PowerShell 中多层嵌套单引号/双引号与 `bash -lc`。

### 3.4 忽略规则同步策略

- 建议提交仓库根目录 `.gitignore`（通用缓存/日志/venv 等）。
- 若后续决定把生成物移出版本控制：需要评估 CI/生成流程依赖，考虑 `git rm --cached` 等操作（这会影响现有工作流，需单独变更单）。

## 04. 复现/验证命令（给 Trae CN）

### 4.1 环境自检

```powershell
docker exec plc-python-dev-env bash -lc 'pwd; python3 -V; go version'
```

### 4.2 Qt 无头验证（已通过）

```powershell
docker exec -e QT_QPA_PLATFORM=offscreen -w "/workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-005_PLC项目管理工具/03_主程序/01_主程序核心代码" plc-python-dev-env python3 -c "from PyQt5.QtWidgets import QApplication; import sys; app=QApplication(sys.argv); print('Qt offscreen OK')"
```

