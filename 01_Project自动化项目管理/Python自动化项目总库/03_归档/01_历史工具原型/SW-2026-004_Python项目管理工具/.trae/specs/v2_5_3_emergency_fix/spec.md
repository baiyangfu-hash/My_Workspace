# V2.5.3 紧急修复：GUI 功能全面验证与修复 Spec

## Why
用户反馈发现多个严重问题，之前的 V2.5.2 修复完全无效且存在虚假测试报告：
1. 模板管理界面表格空白（数据存在但 UI 不渲染）
2. 程序版本号显示为 v1.0.0（应为 V2.5.3）
3. 通过 GUI 创建的项目缺少变更管理目录（脚本创建的正常）
4. 测试数据污染数据库（大量 TEST_ 前缀项目）

**核心问题**：之前的"测试"只是代码层面的模拟，未验证真实 GUI 行为。

## What Changes - 问题清单

### P0 - 致命问题（必须立即修复）
1. **模板管理 UI 表格空白**
   - 现象：底部统计显示"共 5 个模板"，但表格内容为空
   - 根因：`_display_templates()` 方法执行但 QTableWidgetItem 未正确渲染
   
2. **版本号配置错误**
   - 现象：标题栏显示 "Python项目管理工具 v1.0.0"
   - 根因：`src/core/config.py` 中硬编码 `"version": "1.0.0"`，未从 `version.py` 动态读取
   
3. **GUI 创建项目缺少变更管理目录**
   - 现象：通过新建项目对话框创建的项目无 `04_变更管理/` 目录
   - 根因：GUI 调用的项目创建逻辑与 TemplateService 不同，或模板结构未正确传递

### P1 - 严重问题（影响使用体验）
4. **测试数据污染**
   - 数据库中存在 SW-2026-002~006, DJ-2026-001~004 等 TEST_ 前缀项目
   - 需要清理并提供安全的数据清理机制

### P2 - 改进项（提升质量）
5. **日志系统完善**
   - 已添加日志但需要验证是否输出到正确位置
   - 需要确保用户可轻松查看日志定位问题

## Impact
- Affected code:
  - `src/core/config.py` - 版本号配置（P0）
  - `src/ui/widgets/template_manager.py` - 模板管理 UI（P0）
  - `src/ui/dialogs/create_project_dialog.py` 或相关创建逻辑（P0）
  - `src/services/project_service.py` - 项目服务层（P0/P1）
  - `data/project_manager.db` - 测试数据（P1）

## ADDED Requirements

### Requirement: 版本号必须动态读取
系统 SHALL 从 `src/core/version.py` 动态读取版本信息，禁止在配置文件中硬编码。

#### Scenario: 启动程序时显示正确版本号
- **WHEN** 用户启动应用程序
- **THEN** 标题栏和关于对话框必须显示 `version.py` 中的 VERSION 值（V2.5.3）
- **Verification**: `programmatic`

### Requirement: 模板管理 UI 必须正确渲染
系统 SHALL 在模板管理界面正确显示所有内置模板的完整信息。

#### Scenario: 打开模板管理选项卡
- **WHEN** 用户切换到"模板管理"选项卡
- **THEN** 表格必须显示所有 5 个内置模板，包含以下列：
  - 模板ID、模板名称、版本、编译器、适用场景、业务线、内置、描述、操作按钮
- **Verification**: `human-judgment`

#### Scenario: 点击刷新按钮
- **WHEN** 用户点击"刷新"按钮
- **THEN** 表格必须重新加载数据并正确显示，不能出现空白
- **Verification**: `human-judgment`

### Requirement: GUI 创建项目必须包含完整目录结构
系统 SHALL 确保通过 GUI 新建项目功能创建的项目与模板定义完全一致。

#### Scenario: 使用任意模板通过 GUI 创建项目
- **WHEN** 用户在新建项目对话框中选择任意模板并点击"创建"
- **THEN** 生成的项目必须包含完整的目录结构，特别是：
  - `00_项目管理/04_变更管理/01_变更单/`
  - `00_项目管理/04_变更管理/03_变更管理规范/`
  - `00_项目管理/04_变更管理/04_变更记录/`
- **AND** 变更管理相关文件必须被正确生成
- **Verification**: `programmatic` + `human-judgment`

## MODIFIED Requirements

### Requirement: Config 模块重构
修改后的 Config 模块 SHALL 提供动态版本查询接口。

```python
# 之前（错误）
Config.get('version')  # 返回硬编码的 "1.0.0"

# 之后（正确）
from src.core.version import VERSION
Config.get_version() or VERSION  # 返回 version.py 中的值
```

### Requirement: 项目创建流程统一
修改后的项目创建流程 SHALL 确保 GUI 和 API 使用相同的服务层逻辑。

## REMOVED Requirements
无

## 验收标准（AC）

### AC-1: 版本号显示正确
- **Given**: 程序已启动
- **When**: 查看窗口标题栏
- **Then**: 必须显示 "Python项目管理工具 V2.5.3"
- **Verification**: `human-judgment`

### AC-2: 模板管理界面正常
- **Given**: 程序已启动
- **When**: 切换到"模板管理"选项卡 + 点击"刷新"
- **Then**: 表格显示 5 个内置模板，每行包含完整信息
- **Verification**: `human-judgment`

### AC-3: GUI 创建项目结构完整
- **Given**: 用户选择 TPL-SINGLE-PLC-001 模板
- **When**: 通过 GUI 创建新项目 DJ-2026-TEST-FIX
- **Then**: 项目目录包含 `00_项目管理/04_变更管理/` 及其子目录和文件
- **Verification**: `programmatic` (检查文件系统) + `human-judgment`

### AC-4: 无测试数据污染
- **Given**: 清理操作已完成
- **When**: 查看"项目管理"选项卡
- **Then**: 不存在任何 TEST_ 或 SW-2026-00[2-6] 前缀的测试项目
- **Verification**: `programmatic`

## Open Questions
- [ ] 为什么 GUI 创建的项目缺少变更管理目录？（需要深入调试 project_service.py）
- [ ] template_manager.py 的 _display_tables 方法为何不渲染？
- [ ] 是否还有其他硬编码的配置值？

## 测试方案（必须严格执行）

### Phase 1: 单元测试（代码层面）
1. 验证 Config.get('version') 返回值
2. 验证 TemplateService.list_templates() 返回的对象属性完整性
3. 验证 ProjectService.create_project() 生成的目录结构

### Phase 2: GUI 集成测试（真实环境）
1. 启动程序 → 检查标题栏版本号
2. 切换到模板管理 → 截图记录初始状态
3. 点击刷新 → 截图记录刷新后状态
4. 使用每种模板各创建 1 个测试项目 → 验证目录结构
5. 检查生成的项目中变更管理目录是否存在

### Phase 3: 回归测试
1. 总库管理模块项目数统计
2. 变更管理模块能否识别新创建的项目
3. 所有其他功能模块基本操作

### Phase 4: 数据清理
1. 删除所有测试项目（TEST_ 前缀）
2. 验证数据库干净
3. 备份清理后的数据库