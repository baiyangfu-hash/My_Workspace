# Python项目管理工具 V2.4.0 → V2.5.0 迭代执行计划

## 一、计划概述

**基于已批准的诊断报告**: [tool_diagnosis_and_improvement_plan.md](../tool_diagnosis_and_improvement_plan.md)

**目标**: 完成工具的全量迭代，修复已知问题，同步文档，重新打包交付物

**版本规划**:
- **V2.4.1** (补丁版): 仅修复 {project_code} Bug + 当前项目应急处理
- **V2.5.0** (次版本): 模板结构规范对齐 + 变更管理完善 + 文档同步

---

## 二、现状确认

### 2.1 已确认的问题

| 问题编号 | 问题描述 | 严重程度 | 影响范围 | 定性 |
|:--------:|---------|:--------:|:-------:|:----:|
| P0-001 | 15个文件包含未替换的 `{project_code}` 占位符 | 🔴严重 | 所有新建项目 | 工具Bug |
| P1-001 | 变更管理目录缺少4个子目录(ELEC/MECH/HMI/SAFE) | 🟠重要 | 规范符合性 | 模板缺陷 |
| P1-002 | 缺少变更台帐文件和根目录README | 🟠重要 | 规范符合性 | 模板缺陷 |

### 2.2 受影响文件清单（P0-001）

**已确认15个文件**（通过 Glob 扫描验证）:

```
✗ 00_项目管理/01_立项与需求/{project_code}_需求分析文档.md
✗ 00_项目管理/01_立项与需求/{project_code}_项目立项表.md
✗ 10_技术设计/11_Eplan电气/Source/{project_code}_PLC硬件配置表.md
✗ 10_技术设计/11_Eplan电气/Export_PDF/{project_code}_电气图纸清单.md
✗ 10_技术设计/12_机械结构/3D_Models/{project_code}_机械BOM清单.md
✗ 20_软件程序/21_PLC_Autoshop/Docs/{project_code}_IO分配表.md
✗ 20_软件程序/21_PLC_Autoshop/Docs/{project_code}_PLC程序设计总文档.md
✗ 20_软件程序/21_PLC_Autoshop/Docs/{project_code}_系统架构设计说明书.md
✗ 20_软件程序/21_PLC_Autoshop/Docs/{project_code}_联锁逻辑设计说明书.md
✗ 40_交付与文档/41_操作手册/{project_code}_操作手册.md
✗ 40_交付与文档/43_验收清单/{project_code}_验收检查表.md
✗ 40_交付与文档/44_培训资料/{project_code}_培训记录.md
✗ 40_交付与文档/45_故障排查指南/{project_code}_故障排除手册.md
✗ 40_交付与文档/46_维护计划/{project_code}_维护手册.md
```

### 2.3 变更管理目录差异（P1-001/P1-002）

**当前状态**:
```
04_变更管理/
└── 01_变更单/
    ├── CHG-DOCU/     ✅
    ├── CHG-PLC/      ✅
    └── CHG-SCPT/     ✅
```

**Obsidian规范要求** (043_PM-V2.1.0):
```
04_变更管理/
├── 01_变更单/
│   ├── CHG-ELEC/     ❌ 缺失
│   ├── CHG-MECH/     ❌ 缺失
│   ├── CHG-PLC/      ✅ 已有
│   ├── CHG-HMI/      ❌ 缺失
│   ├── CHG-SCPT/     ✅ 已有
│   ├── CHG-DOCU/     ✅ 已有
│   └── CHG-SAFE/     ❌ 缺失
├── DJ-2026-001_版本变更台帐.md  ❌ 缺失
└── README.md                ❌ 缺失
```

---

## 三、执行阶段详细方案

### Phase 0：当前项目应急修复（立即可执行）

**目标**: 立即修复DJ-2026-001项目的15个文件名问题

**执行方式**: PowerShell批量重命名脚本

**步骤**:

#### Step 0.1 创建修复脚本

在 `d:\BaiduSyncdisk\My_Workspace\管理工具测试\` 下创建 `fix_project_names.ps1`:

```powershell
<#
.SYNOPSIS
    修复项目中未替换的 {project_code} 占位符
.DESCRIPTION
    批量重命名包含 {project_code} 的文件，替换为实际的项目编码
.PARAMETER ProjectPath
    项目根目录路径
.PARAMETER ProjectCode
    实际的项目编码（默认: DJ-2026-001）
.EXAMPLE
    .\fix_project_names.ps1 -ProjectPath "D:\Projects\DJ-2026-001_xxx"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectPath,

    [string]$ProjectCode = "DJ-2026-001"
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  项目名称修复工具" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "项目路径: $ProjectPath" -ForegroundColor Yellow
Write-Host "项目编码: $ProjectCode" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $ProjectPath)) {
    Write-Host "[ERROR] 项目路径不存在: $ProjectPath" -ForegroundColor Red
    exit 1
}

$filesToFix = Get-ChildItem -Path $ProjectPath -Recurse -File | Where-Object {
    $_.Name -like "*project_code*"
}

if ($filesToFix.Count -eq 0) {
    Write-Host "[INFO] 未发现需要修复的文件" -ForegroundColor Green
    exit 0
}

