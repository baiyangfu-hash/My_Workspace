@echo off

rem 项目配置
set PROJECT_NAME=Python项目管理工具
set VERSION=1.0.0
set DELIVERY_DIR=19_交付物
set OUTPUT_ZIP=%PROJECT_NAME%_%VERSION%_交付物.zip

rem 创建交付目录结构
echo 创建交付目录结构...
mkdir %DELIVERY_DIR%\01_可执行文件 2>nul
mkdir %DELIVERY_DIR%\02_配置文件 2>nul
mkdir %DELIVERY_DIR%\03_测试文件 2>nul
mkdir %DELIVERY_DIR%\03_测试文件\test_reports 2>nul
mkdir %DELIVERY_DIR%\04_文档 2>nul
mkdir %DELIVERY_DIR%\04_文档\04_技术文档 2>nul
mkdir %DELIVERY_DIR%\05_数据库 2>nul

echo 复制可执行文件...
copy "03_主程序\01_主程序核心代码\build\Python项目管理工具\Python项目管理工具.exe" "%DELIVERY_DIR%\01_可执行文件\" 2>nul

echo 复制配置文件...
copy "03_主程序\01_主程序核心代码\config\*" "%DELIVERY_DIR%\02_配置文件\" 2>nul

echo 复制测试文件...
copy "03_主程序\01_主程序核心代码\run_full_test_suite.py" "%DELIVERY_DIR%\03_测试文件\" 2>nul

echo 复制文档...
copy "06_交付文档\自动化测试使用说明.md" "%DELIVERY_DIR%\04_文档\01_用户手册.md" 2>nul

echo 复制技术文档...
copy "07_技术知识库\01_架构设计\系统架构概述.md" "%DELIVERY_DIR%\04_文档\04_技术文档\" 2>nul
copy "07_技术知识库\01_架构设计\模块设计说明.md" "%DELIVERY_DIR%\04_文档\04_技术文档\" 2>nul
copy "07_技术知识库\02_API文档\服务层API.md" "%DELIVERY_DIR%\04_文档\04_技术文档\" 2>nul
copy "07_技术知识库\03_数据库设计\数据库设计文档.md" "%DELIVERY_DIR%\04_文档\04_技术文档\" 2>nul

echo 复制数据库文件...
copy "03_主程序\01_主程序核心代码\data\project_manager.db" "%DELIVERY_DIR%\05_数据库\" 2>nul

echo 复制交付清单...
copy "%DELIVERY_DIR%\交付清单.md" "%DELIVERY_DIR%\06_交付清单.md" 2>nul

echo 打包交付物...
powershell Compress-Archive -Path %DELIVERY_DIR% -DestinationPath %OUTPUT_ZIP% -Force

echo 清理临时文件...
rd /s /q %DELIVERY_DIR% 2>nul

echo 交付物打包完成！
echo 输出文件：%OUTPUT_ZIP%
echo.
pause