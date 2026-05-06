# 修复模板占位符替换Bug + 变更管理结构完善 Spec

## Why

**P0 严重Bug**: Python项目管理工具 V2.4.0 在创建新项目时，模板文件路径中的 `{project_code}` 占位符未被正确替换，导致生成14个包含未替换占位符的文件名（如 `{project_code}_项目立项表.md` 而非 `DJ-2026-001_项目立项表.md`）。

**P1 重要缺陷**: TPL-SINGLE-PLC-001 等内置模板的变更管理目录结构不完整，仅包含3个子目录（CHG-PLC/CHG-SCPT/CHG-DOCU），缺少 Obsidian 规范 043_PM-V2.1.0 要求的4个子目录（CHG-ELEC/CHG-MECH/CHG-HMI/CHG-SAFE）及版本变更台帐和根目录README。

## What Changes

### Bug修复（P0）

- **修改文件**: `src/services/project_service.py`
- **修改位置**: `create_project()` 方法（第231-261行）和 `change_template()` 方法（第709-750行）
- **修改内容**: 在生成文件路径时，对 `file_def["path"]` 执行变量替换
- **影响范围**: 所有使用内置模板创建的新项目
- **向后兼容**: ✅ 完全兼容，仅修复Bug不影响已有功能

### 模板结构更新（P1）

- **修改文件**: `src/core/constants.py`
- **修改位置**: `DEFAULT_TEMPLATES` 列表中的 `TPL-SINGLE-PLC-001`, `TPL-FULLLINE-AUTO-001`, `TPL-SINGLE-ROBOT-001`
- **修改内容**: 
  - 补全变更管理目录结构（添加 CHG-ELEC/CHG-MECH/CHG-HMI/CHG-SAFE）
  - 添加版本变更台帐模板文件
  - 添加变更管理根目录 README.md
- **影响范围**: 新建项目将自动获得完整的变更管理目录结构
- **向后兼容**: ⚠️ 结构性变更，旧项目需手动补全或使用迁移脚本

## Impact

- Affected specs: 无（这是工具本身的修复）
- Affected code:
  - `src/services/project_service.py` - 核心修改（2处）
  - `src/core/constants.py` - 模板定义修改（3个模板）
- 测试影响: 需要回归测试所有模板创建场景

## ADDED Requirements

### Requirement: P0-BugFix-001 模板文件路径占位符替换

The system SHALL replace all template variables in file paths (not just file contents) when creating a new project.

#### Scenario: Success case - 创建DJ类型项目
- **WHEN** 用户创建一个 DJ 类型项目，项目编号为 "DJ-2026-001"
- **THEN** 系统生成的文件名应为 "DJ-2026-001_项目立项表.md" 而非 "{project_code}_项目立项表.md"
- **AND** Glob 搜索 "*{project_code}* 应返回 0 个结果

#### Scenario: Success case - 创建SW类型项目
- **WHEN** 用户创建一个 SW 类型项目，项目编号为 "SW-2026-005"
- **THEN** 所有模板文件的 {project_code}, {project_name} 等占位符均被正确替换

### Requirement: P1-TplUpdate-001 变更管理目录完整性

The system SHALL generate complete change management directory structure per Obsidian spec 043_PM-V2.1.0 when creating projects with affected templates.

#### Scenario: Success case - TPL-SINGLE-PLC-001 完整性检查
- **WHEN** 使用 TPL-SINGLE-PLC-001 模板创建项目
- **THEN** 项目应包含以下变更管理子目录:
  - CHG-ELEC (电气设计类)
  - CHG-MECH (机械结构类)
  - CHG-PLC (PLC程序类) [已有]
  - CHG-HMI (HMI程序类) [新增]
  - CHG-SCPT (脚本工具类) [已有]
  - CHG-DOCU (文档类) [已有]
  - CHG-SAFE (安全功能类) [新增]
