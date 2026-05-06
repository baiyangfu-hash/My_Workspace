#!/bin/bash
# ============================================
# Dev Container 创建后自动执行脚本
# 安装项目依赖和配置开发环境
# 版本: V1.1.0 (2026-05-06 修复版)
# ============================================

set -e  # 遇到错误立即退出

echo "🚀 开始配置开发环境..."

# ==================== Python 项目依赖安装 ====================
echo "📦 检查并安装Python项目依赖..."

# SW-2026-004_Python项目管理工具
if [ -f "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/requirements.txt" ]; then
    echo "  → 安装 SW-2026-004 依赖..."
    pip install --user -r "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/requirements.txt" || echo "  ⚠️ SW-2026-004 部分依赖安装失败（可手动执行 pip install）"
fi

# SW-2026-001_PLC变量表解析工具
if [ -f "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-001_PLC变量表解析工具/02_开发文件/requirements.txt" ]; then
    echo "  → 安装 SW-2026-001 依赖..."
    pip install --user -r "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-001_PLC变量表解析工具/02_开发文件/requirements.txt" || echo "  ⚠️ SW-2026-001 部分依赖安装失败（可手动执行 pip install）"
fi

# SW-2026-005_PLC项目管理工具
if [ -f "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-005_PLC项目管理工具/03_主程序/01_主程序核心代码/requirements.txt" ]; then
    echo "  → 安装 SW-2026-005 依赖..."
    pip install --user -r "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-005_PLC项目管理工具/03_主程序/01_主程序核心代码/requirements.txt" || echo "  ⚠️ SW-2026-005 部分依赖安装失败（可手动执行 pip install）"
fi

# ==================== Go 模块依赖下载 ====================
echo "📦 检查并下载Go模块依赖..."

# DJ-2026-005 PLC项目 (主程序 .plc-out)
if [ -f "0100_PLC自动化/DJ-2026-005/.plc-out/golang/go.mod" ]; then
    echo "  → 下载 DJ-2026-005 Go模块 (.plc-out)..."
    cd "0100_PLC自动化/DJ-2026-005/.plc-out/golang" && go mod download 2>/dev/null && echo "  ✅ DJ-2026-005 Go模块下载完成" || echo "  ⚠️ DJ-2026-005 Go模块下载失败（可手动执行 go mod download）"
    cd /workspace
fi

# DJ-2026-000 PLC项目
if [ -f "0100_PLC自动化/DJ-2026-000/.plc-out/golang/go.mod" ]; then
    echo "  → 下载 DJ-2026-000 Go模块..."
    cd "0100_PLC自动化/DJ-2026-000/.plc-out/golang" && go mod download 2>/dev/null && echo "  ✅ DJ-2026-000 Go模块下载完成" || echo "  ⚠️ DJ-2026-000 Go模块下载失败（可手动执行 go mod download）"
    cd /workspace
fi

# DJ-2026-005 PLC项目 (通用ST程序及变量表)
if [ -f "0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/.plc-out/golang/go.mod" ]; then
    echo "  → 下载 DJ-2026-005 通用ST程序 Go模块..."
    cd "0100_PLC自动化/DJ-2026-005/02_PLC程序/通用ST程序及变量表/.plc-out/golang" && go mod download 2>/dev/null && echo "  ✅ 通用ST程序Go模块下载完成" || echo "  ⚠️ 通用ST程序Go模块下载失败（可手动执行 go mod download）"
    cd /workspace
fi

# ==================== Git配置检查 ====================
echo "🔧 检查Git配置..."

if [ ! -f ~/.gitconfig ]; then
    echo "  ⚠️ 未检测到.gitconfig挂载，使用默认配置"
    git config --global user.name "Developer"
    git config --global user.email "developer@example.com"
    echo "  💡 提示: 请在容器外执行 git config --global 修改为你的信息，或挂载 ~/.gitconfig"
else
    echo "  ✅ Git配置已从宿主机加载"
    echo "  • 用户名: $(git config --global user.name)"
    echo "  • 邮箱: $(git config --global user.email)"
fi

# ==================== 环境验证 ====================
echo ""
echo "=========================================="
echo "✅ 开发环境配置完成！"
echo "=========================================="
echo ""
echo "📋 环境信息："
echo "  • Python: $(python3 --version 2>/dev/null || python --version)"
echo "  • Go: $(go version | awk '{print $3}')"
echo "  • 工作空间: /workspace"
echo "  • 容器用户: $(whoami)"
echo ""
echo "📁 已识别的项目目录："
[ -d "0100_PLC自动化" ] && echo "  ✅ 0100_PLC自动化/ (PLC项目)"
[ -d "01_Project自动化项目管理" ] && echo "  ✅ 01_Project自动化项目管理/ (Python项目)"
[ -d "00_Obsidian_Base全局规范文件仓库" ] && echo "  ✅ 00_Obsidian_Base全局规范文件仓库/ (规范文档)"
echo ""
echo "💡 下一步操作："
echo "  1. VS Code扩展已自动安装"
echo "  2. 项目依赖已预安装（如有失败请查看上方警告）"
echo "  3. 可以开始开发了！"
echo ""
echo "📖 详细指南: 查看 README_DOCKER.md"
echo ""
