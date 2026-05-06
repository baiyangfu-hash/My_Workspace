# Parser 层接口说明

## 模块概述

Parser层负责文件的解析和数据提取，是将原始文件内容转换为结构化数据的关键环节。每个Parser专注于特定格式的文件解析。

**设计目标**:
- 专注单一格式: 每个Parser只处理一种文件类型
- 容错性强: 格式不规范时不崩溃，返回部分结果
- 性能高效: 支持大文件流式解析
- 可扩展: 易于添加对新格式的支持

---

## 模块结构

```
src/parsers/
├── __init__.py          # 模块初始化
├── st_parser.py         # ST代码解析器 ⭐ (已实现)
└── variable_parser.py   # 变量声明解析器 ⭐ (已实现)
```

---

## 公共API列表

### 1. STParser (ST代码解析器) ⭐

**文件**: `st_parser.py`
**状态**: ✅ 已实现 (Phase 0)

```python
class STParser:
    """
    Structured Text (ST) 代码解析器
    
    功能:
    - 解析IEC 61131-3标准的ST代码文件
    - 提取变量声明 (VAR/VAR_INPUT/VAR_OUTPUT/...)
    - 提取Function Block实例化
    - 提取POU定义 (PROGRAM/FUNCTION/FUNCTION_BLOCK)
    - 基础语法分析
    
    支持的PLC品牌:
    - Codesys (默认)
    - Siemens SCL (TODO)
    - Beckhoff ST (TODO)
    - Omron ST (TODO)
    """
    
    def __init__(self):
        """初始化解析器"""
    
    def parse_file(self, file_path: str) -> 'ParseResult':
        """
        解析ST文件
        
        Args:
            file_path: ST源文件路径 (.st/.txt)
            
        Returns:
            ParseResult: 解析结果对象，包含:
                - success: bool 是否成功
                - variables: list[Variable] 变量列表
                - pous: list[POU] POU定义列表
                - errors: list[ParseError] 错误列表
                - warnings: list[str] 警告列表
        """
    
    def parse_string(self, content: str) -> 'ParseResult':
        """
        解析ST代码字符串
        
        Args:
            content: ST源代码字符串
            
        Returns:
            ParseResult: 同上
        """
    
    def extract_variables(self, content: str) -> list:
        """
        快速提取变量声明 (轻量级方法)
        
        Args:
            content: ST代码字符串
            
        Returns:
            list[dict]: 变量字典列表
                         [{'name': 'xVar', 'type': 'INT', 'scope': 'VAR', ...}, ...]
        """
    
    def extract_pou_declarations(self, content: str) -> list:
        """
        提取POU (Program Organization Unit) 声明
        
        Returns:
            list[dict]: POU定义列表
        """
    
    def validate_syntax(self, content: str) -> tuple:
        """
        基础语法验证
        
        Returns:
            tuple: (is_valid: bool, errors: list[str])
        """
```

#### ParseResult 数据结构

```python
@dataclass
class ParseResult:
    """ST代码解析结果"""
    success: bool                          # 是否完全成功
    file_path: str | None = None           # 源文件路径
    variables: list = field(default_factory=list)     # 变量列表 [Variable]
    pous: list = field(default_factory=list)          # POU列表
    function_blocks: list = field(default_factory=list) # FB实例列表
    errors: list = field(default_factory=list)        # 错误列表 [ParseError]
    warnings: list = field(default_factory=list)      # 警告列表
    statistics: dict = field(default_factory=dict)     # 统计信息
```

#### Variable 数据结构

```python
@dataclass
class Variable:
    """变量定义"""
    name: str                              # 变量名 (如 'bStart')
    data_type: str                         # 数据类型 (如 'BOOL', 'INT', 'REAL')
    scope: str                             # 作用域 (VAR/VAR_INPUT/VAR_OUTPUT/VAR_GLOBAL)
    initial_value: str | None = None       # 初始值
    comment: str | None = None             # 注释
    line_number: int = 0                   # 声明所在行号
    address: str | None = None             # IO地址 (如 '%IX0.0')
    is_retain: bool = False                # 是否保持型变量
```

#### 使用示例

