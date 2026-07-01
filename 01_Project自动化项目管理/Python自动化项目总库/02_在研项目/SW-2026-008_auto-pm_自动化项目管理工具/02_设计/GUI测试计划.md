# GUI 测试计划 V0.5.1

> **项目**: SW-2026-008 auto-pm（自动化项目管理工具）
> **版本**: V0.5.1（V0.5.0 测试整合升级：helpers 复用 + 超时截图 + 边界用例完善）
> **创建日期**: 2026-07-01
> **最后更新**: 2026-07-01（GUI 测试脚本整合）
> **执行脚本**:
> - L2 集成层：`tests/gui/`（pytest，104 passed / 2 skipped）
> - L3 端到端层：`scripts/gui_plc_full_test.py`（15 场景，0 功能 bug，85 截图）
> - 统一入口：`scripts/run_tests.py gui`
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

| 模块 | GUI 原型章节 | L3 脚本覆盖 | L2 pytest 覆盖 | 截图数 | V0.5.1 实际状态 |
|------|-------------|-------------|---------------|--------|----------------|
| 主窗口启动 | §2 | ✅ step_01 | ✅ test_01_launch | 1 | 已验证 |
| 侧边栏导航 | §3 | ✅ step_02 | ✅ test_02_navigation | 6 | 已验证 |
| 项目列表 | §4 | ✅ step_03 | ✅ test_03_project_list | 5 | 已验证 |
| 新建项目 | §7.2 | ✅ step_03 | ✅ test_04_project_crud | 2 | 已验证（V0.5.1 修复） |
| 项目工作区·概览 | §5.1 概览 | ✅ step_04 | ✅ test_05_workspace_overview | 2 | 已验证 |
| 项目工作区·变更 | §5.2 变更 | ✅ step_05/06 | ✅ test_06_change_tab | 8 | 已验证（V0.5.1 修复） |
| 项目工作区·检查 | §5.3 检查 | ✅ step_07 | ✅ test_07_check_tab | 4 | 已验证 |
| 项目工作区·文档 | §5.4 文档 | ✅ step_08 | ✅ test_08_doc_tab | 2 | 已验证 |
| 项目工作区·变量表 | §5.5 变量表 | ✅ step_09 | — | 4 | 已验证（V0.5.1 扩展） |
| 变更中心 | §6 | ✅ step_10 | ✅ test_09_change_center | 2 | 已验证 |
| 报告中心 | §10 | ✅ step_12 | ✅ test_10_report_center | 1 | 已验证 |
| 规范中心页 | §8（V2.2 Week3 重构） | ✅ step_11 | ✅ test_12_spec_center | 3 | 已验证（V0.5.1 扩展） |
| 系统设置 | §11 | ✅ step_13 | ✅ test_13_settings | 2 | 已验证 |
| 工具栏操作 | §12 | ✅ step_14 | ✅ test_14_toolbar | 2 | 已验证 |
| 最终状态 | — | ✅ step_15 | — | 1 | 已验证 |
| **合计** | — | **15/15** | **14/15** | **45** | **覆盖 100%** |

> **说明**：L2 pytest 层变量表 Tab 未单独建测试文件（仅 L3 端到端覆盖），后续可补齐 test_09_vartable_tab.py。

### 2.2 测试方法

- **运行模式（V0.5.2 变更）**：默认 **visible 可见窗口模式**（不设置 `QT_QPA_PLATFORM=offscreen`，或设置 `GUI_VISIBLE=1`）；offscreen 模式仅在用户特别要求时使用（如 CI 无显示器环境、批量回归）
- **可见模式理由**：offscreen 模式无法验证真实字体渲染/DPI 缩放/多显示器场景，且会掩盖部分交互问题；按真实使用场景测试更接近用户实际体验
- **驱动方式**：QTest 程序化驱动（不依赖真实鼠标键盘）
- **截图方式**：`QApplication.activeWindow().grab()` 保存为 PNG
- **截图目录**：
  - L3 端到端：`test_reports/gui/full_test_screenshots/`（含 `_desktop/_tablet/_mobile` 视口后缀）
  - L2 失败截图：`test_reports/gui/failure_screenshots/`（`FAIL_` / `TIMEOUT_` 前缀 + 测试名 + 时间戳）
- **超时截图机制**（V0.5.1 新增）：
  - L2 pytest：`conftest.py` 的 `pytest_runtest_teardown` hook，测试失败/超时时自动截图所有可见顶层窗口 + 关闭残留模态弹窗
  - L3 scripts：`threading` 看门狗（5 分钟总超时，写日志 + `os._exit(2)` 强制退出）
