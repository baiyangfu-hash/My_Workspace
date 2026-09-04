# -*- coding: utf-8 -*-
"""
规范管理服务
"""
import uuid
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from src.models.spec import Spec
from src.dao.spec_dao import SpecDAO
from src.dao.project_dao import ProjectDAO
from src.core.constants import BusinessLine
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

BUILTIN_SPECS = [
    {
        "spec_id": "SPEC-DIR-001",
        "name": "Python项目目录结构规范",
        "category": "目录结构",
        "version": "V1.0.0",
        "content": """# Python项目目录结构规范

## 1. 标准目录结构

```
项目根目录/
├── 00_项目基础信息/          # 项目基础信息
│   └── 0-项目立项表_PROJ.md
├── 01_项目文档/              # 项目文档
│   ├── 1-需求分析文档_REQ.md
│   ├── 2-详细设计说明书_DES.md
│   └── 3-接口文档_INT.md
├── 03_主程序/                # 主程序
│   └── 01_主程序核心代码/
│       ├── src/              # 源代码
│       ├── tests/            # 测试代码
│       └── main.py           # 入口文件
├── 05_变更管理/              # 变更管理
└── 19_交付物/                # 交付物
```

## 2. 目录命名规则

- 使用中文命名，格式：`序号_功能名称`
- 序号使用两位数字，如 `01_`、`02_`
- 功能名称简洁明了，不超过10个字

## 3. 必需目录

| 目录 | 必需性 | 说明 |
|------|--------|------|
| 00_项目基础信息 | 必需 | 存放项目立项表等基础信息 |
| 01_项目文档 | 必需 | 存放项目文档 |
| 03_主程序 | 必需 | 存放源代码 |
| 05_变更管理 | 必需 | 存放变更记录 |
| 19_交付物 | 必需 | 存放交付物 |

## 4. 禁止事项

- 禁止在根目录直接放置源代码文件
- 禁止使用空格或特殊字符命名目录
- 禁止创建过深的目录层级（建议不超过4层）
""",
        "check_rules": [
            {"type": "directory", "pattern": "00_项目基础信息", "required": True},
            {"type": "directory", "pattern": "01_项目文档", "required": True},
            {"type": "directory", "pattern": "03_主程序", "required": True},
            {"type": "directory", "pattern": "05_变更管理", "required": True},
            {"type": "directory", "pattern": "19_交付物", "required": True}
        ],
        "is_active": True
    },
    {
        "spec_id": "SPEC-FILE-001",
        "name": "Python文件命名规范",
        "category": "文件命名",
        "version": "V1.0.0",
        "content": """# Python文件命名规范

## 1. Python源文件命名

- 使用小写字母
- 多个单词用下划线连接
- 示例：`project_service.py`、`user_manager.py`

## 2. 文档文件命名

- 格式：`序号-文档名称_类型前缀.md`
- 示例：`1-需求分析文档_REQ.md`

## 3. 配置文件命名

- 使用小写字母和下划线
- JSON配置：`xxx_config.json`
- 示例：`app_config.json`、`database_config.json`

## 4. 禁止事项

- 禁止使用中文命名Python源文件
- 禁止使用空格
- 禁止使用特殊字符（除下划线和中划线）
- 禁止文件名超过50个字符

## 5. 特殊文件

| 文件名 | 用途 |
|--------|------|
| `__init__.py` | Python包标识 |
| `main.py` | 程序入口 |
| `config.py` | 配置模块 |
| `constants.py` | 常量定义 |
| `utils.py` | 工具函数 |
""",
        "check_rules": [
            {"type": "filename", "pattern": "^[a-z][a-z0-9_]*\\.py$", "target": "*.py", "message": "Python文件应使用小写字母和下划线命名"},
            {"type": "filename", "pattern": "^[a-z][a-z0-9_]*_config\\.json$", "target": "*_config.json", "message": "配置文件命名不符合规范"}
        ],
        "is_active": True
    },
    {
        "spec_id": "SPEC-CODE-001",
        "name": "Python代码风格规范",
        "category": "代码风格",
        "version": "V1.0.0",
        "content": """# Python代码风格规范

## 1. 编码声明

所有Python文件开头应包含编码声明：

```python
# -*- coding: utf-8 -*-
```

## 2. 导入顺序

1. 标准库
2. 第三方库
3. 本地模块

每组导入之间空一行。

## 3. 命名规范

| 类型 | 命名风格 | 示例 |
|------|---------|------|
| 模块 | 小写下划线 | `project_service` |
| 类 | 大驼峰 | `ProjectService` |
| 函数 | 小写下划线 | `create_project` |
| 变量 | 小写下划线 | `project_name` |
| 常量 | 大写下划线 | `MAX_SIZE` |
| 私有属性 | 单下划线前缀 | `_private_var` |

## 4. 文档字符串

```python
def create_project(name: str, template: str) -> Project:
    \"\"\"
    创建新项目
    
    Args:
        name: 项目名称
        template: 模板ID
        
    Returns:
        Project: 创建的项目对象
        
    Raises:
        ValueError: 参数验证失败时抛出
    \"\"\"
    pass
```

## 5. 代码行长度

- 最大行长度：120字符
- 建议行长度：80字符

## 6. 缩进

- 使用4个空格缩进
- 禁止使用Tab

## 7. 空行规则

- 类之间空两行
- 方法之间空一行
- 函数内逻辑块之间空一行
""",
        "check_rules": [
            {"type": "content", "pattern": "# -*- coding: utf-8 -*-", "target": "*.py", "message": "Python文件应包含编码声明"},
            {"type": "content", "pattern": "^\\s{4}", "target": "*.py", "message": "应使用4个空格缩进"}
        ],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-001",
        "name": "项目文档编写规范",
        "category": "文档规范",
        "version": "V1.0.0",
        "content": """# 项目文档编写规范

## 1. 文档类型

| 文档类型 | 编号前缀 | 示例 |
|---------|---------|------|
| 项目立项表 | PROJ | 0-项目立项表_PROJ.md |
| 需求分析文档 | REQ | 1-需求分析文档_REQ.md |
| 详细设计说明书 | DES | 2-详细设计说明书_DES.md |
| 接口文档 | INT | 3-接口文档_INT.md |
| 测试用例 | TEST | 4-测试用例_TEST.md |
| 使用文档 | USE | 5-使用文档_USE.md |

## 2. 文档结构

每个文档应包含以下部分：

1. **标题**：一级标题，文档名称
2. **基本信息**：项目编号、版本、日期、作者
3. **正文**：按章节组织内容
4. **变更记录**：记录文档修改历史

## 3. Markdown格式要求

- 标题层级不超过4级
- 表格使用标准Markdown格式
- 代码块指定语言类型
- 图片使用相对路径

## 4. 版本号规则

- 格式：`V主版本.次版本.修订号`
- 示例：`V1.0.0`、`V1.0.1`、`V1.1.0`

## 5. 变更记录格式

| 日期 | 版本 | 变更类型 | 变更内容 | 变更人 |
|------|------|----------|----------|--------|
| 2026-02-19 | V1.0.0 | 新增文档 | 创建文档 | 作者名 |
""",
        "check_rules": [
            {"type": "content", "pattern": "^# .+", "target": "*.md", "message": "文档应有标题"},
            {"type": "content", "pattern": "## 变更记录", "target": "*.md", "message": "文档应包含变更记录"}
        ],
        "is_active": True
    },
    {
        "spec_id": "SPEC-GIT-001",
        "name": "Git版本控制规范",
        "category": "版本控制",
        "version": "V1.0.0",
        "content": """# Git版本控制规范

## 1. 分支命名

| 分支类型 | 命名规则 | 示例 |
|---------|---------|------|
| 主分支 | main/master | main |
| 开发分支 | develop | develop |
| 功能分支 | feature/功能名 | feature/user-auth |
| 修复分支 | fix/问题描述 | fix/login-error |
| 发布分支 | release/版本号 | release/v1.0.0 |
| 热修复分支 | hotfix/问题描述 | hotfix/critical-bug |

## 2. 提交信息格式

```
<类型>: <简短描述>

<详细描述>（可选）

<关联问题>（可选）
```

## 3. 提交类型

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复Bug |
| docs | 文档更新 |
| style | 代码格式调整 |
| refactor | 重构 |
| test | 测试相关 |
| chore | 构建/工具相关 |

## 4. 提交示例

```
feat: 添加用户登录功能

- 实现用户名密码登录
- 添加登录状态保持
- 添加登录失败提示

Closes #123
```

## 5. 禁止事项

- 禁止直接在main分支提交代码
- 禁止提交敏感信息（密码、密钥等）
- 禁止提交大型二进制文件
- 禁止无意义的提交信息
""",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-API-001",
        "name": "REST API设计规范",
        "category": "接口规范",
        "version": "V1.0.0",
        "content": """# REST API设计规范

## 1. URL设计

- 使用名词复数形式：`/api/v1/projects`
- 使用小写字母和连字符：`/api/v1/project-templates`
- 避免深层嵌套：建议不超过2层

## 2. HTTP方法

| 方法 | 用途 | 示例 |
|------|------|------|
| GET | 查询资源 | GET /api/v1/projects |
| POST | 创建资源 | POST /api/v1/projects |
| PUT | 更新资源（全量） | PUT /api/v1/projects/1 |
| PATCH | 更新资源（部分） | PATCH /api/v1/projects/1 |
| DELETE | 删除资源 | DELETE /api/v1/projects/1 |

## 3. 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

## 4. 响应格式

成功响应：
```json
{
    "code": 0,
    "message": "success",
    "data": { ... }
}
```

错误响应：
```json
{
    "code": 40001,
    "message": "参数错误",
    "errors": ["项目名称不能为空"]
}
```

## 5. 分页参数

- `page`: 页码（从1开始）
- `page_size`: 每页数量
- `sort`: 排序字段
- `order`: 排序方向（asc/desc）

## 6. 版本控制

- URL中包含版本号：`/api/v1/`
- 主版本号变更表示不兼容更新
""",
        "check_rules": [],
        "is_active": True
    },
    # ===== 文档模板类规范 (从 DEFAULT_TEMPLATES 迁移) =====
    {
        "spec_id": "SPEC-DOC-INIT-001",
        "name": "项目立项表模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 项目立项表

| 项目 | 内容 |
|------|------|
| 编号 | {project_code} |
| 名称 | {project_name} |
| 业务线 | {business_line} |
| 负责人 | {manager} |
| 日期 | {create_date} |
| 版本 | V1.0.0 |

## 设备概况
- 设备类型:
- 控制方式: PLC+HMI
- 主要工艺:

## IO概览
| DI | DO | AI | AO |
|:--:|:--:|:--:|:--:|
|   |   |   |   |
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001", "TPL-SINGLE-ROBOT-001", "TPL-UPPER-STD-001"],
        "file_path_pattern": "00_项目管理/01_立项与需求/{project_code}_项目立项表.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-REQ-001",
        "name": "需求分析文档模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 需求分析文档

## 1. 功能需求
### 1.1 主工艺功能
### 1.2 安全保护功能
### 1.3 操作模式(自动/手动/维护)

## 2. IO需求
### 2.1 输入信号(DI/AI)
### 2.2 输出信号(DO/AO)

## 3. 通讯需求
### 3.1 HMI通讯
### 3.2 上位机(预留)

## 4. 性能要求
- PLC扫描周期:
- 急停响应时间:
- 定位精度:
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001", "TPL-SINGLE-ROBOT-001", "TPL-UPPER-STD-001"],
        "file_path_pattern": "00_项目管理/01_立项与需求/{project_code}_需求分析文档.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-IO-001",
        "name": "IO分配表模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} IO分配表

## DI - 数字输入
| 地址 | 符号名 | 描述 | 模块 | 备注 |
|------|--------|------|------|------|

## DO - 数字输出
| 地址 | 符号名 | 描述 | 模块 | 备注 |
|------|--------|------|------|------|

## AI - 模拟输入
| 地址 | 范围 | 描述 | 模块 |
|------|------|------|------|

## AO - 模拟输出
| 地址 | 范围 | 描述 | 模块 |
|------|------|------|------|
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001", "TPL-SINGLE-ROBOT-001"],
        "file_path_pattern": "20_软件程序/21_PLC_Autoshop/Docs/{project_code}_IO分配表.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-PLCDESIGN-001",
        "name": "PLC程序设计总文档模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} PLC程序设计总文档

## 1. 程序架构
### OB组织块列表
### FB/FC功能块清单
### DB数据块清单

## 2. 主要功能块说明

## 3. 变量命名规范

## 4. 联锁逻辑说明
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001"],
        "file_path_pattern": "20_软件程序/21_PLC_Autoshop/Docs/{project_code}_PLC程序设计总文档.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-ARCH-001",
        "name": "系统架构设计说明书模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 系统架构设计

## 1. 硬件配置
### 1.1 CPU选型
### 1.2 IO模块清单
### 1.3 网络拓扑

## 2. 软件架构
### 2.1 程序组织
### 2.2 数据流
### 2.3 接口定义

## 3. HMI接口规划
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001"],
        "file_path_pattern": "20_软件程序/21_PLC_Autoshop/Docs/{project_code}_系统架构设计说明书.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-INTERLOCK-001",
        "name": "联锁逻辑设计说明书模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 联锁逻辑设计

## 1. 正向联锁(防堆积)
## 2. 反向联锁(故障传播)
## 3. 安全联锁
## 4. 启停顺序逻辑
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001"],
        "file_path_pattern": "20_软件程序/21_PLC_Autoshop/Docs/{project_code}_联锁逻辑设计说明书.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-EPLAN-001",
        "name": "电气图纸清单模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 电气图纸清单

## 图纸目录
| 序号 | 图纸名称 | 图纸编号 | 版本 | 状态 |
|:----:|----------|----------|:----:|:----:|

## 绘制规范
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001"],
        "file_path_pattern": "10_技术设计/11_Eplan电气/Export_PDF/{project_code}_电气图纸清单.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-HWCONFIG-001",
        "name": "PLC硬件配置表模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} PLC硬件配置表

## CPU
## IO模块
## 通讯模块
## 电源计算
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001"],
        "file_path_pattern": "10_技术设计/11_Eplan电气/Source/{project_code}_PLC硬件配置表.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-MECHBOM-001",
        "name": "机械BOM清单模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 机械BOM清单

## 标准件
## 加工件
## 外购件
## 总重估算
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001"],
        "file_path_pattern": "10_技术设计/12_机械结构/3D_Models/{project_code}_机械BOM清单.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-OPMAN-001",
        "name": "操作手册模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 操作手册

## 1. 开机前检查 (7项)
## 2. 标准开机流程
## 3. 运行状态监控
## 4. 正常停机流程
## 5. 完整关机流程
## 6. 急停操作SOP
## 7. 报警代码速查

**版本**: V1.0.0 | **编制**: {create_date}
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001", "TPL-SINGLE-ROBOT-001"],
        "file_path_pattern": "40_交付与文档/41_操作手册/{project_code}_操作手册.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-FAULT-001",
        "name": "故障排除手册模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 故障排除手册

## 诊断5步法
## PLC系统故障
## 变频器/驱动器故障
## 机械系统故障
## 传感器故障
## 维修记录
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001", "TPL-SINGLE-ROBOT-001"],
        "file_path_pattern": "40_交付与文档/45_故障排查指南/{project_code}_故障排除手册.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-MAINT-001",
        "name": "维护手册模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 维护手册

## 一级维护(每日/每周)
## 二级维护(每月)
## 三级维护(季/半年)
## 备件库存
## 维护记录
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001"],
        "file_path_pattern": "40_交付与文档/46_维护计划/{project_code}_维护手册.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-ACCEPT-001",
        "name": "验收检查表模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 验收检查表

## 文档验收 (15%)
## 安装质量 (10%)
## 安全功能 (25%, 一票否决)
## 功能性能 (35%)
## 培训效果 (15%)
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001", "TPL-SINGLE-ROBOT-001"],
        "file_path_pattern": "40_交付与文档/43_验收清单/{project_code}_验收检查表.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-TRAIN-001",
        "name": "培训记录模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 培训记录

## 培训日程
## 参训人员
## 考核成绩
## 证书发放
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001"],
        "file_path_pattern": "40_交付与文档/44_培训资料/{project_code}_培训记录.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-SUMMARY-001",
        "name": "项目总结报告模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name} 项目总结报告

## 执行概况
## 技术成果
## 成本分析
## 经验教训
## 后续建议
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001", "TPL-SINGLE-ROBOT-001"],
        "file_path_pattern": "07_交付文档/04_项目总结报告.md",
        "check_rules": [],
        "is_active": True
    },
    {
        "spec_id": "SPEC-DOC-README-001",
        "name": "项目README模板",
        "category": "文档模板",
        "version": "V1.0.0",
        "content": """# {project_name}

- **编号**: {project_code}
- **模板**: TPL-SINGLE-PLC-001 (单机设备PLC+HMI)
- **负责人**: {manager}
- **日期**: {create_date}

{description}
""",
        "applies_to_templates": ["TPL-SINGLE-PLC-001", "TPL-FULLLINE-AUTO-001", "TPL-SINGLE-ROBOT-001", "TPL-UPGRADE-STD-001", "TPL-UPPER-STD-001"],
        "file_path_pattern": "README.md",
        "check_rules": [],
        "is_active": True
    }
]

