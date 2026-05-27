# V2.5.8 计划：SCL 源码解析器 + 接口文档自动生成

> **计划日期**: 2026-04-17
> **触发原因**: 用户提供 PLC 接口文档模板(815) + 实际 SCL 代码(FB_ConveyorControlV4)作为参考
> **目标**: 从 SCL/ST 源码自动提取 FB 接口信息，按 815 模板标准生成接口文档

---

## 一、现状分析

### 1.1 现有插件能力

| 组件 | 当前能力 | 局限 |
|------|----------|------|
| `autoshop_parser.py` | 解析 **CSV 变量表**（导出的符号文件） | ❌ 不能解析 SCL 源代码 |
| `codesys_parser.py` | 解析 Codesys 格式 | ❌ 不能解析 SCL 源代码 |
| `work3_parser.py` | 解析 Work3 格式 | ❌ 不能解析 SCL 源代码 |
| `exporter.py` | 导出为 CSV / JSON / Work3 | ❌ 无 Markdown 文档导出 |

### 1.2 用户提供的参考物

**模板**: [815_PLC接口文档模板_INT-V1.0.0.md](../../../00_Obsidian_Base全局规范文件仓库/02_规划过程/02_技术规划/01_API设计/815_PLC接口文档模板_INT-V1.0.0.md)
- 21 个章节的标准化接口文档格式
- 第 5 章（功能块接口）是核心：输入/INOUT/输出字段表 + 调用示例
- 包含变更记录、时序图、测试用例等完整结构

**实际代码**: [FB_ConveyorControlV4_V4.8.1.scl](../../../../项目文件夹/DJ-2026-014_三段式玻璃输送线控制系统/20_软件程序/21_PLC_Autoshop/ST结构文本/FB_ConveyorControlV4_V4.8.1.scl)
- 典型的 Autoshop ST 结构文本（515 行）
- VAR_INPUT: 9 个变量, VAR_INOUT: 1 个, VAR_OUTPUT: 6 个, 内部 VAR: ~25 个
- 含注释头信息（版本、功能描述、变更记录）
- 含调用示例（末尾注释块）

### 1.3 目标能力差距

```
现状:  CSV变量表 → 解析 → 导出CSV/JSON
目标:  SCL源代码 → 解析FB接口 → 生成815标准接口文档(Markdown)
```

---

## 二、SCL 解析模式分析

从 `FB_ConveyorControlV4_V4.8.1.scl` 提取的关键解析模式：

### 2.1 文件头注释解析（第 1~80 行）

```
模式A - 功能描述:
// 功能：控制输送线电机的启动、停止、速度调节和故障检测

模式B - 输入/输出变量列表:
// 输入变量：
//   i_Start - 启动信号
//   i_Stop - 停止信号
//   ...

模式C - 变更记录:
// [2026-01-22] 变更原因：xxx
// 变更内容：xxx
```

### 2.2 VAR 块解析（第 82~150 行）

```scl
//FUNCTION_BLOCK FB_ConveyorControlV4    ← FB名称声明
//VAR_INPUT                               ← 块开始标记
//    i_Start : BOOL;                    ← 变量声明 (名称 : 类型;)
//    i_Start : BOOL;           // 注释   ← 可选行尾注释
//END_VAR                                   ← 块结束标记
//
//VAR_INOUT                                 ← INOUT块
//    i_SpeedFrequency : REAL;
//END_VAR
//
//VAR_OUTPUT                                ← 输出块
//    q_MotorRunning : BOOL;
//END_VAR
//
//VAR                                        ← 内部变量块
//    tmp_bManualMode : BOOL := FALSE;      ← 带默认值
//    In_tTimer1 : ARRAY [0..9] OF BOOL := (...);  ← 数组类型
//END_VAR
```

### 2.3 调用示例解析（第 490~515 行）

```scl
// // 调用示例
// fbConveyorV4(
//     i_Start := X0,
//     ...
// );
```

### 2.4 正则提取规则总结

| 元素 | 正则模式 | 示例 |
|------|----------|------|
| FB 名称 | `FUNCTION_BLOCK\s+(\w+)` | `FB_ConveyorControlV4` |
| VAR_INPUT 开始 | `//VAR_INPUT` | — |
| VAR_INOUT 开始 | `//VAR_INOUT` | — |
| VAR_OUTPUT 开始 | `//VAR_OUTPUT` | — |
| VAR (内部) 开始 | `//VAR` | — |
| 块结束 | `//END_VAR` | — |
| 变量声明 | `\s+(\w+)\s*:\s*([^;]+?)(?:\s*:=\s*(.+?))?\s*;` | `i_Start : BOOL` 或 `tmp_x : INT := 0` |
| 行尾注释 | `//\s*(.+)$` | `// 启动信号` |
| 版本号 | `版本[：:]\s*(v?[\\d.]+)` | `v1.0.0` 或 `V4.8.1` |

