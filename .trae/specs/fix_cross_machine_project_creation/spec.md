# 修复跨机器创建项目目录失败 Spec

## Why
用户在另一台电脑上运行打包后的 exe 文件时，创建项目报错："创建项目失败：创建项目目录失败"。这是一个严重的跨机器兼容性问题，导致软件无法在其他电脑上正常使用。

## What Changes
- **修复项目路径生成的跨机器兼容性问题**
- **确保在 PyInstaller 冻结环境下能正确创建项目目录**
- **增强路径验证和错误提示**

### 根因分析

通过代码追踪发现完整的错误链路：

1. **`new_project_dialog.py:_update_default_path()` (L181-207)**
   - 从数据库读取总库的 `root_path` 字段
   - 该字段存储的是**开发机器的绝对路径**（如 `D:\BaiduSyncdisk\My_Workspace\...`）
   - 将此路径显示在对话框中供用户确认

2. **`new_project_dialog.py:_on_create()` (L205-242)**
   - 将路径作为 `custom_path` 参数传给 `ProjectService.create_project()`

3. **`project_service.py:create_project()` (L93-99)**
   ```python
   base_path = custom_path or self.config.get("default_project_path")
   if not base_path:
       home_dir = Path.home()
       base_path = str(home_dir / "PythonProjects")
   project_path = get_project_path(base_path, project_code, name)
   ```
   - 直接使用传入的 `custom_path`，**不做有效性验证**

4. **`project_service.py:create_project()` (L125-126)**
   ```python
   if not ensure_directory(project_path):
       return None, "创建项目目录失败"
   ```
   - 在另一台电脑上尝试创建不存在的路径 → **失败**

5. **`path_utils.py:ensure_directory()` (L27-33)**
   ```python
   def ensure_directory(path) -> bool:
       try:
           Path(path).mkdir(parents=True, exist_ok=True)
           return True
       except Exception:
           return False  # ← 吞掉异常，只返回False
   ```
   - **问题**：吞掉所有异常信息，无法定位具体原因

## Impact
- Affected specs: 无（这是基础功能修复）
- Affected code: 
  - `src/services/project_service.py` - create_project() 方法
  - `src/ui/dialogs/new_project_dialog.py` - _update_default_path(), _on_create() 方法
  - `src/utils/path_utils.py` - ensure_directory() 函数
  - `src/services/library_service.py` - _detect_project_base_path() 方法

## ADDED Requirements

### Requirement: 跨机器路径自动检测与回退
系统 SHALL 在创建项目前自动检测目标路径的有效性，如果无效则自动回退到可用路径：

#### Scenario: 目标路径不存在时自动回退
- **WHEN** 用户点击"创建项目"按钮
- **AND** 系统检测到目标路径不存在或不可写
- **THEN** 系统自动回退到可用的备用路径（优先级：总库路径 > exe所在目录/projects > 用户主目录/PythonProjects > 临时目录）
- **AND** 向用户显示实际使用的路径
- **AND** 成功创建项目

#### Scenario: PyInstaller 冻结环境下的路径处理
- **WHEN** 程序在 PyInstaller 打包后的 exe 中运行
- **AND** 数据库中的 root_path 指向不存在的路径
- **THEN** 自动调用 `_detect_project_base_path()` 重新计算有效路径
- **AND** 使用新计算的路径创建项目

### Requirement: 增强的路径验证和错误提示
系统 SHALL 提供详细的路径创建失败原因，帮助用户和开发者快速定位问题：

#### Scenario: 目录创建失败时的详细错误信息
- **WHEN** ensure_directory() 创建目录失败
- **THEN** 返回具体的错误原因（权限不足/路径不存在/磁盘空间不足/路径过长等）
- **AND** 记录完整的异常堆栈到日志
- **AND** 向用户显示友好的中文错误提示

### Requirement: 对话框路径实时验证
系统 SHALL 在新建项目对话框中实时验证并显示路径的有效性状态：

#### Scenario: 路径输入框显示路径有效性
- **WHEN** 对话框中的项目路径发生变化
- **THEN** 实时检测路径是否可写
- **AND** 如果路径不可用，显示警告图标和提示文字
- **AND** 提供一键修正按钮，自动切换到可用路径

## MODIFIED Requirements

### Requirement: 项目创建流程增强
修改 `ProjectService.create_project()` 方法，增加路径预检和自动回退逻辑：

1. **接收 custom_path 参数后立即验证**
2. **如果路径无效，调用 `_detect_project_base_path()` 获取新路径**
3. **使用验证通过的路径创建项目**
4. **返回实际使用的路径信息，便于调试**

### Requirement: 路径工具函数增强
修改 `ensure_directory()` 函数，增加详细错误信息返回：

1. **不再吞掉异常，改为返回 (成功标志, 错误信息) 元组**
2. **区分不同类型的失败原因**
3. **记录完整日志便于排查**

## REMOVED Requirements
无

## Implementation Notes

### 关键修改点

1. **`src/services/project_service.py:L93-126`**
   - 在使用 custom_path 前，先检查路径是否存在且可写
   - 如果不可用，调用 `LibraryService._detect_project_base_path()` 回退
   - 增加多层 fallback 机制

2. **`src/ui/dialogs/new_project_dialog.py:L181-207`**
   - `_update_default_path()` 中增加路径有效性检测
   - 如果总库的 root_path 不可用，自动使用 `_detect_project_base_path()`
   - 显示实际将使用的路径

3. **`src/utils/path_utils.py:L27-33`**
   - `ensure_directory()` 改为返回 `(bool, str)` 元组
   - 第二个元素包含具体错误信息

4. **`src/services/library_service.py:L403-466`**
   - `_detect_project_base_path()` 已有完善的三层 fallback 逻辑
   - 需要将其从 staticmethod 改为可在 service 外部调用的方法
   - 或者在 project_service 中复制该逻辑

### 测试场景

1. ✅ 开发环境正常创建项目（回归测试）
2. ✅ PyInstaller 打包后在另一台电脑创建项目
3. ✅ 总库 root_path 为空时的回退
4. ✅ 总库 root_path 指向不存在路径时的回退
5. ✅ 权限不足时的友好错误提示
6. ✅ 路径过长（>260字符）时的处理
7. ✅ 中文路径和特殊字符的处理
