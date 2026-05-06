# Docker 开发环境使用指南

> **版本**: V1.0.0  
> **更新日期**: 2026-05-05  
> **适用场景**: 更换电脑后快速恢复开发环境

---

## 📋 目录

- [快速开始](#快速开始)
- [首次使用（当前电脑）](#首次使用当前电脑)
- [迁移到新电脑](#迁移到新电脑)
- [常用操作](#常用操作)
- [常见问题排查](#常见问题排查)

---

## 快速开始

### 前置条件

| 软件 | 版本要求 | 用途 |
|------|---------|------|
| Docker Desktop | 最新稳定版 | 运行容器 |
| VS Code | 最新稳定版 | 代码编辑 |
| Remote - Containers 扩展 | 最新版 | 连接容器 |

### 一键启动

```bash
# 1. 使用 VS Code 打开工作空间
code d:\BaiduSyncdisk\My_Workspace

# 2. VS Code 会自动检测到 .devcontainer 目录
# 3. 点击提示框中的 "Reopen in Container"
# 4. 等待镜像构建完成（首次约10-15分钟）
```

---

## 首次使用（当前电脑）

### 步骤 1：安装 Docker Desktop

1. 访问 [Docker Desktop 官网](https://www.docker.com/products/docker-desktop/)
2. 下载 Windows 版本并安装
3. 安装完成后重启电脑
4. 启动 Docker Desktop 并登录（可选）

**推荐设置**：
- Settings → Resources → 内存：建议分配 **4GB+**
- Settings → Resources → 磁盘：建议 **50GB+**
- Settings → General：开启 "Start Docker Desktop when you log in"

### 步骤 2：安装 VS Code 扩展

1. 打开 VS Code
2. 按 `Ctrl+Shift+X` 打开扩展面板
3. 搜索并安装 **"Dev Containers"** (ID: `ms-vscode-remote.remote-containers`)
4. 重启 VS Code

### 步骤 3：启动开发容器

1. 使用 VS Code 打开 `d:\BaiduSyncdisk\My_Workspace`
2. 按 `F1` 或 `Ctrl+Shift+P` 打开命令面板
3. 输入并选择 **"Dev Containers: Reopen in Container"**
4. 等待构建过程完成：

```
✅ 阶段 1: 拉取基础镜像 (~2分钟)
✅ 阶段 2: 安装系统依赖 (~3分钟)  
✅ 阶段 3: 配置Python和Go环境 (~2分钟)
✅ 阶段 4: 安装VS Code扩展 (~3分钟)
✅ 阶段 5: 安装项目依赖 (~2分钟)
```

5. 看到 "开发环境已就绪！" 提示即表示成功

### 步骤 4：验证环境

在 VS Code 终端中运行：

```bash
# 检查 Python
python --version
# 应输出: Python 3.11.x

# 检查 Go
go version
# 应输出: go version go1.24.x linux/amd64

# 检查 Git
git --version
# 应输出: git version 2.x.x

# 测试 Python 项目导入
cd /workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-001_PLC变量表解析工具/02_开发文件
python -c "import pytest; print('pytest OK')"
```

---

## 迁移到新电脑

### 场景描述

当你更换新电脑时，按照以下步骤可在 **10-15分钟** 内恢复完整的开发环境。

### 步骤清单

#### ✅ 第一步：安装基础软件（~10分钟）

| 操作 | 时间 | 说明 |
|------|------|------|
| 安装 Docker Desktop | 3分钟 | 从官网下载安装包 |
| 安装 VS Code | 2分钟 | 从官网下载安装包 |
| 安装 Remote Containers 扩展 | 1分钟 | VS Code扩展市场搜索 |
| 同步百度云盘数据 | 3分钟 | 登录百度云同步盘，等待同步完成 |
| 重启电脑 | 1分钟 | 确保Docker服务正常启动 |

#### ✅ 第二步：启动开发环境（~10-15分钟）

1. 打开 VS Code
2. 文件 → 打开文件夹 → 选择 `D:\BaiduSyncdisk\My_Workspace`
3. VS Code 右下角弹出提示：**"This folder has a Dev Container configuration. Do you want to reopen it in a Container?"**
4. 点击 **"Reopen in Container"**
5. 等待自动构建完成

#### ✅ 第三步：验证环境（~2分钟）

打开终端，运行验证命令（见上方"验证环境"部分）

#### ✅ 第四步：开始开发

所有配置已就绪，可以直接开始编码！

---

## 常用操作

### 重新构建容器

当修改了 `Dockerfile`、`docker-compose.yml` 或 `devcontainer.json` 后需要重建：

```
方法 1: 命令面板
F1 → "Dev Containers: Rebuild Container Without Cache"

方法 2: 命令行（在VS Code终端外）
cd d:\BaiduSyncdisk\My_Workspace
docker-compose -f .devcontainer/docker-compose.yml down
docker-compose -f .devcontainer/docker-compose.yml up --build -d
```

### 进入容器终端

```bash
方法 1: VS Code 内置终端（推荐）
直接使用 VS Code 底部的终端即可，它已经在容器内

方法 2: 外部终端
docker exec -it plc-python-dev-env bash
```

### 安装新的 Python 包

```bash
# 临时安装（容器重启后失效）
pip install package-name

# 永久安装（添加到 requirements.txt）
# 编辑对应项目的 requirements.txt，然后：
pip install -r path/to/requirements.txt
```

### 安装新的 VS Code 扩展

```bash
方法 1: GUI（推荐）
左侧扩展面板 → 搜索 → 安装（会自动安装在容器内）

方法 2: CLI
# 在容器终端中
code-server --install-extension extension-id
```

### 查看容器资源使用

```bash
# 查看容器状态
docker ps

# 查看资源占用
docker stats plc-python-dev-env

# 查看磁盘占用
docker system df
```

### 清理 Docker 资源

```bash
# 清理未使用的镜像（释放磁盘空间）
docker image prune -a

# 清理停止的容器
docker container prune

# 一键清理所有未使用资源
docker system prune -a  # ⚠️ 会删除所有未使用的镜像
```

### 备份和恢复 Volume 数据

```bash
# 备份 Volume
docker run --rm -v plc-dev-go-mod-cache:/data -v $(pwd):/backup alpine tar czf /backup/go-mod-cache-backup.tar.gz -C /data .

# 恢复 Volume
docker run --rm -v plc-dev-go-mod-cache:/data -v $(pwd):/backup alpine tar xzf /backup/go-mod-cache-backup.tar.gz -C /data
```

---

## 常见问题排查

### 问题 1：Docker 构建失败

**症状**: 构建过程中出现错误

**解决方案**:
```bash
# 1. 检查 Docker 是否正常运行
docker info

# 2. 查看详细错误日志
docker build -t test-build .devcontainer/

# 3. 常见原因：
#    - 网络问题：检查代理设置
#    - 磁盘空间不足：清理 Docker 缓存
#    - 权限问题：以管理员身份运行
```

### 问题 2：Volume 挂载失败

**症状**: 容器启动失败，提示路径不存在或权限不足

**解决方案**:
```bash
# Windows 特有问题：确保路径格式正确
# 正确: D:\BaiduSyncdisk\My_Workspace
# 错误: /d/BaiduSyncdisk/My_Workspace

# 在 docker-compose.yml 中检查 volumes 路径
# 确保 .. 指向正确的工作空间父目录
```

### 问题 3：Python 包安装失败

**症状**: `pip install` 报错

**解决方案**:
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像源
pip install package-name -i https://pypi.tuna.tsinghua.edu.cn/simple

# 如果是编译错误，可能缺少系统依赖
# 检查 Dockerfile 中是否包含必要的 lib
```

### 问题 4：Go 模块下载慢

**症状**: `go mod download` 很慢或超时

**解决方案**:
```bash
# 设置 Go 代理（国内）
export GOPROXY=https://goproxy.cn,direct

# 或永久写入 bashrc
echo 'export GOPROXY=https://goproxy.cn,direct' >> ~/.bashrc
```

### 问题 5：中文显示乱码

**症状**: 终端或GUI应用显示中文为问号或方块

**解决方案**:
```bash
# 检查 locale 设置
locale

# 如果不是 zh_CN.UTF-8，手动设置
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 安装中文字体（如果缺失）
sudo apt-get install fonts-wqy-zenhei
```

### 问题 6：性能较慢

**症状**: 容器内操作比本地慢

**优化建议**:
```bash
# 1. 增加 Docker 资源限制
#    Docker Desktop → Settings → Resources → 调高内存和CPU

# 2. 使用 cached 挂载模式（已默认启用）
#    docker-compose.yml 中已配置 :cached

# 3. 将大型依赖缓存到 Volume（已配置）
#    go-mod-cache, pip-cache 等 Volume 已持久化

# 4. 避免频繁读写大文件
#    .plc-out 目录已添加到 .dockerignore
```

### 问题 7：SSH/Git 认证失败

**症状**: Git push/pull 时提示权限错误

**解决方案**:
```bash
# 1. 检查 SSH 密钥是否挂载
ls -la ~/.ssh/
# 应看到 id_rsa, id_rsa.pub 等文件

# 2. 测试 SSH 连接
ssh -T git@github.com

# 3. 如果密钥未挂载，检查 docker-compose.yml
#    确保 - ~/.ssh:/home/vscode/.ssh:ro 存在

# 4. 或者改用 HTTPS + token 方式
git remote set-url origin https://<token>@github.com/user/repo.git
```

---

## 高级配置（可选）

### 配置国内镜像加速

编辑 Docker Desktop 设置：
```
Settings → Docker Engine → JSON configuration:
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://hub-mirror.c.163.com"
  ]
}
```

### 自定义 VS Code 设置

在 `.devcontainer/devcontainer.json` 的 `customizations.vscode.settings` 中添加：

```json
{
  "editor.fontSize": 14,
  "editor.tabSize": 4,
  "terminal.integrated.fontSize": 13,
  "workbench.colorTheme": "Default Dark+"
}
```

### 添加数据库服务

在 `docker-compose.yml` 中添加：

```yaml
db:
  image: postgres:15
  environment:
    POSTGRES_PASSWORD: example
  ports:
    - "5432:5432"
  volumes:
    - postgres-data:/var/lib/postgresql/data
```

---

## 文件结构说明

```
My_Workspace/
├── .devcontainer/           # Docker 配置目录
│   ├── devcontainer.json   # VS Code Dev Container 主配置
│   ├── docker-compose.yml  # 多容器编排配置
│   ├── Dockerfile          # 镜像构建定义
│   └── post-create.sh      # 容器创建后执行脚本
├── .dockerignore            # Docker 构建忽略规则
└── README_DOCKER.md         # 本文档
```

---

## 性能参考

| 操作 | 本地环境 | Docker 环境 | 差异 |
|------|---------|------------|------|
| VS Code 启动 | ~3秒 | ~5秒 | +2秒 |
| Python 文件解释 | 基准 | +5-10% | 可接受 |
| Go 编译 | 基准 | +8-12% | 可接受 |
| 单元测试 | 基准 | +5-8% | 可接受 |
| pip install（首次） | 基准 | 相同 | 无差异 |
| pip install（缓存命中） | 基准 | 更快 | ✅ Volume缓存 |

---

## 联系与支持

如遇到本文档未覆盖的问题：

1. 查看 [VS Code Dev Containers 官方文档](https://code.visualstudio.com/docs/devcontainers/containers)
2. 查看 [Docker Desktop 官方文档](https://docs.docker.com/desktop/)
3. 在项目 Issues 中提交问题

---

**最后更新**: 2026-05-05  
**维护者**: 开发团队
