#!/bin/bash
# ============================================
# Dev Container 创建后自动执行脚本
# 安装项目依赖和配置开发环境
# ============================================

set -e  # 遇到错误立即退出

echo "🚀 开始配置开发环境..."

# ==================== Python 项目依赖安装 ====================
echo "📦 检查并安装Python项目依赖..."

# SW-2026-004_Python项目管理工具
if [ -f "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/requirements.txt" ]; then
    echo "  → 安装 SW-2026-004 依赖..."
    pip install --user -r "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心_code/requirements.txt" || echo "  ⚠️ 部分依赖安装失败（可忽略）"
fi

# SW-2026-001_PLC变量表解析工具
if [ -f "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-001_PLC变量表解析工具/02_开发文件/requirements.txt" ]; then
    echo "  → 安装 SW-2026-001 依赖..."
    pip install --user -r "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-001_PLC变量表解析工具/02_开发文件/requirements.txt" || echo "  ⚠️ 部分依赖安装失败（可忽略）"
fi

# SW-2026-005_PLC项目管理工具
if [ -f "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-005_PLC项目管理工具/03_主程序/01_主程序核心代码/requirements.txt" ]; then
    echo "  → 安装 SW-2026-005 依赖..."
    pip install --user -r "01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-005_PLC项目管理工具/03_主程序/01_主程序核心_code/requirements.txt" || echo "  ⚠️ 部分依赖安装失败（可忽略）"
fi

# ==================== Go 模块依赖下载 ====================
echo "📦 检查并下载Go模块依赖..."

# DJ-2026-005 PLC项目
if [ -f "0100_项目/DJ-2026-005/.plc-out/golang/go.mod" ]; then
    echo "  → 下载 DJ-2026-005 Go模块..."
    cd "0100_项目/DJ-2026-005/.plc-out/golang" && go mod download 2>/dev/null || true
    cd /workspace
fi

# DJ-2026-000 PLC项目
if [ -f "0100_项目/DJ-2026-000/.plc-out/golang/go.mod" ]; then
    echo "  → 下载 DJ-2026-000 Go模块..."
    cd "0100_项目/DJ-2026-000/.plc-out/golang" && go mod download 2>/dev/null || true
    cd /workspace
fi

# 通用ST程序及变量表
if [ -f "0100_项目/DJ-2026-005/02_PLC程序/通用ST程序及变量表/.plc-out/golang/go.mod" ]; then
    echo "  → 下载 通用ST程序 Go模块..."
    cd "0100_项目/DJ-2026-005/02_PLC程序/通用ST程序及变量表/.plc-out/golang" && go mod download 2>/dev/null || true
    cd /workspace
fi

# ==================== Git配置检查 ====================
echo "🔧 检查Git配置..."

if [ ! -f ~/.gitconfig ]; then
    echo "  ⚠️ 未检测到.gitconfig挂载，使用默认配置"
    git config --global user.name "Developer"
    git config --global user.email "developer@example.com"
else
    echo "  ✅ Git配置已从宿主机加载"
fi

# ==================== 环境信息输出 ====================
echo ""
echo "=========================================="
echo "✅ 开发环境配置完成！"
echo "=========================================="
echo ""
echo "📋 环境信息："
echo "  • Python: $(python3 --version 2>/dev/null || python --version)"
echo "  • Go: $(go version)"
echo "  • 工作空间: /workspace"
echo ""
echo "💡 提示："
echo "  • VS Code扩展已自动安装"
echo "  • 项目依赖已预安装"
echo "  • 可以开始开发了！"
echo ""