- **Bug 记录**：`record_bug()` 函数，按 critical/major/minor 三级分类
- **操作日志**：`log_op()` 函数，时间戳精确到毫秒
- **弹窗处理**：统一复用 `tests/gui/helpers/interactions.py`（find_dialog/dismiss_message_boxes/close_all_modal_widgets），L3 scripts 薄包装复用，避免两套实现

### 2.3 测试环境

| 项 | 值 |
|----|-----|
| 工作空间 | L2：`tmp_path_factory` 隔离工作空间；L3：`c:\Users\fubai\Desktop\My_Workspace` |
| 测试项目 ID | L2：`DJ-2026-998`（fixture 创建）；L3：`DJ-2026-099`（脚本自动创建） |
| Python 环境 | `.venv`（必须激活） |
| PySide6 版本 | 6.7+ |
| 屏幕渲染 | **visible 可见窗口（默认）**；`QT_QPA_PLATFORM=offscreen` 切换离屏模式（仅用户特别要求时） |
| L3 截图目录 | `<项目根>/test_reports/gui/full_test_screenshots/` |
| L2 失败截图目录 | `<项目根>/test_reports/gui/failure_screenshots/` |

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

### 3.4 新建项目（TC-04）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-04-01 | 点击工具栏「新建 PLC 项目」 | NewProjectDialog 弹出 | — |
| TC-04-02 | 填写项目 ID/名称/技术栈 | 表单字段可填写 | — |
| TC-04-03 | 勾选 dry-run 后确定 | 预览弹窗弹出 | — |
| TC-04-04 | 取消重新创建（实际） | 项目创建成功 | `04_project_created.png` |
| TC-04-05 | 处理「已存在」错误弹窗 | 弹窗可正常关闭 | — |
| TC-04-06 | ID 为空时点 OK | 弹出"请输入项目编号"警告（V0.5.1 边界用例） | — |
| TC-04-07 | 点取消按钮 | 对话框正确关闭（V0.5.1 边界用例） | — |

> **V0.5.1 修复**：TC-04-01 对话框未弹出问题已修复（根因：`_on_new_project` 调用方式错误）。新增 TC-04-06/07 边界用例验证表单验证和对话框生命周期。

### 3.5 项目工作区·概览（TC-05）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-05-01 | 点击项目卡片 | 进入项目工作区，显示概览 Tab | `05_workspace_overview.png` |
| TC-05-02 | 测试项目未找到时回退 | 使用已有 PLC 项目 | `05_workspace_existing.png` |

### 3.6 项目工作区·变更 Tab（TC-06）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-06-01 | 切换到变更 Tab | 显示变更单列表 | `06_change_tab.png` |
| TC-06-02 | 点击「创建变更单」按钮 | CreateChangeWizard 弹出 | — |
| TC-06-03 | 填写领域/性质/范围/申请人/背景 | 表单字段可填写 | `06_create_change_form.png` |
| TC-06-04 | 点击完成 | 变更单创建成功（监听 change_created 信号） | `06_change_created.png` |
| TC-06-05~11 | 7 步状态流转（submitted→completed） | 每步流转成功（监听 transition_completed 信号） | `06_transition_*.png` + `06_after_*.png` |
| TC-06-12 | 空状态提示与变更单数量一致性 | 无变更单时显示"暂无变更单"（V0.5.1 边界用例） | — |
| TC-06-13 | 取消 wizard 按钮 | wizard 正确关闭（V0.5.1 边界用例） | — |

> **V0.5.1 修复**：TC-06-02 对话框未弹出问题已修复（根因：`_on_create_change` 调用方式错误）。改用 QWizard + 信号驱动成功检测（change_created/transition_completed），新增 TC-06-12/13 边界用例。

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

### 3.9 项目工作区·变量表 Tab（TC-09）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-09-01 | 切换到变量表 Tab | 显示 QSplitter 三栏布局 | `09_vartable_tab.png` |
| TC-09-02 | 导入 io_points.csv | FormatDetector 识别为 io_points 格式，文件列表显示 | `09_import_io_points.png` |
| TC-09-03 | 导入 program_blocks.yml | FormatDetector 识别为 program_blocks 格式 | `09_import_program_blocks.png` |
| TC-09-04 | 点击文件项 | 右侧 VariableTableEditor 加载解析结果 | `09_load_variable_table.png` |
| TC-09-05 | 新增行/删除行 | VariableTableModel 数据更新 | `09_edit_row.png` |
| TC-09-06 | 点击「批量解析」 | 右侧批量解析结果统计卡片显示 | `09_batch_parse_result.png` |
| TC-09-07 | 导出为 CSV/YAML/JSON | 文件生成成功 | `09_export_csv.png` |

