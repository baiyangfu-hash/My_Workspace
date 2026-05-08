# 修复新建项目对话框路径为空 Bug Spec

## Why

用户报告：新建项目对话框中，选择"所属总库"后，"项目路径"字段仍然为空。
上一轮修复添加了`_on_library_changed()`方法解决了对话框崩溃问题，但**路径生成逻辑仍有缺陷**。

**根因**：已存在的默认总库（在`root_path`字段引入之前创建）的`root_path`值为NULL/空字符串。
`_update_default_path()`方法中`if lib and lib.root_path:`检查静默失败，导致路径从未被设置。

## What Changes

### 修改1: `library_service.py` - initialize_default_library() 补全root_path
- 当找到已存在的默认总库时，检查其`root_path`是否为空
- 若为空，自动补全为`os.getcwd()`并持久化到数据库
- 确保幂等性：多次调用不会重复覆盖有效值

### 修改2: `new_project_dialog.py` - _update_default_path() 增加降级策略
- 当总库的`root_path`为空时，降级使用`os.getcwd()`作为基础路径
- 双重保障：即使数据库中root_path未补全，UI仍能显示合理路径

## Impact

- Affected specs: library_management_fix (运行时bug热修复)
- Affected code:
  - `src/services/library_service.py` — `initialize_default_library()` 方法
  - `src/ui/dialogs/new_project_dialog.py` — `_update_default_path()` 方法

## ADDED Requirements

### Requirement: 默认总库root_path自动补全

系统 SHALL 在初始化默认总库时，自动检测并补全已存在总库的缺失`root_path`字段。

#### Scenario: 已存在总库的root_path为空
- **WHEN** 系统启动调用`initialize_default_library()`
- **AND** 数据库中已存在名为"Python自动化项目总库"的记录
- **AND** 该记录的`root_path`字段为NULL或空字符串
- **THEN** 系统自动将`root_path`设置为当前工作目录(`os.getcwd()`)
- **AND** 将更新持久化到数据库
- **AND** 返回补全后的总库对象

#### Scenario: 已存在总库的root_path有效
- **WHEN** 系统启动调用`initialize_default_library()`
- **AND** 数据库中已存在名为"Python自动化项目总库"的记录
- **AND** 该记录的`root_path`字段有有效值
- **THEN** 保持原值不变，直接返回该总库对象（幂等操作）

### Requirement: 项目路径生成降级策略

新建项目对话框 SHALL 在总库root_path无效时提供降级路径生成。

#### Scenario: 总库无root_path时的路径生成
- **WHEN** 用户在新建项目对话框中选择了一个总库
- **AND** 该总库的`root_path`为空或None
- **AND** 用户已输入项目编号和名称
- **THEN** 系统使用`os.getcwd()`作为基础路径生成项目路径
- **AND** 路径格式为: `{cwd}\{project_code}_{project_name}`
- **AND** 路径显示在"项目路径"输入框中

#### Scenario: 总库有root_path时的正常路径生成
- **WHEN** 用户在新建项目对话框中选择了一个有有效root_path的总库
- **AND** 用户已输入项目编号和名称
- **THEN** 系统使用该总库的`root_path`作为基础路径
- **AND** 路径格式为: `{library_root_path}\{project_code}_{project_name}`

## MODIFIED Requirements

### Requirement: _update_default_path() 方法增强

原方法仅在有有效`lib.root_path`时生成路径。修改后增加降级逻辑：
1. 优先使用选中总库的`root_path`
2. 若总库无`root_path`或未选择总库，降级使用`os.getcwd()`
3. 若项目编号为空，不生成路径（保持原有行为）
