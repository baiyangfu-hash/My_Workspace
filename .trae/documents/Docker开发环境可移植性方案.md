# Docker开发环境可移植性方案

## 一、需求分析

### 1.1 当前工作空间概况
- **位置**: `d:\BaiduSyncdisk\My_Workspace`
- **项目类型**:
  - PLC编程项目（Siemens LSP + Go运行时）
  - Python自动化项目（PyQt5 GUI + Flask Web）
- **核心技术栈**:
  - Python 3.x（PyQt5, Flask, SQLAlchemy, PyMuPDF等）
  - Go 1.24.0（PLC代码编译和运行）
  - VS Code + Siemens LSP扩展
  - Git版本控制

### 1.2 核心需求
- ✅ 更换电脑后无需重新配置开发环境
- ✅ 保持现有工作空间结构和项目数据
- ✅ 支持所有现有项目的开发和调试
- ✅ 环境配置一次制作，多机复用
- ✅ 支持GUI应用程序（PyQt5）的开发和测试

---

## 二、解决方案架构

### 2.1 方案选择：VS Code Dev Containers + Docker Compose

采用 **VS Code Remote - Containers** 扩展配合 **Docker Compose** 的方案：
- **优势**:
  - 原生VS Code体验，无需学习新工具
  - 完整的GUI支持（通过本地VS Code连接远程容器）
  - 工作空间通过Volume挂载，数据持久化在本地
  - 所有依赖打包在Docker镜像中，一键复现环境
  - 支持多容器协作（Python + Go + 数据库）

### 2.2 架构图

