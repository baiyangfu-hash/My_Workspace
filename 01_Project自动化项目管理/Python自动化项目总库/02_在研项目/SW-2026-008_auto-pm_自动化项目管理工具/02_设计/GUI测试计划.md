# GUI 测试计划 V0.5.0

> **项目**: SW-2026-008 auto-pm（自动化项目管理工具）
> **版本**: V0.5.0（基于 GUI 原型 V2.1 + V2.3 Week4 实际交付）
> **创建日期**: 2026-07-01
> **执行脚本**: `scripts/gui_plc_full_test.py`（项目内既有端到端 GUI 自动化驱动）
> **关联文档**:
> - [GUI原型设计.md](GUI原型设计.md)（V2.1 已审核通过）
> - [GUI测试整改报告.md](../09_整改项/GUI测试整改报告.md)
> - [PM_SESSION_SW-2026-008.md](PM_SESSION_SW-2026-008.md)

---

## 1. 测试目标

### 1.1 主目标

通过自动化 GUI 测试验证 auto-pm 在 V0.5.0 收口后的端到端功能完整性，并对 V2.3 Week4 新增的「变量表 Tab」和 V2.2 Week3 重构的「规范中心页」做专项验证。

### 1.2 子目标

1. **启动验证**：GUI 主窗口能正常启动，关键控件存在
2. **导航验证**：侧边栏导航树点击切换页面正常
3. **项目列表验证**：搜索/筛选/视图切换/分组模式可用
4. **项目工作区验证**：概览/变更/检查/文档 4 个 Tab 可用
5. **变更单全流程验证**：draft → completed 状态流转完整
6. **变量表 Tab 验证（V2.3 Week4 新增）**：5 格式 Parser + FormatDetector + VariableTableEditor + VartableTab 三栏布局
7. **规范中心页验证（V2.2 Week3 重构）**：6 Tab + DTO/adapter + 14 规范展示
8. **变更中心/报告中心/系统设置**：全局页功能正常
9. **工具栏操作**：同步缓存/刷新列表正常
10. **截图归档**：所有关键步骤生成截图，便于人工审阅

---

## 2. 测试范围

### 2.1 测试覆盖矩阵

| 模块 | GUI 原型章节 | 测试脚本覆盖 | 截图数 | V0.5.0 实际状态 |
|------|-------------|-------------|--------|----------------|
| 主窗口启动 | §2 | ✅ step_01 | 1 | 已验证 |
| 侧边栏导航 | §3 | ✅ step_02 | 6 | 已验证 |
| 项目列表 | §4 | ✅ step_03 | 5 | 已验证 |
| 新建项目 | §7.2 | ✅ step_04 | 0 | ⚠️ Bug：对话框未弹出 |
| 项目工作区·概览 | §5.1 概览 | ✅ step_05 | 2 | 已验证（用现有项目） |
| 项目工作区·变更 | §5.2 变更 | ✅ step_06 | 1 | ⚠️ Bug：创建变更单对话框未弹出 |
| 项目工作区·检查 | §5.3 检查 | ✅ step_07 | 4 | 已验证 |
| 项目工作区·文档 | §5.4 文档 | ✅ step_08 | 2 | 已验证 |
| **项目工作区·变量表** | **§5.5 变量表** | **❌ 未覆盖** | 0 | **V2.3 Week4 新增，原脚本未扩展** |
| 变更中心 | §6 | ✅ step_09 | 2 | 已验证 |
| 报告中心 | §10 | ✅ step_10 | 1 | 已验证 |
| **规范中心页** | **§8（V2.2 Week3 重构）** | **❌ 未覆盖** | 0 | **V2.2 Week3 重构，原脚本未扩展** |
| 系统设置 | §11 | ✅ step_11 | 2 | 已验证 |
| 工具栏操作 | §12 | ✅ step_12 | 2 | 已验证 |
| 最终状态 | — | ✅ step_13 | 1 | 已验证 |
| **合计** | — | **13/15** | **29** | **覆盖 86%，2 个模块待扩展** |

### 2.2 测试方法