class SpecService:
    """规范管理服务类"""
    
    @staticmethod
    def initialize_builtin_specs():
        """初始化内置规范"""
        for spec_data in BUILTIN_SPECS:
            if not SpecDAO.exists(spec_data["spec_id"]):
                spec = Spec(
                    spec_id=spec_data["spec_id"],
                    name=spec_data["name"],
                    category=spec_data["category"],
                    version=spec_data["version"],
                    content=spec_data["content"],
                    check_rules=spec_data.get("check_rules", []),
                    is_active=spec_data.get("is_active", True)
                )
                SpecDAO.create(spec)
                logger.info(f"内置规范已加载: {spec.spec_id} {spec.name}")
        
        logger.info("所有内置规范初始化完成")
    
    @staticmethod
    def list_specs(category: Optional[str] = None, keyword: Optional[str] = None,
                   is_active: Optional[bool] = None) -> List[Spec]:
        """查询规范列表"""
        return SpecDAO.list_all(category=category, keyword=keyword, is_active=is_active)
    
    @staticmethod
    def get_spec(spec_id: str) -> Optional[Spec]:
        """获取规范详情"""
        return SpecDAO.get_by_id(spec_id)
    
    @staticmethod
    def create_spec(data: dict) -> tuple[Optional[Spec], str]:
        """创建规范"""
        try:
            required_fields = ["name", "category", "version", "content"]
            for field in required_fields:
                if field not in data:
                    return None, f"缺少必填字段: {field}"
            
            spec_id = data.get("spec_id") or f"SPEC-{uuid.uuid4().hex[:8]}"
            
            if SpecDAO.exists(spec_id):
                return None, f"规范ID已存在: {spec_id}"
            
            spec = Spec(
                spec_id=spec_id,
                name=data["name"],
                category=data["category"],
                version=data["version"],
                content=data["content"],
                check_rules=data.get("check_rules", []),
                is_active=data.get("is_active", True)
            )
            
            created_spec = SpecDAO.create(spec)
            logger.info(f"规范创建成功: {spec_id} {data['name']}")
            return created_spec, ""
            
        except Exception as e:
            logger.exception(f"创建规范失败: {e}")
            return None, f"创建规范失败: {str(e)}"
    
    @staticmethod
    def update_spec(spec_id: str, data: dict) -> tuple[Optional[Spec], str]:
        """更新规范"""
        try:
            spec = SpecDAO.get_by_id(spec_id)
            if not spec:
                return None, f"规范不存在: {spec_id}"
            
            if "name" in data:
                spec.name = data["name"]
            if "category" in data:
                spec.category = data["category"]
            if "version" in data:
                spec.version = data["version"]
            if "content" in data:
                spec.content = data["content"]
            if "check_rules" in data:
                spec.check_rules = data["check_rules"]
            if "is_active" in data:
                spec.is_active = data["is_active"]
            
            updated_spec = SpecDAO.update(spec)
            logger.info(f"规范更新成功: {spec_id}")
            return updated_spec, ""
            
        except Exception as e:
            logger.exception(f"更新规范失败: {e}")
            return None, f"更新规范失败: {str(e)}"
    
    @staticmethod
    def delete_spec(spec_id: str) -> tuple[bool, str]:
        """删除规范"""
        try:
            if not SpecDAO.exists(spec_id):
                return False, f"规范不存在: {spec_id}"
            
            SpecDAO.delete(spec_id)
            logger.info(f"规范删除成功: {spec_id}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"删除规范失败: {e}")
            return False, f"删除规范失败: {str(e)}"
    
    @staticmethod
    def get_spec_content(spec_id: str) -> tuple[Optional[str], str]:
        """获取规范内容"""
        spec = SpecService.get_spec(spec_id)
        if not spec:
            return None, "规范不存在"
        return spec.content, ""
    
    @staticmethod
    def get_check_rules(spec_id: str) -> tuple[Optional[list], str]:
        """获取规范检查规则"""
        spec = SpecService.get_spec(spec_id)
        if not spec:
            return None, "规范不存在"
        return spec.check_rules, ""
    
    @staticmethod
    def list_categories() -> List[str]:
        """获取所有分类"""
        return SpecDAO.list_categories()
    
    @staticmethod
    def get_quick_reference(category: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取规范速查手册"""
        specs = SpecService.list_specs(category=category, is_active=True)
        
        result = []
        for spec in specs:
            quick_ref = {
                "spec_id": spec.spec_id,
                "name": spec.name,
                "category": spec.category,
                "version": spec.version,
                "summary": SpecService._extract_summary(spec.content),
                "key_points": SpecService._extract_key_points(spec.content)
            }
            result.append(quick_ref)
        
        return result
    
    @staticmethod
    def get_project_specs(project_id: str) -> List:
        """
        获取项目的规范列表 (兼容性方法)
        
        Args:
            project_id: 项目ID（当前版本未使用，保留用于未来扩展）
            
        Returns:
            规范对象列表
        """
        return SpecService.list_specs(is_active=True)
    
    @staticmethod
    def _extract_summary(content: str) -> str:
        """提取规范摘要"""
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("## "):
                if i > 0:
                    return lines[0].replace("# ", "").strip()[:100]
        return content[:100] if content else ""
    
    @staticmethod
    def _extract_key_points(content: str) -> List[str]:
        """提取规范要点"""
        key_points = []
        lines = content.split("\n")
        
        for line in lines:
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                point = line[2:].strip()
                if len(point) > 5 and len(point) < 100:
                    key_points.append(point)
            elif line.startswith("| ") and "------" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and parts[0] not in ["类型", "状态码", "方法", "分支类型", "文档类型"]:
                    key_points.append(f"{parts[0]}: {parts[1]}")
        
        return key_points[:10]
    
    @staticmethod
    def search(keyword: str) -> List[Dict[str, Any]]:
        """搜索规范"""
        specs = SpecService.list_specs(keyword=keyword, is_active=True)
        
        result = []
        for spec in specs:
            result.append({
                "spec_id": spec.spec_id,
                "name": spec.name,
                "category": spec.category,
                "version": spec.version,
                "match_type": "name" if keyword.lower() in spec.name.lower() else "content"
            })
        
        return result

    # ==================== 规范更新感知功能 (P3) ====================

    @staticmethod
    def _compare_versions(current_version: str, latest_version: str) -> str:
        """
        比较两个版本号，返回更新类型
        
        Args:
            current_version: 当前版本号 (如 V1.0.0)
            latest_version: 最新版本号 (如 V1.1.0)
            
        Returns:
            更新类型: major/minor/patch/same
        """
        try:
            # 移除 V 前缀并分割
            current_parts = current_version.lstrip('V').split('.')
            latest_parts = latest_version.lstrip('V').split('.')
            
            if len(current_parts) >= 3 and len(latest_parts) >= 3:
                if int(latest_parts[0]) > int(current_parts[0]):
                    return "major"
                elif int(latest_parts[1]) > int(current_parts[1]):
                    return "minor"
                elif int(latest_parts[2]) > int(current_parts[2]):
                    return "patch"
            
            return "same"
        except (ValueError, IndexError):
            # 版本格式异常时，简单比较是否不同
            return "minor" if current_version != latest_version else "same"

    @staticmethod
    def check_document_updates(project_id: str) -> dict:
        """
        检查项目的文档规范更新状态
        
        Args:
            project_id: 项目ID
            
        Returns:
            {
                "check_time": "2026-04-12 14:00:00",
                "project_id": project_id,
                "updatable": [           # 可更新的文档列表
                    {
                        "file_path": "00_项目管理/01_立项与需求/xxx_项目立项表.md",
                        "spec_id": "SPEC-DOC-INIT-001",
                        "current_version": "V1.0.0",
                        "latest_version": "V1.1.0",
                        "update_type": "minor"  # major/minor/patch
                    }
                ],
                "up_to_date": [...],      # 已最新的文档列表
                "missing_specs": [...]     # 缺失规范的文档列表
            }
        """
        logger.info(f"开始检查项目文档规范更新: {project_id}")
        
        result = {
            "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project_id": project_id,
            "updatable": [],
            "up_to_date": [],
            "missing_specs": []
        }
        
        try:
            # 获取项目对象
            project = ProjectDAO.get_by_id(project_id)
            if not project:
                logger.warning(f"项目不存在: {project_id}")
                return result
            
            # 获取 document_specs 字段
            document_specs = project.document_specs or {}
            
            # 向后兼容：对于没有 document_specs 的旧项目
            if not document_specs:
                logger.info(f"项目 {project_id} 无文档规范追踪信息（可能是旧项目）")
                return result
            
            # 遍历每个文档条目
            for file_path, spec_info in document_specs.items():
                spec_id = spec_info.get("spec_id")
                current_version = spec_info.get("spec_version", "未知")
                
                if not spec_id:
                    logger.warning(f"文档 {file_path} 缺少 spec_id 信息")
                    continue
                
                # 获取当前规范版本
                latest_spec = SpecService.get_spec(spec_id)
                
                if not latest_spec:
                    # 规范已被删除
                    result["missing_specs"].append({
                        "file_path": file_path,
                        "spec_id": spec_id,
                        "current_version": current_version,
                        "message": "该规范已在规范中心被删除"
                    })
                    logger.warning(f"规范不存在(可能已删除): {spec_id}")
                    continue
                
                # 比较版本
                latest_version = latest_spec.version
                update_type = SpecService._compare_versions(current_version, latest_version)
                
                if update_type == "same":
                    # 已是最新版本
                    result["up_to_date"].append({
                        "file_path": file_path,
                        "spec_id": spec_id,
                        "current_version": current_version,
                        "latest_version": latest_version
                    })
                else:
                    # 有新版本可更新
                    result["updatable"].append({
                        "file_path": file_path,
                        "spec_id": spec_id,
                        "current_version": current_version,
                        "latest_version": latest_version,
                        "update_type": update_type
                    })
                    logger.info(f"发现可更新文档: {file_path} ({current_version} -> {latest_version}, {update_type})")
            
            # 统计日志
            total = len(result["updatable"]) + len(result["up_to_date"]) + len(result["missing_specs"])
            logger.info(f"项目 {project_id} 文档检查完成: 共{total}个文档, "
                       f"可更新{len(result['updatable'])}个, "
                       f"已最新{len(result['up_to_date'])}个, "
                       f"缺失规范{len(result['missing_specs'])}个")
            
            return result
            
        except Exception as e:
            logger.exception(f"检查项目文档更新失败: {e}")
            return result

    @staticmethod
    def _build_template_vars(project) -> dict:
        """
        从项目对象构建模板变量字典
        
        Args:
            project: Project 对象
            
        Returns:
            模板变量字典
        """
        from src.services.project_service import BUSINESS_LINE_DESC
        
        create_date = project.created_at.strftime("%Y-%m-%d") if project.created_at else datetime.now().strftime("%Y-%m-%d")
        business_line_desc = BUSINESS_LINE_DESC.get(project.business_line, project.business_line.value if hasattr(project.business_line, 'value') else str(project.business_line))
        
        template_vars = {
            "project_code": project.code,
            "project_name": project.name,
            "business_line": business_line_desc,
            "manager": project.manager or "",
            "description": project.description or "",
            "create_date": create_date,
            "template_id": project.template_id or "",
            "template_name": "",  # 需要额外获取模板名称，如果需要的话
        }
        
        # 尝试获取模板名称
        try:
            from src.dao.template_dao import TemplateDAO
            if project.template_id:
                template = TemplateDAO.get_by_id(project.template_id)
                if template:
                    template_vars["template_name"] = template.name
        except Exception as e:
            logger.debug(f"获取模板名称失败: {e}")
        
        return template_vars

    @staticmethod
    def update_project_document(project_id: str, file_relative_path: str, spec_id: str) -> tuple[bool, str]:
        """
        用最新规范内容更新项目的单个文档
        
        Args:
            project_id: 项目ID
            file_relative_path: 相对于项目根目录的文件路径
            spec_id: 要使用的规范ID
            
        Returns:
            (success, message)
        """
        logger.info(f"开始更新项目文档: project={project_id}, file={file_relative_path}, spec={spec_id}")
        
        try:
            # 1. 获取项目对象
            project = ProjectDAO.get_by_id(project_id)
            if not project:
                error_msg = f"项目不存在: {project_id}"
                logger.error(error_msg)
                return False, error_msg
            
            # 2. 获取指定 spec 的最新内容
            content, content_err = SpecService.get_spec_content(spec_id)
            if content is None:
                error_msg = f"获取规范内容失败: {content_err}"
                logger.error(error_msg)
                return False, error_msg
            
            # 3. 构建完整文件路径
            project_path = Path(project.path)
            full_file_path = project_path / file_relative_path
            
            # 检查目标目录是否存在
            target_dir = full_file_path.parent
            if not target_dir.exists():
                error_msg = f"目标目录不存在: {target_dir}"
                logger.error(error_msg)
                return False, error_msg
            
            # 4. 重建模板变量并替换占位符
            template_vars = SpecService._build_template_vars(project)
            
            try:
                formatted_content = content.format(**template_vars)
            except KeyError as e:
                # 如果有占位符无法替换，使用原始内容并记录警告
                logger.warning(f"模板变量替换失败(缺少变量 {e}), 使用原始内容: {file_relative_path}")
                formatted_content = content
            except Exception as e:
                logger.exception(f"模板格式化异常: {e}")
                formatted_content = content
            
            # 5. 写入文件（事务安全的关键步骤）
            try:
                with open(full_file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
                logger.info(f"文件写入成功: {full_file_path}")
            except IOError as e:
                error_msg = f"文件写入失败: {e}"
                logger.error(error_msg)
                return False, error_msg
            
            # 6. 更新 project.document_specs 中该文件的 version 和 updated_at
            document_specs = project.document_specs or {}
            
            if file_relative_path in document_specs:
                # 更新现有记录
                document_specs[file_relative_path]["spec_version"] = SpecService.get_spec(spec_id).version
                document_specs[file_relative_path]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                # 新增记录（正常情况下不应该发生）
                document_specs[file_relative_path] = {
                    "spec_id": spec_id,
                    "spec_version": SpecService.get_spec(spec_id).version,
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # 7. 保存到数据库
            updated_project = ProjectDAO.update(project_id, {"document_specs": document_specs})
            if not updated_project:
                # 数据库更新失败，但文件已经写入，需要回滚或警告
                error_msg = "数据库更新失败（文件已写入但元数据未更新）"
                logger.error(error_msg)
                return False, error_msg
            
            success_msg = f"文档更新成功: {file_relative_path}"
            logger.info(success_msg)
            return True, success_msg
            
        except Exception as e:
            logger.exception(f"更新项目文档异常: {e}")
            return False, f"更新文档失败: {str(e)}"

    @staticmethod
    def batch_update_documents(project_id: str, file_paths: list[str]) -> tuple[int, int, list[str]]:
        """
        批量更新多个文档
        
        Args:
            project_id: 项目ID
            file_paths: 要更新的文件相对路径列表
            
        Returns:
            (success_count, fail_count, error_messages)
        """
        logger.info(f"开始批量更新文档: project={project_id}, count={len(file_paths)}")
        
        success_count = 0
        fail_count = 0
        error_messages = []
        
        # 先检查项目的更新状态，获取每个文件对应的 spec_id
        check_result = SpecService.check_document_updates(project_id)
        
        # 构建 file_path -> spec_id 映射
        updatable_map = {}
        for item in check_result["updatable"]:
            updatable_map[item["file_path"]] = item["spec_id"]
        
        # 逐个更新文档
        for file_path in file_paths:
            # 从映射中获取 spec_id
            spec_id = updatable_map.get(file_path)
            
            if not spec_id:
                # 尝试从项目的 document_specs 中查找
                try:
                    project = ProjectDAO.get_by_id(project_id)
                    if project and project.document_specs and file_path in project.document_specs:
                        spec_id = project.document_specs[file_path].get("spec_id")
                except Exception:
                    pass
            
            if not spec_id:
                fail_count += 1
                error_msg = f"无法确定 {file_path} 对应的规范ID"
                error_messages.append(error_msg)
                logger.error(error_msg)
                continue
            
            # 执行单个文档更新
            success, message = SpecService.update_project_document(project_id, file_path, spec_id)
            
            if success:
                success_count += 1
                logger.info(f"批量更新进度 [{success_count}/{len(file_paths)}]: {file_path} 成功")
            else:
                fail_count += 1
                error_messages.append(f"{file_path}: {message}")
                logger.warning(f"批量更新失败 [{fail_count}]: {file_path} - {message}")
        
        # 总结日志
        logger.info(f"批量更新完成: project={project_id}, 成功={success_count}, 失败={fail_count}, 总计={len(file_paths)}")
        
        return success_count, fail_count, error_messages
