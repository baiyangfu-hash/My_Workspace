# Python编程规范

## 1. 文档基础信息

**文档标题**：Python编程规范
**文档版本**：V1.1.0
**编制日期**：2026-01-15
**编制人**：文档专家
**审核人**：[审核人姓名]

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 | 详细说明 |
|--------|----------|--------|----------|----------|
| [V1.1.0](1-Python编程规范_DEV-V1.1.0.md#L[详细变更行号]) | 增强 | Trae | 2026-04-25 | 基于SW-2026-004项目实践新增: Service层架构模式、常量集中管理规范、UI组件化开发规范 |
| [V1.0.0](1-Python编程规范_DEV-V1.0.0.md#L[详细变更行号]) | 初始版本 | 文档专家 | 2026-01-15 | [查看详细变更](1-Python编程规范_DEV-V1.0.0.md#L[详细变更行号]) |

## 3. 范围

本规范适用于所有Python项目的代码开发，旨在确保代码的一致性、可读性和可维护性。

## 4. 命名规范

### 4.1 变量命名

- **局部变量**：使用小写字母，单词之间用下划线分隔（snake_case）
- **全局变量**：使用大写字母，单词之间用下划线分隔（SNAKE_CASE）
- **常量**：使用大写字母，单词之间用下划线分隔（SNAKE_CASE）

### 4.2 函数命名

- 使用小写字母，单词之间用下划线分隔（snake_case）
- 函数名应清晰描述函数的功能

### 4.3 类命名

- 使用驼峰命名法（CamelCase）
- 类名应使用名词或名词短语

### 4.4 模块命名

- 使用小写字母，单词之间用下划线分隔（snake_case）
- 模块名应简洁明了，避免使用缩写

### 4.5 包命名

- 使用小写字母，单词之间用下划线分隔（snake_case）
- 包名应简洁明了，避免使用缩写

## 5. 代码风格

### 5.1 缩进

- 使用4个空格进行缩进
- 不要使用制表符（Tab）

### 5.2 行长度

- 每行代码长度不超过79个字符
- 长行应适当换行，保持代码的可读性

### 5.3 空行

- 在函数和类定义之间使用两个空行
- 在函数内部的逻辑块之间使用一个空行

### 5.4 空格

- 在运算符两侧添加空格
- 在逗号、冒号后添加空格
- 不要在括号内添加空格

### 5.5 注释

- 使用#进行单行注释
- 使用""" """进行多行注释
- 注释应清晰描述代码的功能和逻辑
- 避免不必要的注释

## 6. 代码结构

### 6.1 模块结构

```python
# 模块说明
"""
模块功能描述
"""

# 导入模块
import module1
import module2

# 全局变量
GLOBAL_VARIABLE = value

# 类定义
class ClassName:
    """类的描述"""
    
    def __init__(self, param1, param2):
        """初始化方法"""
        self.param1 = param1
        self.param2 = param2
    
    def method(self):
        """方法描述"""
        pass

# 函数定义
def function_name(param1, param2):
    """函数描述"""
    pass

# 主函数
if __name__ == "__main__":
    pass
```

### 6.2 函数结构

```python
def function_name(param1, param2):
    """函数描述
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述
    
    Returns:
        返回值的描述
    """
    # 函数逻辑
    pass
```

## 7. 异常处理

- 使用try-except语句处理异常
- 明确捕获特定类型的异常，避免捕获所有异常
- 在except块中添加适当的错误处理逻辑
- 使用finally块释放资源

```python
try:
    # 可能抛出异常的代码
    pass
except SpecificException as e:
    # 处理特定异常
    pass
except Exception as e:
    # 处理其他异常
    pass
finally:
    # 释放资源
    pass
```

## 8. 导入规范

- 按以下顺序导入模块：
  1. 标准库模块
  2. 第三方库模块
  3. 本地模块
- 每个导入组之间使用空行分隔
- 使用绝对导入，避免使用相对导入

```python
# 标准库模块
import os
import sys

# 第三方库模块
import numpy as np
import pandas as pd

# 本地模块
from mypackage import module
```

## 9. 测试规范

- 为每个模块和函数编写单元测试
- 使用pytest或unittest框架进行测试
- 测试用例应覆盖主要功能和边界情况
- 测试代码应与生产代码分离

## 10. 性能优化

- 避免不必要的计算和循环
- 使用适当的数据结构和算法
- 考虑使用生成器和迭代器减少内存使用
- 避免在循环中进行频繁的I/O操作

## 11. 版本控制

- 使用Git进行版本控制
- 提交代码前进行代码审查
- 提交信息应清晰描述变更内容
- 遵循分支管理规范

## 12. 工具和框架

- 使用lint工具（如flake8、pylint）检查代码风格
- 使用格式化工具（如black、autopep8）统一代码格式
- 使用类型提示提高代码的可读性和可维护性

## 14. Service层架构模式 (DEV-V1.1.0 新增)

### 14.1 设计原则
基于SW-2026-004项目的service层设计实践:

| 原则 | 描述 | SW-2026-004示例 |
|-----|------|------------------|
| 单一职责 | 每个Service只负责一个业务领域 | template_service只管模板操作 |
| 依赖注入 | Service通过构造函数接收依赖 | spec_service接收config对象 |
| 异步优先 | 耗时操作使用async/await | 所有文件IO操作异步化 |

### 14.2 标准Service结构模板

```python
class XxxService:
    """[Service描述]"""

    def __init__(self, config: dict, logger: Logger):
        self._config = config
        self._logger = logger

    async def execute(self, request: Request) -> Response:
        """核心业务方法"""
        # 1. 参数校验
        # 2. 业务逻辑
        # 3. 结果封装
        pass
```

## 15. 常量集中管理规范 (DEV-V1.1.0 新增)

### 15.1 常量定义位置
所有项目级常量必须集中在 `src/core/constants.py` 文件中:

```python
# constants.py 标准结构
class ProjectConfig:
    """项目配置常量"""
    APP_NAME = "Python项目管理工具"
    VERSION = "V1.0.0"

class PathConstants:
    """路径常量"""
    ROOT_DIR = Path(__file__).parent.parent
    TEMPLATE_DIR = ROOT_DIR / "templates"

class ApiConstants:
    """API接口常量"""
    TIMEOUT = 30  # 秒
```

### 15.2 使用规范
- 禁止在业务代码中使用魔法数字/字符串
- 引用方式: `from core.constants import ProjectConfig`

## 16. UI组件化开发规范 (PyQt/PySide) (DEV-V1.1.0 新增)

### 16.1 Widget组织方式
参考SW-2026-004的st_editor等组件:

```
src/ui/
├── widgets/
│   ├── base/           # 基础组件
│   │   └── base_widget.py
│   ├── editors/        # 编辑器组件
│   │   ├── st_editor.py      # ST语言编辑器
│   │   └── markdown_editor.py
│   └── dialogs/        # 对话框组件
└── main_window.py      # 主窗口(组合各Widget)
```

### 16.2 组件开发约定
- 每个Widget独立文件, 继承基类
- 信号(Signal)用于组件间通信
- 样式(QSS)内联或统一资源文件

## 17. 实施指南

### 17.1 代码审查流程
1. **提交前检查**：
   - 使用flake8检查代码风格
   - 使用black格式化代码
   - 运行单元测试确保代码功能正常

2. **代码审查重点**：
   - 命名规范是否符合要求
   - 代码风格是否一致
   - 函数和类的职责是否清晰
   - 异常处理是否合理
   - 测试覆盖率是否充分

3. **审查反馈**：
   - 明确指出问题所在
   - 提供具体的改进建议
   - 确保代码符合项目规范

### 17.2 常见问题解决方案

| 问题 | 解决方案 | 示例 |
|------|---------|------|
| 代码过长 | 拆分函数，每个函数不超过50行 | 将复杂逻辑拆分为多个小型函数 |
| 重复代码 | 提取公共函数或类 | 创建工具函数处理重复逻辑 |
| 缺少注释 | 添加必要的文档字符串 | 为函数和类添加详细的文档字符串 |
| 异常处理不当 | 捕获特定异常，添加错误处理逻辑 | 使用try-except捕获特定异常并处理 |
| 性能问题 | 使用适当的数据结构和算法 | 避免在循环中进行频繁的I/O操作 |

### 17.3 最佳实践示例

#### 17.3.1 模块结构示例
```python
"""模块功能描述"""

# 标准库模块
import os
import sys

# 第三方库模块
import numpy as np
import pandas as pd

# 本地模块
from mypackage import module

# 全局变量
GLOBAL_VARIABLE = 10

class MyClass:
    """类的描述"""
    
    def __init__(self, param1, param2):
        """初始化方法
        
        Args:
            param1: 参数1的描述
            param2: 参数2的描述
        """
        self.param1 = param1
        self.param2 = param2
    
    def method(self):
        """方法描述"""
        return self.param1 + self.param2

def my_function(param1, param2):
    """函数描述
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述
    
    Returns:
        返回值的描述
    """
    return param1 * param2

if __name__ == "__main__":
    obj = MyClass(1, 2)
    print(obj.method())
    print(my_function(3, 4))
```

#### 17.3.2 异常处理示例
```python
try:
    # 可能抛出异常的代码
    with open("file.txt", "r") as f:
        content = f.read()
except FileNotFoundError as e:
    # 处理文件不存在的情况
    print(f"文件不存在: {e}")
except Exception as e:
    # 处理其他异常
    print(f"发生错误: {e}")
finally:
    # 释放资源
    pass
```

## 18. 版本详细变更说明

<a name="v110"></a>
### V1.1.0 版本详细变更
1. 基于SW-2026-004项目实践新增Service层架构模式规范（§14）
2. 新增常量集中管理规范（§15）
3. 新增UI组件化开发规范（PyQt/PySide）（§16）
4. 调整章节编号以适应新增内容

[↑ 返回版本变更记录](1-Python编程规范_DEV-V1.1.0.md#L13)

<a name="v100"></a>
### V1.0.0 版本详细变更
1. 初始版本创建
2. 定义Python编程的基本规范
3. 提供详细的命名规范、代码风格和结构指南

[↑ 返回版本变更记录](1-Python编程规范_DEV-V1.0.0.md#L14)

## 19. 附录

### 19.1 参考资料
| 资料名称 | 版本 | 来源 |
|----------|------|------|
| PEP 8 代码风格指南 | - | https://peps.python.org/pep-0008/ |
| PEP 257 文档字符串指南 | - | https://peps.python.org/pep-0257/ |
| Python官方文档 | - | https://docs.python.org/3/ |
| 通用项目管理规范 | DEV-V1.0.1 | 内部文档 |

### 19.2 联系方式
| 角色 | 姓名 | 邮箱 | 电话 |
|------|------|------|------|
| 文档负责人 | Trae | - | - |
| 技术负责人 | - | - | - |

---

**文档版本**: V1.1.0
**编制日期**: 2026-01-15
**编制人**: 文档专家
**审核人**: [审核人姓名]
