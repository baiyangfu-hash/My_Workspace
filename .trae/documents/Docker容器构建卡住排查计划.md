# Docker 容器构建后卡住问题排查与解决计划

## 📋 当前状态分析

### 已确认的成功步骤
- [x] Docker Desktop 已安装并运行
- [x] Dev Containers 扩展已安装
- [x] 工作区路径正确：`D:\BaiduSyncdisk\My_Workspace`
- [x] `.devcontainer/` 配置文件完整存在
- [x] Dockerfile 已修复（删除 Yarn 过期仓库 + 使用国内镜像源）
- [x] `docker-compose up --build` 执行成功
- [x] 容器 `plc-python-dev-env` 已创建并运行

### 当前问题
终端显示 **"Attaching to plc-python-dev-env"** 后长时间无输出，命令运行中。

---

## 🔍 问题根因假设

### 假设 1：post-create.sh 脚本执行耗时（最可能）
- **现象**：容器已启动，但 post-create.sh 在安装依赖
- **预期时间**：5-15分钟（首次安装 Python/Go 依赖）
- **验证方法**：检查容器日志

### 假设 2：VS Code Remote Containers 连接超时
- **现象**：docker-compose 命令挂起等待输入
- **原因**：Trae Pro 与 Docker 的集成可能不同于标准 VS Code
- **验证方法**：单独测试容器是否正常运行

### 假设 3：网络问题导致依赖下载慢
- **现象**：pip install / go mod download 卡住
- **原因**：国内访问 PyPI/Go 模块代理慢
- **验证方法**：查看容器内进程

---

## 🛠️ 解决方案（按优先级排序）

### 方案 A：验证容器是否正常运行（2分钟）

#### 步骤 A1：打开新终端窗口
```bash
# 在新的 PowerShell/CMD 终端中运行
docker ps
```
**预期结果**：应看到 `plc-python-dev-env` 容器状态为 `Up`

#### 步骤 A2：进入容器内部
```bash
docker exec -it plc-python-dev-env bash
```
**预期结果**：成功进入容器 bash 环境

#### 步骤 A3：在容器内验证环境
```bash
python --version    # 应输出: Python 3.11.x
go version          # 应输出: go1.24.x
ls /workspace/      # 应看到项目目录
```

---

### 方案 B：如果容器正常但 Trae 无法连接（5分钟）

#### 步骤 B1：使用 Dev Containers 命令连接
1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 `Dev Containers: Attach to Running Container`
3. 选择 `plc-python-dev-env`

#### 步骤 B2：如果上述命令无效，尝试 Reopen
1. 按 `Ctrl+Shift+P`
2. 输入 `Dev Containers: Reopen in Container`
3. 等待检测并连接

#### 步骤 B3：手动配置远程连接（备选）
```bash
# 在 Trae 终端中运行
code --remote-container-attach $(docker inspect -f '{{.Id}}' plc-python-dev-env)
```

---

### 方案 C：如果 post-create.sh 卡住（10分钟）

#### 步骤 C1：查看容器日志
```bash
docker logs -f plc-python-dev-env
```
**观察重点**：
- 是否有 `🚀 开始配置开发环境...` 输出
- 是否卡在某个 `pip install` 或 `go mod download` 步骤
- 是否有错误信息

#### 步骤 C2：如果确实卡住，终止并重新启动
```bash
# 停止容器
docker-compose -f .devcontainer/docker-compose.yml down

# 手动启动容器（跳过 post-create.sh）
docker-compose -f .devcontainer/docker-compose.yml up -d

# 手动执行 post-create.sh（可观察进度）
docker exec -it plc-python-dev-env bash .devcontainer/post-create.sh
```

#### 步骤 C3：优化 post-create.sh（如果网络慢）
编辑 `.devcontainer/post-create.sh`，添加国内镜像源：
```bash
# pip 使用清华镜像
pip install xxx -i https://pypi.tuna.tsinghua.edu.cn/simple

# go 使用代理
export GOPROXY=https://goproxy.cn,direct
go mod download
```

---

### 方案 D：终极方案 - 简化 Dockerfile（30分钟）

如果以上方案都失败，考虑简化构建过程：

#### 步骤 D1：使用预构建镜像
修改 `Dockerfile`，基于更稳定的基础镜像：
```dockerfile
FROM python:3.11-slim-bullseye

# 最小化安装，避免网络问题
RUN apt-get update && apt-get install -y \
    golang-go curl git vim build-essential \
    && rm -rf /var/lib/apt/lists/*
```

#### 步骤 D2：分离依赖安装
将依赖安装从 Dockerfile 移到 post-create.sh，并在容器启动后手动执行。

---

## 📊 决策流程图

```
开始
  ↓
docker ps 检查容器状态
  ├─ 容器未运行 → 方案 D（重建）
  │
  ├─ 容器运行中 → docker exec 进入容器
  │   ├─ 进入成功 → 验证环境 → 方案 B（Trae 连接）
  │   └─ 进入失败 → docker logs 查看日志
  │       ├─ post-create 卡住 → 方案 C（手动执行）
  │       └─ 其他错误 → 根据错误处理
  │
  └─ 容器异常 → docker logs + 方案 D
```

---

## ✅ 成功标准

完成以下任一方案后，环境即视为就绪：

1. **容器内验证通过**
   ```bash
   python --version  # Python 3.11.x
   go version        # go1.24.x
   ls /workspace/    # 项目目录可见
   ```

2. **Trae Pro 连接成功**
   - 底部状态栏显示 "Dev Container"
   - 终端为容器内环境
   - 可运行 Python/Go 命令

3. **PLC 调试可用**
   - F5 启动调试
   - launch.json 配置生效

---

## ⏱️ 预计时间

| 方案 | 时间 | 成功率 |
|------|------|--------|
| 方案 A（验证） | 2分钟 | 90% |
| 方案 B（连接） | 5分钟 | 70% |
| 方案 C（调试） | 10分钟 | 80% |
| 方案 D（重建） | 30分钟 | 95% |

---

## 🔄 后续优化建议

问题解决后，建议更新以下文档：

1. **README_DOCKER.md** - 添加"构建卡住"故障排查章节
2. **Dockerfile** - 锁定基础镜像版本，避免未来类似问题
3. **post-create.sh** - 添加超时机制和重试逻辑

---

**制定日期**: 2026-05-08
**适用场景**: Docker 构建成功但容器连接/启动卡住
