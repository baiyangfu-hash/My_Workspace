# 修复模板GUI编辑按钮禁用问题 - Plan

## 问题分析

### 现象
用户反馈：GUI模板管理界面的"编辑"按钮**只能看不能用**（灰色/禁用状态），点击无反应。

### 根本原因
**GUI层与Service层不同步**：

| 层级 | 当前状态 | 应该状态 |
|------|---------|---------|
| **Service层** (template_service.py) | ✅ 已修复：允许编辑内置模板的非标识字段 | ✅ 正确 |
| **Editor层** (template_editor.py) | ✅ 已修复：partial_readonly模式，只锁template_id | ✅ 正确 |
| **GUI层** (template_manager.py) | ❌ **仍禁用**：`btn_edit.setEnabled(False)` | ❌ 需要修复 |

### 具体代码位置

#### 问题1: 操作列按钮禁用 (Line 194-200)
```python
# 内置模板禁用编辑和删除按钮
is_builtin = getattr(tmpl, 'is_builtin', False)
if is_builtin:
    btn_edit.setEnabled(False)              # ← 这里禁止了编辑！
    btn_edit.setToolTip("内置模板暂不支持直接编辑")
    btn_delete.setEnabled(False)            # ← 删除保持禁用（合理）
    btn_delete.setToolTip("内置模板不能删除(可使用重置功能)")
```

#### 问题2: 右键菜单禁用 (Line 283-286)
```python
# 内置模板不能编辑和删除
if template.is_builtin:
    edit_action.setEnabled(False)           # ← 右键菜单也禁用了！
    delete_action.setEnabled(False)
```

### 关于CLI命令行
经检查 `main.py` 的 CLI 命令列表：
- `gui` - 启动GUI
- `api` - 启动API服务
- `create_project` - 创建项目
- `check_project` - 检查项目规范
- `info` / `version` - 信息显示

**结论：当前CLI没有模板编辑命令**，无法通过命令行编辑模板。

---

## 修复方案

### 修改范围
仅修改 **1个文件**: `src/ui/widgets/template_manager.py`

### 修改内容

#### 修改1: 操作列按钮逻辑 (Line 194-200)

**修改前**:
```python
if is_builtin:
    btn_edit.setEnabled(False)
    btn_edit.setToolTip("内置模板暂不支持直接编辑")
    btn_delete.setEnabled(False)
    btn_delete.setToolTip("内置模板不能删除(可使用重置功能)")
```

**修改后**:
```python
if is_builtin:
    btn_edit.setEnabled(True)   # ← 改为启用！
    btn_edit.setToolTip("编辑内置模板（仅可修改名称、描述等非标识字段）")
    btn_delete.setEnabled(False)  # 删除保持禁用
    btn_delete.setToolTip("内置模板不能删除(可使用重置功能)")
```

#### 修改2: 右键菜单逻辑 (Line 283-286)

**修改前**:
```python
if template.is_builtin:
    edit_action.setEnabled(False)
    delete_action.setEnabled(False)
```

**修改后**:
```python
if template.is_builtin:
    edit_action.setEnabled(True)   # ← 改为启用！
    delete_action.setEnabled(False)  # 删除保持禁用
```

---

## 实施步骤

### Step 1: 修改 template_manager.py - 操作列按钮
- [ ] 定位到 Line 194-200 的 `if is_builtin:` 代码块
- [ ] 将 `btn_edit.setEnabled(False)` 改为 `btn_edit.setEnabled(True)`
- [ ] 更新 tooltip 为 "编辑内置模板（仅可修改名称、描述等非标识字段）"
- [ ] 保持 `btn_delete.setEnabled(False)` 不变

### Step 2: 修改 template_manager.py - 右键菜单
- [ ] 定位到 Line 283-286 的 `if template.is_builtin:` 代码块
- [ ] 将 `edit_action.setEnabled(False)` 改为 `edit_action.setEnabled(True)`
- [ ] 保持 `delete_action.setEnabled(False)` 不变

### Step 3: 验证测试
- [ ] 运行 test_template_fix.py 确保7/7仍然通过
- [ ] 运行 regression_test.py 确保18/18仍然通过
- [ ] 手动验证：启动GUI → 打开模板管理 → 点击内置模板行的"编辑"按钮 → 编辑器打开且非标识字段可编辑 → template_id字段readonly

---

## 预期效果

| 操作 | 修复前 | 修复后 |
|------|--------|--------|
| 点击内置模板"编辑"按钮 | ❌ 灰色不可点 | ✅ 可点击，打开编辑器 |
| 内置模板编辑器中修改name | ❌ 无法进入编辑器 | ✅ 可以修改并保存 |
| 内置模板编辑器中修改template_id | N/A | ❌ 被拒绝（readonly保护） |
| 内置模板"删除"按钮 | ❌ 灰色不可点 | ❌ 保持灰色（设计如此） |
| 自定义模板"编辑"按钮 | ✅ 正常 | ✅ 不受影响 |

## 风险评估
- **风险等级**: 🟢 极低
- **改动量**: 4行代码（2处 setEnabled + 2处 tooltip）
- **影响范围**: 仅影响GUI层的按钮启用状态
- **回滚方案**: 改回 `setEnabled(False)` 即可恢复原状
