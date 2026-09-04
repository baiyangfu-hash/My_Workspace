# V2.5.2 模板管理与总库管理全面修复 Spec

## Why
用户反馈 V2.5.1 的修复不仅没有解决问题，反而导致问题更严重。需要全面检查和修复：
1. 模板管理模块的默认模板定义是否与参考规范一致
2. 总库管理模块的项目数统计功能是否正常
3. 使用模板新建项目时是否能正确生成变更管理目录结构
4. 模板管理模块本身的 UI 和功能是否正常

## What Changes
- **全面诊断**：检查模板管理模块和总库管理模块的所有代码
- **模板对齐**：确保默认模板定义与 `06_项目模板规范` 完全一致
- **功能修复**：修复所有发现的问题，包括但不限于：
  - 项目数显示异常
  - 模板定义错误或缺失
  - 变更管理目录结构不正确
  - UI 功能异常
- **全面测试**：使用每种模板类型新建测试项目，验证生成的目录结构

## Impact
- Affected specs: 
  - `06_项目模板规范` 中的所有模板定义
  - 变更管理与模板文件映射文档
- Affected code:
  - `src/core/constants.py` - 模板定义
  - `src/dao/project_dao.py` - 项目数据访问
  - `src/services/project_service.py` - 项目服务
  - `src/ui/widgets/template_manager.py` - 模板管理 UI
  - `src/ui/widgets/library_manager.py` - 总库管理 UI
  - `Python项目管理工具.spec` - 打包配置

## ADDED Requirements

### Requirement: 模板定义与规范完全一致
系统 SHALL 确保所有内置模板的定义与 `06_项目模板规范` 中的规范完全一致，包括：
1. 目录结构（structure）
2. 文件模板（templates）
3. 变更管理目录结构（00_项目管理/04_变更管理/）

#### Scenario: 模板包含正确的变更管理目录
- **WHEN** 用户使用任何内置模板创建新项目
- **THEN** 生成的项目必须包含以下变更管理目录结构：
  ```
  00_项目管理/
  └── 04_变更管理/
      ├── 01_变更单/           # 存放变更单文件
      ├── 03_变更管理规范/     # (可选) 变更管理流程规范
      └── 04_变更记录/         # 版本变更台帐
  ```

#### Scenario: 模板文件内容正确
- **WHEN** 用户使用模板创建项目
- **THEN** 生成的文件必须包含正确的内容，特别是：
  - 变更单模板（040_{code}_变更单{序号}_CHG-V2.0.0.md）
  - 变更台帐模板（041_{code}_版本变更台帐_CHG-V2.1.0.md）
  - 变更管理流程规范（042_{code}_变更管理流程规范_PM-V2.0.0.md）

### Requirement: 总库管理模块项目数统计准确
系统 SHALL 正确统计并显示总库中的项目数量。

#### Scenario: 显示正确的项目总数
- **WHEN** 用户打开总库管理模块
- **THEN** 系统必须显示正确的项目总数（当有项目存在时，应大于 0）

#### Scenario: 按状态统计项目数
- **WHEN** 用户查看不同状态的项目统计
- **THEN** 各状态的项目数必须与实际数据库中的数据一致

### Requirement: 模板管理模块功能正常
系统 SHALL 提供完整的模板管理功能。

#### Scenario: 显示所有内置模板
- **WHEN** 用户打开模板管理模块
- **THEN** 系统必须显示所有内置模板（至少 6 种）：
  - TPL-FULLLINE-AUTO-001 (自动化整线)
  - TPL-SINGLE-PLC-S001 (小型单机设备)
  - TPL-SINGLE-PLC-M001 (中大型单机设备)
  - TPL-SINGLE-ROBOT-001 (单机机器人)
  - TPL-UPGRADE-STD-001 (系统升级)
  - TPL-UPPER-STD-001 (上位机/数据系统)

#### Scenario: 使用模板创建项目成功
- **WHEN** 用户选择任意模板并创建项目
- **THEN** 项目必须成功创建，且目录结构与模板定义一致

## MODIFIED Requirements

### Requirement: 项目服务层正确初始化变更管理
修改后的项目服务 SHALL 在创建项目时正确初始化变更管理目录和文件。

#### Scenario: 创建项目时自动生成变更管理文件
- **WHEN** 使用模板创建新项目
- **THEN** 系统自动在 `00_项目管理/04_变更管理/` 目录下生成：
  - `.gitkeep` 文件（用于保持空目录）
  - `README.md`（变更管理使用说明）
  - `042_{project_code}_变更管理流程规范_PM-V2.0.0.md`（可选）
  - `041_{project_code}_版本变更台帐_CHG-V2.1.0.md`

## REMOVED Requirements
无

## 验证标准

### AC-1: 模板定义验证
- **Given**: 系统已加载所有内置模板
- **When**: 检查每个模板的 structure 和 templates 字段
- **Then**: 所有模板都必须包含完整的变更管理目录结构
- **Verification**: `programmatic`

### AC-2: 项目创建验证
- **Given**: 用户选择任意内置模板
- **When**: 创建新项目
- **Then**: 生成的项目目录必须包含正确的变更管理子目录和文件
- **Verification**: `programmatic` + `human-judgment`

### AC-3: 总库统计验证
- **Given**: 数据库中存在 N 个项目
- **When**: 打开总库管理模块
- **Then**: 显示的项目数必须等于 N
- **Verification**: `programmatic`

### AC-4: 跨模板测试验证
- **Given**: 系统支持多种模板类型
- **When**: 使用每种模板类型分别创建测试项目
- **Then**: 所有项目都能正确创建，且目录结构符合对应模板规范
- **Verification**: `human-judgment`

## Open Questions
- [ ] 当前 constants.py 中是否有语法错误或逻辑错误？
- [ ] 模板管理 UI 是否能正确显示和操作所有模板？
- [ ] 总库管理 UI 的统计数据来源是否正确？
- [ ] PyInstaller 打包配置是否包含了所有必要的模板文件？