---

## 三、执行步骤

### Task 1: 创建 SCL 解析器基类 (P0)

**新建文件**: `src/plugins/plc_variable_parser/parsers/scl_parser.py`

**功能**: 解析 Autoshop SCL/ST 结构文本源文件

**核心类**: `SCLParser(BaseParser)`

**方法设计**:

```python
class SCLParser(BaseParser):
    """SCL/ST结构文本解析器"""
    
    def __init__(self, file_path: str, encoding: str = None):
        super().__init__(file_path, encoding)
        self._format_name = "SCL/Autoshop-ST"
        self.fb_info = {}           # FB基本信息（名称、版本、描述）
        self.input_vars = []        # VAR_INPUT
        self.inout_vars = []        # VAR_INOUT
        self.output_vars = []       # VAR_OUTPUT
        self.internal_vars = []     # 内部VAR
        self.change_log = []        # 变更记录
        self.call_example = ""      # 调用示例
    
    def parse(self) -> List[Dict]:
        """主解析入口"""
        # 1. 读取文件内容
        # 2. 解析头部注释（FB名、版本、描述、变更记录）
        # 3. 解析各VAR块（INPUT/INOUT/OUTPUT/内部）
        # 4. 解析调用示例
        # 5. 返回统一格式的变量列表
        
    def _parse_header_comments(self, lines: List[str]) -> Dict:
        """解析头部注释：提取FB名称、版本、功能描述、变量说明、变更记录"""
        
    def _parse_var_block(self, block_type: str, content: str) -> List[Dict]:
        """解析单个VAR块，返回变量列表"""
        
    def _parse_single_var(self, line: str) -> Optional[Dict]:
        """解析单行变量声明: name : type [:= default] ; // comment"""
        
    def get_fb_info(self) -> Dict:
        """获取FB基本信息"""
        
    def get_change_log(self) -> List[Dict]:
        """获取变更记录"""
```

**返回数据结构**:

```python
{
    'name': 'i_Start',
    'type': 'BOOL',
    'default_value': '',
    'description': '启动信号',       # 来自行尾注释或头部注释列表
    'scope': 'VAR_INPUT',            # INPUT / INOUT / OUTPUT / INTERNAL
}
```

### Task 2: 注册 SCL 解析器到工厂 (P0)

**修改文件**: `parsers/parser_factory.py`

**变更**: 在 `create_parser()` 方法中增加对 `.scl` 文件扩展名的识别，以及手动指定 `'scl'` 类型时的路由。

同时更新 `__init__.py` 导出。

### Task 3: 创建接口文档生成器 (P0)

**新建文件**: `src/plugins/plc_variable_parser/exporters/interface_doc_exporter.py`

**功能**: 将解析后的 SCL 数据渲染为 815 标准格式的 Markdown 接口文档

**核心类**: `InterfaceDocExporter`

**方法设计**:

```python
class InterfaceDocExporter:
    """PLC接口文档生成器（遵循815模板标准）"""
    
    TEMPLATE_SECTIONS = [
        'header',           # 1. 文档基础信息
        'change_log',       # 2. 变更记录
        'overview',         # 3. 接口概述
        'interface_list',   # 4. 接口列表
        'fb_detail',        # 5. 功能块接口（核心！）
        'comm_interface',   # 6. 通信接口（可选填充）
        'hw_interface',     # 7. 硬件接口（可选填充）
        'error_codes',      # 8. 错误码说明
        'version_history',  # 20. 版本详细变更说明
        'appendix',         # 21. 附录
    ]
    
    def __init__(self, parser: SCLParser):
        self.parser = parser
        
    def generate(self, output_path: str, doc_title: str = None,
                 author: str = None, version: str = None) -> bool:
        """生成完整的接口文档"""
        
    def _render_section_header(self, section_id: int, title: str) -> str:
        """渲染章节标题"""
        
    def _render_fb_detail_section(self) -> str:
        """渲染第5章：功能块接口（最复杂的部分）"""
        # 5.1 功能块名称 + 功能描述 + 核心控制逻辑
        # 5.x 调用示例 (SCL代码块)
        # 输入字段表格 (name/type/default/range/description/trigger)
        # INOUT字段表格
        # 输出字段表格
        
    def _render_var_table(self, vars: List[Dict], table_type: str) -> str:
        """渲染变量表格"""
        
    def _render_call_example(self) -> str:
        """渲染调用示例代码块"""
```

**生成的文档结构**（与 815 模板对齐）:

