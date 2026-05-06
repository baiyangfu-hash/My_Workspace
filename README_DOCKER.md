# Docker 开发环境使用指南

> **版本**: V1.1.0 (换电脑开发专用版)
> **更新日期**: 2026-05-06
> **适用场景**:
>   - ✅ 更换电脑后快速恢复开发环境
>   - ✅ 多电脑协同开发
>   - ✅ 国际版 Trae Pro 用户 token 优化
> **预计阅读时间**: 15分钟
> **预计操作时间**: 20-30分钟（首次配置）

---

## 📖 目录

- [🎯 核心概念](#-核心概念)
- [⚡ 快速开始（3步概览）](#-快速开始3步概览)
- [📋 前置条件检查清单](#-前置条件检查清单)
- [🔧 详细步骤：首次配置（当前电脑）](#-详细步骤首次配置当前电脑)
- [🚀 详细步骤：迁移到新电脑](#-详细步骤迁移到新电脑)
- [✅ 环境验证清单](#-环境验证清单)
- [💰 Trae Pro Token 优化策略](#-trae-pro-token-优化策略)
- [🛠️ 常用操作速查](#-常用操作速查)
- [❌ 故障排查手册](#-故障排查手册)
- [📚 高级配置（可选）](#-高级配置可选)

---

## 🎯 核心概念

### 这个Docker环境是什么？

一个**预配置的、可移植的、一致的开发环境容器**，包含：
- **Python 3.11** + 常用开发工具（pytest, black, flake8等）
- **Go 1.24** + 模块缓存
- **VS Code** + 预装扩展（Python, Go, GitLens等）
- **中文支持** + 中文字体
- **所有项目依赖**自动安装

### 为什么需要它？

| 场景 | 不使用Docker | 使用Docker |
|------|-------------|-----------|
| **换电脑** | 需要手动安装Python/Go/VS Code扩展（2-4小时） | **一键启动（15分钟）** |
| **多电脑同步** | 环境可能不一致导致"在我机器上能跑" | **100%环境一致性** |
| **团队协作** | "你装了哪个版本的包？" | **统一标准，消除环境问题** |
| **项目切换** | 不同项目依赖冲突 | **隔离容器，互不影响** |

### 工作空间目录结构（2026-05-06 更新）

```
D:\BaiduSyncdisk\My_Workspace\          ← 百度云同步盘根目录
│
├── .devcontainer/                        ← Docker配置（不要修改！）
│   ├── devcontainer.json                 VS Code Dev Container主配置
│   ├── docker-compose.yml                多容器编排
│   ├── Dockerfile                         镜像构建定义
│   └── post-create.sh                    容器启动后自动执行脚本
│
├── 0100_PLC自动化/                       ← PLC项目（原0100_项目，已重命名）
│   ├── DJ-2026-005/                      边框缓存机项目
│   ├── DJ-2026-000/                      测试项目
│   └── 01_SharedLibraries/                PLC共享库(SysLib)
│       └── SysLib/
│           └── timer/FB_TON.scl          FB_TON定时器(重要!)
│
├── 01_Project自动化项目管理/              ← Python项目
│   └── Python自动化项目总库/
│       └── 02_在研项目/
│           ├── SW-2026-004_Python项目管理工具/
│           ├── SW-2026-001_PLC变量表解析工具/
│           └── SW-2026-005_PLC项目管理工具/
│
├── 00_Obsidian_Base全局规范文件仓库/        ← 规范文档（仅PM通用规范）
│
├── .dockerignore                          Docker构建忽略规则
└── README_DOCKER.md                       ← 你正在看的这个文件
```

---

## ⚡ 快速开始（3步概览）

> ⏱️ **总时间：20-30分钟（首次） | 10-15分钟（后续换电脑）**

```
Step 1: 安装基础软件（5分钟）
   ↓
Step 2: 启动Dev Container（10-15分钟）
   ↓
Step 3: 验证环境（2分钟）
   ↓
✅ 开始开发！
```

---

## 📋 前置条件检查清单

在开始之前，请确认以下事项：

### 必须具备 ✅

- [ ] **百度云同步盘已安装并登录**
  - 确保工作空间路径为 `D:\BaiduSyncdisk\My_Workspace`
  - 状态栏显示"同步完成"
  
- [ ] **磁盘空间充足**
  - Docker需要 **50GB+** 可用空间（用于镜像和Volume）
  - 工作空间本身建议 **20GB+**

- [ ] **网络连接正常**
  - 首次构建需要下载基础镜像（~2GB）
  - 后续启动无需网络（除非重建镜像）

### 推荐配置 💪

- [ ] **内存 ≥ 16GB**（8GB也可用，但会较慢）
- [ ] **CPU ≥ 4核**（2核最低要求）
- [ ] **SSD硬盘**（HDD会明显变慢）

### 软件版本要求

| 软件 | 最低版本 | 推荐版本 | 用途 |
|------|---------|---------|------|
| Docker Desktop | 4.0+ | 最新稳定版 | 运行容器 |
| VS Code | 1.85+ | 最新稳定版 | 代码编辑器 |
| Remote Containers扩展 | 0.200+ | 最新版 | 连接容器 |

---

## 🔧 详细步骤：首次配置（当前电脑）

### Step 1: 安装 Docker Desktop（3分钟）

#### Windows 安装

1. 访问 [Docker Desktop 官网](https://www.docker.com/products/docker-desktop/)
2. 点击 **"Download for Windows"**
3. 运行安装程序，一路默认即可
4. **安装完成后必须重启电脑！**

#### 推荐设置（提升性能）

打开 Docker Desktop → Settings：

```
Resources → Memory: 4GB+ （根据你的物理内存调整，建议25%）
Resources → Disk: 50GB+
General → ☑ Start Docker Desktop when you log in
```

**验证安装成功**:
```powershell
# 打开PowerShell或CMD
docker --version
# 应输出: Docker version 27.x.x, build xxxxx

docker info
# 如果显示系统信息，说明Docker运行正常
```

---

### Step 2: 安装 VS Code 和扩展（3分钟）

1. 打开 VS Code
2. 按 `Ctrl+Shift+X` 打开扩展面板
3. 搜索并安装以下扩展：

| 扩展名 | 扩展ID | 用途 |
|--------|--------|------|
| **Dev Containers** | `ms-vscode-remote.remote-containers` | 🔴 **必需！连接Docker容器** |

> 💡 **提示**: 其他扩展（Python、Go等）会在容器内自动安装，无需手动安装

**验证扩展安装成功**:
- 按 `F1` 输入 "Dev Containers"
- 应该看到多个 "Dev Containers: xxx" 命令

---

### Step 3: 启动开发容器（12-15分钟，仅首次）

#### 方法A：自动检测（推荐）✅

1. 使用 VS Code 打开工作区文件夹：
   ```
   File → Open Folder → 选择 D:\BaiduSyncdisk\My_Workspace
   ```

2. VS Code 右下角弹出提示框：
   ```
   ┌─────────────────────────────────────┐
   │ This folder has a Dev Container     │
   │ configuration. Do you want to        │
   │ reopen it in a Container?            │
   │                                     │
   │ [Reopen in Container] [Don't Ask Again] │
   └─────────────────────────────────────┘
   ```

3. 点击 **"Reopen in Container"**

4. 等待构建过程完成（会看到进度提示）：

   ```
   ⏳ 阶段 1: 准备构建环境 (~30秒)
   ⏳ 阶段 2: 拉取基础镜像 (~2分钟，需网络)
   ⏳ 阶段 3: 安装系统依赖 (~3分钟)
   ⏳ 阶段 4: 配置Python和Go环境 (~2分钟)
   ⏳ 阶段 5: 安装VS Code扩展 (~3分钟)
   ⏳ 阶段 6: 执行post-create.sh (~1分钟)
   ```

5. 看到 **"✅ 开发环境已就绪！"** 提示即表示成功！

#### 方法B：命令面板手动启动

如果自动检测未触发：

1. 按 `F1` 或 `Ctrl+Shift+P`
2. 输入并选择：**"Dev Containers: Reopen in Container"**
3. 等待构建完成

---

### Step 4: 首次启动验证（2分钟）

在 VS Code 底部的终端中（注意：这是容器内的终端），运行：

```bash
# ====== 1. 检查 Python 环境 ======
python --version
# 应输出: Python 3.11.x

pip list | grep -E "(pytest|black|flake)"
# 应显示: pytest, black, flake8 等已安装

# ====== 2. 检查 Go 环境 ======
go version
# 应输出: go version go1.24.x linux/amd64

# ====== 3. 检查工作空间挂载 ======
ls /workspace/
# 应显示: 0100_PLC自动化/  01_Project自动化项目管理/ ...

# ====== 4. 测试Python项目导入 ======
cd /workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-001_PLC变量表解析工具/02_开发文件
python -c "import pytest; print('✅ pytest OK')"
# 应输出: ✅ pytest OK

# ====== 5. 测试Git配置 ======
git config --global user.name
git config --global user.email
# 应显示你的用户名和邮箱（从宿主机加载）
```

**全部通过？** 🎉 **恭喜！环境配置成功，可以开始开发了！**

---

## 🚀 详细步骤：迁移到新电脑

> ⚠️ **前提：旧电脑上的代码已全部同步到百度云盘**

### 场景描述

当你更换新电脑时，按照以下步骤可在 **20-30分钟** 内恢复完整的开发环境。

### Phase 1: 基础软件安装（5-10分钟）

| 操作 | 时间 | 说明 |
|------|------|------|
| 安装Docker Desktop | 3分钟 | 从官网下载安装包 |
| 安装VS Code | 2分钟 | 从官网下载安装包 |
| 安装Remote Containers扩展 | 1分钟 | VS Code扩展市场搜索 |
| 登录百度云同步盘 | 2分钟 | 登录并等待同步完成 |
| 重启电脑 | 1分钟 | 确保Docker服务正常启动 |

**关键点**：
- ✅ 确保百度云同步盘状态栏显示"**同步完成**"
- ✅ 确认 `D:\BaiduSyncdisk\My_Workspace` 目录存在且内容完整
- ✅ 可以看到 `.devcontainer/` 文件夹

### Phase 2: 启动开发环境（10-15分钟）

1. **打开VS Code**
   ```
   File → Open Folder → D:\BaiduSyncdisk\My_Workspace
   ```

2. **等待自动检测**
   - VS Code右下角应弹出Dev Container提示
   - 如果没有，按 `F1` → "Dev Containers: Reopen in Container"

3. **点击 "Reopen in Container"**

4. **等待自动构建**
   
   构建过程中你会看到：
   - 左下角显示进度
   - 终端输出构建日志
   - 最后执行 post-create.sh 脚本

5. **观察post-create.sh输出**（重要！）

   成功时你应该看到：
   ```
   🚀 开始配置开发环境...
   📦 检查并安装Python项目依赖...
     → 安装 SW-2026-004 依赖...
     → 安装 SW-2026-001 依赖...
     → 安装 SW-2026-005 依赖...
   📦 检查并下载Go模块依赖...
     → 下载 DJ-2026-005 Go模块 (.plc-out)...
       ✅ DJ-2026-005 Go模块下载完成
     → 下载 DJ-2026-000 Go模块...
       ✅ DJ-2026-000 Go模块下载完成
     → 下载 DJ-2026-005 通用ST程序 Go模块...
       ✅ 通用ST程序Go模块下载完成
   🔧 检查Git配置...
     ✅ Git配置已从宿主机加载
     • 用户名: Your Name
     • 邮箱: your.email@example.com
   
   ==========================================
   ✅ 开发环境配置完成！
   ==========================================
   
   📋 环境信息：
     • Python: Python 3.11.x
     • Go: go1.24.x
     • 工作空间: /workspace
     • 容器用户: vscode
   
   📁 已识别的项目目录：
     ✅ 0100_PLC自动化/ (PLC项目)
     ✅ 01_Project自动化项目管理/ (Python项目)
     ✅ 00_Obsidian_Base全局规范文件仓库/ (规范文档)
   
   💡 下一步操作：
     1. VS Code扩展已自动安装
     2. 项目依赖已预安装（如有失败请查看上方警告）
     3. 可以开始开发了！
   ```

   > ⚠️ **如果看到警告信息**：通常可以忽略，但不放心的话查看[故障排查手册](#-故障排查手册)

### Phase 3: 快速验证（2分钟）

运行核心验证命令：

```bash
# 一键验证脚本（复制粘贴到终端）
echo "=== 环境验证 ===" && \
python --version && \
go version | awk '{print "Go: "$3}' && \
echo "=== 项目目录 ===" && \
ls -d /workspace/*/ && \
echo "=== Git配置 ===" && \
git config --global user.name && \
git config --global user.email && \
echo "✅ 验证完成！"
```

**预期输出**：
```
=== 环境验证 ===
Python 3.11.x
Go: go1.24.x
=== 项目目录 ===
0100_PLC自动化/
01_Project自动化项目管理/
00_Obsidian_Base全局规范文件仓库/
=== Git配置 ===
Your Name
your.email@example.com
✅ 验证完成！
```

### Phase 4: 开始开发 🎉

所有配置已完成！你可以：

- ✅ 直接编辑代码（保存即同步到百度云盘）
- ✅ 在终端运行Python/Go命令
- ✅ 使用Git提交代码
- ✅ 使用所有VS Code功能

---

## ✅ 环境验证清单

每次换电脑或重新构建后，建议运行此清单：

### 基础环境验证

- [ ] **Python可用？**
  ```bash
  python --version  # Python 3.11.x
  ```

- [ ] **Go可用？**
  ```bash
  go version  # go1.24.x
  ```

- [ ] **Git配置正确？**
  ```bash
  git config --global user.name  # 你的名字
  git config --global user.email # 你的邮箱
  ```

- [ ] **工作空间挂载正确？**
  ```bash
  ls /workspace/  # 能看到项目目录
  ```

### 项目依赖验证

- [ ] **Python pytest可用？**
  ```bash
  pytest --version  # pytest 8.0.x
  ```

- [ ] **PLC项目的Go模块已下载？**
  ```bash
  cd /workspace/0100_PLC自动化/DJ-2026-005/.plc-out/golang
  go list -m all  # 应列出依赖包，无报错
  ```

- [ ] **Python项目管理工具依赖已安装？**
  ```bash
  cd /workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码
  python -c "import fastapi; print('✅ FastAPI OK')"  # 或其他项目的主依赖
  ```

### 功能性验证

- [ ] **VS Code扩展已安装？**
  - 左侧扩展栏能看到：Python, Go, GitLens等
  - Python文件能自动补全
  - Go文件能自动格式化

- [ ] **中文显示正常？**
  - 终端中文无乱码
  - VS Code界面中文正常

- [ ] **Git SSH可用？**
  ```bash
  ssh -T git@github.com
  # 应输出: Hi username! You've successfully authenticated
  ```

---

## 💰 Trae Pro Token 优化策略

> **目标：在保证开发效率的前提下，最大限度减少Token消耗**

### 🎯 核心原则

1. **本地优先，AI辅助**：能在本地做的操作不问AI
2. **精准提问，避免废话**：每次交互都要有明确目的
3. **批量处理，减少轮次**：把相关问题一次性提完
4. **善用上下文，避免重复**：让AI记住之前的决策

### 📊 Token消耗场景分析

| 操作 | Token消耗量 | 优化策略 |
|------|-------------|----------|
| **环境搭建咨询** | 高（~5000-10000） | ❌ **避免**：本文档已覆盖 |
| **代码生成** | 中高（~3000-8000） | ✅ **优化**：提供清晰spec |
| **Bug调试** | 高（~5000-15000） | ✅ **优化**：先自行排查，精确定位 |
| **代码审查** | 中（~2000-5000） | ✅ **适合**：AI擅长此项 |
| **文档编写** | 中高（~4000-10000） | ⚠️ **选择性**：模板类自己做 |
| **架构设计** | 高（~8000-15000） | ✅ **值得**：一次性投入长期受益 |

### ✅ 推荐做法（省Token）

#### 1. 环境配置阶段（Token消耗: ~0）

```bash
# ❌ 不要问AI："如何配置Docker环境？"
# ✅ 自己做：严格按照本指南操作

# 本指南已涵盖99%的环境配置问题
# 只有遇到本文档未覆盖的异常情况才咨询AI
```

**省Token技巧**：
- 遇到错误先看[故障排查手册](#-故障排查手册)
- 复制完整错误信息给AI（而非描述症状）
- 一次性问题自己解决，重复性问题再问AI

#### 2. 代码开发阶段（Token消耗: 优化后降低50%+）

**❌ 低效做法（浪费Token）**:
```
用户: 帮我写一个函数，读取CSV文件
AI: [写了一个通用函数] (消耗3000 tokens)
用户: 改一下，加上错误处理
AI: [修改函数] (消耗2000 tokens)
用户: 再加个日志功能
AI: [再次修改] (消耗2000 tokens)
总消耗: ~7000 tokens
```

**✅ 高效做法（省Token）**:
```
用户: 我需要一个Python函数，需求如下：
      1. 读取CSV文件（路径作为参数）
      2. 跳过空行和注释行
      3. 自动检测编码（UTF-8/GBK）
      4. 错误处理：文件不存在时抛出FileNotFoundError
      5. 日志记录：使用logging模块，级别INFO
      6. 返回list of dict
      参考：项目使用pandas，但这里不需要
      
AI: [一次性写出完整函数] (消耗5000 tokens)
总消耗: ~5000 tokens（省28%）
```

**进一步优化**：
```python
# 先自己写框架，只让AI填关键逻辑
def read_csv_safe(filepath):
    """
    安全读取CSV文件
    
    Args:
        filepath: CSV文件路径
        
    Returns:
        list[dict]: 数据列表
        
    Raises:
        FileNotFoundError: 文件不存在
    """
    # TODO: 让AI实现编码检测和异常处理逻辑
    pass
```

#### 3. Bug调试阶段（Token消耗: 降低60%+）

**❌ 低效做法**:
```
用户: 我的代码报错了
AI: 什么错误？
用户: TypeError: ...
AI: 发一下代码和完整错误栈
[... 多轮对话 ...]
总消耗: ~12000 tokens
```

**✅ 高效做法**:
```
用户: 代码运行时报错，请帮我分析原因和修复方案。
      
错误信息：
TypeError: unsupported operand type(s) for +: 'int' and 'str'
位置：file.py line 45, in function calculate_total()
      
代码片段：
```python
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']  # line 45
    return total
```
      
调用方式：
data = [{'name': 'A', 'price': 100}, {'name': 'B', 'price': 'two'}]
calculate_total(data)

AI: [直接给出分析和修复方案] (消耗4000 tokens)
总消耗: ~4000 tokens（省67%）
```

**关键技巧**：
- ✅ 提供**完整错误信息**（而非概括）
- ✅ 提供**最小复现代码**（而非整个文件）
- ✅ 说明**输入数据**和**期望行为**
- ✅ 一次性说清问题，避免多轮追问

#### 4. 代码审查阶段（Token消耗: 值得投入）

**这是AI最擅长的领域，建议适当投入Token**：

```bash
# ✅ 好的做法：让AI审查关键模块
"请审查以下PLC程序的FB_Conveyor功能块，
重点关注：
1. 命名规范是否符合LSP-905
2. 定时器使用是否符合LSP-903
3. 是否有潜在的竞态条件
4. 错误处理是否完善

[附上完整代码]
"
```

**预期收益**：
- 发现人工容易遗漏的问题
- 学习最佳实践
- 一次性投入，长期受用

#### 5. 文档编写阶段（选择性使用AI）

| 文档类型 | AI参与度 | 建议 |
|----------|---------|------|
| **技术规范** (LSP-905等) | ❌ 不用 | 已有模板，按格式填写 |
| **API接口文档** | ⚠️ 部分 | 让AI生成初稿，人工润色 |
| **用户手册** | ✅ 可用 | AI擅长组织结构 |
| **变更记录** | ❌ 不用 | 机械性工作，自己做更快 |
| **README** | ⚠️ 部分 | AI生成框架，补充实例 |

### 🛠️ Trae Pro 专属优化配置

#### 1. 创建 .trae/rules/project-rule.md（如尚未创建）

```markdown
# Trae Pro Token 优化规则

## 代码生成规范
- 必须遵循现有项目的命名规范和架构模式
- 新增代码必须有类型注解和docstring
- 复杂逻辑必须添加行内注释说明意图

## 对话规范
- 每次提问前先自查本指南和项目文档
- 提供完整的错误信息和上下文代码
- 批量提出相关问题，减少对话轮次
- 明确指定输出格式（代码/文档/分析报告）

## Token预算建议
- 单次对话不超过8000 tokens（复杂任务除外）
- 环境配置类问题优先查阅README_DOCKER.md
- Bug调试类问题先自行排查至少10分钟
```

#### 2. 利用工作空间的已有资源

```bash
# ✅ 优先查阅这些文档（免费且准确）
- 00_Obsidian_Base全局规范文件仓库/  # PM规范和流程
- 0100_PLC自动化/00_通用规范/     # PLC编程规范
- 01_Project/00_通用规范/            # Python开发规范
- .devcontainer/                     # Docker环境配置

# ❌ 避免问AI的重复性问题
- "项目目录结构是怎样的？"  → 看 README
- "命名规范是什么？"          → 看 LSP-905
- "如何配置.plc.json？"      → 看 LSP-907
- "Git提交格式？"             → 看 .trae/rules/git-commit-message.md
```

#### 3. 批量任务合并技巧

**❌ 分开问（高消耗）**:
```
对话1: 帮我写函数A (3000 tokens)
对话2: 帮我写函数B (3000 tokens)  
对话3: 帮我写单元测试 (4000 tokens)
总计: 10000 tokens
```

**✅ 合并问（低消耗）**:
```
对话1: 我需要实现以下3个功能，请一次性完成：
      1. 函数A：[详细需求]
      2. 函数B：[详细需求]
      3. 单元测试：测试A和B的边界情况
      
      注意：遵循项目现有的命名规范和架构模式
      (7000 tokens，省30%)
```

---

## 🛠️ 常用操作速查

### 重新构建容器

当修改了 Dockerfile/docker-compose.yml/devcontainer.json 后：

```bash
# 方法1: VS Code命令面板（推荐）
F1 → "Dev Containers: Rebuild Container Without Cache"

# 方法2: 命令行（在VS Code终端外）
cd D:\BaiduSyncdisk\My_Workspace
docker-compose -f .devcontainer/docker-compose.yml down
docker-compose -f .devcontainer/docker-compose.yml up --build -d
```

### 进入容器终端

```bash
# 方法1: VS Code内置终端（推荐）
# 直接使用底部终端即可，已在容器内

# 方法2: 外部终端
docker exec -it plc-python-dev-env bash
```

### 安装新的Python包

```bash
# 临时安装（容器重启后失效）
pip install package-name

# 永久化（添加到requirements.txt）
# 编辑对应项目的requirements.txt，然后：
pip install -r path/to/requirements.txt

# 使用国内镜像加速
pip install package-name -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 查看容器资源占用

```bash
# 查看容器状态
docker ps

# 查看资源占用（实时）
docker stats plc-python-dev-env

# 查看磁盘占用
docker system df
```

### 清理Docker释放磁盘空间

```bash
# 清理未使用的镜像
docker image prune -a

# 清理停止的容器
docker container prune

# 一键清理（慎用！删除所有未使用资源）
docker system prune -a
```

### 备份Volume数据（跨电脑保留缓存）

```bash
# 备份Go模块缓存（约500MB-2GB）
docker run --rm -v plc-dev-go-mod-cache:/data \
  -v $(pwd):/backup alpine \
  tar czf /backup/go-mod-cache-backup.tar.gz -C /data .

# 恢复（在新电脑上）
docker run --rm -v plc-dev-go-mod-cache:/data \
  -v $(pwd):/backup alpine \
  tar xzf /backup/go-mod-cache-backup.tar.gz -C /data
```

---

## ❌ 故障排查手册

### 问题 1: VS Code 未检测到 Dev Container

**症状**: 打开工作区后没有任何提示

**解决方案**:
1. 确认 `.devcontainer/` 文件夹存在
2. 手动启动：`F1` → "Dev Containers: Reopen in Container"
3. 检查 Docker Desktop 是否正在运行
4. 重启 VS Code

---

### 问题 2: Docker 构建失败

**症状**: 构建过程中出现错误

**常见原因及解决**:

```bash
# 1. 检查Docker是否正常运行
docker info
# 如果报错，重启Docker Desktop

# 2. 网络问题（国内常见）
# 设置Docker镜像加速：
# Docker Desktop → Settings → Docker Engine → JSON:
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://hub-mirror.c.163.com"
  ]
}

# 3. 磁盘空间不足
docker system df
# 如果 Available < 5GB，执行清理（见上节"清理Docker"）

# 4. 权限问题（Windows特有）
# 以管理员身份运行VS Code
```

**高级诊断**:
```bash
# 查看详细构建日志
docker build -t test-build .devcontainer/

# 查看哪一步失败（注意最后几行输出）
```

---

### 问题 3: post-create.sh 部分失败

**症状**: 显示 "⚠️ 部分依赖安装失败"

**可能原因**:

1. **路径不存在**（最常见）
   ```bash
   # 在容器内检查
   ls /workspace/0100_PLC自动化/DJ-2026-005/.plc-out/golang/go.mod
   # 如果不存在，说明：
   #   - 该项目还未初始化Go模块（正常，忽略即可）
   #   - 或者目录名不匹配（检查是否为 0100_PLC自动化 而非 0100_项目）
   ```

2. **网络问题**
   ```bash
   # 手动重试失败的步骤
   cd /workspace/0100_PLC自动化/DJ-2026-005/.plc-out/golang
   go mod download
   ```

3. **pip依赖冲突**
   ```bash
   # 查看具体错误
   pip install -r <requirements.txt>  # 不加 --user，看完整错误
   ```

**影响评估**:
- ⚠️ **Go模块未下载**：首次编译时会自动下载，只是慢一些
- ⚠️ **Python依赖未安装**：运行项目时会报 ImportError，需手动安装
- ✅ **这两个问题都不致命**，只是影响"开箱即用"体验

---

### 问题 4: Volume 挂载失败

**症状**: 容器启动失败，提示路径不存在

**Windows 特有问题解决**:

```bash
# 1. 确认路径格式正确
# 正确: D:\BaiduSyncdisk\My_Workspace
# 错误: /d/BaiduSyncdisk/My_Workspace

# 2. 检查 docker-compose.yml 中的 volumes
# 确保 .. 指向工作空间父目录（已配置正确）

# 3. 权限问题
# Docker Desktop → Settings → Resources → File Sharing
# 添加 D:\ 盘（如果未添加）
```

---

### 问题 5: 容器内性能慢

**优化方案**:

```bash
# 1. 增加Docker资源限制
# Docker Desktop → Settings → Resources
#    Memory: 4GB+ (建议物理内存的25%)
#    CPUs: 4+

# 2. 使用cached模式（已启用）
# docker-compose.yml 已配置 :cached
# 这意味着文件写入先缓存，定期同步到宿主机

# 3. 避免频繁读写大文件
# .plc-out/ 目录已在 .dockerignore 中排除
# 编译产物不会拖慢容器

# 4. 将大型依赖缓存到Volume（已配置）
# go-mod-cache, pip-cache 等 Volume 已持久化
# 第二次启动容器时无需重新下载
```

**性能参考表**:

| 操作 | 本地环境 | Docker环境 | 差异 | 可接受？ |
|------|---------|------------|------|---------|
| VS Code 启动 | ~3秒 | ~5秒 | +2秒 | ✅ |
| Python 解释 | 基准 | +5-10% | 可接受 | ✅ |
| Go 编译 | 基准 | +8-12% | 可接受 | ✅ |
| 单元测试 | 基准 | +5-8% | 可接受 | ✅ |
| pip install (首次) | 基准 | 相同 | 无差异 | ✅ |
| pip install (缓存命中) | 基准 | **更快** | ✅ **更优** |

---

### 问题 6: 中文显示乱码

**解决方案**:

```bash
# 1. 检查locale设置
locale
# 应输出: LANG=zh_CN.UTF-8

# 2. 如果不是zh_CN.UTF-8
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 3. 如果中文字体缺失（容器内通常已安装）
sudo apt-get install fonts-wqy-zenhei
# 需要重新进入容器生效
```

---

### 问题 7: Git/GitHub 认证失败

**症状**: push/pull 时提示权限错误

**解决方案**:

```bash
# 1. 检查SSH密钥是否挂载
ls -la ~/.ssh/
# 应看到: id_rsa, id_rsa.pub, known_hosts 等

# 2. 测试SSH连接
ssh -T git@github.com
# 应输出: Hi username! You've successfully authenticated

# 3. 如果密钥未挂载
# 检查 docker-compose.yml 第34行:
# - ~/.ssh:/home/vscode/.ssh:ro
# 确保宿主机 ~/.ssh 目录存在且有密钥

# 4. 替代方案：使用HTTPS + Personal Access Token
git remote set-url origin https://<token>@github.com/user/repo.git
```

**Windows特殊注意事项**:
- 确保SSH密钥无密码（或使用ssh-agent）
- Docker Desktop → Settings → Resources → Enable "Use credential helper"
- 首次连接GitHub时会弹窗确认

---

### 问题 8: 换电脑后项目路径不对

**症状**: post-create.sh 报错 "路径不存在"

**根本原因**: 工作空间目录名与post-create.sh中的硬编码路径不一致

**已知的历史变更**:
```
2026-05-06: 0100_项目 → 0100_PLC自动化 (已在本版本修复)
```

**验证方法**:
```bash
# 在容器内检查实际目录名
ls -d /workspace/0100*/
# 应显示: 0100_PLC自动化/

# 如果仍显示 0100_项目，说明：
# 1. 百度云还未同步完成（等待同步）
# 2. 或者需要手动更新post-create.sh（联系维护者）
```

---

## 📚 高级配置（可选）

### 配置国内镜像加速（推荐国内用户）

编辑 Docker Desktop：
```
Settings → Docker Engine → JSON configuration:
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

**效果**: 镜像拉取速度提升 **5-10倍**

### 自定义VS Code设置

在 `.devcontainer/devcontainer.json` 的 `customizations.vscode.settings` 中添加：

```json
{
  "editor.fontSize": 14,
  "editor.tabSize": 4,
  "terminal.integrated.fontSize": 13,
  "workbench.colorTheme": "Default Dark+",
  "python.formatting.provider": "black",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  }
}
```

### 添加数据库服务（如需要）

在 `docker-compose.yml` 末尾添加：

```yaml
  # PostgreSQL数据库示例
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: example
      POSTGRES_DB: myproject
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - dev-network

# 在 volumes: 部分添加
volumes:
  # ... 已有的volumes ...
  postgres-data:

# 保存后重建容器
```

### 调整容器资源限制

编辑 `docker-compose.yml` 的 `deploy.resources` 部分：

```yaml
deploy:
  resources:
    limits:
      memory: 8G      # 最大内存（根据你的物理内存调整）
      cpus: '4'       # 最大CPU核数
    reservations:
      memory: 2G      # 保证内存
      cpus: '1'       # 保证CPU
```

**推荐配置**:

| 物理内存 | memory限制 | 保留内存 |
|---------|-----------|---------|
| 8GB | 4G | 1G |
| 16GB | 8G | 2G |
| 32GB | 16G | 4G |

---

## 📊 性能对比参考

| 操作 | 本地裸机 | Docker环境 | 差异 | 备注 |
|------|---------|-----------|------|------|
| **环境搭建** | 2-4小时 | **15-20分钟** | ⬇️ **90%+** | Docker完胜 |
| **VS Code 启动** | ~3秒 | ~5秒 | +2秒 | 可接受 |
| **Python 运行** | 基准 | +5-10% | 可接受 | 容器开销 |
| **Go 编译** | 基准 | +8-12% | 可接受 | 容器开销 |
| **单元测试** | 基准 | +5-8% | 可接受 | 影响很小 |
| **pip install (首次)** | 基准 | 相同 | 0% | 无差异 |
| **pip install (缓存)** | 基准 | **更快** | ✅ **更优** | Volume缓存生效 |
| **第二次启动容器** | N/A | **<30秒** | ✅ **极快** | 镜像和缓存已就绪 |
| **跨电脑迁移** | 2-4小时 | **20分钟** | ⬇️ **90%** | Docker完胜 |

---

## 🔄 版本历史

| 版本 | 日期 | 主要变更 | 影响范围 |
|------|------|----------|----------|
| **V1.1.0** | **2026-05-06** | **🆕 修复post-create.sh路径错误**<br>**🆕 添加Trae Pro Token优化章节**<br>**🆕 增强故障排查手册**<br>**🆕 更新目录名称(0100_PLC自动化)** | 所有用户 |
| V1.0.0 | 2026-05-05 | 初始版本 | - |

---

## 📞 获取帮助

如果本文档未能解决你的问题：

### 优先级排序（省Token原则）

1. **查阅本文档** - 90%的问题都有答案
2. **查看官方文档**:
   - [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
   - [Docker Desktop](https://docs.docker.com/desktop/)
3. **在项目Issues中提交问题** - 附上完整错误信息
4. **最后手段：咨询AI** - 提供完整上下文，避免多轮追问

### 提交问题时请包含

```bash
# 必须信息（缺少可能导致无法诊断）
1. 操作系统和版本: Windows 10/11 x64
2. Docker Desktop版本: docker --version
3. VS Code版本: Help → About
4. 完整错误信息（截图或文本）
5. 复现步骤（越详细越好）

# 可选信息（有助于快速定位）
6. .devcontainer/ 目录截图
7. docker logs plc-python-dev-env 输出
8. 已尝试的解决方法
```

---

## ✨ 最佳实践总结

### 日常开发习惯

1. **每天开工**:
   - 打开VS Code → 自动重连容器（<30秒）
   - 终端运行 `git pull` 拉取最新代码
   - 开始编码 🚀

2. **下班前**:
   - Git commit + push（代码自动同步到百度云盘）
   - 关闭VS Code（容器自动停止）
   - Docker Desktop 保持后台运行（可选）

3. **换电脑时**:
   - 安装Docker + VS Code（10分钟）
   - 打开工作区 → Reopen in Container（15分钟）
   - 验证环境 → 开始开发 ✅

### Token节省口诀

> **"三思而后问AI"**

1. **我能从文档找到答案吗？** → 是 → 查文档（省5000+ tokens）
2. **我能自己试5分钟解决吗？** → 是 → 先尝试（省3000+ tokens）
3. **这个问题值得问吗？** → 否 → 放弃或简化需求
4. **能否批量合并问题？** → 是 → 一次问完（省50% tokens）

---

**最后更新**: 2026-05-06
**维护者**: 开发团队
**适用范围**: 所有使用Docker开发环境的团队成员
**下次审查**: 按需（当目录结构或依赖发生重大变化时）
