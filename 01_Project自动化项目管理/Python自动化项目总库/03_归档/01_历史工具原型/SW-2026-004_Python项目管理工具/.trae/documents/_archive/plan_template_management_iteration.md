# 模板管理功能模块迭代计划

## 一、现状分析

### 1.1 用户反馈的核心问题

| # | 问题 | 严重程度 | 现状 |
|---|------|:--------:|------|
| P0-1 | **内置模板只能查看不能编辑** | 🔴 致命 | 点击"编辑"后整个界面为只读模式 |
| P0-2 | **文档名称中的占位符无法删除/修改** | 🔴 致命 | 如 `{project_code}_需求分析文档.md` 路径中的占位符不可编辑 |
| P1-1 | **文件内容编辑体验差** | 🟠 严重 | 无语法高亮、无搜索替换、无撤销重做 |
| P1-2 | **目录操作不够灵活** | 🟠 严重 | 不支持拖拽排序、不支持批量操作 |
| P2-1 | **缺少模板预览功能** | 🟡 一般 | 无法预览占位符替换后的实际效果 |

### 1.2 根因定位

#### 问题P0-1：内置模板只读锁死
**文件**: [template_manager.py](../../03_主程序/01_主程序核心代码/src/ui/widgets/template_manager.py#L327-L336)
```python
def _edit_template(self, template):
    readonly = template.is_builtin  # ← 内置模板强制只读！
    dialog = TemplateEditorDialog(
        template_id=template.template_id,
        parent=self,
        readonly=readonly          # ← 导致整个编辑器禁用
    )
```

**文件**: [template_editor.py](../../03_主程序/01_主程序核心代码/src/ui/widgets/template_editor.py#L595-L614)
```python
def _apply_readonly_mode(self):
    self.id_input.setReadOnly(True)       # 基本信息全部锁定
    self.name_input.setReadOnly(True)
    ...
    self.file_content_edit.setReadOnly(True)  # 文件内容也锁定！
    self.add_dir_btn.setEnabled(False)      # 目录操作按钮禁用
    self.add_file_btn.setEnabled(False)
    self.delete_item_btn.setEnabled(False)
```

**设计意图 vs 实际需求偏差**:
- 原设计：保护内置模板的 `template_id` 和 `is_builtin` 标识不被篡改
- 实际效果：用户连名称、描述、目录结构、文件内容都无法修改
- 用户真实需求：基于内置模板**克隆/定制**为自己的版本

#### 问题P0-2：占位符处理
**当前行为**:
- 文件路径中的 `{project_code}` 是硬编码在 `DEFAULT_TEMPLATES` 的 `templates[].path` 中
- 文件内容中的 `{project_name}` 同样是硬编码在 `content` 字段中
- GUI加载时直接显示原始文本，用户可以"看到"但只读模式下无法修改

### 1.3 当前模块架构

```
template_manager.py (列表管理)
├── _edit_template() → TemplateEditorDialog(readonly=is_builtin)
├── _on_new_template() → TemplateEditorDialog(readonly=False)
├── _duplicate_template() → 导出→导入(创建副本)
└── _delete_template() / _export_template()

template_editor.py (编辑器对话框)
├── _init_ui(): 信息栏 + 目录树 + 文件编辑面板 + 按钮
├── _load_structure(): 加载目录结构和文件模板到树控件
├── _on_structure_item_clicked(): 点击显示文件内容
├── _add_directory / _add_file_template / _delete_item: CRUD
├── _save_template(): 收集数据 → TemplateService.update/create
└── _apply_readonly_mode(): 全局只读(问题根源)

template_service.py (业务逻辑)
├── get_template / list_templates: 查询
├── create_template / update_template: 增删改
├── export_template / import_template: 导入导出
└── validate_template_structure: 结构验证

constants.py (模板定义)
└── DEFAULT_TEMPLATES: 5个内置模板的完整定义(structure + templates)
```

---

## 二、迭代方案

### 2.1 方案概述：三阶段渐进式增强

| 阶段 | 目标 | 优先级 | 预计工作量 |
|------|------|:------:|----------|
| **Phase 1** | 解锁内置模板编辑 + 修复占位符管理 | P0 | 核心 |
| **Phase 2** | 编辑体验增强（搜索/高亮/预览） | P1 | 改善 |
| **Phase 3** | 高级功能（批量操作/版本对比/模板继承） | P2 | 扩展 |

---

### Phase 1：解锁编辑 + 占位符管理（核心修复）

#### F1.1 内置模板编辑策略重构

**目标**: 允许用户编辑内置模板，通过"另存为"机制保护原模板

**方案选择**: 推荐 **方案A - 另存为新模板**

| 方案 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| **A ✅** | 编辑内置模板时自动切换为"另存为"模式 | 保护原模板、用户体验自然 | 需要新建ID |
| B | 直接允许修改内置模板（仅限非标识字段） | 简单 | 重置内置模板时会丢失用户修改 |
| C | 克隆后再编辑（先复制再打开） | 两步操作 | 多一步确认 |

**具体实现**:

1. **修改 `_edit_template()`** ([template_manager.py:L327](../../03_主程序/01_主程序核心代码/src/ui/widgets/template_manager.py#L327))
```python
def _edit_template(self, template):
    if template.is_builtin:
        # 内置模板：以"另存为副本"模式打开
        dialog = TemplateEditorDialog(
            template_id=template.template_id,
            parent=self,
            readonly=False,           # ← 改为可编辑
            is_clone_mode=True        # ← 新增标记：保存时自动生成新ID
        )
    else:
        dialog = TemplateEditorDialog(
            template_id=template.template_id,
            parent=self,
            readonly=False
        )
    dialog.template_saved.connect(self._load_templates)
    dialog.exec_()
```

2. **修改 `TemplateEditorDialog.__init__()`** 接受 `is_clone_mode` 参数
```python
def __init__(self, template_id=None, parent=None, readonly=False, is_clone_mode=False):
    ...
    self.is_clone_mode = is_clone_mode  # 内置模板副本模式
    if is_clone_mode:
        self.setWindowTitle(f"模板编辑器 [副本模式 - 将保存为新模板]")
```

3. **修改 `_save_template()`** 处理副本模式
```python
def _save_template(self):
    if self.is_clone_mode or self.is_new:
        # 副本/新模式：自动生成新ID或使用用户输入的ID
        new_id = f"{self.id_input.text().strip()}_CUSTOM"
        ...
        success, error = TemplateService.create_template(template_data)
    else:
        # 普通自定义模板更新
        success, error = TemplateService.update_template(template_id, template_data)
```

4. **UI提示优化**: 当打开内置模板时，顶部显示醒目提示条
```
┌─────────────────────────────────────────────────────┐
│ ⚠️ 您正在编辑内置模板「单机设备(PLC+HMI)」的副本     │
│    保存后将创建为新的自定义模板，原内置模板不受影响    │
└─────────────────────────────────────────────────────┘
```

#### F1.2 占位符管理系统增强

**目标**: 让占位符可见、可编辑、可验证

**F1.2.1 占位符可视化高亮**

在文件内容编辑器(`QTextEdit`)中，对 `{xxx}` 格式的占位符进行语法高亮:

- 使用 `QSyntaxHighlighter` 子类实现
- 占位符显示为特殊背景色（浅蓝色）+ 花括号高亮
- 鼠标悬停显示占位符说明tooltip

**新增文件**: `src/ui/widgets/template_highlighter.py`
```python
class PlaceholderHighlighter(QSyntaxHighlighter):
    PLACEHOLDER_PATTERN = r'\{[a-zA-Z_]+\}'
    
    def highlightBlock(self, text):
        # 匹配 {xxx} 格式 → 应用占位符样式
        for match in re.finditer(self.PLACEHOLDER_PATTERN, text):
            format = self.placeholder_format
            self.setFormat(match.start(), match.end() - match.start(), format)
```

**F1.2.2 占位符编辑增强**

在右侧面板增加第三个标签页 **"占位符管理"**:

| 功能 | 说明 |
|------|------|
| 当前文件占位符列表 | 自动扫描文件内容提取所有 `{xxx}` |
| 占位符值编辑 | 直接在此处填写每个占位符的实际值 |
| 即时预览 | 显示替换后的实际文本效果 |
| 全局变量同步 | 与项目创建时的变量值保持一致 |

**F1.2.3 文件路径占位符支持**

当前文件路径中的占位符（如 `{project_code}_需求分析文档.md`）是静态字符串。
需要支持:
- 在目录树中显示原始路径（含占位符）
- 点击文件时可查看/编辑路径
- 保存时保留占位符格式（不做提前替换）

> **注意**: 路径占位符的**替换时机**是在创建项目时（`project_service.py`），不在模板编辑时。模板编辑阶段只需保证占位符完整即可。

#### F1.3 目录结构操作完善

| 操作 | 当前状态 | 改进 |
|------|----------|------|
| 添加目录 | ✅ 支持 | 增加"必填"选项说明tooltip |
| 添加文件 | ✅ 支持 | 增加文件类型选择(与右侧联动) |
| 删除项 | ✅ 支持 | 增加确认对话框+级联删除子项警告 |
| 重命名 | ✅ 支持 | 增加路径冲突检测 |
| **拖拽排序** | ❌ 不支持 | 新增：支持同级目录/文件的拖拽调整顺序 |
| **批量操作** | ❌ 不支持 | 新增：多选删除/批量修改类型 |

---

### Phase 2：编辑体验增强

#### F2.1 文件内容编辑器升级

| 功能 | 实现方式 | 优先级 |
|------|----------|:------:|
| **语法高亮** | QSyntaxHighlighter（Markdown基础高亮） | P1 |
| **搜索替换** | 工具栏添加查找/替换框（Ctrl+F/H） | P1 |
| **撤销重做** | QTextEdit原生支持（需确保未禁用） | P1 |
| **行号显示** | 左侧行号栏（可选开关） | P2 |
| **字体缩放** | Ctrl+滚轮缩放 | P2 |
| **自动保存** | 编辑后3秒自动暂存（关闭时提示恢复） | P2 |

#### F2.2 模板预览功能

新增 **"预览"** 按钮/标签页:
- 输入示例变量值（project_name="测试项目", project_code="TEST-001"...）
- 实时渲染显示替换后的完整目录结构和文件内容
- 支持一键复制预览结果
- 支持导出预览为实际项目结构

#### F2.3 模板校验增强

保存前自动执行:
- [ ] 路径格式检查（禁止 `\`、禁止空名）
- [ ] 占位符完整性检查（使用的占位符是否在SUPPORTED_VARIABLES中定义）
- [ ] 循环引用检查
- [ ] 必填目录/文件存在性检查

---

### Phase 3：高级功能（后续迭代）

| 功能 | 描述 | 优先级 |
|------|------|:------:|
| 模板继承 | 基于内置模板创建子模板，仅记录差异部分 | P2 |
| 版本对比 | 对比两个版本的模板差异 | P2 |
| 模板市场 | 从在线仓库导入社区模板 | P3 |
| 协作编辑 | 多人同时编辑一个模板（需后端支持） | P3 |

---

## 三、实施计划（本次迭代范围）

### 3.1 本次实施：Phase 1 全部 + Phase 2 部分

| 任务编号 | 任务 | 涉及文件 | 复杂度 |
|----------|------|----------|:------:|
| T01 | 内置模板编辑策略重构（另存为副本模式） | template_manager.py, template_editor.py | 中 |
| T02 | 新增副本模式提示UI | template_editor.py | 低 |
| T03 | 占位符语法高亮器 | 新建 template_highlighter.py | 中 |
| T04 | 占位符管理标签页（变量值编辑+即时预览） | template_editor.py | 高 |
| T05 | 文件路径占位符编辑支持 | template_editor.py | 中 |
| T06 | 目录操作完善（删除确认+冲突检测） | template_editor.py | 低 |
| T07 | 搜索替换功能（Ctrl+F/H） | template_editor.py | 中 |
| T08 | 模板保存前自动校验增强 | template_service.py, template_editor.py | 中 |
| T09 | 测试验证（内置模板编辑流程+自定义模板+边界情况） | 回归测试 | 中 |

### 3.2 不做的事项（明确排除）

- ❌ 不修改 `DEFAULT_TEMPLATES` 的内置模板定义内容（那是数据不是功能）
- ❌ 不改变模板的数据模型（Template表结构不变）
- ❌ 不做 Phase 3 的高级功能（模板继承/版本对比/市场）
- ❌ 不修改 `project_service.py` 中的占位符替换逻辑（那是另一个独立问题）

---

## 四、技术风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 内置模板被误修改 | 用户期望修改原模板 | "另存为"模式 + 明确提示 + 保留重置功能 |
| 占位符高亮性能 | 大文件卡顿 | 异步高亮 + 防抖处理 |
| 向后兼容 | 已有自定义模板不受影响 | 仅修改GUI层，service/dao层接口不变 |
| 数据一致性 | 并发编辑冲突 | 单实例编辑器 + 文件锁机制 |

---

## 五、验收标准

### 功能验收

- [ ] **AC-01**: 点击内置模板的"编辑"按钮 → 打开可编辑窗口（非只读）
- [ ] **AC-02**: 编辑内置模板后点击"保存" → 自动生成为新模板（ID带_CUSTOM后缀）
- [ ] **AC-03**: 原内置模板未被修改（重置后仍为默认值）
- [ ] **AC-04**: 文件内容中的 `{project_name}` 等占位符有视觉高亮
- [ ] **AC-05**: 可正常删除/修改文件内容中的占位符字符
- [ ] **AC-06**: Ctrl+F 可搜索文件内容
- [ ] **AC-07**: 保存时有完整的校验提示

### 兼容性验收

- [ ] **AC-08**: 自定义模板的编辑流程不受影响
- [ ] **AC-09**: 新建模板流程不受影响
- [ ] **AC-10**: 导入/导出/复制/删除功能不受影响
