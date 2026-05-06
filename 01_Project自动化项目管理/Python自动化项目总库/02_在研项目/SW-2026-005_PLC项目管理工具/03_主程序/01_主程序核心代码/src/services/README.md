# Service 层接口说明

## 模块概述

Service层是项目的业务逻辑核心，负责处理所有数据操作和业务规则。采用面向服务架构(SOA)设计，每个Service类对应一个业务领域。

**职责边界**:
- 数据的CRUD操作 (Create, Read, Update, Delete)
- 业务规则的验证和执行
- 与Model层和Parser层的协调
- 通过EventBus响应UI层请求（间接）

---

## 模块结构

```
src/services/
├── __init__.py              # 模块初始化
├── project_service.py       # 项目管理服务
├── document_service.py      # 文档管理服务
├── template_service.py      # 模板管理服务
├── plc_service.py           # PLC相关服务
├── hmi_service.py           # HMI相关服务
├── variable_service.py      # 变量管理服务
└── spec_service.py          # 规范检查服务
```

---

## 公共API列表

### 1. ProjectService (项目管理服务)

**文件**: `project_service.py`

```python
class ProjectService:
    """项目管理服务 - 负责PLC项目的创建、加载、查询和管理"""
    
    @classmethod
    def initialize(cls):
        """初始化服务 (加载已有项目列表)"""
    
    @classmethod
    def create_project(cls, project_data: dict) -> tuple:
        """
        创建新项目
        
        Args:
            project_data: 项目数据字典
            
        Returns:
            tuple: (Project对象 | None, 错误消息 | None)
        """
    
    @classmethod
    def load_project_from_path(cls, path: str) -> tuple:
        """
        从路径加载项目
        
        Args:
            path: 项目根目录路径
            
        Returns:
            tuple: (Project对象 | None, 错误消息 | None)
        """
    
    @classmethod
    def get_all_projects(cls) -> list:
        """
        获取所有项目列表
        
        Returns:
            list[Project]: 项目对象列表
        """
    
    @classmethod
    def get_project_by_id(cls, project_id: str) -> Project | None:
        """
        根据ID查询项目
        
        Args:
            project_id: 项目编号 (如 DJ-2026-006)
            
        Returns:
            Project | None: 项目对象或None
        """
    
    @classmethod
    def delete_project(cls, project_id: str) -> bool:
        """
        删除项目
        
        Args:
            project_id: 项目编号
            
        Returns:
            bool: 是否删除成功
        """
```

---

### 2. TemplateService (模板管理服务)

**文件**: `template_service.py`

```python
class TemplateService:
    """模板管理服务 - 管理PLC项目模板的加载和应用"""
    
    _templates: dict = {}  # 模板缓存
    
    @classmethod
    def initialize_builtin_templates(cls):
        """初始化内置模板 (M001完整版 + S001精简版)"""
    
    @classmethod
    def get_template(cls, template_id: str) -> dict | None:
        """
        获取模板数据
        
        Args:
            template_id: 模板ID (如 TPL-SINGLE-PLC-M001)
            
        Returns:
            dict | None: 模板数据字典或None
        """
    
    @classmethod
    def get_all_templates(cls) -> list:
        """
        获取所有可用模板列表
        
        Returns:
            list[dict]: 模板信息列表
        """
    
    @classmethod
    def validate_template(cls, template_id: str) -> tuple:
        """
        验证模板有效性
        
        Args:
            template_id: 模板ID
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
```

---

### 3. DocumentService (文档管理服务)

**文件**: `document_service.py`

```python
class DocumentService:
    """文档管理服务 - 负责项目文档的CRUD操作"""
    
    @classmethod
    def create_document(cls, project_path: str, doc_type: str, data: dict) -> tuple:
        """
        创建新文档
        
        Args:
            project_path: 项目根路径
            doc_type: 文档类型 (如 'REQ', 'DSN', 'IO')
            data: 文档元数据
            
        Returns:
            tuple: (Document对象 | None, 错误消息 | None)
        """
    
    @classmethod
    def load_document(cls, file_path: str) -> Document | None:
        """从文件路径加载文档"""
    
    @classmethod
    def save_document(cls, document: Document) -> bool:
        """保存文档到文件"""
    
    @classmethod
    def get_documents_by_project(cls, project_path: str) -> list:
        """获取项目的所有文档列表"""
    
    @classmethod
    def delete_document(cls, file_path: str) -> bool:
        """删除文档"""
```

---

### 4. VariableService (变量管理服务)

**文件**: `variable_service.py`

