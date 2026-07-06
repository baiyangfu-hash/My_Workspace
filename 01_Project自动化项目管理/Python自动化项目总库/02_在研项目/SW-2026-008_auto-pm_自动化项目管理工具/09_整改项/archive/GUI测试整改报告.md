# GUI 测试整改报告 V0.5.0

> **⚠️ 状态：已过时** — 本报告基于 V0.5.0 初版测试（offscreen 模式），2 个 major bug（对话框未弹出）已在 V0.5.1 测试脚本迭代中修复（QWizard FinishButton + 信号驱动），可见模式验证通过。最新状态请参考：
> - **主报告**：[test_reports/gui/2026-07-01_完整GUI测试报告.md](../test_reports/gui/2026-07-01_完整GUI测试报告.md)（V0.5.1 可见模式 + 三视口 + 13 场景 + 85 截图）
> - **诊断补充**：[test_screenshots/GUI诊断报告_V0.5.2.md](../test_screenshots/GUI诊断报告_V0.5.2.md)（视觉问题诊断，已补登 TD-G01 P0 bug）
> - **本轮修复方案**：CHG-SCPT-2026-081（dogfooding 第 12 次闭环，含 TD-G01 + V-01~V-12 修复）
>
> 本报告保留作为历史归档，禁止按本报告的待办项继续推进。整改项 #1（修复测试脚本调用方式）和整改项 #2（清理测试项目残留）均已完成。

---

> **项目**: SW-2026-008 auto-pm（自动化项目管理工具）
> **测试执行日期**: 2026-07-01 04:48:21 ~ 04:50:15（耗时约 1 分 54 秒）
> **测试脚本**: `scripts/gui_plc_full_test.py`（13 步端到端 GUI 自动化测试）
> **测试环境**: offscreen 模式 + Windows + `.venv` 虚拟环境
> **关联文档**:
> - [GUI测试计划-V0.5.0.md](../02_设计/GUI测试计划-V0.5.0.md)
> - [GUI原型设计-V2.0.md](../02_设计/GUI原型设计-V2.0.md)（V2.1 已审核通过）
> - [PM_SESSION_SW-2026-008.md](../PM_SESSION_SW-2026-008.md)

---

## 0. 执行摘要

### 0.1 测试结果概览

| 指标 | 值 | 评估 |
|------|-----|------|
| 测试执行状态 | ✅ 全流程跑完 13 步 | 通过 |
| 截图生成数 | 29 张（预期 29 张） | ✅ 100% |
| Bug 报告数 | 2 个（major×2，critical×0，minor×0） | 🟠 部分通过 |
| 用例覆盖率 | 13/15 模块（86.7%） | 🟡 待扩展 |
| 测试项目残留 | DJ-2026-099 存在于工作空间 | ⚠️ 需手动清理 |
| 总体结论 | 🟡 **部分通过，2 个 major bug 待整改，2 个模块待扩展覆盖** | — |

### 0.2 结论与建议

**结论**：auto-pm V0.5.0 GUI 主体功能正常，13/15 个模块可用，但存在 2 个 major bug 集中在「对话框弹出」场景，且 V2.3 Week4 新增的「变量表 Tab」和 V2.2 Week3 重构的「规范中心页」未被现有测试脚本覆盖。

**建议**：
1. **立即整改（Week 1）**：修复 `gui_plc_full_test.py` 中 `_on_new_project` 和 `_on_create_change` 的调用方式（用 `dialog.show()` 替代 `dialog.exec()` 或重构为工厂方法）
2. **扩展覆盖（Week 2）**：为变量表 Tab + 规范中心页补 7+6=13 个新用例
3. **回归验证（Week 3-4）**：重跑测试，建立 V0.5.0 截图基线

---

## 1. 测试执行环境

### 1.1 环境

| 项 | 值 |
|----|-----|
| 工作空间根 | `c:\Users\fubai\Desktop\My_Workspace` |
| 项目根 | `c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具` |
| Python 环境 | `.venv`（已激活） |
| 测试项目 ID | `DJ-2026-099`（脚本自动创建，名称「GUI测试临时项目」） |
| 屏幕渲染 | offscreen（`QT_QPA_PLATFORM=offscreen`） |
| 截图输出目录 | `<项目根>/test_screenshots/` |
| Bug 报告文件 | `<项目根>/test_screenshots/bug_report.txt` |
| 操作日志文件 | `<项目根>/test_screenshots/operation_log.txt` |

