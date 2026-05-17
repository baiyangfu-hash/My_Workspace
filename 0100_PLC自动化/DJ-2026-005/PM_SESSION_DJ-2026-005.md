# PM_SESSION_DJ-2026-005

## 0. Meta
- project_id: DJ-2026-005
- project_name: 边框缓存机
- project_root: c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\DJ-2026-005
- last_updated: 2026-05-17
- owners: 待补充

## 1. Positioning（项目定位）
- one_liner: 边框缓存机 PLC/HMI 软件工程交付与维护
- users: 设备调试/维护工程师；产线操作人员
- non_goals: 待补充

## 2. Current Focus（当前焦点）
- current_focus: 编译器导出 PDF 的 MCP 解析与一致性检查
- milestone: 待补充
- acceptance: PDF 解析结果落盘；与现有提取文本/工程文件的差异清单输出

## 3. Status Summary（当前状态摘要）
- in_progress:
  - PDF（编译器导出）准备完成，待 MCP 解析与对比
- next_up:
  - 解析 PDF 并落盘为可比对文本
  - 对比 .trae/specs/source-program-audit/pdf_extracted 的已有提取结果
  - 抽样核对 ST/FB 源文件与 PDF 内容的一致性
- open_questions:
  - “匹配”判定口径：需要全文一致/关键字段一致/抽样一致？
- risks_dependencies:
  - OCR/版面解析导致文本差异（空格、换行、字符误识别），需定义容忍规则
  - PaddlePaddle 3.3.x 在 Windows/CPU 的 PP-StructureV3 推理可能触发 ConvertPirAttribute2RuntimeAttribute 异常，需要固定 paddlepaddle==3.2.2

## 4. Artifacts Index（文档索引）
- prd:
  - 01_需求与设计\13_软件方案\012_DJ-2026-005_需求规格说明书_REQ-V2.0.0.md
- req:
  - 00_项目管理\01_立项与需求\005_DJ-2026-005_需求分析文档_REQ-V2.0.0.md
- des:
  - 02_PLC程序\程序文档\016_DJ-2026-005_PLC程序设计总文档_PLC-V2.0.0.md
  - 02_PLC程序\程序文档\程序架构文档_ARC-DJ-2026-005-V4.2.0.md
  - 02_PLC程序\程序文档\详细设计说明书_DSN-DJ-2026-005-V4.2.0.md
- test:
  - 05_测试与验证\测试报告\Eplan电路整改报告.md
  - 05_测试与验证\整改方案_DJ-2026-005_梯形图对照通用ST一致性整改_V1.0.0.md
- change_mgmt:
  - 00_项目管理\04_变更管理\04_变更记录\01_版本变更台帐.md
- delivery:
  - 06_文档与交付\验收交付清单\验收交付清单.md

## 5. Logs（按事件沉淀）
- iteration_log:
  - 2026-05-17 PDF MCP解析与一致性检查 进行中
  - 2026-05-17 排查：pp_structurev3 调用失败定位为 paddlepaddle 3.3.1 推理异常；建议固定 paddlepaddle==3.2.2
  - 2026-05-17 输出梯形图对照通用ST一致性整改方案V1.0.0（含风险点、任务拆解、测试用例建议）
  - 2026-05-17 决策：取消CC-Link对齐；不要求地址对齐；最终交付以OB1/DB/FB为主；轴控以可移植的抽象接口/占位符对齐