```markdown
# {FB_Name} 接口文档

## 1. 文档基础信息
| 文档标题 | {FB_Name}接口文档 |
| 文档类型 | 接口文档 |
| 版本号 | {从SCL提取} |
| ... | ...

## 2. 变更记录
| 日期 | 版本 | 变更原因 | 变更内容 | 变更人员 |
| ... | ... | ... | ... | ... |

## 5. 功能块接口

### 5.1 {FB_Name}

**功能描述**: {从头部注释提取}

**核心控制逻辑**: {从头部注释提取}

**调用示例**:
```scl
{从SCL提取的调用示例}
```

**输入字段**：
| 字段 | 类型 | 默认值 | 取值范围 | 描述 | 触发条件 |
|------|------|--------|----------|------|----------|
| i_Start | BOOL | FALSE | TRUE/FALSE | 启动信号 | ... |

**INOUT字段**：（同上格式）

**输出字段**：（同上格式）

## 20. 版本详细变更说明
...
```

### Task 4: UI 集成 — 新增"生成接口文档"按钮 (P1)

**修改文件**: `ui/parser_widget.py`

**变更**: 在现有的"导出"按钮区域旁新增「生成接口文档」按钮。

点击后流程:
1. 弹出保存对话框（选择 .md 输出路径）
2. 使用 SCLParser 解析当前文件
3. 使用 InterfaceDocExporter 生成文档
4. 成功提示 + 可选"打开文件夹"

### Task 5: 用 FB_ConveyorControlV4 验证 (P1)

**验证目标**: 用用户提供的 `FB_ConveyorControlV4_V4.8.1.scl` 作为测试输入

**预期产出**:

| 验证项 | 预期结果 |
|--------|----------|
| FB 名称提取 | `FB_ConveyorControlV4` |
| VAR_INPUT 数量 | 9 个变量 |
| VAR_INOUT 数量 | 1 个变量 (`i_SpeedFrequency`) |
| VAR_OUTPUT 数量 | 6 个变量 |
| 内部 VAR 数量 | ~25 个变量 |
| 变更记录条数 | ~18 条（从注释中提取）|
| 调用示例提取 | 完整的 SCL 调用代码块 |
| 生成的 .md 文件 | 符合 815 模板格式，含完整变量表格 |

### Task 6: 更新文档 (P2)

- `07_技术知识库/10_版本迭代历史.md`: 补充 V2.5.8 记录
- `06_交付物/02_发布说明/`: V2.5.8 更新说明（如需打包）

---

## 四、不修改的部分

| 组件 | 原因 |
|------|------|
| 现有的 `autoshop_parser.py` | 保持不变，它处理的是 CSV 符号表，与 SCL 源码是不同用途 |
| 现有的 `exporter.py` (CSV/JSON/Work3) | 保持不变，新增独立的 `interface_doc_exporter.py` |
| 815 模板文件本身 | 只读参考，不修改全局规范仓库中的模板 |
| FB_ConveyorControlV4.scl | 只读参考，不修改用户的源代码 |

---

## 五、文件变更清单

| 操作 | 文件路径 | 说明 |
|------|----------|------|
| **新建** | `parsers/scl_parser.py` | SCL/ST 源码解析器 |
| **新建** | `exporters/interface_doc_exporter.py` | 815 标准接口文档生成器 |
| **修改** | `parsers/parser_factory.py` | 注册 SCL 解析器类型 |
| **修改** | `parsers/__init__.py` | 导出 SCLParser |
| **修改** | `exporters/__init__.py` | 导出 InterfaceDocExporter |
| **修改** | `ui/parser_widget.py` | 新增"生成接口文档"按钮 |
| **修改** | `07_技术知识库/10_版本迭代历史.md` | V2.5.8 记录 |

---

## 六、执行顺序

```
Task 1 (SCL解析器 scl_parser.py)
   ↓
Task 2 (注册到工厂 parser_factory.py)
   ↓
Task 3 (文档生成器 interface_doc_exporter.py)
   ↓
Task 5 (用 FB_ConveyorControlV4 验证)
   ↓
Task 4 (UI集成 parser_widget.py)
   ↓
Task 6 (文档更新)
```

> 注意: Task 5 在 Task 4 之前，先确保解析+生成逻辑正确再接 UI。

## 七、验收标准

- [ ] `FB_ConveyorControlV4_V4.8.1.scl` 能正确解析出全部 16 个接口变量 (9+1+6)
- [ ] 头部注释中的 18 条变更记录能正确提取并填入文档第 2 章
- [ ] 调用示例能以代码块形式正确渲染在文档第 5 章
- [ ] 生成的 Markdown 文件符合 815 模板的章节结构和表格格式
- [ ] UI 中能通过按钮触发生成操作，输出路径可自定义