- **运行模式**：默认 offscreen（`QT_QPA_PLATFORM=offscreen`，CI 兼容）；可选 visible（设置环境变量 `GUI_VISIBLE=1`）
- **驱动方式**：QTest 程序化驱动（不依赖真实鼠标键盘）
- **截图方式**：`QApplication.activeWindow().grab()` 保存为 PNG，输出到 `test_screenshots/`
- **Bug 记录**：`record_bug()` 函数，按 critical/major/minor 三级分类
- **操作日志**：`log_op()` 函数，时间戳精确到毫秒

### 2.3 测试环境

| 项 | 值 |
|----|-----|
| 工作空间 | `c:\Users\fubai\Desktop\My_Workspace` |
| 测试项目 ID | `DJ-2026-099`（脚本自动创建） |
| Python 环境 | `.venv`（必须激活） |
| PySide6 版本 | 6.7+ |
| 屏幕渲染 | offscreen（无显示器环境兼容） |
| 截图目录 | `<项目根>/test_screenshots/` |

---

## 3. 测试用例详情

### 3.1 启动与窗口基础（TC-01）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-01-01 | 启动 MainWindow | 窗口标题="auto-pm 项目管理工具"，width≥1280，height≥800 | `01_main_window.png` |
| TC-01-02 | 验证状态栏 | 含「工作空间:」标签 | — |
| TC-01-03 | 验证导航树 | `_nav_tree` 不为 None | — |
| TC-01-04 | 验证项目列表视图 | `_project_list_view` 不为 None | — |
| TC-01-05 | 验证中央页面栈 | `_stack.count() >= 8` | — |

### 3.2 侧边栏导航（TC-02）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-02-01 | 点击「PLC 总库」节点 | 切换到 PLC 总库分组视图 | `02_nav_plc_stack.png` |
| TC-02-02 | 点击「PLC 在研项目」子节点 | 筛选 PLC 总库下阶段=developing 的项目 | `02_nav_plc_developing.png` |
| TC-02-03 | 点击「全部项目」节点 | 切换到全部项目列表 | `02_nav_all_projects.png` |
| TC-02-04 | 点击「变更中心」节点 | 切换到变更中心页（index 3） | `02_nav_change_center.png` |
| TC-02-05 | 点击「报告中心」节点 | 切换到报告中心页（index 4） | `02_nav_report.png` |
| TC-02-06 | 点击「系统设置」节点 | 切换到系统设置页（index 6） | `02_nav_settings.png` |

### 3.3 项目列表（TC-03）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-03-01 | 搜索框输入「DJ」 | 列表过滤显示 DJ- 开头项目 | `03_search_dj.png` |
| TC-03-02 | 业务线筛选切换 | 切换 DJ/SW/全部 三个状态 | `03_business_line_filter.png` |
| TC-03-03 | 视图切换·列表视图 | 切换到列表视图正常 | `03_list_view.png` |
| TC-03-04 | 视图切换·卡片视图 | 切换回卡片视图正常 | `03_card_view.png` |
| TC-03-05 | 分组模式切换（4 种） | 总库+业务线 / 总库+阶段 / 业务线 / 阶段 均可切换 | `03_group_mode.png` |

### 3.4 新建项目（TC-04）⚠️ 已知缺陷

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-04-01 | 点击工具栏「新建 PLC 项目」 | NewProjectDialog 弹出 | — |
| TC-04-02 | 填写项目 ID/名称/技术栈 | 表单字段可填写 | — |
| TC-04-03 | 勾选 dry-run 后确定 | 预览弹窗弹出 | — |
| TC-04-04 | 取消重新创建（实际） | 项目创建成功 | `04_project_created.png` |
| TC-04-05 | 处理「已存在」错误弹窗 | 弹窗可正常关闭 | — |