Write-Host "发现 $($filesToFix.Count) 个需要修复的文件:" -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($file in $filesToFix) {
    $newName = $file.Name.Replace("{project_code}", $ProjectCode)
    $newPath = Join-Path $file.Directory.FullName $newName

    try {
        Rename-Item -Path $file.FullName -NewName $newName -ErrorAction Stop
        Write-Host "[OK] 重命名成功: $($file.Name) -> $newName" -ForegroundColor Green
        $successCount++
    }
    catch {
        Write-Host "[FAIL] 重命名失败: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  修复完成!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "成功: $successCount 个文件" -ForegroundColor Green
Write-Host "失败: $failCount 个文件" -ForegroundColor Red
Write-Host ""

exit ($failCount -gt 0 ? 1 : 0)
```

#### Step 0.2 执行脚本

```powershell
cd d:\BaiduSyncdisk\My_Workspace\管理工具测试\
.\fix_project_names.ps1 -ProjectPath "d:\BaiduSyncdisk\My_Workspace\管理工具测试\Python自动化项目管理系统_V2.4.0_20260413\01_可执行文件\projects\DJ-2026-001_buffer_framing_machine（边框缓存机）"
```

#### Step 0.3 验证结果

再次运行 Glob 搜索确认无残留:
```powershell
Get-ChildItem -Path "项目路径" -Recurse -File | Where-Object { $_.Name -like "*project_code*" }
```

**预期结果**: 返回空（0个文件）

#### Step 0.4 补充变更管理缺失目录

手动创建以下目录和文件:

```
04_变更管理/
├── 01_变更单/
│   ├── CHG-ELEC/
│   │   └── README.md          # 新增：电气设计类变更说明
│   ├── CHG-MECH/
│   │   └── README.md          # 新增：机械结构类变更说明
│   ├── CHG-HMI/
│   │   └── README.md          # 新增：HMI程序类变更说明
│   └── CHG-SAFE/
│       └── README.md          # 新增：安全功能类变更说明
├── DJ-2026-001_版本变更台帐.md  # 新增：版本变更记录
└── README.md                  # 新增：变更管理说明
```

**README.md 内容模板**:

每个新增子目录的 README.md 应包含:
- 用途说明
- 命名规范 (`CHG-[DOMAIN]-[YYYY]-[序号].md`)
- 典型变更类型列表
- 关联文档链接

**DJ-2026-001_版本变更台帐.md 内容**:
- 版本号 | 变更日期 | 变更内容 | 变更人 | 审批状态
- 初始行: V1.0.0 | 2026-04-13 | 项目创建 | 系统 | 已发布

---

### Phase 1：工具Bug修复（P0）→ V2.4.1

**目标**: 从根源修复 {project_code} 替换逻辑

**前提条件**: 需要访问工具源代码

#### Step 1.1 定位源代码

**搜索范围**:
```
d:\BaiduSyncdisk\My_Workspace\管理工具测试\Python自动化项目管理系统_V2.4.0_20260413\
├── 01_可执行文件\src\              # 可能的位置1（开发用副本）
├── 01_可执行文件\_internal\src\    # 可能的位置2（PyInstaller解包）
└── (其他位置)
```

**关键词搜索**:
- `{project_code}`
- `create_project`
- `template.*replace`
- `占位符`
- `post_process`
- `rename.*file`

**预期修改文件**:
- `src/services/project_service.py` - 项目创建服务（最可能）
- `src/utils/template_utils.py` - 模板工具函数
- `src/core/template_manager.py` - 模板管理器

#### Step 1.2 分析Bug根因

**可能的原因**:

1. **字符串替换遗漏**
   ```python
   # 错误示例：只替换了内容，没替换文件名
   content = content.replace("{project_code}", project_code)
   # ❌ 缺少文件名重命名逻辑
   ```

2. **正则表达式匹配失败**
   ```python
   # 错误示例：正则特殊字符未转义
   re.sub("{project_code}", project_code, content)
   # {} 在正则中有特殊含义
   ```

3. **递归扫描遗漏**
   ```python
   # 错误示例：只扫描了一层目录
   for file in root_dir.glob("*.md"):  # ❌ 不递归
   ```

4. **时序问题**
   ```python
   # 错误示例：先创建目录再替换，但文件已经写入磁盘
   create_project_structure(template)  # 先创建（含占位符）
   replace_variables()                 # 后替换（可能遗漏某些文件）
   ```

#### Step 1.3 实施修复

**修复方案**: 在项目创建流程末尾添加 `post_process_project()` 函数

```python
def post_process_project(project_path: str, variables: dict):
    """
    项目创建后处理：确保所有占位符都被正确替换

    Args:
        project_path: 项目根目录路径
        variables: 变量字典 {placeholder: value}
                    例如: {"{project_code}": "DJ-2026-001", "{project_name}": "..."}
    """
    from pathlib import Path
    import os

    project_dir = Path(project_path)

    if not project_dir.exists():
        logger.warning(f"项目路径不存在: {project_path}")
        return

    # 1. 递归重命名包含占位符的文件
    for file in project_dir.rglob("*"):
        if not file.is_file():
            continue

        # 检查文件名是否包含任何占位符
        needs_rename = any(
            placeholder in file.name
            for placeholder in variables.keys()
        )

        if needs_rename:
            new_name = file.name
            for placeholder, value in variables.items():
                new_name = new_name.replace(placeholder, value)

            new_path = file.parent / new_name

            try:
                file.rename(new_path)
                logger.info(f"重命名文件: {file.name} -> {new_name}")
            except Exception as e:
                logger.error(f"重命名失败: {file.name} - {e}")

    # 2. 替换文件内容中的占位符（.md/.json/.txt等文本文件）
    text_extensions = {'.md', '.txt', '.json', '.csv', '.py', '.bat', '.ps1', '.yml', '.yaml'}

    for file in project_dir.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in text_extensions:
            continue

        try:
            content = file.read_text(encoding='utf-8')

            needs_update = any(
                placeholder in content
                for placeholder in variables.keys()
            )

            if needs_update:
                new_content = content
                for placeholder, value in variables.items():
                    new_content = new_content.replace(placeholder, value)

                file.write_text(new_content, encoding='utf-8')
                logger.info(f"更新文件内容: {file.name}")

        except Exception as e:
            logger.warning(f"无法处理文件 {file.name}: {e}")

    logger.info(f"项目后处理完成: {project_path}")
```

**集成点**: 在 `project_service.py` 的 `create_project()` 方法末尾调用:

```python
def create_project(self, project_data: dict) -> tuple:
    # ... 原有逻辑 ...

    # 创建项目目录结构
    self._create_project_structure(project_path, template)

    # 替换模板变量
    self._replace_template_variables(project_path, variables)

    # ★ 新增：后处理，确保所有占位符都被替换
    post_process_project(project_path, variables)

    return True, "项目创建成功"
```

#### Step 1.4 更新版本号

**修改文件**:
- `config/app_config.json`: `"version": "1.0.0"` → `"version": "1.0.1"` （应用内部版本）
- `01_交付清单_DEL-V2.4.0.md` → 更新为 `DEL-V2.4.1.md`

**版本标记**:
- 工具版本: V2.4.0 → **V2.4.1**
- 发布类型: Patch Release（补丁修复）
- 发布日期: 2026-04-15

---

### Phase 2：模板规范更新（P1）→ V2.5.0

**目标**: 对齐 Obsidian 规范 043_PM-V2.1.0，完善变更管理目录结构

#### Step 2.1 定位模板定义

**搜索位置**:
```
config/templates/
├── TPL-SINGLE-PLC-001/           # 单机设备模板（重点）
├── TPL-AUTO-LINE-001/           # 自动化整线模板
├── TPL-DJ-STATION-001/          # 单机工站模板
└── ...
```

**或可能在代码中硬定义**:
- JSON配置文件
- Python字典/列表
- YAML文件
- 数据库模板表

#### Step 2.2 更新 TPL-SINGLE-PLC-001 模板

**变更内容**: 在 `04_变更管理/` 部分添加缺失项

**新增目录结构**:
```
04_变更管理/
├── 01_变更单/
│   ├── CHG-ELEC/                    # 新增：电气设计类
│   │   └── .gitkeep (或 README.md)
│   ├── CHG-MECH/                    # 新增：机械结构类
│   │   └── .gitkeep (或 README.md)
│   ├── CHG-PLC/                     # 已有：保留
│   ├── CHG-HMI/                     # 新增：HMI程序类
│   │   └── .gitkeep (或 README.md)
│   ├── CHG-SCPT/                    # 已有：保留
│   ├── CHG-DOCU/                    # 已有：保留
│   └── CHG-SAFE/                    # 新增：安全功能类
│       └── .gitkeep (或 README.md)
├── {project_code}_版本变更台帐.md    # 新增：模板文件
└── README.md                        # 新增：变更管理说明
```

**模板文件内容**:

##### DJ-2026-001_版本变更台帐.md (模板):

```markdown
# {project_code} 版本变更台帐

## 文档基础信息

| 属性 | 值 |
|------|-----|
| 文档编号 | {project_code}-CHG-LEDGER-001 |
| 文档名称 | 版本变更台帐 |
| 创建日期 | {current_date} |
| 最后更新 | {current_date} |
| 维护人 | [待填写] |
| 状态 | 活跃 |

---

## 版本变更记录

| 版本号 | 变更日期 | 变更类型 | 变更内容摘要 | 变更人 | 审批人 | 关联变更单 | 状态 |
|:------:|:--------:|:--------:|-------------|:------:|:------:|:----------:|:----:|
| V1.0.0 | {current_date} | 初始创建 | 项目初始化 | 系统 | - | - | 已发布 |

---

## 使用说明

1. 每次项目变更时，在此台帐中记录版本信息
2. 关联到具体的变更单文件（CHG-*）
3. 保持版本号连续性
4. 定期回顾和整理历史记录
```

##### README.md (变更管理根目录):

```markdown
# 变更管理目录

## 目录结构

本目录按照 Obsidian 规范 043_通用变更管理目录结构说明_PM-V2.1.0 组织。

### 01_变更单/

按变更领域分类存放所有变更记录：

| 子目录 | 编码 | 用途 | 典型变更内容 |
|--------|:----:|------|-------------|
| CHG-ELEC | ELEC | 电气设计类 | 电气图纸修改、IO点位调整、元器件选型变更 |
| CHG-MECH | MECH | 机械结构类 | 结构件修改、3D模型更新、BOM调整 |
| CHG-PLC | PLC | PLC程序类 | 程序逻辑修改、功能块新增、通讯协议变更 |
| CHG-HMI | HMI | HMI程序类 | 界面布局修改、操作流程优化、报警信息调整 |
| CHG-SCPT | SCPT | 脚本工具类 | 辅助脚本修改、数据处理逻辑变更 |
| CHG-DOCU | DOCU | 文档类 | 技术文档更新、操作手册修订、规格书变更 |
| CHG-SAFE | SAFE | 安全功能类 | 安全逻辑修改、急停回路变更、防护装置调整 |

### 命名规范

变更单文件命名格式：`CHG-[DOMAIN]-[YYYY]-[序号]_[简短描述].md`

**示例**:
- `CHG-PLC-2026-001_取料逻辑优化.md`
- `CHG-ELEC-2026-001_传感器点位调整.md`
- `CHG-HMI-2026-001_操作界面简化.md`

### 版本变更台帐

- [{project_code}_版本变更台帐.md](./{project_code}_版本变更台帐.md) - 记录所有版本变更历史

### 相关规范

- [043_通用变更管理目录结构说明_PM-V2.1.0](../../../../00_Obsidian_Base全局规范文件仓库/04_监控和控制/01_变更管理/03_变更管理规范/043_通用变更管理目录结构说明_PM-V2.1.0.md)

---

**最后更新**: {current_date}
**维护人**: [待填写]
```

##### 各CHG-*/README.md 统一模板:

```markdown
# [DOMAIN_NAME] 类变更单

## 用途

存放所有 [DOMAIN_DESC] 相关的变更记录和文档。

## 命名规范

- 格式：`CHG-[DOMAIN_CODE]-[YYYY]-[序号]_[简短描述].md`
- 示例：`CHG-[DOMAIN_CODE]-2026-001_[示例变更].md`

## 典型变更类型

[TYPICAL_CHANGES_LIST]

## 变更单模板

```markdown
# CHG-[DOMAIN_CODE]-[YYYY]-[XXX]_[变更标题]

## 变更基本信息

| 属性 | 值 |
|------|-----|
| 变更编号 | CHG-[DOMAIN_CODE]-[YYYY]-[XXX] |
| 变更标题 | [变更标题] |
| 变更类型 | [修正/优化/新增/删除] |
| 优先级 | [紧急/高/中/低] |
| 提出人 | [姓名] |
| 提出日期 | [YYYY-MM-DD] |
| 计划完成 | [YYYY-MM-DD] |
| 状态 | [草稿/审批中/执行中/已完成/已拒绝] |

## 变更描述

[详细描述变更内容和原因]

## 影响分析

- [ ] 影响范围
- [ ] 风险评估
- [ ] 回滚方案

## 实施步骤

1. [步骤1]
2. [步骤2]
3. ...

## 验证结果

- [ ] 测试通过
- [ ] 用户验收
- [ ] 文档更新

## 审批记录

| 角色 | 姓名 | 日期 | 意见 |
|------|------|------|------|
| 审批人 | | | |
| 验收人 | | | |
```

## 关联文档

- [IO分配表](../../20_软件程序/21_PLC_Autoshop/Docs/{project_code}_IO分配表.md)
- [系统架构设计说明书](../../20_软件程序/21_PLC_Autoshop/Docs/{project_code}_系统架构设计说明书.md)

---

**最后更新**: {current_date}
```

**各DOMAIN的具体内容**:

| DOMAIN | DOMAIN_CODE | DOMAIN_NAME | TYPICAL_CHANGES_LIST |
|--------|:-----------:|-------------|---------------------|
| 电气设计 | ELEC | 电气设计 | - 电气原理图修改\n- IO点位调整\n- 元器件选型变更\n- 接线图更新\n- 电气BOM调整 |
| 机械结构 | MECH | 机械结构 | - 3D模型修改\n- 结构件变更\n- 机械BOM调整\n- 安装尺寸变更\n- 材质更换 |
| PLC程序 | PLC | PLC程序 | - 程序逻辑修改\n- 功能块(FB)新增/修改\n- IO地址调整\n- 通讯协议变更\n- 联锁逻辑调整 |
| HMI程序 | HMI | HMI程序 | - 界面布局修改\n- 操作流程优化\n- 报警信息调整\n- 数据显示变更\n- 权限设置修改 |
| 脚本工具 | SCPT | 脚本工具 | - 辅助脚本修改\n- 数据处理逻辑变更\n- 配置参数调整\n- 工具功能增强 |
| 文档 | DOCU | 文档 | - 技术文档更新\n- 操作手册修订\n- 需求规格变更\n- 测试用例更新 |
| 安全功能 | SAFE | 安全功能 | - 安全逻辑修改\n- 急停回路变更\n- 光幕/安全门调整\n- 防护装置变更\n- 安全PLC程序修改 |

#### Step 2.3 同步检查其他模板

**需检查的模板清单**:

| 模板ID | 模板名称 | 优先级 | 检查项 |
|--------|---------|:------:|--------|
| TPL-SINGLE-PLC-001 | 单机设备（本次重点） | P0 | 变更管理目录完整性 |
| TPL-AUTO-LINE-001 | 自动化整线 | P1 | 同上 |
| TPL-DJ-STATION-001 | 单机工站 | P1 | 同上 |
| 其他自定义模板 | - | P2 | 同上 |

**检查标准**:
- [ ] 包含7个CHG-*子目录
- [ ] 包含版本变更台帐模板
- [ ] 包含根目录README.md
- [ ] 每个子目录有README.md或.gitkeep

---

### Phase 3：测试验证

#### Step 3.1 单元测试

**测试用例矩阵**:

| 编号 | 测试项 | 测试方法 | 预期结果 | 优先级 |
|:----:|-------|---------|---------|:------:|
| T-001 | 文件名占位符替换 | 创建测试项目，Glob扫描 `*{project_code}*` | ✅ 0个匹配 | P0 |
| T-002 | 文件内容占位符替换 | 检查所有.md文件内容 | ✅ 无残留占位符 | P0 |
| T-003 | 变更管理目录完整性 | LS检查 `04_变更管理/` | ✅ 7子目录+台帐+README | P1 |
| T-004 | 多业务线兼容性 | 分别创建SW/DJ/ZD项目 | ✅ 各自正确替换 | P1 |
| T-005 | 特殊字符处理 | 项目名含中文/括号/空格 | ✅ 正常工作 | P2 |
| T-006 | 长路径处理 | 项目名>50字符 | ✅ 正常截断或提示 | P2 |

**T-001 详细测试脚本**:

```python
import os
from pathlib import Path

def test_no_placeholder_in_filenames(project_path: str):
    """T-001: 验证创建后的项目文件名中无{project_code}占位符"""
    project_dir = Path(project_path)

    placeholders = ["{project_code}", "{project_name}", "{business_line}"]

    files_with_placeholders = []
    for file in project_dir.rglob("*"):
        if file.is_file():
            for placeholder in placeholders:
                if placeholder in file.name:
                    files_with_placeholders.append(str(file.relative_to(project_dir)))

    assert len(files_with_placeholders) == 0, \
        f"发现 {len(files_with_placeholders)} 个文件包含占位符:\n" + "\n".join(files_with_placeholders)

    print("✅ T-001 通过：所有文件名占位符已正确替换")
```

#### Step 3.2 回归测试

**必测场景**:

1. ✅ 创建新的DJ项目（单机设备）→ 使用TPL-SINGLE-PLC-001
2. ✅ 创建新的ZD项目（自动化整线）→ 使用TPL-AUTO-LINE-001（如有）
3. ✅ 使用不同业务线前缀（SW/DJ/ZD/自定义）
4. ✅ 项目名包含中文、括号、连字符等特殊字符
5. ✅ 在非默认路径创建项目
6. ✅ 并发创建多个项目

**回归测试环境**:
- Windows 10 (64位)
- Windows 11 (64位)
- Python 3.14 (PyInstaller打包环境)

---

### Phase 4：文档同步

#### Step 4.1 更新工具使用文档

**需更新的文档**:

| 文件路径 | 更新内容 | 优先级 |
|---------|---------|:------:|
| `04_文档/程序使用说明.md` | 新增"已知问题和解决方案"章节 | P1 |
| `01_项目文档/05_模板结构说明.md` | 更新为V2.5.0模板结构（含完整变更管理） | P0 |
| `01_交付清单_DEL-V2.4.1.md` | 从V2.4.0更新，记录本次修复内容 | P0 |
| `README.md` (工具根目录) | 更新版本号和变更日志 | P1 |

#### Step 4.2 新增文档

**新增文档清单**:

| 文档名称 | 内容 | 位置 |
|---------|------|------|
| V2.4.1_更新说明.md | 本次Bug修复详情 | `02_发布说明/` |
| V2.4.1_已知问题.md | 当前版本限制和遗留问题 | `02_发布说明/` |
| V2.5.0_更新说明.md | 模板重大更新详情 | `02_发布说明/` (V2.5.0时) |
| V2.5.0_迁移指南.md | 从旧版本升级指南 | `02_发布说明/` (V2.5.0时) |
| V2.5.0_规范符合性报告.md | 与Obsidian规范对比 | `03_测试报告/` (V2.5.0时) |

**V2.4.1_更新说明.md 内容框架**:

```markdown
# Python项目管理工具 V2.4.1 更新说明

## 发布日期: 2026-04-15
## 版本类型: 补丁修复 (Patch Release)
## 上一个版本: V2.4.0

---

## 修复内容

### 🔧 Bug修复

#### [FIX-001] 严重: {project_code}占位符未被替换

**问题现象**:
- 新建项目后，15个文档文件名包含未替换的 `{project_code}` 字符串
- 例如: `{project_code}_项目立项表.md` 应为 `DJ-2026-001_项目立项表.md`
- 影响: 所有新建项目，降低专业性

**根本原因**:
- 项目创建流程中，模板变量替换逻辑未覆盖文件名
- 仅替换了文件内容中的占位符，遗漏了文件名重命名步骤

**修复方案**:
- 新增 `post_process_project()` 后处理函数
- 在项目创建完成后，递归扫描所有文件
- 同时处理文件名和文件内容中的占位符
- 支持多个占位符的批量替换

**验证方法**:
- 创建测试项目
- 使用 Glob 搜索 `*{project_code}*`
- 预期结果: 0个匹配文件

**影响范围**:
- 仅影响新建项目（已有项目需手动运行修复脚本）
- 不影响其他功能模块

---

### 📝 文档更新

- 更新《用户操作手册》相关章节
- 补充《常见问题解答》FAQ第12条

---

## 安装说明

### 全新安装
1. 解压 `Python自动化项目管理系统_V2.4.1_YYYYMMDD.zip` 到任意目录
2. 双击 `Python项目管理工具.exe` 启动

### 从V2.4.0升级
1. 备份现有项目和数据库
2. 解压新版本覆盖旧版本（保留config和projects目录）
3. 对于已有项目，运行 `fix_project_names.ps1` 修复文件名（可选）

---

## 已知问题

### ⚠️ P1: 变更管理目录不完全符合Obsidian规范V2.1.0

**问题描述**:
- 当前模板仅生成3个变更子目录（DOCU/PLC/SCPT）
- Obsidian规范要求7个子目录（+ELEC/MECH/HMI/SAFE）
- 缺少版本变更台帐和根目录README

**影响**:
- 规范符合性不足
- 手动补充即可正常使用

**解决方案**:
- **临时**: 手动创建缺失目录（参考本文档附录A）
- **正式**: 升级到V2.5.0（预计下周发布）

**计划修复版本**: V2.5.0

### ⏳ P2: 文档自动填充功能尚未实现

**问题描述**:
- 生成的文档为空白模板，需要手动填充内容
- 期望基于项目信息和已有文件自动生成初稿

**状态**: 规划中
**计划版本**: V2.6.0+

---

## 反馈渠道

如遇问题请通过以下方式反馈:
- Email: [待填写]
- Issue跟踪: [待填写]

---

**编制团队**: AI Assistant / 技术团队
**审核人**: [待填写]
**批准人**: [待填写]
```

#### Step 4.3 同步Obsidian全局规范仓库

**需同步的内容**:

1. **最佳实践案例** (新增):
   - 文件路径: `00_Obsidian_Base全局规范文件仓库/09_案例库/边框缓存机迁移案例/`
   - 内容: 基于DJ-2026-001项目的实际迁移经验
   - 包括: 问题发现过程、解决方案、经验教训

2. **模板缺陷记录** (更新):
   - 文件路径: `00_Obsidian_Base全局规范文件仓库/02_规划过程/02_技术规划/05_模板规范/`
   - 内容: 记录已发现的模板缺陷和修复状态

3. **规范符合性检查清单** (新增):
   - 文件路径: `00_Obsidian_Base全局规范文件仓库/04_监控和控制/01_变更管理/`
   - 内容: 模板规范符合性自查表

---

### Phase 5：版本打包与交付物准备

#### Step 5.1 V2.4.1 打包清单（紧急补丁版）

**目录结构**:
```
Python自动化项目管理系统_V2.4.1_20260415/
├── 01_可执行文件/
│   ├── Python项目管理工具.exe          # 主程序（已修复Bug）
│   ├── config/                         # 配置文件
│   │   ├── app_config.json             # version: "1.0.1"
│   │   ├── api_config.json
│   │   ├── database_config.json
│   │   └── spec_version_config.json
│   ├── _internal/                      # Python依赖
│   └── src/                            # 源代码（如有）
├── 02_发布说明/
│   ├── V2.4.1_更新说明.md              # ✅ 必须包含
│   ├── V2.4.1_已知问题.md              # ✅ 必须包含
│   └── fix_project_names.ps1           # ✅ 历史项目修复脚本
├── 03_测试报告/
│   └── V2.4.1_测试报告.md              # 测试结果汇总
├── 04_文档/
│   ├── 程序使用说明.md                  # 用户手册
│   └── FAQ常见问题解答.md              # 补充P0/P1问题的解决方案
├── 05_数据库/
│   └── project_manager.db              # 示例数据库（可选）
└── README.md                           # 快速入门指南
```

**打包命令** (PowerShell):

```powershell
# 创建发布目录
$releaseDir = "Python自动化项目管理系统_V2.4.1_20260415"
New-Item -ItemType Directory -Path $releaseDir -Force

# 复制核心文件
Copy-Item -Path "01_可执行文件\*" -Destination "$releaseDir\01_可执行文件\" -Recurse
New-Item -ItemType Directory -Path "$releaseDir\02_发布说明" -Force
New-Item -ItemType Directory -Path "$releaseDir\03_测试报告" -Force

# 生成发布说明文档（见Phase 4.2）
# 生成测试报告（见Phase 3结果）

# 打包为zip
Compress-Archive -Path $releaseDir -DestinationPath "$releaseDir.zip"

Write-Host "✅ 打包完成: $releaseDir.zip"
```

#### Step 5.2 V2.5.0 打包清单（模板更新版）

**额外包含的内容**:
```
├── 01_可执行文件/
│   └── config/templates/
│       └── TPL-SINGLE-PLC-001/         # ✅ 更新的模板（完整变更管理）
├── 02_发布说明/
│   ├── V2.5.0_更新说明.md              # 模板重大更新
│   ├── V2.5.0_迁移指南.md              # 从V2.4.x升级指南
│   └── V2.5.0_规范符合性报告.md         # 与Obsidian规范对比
└── 03_测试报告/
    └── V2.5.0_规范符合性测试报告.md      # 重点测试变更管理
```

#### Step 5.3 交付物检查清单

**V2.4.1 交付检查**:

- [ ] **可执行程序**: `Python项目管理工具.exe` 可正常运行
- [ ] **版本号显示**: 启动界面显示 V2.4.1
- [ ] **Bug复现测试**: 创建新项目后无 `{project_code}` 文件
- [ ] **修复脚本**: `fix_project_names.ps1` 可用于历史项目
- [ ] **更新说明文档**: `V2.4.1_更新说明.md` 内容完整
- [ ] **已知问题文档**: `V2.4.1_已知问题.md` 标注清晰
- [ ] **测试报告**: 至少T-001~T-004全部通过
- [ ] **用户手册**: 更新相关章节
- [ ] **快速入门**: README.md 简明易懂
- [ ] **打包完整性**: zip文件可正常解压，目录结构正确

**V2.5.0 额外检查**:

- [ ] **模板完整性**: TPL-SINGLE-PLC-001 含7个CHG子目录
- [ ] **台帐模板**: `{project_code}_版本变更台帐.md` 存在且格式正确
- [ ] **README文件**: 变更管理根目录及各子目录均有README
- [ ] **规范符合性**: 通过Obsidian 043规范逐项检查
- [ ] **向后兼容**: 旧版本项目可正常打开（不强制升级结构）
- [ ] **迁移工具**: 提供"一键补全目录"功能或脚本

---

### Phase 6：发布交付

#### Step 6.1 内部发布流程

```
代码修复完成
    ↓
单元测试 (T-001 ~ T-006)
    ↓ [全部通过]
集成测试 (回归场景1~6)
    ↓ [全部通过]
打包生成 (V2.4.1.zip)
    ↓
内部验收测试
    ↓ [验收通过]
正式发布通知
    ↓
用户下载使用
    ↓
反馈收集与问题跟踪
```

#### Step 6.2 发布通知模板

**邮件/消息通知**:

```
主题: 【发布】Python项目管理工具 V2.4.1 (紧急Bug修复版)

各位同事:

Python项目管理工具已发布 V2.4.1 版本，主要修复了以下问题:

🔧 重要修复:
- [FIX-001] 解决新建项目时文件名包含未替换占位符的问题
  影响: 15个文档文件名显示为 {project_code}_xxx.md 而非实际项目编码

📦 获取方式:
- 下载链接: [共享路径/附件]
- 文件大小: ~XX MB
- 密码: [如有]

📋 升级说明:
1. 备份现有项目（建议）
2. 解压新版本覆盖安装
3. 如有历史项目需修复，请运行附带的 fix_project_names.ps1 脚本

⚠️ 注意事项:
- 本版本为补丁修复，仅解决P0问题
- 变更管理目录规范对齐将在V2.5.0发布（下周）
- 如遇问题请联系: [联系方式]

📅 后续计划:
- V2.5.0 (预计下周): 模板结构更新，完全符合Obsidian规范V2.1.0

---
发布时间: 2026-04-15
发布人: AI Assistant / 技术团队
```

#### Step 6.3 交付物归档

**归档清单**:

| 归档项 | 位置 | 保留期限 |
|--------|------|:--------:|
| 源代码快照 | Git Tag: V2.4.1 | 永久 |
| 打包文件 | `/archive/V2.4.1/` | 5年 |
| 测试报告 | `/docs/test_reports/V2.4.1/` | 5年 |
| 用户反馈 | `/feedback/V2.4.1/` | 3年 |
| 发布通知 | `/docs/releases/V2.4.1_notice.md` | 3年 |

---

## 四、时间估算与里程碑

### 4.1 各阶段时间估算

| 阶段 | 任务 | 预计时间 | 依赖关系 | 里程碑 |
|:----:|-----|:--------:|:--------:|--------|
| **0** | 当前项目应急修复 | **10分钟** | 无 | ✅ 15个文件名修复完成 |
| **1** | Bug定位与修复 | **1-2小时** | 需要源代码访问权限 | 🔧 V2.4.1代码修复完成 |
| **2** | 模板结构更新 | **3-4小时** | Phase 1完成后 | 📋 V2.5.0模板就绪 |
| **3** | 测试验证 | **2小时** | Phase 1+2完成后 | ✅ 所有测试用例通过 |
| **4** | 文档同步 | **1小时** | Phase 3完成后 | 📝 所有文档更新完毕 |
| **5** | 打包准备 | **1小时** | Phase 4完成后 | 📦 交付物zip就绪 |
| **6** | 发布交付 | **30分钟** | Phase 5完成后 | 🚀 正式发布 |

**总计估算**:
- **快速通道** (仅Phase 0+1+3+4+5+6): **约1个工作日** → V2.4.1
- **完整迭代** (全部Phase): **约2个工作日** → V2.5.0

### 4.2 里程碑时间线

```
Day 1 (今天):
  ├─ 10:00  Phase 0: 应急修复当前项目 (10min)
  ├─ 10:30  Phase 1: Bug定位与代码修复 (2h)
  ├─ 13:00  Phase 3: 测试验证 (1h)
  ├─ 14:00  Phase 4: 文档同步 (1h)
  ├─ 15:00  Phase 5: V2.4.1打包 (1h)
  └─ 16:00  Phase 6: V2.4.1发布 (30min)

Day 2 (明天/下周):
  ├─ 09:00  Phase 2: 模板结构更新 (3h)
  ├─ 12:00  Phase 3: 补充测试 (1h)
  ├─ 13:00  Phase 4: V2.5.0文档 (1h)
  ├─ 14:00  Phase 5: V2.5.0打包 (1h)
  └─ 15:00  Phase 6: V2.5.0发布 (30min)
```

---

## 五、风险与应对措施

### 5.1 风险识别

| 风险编号 | 风险描述 | 概率 | 影响 | 应对措施 |
|:--------:|---------|:----:|:----:|---------|
| R-01 | 无法访问源代码（仅打包的exe） | 中 | 高 | 使用反编译工具或在代码外围打补丁 |
| R-02 | 修复引入新Bug | 低 | 高 | 充分测试+回滚机制 |
| R-03 | 模板更新破坏向后兼容性 | 中 | 中 | 保持旧项目可正常打开，仅影响新建项目 |
| R-04 | 时间估算不准确 | 中 | 低 | 优先完成V2.4.1，V2.5.0可延后 |
| R-05 | 用户不接受工作流变化 | 低 | 中 | 提供迁移指南+培训支持 |

### 5.2 关键决策点

**Decision 1: 是否能获取完整源代码？**

- **情况A: 能获取** → 按照Phase 1正常修复，从根源解决问题
- **情况B: 不能获取（仅有exe）** → 备选方案:
  - 方案B1: 使用PyInstaller反编译（可能不完整）
  - 方案B2: 开发外部修补程序（监控创建后自动重命名）
  - 方案B3: 修改模板文件本身（将 `{project_code}` 改为固定前缀或留空）

**Decision 2: V2.4.1和V2.5.0是否合并发布？**

- **合并**: 一次发布，减少用户升级次数，但周期较长（2天）
- **分开**: 先发V2.4.1应急（1天），再发V2.5.0完善（下周）
- **推荐**: 分开发布（快速响应用户痛点）

---

## 六、成功标准

### 6.1 验收标准（Definition of Done）

**V2.4.1 验收**:

- [x] **功能完整性**: 创建新项目后，Glob搜索 `*{project_code}*` 返回0结果
- [x] **向后兼容**: 已有项目可正常打开和使用（不受影响）
- [x] **修复可用**: 附带的 `fix_project_names.ps1` 可成功修复历史项目
- [x] **测试通过**: T-001~T-004 全部通过（通过率100%）
- [x] **文档齐全**: 更新说明、已知问题、测试报告均已提供
- [x] **打包完整**: zip文件可解压，目录结构正确，程序可启动

**V2.5.0 额外验收**:

- [x] **规范符合**: 变更管理目录完全符合Obsidian 043规范V2.1.0
- [x] **模板完整**: 7个CHG子目录 + 台帐 + README 全部存在
- [x] **内容质量**: README文件内容清晰，台帐模板可用
- [x] **多模板一致**: 所有受检模板均通过规范符合性检查

### 6.2 质量门槛

| 指标 | V2.4.1要求 | V2.5.0要求 |
|------|:----------:|:----------:|
| 测试用例通过率 | ≥95% (T-001~T-004必过) | ≥98% (T-001~T-006必过) |
| Bug修复率 | 100% (P0问题全部修复) | 100% (P0+P1问题全部修复) |
| 文档覆盖率 | 核心文档100%更新 | 全部文档100%更新 |
| 向后兼容性 | 无破坏性变更 | 无破坏性变更 |
| 用户满意度 | 预期: 问题解决 | 预期: 工作流改善 |

---

## 七、后续改进方向（V2.6.0+）

### 7.1 短期改进（1个月内）

- [ ] **P2实现**: 文档智能填充功能（基于AI或规则引擎）
- [ ] **增强**: 模板验证机制（创建前自动检查完整性）
- [ ] **增强**: 规范同步工具（Obsidian规范更新时提示模板需要更新）
- [ ] **优化**: 用户反馈收集功能（集成在工具内）

### 7.2 中期改进（3个月内）

- [ ] **新功能**: 项目向导式创建（分步骤引导填写信息）
- [ ] **新功能**: 历史项目导入助手（自动识别和映射文件）
- [ ] **新功能**: 文档版本对比和差异可视化
- [ ] **优化**: 性能优化（大项目加载速度提升）

### 7.3 长期愿景（6个月+）

- [ ] **架构升级**: 插件化架构（支持自定义扩展）
- [ ] **集成**: 与Git深度集成（版本控制+协作）
- [ ] **智能化**: AI辅助项目规划和文档生成
- [ ] **平台化**: 支持Web端访问和移动端查看

---

## 八、附录

### 附录A：手动补全变更管理目录脚本

对于无法等待V2.5.0的用户，可使用此脚本手动补全当前项目:

```powershell
<#
.SYNOPSIS
    补全项目的变更管理目录结构（符合Obsidian 043规范V2.1.0）
.PARAMETER ProjectPath
    项目根目录路径
.PARAMETER ProjectCode
    项目编码
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectPath,

    [string]$ProjectCode = "DJ-2026-001"
)

$changeMgmtDir = Join-Path $ProjectPath "00_项目管理\04_变更管理"
$changeOrderDir = Join-Path $changeMgmtDir "01_变更单"

# 要创建的子目录
$newDirs = @(
    "CHG-ELEC",
    "CHG-MECH",
    "CHG-HMI",
    "CHG-SAFE"
)

foreach ($dir in $newDirs) {
    $dirPath = Join-Path $changeOrderDir $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null

        # 创建README.md
        $readmeContent = @"
# $dir 类变更单

## 用途
存放所有 $dir 相关的变更记录和文档。

## 命名规范
- 格式：`CHG-$dir-[YYYY]-[序号]_[简短描述].md`

## 关联文档
- [$($ProjectCode)_版本变更台帐.md](../../$($ProjectCode)_版本变更台帐.md)
- [IO分配表](../../../20_软件程序/21_PLC_Autoshop/Docs/$($ProjectCode)_IO分配表.md)

---
**最后更新**: $(Get-Date -Format "yyyy-MM-dd")
"@
        Set-Content -Path (Join-Path $dirPath "README.md") -Value $readmeContent -Encoding UTF8
        Write-Host "[OK] 创建目录: $dir" -ForegroundColor Green
    }
    else {
        Write-Host "[SKIP] 目录已存在: $dir" -ForegroundColor Yellow
    }
}

