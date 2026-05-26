# Git仓库全新初始化教学计划

## 目标
教会用户如何为一个项目全新初始化Git仓库，删除原有的`.git`文件夹后从零开始。

## 教学案例
以 `SW-2026-004_Python项目管理工具` 项目为案例：
`d:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-004_Python项目管理工具`

## 当前问题
- 该项目可能已有Git仓库（.git文件夹）
- 用户要求全新初始化，需要先删除原有的.git

## 完整步骤计划

### 步骤1：检查并删除原有的.git文件夹
- 进入项目目录
- 检查是否存在 `.git` 文件夹
- 如果存在，删除它（全新初始化）

### 步骤2：初始化新的Git仓库
- 在项目目录执行 `git init`
- 这会创建一个全新的 `.git` 文件夹

### 步骤3：配置Git用户信息（如果还没配置）
- 配置用户名：
  ```
  git config --global user.name "你的名字"
  ```
- 配置邮箱：
  ```
  git config --global user.email "你的邮箱"
  ```

### 步骤4：创建或更新.gitignore文件
- 创建 `.gitignore` 文件（如果还没有）
- 或者检查现有的 `.gitignore` 是否合适
- Python项目常用的忽略项：
  ```
  __pycache__/
  *.pyc
  *.pyo
  .env
  venv/
  .vscode/
  .idea/
  *.log
  ```

### 步骤5：添加所有项目文件
- 执行 `git add .` 添加所有文件
- gitignore中的文件不会被添加

### 步骤6：执行首次提交
- 执行：
  ```
  git commit -m "首次提交：项目初始化"
  ```

### 步骤7：连接远程仓库（可选）
- 添加远程仓库地址：
  ```
  git remote add origin https://github.com/baiyangfu-hash/SW-2026-004-python.git
  ```
- 推送代码：
  ```
  git push -u origin master
  ```

## 教学方式
提供两种方式供用户选择：
1. **PowerShell命令行方式**：一步一步输入命令
2. **VS Code图形界面方式**：在VS Code中点击操作

## 注意事项
- 每一步都要解释为什么要这样做
- 强调 `.gitignore` 的重要性
- 说明首次提交的重要性
- 提供常见问题的解决方法