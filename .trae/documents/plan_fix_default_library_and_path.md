# 计划: 修复新建项目对话框默认总库关联 + 路径定位

## 问题分析（基于截图）

### 问题1: 所属总库默认显示"(不关联总库)" ⚠️ P0
**根因**: ID不匹配
- `new_project_dialog.py:116` 用 `findData("LIB-DEFAULT-001")` 硬编码查找
- 但 `library_service.py:51` 创建时用UUID格式: `f"LIB-{Ymd}-{8位hex}"`
- 实际library_id ≠ "LIB-DEFAULT-001" → findData返回-1 → 选中失败

### 问题2: 项目路径指向了cwd而不是总库项目目录 ⚠️ P0
**根因**: root_path设置不合理
- `library_service.py:447/457` 设置 `root_path = os.getcwd()` (即程序运行目录)
- 截图路径: `d:\BaiduSyncdisk\My_Workspace\SW-2026-002_未命名项目`
- 用户期望: 总库root_path应指向实际的项目存放目录 (`0100_项目/`)
- 实际目录结构:
  ```
  01_Project自动化项目管理/
    Python自动化项目总库/
      0100_项目/          ← 新建项目应该放这里
        DJ-2026-001_测试/
        DJ-2026-002_xxx/
      02_在研项目/
  ```

---

## 修改方案

### 修改1: `library_service.py` — root_path指向正确的项目目录

**位置**: `initialize_default_library()` 方法 (第447行和第457行)

**改动A — 补全已有总库的root_path** (第446-448行):
```python
# 原来:
if not existing.root_path:
    existing.root_path = os.getcwd()

# 改为:
if not existing.root_path:
    # root_path指向总库下的"0100_项目"目录（项目统一存放位置）
    project_base = os.path.join(os.getcwd(), "01_Project自动化项目管理", "Python自动化项目总库", "0100_项目")
    os.makedirs(project_base, exist_ok=True)
    existing.root_path = project_base
```

**改动B — 新建总库的root_path** (第457行):
```python
# 原来:
root_path = os.getcwd()

# 改为:
project_base = os.path.join(os.getcwd(), "01_Project自动化项目管理", "Python自动化项目总库", "0100_项目")
os.makedirs(project_base, exist_ok=True)
root_path = project_base
```

### 修改2: `new_project_dialog.py` — 默认选中逻辑改用名称匹配

**位置**: `_load_data()` 方法 (第115-118行)

```python
# 原来:
idx = self.lib_combo.findData("LIB-DEFAULT-001")
if idx >= 0:
    self.lib_combo.setCurrentIndex(idx)

# 改为: 按名称查找默认总库并选中（跳过index=0的"不关联"选项）
default_idx = None
for i in range(1, self.lib_combo.count()):  # 从1开始跳过"(不关联总库)"
    if self.lib_combo.itemText(i) == "Python自动化项目总库":
        default_idx = i
        break
if default_idx is not None:
    self.lib_combo.setCurrentIndex(default_idx)
```

---

## 预期效果

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| 所属总库 | (不关联总库) | ✅ Python自动化项目总库 |
| 项目路径 | `d:\My_Workspace\SW-2026-xxx_未命名项目` | ✅ `...\0100_项目\SW-2026-xxx_项目名称` |
| 总库管理意义 | ❌ 路径与总库无关 | ✅ 项目自动归档到总库目录下 |

## 验证步骤

1. 运行应用，打开新建项目对话框
2. 确认"所属总库"默认显示"Python自动化项目总库"
3. 确认"项目路径"自动填充为 `{总库}\0100_项目\{编号}_{名称}`
4. 输入项目名称后确认路径实时更新
5. 切换到"(不关联总库)"确认路径降级到cwd
