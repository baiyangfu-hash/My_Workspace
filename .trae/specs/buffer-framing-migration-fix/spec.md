# 边框缓存机项目迁移整理Spec（修正版）

## Why
之前方案与工具V2.4.0实际生成的目录结构不一致，导致迁移后出现文件遗漏、位置错误、文档空白等问题。需要基于实际工具输出重新制定修正方案。

## What Changes
- **以工具V2.4.0实际结构为准** - 不修改已生成的目录结构
- **补全3个缺失文件** - CClink文档、流程图、IO表归位
- **填充6个核心文档** - 基于现有信息自动生成内容
- **建立符合实际的文件映射标准**

## Impact
- Affected specs: TPL-SINGLE-PLC-001模板（工具V2.4.0实现版）
- Affected code: DJ-2026-001_buffer_framing_machine项目

## ADDED Requirements

### Requirement: 文件完整性验证
系统 SHALL 确保原始目录中的所有文件都在新项目中有对应位置。

#### Scenario: 识别缺失文件
- **WHEN** 对比 `6.边框缓存机-buffer framing` 与 `DJ-2026-001_buffer_framing_machine`
- **THEN** 列出缺失的3个文件：CClink文档、流程图、IO表（位置错误）

### Requirement: 基于实际结构的文档填充
系统 SHALL 根据工具V2.4.0的实际目录结构生成和填充文档。

#### Scenario: IO分配表自动填充
- **WHEN** 检测到 `20_软件程序/21_PLC_Autoshop/Docs/IO表.xlsx`
- **THEN** 读取Excel内容并转换为Markdown格式填入 `{project_code}_IO分配表.md`

## MODIFIED Requirements

### Requirement: 目录结构遵循工具实际输出
所有操作必须基于以下实际目录结构（非理想方案）：

```
DJ-2026-001_buffer_framing_machine/
├── 00_项目管理/              # 非之前的"00_项目基础信息"
├── 10_技术设计/              # 非之前的"01_项目文档"
│   ├── 11_Eplan电气/
│   ├── 12_机械结构/
│   └── 13_通讯与协议/
├── 20_软件程序/              # 非之前的"02_开发文件"
│   ├── 21_PLC_Autoshop/
│   │   └── Source/2.PLC/    # 注意：保留2.PLC子目录
│   └── 22_HMI_ProFace/
│       └── 1.HMI/           # 注意：保留1.HMI子目录
├── 30_设备配置/
│   └── 驱动器参数/3.SV/     # 注意：路径为"驱动器参数"非"智能模块配置"
├── 40_交付与文档/
├── 07_交付文档/
└── 90_知识库_本项目/
```

### Requirement: 最终文件映射表（修正版）

| 原始文件 | 最终目标位置 | 当前状态 | 操作 |
|---------|------------|---------|------|
| `1.HMI/*.prx,.bak` | `20_软件程序/22_HMI_ProFace/1.HMI/` | ✅ 已完成 | 无 |
| `2.PLC/*.gx3` | `20_软件程序/21_PLC_Autoshop/Source/2.PLC/` | ✅ 已完成 | 无 |
| `3.SV/*` (3轴) | `30_设备配置/驱动器参数/3.SV/` | ✅ 已完成 | 无 |
| `5.边框储料机.pdf` | `10_技术设计/11_Eplan电气/Export_PDF/` | ✅ 已完成 | 无 |
| `CClink线体对接文档/*.txt` | `10_技术设计/13_通讯与协议/` | ❌ 缺失 | **复制** |
| `IO表.xlsx` | 项目根目录 | ⚠️ 位置错误 | **移动到Docs/** |
| `分料送料流程分析.vsdx` | ❌ 未找到 | ❌ 缺失 | **复制到12_机械结构/** |

## REMOVED Requirements
无