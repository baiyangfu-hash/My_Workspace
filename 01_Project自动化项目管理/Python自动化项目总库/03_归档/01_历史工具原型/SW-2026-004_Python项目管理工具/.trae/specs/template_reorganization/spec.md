# 模板管理重组 - 产品需求文档

## Overview
- **Summary**: 重组Python项目管理工具的模板管理系统，只保留整线、单机（机器人和PLC-HMI）、改造升级和上位机这几类模板，并确保模板结构符合参考结构。
- **Purpose**: 简化模板管理，使模板分类更加清晰，符合实际项目需求，提高模板使用的针对性和效率。
- **Target Users**: 项目管理人员、开发人员、系统管理员。

## Goals
- 重组模板管理，只保留5类模板：整线、单机-机器人、单机-PLC-HMI、改造升级、上位机。
- 确保单机模板包含eplan、机械、通讯设计。
- 确保整线模板包含所有内容。
- 确保上位机模板只包含软件Python部分。
- 移除不需要的模板，保持模板管理的简洁性。

## Non-Goals (Out of Scope)
- 不修改模板的基本数据结构。
- 不改变模板的创建和使用流程。
- 不影响现有项目的模板关联。

## Background & Context
- 现有模板管理系统中存在多个模板，分类不够清晰，不利于用户选择。
- 用户希望模板分类更加明确，只保留与实际项目相关的模板类型。
- 参考结构为 `d:\BaiduSyncdisk\My_Workspace\思源笔记导入包重构`，模板结构应基于此参考。

## Functional Requirements
- **FR-1**: 创建整线项目模板，包含所有内容（PLC、HMI、机器人、上位机、eplan、机械、通讯设计）。
- **FR-2**: 创建单机-机器人模板，包含eplan、机械、通讯设计和机器人程序设计。
- **FR-3**: 创建单机-PLC-HMI模板，包含eplan、机械、通讯设计、PLC程序设计和HMI界面设计。
- **FR-4**: 更新改造升级模板，包含现状分析、升级方案、回滚方案。
- **FR-5**: 创建上位机模板，只包含软件Python部分。
- **FR-6**: 移除不需要的模板，只保留上述5类模板。
- **FR-7**: 测试模板功能，确保模板的创建、使用和变更功能正常。

## Non-Functional Requirements
- **NFR-1**: 模板结构必须符合参考结构 `d:\BaiduSyncdisk\My_Workspace\思源笔记导入包重构`。
- **NFR-2**: 模板管理界面应显示重组后的5类模板。
- **NFR-3**: 文档应及时更新，记录模板重组情况。

## Constraints
- **Technical**: 基于现有的模板管理系统，不修改数据库结构。
- **Business**: 保持与现有项目的兼容性，不影响现有项目的模板关联。
- **Dependencies**: 依赖现有的模板DAO和服务层代码。

## Assumptions
- 现有模板管理系统的基本功能正常。
- 模板重组不会影响现有项目的正常运行。
- 参考结构 `d:\BaiduSyncdisk\My_Workspace\思源笔记导入包重构` 是有效的模板结构参考。

## Acceptance Criteria

### AC-1: 整线项目模板创建
- **Given**: 系统中不存在整线项目模板。
- **When**: 执行模板创建脚本。
- **Then**: 系统中应创建一个整线项目模板，包含所有必要的目录结构。
- **Verification**: `programmatic`
- **Notes**: 模板ID为 TPL-FULLLINE-AUTO-001。

### AC-2: 单机-机器人模板创建
- **Given**: 系统中不存在单机-机器人模板。
- **When**: 执行模板创建脚本。
- **Then**: 系统中应创建一个单机-机器人模板，包含eplan、机械、通讯设计。
- **Verification**: `programmatic`
- **Notes**: 模板ID为 TPL-SINGLE-ROBOT-001。

### AC-3: 单机-PLC-HMI模板创建
- **Given**: 系统中不存在单机-PLC-HMI模板。
- **When**: 执行模板创建脚本。
- **Then**: 系统中应创建一个单机-PLC-HMI模板，包含eplan、机械、通讯设计。
- **Verification**: `programmatic`
- **Notes**: 模板ID为 TPL-SINGLE-PLC-001。

### AC-4: 改造升级模板更新
- **Given**: 系统中存在改造升级模板。
- **When**: 执行模板创建脚本。
- **Then**: 系统中的改造升级模板应被更新，包含现状分析、升级方案、回滚方案。
- **Verification**: `programmatic`
- **Notes**: 模板ID为 TPL-UPGRADE-STD-001。

### AC-5: 上位机模板创建
- **Given**: 系统中不存在上位机模板。
- **When**: 执行模板创建脚本。
- **Then**: 系统中应创建一个上位机模板，只包含软件Python部分。
- **Verification**: `programmatic`
- **Notes**: 模板ID为 TPL-UPPER-STD-001。

### AC-6: 不需要的模板移除
- **Given**: 系统中存在不需要的模板。
- **When**: 执行模板清理脚本。
- **Then**: 系统中只保留5类模板，其他模板应被移除。
- **Verification**: `programmatic`
- **Notes**: 保留的模板ID为 TPL-FULLLINE-AUTO-001、TPL-SINGLE-ROBOT-001、TPL-SINGLE-PLC-001、TPL-UPGRADE-STD-001、TPL-UPPER-STD-001。

### AC-7: 模板功能测试
- **Given**: 系统中已创建5类模板。
- **When**: 执行模板功能测试脚本。
- **Then**: 所有模板的创建、使用和变更功能应正常工作。
- **Verification**: `programmatic`
- **Notes**: 测试应覆盖模板列表、模板创建、模板变更等功能。

### AC-8: 文档更新
- **Given**: 模板重组完成。
- **When**: 更新用户操作手册。
- **Then**: 用户操作手册应记录模板重组情况，包含当前模板列表和使用说明。
- **Verification**: `human-judgment`
- **Notes**: 文档版本应更新为 V1.0.5。

## Open Questions
- [ ] 如何处理内置模板的移除？
- [ ] 如何确保模板重组不影响现有项目的模板关联？