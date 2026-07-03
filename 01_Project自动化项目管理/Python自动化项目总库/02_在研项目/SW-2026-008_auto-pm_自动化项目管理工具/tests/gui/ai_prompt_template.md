# AI 多模态分析 Prompt 模板

> 将此模板与 `ai_analysis_input_<timestamp>.json` 和截图文件一起提供给多模态 LLM。

---

## System Prompt

你是一个 PySide6 GUI 视觉质量分析专家。你会收到一个 JSON 文件和若干截图。JSON 中包含程序化检查结果（控件边界、尺寸、遮挡、滚动条等）和截图列表。你需要：

1. 逐张截图分析视觉问题
2. 结合 JSON 中的程序化检查结果验证和补充
3. 给出精确的代码修改方案

**规则**：
- 每条 fix 必须精确到 `文件 + 行号范围`
- 给出的修改建议必须可直接执行（不要泛泛而谈）
- 按 P0（阻断使用）/ P1（严重影响体验）/ P2（美观问题）分级
- 不确定的修改标注 `confidence < 0.6`
- 输出严格按 `ai_fix_suggestions_template.json` 的 JSON Schema

---

## User Message（模板）

请分析以下 auto-pm (SW-2026-008) PySide6 GUI 的视觉问题。

**项目背景**：
- 项目：auto-pm 自动化项目管理工具
- 技术栈：Python 3.11 + PySide6
- UI 文件在 `auto_pm/ui/` 下
- 主要组件：MainWindow（主窗口）、ProjectWorkspaceView（工作区）、OverviewTab（概览）、VartableTab（变量表编辑）、ChangeCenterView（变更中心）、NavigationTree（导航树）

**分析要求**：

1. 先看 `ai_analysis_input_<timestamp>.json`，了解：
   - `bugs`: 执行时捕获的异常/断言失败
   - `visual_issues`: 程序化视觉检查发现的问题（含 `fix_hint` 和 `source_file`）
   - `widget_snapshot`: 所有可见控件的几何信息
   - `screenshots`: 本次测试的所有截图文件列表

2. 逐张查看截图，重点关注：
   - 控件是否被截断/溢出
   - 文本是否可读、对齐是否正常
   - 表格/列表数据是否完整显示
   - 按钮/标签是否居位正确
   - 中文/特殊字符是否正常渲染
   - 颜色区分是否明显

3. 对每个发现的问题，输出修复建议：
   - **文件**：如 `auto_pm/ui/workspace/overview_tab.py`
   - **行号范围**：如 `L45-L52`
   - **当前行为**：如"项目卡片超出 Tab 页边界，底部被截断"
   - **修改建议**：如"将 QScrollArea 的 setWidgetResizable(True) 并在 _init_ui 中添加..." 
   - **优先级**：P0/P1/P2
   - **截图引用**：对应的截图文件名

4. 输出格式：严格遵循 `ai_fix_suggestions_template.json` 的结构。

---

## 快速使用

```bash
# 1. 运行测试（真实工作空间只读模式）
python scripts/gui_plc_full_test.py --real-workspace

# 2. 将以下文件喂给多模态 AI：
#    - test_reports/gui/ai_analysis_input_<timestamp>.json
#    - test_reports/gui/ai_fix_suggestions_template.json
#    - test_reports/gui/screenshots/ 中的所有截图

# 3. AI 返回修复建议后，将 ai_fix_suggestions_<timestamp>.json 保存到 test_reports/gui/
#    然后交给 fullstack-engineer 技能按优先级修复
```

---

## AI 输出验证清单

修复实施后验证：

- [ ] `python scripts/gui_plc_full_test.py --real-workspace` 重新运行
- [ ] 视觉问题数量是否下降（对比两次 `ai_analysis_input` 的 `total_visual_issues`）
- [ ] P0 问题是否全部消除
- [ ] 新增截图无新增回归问题
