# Trae 环境下 Docker 依赖与 Go 版本修复计划

## Summary

在 Trae 无法使用 VS Code Dev Containers 扩展的前提下，改造现有 `.devcontainer` 方案，使其可以通过 **docker compose + docker exec** 稳定完成：

- Python（含 PyQt5）依赖安装与验证（以 SW-2026-005 为目标项目）
- Go 工具链版本升级到与项目 `go.mod` 一致（Go 1.24.x），并完成模块下载
- 输出一份“Trae 小白可用”的使用文档，避免再次踩坑（挂载≠使用容器解释器、PowerShell 脚本策略等）

最终目标：用户只需按文档执行少量固定命令即可在容器内完成 Python/Go 的依赖安装、验证与日常运行。

---

## Current State Analysis（基于仓库实际探查）

### 1) 容器与配置现状

- 容器编排文件为 [.devcontainer/docker-compose.yml](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/.devcontainer/docker-compose.yml)
  - `container_name: plc-python-dev-env`
  - 工作区挂载：`..:/workspace`
  - `command: sleep infinity`（用于保持容器运行）
- 镜像构建文件为 [.devcontainer/Dockerfile](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/.devcontainer/Dockerfile)
  - 通过 `apt-get install golang-go` 安装 Go（Debian bullseye 默认是 Go 1.15.x）
  - 同时安装了 PyQt5 常见系统库（xcb/gl 等），适合 PyQt5 运行时依赖
- DevContainer 配置为 [.devcontainer/devcontainer.json](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/.devcontainer/devcontainer.json)
  - 配置了 `features.go` 与 `ms-vscode-remote.remote-containers` 扩展，但这些仅在 VS Code Dev Containers 场景会生效；Trae 当前无法安装/使用该扩展，因此 **features 不会自动生效**
- 容器启动后的依赖安装脚本为 [.devcontainer/post-create.sh](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/.devcontainer/post-create.sh)
  - 会对 SW-2026-004/001/005 安装 Python requirements，并执行多个 `go mod download`

### 2) 关键问题（已复现/已观测）