- **AND** 包含版本变更台帐文件 "{project_code}_版本变更台帐.md"
- **AND** 包含变更管理根目录 README.md

## MODIFIED Requirements

### Requirement: MOD-001 create_project() 方法增强

**原有行为**:
```python
file_path = project_path / file_def["path"]  # 未替换路径中的占位符
```

**修改后行为**:
```python
# 先替换路径中的占位符
resolved_path = file_def["path"]
for var_name, var_value in template_vars.items():
    resolved_path = resolved_path.replace(f"{{{var_name}}}", str(var_value))
file_path = project_path / resolved_path  # 路径已正确替换
```

**修改位置**:
1. `create_project()` 方法 - 第233行附近
2. `change_template()` 方法 - 第711行附近（相同逻辑）

### Requirement: MOD-002 DEFAULT_TEMPLATES 常量更新

**TPL-SINGLE-PLC-001 structure 字段新增**:
```python
{"path": "00_项目管理/04_变更管理/01_变更单/CHG-ELEC", "required": False, "description": "电气设计类变更"},
{"path": "00_项目管理/04_变更管理/01_变更单/CHG-MECH", "required": False, "description": "机械结构类变更"},
{"path": "00_项目管理/04_变更管理/01_变更单/CHG-HMI", "required": False, "description": "HMI程序类变更"},
{"path": "00_项目管理/04_变更管理/01_变更单/CHG-SAFE", "required": False, "description": "安全功能类变更"},
{"path": "00_项目管理/04_变更管理/{project_code}_版本变更台帐.md", ...},
{"path": "00_项目管理/04_变更管理/README.md", ...},
```

**同步更新**: TPL-FULLLINE-AUTO-001, TPL-SINGLE-ROBOT-001

---

## 技术细节

### Bug根因分析

**问题代码** (`project_service.py:231-261`):
```python
for file_def in template.templates:
    file_path = project_path / file_def["path"]  # ❌ 第233行：直接使用原始path
    
    # ... 内容替换逻辑（第245-256行）✅ 正确
    content = file_def["content"].format(**template_vars)
    
    with open(file_path, "w", encoding="utf-8") as f:  # ❌ 第259行：写入未替换的路径
        f.write(content)
```

**模板定义** (`constants.py:403`):
```python
{
    "path": "00_项目管理/01_立项与需求/{project_code}_项目立项表.md",  # path含占位符
    "content": "# {project_name} 项目立项表\n\n...",  # content也有占位符
}
```

**结果**: content被正确替换，但path未被替换 → 文件名保留 {project_code}

### 修复方案

在 `project_service.py` 中添加路径解析逻辑：

```python
def _resolve_template_path(file_def: dict, template_vars: dict) -> Path:
    """解析模板文件路径，替换其中的占位符"""
    raw_path = file_def.get("path", "")
    
    # 替换所有模板变量
    resolved_path = raw_path
    for var_name, var_value in template_vars.items():
        placeholder = f"{{{var_name}}}"
        if placeholder in resolved_path:
            resolved_path = resolved_path.replace(placeholder, str(var_value))
    
    return Path(resolved_path)
```

然后在 `create_project()` 和 `change_template()` 中调用此函数替代原来的 `file_path = project_path / file_def["path"]`

### 版本规划

| 版本 | 类型 | 内容 | 发布时间 |
|:----:|:----:|-----|:--------:|
| **V2.4.1** | 补丁版 | 仅修复P0 Bug（路径占位符替换） | 本次 |
| **V2.5.0** | 次版本 | P1模板结构更新+规范对齐 | 下次 |

---

**文档版本**: V1.0.0
**编制日期**: 2026-04-15
**编制人**: AI Assistant
**关联文档**: 
- [tool_diagnosis_and_improvement_plan.md](../../documents/tool_diagnosis_and_improvement_plan.md)
- [tool_iteration_execution_plan_V2.4.1-V2.5.0.md](../../documents/tool_iteration_execution_plan_V2.4.1-V2.5.0.md)