```python
class VariableService:
    """变量管理服务 - 负责PLC变量的检查、解析和管理"""
    
    @classmethod
    def check_variables(cls, st_file_paths: list[str]) -> dict:
        """
        检查变量问题
        
        Args:
            st_file_paths: ST文件路径列表
            
        Returns:
            dict: {
                'errors': [...],      # 错误列表
                'warnings': [...],    # 警告列表
                'statistics': {...}   # 统计信息
            }
        """
    
    @classmethod
    def parse_st_file(cls, file_path: str) -> list:
        """解析ST文件提取变量声明"""
    
    @classmethod
    def check_naming_conventions(cls, variables: list) -> list:
        """检查变量命名规范"""
    
    @classmethod
    def find_duplicate_variables(cls, variables: list) -> list:
        """查找重复变量"""
```

---

### 5. PLCHMISpecService (PLC/HMI/规范服务)

这些服务将在后续Phase实现，当前为占位符:

- **PLCService**: ST代码生成、语法检查、FB文档生成
- **HMIService**: HMI变量映射、报警配置、界面生成
- **SpecService**: 801规范校验、文档规范检查

---

## 依赖关系

### 上游依赖 (导入的模块)

| 模块层 | 用途 |
|--------|------|
| `src.models.*` | 数据模型定义 (Project, Document, Variable等) |
| `src.parsers.*` | 文件解析器 (ST解析、变量解析等) |
| `src.core.project` | Project核心类 |
| `src.core.settings` | 配置读取 |
| `src.utils.file_utils` | 文件操作工具 |
| `src.utils.validators` | 数据验证工具 |

### 下游依赖 (使用本层的模块)

| 模块层 | 用途 |
|--------|------|
| `src.ui.*` | UI层通过EventBus间接调用 |
| `src.ui.dialogs.*` | 对话框直接调用 (如NewProjectDialog) |
| `src.ui.managers.*` | Manager层间接调用 |

---

## EventBus 信号交互

### Service层发射的信号

当前版本Service层不直接发射信号，而是返回结果给调用者。

**推荐模式** (后续Phase优化):
```python
# UI层调用Service后手动发射信号
result = ProjectService.create_project(data)
if result[0]:
    event_bus.project_created.emit(result[0].path)
```

### Service层监听的信号

当前版本未直接监听信号（被动响应模式）。

---

## 设计原则

### 1. 类方法模式 (Class Method Pattern)
- 所有Service使用 `@classmethod`，无需实例化
- 便于全局访问和测试Mock
- 避免循环依赖问题

### 2. 返回值约定
- **成功**: `(Object, None)` 或 `True`
- **失败**: `(None, "错误消息")` 或 `False`
- **列表操作**: 返回 `list` 或空列表 `[]`

### 3. 异常处理原则
- Service层捕获所有异常并转换为返回值
- 不向上抛出异常，保证UI层稳定
- 关键错误记录日志便于排查

### 4. 数据验证
- 所有输入参数在Service入口处验证
- 使用 `src/utils/validators.py` 统一验证逻辑
- 无效数据立即返回错误，不继续执行

---

## 扩展指南

### 添加新的Service

1. 创建新文件 `src/services/xxx_service.py`
2. 定义类并继承基本模式
3. 实现必要的 CRUD 方法
4. 在 `__init__.py` 中导出
5. 编写单元测试

示例骨架:
```python
# src/services/new_service.py
from typing import Optional, Tuple, List
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class NewService:
    """新服务 - 简要描述"""
    
    @classmethod
    def initialize(cls):
        """初始化服务"""
        pass
    
    @classmethod
    def create(cls, data: dict) -> Tuple[Optional[object], Optional[str]]:
        """
        创建资源
        
        Args:
            data: 输入数据
            
        Returns:
            Tuple[对象 | None, 错误消息 | None]
        """
        try:
            # 业务逻辑
            return result, None
        except Exception as e:
            logger.exception(f"创建失败: {e}")
            return None, str(e)
    
    # ... 其他方法
```

---

## 注意事项

1. **线程安全**: Service可能被多线程调用，注意共享数据的锁机制
2. **性能优化**: 大量数据操作时考虑分页或异步处理
3. **事务一致性**: 涉及多步操作时确保原子性（全部成功或全部回滚）
4. **日志记录**: 所有关键操作必须记录日志（INFO级别）
5. **错误隔离**: 单个项目错误不应影响其他项目

---

## 测试策略

每个Service应有对应的单元测试:
- 文件位置: `tests/test_xxx_service.py`
- 测试框架: `pytest`
- 覆盖率目标: > 80%

测试要点:
- 正常流程测试
- 边界值测试
- 异常输入测试
- 并发安全测试 (如适用)

---

## 版本历史

- **v1.0.0** (Phase 0): 初始版本
  - ProjectService: 基本项目CRUD
  - TemplateService: 内置模板管理
  - DocumentService: 基础文档操作
  - VariableService: 变量检查框架