```
┌─────────────────────────────────────────────────────┐
│                   新电脑（目标机器）                    │
│  ┌──────────┐    ┌──────────────────────────────┐  │
│  │ VS Code  │───▶│     Docker Desktop           │  │
│  │ (本地)   │    │  ┌────────────────────────┐  │  │
│  └──────────┘    │  │  dev-container          │  │  │
│                  │  │  ┌──────────────────┐  │  │  │
│                  │  │  │ Python 3.11      │  │  │  │
│                  │  │  │ Go 1.24          │  │  │  │
│                  │  │  │ Git              │  │  │  │
│                  │  │  │ Siemens LSP      │  │  │  │
│                  │  │  │ Node.js (可选)   │  │  │  │
│                  │  │  └──────────────────┘  │  │  │
│                  │  └────────────────────────┘  │  │
│                  │              │               │  │
│                  │              ▼               │  │
│                  │  ┌────────────────────────┐  │  │
│                  │  │  Volume (数据持久化)    │  │  │
│                  │  │  /workspace            │  │  │
│                  │  │  → d:\BaiduSyncdisk\   │  │  │
│                  │  │    My_Workspace        │  │  │
│                  │  └────────────────────────┘  │  │
│                  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 三、实施方案详细步骤

### 步骤 1：创建Docker配置文件结构

在工作空间根目录创建以下文件：

```
d:\BaiduSyncdisk\My_Workspace\
├── .devcontainer/
│   ├── devcontainer.json        # VS Code Dev Container配置
│   ├── docker-compose.yml       # 多容器编排
│   └── Dockerfile               # 主开发环境镜像定义
├── .dockerignore                # Docker构建忽略文件
└── README_DOCKER.md             # Docker使用说明文档
```

### 步骤 2：编写Dockerfile（主开发环境镜像）

**基础镜像选择**: `mcr.microsoft.com/devcontainers/python:1-3.11-bullseye`（微软官方维护的Dev Container基础镜像）

**需要安装的组件**:
1. **Python 3.11** + 项目依赖包
2. **Go 1.24** (用于PLC程序编译)
3. **Git** + 常用工具（curl, wget, vim等）
4. **Siemens LSP相关依赖**
5. **中文语言支持和字体**（用于PyQt5 GUI显示）
6. **VS Code Server**（由Dev Container自动安装）

### 步骤 3：编写docker-compose.yml

**服务划分**:
- **dev**: 主开发环境（Python + Go + VS Code）
- **db**（可选）: PostgreSQL/MySQL数据库服务（如果项目需要）

**Volume挂载**:
- 工作空间目录 → 容器内的 `/workspace`
- Git配置持久化（~/.gitconfig）
- SSH密钥挂载（用于Git操作）

### 步骤 4：编写devcontainer.json

**VS Code扩展自动安装**:
- Python扩展包
- Go扩展包
- Siemens LSP扩展（如果可用）
- GitLens
- 其他常用扩展

**端口映射**:
- Flask Web服务端口（如需调试Web应用）

**环境变量**:
- PYTHONPATH
- GOPATH
- LANG=zh_CN.UTF-8（支持中文）

### 步骤 5：创建使用文档

编写详细的迁移和使用指南，包括：
- 新电脑环境准备步骤
- Docker Desktop安装
- 工作空间迁移方法
- 常见问题排查

---

## 四、具体文件内容设计

### 4.1 Dockerfile 关键内容

```dockerfile
FROM mcr.microsoft.com/devcontainers/python:0-3.11-bullseye

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    # Go语言环境
    golang-go \
    # GUI支持库（PyQt5需要）
    libgl1-mesa-dev \
    libglib2.0-0 \
    # 中文支持
    fonts-wqy-zenhei \
    locales \
    # 常用工具
    curl wget vim git \
    && rm -rf /var/lib/apt/lists/*

# 配置中文 locale
RUN sed -i '/zh_CN.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG zh_CN.UTF-8
ENV LANGUAGE zh_CN:zh
ENV LC_ALL zh_CN.UTF-8

# 安装Python全局工具
RUN pip install --no-cache-dir \
    pytest \
    black \
    flake8 \
    mypy

# 设置工作目录
WORKDIR /workspace
```

### 4.2 docker-compose.yml 关键内容

```yaml
version: '3.8'

services:
  dev:
    build:
      context: .
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - ..:/workspace:cached
      - ~/.gitconfig:/root/.gitconfig
      - ~/.ssh:/root/.ssh:ro
    environment:
      - PYTHONPATH=/workspace
      - GOPATH=/go
    command: sleep infinity
    # 如需GUI应用调试，取消以下注释
    # environment:
    #   - DISPLAY=${DISPLAY}
    # volumes:
    #   - /tmp/.X11-unix:/tmp/.X11-unix:rw
```

### 4.3 devcontainer.json 关键内容

```json
{
  "name": "PLC & Python Dev Environment",
  "dockerComposeFile": "docker-compose.yml",
  "service": "dev",
  "workspaceFolder": "/workspace",

  "features": {
    "ghcr.io/devcontainers/features/go:1": {},
    "ghcr.io/devcontainers/features/git:1": {}
  },

  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "golang.go",
        "eamodio.gitlens",
        "ms-vscode-remote.remote-containers"
      ]
    }
  },

  "postCreateCommand": "pip install -r requirements.txt || echo 'No root requirements.txt'"
}
```

---

## 五、迁移流程（更换电脑时）

### 5.1 新电脑准备清单

| 序号 | 操作步骤 | 说明 |
|------|---------|------|
| 1 | 安装Docker Desktop | 从官网下载并安装 |
| 2 | 安装VS Code | 从官网下载并安装 |
| 3 | 安装Remote-Containers扩展 | VS Code扩展市场搜索安装 |
| 4 | 同步工作空间 | 通过百度云同步盘或其他方式 |
| 5 | 打开工作空间 | VS Code打开 `My_Workspace` 文件夹 |
| 6 | 重新构建容器 | VS Code提示"Reopen in Container"时确认 |

### 5.2 首次启动时间估算

- Docker镜像构建：**5-10分钟**（首次，之后有缓存会更快）
- 依赖安装：**2-3分钟**
- 总计：**约10-15分钟**即可完成环境搭建

---

## 六、特殊场景处理

### 6.1 PyQt5 GUI应用调试

**方案A（推荐）**: 在宿主机运行GUI应用，容器仅负责代码编辑和测试
- 容器内运行单元测试（headless模式）
- GUI应用在本地Python环境运行（可选保留本地轻量Python）

**方案B**: X11转发（Linux/Mac适用，Windows需额外配置VcXsrv）
- 配置复杂，不推荐作为主要方案

### 6.2 Siemens LSP支持

Siemens LSP是VS Code扩展，需要在容器内安装：
- 将扩展下载为 `.vsix` 文件
- 在 `devcontainer.json` 中指定本地 `.vsix` 路径
- 或使用扩展ID从 marketplace 自动安装

### 6.3 大文件处理（.plc-out目录）

PLC项目的编译输出目录可能较大：
- 已在docker-compose中使用 `cached` 模式挂载
- 可考虑将 `.plc-out` 添加到 `.dockerignore` 避免构建时复制

---

## 七、优势总结

| 特性 | 传统方式 | Docker方式 |
|------|---------|-----------|
| 环境配置时间 | 2-4小时 | 10-15分钟 |
| 环境一致性 | ❌ 易出差异 | ✅ 完全一致 |
| 多项目管理 | 需分别配置虚拟环境 | 统一容器管理 |
| 团队协作 | 手动同步环境要求 | 共享devcontainer配置 |
| 版本回退 | 困难 | 切换镜像标签即可 |
| 清理环境 | 复杂 | `docker prune` 一键清理 |

---

## 八、风险与注意事项

### 8.1 潜在风险
1. **性能开销**: Docker在Windows上基于WSL2，有一定性能损耗（约5-10%）
2. **磁盘空间**: Docker镜像占用约2-5GB磁盘空间
3. **网络配置**: 公司网络可能限制Docker Hub访问（可配置镜像加速）

### 8.2 缓解措施
- 性能敏感的操作（如大型PLC编译）可在本地执行
- 定期清理无用的Docker镜像和容器
- 提前配置国内Docker镜像源

---

## 九、后续优化方向（可选）

1. **多阶段构建**: 分离开发环境和生产环境镜像
2. **预构建镜像**: 推送到私有仓库，新电脑直接pull
3. **CI/CD集成**: 结合GitHub Actions自动化测试
4. **数据库服务**: 添加PostgreSQL容器用于项目测试

---

## 十、执行计划

### Phase 1: 基础配置（本次任务）
- [ ] 创建 `.devcontainer/` 目录结构
- [ ] 编写 `Dockerfile`
- [ ] 编写 `docker-compose.yml`
- [ ] 编写 `devcontainer.json`
- [ ] 创建 `.dockerignore`
- [ ] 编写使用文档

### Phase 2: 测试验证
- [ ] 在当前电脑测试容器构建
- [ ] 验证Python项目可正常运行
- [ ] 验证Go/PLC项目可正常编译
- [ ] 验证VS Code扩展正常工作

### Phase 3: 文档完善
- [ ] 编写详细的迁移指南
- [ ] 录制操作视频（可选）
- [ ] 整理常见问题FAQ
