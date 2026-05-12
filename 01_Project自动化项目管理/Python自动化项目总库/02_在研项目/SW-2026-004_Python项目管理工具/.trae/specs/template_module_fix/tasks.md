# 模板管理模块迭代优化 - 任务计划

## [x] Task 1: 修复 template_service.py (P0 核心Bug)
- **Priority**: P0
- **Depends On**: None
- **Description**:
  1. **修复 initialize_builtin_templates()**: 在循环前先删除数据库中 `is_builtin=True` 但 ID 不在当前 DEFAULT_TEMPLATES 中的旧记录（清理孤立旧模板）
  2. **修复 update_template()**: 移除 `if template.is_builtin: return None` 的硬性拒绝。改为：允许修改 name/version/compiler/scene/description/structure/templates/business_lines；如果 data 中包含 template_id 或 is_builtin 字段则忽略这些字段并给出提示
  3. **新增 reset_builtin_templates()** 静态方法: 删除所有 is_builtin=True 的记录，然后重新调用 initialize_builtin_templates()
  4. **新增 cleanup_orphan_templates()** 静态方法: 删除 DB 中不在 DEFAULT_TEMPLATES IDs 列表中的非内置模板（可选，用于高级清理）
- **Files**: src/services/template_service.py
- **Test Requirements**:
  - `programmatic` TR-1.1: initialize后DB中只有5个内置模板(无旧模板残留)
  - `programmatic` TR-1.2: update_template 对内置模板能成功修改name/description
  - `programmatic` TR-1.3: update_template 对内置模板拒绝修改template_id(返回友好提示)
  - `programmatic` TR-1.4: reset_builtin_templates 能恢复所有内置模板到默认状态

## [x] Task 2: 修复 template_editor.py 业务线枚举 + 移除硬限制 (P0)
- **Priority**: P0
- **Depends On**: None (可与Task1并行)
- **Description**:
  1. **修复业务线枚举不一致**: 将 L119-132 的硬编码 CheckBox(SW/DJ/ZD/LX/XT/QT/WX) 改为动态从 BusinessLine 枚举生成
  2. **修复 _load_template 中业务线映射**: L272-287 的 if-elif 链改为动态映射
  3. **修复 _collect_business_lines 方法**: 返回值与动态生成的CheckBox一致
  4. **移除内置模板的 readonly 硬限制**: L261 不再传递 readonly=True 给内置模板（或改为 partial_readonly），允许编辑非标识字段
  5. **修复 _apply_readonly_mode**: 只锁定 template_id 字段，其他字段可编辑
- **Files**: src/ui/widgets/template_editor.py
- **Test Requirements**:
  - `programmatic` TR-2.1: 编辑器中显示的业务线选项与BusinessLine枚举一致
  - `programmatic` TR-2.2: 打开内置模板编辑器时，名称/描述等字段可编辑
  - `programmatic` TR-2.3: 内置模板的template_id字段仍为readonly

## [x] Task 3: GUI优化 - template_manager.py (P1-P2)
- **Priority**: P1
- **Depends On**: Task 1, Task 2
- **Description**:
  1. **操作列按钮化**: 在 _display_templates() 的操作列(QTableWidget)添加实际QPushButton widgets:
     - "编辑" 按钮 → 连接 _edit_template()
     - "导出" 按钮 → 连接 _export_template()  
     - "复制" 按钮 → 连接 _duplicate_template()
     - "删除" 按钮 → 连接 _delete_template()
     - 内置模板的编辑/删除按钮设为 disabled 或隐藏
  2. **内置模板视觉区分**: 
     - 内置模板行使用不同背景色(如浅蓝色)或前置★图标
     - 自定义模板行保持默认样式
  3. **新增工具栏按钮**:
     - "重置内置模板"按钮 → 调用 TemplateService.reset_builtin_templates() → 确认对话框 → 刷新列表
     - 放在"刷新"按钮旁边
  4. **底部统计栏**: 在表格下方添加 QLabel 显示 "共 X 个模板 (Y 个内置 / Z 个自定义)"
- **Files**: src/ui/widgets/template_manager.py
- **Test Requirements**:
  - `programmatic` TR-3.1: 操作列显示4个实际按钮(编辑/导出/复制/删除)
  - `programmatic` TR-3.2: 内置模板行的编辑和删除按钮为disabled
  - `programmatic` TR-3.3: 内置模板行有视觉区分(颜色或图标)
  - `programmatic` TR-3.4: 底部统计栏正确显示模板数量
  - `programmatic` TR-3.5: 点击"重置内置模板"后确认对话框出现且执行成功

## [x] Task 4: 回归测试验证
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  1. 运行 regression_test.py (18项基础测试)
  2. 运行模板专项测试:
     - 创建自定义模板 → 编辑 → 导出 → 复制 → 删除 全流程
     - 打开内置模板编辑器 → 修改名称/描述 → 保存 → 验证修改生效
     - 重置内置模板 → 验证恢复到默认状态
     - 新建项目时模板下拉框只显示5个模板
  3. 验证 GUI MainWindow 正常启动无报错
- **Files**: regression_test.py, main.py
- **Test Requirements**:
  - `programmatic` TR-4.1: regression_test.py 18/18 通过
  - `programmatic` TR-4.2: 模板CRUD全流程正常
  - `programmatic` TR-4.3: 新建项目模板选择正常(只有5个)

## Task Dependencies
- [Task 1] || [Task 2] 可并行执行
- [Task 3] depends on [Task 1], [Task 2]
- [Task 4] depends on [Task 1], [Task 2], [Task 3]
