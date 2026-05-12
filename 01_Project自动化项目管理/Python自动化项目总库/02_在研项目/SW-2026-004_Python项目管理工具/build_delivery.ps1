# 项目配置
$ProjectName = "Python项目管理工具"
$Version = "1.0.3"
$DeliveryDir = "19_交付物"
$OutputZip = "${ProjectName}_${Version}_交付物.zip"

# 创建交付目录结构
Write-Host "创建交付目录结构..."
New-Item -Path "$DeliveryDir\01_可执行文件" -ItemType Directory -Force | Out-Null
New-Item -Path "$DeliveryDir\02_配置文件" -ItemType Directory -Force | Out-Null
New-Item -Path "$DeliveryDir\03_测试文件" -ItemType Directory -Force | Out-Null
New-Item -Path "$DeliveryDir\03_测试文件\test_reports" -ItemType Directory -Force | Out-Null
New-Item -Path "$DeliveryDir\04_文档" -ItemType Directory -Force | Out-Null
New-Item -Path "$DeliveryDir\04_文档\04_技术文档" -ItemType Directory -Force | Out-Null
New-Item -Path "$DeliveryDir\05_数据库" -ItemType Directory -Force | Out-Null

# 复制可执行文件
Write-Host "复制可执行文件..."
Copy-Item -Path "03_主程序\01_主程序核心代码\build\Python项目管理工具\Python项目管理工具.exe" -Destination "$DeliveryDir\01_可执行文件\" -Force -ErrorAction SilentlyContinue

# 复制配置文件
Write-Host "复制配置文件..."
Copy-Item -Path "03_主程序\01_主程序核心代码\config\*" -Destination "$DeliveryDir\02_配置文件\" -Force -ErrorAction SilentlyContinue

# 复制测试文件
Write-Host "复制测试文件..."
Copy-Item -Path "03_主程序\01_主程序核心代码\run_full_test_suite.py" -Destination "$DeliveryDir\03_测试文件\" -Force -ErrorAction SilentlyContinue

# 复制文档
Write-Host "复制文档..."
Copy-Item -Path "06_交付文档\自动化测试使用说明.md" -Destination "$DeliveryDir\04_文档\01_用户手册.md" -Force -ErrorAction SilentlyContinue

# 复制技术文档
Write-Host "复制技术文档..."
Copy-Item -Path "07_技术知识库\01_架构设计\系统架构概述.md" -Destination "$DeliveryDir\04_文档\04_技术文档\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path "07_技术知识库\01_架构设计\模块设计说明.md" -Destination "$DeliveryDir\04_文档\04_技术文档\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path "07_技术知识库\02_API文档\服务层API.md" -Destination "$DeliveryDir\04_文档\04_技术文档\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path "07_技术知识库\03_数据库设计\数据库设计文档.md" -Destination "$DeliveryDir\04_文档\04_技术文档\" -Force -ErrorAction SilentlyContinue

# 复制数据库文件
Write-Host "复制数据库文件..."
Copy-Item -Path "03_主程序\01_主程序核心代码\data\project_manager.db" -Destination "$DeliveryDir\05_数据库\" -Force -ErrorAction SilentlyContinue

# 复制交付清单
Write-Host "复制交付清单..."
Copy-Item -Path "06_交付物\交付清单.md" -Destination "$DeliveryDir\06_交付清单.md" -Force -ErrorAction SilentlyContinue

# 打包交付物
Write-Host "打包交付物..."
Compress-Archive -Path $DeliveryDir -DestinationPath $OutputZip -Force -ErrorAction SilentlyContinue

# 清理临时文件
Write-Host "清理临时文件..."
Remove-Item -Path $DeliveryDir -Recurse -Force -ErrorAction SilentlyContinue

# 完成
Write-Host "交付物打包完成！"
Write-Host "输出文件：$OutputZip"
Read-Host "按任意键继续..."