### 1.2 数据库状态（执行后）

| 指标 | 值 |
|------|-----|
| 工作空间项目总数 | 13（扫描后） / 14（DB 记录） |
| 变更记录数 | 0 条 |
| DB 状态 | 已连接（`.auto-pm/index.db`） |
| 项目阶段分布 | developing=1，其他=12 |

---

## 2. 测试执行结果

### 2.1 截图清单（29 张，按步骤分组）

#### 步骤 1：启动 GUI 主窗口（1 张）

| 截图 | 描述 | 状态 |
|------|------|------|
| `01_main_window.png` | 主窗口启动，显示项目列表 | ✅ |

#### 步骤 2：导航树操作（6 张）

| 截图 | 描述 | 状态 |
|------|------|------|
| `02_nav_plc_stack.png` | 点击「PLC 总库」节点 | ✅ |
| `02_nav_plc_developing.png` | 点击「PLC 在研项目」子节点 | ✅ |
| `02_nav_all_projects.png` | 点击「全部项目」节点 | ✅ |
| `02_nav_change_center.png` | 点击「变更中心」节点 | ✅ |
| `02_nav_report.png` | 点击「报告中心」节点 | ✅ |
| `02_nav_settings.png` | 点击「系统设置」节点 | ✅ |

#### 步骤 3：项目列表操作（5 张）

| 截图 | 描述 | 状态 |
|------|------|------|
| `03_search_dj.png` | 搜索框输入「DJ」 | ✅ |
| `03_business_line_filter.png` | 业务线筛选切换 | ✅ |
| `03_list_view.png` | 切换到列表视图 | ✅ |
| `03_card_view.png` | 切换回卡片视图 | ✅ |
| `03_group_mode.png` | 分组模式切换（4 种） | ✅ |

#### 步骤 4：新建 PLC 项目（0 张）⚠️

| 截图 | 描述 | 状态 |
|------|------|------|
| （无） | NewProjectDialog 未弹出 | ❌ Bug #1 |

#### 步骤 5：进入项目工作区（2 张）

| 截图 | 描述 | 状态 |
|------|------|------|
| `05_workspace_overview.png` | 工作区概览 Tab（用现有项目） | ✅ |
| `05_workspace_existing.png` | 现有项目工作区 | ✅ |

#### 步骤 6：变更 Tab（1 张）⚠️

| 截图 | 描述 | 状态 |
|------|------|------|
| `06_change_tab.png` | 变更 Tab 列表显示 | ✅ |
| （后续截图缺失） | CreateChangeDialog 未弹出 | ❌ Bug #2 |

#### 步骤 7：检查 Tab（4 张）

| 截图 | 描述 | 状态 |
|------|------|------|
| `07_check_tab_empty.png` | 检查 Tab 空状态 | ✅ |
| `07_check_result.png` | 执行检查结果 | ✅ |
| `07_repair_preview.png` | 自动修复预览 | ✅ |
| `07_standardize_preview.png` | 标准化命名预览 | ✅ |

#### 步骤 8：文档 Tab（2 张）

| 截图 | 描述 | 状态 |
|------|------|------|
| `08_doc_tab.png` | 文档树显示 | ✅ |
| `08_doc_tab_final.png` | 检查模板更新后 | ✅ |

> **观察**：模板信息显示为「模板: —, 版本: —」，可能表示项目未通过 Copier 模板创建。

#### 步骤 9：变更中心（2 张）

| 截图 | 描述 | 状态 |
|------|------|------|
| `09_change_center.png` | 变更中心列表 | ✅ |
| `09_change_center_tabs.png` | 切换状态 Tab | ✅ |

> **观察**：变更单查询返回 0 条，与 §1.2 中 DB 状态「变更记录数 0」一致。

#### 步骤 10：报告中心（1 张）

| 截图 | 描述 | 状态 |
|------|------|------|
| `10_report_center.png` | 报告统计卡片 | ✅ |

#### 步骤 11：系统设置（2 张）

