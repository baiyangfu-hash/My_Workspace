@echo off
chcp 65001 >nul
title Auto-PM 研发工作台 - 环境初始化向导

echo ==============================================================================
echo        Auto-PM 工业级 AI 研发工作台 - 一键环境初始化向导
echo ==============================================================================
echo.

:: 1. 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python 环境！请先安装 Python 3.11+ 并勾选 "Add Python to PATH"。
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] 正在检测 Python 版本...
python --version

:: 2. 创建虚拟环境
if not exist ".venv" (
    echo [2/4] 正在创建专属虚拟环境 (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [错误] 创建虚拟环境失败，请检查 Python 权限。
        pause
        exit /b 1
    )
) else (
    echo [2/4] 虚拟环境 (.venv) 已存在，跳过创建。
)

:: 3. 激活虚拟环境并安装依赖
echo [3/4] 正在激活虚拟环境并安装核心依赖库...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet

if exist "requirements.txt" (
    echo 正在从 requirements.txt 安装依赖...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

:: 4. 安装 auto-pm 本地开发包（优先工作空间基础设施运行位，旧项目路径回退）
set "CORE_PATH=00_Infrastructure\auto_pm"
set "LEGACY_CORE_PATH=01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具"
if not exist "%CORE_PATH%" (
    set "CORE_PATH=%LEGACY_CORE_PATH%"
)
if exist "%CORE_PATH%" (
    echo [4/4] 正在挂接 auto-pm 核心模块: %CORE_PATH%
    pip install -e "%CORE_PATH%" --no-deps
)

echo.
echo ==============================================================================
echo  [成功] Auto-PM 工作台环境已成功就绪！
echo.
echo  • 启动桌面驾驶舱：双击运行 "双击启动驾驶舱.bat" 或执行 "python main.py"
echo  • 运行全量单测：pytest
echo  • 运行规范体检：python -m auto_pm spec sync
echo ==============================================================================
echo.
pause
