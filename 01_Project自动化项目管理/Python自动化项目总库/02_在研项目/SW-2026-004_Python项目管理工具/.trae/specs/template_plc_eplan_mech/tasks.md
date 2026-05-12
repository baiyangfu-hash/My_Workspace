# Tasks: 单机设备模板补充Eplan+机械3D目录

## Task 1: 修改 constants.py 中 TPL-SINGLE-PLC-001 的 structure
- [x] 1.1 将 `01_需求与设计` 从扁平项改为含子目录的结构
- [x] 1.2 新增 `01_需求与设计/11_Eplan电气/Export_PDF`
- [x] 1.3 新增 `01_需求与设计/11_Eplan电气/Source`
- [x] 1.4 新增 `01_需求与设计/12_机械结构/3D_Models`
- [x] 1.5 新增 `01_需求与设计/12_机械结构/2D_Drawings`
- [x] 1.6 新增 `01_需求与设计/13_软件方案` (原有内容归入此子目录)
- [x] 1.7 确保一级目录仍为00~07共8个（不破坏编号规则）

## Task 2: 更新 TPL-SINGLE-PLC-001 的 templates 字段
- [x] 2.1 新增 Eplan检查清单模板文件定义
- [x] 2.2 新增 机械BOM模板文件定义
- [x] 2.3 新增 IO分配表模板文件定义（移入13_软件方案）
- [x] 2.4 调整现有模板文件的路径（归入13_软件方案子目录）

## Task 3: 更新 template_editor.py 占位符文本 (如需要)
- [x] 3.1 检查是否有硬编码的占位符文本需要更新
- [x] 3.2 占位符文本为通用型，无需修改

## Task 4: 自测验证
- [x] 4.1 调用 initialize_builtin_templates() 确认DB更新成功
- [x] 4.2 用 TPL-SINGLE-PLC-001 创建测试项目
- [x] 4.3 验证生成的目录包含 11_Eplan电气 和 12_机械结构 子目录
- [x] 4.4 验证一级目录仍为8个(00~07)
- [x] 4.5 验证总物理目录数约14个 (实际11项检查全部PASS)

## Task 5: 重新编译+打包V2.4.4
- [x] 5.1 更新 version.py → V2.4.4
- [x] 5.2 PyInstaller重新编译exe (58.38MB)
- [x] 5.3 使用 build_delivery.py 打包交付物 (951 files, 160.14MB, 🟢7/7 CHK)
