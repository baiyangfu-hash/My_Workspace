# 修复删除项目级联错误 + 已迭代模块全面回归 Spec

## Why

### Bug A (截图): 删除项目时 "DELETE statement on table 'library_projects' expected to delete 1 row(s); Only 0 were matched." ⚠️ P0

**完整根因链路**:

1. `Project`模型 ([project.py:31](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/models/project.py#L31)) 定义了secondary relationship:
   ```python
   libraries = relationship("Library", secondary="library_projects", ...)
   ```

2. `ProjectDAO.delete()` ([project_dao.py:117-120](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/dao/project_dao.py#L117-L120)) 硬删除时直接 `session.delete(project)`:
   ```python
   if hard_delete:
       session.query(Change).filter(Change.project_id == project_id).delete()
       session.delete(project)  # ← 触发SQLAlchemy级联删除library_projects！
   ```

3. SQLAlchemy默认行为: 删除有secondary relationship的对象时，会同步尝试删除关联表行

4. **关键**: 老项目（如SW-2026-001）在总库管理迭代**之前**创建 → `library_projects`表中无对应记录 → 级联删除找不到行 → 报错

5. 新建项目的自动归档逻辑 ([project_service.py:255-271](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/services/project_service.py#L255-L271)) 是总库迭代后加的，老项目没经过此流程

### Bug B: 用户怀疑已迭代功能模块存在其他隐藏问题
需要全面回归检查所有已完成的迭代功能。

## What Changes

### 修改1: `project_dao.py` — 删除前清理library_projects关联 ⚠️ P0
- 在硬删除分支中，`session.delete(project)`之前，先显式删除`library_projects`中的关联记录
- 使用synchronize_session=False避免"expected to delete N rows"的严格校验

### 修改2: 全面回归检查已迭代模块 🔍 P1
逐一验证以下已完成迭代的运行状态:
- 模板模块 (template_module_fix)
- 规范驱动文档 (spec_driven_documents)  
- 总库管理 (library_management_fix)
- 路径修复 (fix_empty_project_path)

## Impact

- Affected specs: fix_empty_project_path (延续), library_management_fix (关联影响)
- Affected code:
  - `src/dao/project_dao.py` — `delete()` 方法
  - 全部已迭代模块需回归验证

## ADDED Requirements

### Requirement: 项目删除时的关联表安全清理

系统 SHALL 在硬删除项目前，安全清理所有关联表记录。

#### Scenario: 删除无library_projects关联的老项目
- **WHEN** 用户执行硬删除操作（如从项目管理界面点击删除确认）
- **AND** 目标项目是在总库管理模块迭代之前创建的（无library_projects记录）
- **THEN** 系统不报错，成功删除项目及其变更记录
- **AND** 不抛出 "DELETE statement expected to delete 1 row(s); Only 0 were matched" 异常

#### Scenario: 删除有library_projects关联的新项目
- **WHEN** 用户执行硬删除操作
- **AND** 目标项目有关联的总库记录
- **THEN** 系统先清理library_projects关联记录，再删除project和change记录
- **AND** 总库中该项目自动移除

## MODIFIED Requirements

### Requirement: ProjectDAO.delete() 方法增强

原方法在hard_delete分支中直接调用session.delete(project)，未处理级联关联表。
修改后增加关联表预清理步骤：
1. 先清理library_projects关联（使用synchronize_session=False宽容模式）
2. 再清理changes关联
3. 最后删除project本身
