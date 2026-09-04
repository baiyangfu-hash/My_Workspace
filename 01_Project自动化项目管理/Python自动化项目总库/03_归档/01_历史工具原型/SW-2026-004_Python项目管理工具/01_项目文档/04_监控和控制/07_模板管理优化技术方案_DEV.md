# 模板管理模块优化技术方案

**文档版本**：DEV V2.8.0
**编制日期**：2026-06-14
**编制人**：技术负责人
**对应项目**：SW-2026-004 Python项目管理工具

## 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 |
|--------|----------|--------|----------|
| DEV V2.8.0 | 初始创建：模板数据外置、服务解耦、ID生成改进、版本管理、继承机制 | 技术负责人 | 2026-06-14 |

## 1. 背景与目标

### 1.1 现状问题

| 编号 | 问题 | 严重度 | 影响 |
|------|------|--------|------|
| TPL-01 | 内置模板数据硬编码在 `_template_constants.py`（443行Python字典），修改模板需改代码重启应用 | P0 | 维护成本高，用户无法自定义内置模板 |
| TPL-02 | `ProjectService` 直接调用 `TemplateDAO`，`ReportService` 用 `__import__` 动态导入 `TemplateService`，违反分层原则 | P1 | 耦合度高，DAO变更会波及多个Service |
| TPL-03 | 模板ID自生成用 `TPL-{count+1:03d}`，删除后再创建会ID冲突 | P1 | 数据不一致 |
| TPL-04 | 模板无版本管理，内置模板更新后已创建项目无法感知变更 | P2 | 项目结构过时无法升级 |
| TPL-05 | 5个内置模板80%结构重复，无法复用公共部分 | P2 | 维护冗余 |

### 1.2 优化目标

- **高内聚**：模板相关逻辑全部收敛到 `TemplateService`，外部模块通过 Service 层统一访问
- **低耦合**：模板数据与代码分离，Service 间通过接口调用而非直接访问 DAO
- **可维护**：模板数据外置为 YAML 文件，修改无需改代码
- **可演进**：支持模板版本管理和继承派生

### 1.3 不做的事

- 不改 PyQt5（保留 PyQt5，PySide6 迁移声明作废）
- 不做模板市场/在线共享（V3.0+ 范畴）
- 不做拖拽式结构编辑器（V3.0+ 范畴）
- 不改 Template 数据库表核心字段（仅新增字段，不删不改已有字段）

## 2. 技术方案

### 2.1 TPL-01：内置模板数据外置

#### 2.1.1 方案

将 `_template_constants.py` 中的 5 个内置模板字典迁移到 `config/templates/` 目录下的 YAML 文件：

```
config/
├── templates/                    # 新增：模板数据目录
│   ├── TPL-FULLLINE-AUTO-001.yaml    # 自动化整线项目
│   ├── TPL-SINGLE-ROBOT-001.yaml     # 单机设备(机器人)
│   ├── TPL-SINGLE-PLC-001.yaml       # 单机设备(PLC+HMI)
│   ├── TPL-PYTHON-001.yaml           # Python自动化项目
│   ├── TPL-PYTHON-SIMPLE-001.yaml    # Python简单脚本
│   └── README.md                     # 模板文件格式说明
```

#### 2.1.2 YAML 文件格式

```yaml
# TPL-FULLLINE-AUTO-001.yaml
id: TPL-FULLLINE-AUTO-001
name: 自动化整线项目
version: V1.0.0
schema_version: "1.0"          # 新增：模板结构版本
compiler: Step7/TIA Portal + Python
scene: 多PLC协同自动化整线项目
description: 包含PLC、HMI、机器人、上位机、Eplan电气、机械设计、通讯协议的完整整线结构
is_builtin: true
business_lines: [ZD, DJ]
base_template_id: null         # 新增：继承自哪个模板

structure:
  - path: 00_项目管理/01_立项与需求
    required: true
    description: 立项表、需求分析
  - path: 00_项目管理/02_进度与风险
    required: true
    description: 进度计划、风险管理
  # ...

templates:
  - path: .gitignore
    type: config
    content: |
      # PLC Project
      *.zap
      *.bak
  - path: README.md
    type: document
    spec_id: SPEC-DOC-README-001
    content: |
      # {project_name}
      ## 项目信息
      - **编号**: {project_code}
  # ...
```

#### 2.1.3 加载机制

`TemplateService.initialize_builtin_templates()` 改为：

