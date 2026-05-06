# 多项目隔离与库共享配置分析 Spec

## Why
用户重新整理了 `0100_项目` 目录结构，需要验证：
1. 两个 PLC 项目（DJ-2026-000 和 DJ-2026-005）是否通过 `.plc.json` 实现正确的类型作用域隔离
2. 共享库 `01_SharedLibraries/SysLib` 是否被正确引用
3. 两个项目是否完全适配 Siemens LSP 插件的要求

## What Changes
- **分析现有项目结构和配置**
- **识别配置问题和潜在冲突**
- **提供修复建议和验证方案**

## Impact
- Affected specs: 无（这是新的分析任务）
- Affected code:
  - `DJ-2026-000/.plc.json`
  - `DJ-2026-005/.plc.json`
  - `DJ-2026-000/OB1/OB1.scl`
  - `DJ-2026-000/DB1/GlobalVars.db`
  - `01_SharedLibraries/SysLib/*`

## ADDED Requirements

### Requirement: 项目隔离性验证
系统 SHALL 确保每个 PLC 项目具有独立的类型作用域，符合 Siemens LSP 插件的 `.plc.json` 隔离机制。

#### Scenario: 独立编译输出
- **WHEN** 两个项目位于不同的目录且各自拥有 `.plc.json` 文件
- **THEN** 每个项目应生成独立的 `.plc-out/golang` 编译输出目录
- **THEN** 编译输出中的路径应指向各自的项目根目录
- **THEN** 一个项目的类型定义不应泄漏到另一个项目

#### Scenario: 类型作用域隔离
- **WHEN** DJ-2026-000 定义了 `FB_ValveControl` 功能块
- **WHEN** DJ-2026-005 定义了相同名称的功能块
- **THEN** 两个功能块应在各自的项目作用域内独立存在
- **THEN** 不应发生类型冲突或命名空间污染

### Requirement: 共享库引用验证
系统 SHALL 允许多个项目通过 `.plc.json` 的 `libraries` 字段引用同一共享库。

#### Scenario: 库路径解析
- **WHEN** DJ-2026-005 的 `.plc.json` 配置 `"libraries": ["../01_SharedLibraries/SysLib"]`
- **THEN** 路径应相对于 `.plc.json` 文件所在目录解析
- **THEN** 解析后的绝对路径应为 `d:\BaiduSyncdisk\My_Workspace\0100_项目\01_SharedLibraries\SysLib`
- **THEN** 库中的所有 SCL 文件（FB_TON, FB_CTD 等）应可被项目代码引用

#### Scenario: 库内容可见性
- **WHEN** 项目正确配置了库引用
- **THEN** 库中的功能块（timer, counter, edge, convert, log, pulse）应在代码补全中可见
- **THEN** 库类型应参与类型检查和诊断
- **THEN** 修改库文件后应触发项目重新扫描

### Requirement: 插件适配性验证
系统 SHALL 确保所有项目文件符合 Siemens LSP Go 后端的语法和类型要求。

#### Scenario: 功能块定义完整性
- **WHEN** OB1.scl 中调用了 `FB_ValveControl` 功能块
- **THEN** 项目中必须存在 `FB_ValveControl` 的 SCL 定义文件
- **THEN** 或者该功能块必须在 `libraries` 引用的库中定义
- **否则** LSP 将生成 builtin stub 导致运行时错误

#### Scenario: 配置文件格式合规
- **WHEN** `.plc.json` 文件存在于项目根目录
- **THEN** 必须包含有效的 `name` 字段（非空字符串）
- **THEN** `name` 字段值应与项目功能一致
- **THEN** `libraries` 数组中的路径必须存在且可访问

## MODIFIED Requirements
无（这是全新的分析任务）

## REMOVED Requirements
无
