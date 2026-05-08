# Trae 使用 Docker 开发环境指南（不依赖 Dev Containers 扩展）

本指南适用于：Trae 无法安装/使用 VS Code 的 Dev Containers 扩展，但你仍然希望把 **Python/Go 环境与依赖** 全部放在 Docker 容器里。

核心原则只有一句：

- 代码文件可以在宿主机编辑（挂载到容器里），但**安装依赖/运行命令必须在容器内执行**。

---

## 00. 常见误区

- 挂载目录 ≠ 使用容器解释器
  - 你在 Trae 里点“运行”，默认用的是宿主机 PowerShell/Python（路径通常是 `C:\Users\...`）
  - 容器里的 Python/Go/依赖不会自动被 Trae 使用

---

## 01. 启动/重建容器

在工作区根目录（`My_Workspace`）用 PowerShell 执行：

```powershell
docker compose -f .devcontainer\docker-compose.yml up -d --build
```

确认容器名：

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"
```

预期能看到：

- `plc-python-dev-env    Up ... (healthy)`

---

## 02. Trae 场景的标准执行方式（推荐）

为了避免 “Attach Shell / 终端类型 / 引号嵌套” 带来的不确定性，推荐统一使用：

```powershell
docker exec plc-python-dev-env bash -lc '...这里写容器内命令...'
```

### 2.1 环境自检（复制粘贴即可）

```powershell
docker exec plc-python-dev-env bash -lc 'pwd; python3 -V; go version'
```

预期输出形态：

- `/workspace`
- `Python 3.11.x`
- `go version go1.24.x linux/amd64`

---

## 03. Python：安装并验证 SW-2026-005 依赖（PyQt5 必须可用）

```powershell
docker exec plc-python-dev-env bash -lc 'cd "/workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-005_PLC项目管理工具/03_主程序/01_主程序核心代码" && python3 -m pip install -U pip && python3 -m pip install -r requirements.txt && python3 -c "import PyQt5; print(\"PyQt5 OK\")"'
```

说明：

- QScintilla 可选；如果安装失败允许回退到基础文本编辑器模式（项目内已有回退逻辑）。

---

## 04. Go：下载 3 处 go.mod 的依赖

### 4.1 DJ-2026-005（主程序 .plc-out）

```powershell
docker exec plc-python-dev-env bash -lc 'cd "/workspace/0100_PLC自动化/DJ-2026-005/.plc-out/golang" && go mod download && go list -m all >/dev/null && echo "✅ DJ-2026-005 (.plc-out) Go modules OK"'
```

### 4.2 DJ-2026-000

```powershell
docker exec plc-python-dev-env bash -lc 'cd "/workspace/0100_PLC自动化/DJ-2026-000/.plc-out/golang" && go mod download && go list -m all >/dev/null && echo "✅ DJ-2026-000 Go modules OK"'
```

### 4.3 DJ-2026-005（通用ST程序及变量表）

```powershell
docker exec plc-python-dev-env bash -lc 'cd "/workspace/0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/.plc-out/golang" && go mod download && go list -m all >/dev/null && echo "✅ DJ-2026-005 通用ST程序 Go modules OK"'
```

---

## 05. 运行 SW-2026-005（重要：GUI 显示）

你可以在容器内运行 Python，但容器默认没有图形显示链路，因此：

- 能 `import PyQt5` ≠ 一定能弹出窗口

如果你只是验证程序能启动/导入依赖，建议先做无头验证：

```powershell
docker exec plc-python-dev-env bash -lc 'cd "/workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-005_PLC项目管理工具/03_主程序/01_主程序核心代码" && QT_QPA_PLATFORM=offscreen python3 -c "from PyQt5.QtWidgets import QApplication; import sys; app=QApplication(sys.argv); print(\"✅ Qt offscreen OK\")"'
```

如果你需要真正看到窗口，建议后续采用：

- Windows 11 + WSLg（推荐）
- 容器内 VNC/noVNC（跨平台稳定）

---

## 06. 常用命令速查

- 停止容器：
  ```powershell
  docker compose -f .devcontainer\docker-compose.yml stop
  ```
- 重新构建并启动：
  ```powershell
  docker compose -f .devcontainer\docker-compose.yml up -d --build
  ```
- 查看容器日志：
  ```powershell
  docker logs -n 200 plc-python-dev-env
  ```