```python
# 伪代码
class TemplateService:
    TEMPLATE_DIR = Path(__file__).parent.parent.parent / "config" / "templates"

    @staticmethod
    def _load_builtin_templates_from_yaml() -> list[dict]:
        """从 config/templates/ 目录加载所有内置模板 YAML 文件"""
        templates = []
        for yaml_file in sorted(TEMPLATE_DIR.glob("TPL-*.yaml")):
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                data["_source_file"] = yaml_file.name  # 记录来源
                templates.append(data)
        return templates

    @staticmethod
    def initialize_builtin_templates():
        """初始化内置模板到数据库（从YAML加载）"""
        builtin_templates = TemplateService._load_builtin_templates_from_yaml()
        # ... 后续逻辑与现有相同，只是数据源从 DEFAULT_TEMPLATES 常量改为 YAML
```

#### 2.1.4 `_template_constants.py` 处理

- 保留文件作为 re-export 入口（保持 `from src.core.constants import DEFAULT_TEMPLATES` 的兼容性）
- `DEFAULT_TEMPLATES` 改为运行时从 YAML 加载的懒加载属性
- 后续版本可废弃此常量

### 2.2 TPL-02：ProjectService 解耦

#### 2.2.1 当前问题

```python
# project_service.py - 直接访问 TemplateDAO
template = self.template_dao.get_by_id(template_id)

# report_service.py - 动态导入
template_service = __import__('src.services.template_service', fromlist=['TemplateService']).TemplateService
```

#### 2.2.2 方案

**ProjectService**：
- 移除 `self.template_dao = template_dao or TemplateDAO`
- 所有模板访问改为 `TemplateService.get_template(template_id)`
- 新增 `TemplateService.get_template_for_project(template_id)` 方法，封装模板获取+默认值逻辑

**ReportService**：
- 移除 `__import__` 动态导入
- 改为正常 `from src.services.template_service import TemplateService`

#### 2.2.3 变更清单

| 文件 | 变更内容 |
|------|----------|
| `project_service.py` | 移除 `template_dao` 依赖，改用 `TemplateService` |
| `report_service.py` | 移除 `__import__`，改为正常 import |
| `template_service.py` | 新增 `get_template_for_project()` 方法 |

### 2.3 TPL-03：模板 ID 生成改进

#### 2.3.1 当前问题

```python
count = TemplateDAO.count()
template_id = f"TPL-{count + 1:03d}"
# 删除 TPL-002 后，count=4，下一个是 TPL-005
# 但如果 TPL-005 已存在，就会冲突
```

#### 2.3.2 方案

自定义模板 ID 格式改为：`TPL-CUSTOM-{YYYYMMDD}-{4位随机hex}`

```python
import uuid
from datetime import datetime

def _generate_template_id() -> str:
    """生成唯一模板ID"""
    date_str = datetime.now().strftime("%Y%m%d")
    short_id = uuid.uuid4().hex[:4].upper()
    return f"TPL-CUSTOM-{date_str}-{short_id}"
```

- 内置模板保持原有 ID 格式（`TPL-FULLLINE-AUTO-001` 等）
- 自定义模板使用新格式，天然避免冲突
- 用户创建时仍可手动指定 ID，自动生成时使用新格式

### 2.4 TPL-04：模板版本管理

#### 2.4.1 数据模型变更

Template 模型新增字段：

```python
class Template(BaseModel):
    # ... 现有字段不变 ...
    schema_version = Column(String(10), default="1.0", comment="模板结构版本号")
```

Project 模型新增字段：

```python
class Project(BaseModel):
    # ... 现有字段不变 ...
    applied_template_version = Column(String(20), comment="创建时应用的模板版本")
```

#### 2.4.2 版本比较逻辑

```python
class TemplateService:
    @staticmethod
    def check_template_updates(project: Project) -> dict:
        """检查项目所用模板是否有更新版本"""
        template = TemplateService.get_template(project.template_id)
        if not template:
            return {"has_update": False, "reason": "模板不存在"}

        current = project.applied_template_version or "1.0"
        latest = template.schema_version or "1.0"

        if current < latest:
            return {
                "has_update": True,
                "current_version": current,
                "latest_version": latest,
                "template_name": template.name,
                "diff": TemplateService._diff_template_versions(current, latest)
            }
        return {"has_update": False, "current_version": current, "latest_version": latest}
```

#### 2.4.3 数据库迁移

新增 Alembic 迁移脚本：
- `templates` 表新增 `schema_version` 列（VARCHAR(10), DEFAULT '1.0'）
- `projects` 表新增 `applied_template_version` 列（VARCHAR(20), NULL）
- 已有内置模板回填 `schema_version = '1.0'`
- 已有项目回填 `applied_template_version = '1.0'`

