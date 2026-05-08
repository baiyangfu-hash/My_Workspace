# 全面深度QA审计 + 文档同步检查 Spec

## Why

用户要求对项目进行深度功能测试、问题排查、临时文件清理、以及文档与代码同步性审查。此前已完成多次迭代修复（模板/规范文档/总库管理/路径定位/级联删除），需要系统性验证所有功能的运行状态，发现隐藏问题，确保交付质量。

**核心目标**:
1. 逐一验证项目各功能模块的运行状态（代码层面静态分析 + 逻辑审查）
2. 识别并报告所有问题点及整改方向
3. 清理测试过程中产生的临时文件
4. 审查文档与代码的一致性和同步状态

## What Changes

### 输出1: 深度QA审计报告
- 覆盖全部9大功能模块的逐项检查
- 问题分级: 🔴 Critical / 🟡 Warning / ℹ️ Suggestion
- 每个问题附带: 位置(文件:行号)、根因分析、整改建议

### 输出2: 临时文件清理
- 清理 `06_交付物打包/archive_temp/` (ZIP已生成)
- 清理 `dist/` 以外的构建缓存
- 清理日志文件(可选)

### 输出3: 文档-代码同步性审查
- 对比 spec 中声明的功能 vs 代码实际实现
- 对比 01_项目文档 中的设计 vs src/ 中的代码
- 标注不一致项

## Impact

- Affected code: 无代码修改（仅读操作 + 清理）
- Affected docs: 可能产出审计报告
- Affected output: 审计报告 + 清理后的目录结构

## ADDED Requirements

### Requirement: 全面功能模块审计

系统 SHALL 接受覆盖全部功能模块的深度审计。

#### 审计范围（9大模块）

| # | 模块 | 关键文件 | 审计重点 |
|---|------|----------|----------|
| 1 | 项目管理 | project_service.py, project_dao.py, project_list.py | CRUD完整性、删除级联、搜索过滤 |
| 2 | 变更管理 | change_service.py, change_manager.py | 二维分类(Domain×Nature×Scope)、审批流 |
| 3 | 模板管理 | template_service.py, template_dao.py, template_manager.py | 内置模板保护、list_all/force_delete、编辑按钮 |
| 4 | 规范中心 | spec_service.py, spec_center.py | BUILTIN_SPECS(22条)、版本追踪、document_specs |
| 5 | 总库管理 | library_service.py, library_manager.py | 默认总库初始化幂等性、4Tab UI、扫描导入、root_path检测 |
| 6 | 新建项目 | new_project_dialog.py, project_service.py(create) | 路径自动填充、总库默认选中、归档关联、规范驱动文档生成 |
| 7 | 插件管理 | plugin_service.py, plugin_manager.py, plugin_market.py | 插件加载、配置、启用禁用 |
| 8 | 报告中心 | report_service.py, report_center.py | 统计报告生成 |
| 9 | 主窗口/导航 | main_window.py | 菜单完整性、Tab切换、信号连接 |

#### 审计方法
- **静态代码分析**: 读取每个关键文件，检查逻辑缺陷、硬编码、异常处理缺失
- **跨模块调用链**: 验证 Service → DAO → Model 层的数据一致性
- **边界条件**: 空值、None、空列表、不存在记录的处理

### Requirement: 问题分级报告

审计结果 SHALL 按严重度分级输出。

#### 分级标准
- **🔴 Critical**: 导致程序崩溃或数据丢失的Bug
- **🟡 Warning**: 功能异常但不崩溃，或有明显设计缺陷
- **ℹ️ Suggestion**: 代码质量改进建议（命名、注释、性能）

### Requirement: 临时文件清理

系统 SHALL 在审计完成后清理不必要的临时文件。

#### 清理范围
- `06_交付物打包/archive_temp/` — ZIP已生成，临时目录可删除
- `build/` 目录 — PyInstaller构建缓存（可保留也可清理）
- `__pycache__/` — Python字节码缓存
- *.pyc 文件

> 注意: 不删除 `dist/Python项目管理工具.exe` 和 `data/project_manager.db`

### Requirement: 文档-代码同步审查

系统 SHALL 审查项目文档与技术实现的同步性。

#### 审查维度
1. **需求→实现**: 02_规划过程/需求规格 → src/ 实际功能是否覆盖
2. **设计→代码**: 架构设计/详细设计 → 实际模块结构是否匹配
3. **变更记录→代码**: 版本变更台帐 → 代码变更是否一致
4. **Spec声明→实际**: 各迭代spec中声明的功能 → 是否真正实现