- Trae 侧无法使用 “Dev Containers” 扩展，因此不能把编辑器解释器切到容器；如果直接点击 Trae 的运行按钮，会走宿主机 PowerShell/Python，导致 `ModuleNotFoundError: No module named 'PyQt5'`。
- 宿主机 PowerShell 还存在脚本执行策略限制（阻止 `.venv\\Scripts\\Activate.ps1`），会干扰“在宿主机 venv 路线”的任何操作。
- 当前容器内实际 Go 版本为 `go1.15.15 linux/amd64`（用户已验证），而项目 go.mod 要求 Go 1.24：
  - 例如 [DJ-2026-005/.plc-out/golang/go.mod](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/0100_PLC自动化/DJ-2026-005/.plc-out/golang/go.mod#L1-L4) 为 `go 1.24.0`
  - 因此 `go mod download`/构建存在必然不一致风险
- 目前 README 指导偏 VS Code Dev Containers 流程（例如要求 “Dev Containers: Reopen in Container”），与 Trae 使用场景不匹配。

---

## Proposed Changes（文件级改造方案）

> 目标原则：**让容器本身就自带正确版本的 Go**，并提供 Trae 可用的“进入容器/运行命令”方式；尽量不依赖 Trae 扩展能力。

### Change 00：新增 Trae 专用使用文档（核心交付）

**新增文件**
- `README_DOCKER_TRAE.md`（位于仓库根目录）

**内容包含**
- Trae 场景下的正确心智模型：挂载只是文件共享，运行环境必须在容器内
- 容器生命周期操作（启动/停止/重建）
  - `docker compose -f .devcontainer/docker-compose.yml up -d --build`
  - `docker ps` 确认容器名 `plc-python-dev-env`
- 统一的 “在容器内执行命令”模板（解决 PowerShell 引号问题）
  - 推荐用：`docker exec plc-python-dev-env bash -lc '...命令...'`
- Python 依赖安装与验证（SW-2026-005）
- Go 依赖下载与验证（3 个 go.mod 目录）
- GUI 说明：PyQt5 在容器内可能无法直接弹窗；提供 3 种选择
  - 无头验证（`QT_QPA_PLATFORM=offscreen`）
  - WSLg/X11（如果用户需要可视化）
  - VNC/noVNC（如需跨平台稳定方案，作为可选扩展）

### Change 01：修复容器 Go 版本（强制匹配 go.mod）

**修改文件**
- [.devcontainer/Dockerfile](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/.devcontainer/Dockerfile)

**改造策略（决定稿）**
- 移除 `apt-get install golang-go`（避免锁定 bullseye 的 go1.15）
- 通过官方下载 tarball 安装 Go 1.24.x（默认 1.24.0），安装到 `/usr/local/go`
- 通过 `ENV PATH=/usr/local/go/bin:...` 确保 `go` 可用
- 增加 `ARG GO_VERSION=1.24.0`，便于后续更新
- 可选：增加 SHA256 校验（下载官方 `go${GO_VERSION}.linux-amd64.tar.gz` 并校验）

**为什么这样做**
- Trae 当前无法使用 devcontainer features 自动安装 Go 1.24
- 让镜像自带正确 Go 版本，`post-create.sh` 的 `go mod download` 才能稳定工作

### Change 02：让依赖安装在 Trae 下也“一键可跑”

**修改文件**
- [.devcontainer/post-create.sh](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/.devcontainer/post-create.sh)

**改造点**
- 保持现有逻辑，但补充两类鲁棒性（不引入注释）
  - 在脚本开头打印关键版本信息：`python3 -V`、`go version`、`whoami`、`pwd`
  - `go mod download` 前增加 Go 版本检查（若低于 1.24，给出清晰错误并跳过/退出）
- 额外提供一个更短的“Trae 一键 bootstrap”入口（例如新增 `scripts/bootstrap_container.sh`），内部调用该脚本

> 说明：Trae 下不会自动触发 `postCreateCommand`，因此文档中会指导用户手动运行 bootstrap。

### Change 03：修正文档与验证口径（与 Trae 真实流程一致）

**修改文件**
- [README_DOCKER.md](file:///c:/Users/fubai/Documents/BaiduSyncdisk/My_Workspace/README_DOCKER.md)

**改造点**
- 在“快速开始/验证”章节增加 “Trae 使用说明” 引导到 `README_DOCKER_TRAE.md`
- 明确指出：未使用 VS Code Dev Containers 时，features/扩展不会自动生效
- 更新 Go 版本验证说明：要求 `go1.24.x`，并说明若不是则需重建镜像

---

## Assumptions & Decisions

- 目标 Go 版本采用 **Go 1.24.0**（用户确认；满足 `go 1.24.0` 的 go.mod 要求，固定版本便于一致性）。
- 主要运行环境以 **容器内 bash** 为准；宿主机不要求安装 Python/Go（减少环境干扰）。
- Trae 无 Dev Containers 扩展能力，采用 `docker exec ... bash -lc '...'` 作为标准执行方式。
- Python 依赖中 **PyQt5 必须可用**；**QScintilla 可选**（用户确认；若安装失败允许回退到基础文本编辑模式）。
- 本计划不在本轮强制实现“容器内可见 GUI 窗口”，只提供可选方案说明；默认以无头验证/命令行运行作为成功标准。

---

## Delivery（提交与发布）

- 完成所有验证后，将变更提交并推送到 GitHub（用户要求）。
- 提交信息遵循仓库约定（类型 + 中文 50 字内 + 使用真实模块名），并在提交说明中明确包含：`此次提交来自Trae Pro订阅的提交发布`。

---

## Verification（验收与自测步骤）

### 1) 镜像构建与容器启动

- `docker compose -f .devcontainer/docker-compose.yml up -d --build`
- `docker ps --format "table {{.Names}}\t{{.Status}}"` 应看到 `plc-python-dev-env` 为 healthy/running

### 2) 版本验证（容器内）

- `docker exec plc-python-dev-env bash -lc 'pwd; python3 -V; go version'`
  - `pwd` 输出 `/workspace`
  - Python 为 3.11.x
  - Go 为 1.24.x

### 3) Python 依赖验证（SW-2026-005）

- `docker exec plc-python-dev-env bash -lc 'cd ".../SW-2026-005.../01_主程序核心代码" && python3 -m pip install -r requirements.txt'`
- `docker exec plc-python-dev-env bash -lc 'python3 -c "import PyQt5; print(\"PyQt5 OK\")"'` 输出 `PyQt5 OK`

### 4) Go 模块验证（3 个 go.mod 目录）

- 对以下目录逐个执行：
  - `/workspace/0100_PLC自动化/DJ-2026-000/.plc-out/golang`
  - `/workspace/0100_PLC自动化/DJ-2026-005/.plc-out/golang`
  - `/workspace/0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/.plc-out/golang`
- 命令：
  - `go mod download`
  - `go list -m all`（无报错）

### 5) 文档验收

- `README_DOCKER_TRAE.md` 里的命令复制粘贴可直接跑通（不依赖 Dev Containers 扩展）
