# 项目通用规范整合 Spec

## Why

在 DJ-2026-005 项目开发过程中, AI 助手反复犯下以下错误:

1. **定时器类型混淆**: 将自定义 `FB_TON`(DINT 类型 PT/ET) 与标准 Siemens `TON`(TIME 类型) 混淆, 导致 `PT := T#0ms`(TIME 字面量) 赋给 DINT 参数
2. **定时器 Q 参数省略**: 使用 `Q => ,` 空参数语法, 违反了 905 规范"定时器调用必须包含所有参数"的要求
3. **库路径未配置**: `.plc.json` 缺少 `libraryDirectories` 配置, 导致 LSP 无法找到 `FB_TON` 定义
4. **METHOD 命名不规范**: 使用 `CALL_AutoModeStateMachine` 而非规范的 `AutoModeStateMachine`
5. **盲目修改自动生成文件**: 修改 `.plc-out/golang/builtins/` 下的 Go 文件, 而非从 SCL 源码层面解决问题

**根本原因**: 全局规范文件散落在 `00_Obsidian_Base全局规范文件仓库`, 项目开发时无法快速查阅, 且缺少基于实战经验的"错误预防规则"。

## What Changes

- 在 `d:\BaiduSyncdisk\My_Workspace\0100_项目` 下创建 `00_通用规范` 目录
- 将全局规范仓库中与 PLC 编程和项目管理直接相关的规范整合到项目级目录
- 基于实战错误新增"错误预防规则"文档
- 整合后的规范保留原文档的版本号和溯源信息, 不修改原始全局规范

### 整合来源

| 源文件(全局规范仓库) | 目标位置(项目级) | 说明 |
|---|---|---|
| `903_Siemens-LSP_Go-Gen_定时器使用规范_DEV-V1.0.0.md` | `00_通用规范/PLC编程/903_定时器使用规范.md` | 核心规范: FB_TON 使用规则 |
| `904_SCL注释规范_Siemens-LSP兼容版_DEV-V1.0.0.md` | `00_通用规范/PLC编程/904_SCL注释规范.md` | 注释格式规范 |
| `905_SCL编程规范_Siemens-LSP兼容版_DEV-V1.0.0.md` | `00_通用规范/PLC编程/905_SCL编程规范.md` | 编程语法规范 |
| `902_Git使用指南_DEV-V1.0.0.md` | `00_通用规范/项目管理/902_Git使用指南.md` | Git 工作流规范 |
| (新增) | `00_通用规范/PLC编程/906_错误预防规则.md` | 基于实战错误总结的预防规则 |
| (新增) | `00_通用规范/PLC编程/907_项目配置规范.md` | .plc.json 配置规范 |
| (新增) | `00_通用规范/README.md` | 规范索引和使用说明 |

### **BREAKING** 变更

无破坏性变更。本任务仅创建新文件, 不修改任何现有文件。

## Impact

- Affected specs: 无(纯新增)
- Affected code: 无(规范文档, 不涉及代码修改)
- 后续影响: 所有 PLC 项目开发应优先参考 `00_通用规范` 目录

## ADDED Requirements

### Requirement: 项目级规范整合

系统 SHALL 在 `d:\BaiduSyncdisk\My_Workspace\0100_项目\00_通用规范` 下提供完整的项目级规范库, 包含以下内容:

#### Scenario: PLC 编程规范可查阅
- **WHEN** 开发者需要查看定时器使用规则
- **THEN** 可在 `00_通用规范/PLC编程/903_定时器使用规范.md` 找到完整规范
- **AND** 规范中明确说明 FB_TON 的 PT/ET 参数为 DINT 类型(扫描周期数), 不是 TIME 类型
- **AND** 规范中明确说明定时器调用必须包含所有参数(IN/PT/Q/ET), Q 不能省略

#### Scenario: 错误预防规则可查阅
- **WHEN** AI 助手或开发者准备修改 PLC 代码
- **THEN** 可在 `00_通用规范/PLC编程/906_错误预防规则.md` 找到基于实战的错误预防清单
- **AND** 规范中包含"禁止修改 .plc-out 自动生成文件"等关键规则

#### Scenario: 项目配置规范可查阅
- **WHEN** 创建新 PLC 项目或配置现有项目
- **THEN** 可在 `00_通用规范/PLC编程/907_项目配置规范.md` 找到 .plc.json 配置规范
- **AND** 规范中明确说明 libraryDirectories 的配置方法

### Requirement: 错误预防规则文档

系统 SHALL 提供基于 DJ-2026-005 项目实战经验的错误预防规则文档, 包含以下核心规则:

#### Scenario: 定时器类型正确使用
- **WHEN** 开发者使用 FB_TON 定时器
- **THEN** PT 参数使用 DINT 类型(扫描周期数), 不使用 TIME 类型字面量(如 T#0ms, T#500ms)
- **AND** ET 输出变量声明为 DINT 类型, 不声明为 TIME 类型
- **AND** Q 参数必须指定接收变量, 不使用 `Q => ,` 空参数语法
- **AND** 复位定时器时使用 `PT := 0`(DINT 零值), 不使用 `PT := T#0ms`(TIME 字面量)

#### Scenario: 不修改自动生成文件
- **WHEN** 测试失败或运行时错误出现在 `.plc-out/` 目录下的 Go 文件中
- **THEN** 开发者 SHALL NOT 直接修改这些文件
- **AND** 应从 SCL 源码层面解决问题, 或检查项目配置

#### Scenario: 项目配置完整性
- **WHEN** 创建新 PLC 项目
- **THEN** .plc.json 必须包含 libraryDirectories 配置
- **AND** libraryDirectories 指向 SysLib 共享库的相对路径

### Requirement: 规范索引文档

系统 SHALL 提供 `00_通用规范/README.md` 索引文件, 包含:
- 所有规范的文件列表和简要说明
- 规范之间的引用关系
- 快速查找指南(按场景查找对应规范)

## MODIFIED Requirements

无修改需求。本任务仅新增文档。

## REMOVED Requirements

无删除需求。