> **V0.5.1 扩展**：新增 step_09_vartable_tab 覆盖变量表 Tab 三栏布局、文件列表、批量解析、编辑器加载。

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

### 3.12 规范中心页（TC-12）

| 用例 ID | 步骤 | 期望 | 截图 |
|---------|------|------|------|
| TC-12-01 | 切换到规范中心 | 显示 6 Tab 布局 | `12_spec_center.png` |
| TC-12-02 | 切换到「索引」Tab | 显示 14 规范列表 | `12_spec_index.png` |
| TC-12-03 | 切换到「检查」Tab | 显示 10 健康检查项 | `12_spec_check.png` |
| TC-12-04 | 切换到「Frontmatter」Tab | 显示规范文件 frontmatter 列表 | `12_spec_frontmatter.png` |
| TC-12-05 | 切换到「报告」Tab | 显示规范报告生成 | `12_spec_report.png` |
| TC-12-06 | 切换到「对比」Tab | 显示规范对比界面 | `12_spec_diff.png` |

> **V0.5.1 扩展**：新增 step_11_spec_center 覆盖规范中心页 6 Tab 切换 + 视口截图。

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
  - `01-15`：15 个主要步骤
  - `99`：最终状态
  - `06_transition_<status>`：状态流转中间步骤
  - L2 失败截图：`FAIL_<测试名>_<时间戳>_w<序号>.png` / `TIMEOUT_<测试名>_<时间戳>_w<序号>.png`

### 4.2 截图存储

- L3 端到端目录：`<项目根>/test_reports/gui/full_test_screenshots/`
- L2 失败截图目录：`<项目根>/test_reports/gui/failure_screenshots/`
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

1. **截图目录** `test_reports/gui/full_test_screenshots/`：所有 PNG 截图
2. **Bug 报告** `test_reports/gui/full_test_screenshots/bug_report.txt`：自动生成的 Bug 清单
3. **操作日志** `test_reports/gui/full_test_screenshots/operation_log.txt`：完整的操作时间线

基于这 3 类产物，输出人工整改报告：`09_整改项/GUI测试整改报告-V<版本>.md`

---

## 6. 执行命令

### 6.1 L2 集成层（pytest）

```powershell
# 激活虚拟环境
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"

# 切换到项目目录
cd "c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具"

# 全量 GUI 测试（visible 可见模式，默认）
python scripts/run_tests.py gui

# 或直接用 pytest（默认可见模式）
pytest tests/gui/ -v --timeout=90

# offscreen 模式（仅用户特别要求时，如 CI 无显示器环境）
$env:QT_QPA_PLATFORM = "offscreen"
pytest tests/gui/ -v --timeout=90

# 单个测试文件
pytest tests/gui/test_04_project_crud.py -v
```

### 6.2 L3 端到端层（scripts）

```powershell
# 标准执行（visible 可见模式，默认）
python scripts/gui_plc_full_test.py

# offscreen 模式（仅用户特别要求时，如 CI 无显示器环境）
$env:QT_QPA_PLATFORM = "offscreen"
python scripts/gui_plc_full_test.py
```

### 6.3 冒烟测试

```powershell
# GUI 冒烟测试（visible 可见模式，默认）
pytest tests/ui/test_gui_smoke.py -v

# 启动测试（visible 可见模式，默认）
pytest tests/gui/test_01_launch.py -v
```

---

## 7. 已知限制

### 7.1 测试脚本覆盖缺口

- ⚠️ L2 pytest 层变量表 Tab 未单独建测试文件（仅 L3 端到端覆盖），后续可补齐 test_09_vartable_tab.py
- ✅ V0.5.0 时期的"新建项目对话框未弹出"和"创建变更单对话框未弹出"问题已在 V0.5.1 修复

### 7.2 测试环境限制

- offscreen 模式下无法验证真实字体渲染、DPI 缩放
- 无法验证真实用户输入速度（QTest 输入速度固定）
- 无法验证多显示器场景

### 7.3 测试项目残留

- L3 脚本创建的 `DJ-2026-099` 项目不会自动删除，需手动清理
- 路径：`c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\DJ-2026-099_P1修复测试标准项目`
- L2 测试使用 `tmp_path_factory` 隔离工作空间，测试结束自动清理，无残留

---

## 8. 后续迭代计划

### 8.1 V0.5.1 已完成（2026-07-01）

