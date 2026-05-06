# Tasks - 修复跨机器创建项目目录失败

## Task 1: 增强 ensure_directory() 函数，返回详细错误信息
- [x] 1.1 修改 `src/utils/path_utils.py` 中的 `ensure_directory()` 函数
  - 将返回值从 `bool` 改为 `tuple[bool, str]`
  - 成功时返回 `(True, "")`
  - 失败时返回 `(False, 具体错误原因)`
  - 区分：权限不足/路径不存在/路径过长/磁盘空间不足/其他错误
  - 记录完整的异常堆栈到日志

## Task 2: 修改 ProjectService.create_project() 增加路径预检和自动回退
- [x] 2.1 在 `src/services/project_service.py` 的 `create_project()` 方法中（L93-126区域）
  - 接收 custom_path 后立即验证路径有效性（存在且可写）
  - 如果路径无效：
    - 调用 `LibraryService._detect_project_base_path()` 获取可用基础路径
    - 使用新基础路径重新生成 project_path
    - 记录日志说明使用了回退路径
  - 如果回退路径也无效：
    - 使用用户主目录作为最终兜底
    - 返回明确的错误信息："无法在当前环境创建项目目录，请检查磁盘权限"
  - 确保实际使用的路径被记录到项目对象的 path 属性中

## Task 3: 修改 new_project_dialog.py 增加路径实时验证
- [x] 3.1 修改 `_update_default_path()` 方法（L181-207）
  - 获取 base_path 后立即检测是否可写
  - 如果总库的 root_path 不可用：
    - 调用 `_detect_project_base_path()` 获取替代路径
    - 使用替代路径生成完整路径
    - 记录警告日志
  - 显示实际将使用的路径（可能不同于总库配置的 root_path）

- [x] 3.2 修改 `_on_create()` 方法（L205-242区域）
  - 在调用 create_project 前，再次验证 path_input 中的路径
  - 如果路径看起来无效（如包含不存在的驱动器盘符），提示用户
  - 将验证后的路径传入 service

## Task 4: 增强错误提示信息
- [x] 4.1 修改 `project_service.py:L125-126` 的目录创建逻辑
  - 使用新的 `ensure_directory()` 返回值格式
  - 根据具体错误原因返回不同的中文错误消息：
    - 权限不足 → "权限不足：无法创建项目目录，请检查文件夹权限设置"
    - 路径不存在 → "目标路径不存在，请选择有效的保存位置"
    - 路径过长 → "项目路径过长（超过260字符），请使用较短的项目名称"
    - 磁盘空间不足 → "磁盘空间不足，无法创建项目目录"
    - 其他 → "创建项目目录失败：{具体原因}"

## Task 5: 集成测试与回归验证
- [ ] 5.1 测试开发环境下的正常创建流程（确保不破坏现有功能）
- [ ] 5.2 模拟 PyInstaller 冻结环境测试（sys.frozen = True）
  - 模拟数据库中的 root_path 指向不存在路径
  - 验证自动回退到 exe 所在目录或临时目录
  - 验证项目能成功创建
- [ ] 5.3 测试边界情况
  - 总库 root_path 为 None 或空字符串
  - 总库 root_path 包含中文和特殊字符
  - 目标路径需要创建多级目录（parents=True）
  - 路径长度接近 Windows 260 字符限制

## Task Dependencies
- [x] [Task 1] 必须最先完成（其他任务依赖新的函数签名）
- [x] [Task 2] 依赖 [Task 1]
- [x] [Task 3] 可与 [Task 2] 并行执行
- [x] [Task 4] 依赖 [Task 1]
- [Task 5] 必须最后执行（依赖所有修复完成）