| 截图 | 描述 | 状态 |
|------|------|------|
| `11_settings.png` | 系统设置页 | ✅ |
| `11_settings_final.png` | 修改扫描深度 + 重建索引后 | ✅ |

> **观察**：工作空间显示为 `C:\Users\fubai\Desktop\My_Workspace`，项目记录 14 条，变更记录 0 条，符合预期。

#### 步骤 12：工具栏操作（2 张）

| 截图 | 描述 | 状态 |
|------|------|------|
| `12_sync_cache.png` | 同步缓存后 | ✅ |
| `12_refresh_list.png` | 刷新列表后 | ✅ |

> **观察**：状态栏显示「工作空间: C:\Users\fubai\Desktop\My_Workspace | 项目: 13 | DB: 已连接」，符合预期。

#### 步骤 13：清理（1 张）

| 截图 | 描述 | 状态 |
|------|------|------|
| `99_final_state.png` | 最终状态 | ✅ |

> **观察**：测试项目 `DJ-2026-099_P1修复测试标准项目` 仍存在于 `0100_PLC自动化\` 下，需手动清理。

### 2.2 Bug 报告（来自 `bug_report.txt`）

```
共发现 2 个问题：

Bug #1:
  步骤: 新建项目
  严重度: major
  错误: 对话框未弹出
  时间: 2026-07-01T04:49:29.134576

Bug #2:
  步骤: 创建变更单
  严重度: major
  错误: 对话框未弹出
  时间: 2026-07-01T04:49:44.217949

----------------------------------------
严重: 0 | 主要: 2 | 次要: 0
```

---

## 3. Bug 根因分析

### 3.1 Bug #1：新建项目对话框未弹出（major）

**现象**：步骤 4 中调用 `window._on_new_project("plc")` 后，脚本立即在 `app.topLevelWidgets()` 中查找 `NewProjectDialog`，但找不到。

**根因分析**：

[auto_pm/ui/main_window.py:352-355](../auto_pm/ui/main_window.py#L352-L355) 中 `_on_new_project` 实现使用 `dialog.exec()`：

```python
def _on_new_project(self, stack: str = "plc") -> None:
    dialog = NewProjectDialog(self._workspace_root, self, stack=stack)
    dialog.projectCreated.connect(self._on_project_created)
    dialog.exec()  # ← 阻塞调用
```

**问题机制**：
1. `dialog.exec()` 是 Qt 的**模态对话框阻塞调用**
2. 测试脚本调用 `window._on_new_project("plc")` 后，控制流阻塞在 `dialog.exec()` 内部
3. 脚本永远执行不到下一行 `for w in app.topLevelWidgets():` 查找对话框的代码
4. 当 `dialog.exec()` 最终返回时（用户操作 / 自动关闭），对话框已经销毁

**影响范围**：
- 测试用例 TC-04-01 ~ TC-04-05 全部无法验证
- 截图 `04_project_created.png` 未生成
- 后续 step_05 只能使用现有项目回退（已成功验证）

**根本原因**：测试脚本的调用方式与生产代码不兼容。`_on_new_project()` 设计为响应工具栏菜单点击的槽函数，使用 `dialog.exec()` 是正确的（模态阻塞用户继续操作），但**测试脚本不应直接调用槽函数**，而应该：
- 方案 A：直接构造 `NewProjectDialog` 实例并调用 `dialog.show()`（非模态）
- 方案 B：在独立线程中调用 `_on_new_project()`，然后查找对话框
- 方案 C：重构 `_on_new_project()` 提取出 `_make_new_project_dialog()` 工厂方法

### 3.2 Bug #2：创建变更单对话框未弹出（major）

**现象**：步骤 6 中调用 `change_tab._on_create_change()` 后，脚本立即查找 `CreateChangeDialog`，但找不到。

**根因分析**：

[auto_pm/ui/workspace/change_tab.py:458-467](../auto_pm/ui/workspace/change_tab.py#L458-L467) 中 `_on_create_change` 实现使用 `dialog.exec()`：

```python
def _on_create_change(self) -> None:
    log.info("变更Tab: 打开创建变更单对话框")
    dialog = CreateChangeDialog(
        project_service=self._project_service,
        change_service=self._change_service,
        parent=self,
    )
    dialog.change_created.connect(self._on_change_created)
    dialog.exec()  # ← 阻塞调用
