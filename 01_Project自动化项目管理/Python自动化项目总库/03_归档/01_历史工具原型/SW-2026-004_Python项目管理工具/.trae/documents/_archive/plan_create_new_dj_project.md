# 使用项目管理工具创建新项目计划

## 目标
使用修复后的 SW-2026-004 Python项目管理工具，以 DJ-2026-014 三段式玻璃输送线控制系统为基础，**通过 CLI 命令创建一个全新的项目**，验证工具的模板生成和项目创建功能。

## 新项目参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 业务线 | `DJ` | 单机设备项目 |
| 项目名称 | `三段式玻璃输送线控制系统(V2)` | 基于原项目重新创建 |
| 模板ID | `TPL-DJ-STD-001` | 单机设备标准版（DJ业务线推荐模板） |
| 负责人 | `AI开发助手` | 项目负责人 |
| 输出路径 | `d:\BaiduSyncdisk\My_Workspace\项目文件夹\` | 与原 DJ-2026-014 同级目录 |

## 执行步骤

### Step 1: 通过 CLI 创建项目
```bash
cd "d:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-004_Python项目管理工具\03_主程序\01_主程序核心代码"
py -3 main.py create-project --business-line DJ --name "三段式玻璃输送线控制系统(V2)" --template-id TPL-DJ-STD-001 --manager "AI开发助手" --path "d:\BaiduSyncdisk\My_Workspace\项目文件夹"
```

**预期结果**: 
- 工具返回 `项目创建成功: DJ-XXXX-XXX 三段式玻璃输送线控制系统(V2)`
- 在 `d:\BaiduSyncdisk\My_Workspace\项目文件夹\` 下生成新的项目目录

### Step 2: 查看生成的项目结构
```bash
# 列出新项目的完整目录结构
ls -R "d:\BaiduSyncdisk\My_Workspace\项目文件夹\DJ-*_三段式玻璃输送线*" 2>/dev/null || dir /s /b "d:\BaiduSyncdisk\My_Workspace\项目文件夹\DJ-*_三段式*"
```

**预期输出**: 展示 TPL-DJ-STD-001 模板生成的完整目录结构和自动生成的文档

### Step 3: 对比新旧项目
- 对比原 DJ-2026-014（手动填充）与新项目（工具生成）的目录结构差异
- 展示工具自动生成的 README 和基础文档
- 统计新项目的空目录率（应远低于原来的 77.6%）

### Step 4: 验证项目完整性
- 确认 .gitignore 存在
- 确认 README.md 存在且有内容
- 确认项目立项表等核心文档已生成
- 统计总文件数和目录数

## 预期产出
1. 一个全新的、由工具正式创建的 DJ 项目
2. 完整的项目目录结构展示
3. 与原手工项目的对比分析
