@echo off
chcp 65001 >nul
title Auto-PM 工业级桌面驾驶舱

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\python.exe" main.py
) else (
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [提示] 检测到尚未初始化环境，请先双击运行 "setup_env.bat" 进行一键配置。
        pause
        exit /b 1
    )
    start "" python main.py
)