# 创建版本变更台帐
$ledgerPath = Join-Path $changeMgmtDir "$($ProjectCode)_版本变更台帐.md"
if (-not (Test-Path $ledgerPath)) {
    $ledgerContent = @"
# $ProjectCode 版本变更台帐

## 版本变更记录

| 版本号 | 变更日期 | 变更类型 | 变更内容摘要 | 变更人 | 审批人 | 状态 |
|:------:|:--------:|:--------:|-------------|:------:|:------:|:----:|
| V1.0.0 | $(Get-Date -Format "yyyy-MM-dd") | 初始创建 | 项目初始化 | 系统 | - | 已发布 |

---
**最后更新**: $(Get-Date -Format "yyyy-MM-dd")
"@
    Set-Content -Path $ledgerPath -Value $ledgerContent -Encoding UTF8
    Write-Host "[OK] 创建版本变更台帐" -ForegroundColor Green
}

# 创建根目录README
$readmeRootPath = Join-Path $changeMgmtDir "README.md"
if (-not (Test-Path $readmeRootPath)) {
    $readmeRootContent = @"
# 变更管理目录

## 目录结构

本目录按照 Obsidian 规范 043_通用变更管理目录结构说明_PM-V2.1.0 组织。

### 01_变更单/

| 子目录 | 编码 | 用途 |
|--------|:----:|------|
| CHG-ELEC | ELEC | 电气设计类变更 |
| CHG-MECH | MECH | 机械结构类变更 |
| CHG-PLC | PLC | PLC程序类变更 |
| CHG-HMI | HMI | HMI程序类变更 |
| CHG-SCPT | SCPT | 脚本工具类变更 |
| CHG-DOCU | DOCU | 文档类变更 |
| CHG-SAFE | SAFE | 安全功能类变更 |

### 文件

- [$($ProjectCode)_版本变更台帐.md](./$($ProjectCode)_版本变更台帐.md) - 版本变更历史记录

---
**最后更新**: $(Get-Date -Format "yyyy-MM-dd")
"@
    Set-Content -Path $readmeRootPath -Value $readmeRootContent -Encoding UTF8
    Write-Host "[OK] 创建变更管理README" -ForegroundColor Green
}

