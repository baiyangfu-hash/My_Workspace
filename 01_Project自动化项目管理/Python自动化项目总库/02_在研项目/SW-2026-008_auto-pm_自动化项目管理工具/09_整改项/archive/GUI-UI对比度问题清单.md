# GUI UI 对比度问题清单

> **项目**: SW-2026-008 auto-pm（自动化项目管理工具）
> **分析日期**: 2026-07-02
> **分析来源**: [test_reports/gui/full_test_screenshots/](../test_reports/gui/full_test_screenshots/)（48 张截图，覆盖 13 场景 + 三视口）
> **评估标准**: WCAG 2.1 AA（文字与背景对比度 ≥ 4.5:1）
> **关联文档**: [GUI测试整改报告.md](./GUI测试整改报告.md)

---

## 0. 执行摘要

### 0.1 问题概览

| 指标 | 值 | 评估 |
|------|-----|------|
| 截图总数 | 48 张 | — |
| 问题截图数 | 5 张（严重×4，中等×1） | 🟠 部分通过 |
| 正常截图数 | 43 张 | ✅ 89.6% |
| 总体结论 | **5 个对比度问题需修复，其中 4 个严重影响可读性，1 个影响长时间阅读体验** | — |

### 0.2 优先级排序

| 优先级 | 问题页面 | 严重程度 | 影响范围 |
|--------|----------|----------|----------|
| ~~P0~~ | ~~`06_after_submitted_mobile.png`~~ | ✅ 已修复（截图函数缺陷） | 8x8 微小窗口 → 520x392 正常 |
| P0 | `03_new_project_form_mobile.png` | 🔴 严重 | 表单标签不可读 |
| P0 | `05_create_change_page1_mobile.png` | 🔴 严重 | 整页文字过浅 |
| P0 | `13_settings_desktop.png` | 🔴 严重 | 设置项不可读 |
| P1 | `02_list_view_desktop.png` | 🟡 中等 | 表格阅读疲劳 |

---

## 1. 问题详情

### 1.1 ~~P0~~ ✅ 已修复 - 提交后状态页（截图函数缺陷）

| 项 | 值 |
|----|-----|
| 截图 | `06_after_submitted_mobile.png` |
| 视图 | 移动端 |
| 严重程度 | ✅ 已修复 |
| 修复日期 | 2026-07-02 |

**原问题描述**：整页呈深灰/黑色背景，几乎无可见文字或元素。

**实际根因**：非深色模式渲染异常，而是 `screenshot()` 函数使用 `app.activeWindow()` 获取活跃窗口时，第一次流转（draft→submitted）GUI 对话框尝试+降级 API 后，`activeWindow()` 返回了残留的 8x8 像素 QMenu/Dialog 窗口。截图尺寸仅 8x8，平均亮度 30.0。

