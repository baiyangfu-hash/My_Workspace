# 模板管理模块迭代优化 - 验证清单

## Task 1: template_service.py 修复
- [x] initialize_builtin_templates() 增加清理旧内置模板逻辑（删除DB中is_builtin=True但ID不在DEFAULT_TEMPLATES中的记录）
- [x] update_template() 移除 is_builtin 硬性拒绝，允许修改非标识字段
- [x] update_template() 对 template_id/is_builtin 字段修改返回友好提示
- [x] 新增 reset_builtin_templates() 静态方法，能删除并重建所有内置模板
- [x] 新增 cleanup_orphan_templates() 静态方法
- [x] 修复 Bug A: TemplateDAO.list_all() 方法不存在 → 已在template_dao.py添加
- [x] 修复数据膨胀问题: 16个模板→5个模板（使用force_delete硬删除旧内置模板）
- [x] 修复重置功能失效: reset_ok=N→Y（修正返回值）

## Task 2: template_editor.py 修复
- [x] 业务线CheckBox动态从BusinessLine枚举生成（不再硬编码SW/DJ/ZD/LX/XT/QT/WX）
- [x] _load_template中业务线映射改为动态
- [x] _collect_business_lines返回值与动态CheckBox一致
- [x] 打开内置模板编辑器时，name/description/compiler/scene字段可编辑
- [x] 内置模板的template_id字段仍为readonly
- [x] _apply_readonly_mode只锁定template_id，不锁定其他字段

## Task 3: template_manager.py GUI优化
- [x] 操作列显示4个实际QPushButton(编辑/导出/复制/删除)
- [x] 内置模板行的编辑和删除按钮为disabled
- [x] 内置模板行有视觉区分(颜色/图标/★标记)
- [x] 工具栏有"重置内置模板"按钮
- [x] 点击"重置内置模板"弹出确认对话框
- [x] 底部统计栏显示 "共 X 个模板 (Y 个内置 / Z 个自定义)"
- [x] 统计数字与实际数据一致

## Task 4: 回归测试验证
- [x] regression_test.py 18/18 通过 (100%)
- [x] GUI MainWindow 正常创建无报错
- [x] 模板列表加载后只显示5个内置模板（无旧模板残留）✅ TM-01: total=5 builtin=5 custom=0
- [x] 创建自定义模板 → 保存 → 列表刷新后可见
- [x] 编辑自定义模板 → 修改名称 → 保存 → 名称已更新
- [x] 编辑内置模板 → 修改描述 → 保存 → 描述已更新 ✅ TM-04: updated_name=TestName_V2
- [x] 编辑内置模板 → 尝试修改template_id → 被拒绝且有友好提示 ✅ TM-05: identity_rejected_OK
- [x] 导出模板 → 选择路径 → 文件成功写入
- [x] 复制模板 → 输入新ID → 列表中出现副本
- [x] 删除自定义模板 → 确认 → 从列表消失
- [x] 重置内置模板 → 确认 → 所有内置模板恢复默认状态 ✅ TM-06: reset_ok=Y name_changed_back=Y
- [x] 新建项目对话框模板下拉框显示5个可选模板

## 综合验收
- [x] 数据库中无旧模板残留（TPL-001/TPL-002等旧ID不存在）✅ TM-02: conflicts=0
- [x] 所有模板操作(CRUD+导入导出复制重置)端到端正常 ✅ 7/7 PASS (100%)
- [x] 无新增语法错误或导入错误
- [x] Bug A完全修复: TemplateDAO.list_all() 正常工作
- [x] Bug B完全修复: update_template()正确处理ORM对象输入
- [x] 数据一致性验证通过: 数据库只有5个有效模板（无膨胀）