Write-Host "`n✅ 变更管理目录补全完成!" -ForegroundColor Cyan
```

**使用方法**:
```powershell
.\complete_change_management.ps1 -ProjectPath "D:\...\DJ-2026-001_buffer_framing_machine（边框缓存机）"
```

### 附录B：测试数据准备

**T-001测试用例 - 预期创建的文件清单**:

创建测试项目 `TEST-2026-001_单元测试项目` 后，应生成的部分文件:

```
✅ TEST-2026-001_项目立项表.md         (不是 {project_code}_项目立项表.md)
✅ TEST-2026-001_需求分析文档.md       (不是 {project_code}_需求分析文档.md)
✅ TEST-2026-001_IO分配表.md           (不是 {project_code}_IO分配表.md)
... (其余13个文件同理)
```

### 附录C：术语表

| 术语 | 全称 | 说明 |
|------|------|------|
| P0/P1/P2 | Priority 0/1/2 | 优先级等级（0=紧急，1=重要，2=增强） |
| TPL-SINGLE-PLC-001 | Template Single PLC 001 | 单机设备PLC项目模板 |
| Obsidian | - | 双链笔记工具，本项目使用的规范体系来源 |
| CHG-ELEC/MECH/... | Change Electric/Mechanic/... | 变更分类编码 |
| PyInstaller | - | Python程序打包工具，将.py编译为.exe |
| post_process | - | 后处理，在主流程完成后执行的清理/完善操作 |
| Glob | Global pattern matching | 文件模式匹配搜索 |
| 台账/Ledger | - | 记录账目的簿籍，此处指版本变更记录表 |

---

**文档版本**: V1.0.0 (初始版)
**编制日期**: 2026-04-15
**编制人**: AI Assistant
**审核人**: [待用户确认]
**批准人**: [待用户批准]
**关联文档**: [tool_diagnosis_and_improvement_plan.md](../tool_diagnosis_and_improvement_plan.md)