**修复方案**：在 [scripts/gui_plc_full_test.py:119-135](../scripts/gui_plc_full_test.py#L119-L135) 的 `screenshot()` 函数中增加微小窗口保护：当 `activeWindow()` 返回的窗口尺寸 < 100x100 时，回退到查找正常尺寸的 `topLevelWidget`。

**验证结果**：修复后 `06_after_submitted_mobile.png` 从 8x8 像素变为 520x392 像素，平均亮度从 30.0 提升至 245.5。全量 GUI 测试 0 Bug。

---

### 1.2 P0 - 新建项目表单页

| 项 | 值 |
|----|-----|
| 截图 | `03_new_project_form_mobile.png` |
| 视图 | 移动端 |
| 严重程度 | 🔴 严重 |

**问题描述**：表单标签文字颜色极浅（接近白色），与浅色背景对比度严重不足，几乎不可读。

**影响范围**：所有表单标签、字段说明文字

**建议修复**：
- 将表单标签文字从浅色（如 `#cccccc`）改为深色（如 `#333333`）
- 确保对比度 ≥ 4.5:1（符合 WCAG 2.1 AA 标准）

**注意**：该场景仅有 mobile 视口截图，desktop/tablet 未覆盖。修复后建议补充其他视口测试。

---

### 1.3 P0 - 变更创建页

| 项 | 值 |
|----|-----|
| 截图 | `05_create_change_page1_mobile.png` |
| 视图 | 移动端 |
| 严重程度 | 🔴 严重 |

**问题描述**：页面标题、表单标签、输入内容、按钮文字整体颜色过浅，几乎呈白色，与浅色背景对比度严重不足，可读性极差。

**影响范围**：页面标题、表单标签、输入内容、按钮文字

**建议修复**：
- 统一调整文字颜色至 `#333333` 或 `#444444`
- 按钮文字确保与按钮背景对比度 ≥ 4.5:1

**注意**：该场景仅有 mobile 视口截图，desktop/tablet 未覆盖。修复后建议补充其他视口测试。

---

### 1.4 P0 - 系统设置页

| 项 | 值 |
|----|-----|
| 截图 | `13_settings_desktop.png` |
| 视图 | 桌面端 |
| 严重程度 | 🔴 严重 |

**问题描述**：页面内容区域文字颜色极浅，与浅色背景对比度严重不足，大部分设置项文字几乎不可见。

**影响范围**：设置项文字、标签页文字、按钮文字

**建议修复**：
- 将设置项文字颜色统一调整至 `#333333`
- 标签页与按钮文字颜色需加深

---

### 1.5 P1 - 列表视图

| 项 | 值 |
|----|-----|
| 截图 | `02_list_view_desktop.png` |
| 视图 | 桌面端 |
| 严重程度 | 🟡 中等 |

**问题描述**：表格背景为深灰色，表头与行数据为浅色字，对比度偏低，长时间阅读易造成视觉疲劳。

**影响范围**：表格内容区域

**建议修复**：
- 表格背景改为白色或浅灰色（如 `#fafafa`），文字颜色保持深色（`#333333`）
- 或保持深色背景但使用更亮的文字颜色（如 `#e0e0e0`）

---

## 2. 通过项清单

以下页面对比度与可读性均达标：

| 步骤 | 页面 | 视图 | 状态 |
|------|------|------|------|
| 01 | 首次加载 | desktop/mobile/tablet | ✅ |
| 02 | 卡片视图 | desktop/mobile/tablet | ✅ |
| 02 | 业务线筛选 | mobile | ✅ |
| 02 | 搜索 | mobile | ✅ |
| 04 | 工作区概览 | desktop/mobile/tablet | ✅ |
| 05 | 变更 Tab 空状态 | mobile | ✅ |
| 05 | 变更创建确认 | mobile | ✅ |
| 05 | 变更已创建 | mobile | ✅ |
| 06 | 状态流转（除提交后） | mobile | ✅ |
| 07 | 检查 Tab | mobile | ✅ |
| 08 | 文档 Tab | mobile | ✅ |
| 09 | 变量表 Tab | desktop/mobile/tablet | ✅ |
| 10 | 变更中心 | desktop/mobile/tablet | ✅ |
| 11 | 规范中心 | desktop/mobile/tablet | ✅ |
| 12 | 报告中心 | desktop/mobile/tablet | ✅ |
| 14 | 工具栏操作 | mobile | ✅ |
| 15 | 返回列表 | mobile | ✅ |
| 99 | 最终状态 | desktop | ✅ |

---

## 3. 系统性建议

### 3.1 建立统一颜色 Token 体系

定义全局颜色变量，从根源避免对比度不一致：

| Token | 值 | 用途 |
|-------|-----|------|
| `--text-primary` | `#333333` | 主要文字 |
| `--text-secondary` | `#666666` | 次要文字 |
| `--text-muted` | `#999999` | 辅助文字 |
| `--bg-primary` | `#ffffff` | 主背景 |
| `--bg-secondary` | `#f5f5f5` | 次要背景 |
| `--bg-surface` | `#fafafa` | 卡片/表格背景 |

### 3.2 对比度检查清单

- 文字与背景对比度 ≥ 4.5:1（小文字）
- 文字与背景对比度 ≥ 3:1（大文字，≥18pt）
- 按钮文字与按钮背景对比度 ≥ 4.5:1

### 3.3 移动端特殊处理

- 确保移动端文字最小字号 ≥ 14px
- 表单标签文字颜色统一加深
- 避免浅色背景配浅色文字的组合

### 3.4 深色模式适配检查

针对 `06_after_submitted_mobile.png` 的异常，建议：
- 检查深色模式切换逻辑
- 验证各页面在深色模式下的文字颜色适配
- 添加强制对比测试用例

---

## 4. 后续行动清单

- [x] ~~**立即（P0）**：排查 `06_after_submitted_mobile.png` 渲染异常根因~~ → 已修复（截图函数微小窗口保护）
- [ ] **立即（P0）**：修复 `03_new_project_form_mobile.png` 表单标签文字颜色
- [ ] **立即（P0）**：修复 `05_create_change_page1_mobile.png` 整页文字颜色
- [ ] **立即（P0）**：修复 `13_settings_desktop.png` 设置项文字颜色
- [ ] **Week 1（P1）**：优化 `02_list_view_desktop.png` 表格对比度
- [ ] **持续**：建立颜色 Token 体系，统一管理全局样式
- [ ] **持续**：每次 GUI 样式变更后，检查各视口截图对比度

---

## 5. 附录

### 5.1 截图目录结构

```
test_reports/gui/full_test_screenshots/
├── 01_first_load_*.png              # 首次加载（3张）
├── 02_*.png                         # 项目列表视图（6张）
├── 03_*.png                         # 新建项目（2张）
├── 04_workspace_overview_*.png      # 工作区概览（3张）
├── 05_*.png                         # 变更创建（4张）
├── 06_*.png                         # 状态流转（8张）
├── 07_*.png                         # 检查 Tab（4张）
├── 08_*.png                         # 文档 Tab（2张）
├── 09_vartable_*.png                # 变量表 Tab（5张）
├── 10_change_center_*.png           # 变更中心（5张）
├── 11_spec_center_*.png             # 规范中心（9张）
├── 12_report_center_*.png           # 报告中心（3张）
├── 13_settings_*.png                # 系统设置（4张）
├── 14_*.png                         # 工具栏（2张）
├── 15_back_to_list_mobile.png       # 返回列表
└── 99_final_state_desktop.png       # 最终状态
```

### 5.2 关联代码引用

- 主窗口样式：[auto_pm/ui/main_window.py](../auto_pm/ui/main_window.py)
- 新建项目对话框：[auto_pm/ui/dialogs/new_project_dialog.py](../auto_pm/ui/dialogs/new_project_dialog.py)
- 创建变更对话框：[auto_pm/ui/dialogs/create_change_dialog.py](../auto_pm/ui/dialogs/create_change_dialog.py)
- 系统设置页面：[auto_pm/ui/settings/settings_page.py](../auto_pm/ui/settings/settings_page.py)
- 项目列表视图：[auto_pm/ui/project_list/project_list_widget.py](../auto_pm/ui/project_list/project_list_widget.py)