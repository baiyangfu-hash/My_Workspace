# Checklist: 单机设备模板补充Eplan+机械3D目录

## Task 1: constants.py structure修改
- [x] TPL-SINGLE-PLC-001 的 structure 字段已更新
- [x] 01_需求与设计 下含 11_Eplan电气/Export_PDF
- [x] 01_需求与设计 下含 11_Eplan电气/Source
- [x] 01_需求与设计 下含 12_机械结构/3D_Models
- [x] 01_需求与设计 下含 12_机械结构/2D_Drawings
- [x] 01_需求与设计 下含 13_软件方案
- [x] 一级目录仍为8个(00~07)，无新增一级目录

## Task 2: templates字段更新
- [x] 新增Eplan检查清单模板定义 (Eplan检查清单.md)
- [x] 新增机械BOM模板定义 (BOM模板.md)
- [x] 新增IO分配表模板定义 (归入13_软件方案)
- [x] 原有需求类文档路径已归入13_软件方案/ (3个文档)

## Task 3: template_editor.py (如需)
- [x] 占位符文本为通用型，无需修改

## Task 4: 自测验证
- [x] initialize_builtin_templates() 执行无报错
- [x] DB中 TPL-SINGLE-PLC-001 版本更新为 V2.1.0
- [x] 测试项目创建成功
- [x] 测试项目包含 `01_需求与设计/11_Eplan电气/` 目录
- [x] 测试项目包含 `01_需求与设计/12_机械结构/` 目录
- [x] 测试项目一级目录数为8 (00~07)
- [x] 总物理目录数 >= 13 (实际14个)

## Task 5: 打包交付
- [x] version.py 已更新至 V2.4.4
- [x] exe 已重新编译 (58.38MB)
- [x] build_delivery.py 执行结果 🟢 7/7 CHK PASS (951 files, 160.14MB)
