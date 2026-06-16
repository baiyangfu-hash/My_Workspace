# SYS-2026-001 工作区治理方案

## 1. 设计原则

- 顶层主目录保持稳定，不做推倒重来。
- 工作区级长期事项统一进入 `SYS-2026-001` 管理。
- 根 `.trae/documents/` 只保留临时分析和短期计划。
- 先映射，再归档；先边界，再自动化。

## 2. 目标结构

### 2.1 工作空间主线

- `00_Obsidian_Base全局规范文件仓库`
  - 保留跨技术栈 PM 通用规范
- `0100_PLC自动化`
  - 保留 PLC 规范、共享库、设备项目主线
- `01_Project自动化项目管理`
  - 保留上位机、工具链、软件项目主线
- `SYS-2026-001_WorkspaceGovernance`
  - 新增为整个工作空间的系统级治理入口

### 2.2 根目录辅助入口

- `README.md`
  - 工作空间一级导航
- `.trae/documents/README.md`
  - 根级临时文档职责说明

## 3. 职责边界

### 3.1 `SYS-2026-001_WorkspaceGovernance`

负责:
- 跨主线治理事项
- 根入口治理
- 长期计划收编与节奏控制
- 风险台账与变更准入

不负责:
- 替代具体项目的 PM_SESSION
- 承担具体软件/PLC 需求开发
- 直接维护规范正文内容

### 3.2 `.trae/documents`

负责:
- 一次性分析
- 短期计划
- 草稿型调研

不负责:
- 长期工作区治理的单一真源
- 正式项目级状态管理

## 4. 收编策略

- 第一阶段: 仅建立映射，不移动文件
- 第二阶段: 已完成的长期计划逐步归档
- 第三阶段: 评估是否补充自动化索引或迁移脚本

## 5. 首批映射对象

- `.trae/documents/工作空间重构分阶段治理建议计划.md`
- `.trae/documents/workspace-health-remediation-plan.md`
- `.trae/documents/workspace-temp-files-cleanup-plan.md`
- `.trae/documents/project-rule-optimization-plan.md`

## 6. 验收要点

- 新治理入口建立完成
- 根入口清晰
- 历史长期计划已有明确归口
- 后续新增工作区级事项有准入边界