### 2.5 TPL-05：模板继承/派生机制

#### 2.5.1 数据模型变更

Template 模型新增字段：

```python
class Template(BaseModel):
    # ... 现有字段不变 ...
    base_template_id = Column(String(32), nullable=True, comment="继承的父模板ID")
```

#### 2.5.2 继承合并逻辑

子模板只需定义差异部分，运行时与父模板合并：

```python
class TemplateService:
    @staticmethod
    def resolve_template(template_id: str) -> Optional[dict]:
        """解析模板（含继承合并）"""
        template = TemplateDAO.get_by_id(template_id)
        if not template:
            return None

        result = template.to_dict()

        # 如果有父模板，递归合并
        if template.base_template_id:
            parent = TemplateService.resolve_template(template.base_template_id)
            if parent:
                result = TemplateService._merge_templates(parent, result)

        return result

    @staticmethod
    def _merge_templates(base: dict, override: dict) -> dict:
        """合并父子模板"""
        # structure: 子模板的 path 合并到父模板，同名 path 覆盖
        base_paths = {s["path"]: s for s in base.get("structure", [])}
        for s in override.get("structure", []):
            base_paths[s["path"]] = s  # 同路径覆盖，新路径追加

        # templates: 子模板的 path 合并到父模板，同名 path 覆盖
        base_files = {t["path"]: t for t in base.get("templates", [])}
        for t in override.get("templates", []):
            base_files[t["path"]] = t

        merged = {**base, **override}  # 顶层字段子覆盖父
        merged["structure"] = sorted(base_paths.values(), key=lambda x: x["path"])
        merged["templates"] = sorted(base_files.values(), key=lambda x: x["path"])
        merged["base_template_id"] = override.get("base_template_id")  # 保留继承链

        return merged
```

#### 2.5.3 GUI 变更

`TemplateEditorDialog` 新增：
- "继承自" 下拉框，列出所有已有模板
- 选择父模板后，自动展示合并预览（父模板结构 + 子模板差异高亮）
- 保存时只存储差异部分

#### 2.5.4 数据库迁移

- `templates` 表新增 `base_template_id` 列（VARCHAR(32), NULL, FK→templates.template_id）
- 已有内置模板 `base_template_id = NULL`

## 3. 实施计划

### 3.1 分阶段实施

| 阶段 | 内容 | 涉及文件 | 依赖 |
|------|------|----------|------|
| Phase 1 | 模板数据外置（YAML） | `_template_constants.py`, `template_service.py`, 新增 `config/templates/*.yaml` | 无 |
| Phase 2 | ProjectService 解耦 | `project_service.py`, `report_service.py`, `template_service.py` | Phase 1 |
| Phase 3 | 模板 ID 生成改进 | `template_service.py` | Phase 2 |
| Phase 4 | 模板版本管理 | `template.py`, `project.py`, 新增 Alembic 迁移, `template_service.py` | Phase 3 |
| Phase 5 | 模板继承机制 | `template.py`, 新增 Alembic 迁移, `template_service.py`, `template_editor.py` | Phase 4 |

### 3.2 向后兼容

- Phase 1-3：无数据库变更，纯代码重构，完全向后兼容
- Phase 4-5：新增数据库列（nullable），已有数据自动回填，无破坏性变更
- `DEFAULT_TEMPLATES` 常量保持可用（懒加载代理），所有现有 import 路径不变

### 3.3 验证标准

| 阶段 | 验证项 |
|------|--------|
| Phase 1 | YAML 加载 = 原 Python 常量数据；内置模板初始化正常；导入导出正常 |
| Phase 2 | ProjectService 不再 import TemplateDAO；ReportService 不再使用 __import__ |
| Phase 3 | 创建/删除/再创建模板，ID 不冲突 |
| Phase 4 | schema_version 字段可读写；项目可查询模板更新状态 |
| Phase 5 | 子模板继承父模板后结构正确合并；GUI 可选择父模板 |

## 4. 风险评估

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| YAML 解析性能（5个文件） | 低 | 低 | 文件数少，首次加载后缓存到数据库 |
| 继承链循环引用 | 中 | 中 | 合并时检测循环，限制最大深度3层 |
| 数据库迁移失败 | 低 | 高 | 迁移脚本先 dry-run，新增列均为 nullable |
| 用户已有自定义模板无 schema_version | 低 | 低 | 默认值 '1.0'，不影响现有功能 |
