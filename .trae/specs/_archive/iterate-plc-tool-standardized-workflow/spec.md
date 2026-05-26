# PLC项目管理工具标准化工作流迭代 Spec

## Why

当前PLC项目开发过程中存在以下痛点：
1. **规范执行不一致**：已总结的SCL编程规范（903-907）未能系统化地集成到开发工具中，依赖人工记忆和手动检查
2. **错误预防能力不足**：实际项目（如DJ-2026-000/005）中反复出现定时器类型错误、METHOD命名不规范、配置文件字段名错误等问题
3. **诊断效率低下**：遇到Siemens LSP插件兼容性问题时，缺乏系统化的诊断流程和自动化检测手段
4. **测试流程不完善**：虽然有.scltest测试框架，但缺少与项目管理工具的集成，无法形成完整的"编码→检查→测试→诊断"闭环

通过迭代SW-2026-005 PLC项目管理工具，建立**标准化工作流**，将规范检查、深度诊断、测试管理集成到统一平台，提升开发效率和代码质量。

## What Changes

### 1. 规范检查引擎 (Specification Checker Engine)
- 集成`00_通用规范/PLC编程/`下的所有规范文档（903-907）
- 实现可配置的规则集，支持按需启用/禁用检查项
- 提供实时检查（编辑时）和批量检查（项目级）两种模式
- 检查范围包括：
  - **定时器使用规范**（903）：FB_TON参数完整性、PT/ET类型验证（DINT vs TIME）
  - **SCL注释规范**（904）：嵌套注释检测、标点符号检查
  - **SCL编程规范**（905）：METHOD命名规范、变量前缀验证、控制结构语法
  - **错误预防规则**（906）：自动生成文件保护警告、类型转换限制检查
  - **项目配置规范**（907）：.plc.json字段验证、libraries路径解析、目录结构合规性

### 2. 深度诊断模块 (Deep Diagnostics Module)
- **Siemens LSP兼容性诊断**：
  - 自动检测.plc-out/golang/生成的Go代码质量问题
  - 分析OB→FB实例化调用链，识别builtin stub误用问题
  - 生成诊断报告，包含根因分析和修复建议
- **项目健康度评估**：
  - 扫描项目目录结构合规性
  - 检测共享库引用路径有效性
  - 识别潜在的配置冲突（多项目场景）
- **代码质量度量**：
  - 变量命名规范符合率统计
  - 注释覆盖率计算
  - 功能块复杂度分析（圈复杂度）

### 3. 测试管理集成 (Test Management Integration)
- 解析.scltest测试文件，提取TEST_CASE结构
- 在UI中展示测试用例列表和执行状态
- 支持触发plccheck test命令并捕获输出结果
- 测试结果可视化：通过/失败/错误状态展示
- 关联测试失败与源码位置，支持快速跳转定位

### 4. 项目管理增强 (Project Management Enhancement)
- 新建项目向导增加规范配置步骤（选择适用的规范版本）
- 项目模板集成规范检查配置（.plcjson + rules.json）
- 项目仪表盘显示规范符合度指标
- 支持多项目并行管理和批量检查

### 5. 工作流标准化 (Workflow Standardization)
定义标准的PLC项目开发工作流：
```
创建项目 → 配置规范 → 编写代码 → 实时检查 → 运行测试 → 深度诊断 → 修复问题 → 文档更新
```
每个环节都有明确的输入/输出和质量门禁。

## Impact

### Affected specs
- 无现有spec受影响（全新功能迭代）

### Affected code
**核心新增模块**：
- `src/services/spec_checker_service.py` - 规范检查服务（核心引擎）
- `src/services/diagnostic_service.py` - 深度诊断服务
- `src/services/test_management_service.py` - 测试管理服务
- `src/checkers/` - 检查器规则集目录
  - `timer_checker.py` - 定时器使用规范检查器
  - `naming_checker.py` - 命名规范检查器
  - `syntax_checker.py` - 语法规范检查器
  - `config_checker.py` - 配置文件检查器
  - `comment_checker.py` - 注释规范检查器
- `src/diagnostics/` - 诊断模块目录
  - `lsp_compatibility_checker.py` - LSP兼容性诊断
  - `project_health_analyzer.py` - 项目健康度分析
  - `code_quality_metrics.py` - 代码质量度量
- `src/ui/widgets/spec_check_panel.py` - 规范检查面板UI
- `src/ui/widgets/diagnostic_panel.py` - 诊断结果面板UI
- `src/ui/widgets/test_runner_panel.py` - 测试运行器面板UI

