# Git使用入门计划

## 1. 仓库现状分析

根据提供的信息，用户已经：

* 拥有GitHub账号

* 配置了GitHub个人访问令牌(token)

* 安装了本地Git

* 正在开发边框缓存机项目，需要进行版本管理

## 2. 实施步骤

### 2.1 Git基础配置

1. **配置用户信息**

   * 设置用户名和邮箱

   * 验证Git安装状态

2. **Token配置**

   * 确认token已正确配置

   * 配置Git使用token进行认证

### 2.2 本地仓库初始化

1. **初始化新仓库**

   * 在项目目录中初始化Git仓库

   * 创建.gitignore文件

2. **首次提交**

   * 添加所有文件到暂存区

   * 进行首次提交

### 2.3 远程仓库连接

1. **创建GitHub仓库**

   * 在GitHub上创建新仓库

   * 复制仓库URL

2. **关联本地与远程**

   * 添加远程仓库

   * 推送本地代码到远程

### 2.4 日常版本管理

1. **基本Git命令**

   * `git status` - 查看状态

   * `git add` - 添加文件

   * `git commit` - 提交更改

   * `git push` - 推送更改

   * `git pull` - 拉取更改

2. **分支管理**

   * 创建分支

   * 切换分支

   * 合并分支

### 2.5 版本管理最佳实践

1. **提交规范**

   * 提交信息格式

   * 提交频率

2. **分支策略**

   * 主分支(main)

   * 开发分支(develop)

   * 功能分支(feature)

3. **标签管理**

   * 创建版本标签

   * 发布版本

## 3. 具体操作指南

### 3.1 Git配置

```bash
# 配置用户名
git config --global user.name "Your Name"

# 配置邮箱
git config --global user.email "your.email@example.com"

# 验证配置
git config --list
```

### 3.2 初始化仓库

```bash
# 进入项目目录
cd "d:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\0100_项目\DJ-2026-005_边框缓存机"

# 初始化Git仓库
git init

# 创建.gitignore文件
echo "# IDE files\n.vscode/\n.idea/\n\n# Build files\nbuild/\ndist/\n\n# Log files\nlogs/\n*.log\n\n# Environment files\n.env\n.env.local\n\n# OS files\n.DS_Store\nThumbs.db" > .gitignore
```

### 3.3 首次提交

```bash
# 添加所有文件
git add .

# 首次提交
git commit -m "Initial commit: 边框缓存机项目"
```

### 3.4 连接GitHub

```bash
# 添加远程仓库 (替换为你的GitHub仓库URL)
git remote add origin https://github.com/your-username/buffer-framing-machine.git

# 推送代码到远程
git push -u origin main
```

### 3.5 日常使用

```bash
# 查看状态
git status

# 添加更改
git add .

# 提交更改
git commit -m "Add: 机器人交互功能"

# 推送更改
git push

# 拉取更改
git pull
```

## 4. 注意事项

1. **Token安全**

   * 不要将token保存在代码中

   * 使用Git凭证管理器存储token

2. **版本控制范围**

   * 只提交源代码和配置文件

   * 排除生成文件和敏感信息

3. **分支管理**

   * 避免直接在main分支上开发

   * 使用功能分支进行开发

4. **提交规范**

   * 提交信息要清晰明了

   * 遵循统一的提交信息格式

## 5. 风险处理

1. **Git冲突**

   * 当多人同时修改同一文件时可能产生冲突

   * 解决方法：手动编辑冲突文件，然后提交

2. **误操作回滚**

   * 如果提交了错误的内容，可以使用`git reset`命令回滚

   * 注意：已推送的更改需要谨慎处理

3. **远程仓库权限**

   * 确保GitHub仓库权限设置正确

   * 定期更新token以确保安全性

## 6. 后续步骤

1. **学习高级Git命令**

   * `git rebase` - 整理提交历史

   * `git stash` - 暂存更改

   * `git cherry-pick` - 选择特定提交

2. **使用Git GUI工具**

   * Git GUI

   * GitHub Desktop

   * VS Code Git集成

3. **建立团队协作流程**

   * 分支策略

   * 代码审查

   * 持续集成

