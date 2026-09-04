# V2.5.4 模板功能模块专项修复 Spec

## Why
V2.5.3 的修复未解决核心问题：
1. 模板管理界面点击刷新后只显示 1 个模板（应为 6 个）
2. 版本号仍显示 v1.0.0（config.py 修改未生效）
3. 内置模板数量与参考规范不一致（规范 6 个 vs 系统 5/6 个）

## What Changes - 聚焦范围

### 核心修复（本次必须完成）
1. **修复模板管理 UI 刷新逻辑** - 确保刷新后显示所有内置模板
2. **对齐参考规范的 6 个模板** - 确保 DEFAULT_TEMPLATES 包含全部 6 个
3. **验证版本号修复生效** - 确认 config.py 修改正确应用

### 交付物
4. **详细 GUI 测试方案** - 可复用的测试步骤文档
5. **功能模块迭代方案** - 标准化的迭代流程文档

## Impact
- Affected code:
  - `src/core/config.py` - 版本号配置
  - `src/ui/widgets/template_manager.py` - 模板管理 UI（刷新逻辑）
  - `src/core/constants.py` - 模板定义（需对比参考规范）
  - `src/services/template_service.py` - 模板服务层

## ADDED Requirements

### Requirement: 模板数量与参考规范一致
系统 SHALL 内置与 `06_项目模板规范` 完全一致的 6 个模板。

**参考规范中的 6 个模板**:
1. TPL-FULLLINE-AUTO-001 (自动化整线项目)
2. TPL-SINGLE-PLC-S001 (小型单机设备 PLC+HMI)
3. TPL-SINGLE-PLC-M001 (中大型单机设备 PLC+HMI)
4. TPL-SINGLE-ROBOT-001 (单机设备机器人)
5. TPL-UPGRADE-STD-001 (系统升级改造)
6. TPL-UPPER-STD-001 (上位机/数据系统)

#### Scenario: 刷新后显示所有模板
- **WHEN** 用户在模板管理界面点击"刷新"按钮
- **THEN** 表格必须显示所有 6 个内置模板，每行包含完整信息

### Requirement: 版本号正确显示
系统 SHALL 在窗口标题栏显示正确的版本号。

#### Scenario: 启动程序
- **WHEN** 用户运行 main.py
- **THEN** 标题栏必须显示 "Python项目管理工具 V{version.py中的VERSION}"

## MODIFIED Requirements

### Requirement: 模板管理 UI 健壮性
修改后的模板管理 UI SHALL 在任何情况下都能正确显示所有模板数据。

- 初始加载：显示 6 个模板
- 点击刷新：重新加载并显示 6 个模板（不能减少）
- 筛选操作：筛选后的结果正确，清除筛选后恢复 6 个

## 验收标准

### AC-1: 模板数量正确
- **Given**: 系统已加载内置模板
- **When**: 打开模板管理界面
- **Then**: 表格显示 **6 个**内置模板（非 5 个，非 1 个）
- **Verification**: `human-judgment` (截图)

### AC-2: 刷新功能正常
- **Given**: 模板管理界面已打开
- **When**: 点击"刷新"按钮
- **Then**: 表格仍然显示 **6 个**模板，且数据完整
- **Verification**: `human-judgment`

### AC-3: 版本号正确
- **Given**: 程序已启动
- **When**: 查看窗口标题栏
- **Then**: 显示 **V2.5.x** (x ≥ 3)，不能是 v1.0.0
- **Verification**: `human-judgment`

## Open Questions
- [ ] 为什么刷新后只显示 1 个模板？（可能是查询逻辑 bug）
- [ ] constants.py 中实际定义了多少个模板？
- [ ] 缺少哪个模板（对比参考规范的 6 个）？

## 交付物清单

### 1. GUI 测试方案文档
包含以下内容：
- 测试环境准备
- 分步测试步骤（带预期结果）
- 截图检查点
- 问题记录模板
- 通过/失败判定标准

### 2. 功能模块迭代方案文档
包含以下内容：
- 迭代触发条件
- 标准化迭代流程（Spec → 实现 → 测试 → 验收）
- 每阶段产出物清单
- 回归测试要求
- 发布标准