```python
from src.parsers.st_parser import STParser

# 创建解析器实例
parser = STParser()

# 方式1: 从文件解析
result = parser.parse_file("path/to/main.st")

if result.success:
    print(f"找到 {len(result.variables)} 个变量")
    for var in result.variables[:10]:
        print(f"  {var.name}: {var.data_type} ({var.scope})")
else:
    print(f"解析失败: {len(result.errors)} 个错误")
    for err in result.errors:
        print(f"  行 {err.line}: {err.message}")

# 方式2: 快速提取变量
code = '''
PROGRAM MainProgram
VAR
    bStart : BOOL := FALSE;
    nCounter : INT := 0;
    fSpeed : REAL;
END_VAR
'''
variables = parser.extract_variables(code)
# => [{'name': 'bStart', 'type': 'BOOL', 'scope': 'VAR', ...}, ...]
```

---

### 2. VariableParser (变量声明解析器) ⭐

**文件**: `variable_parser.py`
**状态**: ✅ 已实现 (Phase 0)

```python
class VariableParser:
    """
    变量声明专用解析器 (轻量级)
    
    相比STParser更专注，专门用于快速提取变量声明，
    不进行完整的语法分析。适合变量检查、IO表生成等场景。
    """
    
    def __init__(self):
        """初始化解析器"""
    
    def parse_file(self, file_path: str) -> list:
        """
        从文件提取变量列表
        
        Returns:
            list[dict]: 变量字典列表
        """
    
    def parse_content(self, content: str) -> list:
        """
        从文本内容提取变量列表
        
        Returns:
            list[dict]: 变量字典列表
        """
    
    def parse_variable_block(self, block_text: str, scope: str) -> list:
        """
        解析单个VAR...END_VAR块
        
        Args:
            block_text: VAR块内的文本
            scope: 作用域 ('VAR', 'VAR_INPUT', etc.)
            
        Returns:
            list[dict]: 该块内的变量列表
        """
    
    def find_duplicate_names(self, variables: list) -> list:
        """
        查找重复变量名
        
        Args:
            variables: 变量列表 (list[dict] 或 list[Variable])
            
        Returns:
            list[tuple]: [(name, count, locations), ...]
        """
    
    def check_type_consistency(self, variables: list) -> list:
        """
        检查类型一致性问题
        
        Returns:
            list[dict]: 问题描述列表
        """
    
    def generate_var_list_markdown(self, variables: list) -> str:
        """
        生成变量清单Markdown文本 (用于文档生成)
        
        Returns:
            str: Markdown格式的变量清单
        """
```

#### 使用示例

```python
from src.parsers.variable_parser import VariableParser

parser = VariableParser()

# 解析单个文件
vars_list = parser.parse_file("path/to/variables.st")

# 查找重复项
duplicates = parser.find_duplicate_names(vars_list)
for name, count, locs in duplicates:
    print(f"重复变量: {name} 出现 {count} 次 @ {locs}")

# 生成Markdown报告
markdown = parser.generate_var_list_markdown(vars_list)
with open('VAR_LIST.md', 'w') as f:
    f.write(markdown)
```

---

## 依赖关系

### 上游依赖 (导入的模块)

| 模块 | 用途 |
|------|------|
| Python标准库 | `re`, `pathlib`, `dataclasses`, `typing`, `enum` |
| `src.models.variable` | Variable数据模型 |
| `src.utils.logger` | 日志记录 |

### 下游依赖 (使用本层的模块)

| 模块 | 用途 |
|------|------|
| `src.services.variable_service` | 变量检查服务 |
| `src.services.plc_service` | PLC代码分析 |
| `src.ui.widgets.variable_checker` | 变量检查UI |

---

## 支持的语法特性

### IEC 61131-3 ST 关键字识别

**POU类型**:
- `PROGRAM`
- `FUNCTION`
- `FUNCTION_BLOCK`

**变量作用域**:
- `VAR` - 局部变量
- `VAR_INPUT` - 输入参数
- `VAR_OUTPUT` - 输出参数
- `VAR_IN_OUT` - 输入输出参数
- `VAR_TEMP` - 临时变量
- `VAR_GLOBAL` - 全局变量
- `VAR_EXTERNAL` - 外部变量
- `VAR_ACCESS` - 访问变量
- `VAR_CONFIG` - 配置变量

**数据类型** (基础类型):
- 布尔: `BOOL`, `BYTE`, `WORD`, `DWORD`, `LWORD`
- 整数: `SINT`, `USINT`, `INT`, `UINT`, `DINT`, `UDINT`, `LINT`, `ULINT`
- 实数: `REAL`, `LREAL`
- 时间: `TIME`, `DATE`, `TOD`, `DT`, `LTIME`
- 字符串: `STRING`, `WSTRING`

