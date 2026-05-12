@echo off

echo 开始运行自动化测试...
echo ====================

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    echo 请确保Python已安装并添加到系统PATH中
    pause
    exit /b 1
)

REM 运行自动化测试
echo 运行自动化测试脚本...
python auto_test_all.py

REM 检查测试结果
if %errorlevel% equ 0 (
    echo 测试完成！
) else (
    echo 测试过程中出现错误
)

echo ====================
echo 测试执行完毕
pause