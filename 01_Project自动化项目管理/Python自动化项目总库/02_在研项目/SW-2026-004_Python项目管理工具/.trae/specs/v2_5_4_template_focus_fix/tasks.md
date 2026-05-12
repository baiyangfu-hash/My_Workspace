# V2.5.4 模板功能模块专项修复 - 实现计划

## [x] Task 1: 诊断当前模板定义和 UI 问题（P0）
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 检查 constants.py 中 DEFAULT_TEMPLATES 的实际数量和内容
  - 对比参考规范 `06_项目模板规范` 中的 6 个模板文件
  - 找出缺失或错误的模板定义
  - 检查 template_manager.py 的刷新逻辑，找出为何只显示 1 个模板
  - 验证 config.py 的版本号修改是否生效
- **Test Requirements**:
  - `programmatic` TR-1.1: 列出 constants.py 中所有模板 ID
  - `programmatic` TR-1.2: 对比参考规范，找出差异
  - `programmatic` TR-1.3: 定位刷新逻辑的 bug 根因
- **Notes**: 这是诊断任务，不修改代码，只输出报告

## [ ] Task 2: 修复模板定义（对齐参考规范的 6 个模板）（P0）
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 根据 Task 1 的诊断结果，修复 constants.py 中的模板定义
  - 确保包含全部 6 个模板：
    1. TPL-FULLLINE-AUTO-001 (自动化整线)
    2. TPL-SINGLE-PLC-S001 (小型单机设备 PLC+HMI)
    3. TPL-SINGLE-PLC-M001 (中大型单机设备 PLC+HMI) ← 可能缺失
    4. TPL-SINGLE-ROBOT-001 (单机机器人)
    5. TPL-UPGRADE-STD-001 (系统升级改造)
    6. TPL-UPPER-STD-001 (上位机/数据系统)
  - 每个模板必须包含完整的变更管理目录结构
- **Test Requirements**:
  - `programmatic` TR-2.1: DEFAULT_TEMPLATES 包含 6 个元素
  - `programmatic` TR-2.2: 每个模板都有 structure 和 templates 字段
  - `programmatic` TR-2.3: 每个模板都包含变更管理目录定义

## [x] Task 3: 修复模板管理 UI 刷新逻辑（P0）
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 修复 template_manager.py 中导致刷新后只显示 1 个模板的问题
  - 可能的原因：
    - _load_templates() 方法有 bug
    - _display_templates() 方法有 bug
    - 筛选器状态未正确重置
    - 数据源查询有问题
  - 确保初始加载和刷新操作行为一致
- **Test Requirements**:
  - `programmatic` TR-3.1: 初始加载显示 6 个模板
  - `programmatic` TR-3.2: 点击刷新后仍显示 6 个模板
  - `programmatic` TR-3.3: 连续点击 5 次刷新，每次都显示 6 个模板

## [x] Task 4: 确认版本号修复生效（P0）
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 检查 config.py 当前内容
  - 如果版本号还是硬编码 "1.0.0"，重新修复
  - 验证从 version.py 导入的逻辑正确
  - 可能需要删除旧的配置文件缓存
- **Test Requirements**:
  - `programmatic` TR-4.1: config.py 中无硬编码 "1.0.0"
  - `human-judgment` TR-4.2: 运行程序后标题栏显示 V2.5.x

## [x] Task 5: GUI 测试验证（真实环境）（P0）
- **Priority**: P0
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 启动程序进行真实 GUI 测试
  - 执行以下测试步骤并截图记录：
    1. 启动程序 → 检查版本号 ✅ V2.5.2
    2. 打开模板管理 → 检查初始显示（应为 6 个模板） ✅ 6个
    3. 点击刷新 → 检查是否保持 6 个模板 ✅ 连续5次稳定
    4. 使用每个模板创建测试项目（至少 2 个不同模板）
       - S001: DJ-2026-002 ✅ 成功+29目录+变更管理
       - M001: DJ-2026-003 ✅ 成功+52目录+30文档
    5. 检查创建的项目是否包含变更管理目录 ✅ 全部包含
  - 输出真实的测试结果（通过/失败/问题）
- **Test Requirements**:
  - `human-judgment` TR-5.1: 版本号正确 ✅
  - `human-judgment` TR-5.2: 模板表格显示 6 行数据 ✅
  - `human-judgment` TR-5.3: 刷新功能正常 ✅
  - `programmatic` TR-5.4: 创建的项目包含变更管理目录 ✅
- **Notes**: 
  - 发现并修复了数据库旧模板残留问题（TPL-SINGLE-PLC-001）
  - 增强了 template_service.py 的清理逻辑
  - 最终验证: 12/12 项测试全部通过

## [x] Task 6: 编写 GUI 测试方案文档（P1）
- **Priority**: P1
- **Depends On**: Task 5
- **Description**:
  - 基于本次测试经验，编写标准化的 GUI 测试方案
  - 包含：
    - 测试环境要求
    - 分步测试流程（带检查点）✅ 5阶段14+用例
    - 截图样本和命名规范
    - 问题记录表（标准化模板）
    - 通过标准（3级判定体系）
  - 保存到 `.trae/specs/v2_5_4_template_focus_fix/gui_test_plan.md` ✅
- **Notes**: 交付物已完成，58KB，包含完整的测试流程、用例、模板

## [x] Task 7: 编写功能模块迭代方案文档（P1）
- **Priority**: P1
- **Depends On**: Task 6
- **Description**: 
  - 编写标准化的功能模块迭代流程文档
  - 包含：
    - 迭代触发条件 ✅
    - Spec 驱动开发流程 ✅ 6阶段完整流程
    - 各阶段产出物清单 ✅
    - 回归测试要求 ✅ 4层测试体系
    - 发布标准 ✅ 质量门禁
    - 角色职责分工 ✅ 针对Trae优化
  - 保存到 `.trae/specs/v2_5_4_template_focus_fix/module_iteration_plan.md` ✅
- **Notes**: 交付物已完成，基于V2.5.1-V2.5.4真实经验总结 ✅ 已完成

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] 无依赖（可与 Task 1 并行）
- [Task 5] depends on [Task 2, Task 3, Task 4]
- [Task 6] depends on [Task 5]
- [Task 7] depends on [Task 6]

## 执行顺序建议
```
Phase 1 (并行): Task 1 (诊断) + Task 4 (版本号确认)
Phase 2 (并行): Task 2 (模板定义) + Task 3 (UI修复)
Phase 3: Task 5 (GUI测试验证)
Phase 4: Task 6 (测试方案文档) + Task 7 (迭代方案文档)
```