> **⚠️ V0.5.0 测试结果**：TC-04-01 失败，对话框未弹出。根因详见 [整改报告 §3.1](../09_整改项/GUI测试整改报告-V0.5.0.md#31-bug-1新建项目对话框未弹出major)。

### 3.5 项目工作区·概览（TC-05）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-05-01 | 点击项目卡片 | 进入项目工作区，显示概览 Tab | `05_workspace_overview.png` |
| TC-05-02 | 测试项目未找到时回退 | 使用已有 PLC 项目 | `05_workspace_existing.png` |

### 3.6 项目工作区·变更 Tab（TC-06）⚠️ 已知缺陷

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-06-01 | 切换到变更 Tab | 显示变更单列表 | `06_change_tab.png` |
| TC-06-02 | 点击「创建变更单」按钮 | CreateChangeDialog 弹出 | — |
| TC-06-03 | 填写领域/性质/范围/申请人/背景 | 表单字段可填写 | `06_create_change_form.png` |
| TC-06-04 | 点击确定 | 变更单创建成功 | `06_change_created.png` |
| TC-06-05~11 | 7 步状态流转（submitted→completed） | 每步流转成功 | `06_transition_*.png` + `06_after_*.png` |

> **⚠️ V0.5.0 测试结果**：TC-06-02 失败，对话框未弹出。根因详见 [整改报告 §3.2](../09_整改项/GUI测试整改报告-V0.5.0.md#32-bug-2创建变更单对话框未弹出major)。

### 3.7 项目工作区·检查 Tab（TC-07）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-07-01 | 切换到检查 Tab | 显示检查 Tab 空状态 | `07_check_tab_empty.png` |
| TC-07-02 | 点击「执行检查」 | 显示检查结果（pass/warn/fail） | `07_check_result.png` |
| TC-07-03 | 点击「自动修复」 | 显示修复预览 | `07_repair_preview.png` |
| TC-07-04 | 点击「标准化命名」 | 显示标准化预览 | `07_standardize_preview.png` |

### 3.8 项目工作区·文档 Tab（TC-08）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-08-01 | 切换到文档 Tab | 显示文档树 | `08_doc_tab.png` |
| TC-08-02 | 检查文档分类 | 至少有「PM_SESSION」和「其他文档」两类 | — |
| TC-08-03 | 检查模板信息 | 显示模板名称和版本 | — |
| TC-08-04 | 点击「检查模板更新」 | 显示更新预览 | `08_doc_tab_final.png` |

### 3.9 项目工作区·变量表 Tab（TC-09）⏳ 待扩展

> **未覆盖模块**：V2.3 Week4 新增的变量表 Tab，原 `gui_plc_full_test.py` 未扩展。
> 需要扩展测试脚本覆盖 §5.5 的 9 小节功能。

| 用例 ID（计划） | 步骤 | 期望 | 截图（计划） |
|----------------|------|------|--------------|
| TC-09-01 | 切换到变量表 Tab | 显示 QSplitter 三栏布局 | `09_vartable_tab.png` |
| TC-09-02 | 导入 io_points.csv | FormatDetector 识别为 io_points 格式，文件列表显示 | `09_import_io_points.png` |
| TC-09-03 | 导入 program_blocks.yml | FormatDetector 识别为 program_blocks 格式 | `09_import_program_blocks.png` |
| TC-09-04 | 点击文件项 | 右侧 VariableTableEditor 加载解析结果 | `09_load_variable_table.png` |
| TC-09-05 | 新增行/删除行 | VariableTableModel 数据更新 | `09_edit_row.png` |
| TC-09-06 | 点击「批量解析」 | 右侧批量解析结果统计卡片显示 | `09_batch_parse_result.png` |
| TC-09-07 | 导出为 CSV/YAML/JSON | 文件生成成功 | `09_export_csv.png` |

### 3.10 变更中心（TC-10）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-10-01 | 切换到变更中心 | 显示变更单列表 + 状态 Tab | `09_change_center.png` |
| TC-10-02 | 切换状态 Tab（草稿/已提交/实施中/已完成/已归档） | 列表筛选正常 | `09_change_center_tabs.png` |
| TC-10-03 | 点击「创建变更单」 | CreateChangeDialog 弹出 | — |

### 3.11 报告中心（TC-11）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-11-01 | 切换到报告中心 | 显示统计卡片 | `10_report_center.png` |

### 3.12 规范中心页（TC-12）⏳ 待扩展

> **未覆盖模块**：V2.2 Week3 重构的规范中心页，原 `gui_plc_full_test.py` 未扩展。
> 需要扩展测试脚本覆盖 6 Tab（概览/索引/检查/Frontmatter/报告/对比）。

| 用例 ID（计划） | 步骤 | 期望 | 截图（计划） |
|----------------|------|------|--------------|
| TC-12-01 | 切换到规范中心 | 显示 6 Tab 布局 | `12_spec_center.png` |
| TC-12-02 | 切换到「索引」Tab | 显示 14 规范列表 | `12_spec_index.png` |
| TC-12-03 | 切换到「检查」Tab | 显示 10 健康检查项 | `12_spec_check.png` |
| TC-12-04 | 切换到「Frontmatter」Tab | 显示规范文件 frontmatter 列表 | `12_spec_frontmatter.png` |
| TC-12-05 | 切换到「报告」Tab | 显示规范报告生成 | `12_spec_report.png` |
| TC-12-06 | 切换到「对比」Tab | 显示规范对比界面 | `12_spec_diff.png` |

### 3.13 系统设置（TC-13）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-13-01 | 切换到系统设置 | 显示工作空间/缓存路径/项目数/变更数 | `11_settings.png` |
| TC-13-02 | 修改扫描深度 | 数值可改 | — |
| TC-13-03 | 点击「重建索引」 | 弹出确认弹窗 | `11_settings_final.png` |

### 3.14 工具栏操作（TC-14）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-14-01 | 点击「同步缓存」 | 同步完成，状态栏更新 | `12_sync_cache.png` |
| TC-14-02 | 点击「刷新列表」 | 列表刷新 | `12_refresh_list.png` |
| TC-14-03 | 检查状态栏 | 显示「工作空间/项目数/DB状态」 | — |

### 3.15 最终状态与清理（TC-15）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-15-01 | 回到项目列表 | 列表显示正常 | — |
| TC-15-02 | 检查测试项目残留 | DJ-2026-099 存在，需手动清理 | — |
| TC-15-03 | 最终截图 | GUI 状态完整记录 | `99_final_state.png` |

---

## 4. 截图要求

### 4.1 截图命名规则

- 格式：`<步骤号>_<功能描述>.png`（如 `01_main_window.png`、`07_check_result.png`）
- 时间戳：通过操作日志记录，不嵌入文件名
- 编号规则：
  - `01-13`：13 个主要步骤
  - `99`：最终状态
  - `06_transition_<status>`：状态流转中间步骤

### 4.2 截图存储

- 目录：`<项目根>/test_screenshots/`
- 格式：PNG
- 文件大小：约 50-200KB/张（取决于窗口内容复杂度）

### 4.3 截图用途

1. **Bug 复现**：作为 Bug 报告的视觉证据
2. **回归对比**：后续版本 GUI 测试的对比基线
3. **文档配图**：可挑选关键截图用于产品文档
4. **人工审阅**：自动化无法判断的视觉问题（如布局错乱、字体显示）

---

## 5. 评估标准

### 5.1 通过/失败标准

| 等级 | 标准 |
|------|------|
| ✅ 全部通过 | 0 个 critical/major bug，所有截图生成正常 |
| 🟡 部分通过 | 0 个 critical，1-2 个 major，截图覆盖 ≥80% |
| ❌ 失败 | 任何 critical bug，或截图覆盖 <60% |

### 5.2 Bug 严重程度分级

| 等级 | 定义 | 示例 |
|------|------|------|
| 🔴 critical | 阻断主流程，无法继续测试 | GUI 启动失败、核心功能不可用 |
| 🟠 major | 关键功能异常，但有 workaround | 对话框未弹出、状态流转失败 |
| 🟡 minor | 非关键功能异常或视觉问题 | 截图缺失、文案错误 |

### 5.3 测试报告产出

每次执行后，生成 3 类产物：

1. **截图目录** `test_screenshots/`：所有 PNG 截图
2. **Bug 报告** `test_screenshots/bug_report.txt`：自动生成的 Bug 清单
3. **操作日志** `test_screenshots/operation_log.txt`：完整的操作时间线

基于这 3 类产物，输出人工整改报告：`09_整改项/GUI测试整改报告-V<版本>.md`

---

## 6. 执行命令

### 6.1 标准执行（offscreen 模式）

```powershell
# 激活虚拟环境
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"

# 切换到项目目录
cd "c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具"

# 执行测试
python scripts/gui_plc_full_test.py
```

### 6.2 可见模式（人工观察）

```powershell
$env:GUI_VISIBLE = "1"
python scripts/gui_plc_full_test.py
```

### 6.3 单元测试（冒烟测试）

```powershell
# GUI 冒烟测试（offscreen，不调用 show）
pytest tests/ui/test_gui_smoke.py -v

# 启动测试（offscreen，不调用 show）
pytest tests/gui/test_01_launch.py -v
```

---

## 7. 已知限制

### 7.1 测试脚本覆盖缺口

- ❌ 变量表 Tab（V2.3 Week4 新增）未覆盖
- ❌ 规范中心页（V2.2 Week3 重构）未覆盖
- ⚠️ 新建项目对话框与创建变更单对话框未弹出（详见 [整改报告 §3](../09_整改项/GUI测试整改报告-V0.5.0.md)）

### 7.2 测试环境限制

- offscreen 模式下无法验证真实字体渲染、DPI 缩放
- 无法验证真实用户输入速度（QTest 输入速度固定）
- 无法验证多显示器场景

### 7.3 测试项目残留

- 脚本创建的 `DJ-2026-099` 项目不会自动删除，需手动清理
- 路径：`c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\DJ-2026-099_P1修复测试标准项目`

---

## 8. 后续迭代计划

### 8.1 V0.5.x 稳定期整改（Week 1-2）

1. 修复 `gui_plc_full_test.py` 中 `_on_new_project` 和 `_on_create_change` 的调用方式
2. 扩展脚本覆盖变量表 Tab（§5.5 的 9 小节）
3. 扩展脚本覆盖规范中心页（6 Tab）

### 8.2 V0.5.x 稳定期回归（Week 3-4）

- 重跑测试，验证整改后所有用例通过
- 建立 V0.5.0 截图基线，作为后续版本回归对比基准

### 8.3 V0.6.0+ 长期演进

- 引入 GUI 视觉回归测试工具（如 pytest-qt + 图像对比）
- 评估 visible 模式下的真实交互测试
- 测试规模超过 2000 时重新评估 pytest-xdist 并行化

---

## 9. 附录

### 9.1 测试脚本结构

```
scripts/
└── gui_plc_full_test.py    # 端到端 GUI 自动化测试
    ├── step_01_launch_gui       # 启动
    ├── step_02_navigation_tree   # 导航
    ├── step_03_project_list      # 项目列表
    ├── step_04_create_plc_project # 新建项目 ⚠️
    ├── step_05_enter_workspace   # 进入工作区
    ├── step_06_change_tab        # 变更 Tab ⚠️
    ├── step_07_check_tab         # 检查 Tab
    ├── step_08_doc_tab           # 文档 Tab
    ├── step_09_change_center     # 变更中心
    ├── step_10_report_center     # 报告中心
    ├── step_11_settings          # 系统设置
    ├── step_12_toolbar_actions   # 工具栏
    └── step_13_cleanup           # 清理
```

### 9.2 截图清单（V0.5.0 实际产出 29 张）

详见 [GUI测试整改报告-V0.5.0.md §2](../09_整改项/GUI测试整改报告-V0.5.0.md#2-测试执行结果)。

### 9.3 关键代码引用

- 测试脚本入口：[scripts/gui_plc_full_test.py](../scripts/gui_plc_full_test.py)
- 主窗口实现：[auto_pm/ui/main_window.py](../auto_pm/ui/main_window.py)
- 变更 Tab：[auto_pm/ui/workspace/change_tab.py](../auto_pm/ui/workspace/change_tab.py)
- 变量表 Tab（V2.3 新增）：[auto_pm/ui/vartable/](../auto_pm/ui/vartable/)
- 规范中心页（V2.2 重构）：[auto_pm/ui/global_pages/spec_center.py](../auto_pm/ui/global_pages/spec_center.py)