1. ✅ 修复 helpers/interactions.py + assertions.py 嵌套 QDialog 查找 bug
2. ✅ scripts/gui_plc_full_test.py 复用 tests/gui/helpers/ 实现
3. ✅ 升级 tests/gui/test_04/06/09 为实际提交模式（QWizard FinishButton + 信号驱动成功检测）
4. ✅ 补超时截图机制（conftest teardown 失败截图 + scripts 看门狗）
5. ✅ 清理重叠 + 统一入口（run_tests.py gui）+ 更新文档
6. ✅ 新增 4 个边界用例（空 ID 提交、取消按钮、空状态显示、取消 wizard）

### 8.2 V0.5.x 后续优化

- 补齐 L2 pytest 层变量表 Tab 测试文件（test_09_vartable_tab.py）
- 建立 V0.5.1 截图基线，作为后续版本回归对比基准
- 评估 visible 模式下的真实交互测试

### 8.3 V0.6.0+ 长期演进

- 引入 GUI 视觉回归测试工具（如 pytest-qt + 图像对比）
- 测试规模超过 2000 时重新评估 pytest-xdist 并行化
- 评估可见窗口模式下的真实用户交互路径测试

---

## 9. 附录

### 9.1 测试脚本结构

```
scripts/
├── gui_plc_full_test.py    # L3 端到端 GUI 自动化测试（15 步）
│   ├── step_01_launch_gui          # 启动
│   ├── step_02_navigation          # 导航
│   ├── step_03_create_project      # 新建项目
│   ├── step_04_enter_workspace     # 进入工作区
│   ├── step_05_create_change       # 变更 Tab·创建变更单
│   ├── step_06_change_transitions  # 变更 Tab·状态流转
│   ├── step_07_check_tab           # 检查 Tab
│   ├── step_08_doc_tab             # 文档 Tab
│   ├── step_09_vartable_tab        # 变量表 Tab（V0.5.1 扩展）
│   ├── step_10_change_center       # 变更中心
│   ├── step_11_spec_center         # 规范中心页（V0.5.1 扩展）
│   ├── step_12_report_center       # 报告中心
│   ├── step_13_settings            # 系统设置
│   ├── step_14_toolbar             # 工具栏
│   └── step_15_cleanup             # 清理
└── run_tests.py                    # 统一测试入口（smoke/unit/gui/all/coverage）

tests/gui/                          # L2 集成层（17 个测试文件）
├── helpers/                        # 共享 helpers（interactions/assertions/bug_recorder）
├── conftest.py                     # fixture + 失败截图 hooks
├── test_01_launch.py               # 启动
├── test_02_navigation.py           # 导航
├── test_03_project_list.py         # 项目列表
├── test_04_project_crud.py         # 新建项目（含边界用例）
├── test_05_workspace_overview.py   # 概览
├── test_06_change_tab.py           # 变更 Tab（含实际提交+状态流转+边界用例）
├── test_07_check_tab.py            # 检查 Tab
├── test_08_doc_tab.py              # 文档 Tab
├── test_09_change_center.py        # 变更中心
├── test_10_report_center.py        # 报告中心
├── test_11_template_page.py        # 模板页
├── test_12_spec_center.py          # 规范中心页
├── test_13_settings.py             # 系统设置
├── test_14_toolbar.py              # 工具栏
├── test_15_edge_cases.py           # 边界用例
├── test_16_regression.py           # 回归测试
└── test_17_edit_change_dialog.py   # 编辑变更单对话框
```

### 9.2 V0.5.1 测试执行结果

- **L2 集成层**：104 passed, 2 skipped in 176.55s（17 个测试文件）
- **L3 端到端层**：15 场景全部完成，0 功能 bug，85 截图
- **超时截图机制验证**：conftest hooks 不影响正常测试（12 passed in 30.38s）

### 9.3 关键代码引用

- L3 测试脚本：[scripts/gui_plc_full_test.py](../scripts/gui_plc_full_test.py)
- L2 helpers：[tests/gui/helpers/interactions.py](../tests/gui/helpers/interactions.py)
- L2 conftest（含失败截图 hooks）：[tests/gui/conftest.py](../tests/gui/conftest.py)
- 统一测试入口：[scripts/run_tests.py](../scripts/run_tests.py)
- 主窗口实现：[auto_pm/ui/main_window.py](../auto_pm/ui/main_window.py)
- 变更 Tab：[auto_pm/ui/workspace/change_tab.py](../auto_pm/ui/workspace/change_tab.py)
- 变量表 Tab（V2.3 新增）：[auto_pm/ui/vartable/](../auto_pm/ui/vartable/)
- 规范中心页（V2.2 重构）：[auto_pm/ui/global_pages/spec_center.py](../auto_pm/ui/global_pages/spec_center.py)