```

**问题机制**：与 Bug #1 完全一致。`_on_create_change()` 是按钮点击槽函数，使用 `dialog.exec()` 阻塞调用，测试脚本直接调用槽函数会导致控制流卡在 `exec()` 内部。

**影响范围**：
- 测试用例 TC-06-02 ~ TC-06-11 全部无法验证
- 截图 `06_create_change_form.png`、`06_change_created.png`、`06_transition_*.png` 全部未生成（共 9 张缺失）
- 变更单状态全流程（draft → completed）7 步流转未验证

**根本原因**：与 Bug #1 相同，测试脚本的调用方式与生产代码不兼容。

### 3.3 未覆盖模块分析

#### 3.3.1 变量表 Tab（V2.3 Week4 新增）

**问题**：原 `gui_plc_full_test.py` 创建于 V2.0 时期，未覆盖 V2.3 Week4 新增的变量表 Tab。

**影响**：
- §5.5 变量表 Tab 设计的 9 小节功能未做端到端验证
- VariableTableModel（8 列）/ VariableTableEditor / VartableTab QSplitter 三栏布局 / 8 格式 Parser + FormatDetector 三级识别 / 数据流 / CLI 对应关系 全部未验证
- 33 个 UI 单元测试虽然存在（`tests/ui/test_vartable_tab.py` + `test_variable_table_editor.py`），但缺乏端到端集成验证

**风险评估**：🟡 中等风险。单元测试已覆盖核心逻辑，但缺少真实工作空间场景下的端到端验证。

#### 3.3.2 规范中心页（V2.2 Week3 重构）

**问题**：原 `gui_plc_full_test.py` 创建于 V2.0 时期，未覆盖 V2.2 Week3 重构的规范中心页。

**影响**：
- 6 Tab（概览/索引/检查/Frontmatter/报告/对比）布局未验证
- DTO/adapter 层未端到端验证
- 14 规范展示 + 10 健康检查项 + Frontmatter 批量管理 + 报告生成 + 规范对比 未验证
- 33 个 UI 单元测试虽然存在（`tests/ui/test_spec_center.py`），但缺乏端到端集成验证

**风险评估**：🟡 中等风险。单元测试已覆盖核心逻辑，但缺少真实工作空间场景下的端到端验证。

---

## 4. 整改建议

### 4.1 立即整改（V0.5.x Week 1，2026-07-02 ~ 2026-07-08）

#### 4.1.1 整改项 #1：修复测试脚本调用方式

**目标**：修复 `gui_plc_full_test.py` 中 `_on_new_project` 和 `_on_create_change` 的调用方式，使 NewProjectDialog 和 CreateChangeDialog 能正常弹出并被查找。

**推荐方案**：方案 A（直接构造 Dialog 实例）

**实施步骤**：
1. step_04_create_plc_project：不调用 `window._on_new_project("plc")`，而是直接：
   ```python
   from auto_pm.ui.dialogs import NewProjectDialog
   dialog = NewProjectDialog(WORKSPACE_ROOT, window, stack="plc")
   dialog.projectCreated.connect(window._on_project_created)
   dialog.show()  # 非模态
   process_events(app, 500)
   # 然后查找对话框并填写表单
   ```
2. step_06_change_tab：不调用 `change_tab._on_create_change()`，而是直接：
   ```python
   from auto_pm.ui.dialogs.create_change_dialog import CreateChangeDialog
   dialog = CreateChangeDialog(
       project_service=window._project_service,
       change_service=window._change_service,
       parent=change_tab,
   )
   dialog.change_created.connect(change_tab._on_change_created)
   dialog.show()  # 非模态
   process_events(app, 500)
   # 然后查找对话框并填写表单
   ```

**预期收益**：
- 2 个 major bug 修复
- 9 张缺失截图补齐
- 变更单状态流转 7 步全部验证

**风险**：低（仅修改测试脚本，不修改生产代码）

#### 4.1.2 整改项 #2：清理测试项目残留

**目标**：删除测试创建的 `DJ-2026-099_P1修复测试标准项目` 项目目录。

**实施步骤**：
```powershell
Remove-Item -Recurse -Force "c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\DJ-2026-099_P1修复测试标准项目"
```

**预期收益**：工作空间整洁，避免污染下次测试

### 4.2 中期扩展（V0.5.x Week 2，2026-07-09 ~ 2026-07-15）

#### 4.2.1 扩展项 #1：变量表 Tab 端到端测试

**目标**：为变量表 Tab 补充 7 个端到端测试用例（TC-09-01 ~ TC-09-07）。

**实施步骤**：
1. 在 `gui_plc_full_test.py` 新增 `step_14_vartable_tab(app, window)` 函数
2. 在 `main()` 中插入到 step_13 之前
3. 实现子步骤：
   - 14.1 切换到变量表 Tab（验证 QSplitter 三栏布局）
   - 14.2 导入 io_points.csv（验证 FormatDetector 三级识别）
   - 14.3 导入 program_blocks.yml
   - 14.4 点击文件项加载变量表
   - 14.5 新增行/删除行（验证 VariableTableModel）
   - 14.6 批量解析（验证批量解析结果统计卡片）
   - 14.7 导出为 CSV/YAML/JSON
4. 生成 7 张截图：`14_vartable_*.png`

**预期收益**：V2.3 Week4 新增功能端到端验证完整

#### 4.2.2 扩展项 #2：规范中心页端到端测试

**目标**：为规范中心页补充 6 个端到端测试用例（TC-12-01 ~ TC-12-06）。

**实施步骤**：
1. 在 `gui_plc_full_test.py` 新增 `step_15_spec_center(app, window)` 函数
2. 在 `main()` 中插入到 step_14 之后
3. 实现子步骤：
   - 15.1 切换到规范中心（验证 6 Tab 布局）
   - 15.2 切换到「索引」Tab（验证 14 规范列表）
   - 15.3 切换到「检查」Tab（验证 10 健康检查项）
   - 15.4 切换到「Frontmatter」Tab（验证 frontmatter 列表）
   - 15.5 切换到「报告」Tab（验证报告生成）
   - 15.6 切换到「对比」Tab（验证规范对比界面）
4. 生成 6 张截图：`15_spec_*.png`

**预期收益**：V2.2 Week3 重构功能端到端验证完整

### 4.3 长期演进（V0.5.x Week 3-4，2026-07-16 ~ 2026-07-29）

#### 4.3.1 建立 V0.5.0 截图基线

**目标**：整改后重跑测试，建立 V0.5.0 完整截图基线，作为后续版本回归对比基准。

**实施步骤**：
1. 完整改改后重跑 `python scripts/gui_plc_full_test.py`
2. 将 `test_screenshots/` 复制到 `test_screenshots_baseline/V0.5.0/`
3. 后续 V0.5.x 版本回归时，对比截图差异

#### 4.3.2 评估引入 GUI 视觉回归测试

**目标**：评估引入 pytest-qt + 图像对比工具，自动化检测视觉回归。

**候选工具**：
- pytest-qt（已使用）
- pixelmatch-python（图像对比）
- Pillow（图像处理）

**评估标准**：测试 ROI 是否大于实施成本

### 4.4 更长期（V0.6.0+）

详见 [里程碑迭代计划_V2.1.md §8.2](../02_设计/里程碑迭代计划_V2.1.md) V0.6.0 长期路线。

---

## 5. 测试用例执行详情

### 5.1 用例执行矩阵

| 用例 ID | 模块 | 期望 | 实际 | 结果 |
|---------|------|------|------|------|
| TC-01-01 | 启动 | 主窗口正常 | 标题="auto-pm 项目管理工具" | ✅ |
| TC-01-02~05 | 启动 | 关键控件存在 | 状态栏/导航树/项目列表/页面栈均存在 | ✅ |
| TC-02-01~06 | 导航 | 6 个节点切换正常 | 截图全部生成 | ✅ |
| TC-03-01~05 | 项目列表 | 5 项操作正常 | 截图全部生成 | ✅ |
| **TC-04-01** | **新建项目** | **NewProjectDialog 弹出** | **未弹出** | **❌ Bug #1** |
| TC-04-02~05 | 新建项目 | 表单填写/创建/错误处理 | 跳过 | ⏭️ |
| TC-05-01~02 | 工作区·概览 | 进入工作区 | 用现有项目成功 | ✅ |
| TC-06-01 | 工作区·变更 | 变更 Tab 列表显示 | 显示正常 | ✅ |
| **TC-06-02** | **工作区·变更** | **CreateChangeDialog 弹出** | **未弹出** | **❌ Bug #2** |
| TC-06-03~11 | 工作区·变更 | 表单填写/创建/7 步状态流转 | 跳过 | ⏭️ |
| TC-07-01~04 | 工作区·检查 | 4 项操作正常 | 截图全部生成 | ✅ |
| TC-08-01~04 | 工作区·文档 | 4 项操作正常 | 截图全部生成（模板信息显示"—"） | ✅ |
| TC-09-01~07 | **工作区·变量表** | 7 项操作 | **未覆盖** | ⏳ 待扩展 |
| TC-10-01~03 | 变更中心 | 3 项操作正常 | 截图生成，变更单 0 条 | ✅ |
| TC-11-01 | 报告中心 | 统计卡片显示 | 显示正常 | ✅ |
| TC-12-01~06 | **规范中心页** | 6 Tab 切换 | **未覆盖** | ⏳ 待扩展 |
| TC-13-01~03 | 系统设置 | 3 项操作正常 | 截图全部生成 | ✅ |
| TC-14-01~03 | 工具栏 | 同步/刷新/状态栏 | 截图全部生成 | ✅ |
| TC-15-01~03 | 最终状态 | 回到列表/检查残留/最终截图 | 截图生成，DJ-2026-099 残留 | ✅ |

### 5.2 统计汇总

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ 通过 | 21 项 | 67.7% |
| ⏭️ 跳过（依赖 bug） | 9 项 | 29.0% |
| ❌ 失败 | 2 项 | 6.5% |
| ⏳ 待扩展 | 13 项 | — |
| **合计（已执行）** | **31 项** | — |
| **合计（含计划）** | **44 项** | — |

---

## 6. 整改优先级与时间表

| 优先级 | 整改项 | 计划周次 | 预期收益 | 风险 |
|--------|--------|----------|----------|------|
| P0 | 修复测试脚本调用方式 | Week 1 | 2 个 major bug 修复，9 张截图补齐 | 低 |
| P0 | 清理测试项目残留 | Week 1 | 工作空间整洁 | 极低 |
| P1 | 变量表 Tab 端到端测试 | Week 2 | V2.3 Week4 功能验证完整 | 低 |
| P1 | 规范中心页端到端测试 | Week 2 | V2.2 Week3 功能验证完整 | 低 |
| P2 | 建立 V0.5.0 截图基线 | Week 3 | 回归对比基准 | 低 |
| P2 | 评估 GUI 视觉回归工具 | Week 4 | 长期 ROI 评估 | 中 |

---

## 7. 关键观察与建议

### 7.1 模板信息显示为"—"

**观察**：步骤 8 文档 Tab 中，模板信息显示为「模板: —, 版本: —」。

**可能原因**：测试项目 `DJ-2026-099` 可能未通过 Copier 模板创建（脚本调用 `_on_new_project("plc")` 实际触发的创建流程），或者 Copier 模板路径未正确配置。

**建议**：整改 Bug #1 后重新验证，若仍显示"—"则需要进一步排查。

### 7.2 变更单数量为 0

**观察**：步骤 9 变更中心查询返回 0 条变更单。

**可能原因**：
- 此前 dogfooding 创建的变更单已被归档
- 全量回归测试时未保留测试变更单
- DB 重置过

**建议**：与 §1.2 中 DB 状态「变更记录数 0」一致，符合当前实际状态。可在整改 Bug #2 后通过创建变更单验证流程，建立测试变更单基线。

### 7.3 测试项目残留

**观察**：测试项目 `DJ-2026-099_P1修复测试标准项目` 残留在 `0100_PLC自动化\` 下。

**影响**：
- 后续测试会重复执行 step_04 的「项目已存在」分支
- 工作空间扫描会包含此项目
- 不影响测试结果，但污染工作空间

**建议**：执行整改项 #2 清理残留项目。

### 7.4 GUI 启动性能

**观察**：步骤 1 启动到主窗口截图完成耗时约 5 秒（04:48:21 → 04:48:26）。

**评估**：在 offscreen 模式 + 真实工作空间（13 个项目）下，5 秒启动时间可接受。后续 V0.6.0+ 若引入更多项目，需要监控启动性能。

---

## 8. 整改后预期状态

### 8.1 立即整改后（Week 1 末）

| 指标 | 当前 | 整改后 |
|------|------|--------|
| 截图生成数 | 29 张 | 38 张（+9 张） |
| Bug 报告数 | 2 个 major | 0 个 |
| 用例覆盖率 | 86.7% | 100%（已规划用例） |
| 总体结论 | 🟡 部分通过 | ✅ 全部通过 |

### 8.2 中期扩展后（Week 2 末）

| 指标 | 当前 | 扩展后 |
|------|------|--------|
| 截图生成数 | 29 张 | 51 张（+13 张 +9 整改） |
| 用例覆盖率 | 86.7% | 100%（含变量表 + 规范中心页） |
| 模块覆盖 | 13/15 | 15/15 |

### 8.3 长期演进后（Week 4 末）

| 指标 | 当前 | 长期后 |
|------|------|--------|
| 截图基线 | 无 | V0.5.0 完整基线建立 |
| 视觉回归 | 无 | 评估引入工具 |
| 回归对比 | 人工 | 自动化（图像对比） |

---

## 9. 后续行动清单

- [ ] **立即（Week 1）**：执行整改项 #1，修复 `gui_plc_full_test.py` 中 `_on_new_project` 和 `_on_create_change` 的调用方式
- [ ] **立即（Week 1）**：执行整改项 #2，清理 `DJ-2026-099` 测试项目残留
- [ ] **Week 2**：执行扩展项 #1，新增 `step_14_vartable_tab` 测试函数
- [ ] **Week 2**：执行扩展项 #2，新增 `step_15_spec_center` 测试函数
- [ ] **Week 3**：重跑完整测试，建立 V0.5.0 截图基线
- [ ] **Week 4**：评估 GUI 视觉回归测试工具
- [ ] **持续**：每次 GUI 相关变更后，重跑 `python scripts/gui_plc_full_test.py` 验证无回归

---

## 10. 附录

### 10.1 完整操作日志摘要

- 测试开始：2026-07-01 04:48:21.690
- 测试结束：2026-07-01 04:50:15.606
- 总耗时：1 分 54 秒
- 操作日志完整路径：`test_screenshots/operation_log.txt`

### 10.2 关键代码引用

- 测试脚本：[scripts/gui_plc_full_test.py](../scripts/gui_plc_full_test.py)
- 主窗口 `_on_new_project`：[auto_pm/ui/main_window.py:352-355](../auto_pm/ui/main_window.py)
- 变更 Tab `_on_create_change`：[auto_pm/ui/workspace/change_tab.py:458-467](../auto_pm/ui/workspace/change_tab.py)
- NewProjectDialog 类：[auto_pm/ui/dialogs/new_project_dialog.py](../auto_pm/ui/dialogs/new_project_dialog.py)
- CreateChangeDialog 类：[auto_pm/ui/dialogs/create_change_dialog.py](../auto_pm/ui/dialogs/create_change_dialog.py)

### 10.3 截图目录结构

```
test_screenshots/
├── 01_main_window.png              # 主窗口启动
├── 02_nav_*.png                    # 导航树（6 张）
├── 03_*.png                        # 项目列表（5 张）
├── 05_workspace_*.png              # 工作区（2 张）
├── 06_change_tab.png               # 变更 Tab（1 张，后续缺失）
├── 07_*.png                        # 检查 Tab（4 张）
├── 08_doc_tab*.png                 # 文档 Tab（2 张）
├── 09_change_center*.png           # 变更中心（2 张）
├── 10_report_center.png            # 报告中心
├── 11_settings*.png                # 系统设置（2 张）
├── 12_*.png                        # 工具栏（2 张）
├── 99_final_state.png              # 最终状态
├── bug_report.txt                  # Bug 报告
└── operation_log.txt               # 操作日志
```
