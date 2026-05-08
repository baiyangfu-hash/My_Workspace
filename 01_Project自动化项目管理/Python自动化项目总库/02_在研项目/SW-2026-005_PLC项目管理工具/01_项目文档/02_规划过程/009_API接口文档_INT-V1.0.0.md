# API接口文档 INT-V1.0.0

> **项目**: SW-2026-005 PLC项目管理工具
> **版本**: V1.0.0 | **日期**: 2026-05-08
> **来源**: 从 `05_docs/02_技术文档/` 迁移至标准位置

---

## 1. SettingsManager API

**模块**: `src.core.settings.SettingsManager`
**用途**: 应用级配置的读写、最近项目管理

### 1.1 初始化与加载

```python
from src.core.settings import SettingsManager

# 加载配置文件（必须在首次使用前调用）
SettingsManager.load(Path("data/settings.json"))
```

### 1.2 配置读写

```python
# 读取配置
app_name = SettingsManager.get("app_name", "PLC项目管理工具")
version = SettingsManager.get("version", "1.0.0")

# 写入配置（仅内存）
SettingsManager.set("theme", "material_light")

# 持久化到文件
SettingsManager.save()
```

### 1.3 最近项目管理

```python
# 添加最近项目（路径会自动转换为相对路径存储）
SettingsManager.add_recent_project(
    project_path="D:/Projects/DJ-2026-005",
    project_name="DJ-2026-005_边框缓存机"
)

# 获取最近项目列表（路径已解析为绝对路径）
projects = SettingsManager.get_recent_projects()
# 返回: [{"path": "D:/Projects/DJ-2026-005", name: "..."}, ...]
```

---

## 2. ProjectService API

**模块**: `src.services.project_service.ProjectService`
**用途**: 项目CRUD操作、模板应用

### 2.1 创建项目

```python
from src.services.project_service import ProjectService

project, error = ProjectService.create_project(
    name="DJ-2026-006_贴标机",
    business_line=BusinessLine.PACKAGING,
    template_id="M001",  # 或 "S001"
    manager="张三",
    description="全自动贴标生产线"
)

if project:
    print(f"项目创建成功: {project.path}")
else:
    print(f"创建失败: {error}")
```

### 2.2 打开/关闭项目

```python
# 打开项目
project = ProjectService.open_project("D:/Projects/DJ-2026-005")

# 关闭当前项目
ProjectService.close_project()
```

---

## 3. DiagnosticService API

**模块**: `src.services.diagnostic_service.DiagnosticService`
**用途**: 执行深度诊断和LSP检查

### 3.1 七维度诊断

```python
from src.services.diagnostic_service import DiagnosticService

report = DiagnosticService.run_diagnosis("D:/Projects/DJ-2026-005")

print(f"总体分数: {report.overall_score}")
for dim, score in report.dimension_scores.items():
    print(f"  {dim}: {score}")

for issue in report.issues:
    print(f"  [{issue.severity.value}] {issue.message}")
```

### 3.2 LSP兼容性检查

```python
lsp_result = DiagnosticService.run_lsp_check("D:/Projects/DJ-2026-005")
print(f"兼容性: {lsp_result.compatible}")
for risk in lsp_result.risks:
    print(f"  风险: {risk.description} (位置: {risk.file})")
```

---

## 4. DocumentService API

**模块**: `src.services.document_service.DocumentService`
**用途**: 标准文档生成

### 4.1 获取可用模板类型

```python
from src.services.document_service import DocumentService

templates = DocumentService.get_template_types()
# 返回: [{"type": "REQ", "name": "需求规格说明书", ...}, ...]
```

### 4.2 生成文档

```python
doc, error = DocumentService.generate_document(
    doc_type="REQ",                    # 文档类型
    project_path="D:/Projects/DJ-2026-005",
    doc_number="REQ-DJ-2026-006-V1.0.0",
    author="张三",
    output_dir=None                    # 默认项目Documents目录
)

if doc:
    print(f"文档生成: {doc.path}")
    print(f"预览:\n{doc.content[:200]}...")
```

---

## 5. SpecCheckerService API

**模块**: `src.services.spec_checker_service.SpecCheckerService`
**用途**: 规范检查执行

### 5.1 获取可用规则

```python
from src.services.spec_checker_service import SpecCheckerService

rules = SpecCheckerService.get_available_rules()
# 返回: [RuleInfo(id="NAM-001", name="...", severity=Severity.HIGH), ...]
```

### 5.2 执行检查

```python
report = SpecCheckerService.run_checks(
    project_path="D:/Projects/DJ-2026-005",
    rule_ids=["NAM-001", "SYN-001"]  # 可选，空则全部
)

print(f"通过: {report.passed_count}, 问题: {report.issue_count}")
for result in report.results:
    if not result.passed:
        print(f"  [{result.rule_id}] {result.file}:{result.line} - {result.message}")
```

---

## 6. EventBus 信号清单

**模块**: `src.core.event_bus.EventBus`
**用途**: 跨组件事件通信

### 6.1 订阅示例

```python
from src.core.event_bus import EventBus

bus = EventBus.instance()

# 连接信号槽
bus.project_opened.connect(on_project_opened)
bus.check_completed.connect(on_check_done)
bus.diagnostic_completed.connect(on_diagnosis_done)

def on_project_opened(path: str):
    print(f"项目已打开: {path}")

def on_check_done(report):
    print(f"检查完成，发现 {len(report.results)} 个问题")
```

### 6.2 发送信号

```python
bus = EventBus.instance()
bus.project_selected.emit("/path/to/project")
bus.check_started.emit()
```

---

## 7. PathResolver API (工具层)

**模块**: `src.utils.path_resolver.PathResolver`
**用途**: 路径规范化与解析（策略模式）

### 7.1 基本使用

```python
from src.utils.path_resolver import PathResolver, RelativePathStrategy, get_default_resolver

resolver = PathResolver(RelativePathStrategy())

# 规范化（绝对→相对）
relative = resolver.normalize(
    raw_path="D:/Projects/DJ-2026-005",
    base_path=Path("data/")  # settings.json所在目录
)
# 返回: "../../../Projects/DJ-2026-005"

# 解析（相对→绝对）
absolute = resolver.resolve(
    stored_path="../../../Projects/DJ-2026-005",
    base_path=Path("data/")
)
# 返回: "D:/Projects/DJ-2026-005" (如果存在)
```

### 7.2 使用默认单例

```python
from src.utils.path_resolver import get_default_resolver

resolver = get_default_resolver()
# 默认使用 RelativePathStrategy
```

---

*文档版本: INT-V1.0.0 | 最后更新: 2026-05-08*
*迁移记录: 2026-05-08 从 `05_docs/02_技术文档/` 迁移至本标准位置*