**数据类型** (复合类型):
- 数组: `ARRAY [x..y] OF type`
- 结构体: `STRUCT ... END_STRUCT`
- 枚举: `TYPE ... END_TYPE`

**保持属性**:
- `RETAIN` - 保持型 (断电保持)
- `CONSTANT` - 常量
- `PERSISTENT` - 持久化

---

## 错误处理策略

### 1. 容错原则

Parser遵循**最大努力解析**原则:
- 遇到语法错误时跳过当前行，继续解析后续内容
- 不确定的内容标记为警告而非错误
- 尽可能返回部分有效结果

### 2. 错误分级

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| **Error** | 严重语法错误，无法继续 | 记录并跳过 |
| **Warning** | 可疑但不致命 | 记录并继续 |
| **Info** | 信息提示 | 仅在详细模式下输出 |

### 3. ParseError 数据结构

```python
@dataclass
class ParseError:
    """解析错误"""
    level: str              # 'ERROR' | 'WARNING' | 'INFO'
    line_number: int        # 出错行号 (0-based)
    column: int = 0         # 出错列号
    message: str = ""       # 错误描述
    context: str = ""       # 出错行的内容片段
    suggestion: str = ""    # 修复建议 (可选)
```

---

## 性能指标

### 目标性能 (参考)

| 场景 | 文件大小 | 解析时间 | 内存占用 |
|------|----------|----------|----------|
| 小型项目 (<500行) | < 50KB | < 100ms | < 10MB |
| 中型项目 (500-2000行) | 50-200KB | < 500ms | < 30MB |
| 大型项目 (>2000行) | > 200KB | < 2s | < 100MB |

### 优化建议

1. **流式解析**: 对于超大文件，逐行读取而非一次性加载
2. **缓存机制**: 相同文件多次解析时缓存结果
3. **增量解析**: 只重新解析修改的部分 (IDE场景)
4. **并行解析**: 多文件时可使用多线程 (注意GIL限制)

---

## 扩展指南

### 添加对新PLC方言的支持

```python
class SiemensSCLParser(STParser):
    """Siemens SCL语言解析器"""
    
    # SCL特有语法扩展
    KEYWORDS_SCL = {'VAR_TEMP', 'VAR_STATIC', ...}
    
    def parse_variable_block(self, block_text, scope):
        # 先调用父类通用解析
        variables = super().parse_variable_block(block_text, scope)
        
        # 处理SCL特有的语法糖
        # 例如: #attribute('visibility'='internal')
        return variables
```

### 添加新的文件格式Parser

1. 创建 `src/parsers/xxx_parser.py`
2. 定义统一的接口:
   ```python
   class XXXParser:
       def parse_file(self, path) -> ParseResult: ...
       def parse_string(self, content) -> ParseResult: ...
       def validate(self, content) -> tuple: ...
   ```
3. 实现特定格式解析逻辑
4. 编写测试用例覆盖各种情况
5. 更新文档

---

## 测试要求

每个Parser必须有完善的单元测试:

**test_st_parser.py**:
- 有效ST代码完整解析
- 各种变量声明的正确识别
- 嵌套结构的处理
- 注释和空白字符的处理
- 错误恢复能力
- 边界情况 (空文件/超大文件/非法字符)

**test_variable_parser.py**:
- 变量提取准确性
- 重复检测正确性
- 类型一致性检查
- 特殊字符处理
- 多种编码支持 (UTF-8/GBK/ASCII)

测试数据位置: `tests/fixtures/st_samples/`

---

## 注意事项

1. **编码处理**: ST文件可能是多种编码，需自动检测或指定编码
2. **BOM处理**: Windows系统可能有UTF-8 BOM头
3. **行尾符号**: 统一处理 `\r\n` (Windows) 和 `\n` (Linux/Mac)
4. **注释风格**: 支持 `(* ... *)` 和 `// ...` 两种注释
5. **大小写**: IEC 61131-3 不区分大小写，但通常大写关键字

---

## 版本历史

- **v1.0.0** (Phase 0): 初始版本
  - ✅ STParser: 基础ST代码解析 (IEC 611-3子集)
  - ✅ VariableParser: 专注变量声明提取
  - ✅ 错误处理和容错机制
  - 🔨 后续: 更多PLC方言支持 (Phase 2+)