**需修改的现有模块**：
- `src/services/plc_service.py` - 从预留接口改为实现规范检查入口
- `src/ui/widgets/variable_checker.py` - 升级为完整的规范检查器
- `src/parsers/st_parser.py` - 增强解析能力以支持更精确的规范检查
- `src/ui/main_window.py` - 集成新功能面板到主界面
- `src/core/app.py` - 可能需要调整应用初始化流程

**配置文件**：
- `config.py` - 增加规范检查相关配置项
- `src/templates/` - 新增规范检查规则模板

## ADDED Requirements

### Requirement: 规则引擎架构
系统SHALL提供可扩展的规则引擎架构，支持：
- 基于Python类的检查器注册机制
- 规则优先级和严重级别定义（Error/Warning/Info）
- 规则元数据描述（名称、描述、适用规范编号、修复建议）
- 规则启用/禁用配置（项目级和全局级）

#### Scenario: 加载默认规则集
- **WHEN** 系统启动或打开项目时
- **THEN** 自动加载`00_通用规范/PLC编程/`目录下的所有规范文件，解析为可执行的检查规则

#### Scenario: 执行规范检查
- **WHEN** 用户触发"规范检查"操作（F5快捷键或菜单）
- **THEN** 系统扫描项目中所有.scl文件，逐条应用启用的规则，生成结构化的检查报告

### Requirement: Siemens LSP诊断集成
系统SHALL提供Siemens LSP插件的兼容性诊断功能：
- 自动识别.plc-out/golang/目录下的生成代码
- 检测常见的代码生成bug模式（如builtin stub误用）
- 解析plccheck命令的错误输出，关联到源码位置
- 生成包含修复建议的诊断报告

#### Scenario: 诊断LSP测试失败
- **WHEN** 用户执行plccheck test失败时
- **THEN** 系统自动收集错误堆栈，分析根因，并在诊断面板展示可能的解决方案

### Requirement: 测试生命周期管理
系统SHALL提供.scltest测试文件的解析和管理功能：
- 解析TEST_CASE块，提取测试名称、步骤、断言
- 展示测试用例树状列表
- 支持选择单个或批量执行测试用例
- 可视化展示测试结果（通过/失败/错误）

#### Scenario: 运行测试并查看结果
- **WHEN** 用户在测试面板点击"运行测试"
- **THEN** 系统调用plccheck test命令，实时捕获输出，更新测试状态图标

### Requirement: 项目健康度仪表盘
系统SHALL在项目仪表盘中展示关键质量指标：
- 规范符合度百分比（基于最近一次检查结果）
- 测试通过率
- 代码质量问题数量趋势
- 共享库引用状态

#### Scenario: 查看项目概览
- **WHEN** 用户打开项目或切换到仪表盘视图
- **THEN** 显示项目的整体健康状况摘要和质量指标卡片

## MODIFIED Requirements

### Requirement: PLCService接口完善
原有的`PLCService`类（目前为预留接口）需要实现以下方法：
- `check_specifications(project_path: str) -> SpecificationReport` - 执行规范检查
- `run_diagnostics(project_path: str) -> DiagnosticReport` - 执行深度诊断
- `run_tests(project_path: str, test_cases: List[str] = None) -> TestResult` - 执行测试
- `get_project_health(project_path: str) -> HealthMetrics` - 获取项目健康指标

### Requirement: VariableCheckerWidget升级
原有的`VariableCheckerWidget`组件需要从模拟数据演示升级为真实的规范检查器界面：
- 连接到后端的`SpecCheckerService`
- 展示实际的检查结果（而非硬编码的示例数据）
- 支持结果过滤、排序、导出
- 提供快速修复建议的一键应用功能

## REMOVED Requirements

无（纯增量迭代，不删除现有功能）

## 技术约束

1. **规范文件格式**：必须兼容Markdown格式的规范文档（00_通用规范中的.md文件）
2. **性能要求**：单文件检查响应时间 < 2秒，项目级批量检查 < 30秒（100个文件以内）
3. **可扩展性**：新规则添加不应修改核心引擎代码，仅需在`src/checkers/`目录新增文件并注册
4. **兼容性**：必须同时支持Windows环境（主要目标）和Linux环境（CI/CD场景）
5. **依赖最小化**：避免引入重型NLP/ML库，优先使用正则表达式和AST解析

## 验收标准

1. 能够成功加载并解析903-907共5份规范文档
2. 对DJ-2026-000项目执行规范检查，能够发现至少3类已知问题（定时器类型、METHOD命名等）
3. 对.plc-out/golang/生成的代码进行诊断，能识别出类似B_ValveCtrl stub误用的问题
4. 能正确解析valve_test.scltest文件中的5个TEST_CASE
5. UI界面能流畅展示检查结果、诊断报告和测试状态
6. 整体工作流可在10分钟内完成一个项目的初步检查和诊断
