# Spec: 单机设备(PLC+HMI)模板补充Eplan+机械3D目录

## Why

用户使用V2.4.3最新版创建 **DJ-2026-001** 项目（单机设备PLC+HMI模板），发现生成的00~07目录中 **没有Eplan电气图纸和机械3D模型的存放位置**。

对比发现：**整线模板(TPL-FULLLINE-AUTO-001)** 已包含 `10_技术设计/11_Eplan电气/` 和 `10_技术设计/12_机械结构/`，但**单机设备模板(TPL-SINGLE-PLC-001)** 完全缺失这两类关键工程文档的目录。

实际项目中，即使是单机PLC设备，也必然涉及：
- **Eplan电气原理图**（IO分配、控制回路、安全回路）
- **机械3D模型**（设备布局、安装尺寸、BOM清单）

## What Changes

### 修改1: TPL-SINGLE-PLC-001 的 structure 字段

在现有8项基础上，**扩展2个目录**，将 `01_需求与设计` 拆分为带子目录的结构：

**当前结构 (8项)**：
```
00_项目管理
01_需求与设计          ← 扁平化，无子分类
02_PLC程序
03_HMI设计
04_驱动器与设备
05_测试与验证
06_文档与交付
07_工具与配置
```

**目标结构 (8项，01拆为子目录)**：
```
00_项目管理
01_需求与设计/
    11_Eplan电气/       ← 新增: Export_PDF + Source
    12_机械结构/        ← 新增: 3D_Models + 2D_Drawings  
    13_软件方案/        ← 原有内容移入
02_PLC程序
03_HMI设计
04_驱动器与设备
05_测试与验证
06_文档与交付
07_工具与配置
```

**设计原则**：
- 保持一级目录仍为 **00~07 共8个**（不破坏已验证通过的编号规则）
- 将 `01_需求与设计` 从扁平目录改为**含子目录的分类结构**
- 子目录编号对齐整线模板的命名风格（11=电气, 12=机械, 13=软件）
- 与 `TPL-FULLLINE-AUTO-001` 的 `10_技术设计/11_Eplan电气/12_机械结构` 保持一致的专业分类逻辑

### 修改2: TPL-SINGLE-PLC-001 的 templates 字段

新增以下模板文件：

| 路径 | 类型 | 内容 |
|------|------|------|
| `01_需求与设计/11_Eplan电气/Eplan检查清单.md` | document | Eplan图纸完整性检查项 |
| `01_需求与设计/12_机械结构/BOM模板.md` | document | 机械BOM清单模板 |
| `01_需求与设计/13_软件方案/IO分配表.md` | document | PLC IO分配表模板 |

### 修改3: 同步更新 template_editor.py 占位符文本

更新 `01_需求与设计` 相关占位符说明，体现新的子目录结构。

## Impact

- **Affected specs**: 无（本次为独立修复）
- **Affected code**:
  - `src/core/constants.py` — TPL-SINGLE-PLC-001 的 structure 和 templates 字段
  - `src/ui/widgets/template_editor.py` — 占位符提示文本（如有硬编码）
- **Affected data**: 数据库中已有项目不受影响（仅影响新建项目）
- **Breaking change**: **否** — 已有项目的目录结构不变，仅新建项目使用新结构

## ADDED Requirements

### Requirement: Eplan电气子目录

系统 SHALL 在 TPL-SINGLE-PLC-001 模板的 `01_需求与设计` 下创建 `11_Eplan电气` 子目录，包含：
- `Export_PDF/` — 存放导出的PDF电气原理图
- `Source/` — 存放Eplan源文件(.edz/.edb)

#### Scenario: 创建单机设备项目时自动生成Eplan目录
- **WHEN** 用户选择 TPL-SINGLE-PLC-001 模板创建新项目
- **THEN** 项目目录下存在 `01_需求与设计/11_Eplan电气/Export_PDF/` 和 `01_需求与设计/11_Eplan电气/Source/`

### Requirement: 机械结构子目录

系统 SHALL 在 TPL-SINGLE-PLC-001 模块的 `01_需求与设计` 下创建 `12_机械结构` 子目录，包含：
- `3D_Models/` — 存放SolidWorks/UG等3D模型文件
- `2D_Drawings/` — 存放2D工程图(PDF/DWG)

#### Scenario: 创建单机设备项目时自动生成机械目录
- **WHEN** 用户选择 TPL-SINGLE-PLC-001 模板创建新项目
- **THEN** 项目目录下存在 `01_需求与设计/12_机械结构/3D_Models/` 和 `01_需求与设计/12_机械结构/2D_Drawings/`

### Requirement: 软件方案子目录

系统 SHALL 将原有 `01_需求与设计` 下的内容归入 `13_软件方案/` 子目录，保持向后兼容。

#### Scenario: 需求设计文档存放在正确位置
- **WHEN** 系统生成需求规格、架构设计等文档
- **THEN** 文档位于 `01_需求与设计/13_软件方案/` 下

## MODIFIED Requirements

### Requirement: TPL-SINGLE-PLC-001 结构完整性

原要求：模板包含8个一级目录 (00~07)
修改后：模板包含8个一级目录 (00~07)，其中 `01_需求与设计` 包含3个子目录 (11_Eplan电气, 12_机械结构, 13_软件方案)

总物理目录数：从8个 → **约14个**（含子目录）

### Requirement: 模板跨模板一致性

原要求：各模板目录结构独立定义
修改后：**单机设备和整线模板在Eplan/机械分类上保持一致的命名规范**（11=Eplan, 12=机械）

## 不做的事项

- ❌ 不修改其他4个模板（FULLLINE已有Eplan/机械，其余模板不适用）
- ❌ 不改变00~07的一级目录编号规则
- ❌ 不删除或重命名现有的任何目录
- ❌ 不修改已有项目（DJ-2026-001等）的目录结构
