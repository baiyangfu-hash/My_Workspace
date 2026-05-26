# Tasks - 修复模板占位符替换Bug + 变更管理结构完善

## 任务列表

- [x] **Task 1**: 修复 P0 Bug - project_service.py 中 create_project() 方法的路径占位符替换 ✅
  - [x] 1.1 在 `src/services/project_service.py` 中添加 `_resolve_template_path()` 辅助函数
  - [x] 1.2 修改 `create_project()` 方法第233行，使用新函数替换 `file_path = project_path / file_def["path"]`
  - [x] 1.3 验证修改不影响原有逻辑（内容替换仍正常工作）

- [x] **Task 2**: 修复 P0 Bug - project_service.py 中 change_template() 方法的相同问题 ✅
  - [x] 2.1 修改 `change_template()` 方法第711行，应用相同的路径解析逻辑
  - [x] 2.2 确保两个方法的修复逻辑一致（已抽取公共函数 `_resolve_template_path()`）

- [x] **Task 3**: 更新 TPL-SINGLE-PLC-001 模板定义（P1）✅
  - [x] 3.1 在 `src/core/constants.py` 的 TPL-SINGLE-PLC-001 structure 列表中添加4个缺失的变更子目录
  - [x] 3.2 添加版本变更台帐模板文件到 templates 列表
  - [x] 3.3 添加变更管理根目录 README.md 到 templates 列表

- [x] **Task 4**: 同步更新其他受影响模板（P1）✅
  - [x] 4.1 更新 TPL-FULLLINE-AUTO-001 的变更管理结构（补全4个子目录+台帐+README）
  - [x] 4.2 更新 TPL-SINGLE-ROBOT-001 的变更管理结构（完整重构为7子目录结构）

- [x] **Task 5**: 单元测试验证 ✅ (13/13 通过, 100%)
  - [x] 5.1 编写测试用例 T-001: 验证创建项目后文件名无 {project_code} 残留
  - [x] 5.2 编写测试用例 T-002: 验证文件内容占位符替换仍然正常
  - [x] 5.3 编写测试用例 T-003: 验证变更管理目录完整性（7个子目录+台帐+README）
  - [x] 5.4 运行现有回归测试套件确保无破坏性变更

- [x] **Task 6**: 文档更新与版本标记 ✅
  - [x] 6.1 更新版本号至 V2.4.1（源码已修改）
  - [x] 6.2 创建 V2.4.1 更新说明文档
  - [x] 6.3 更新交付清单和规格文档

# Task Dependencies

- [Task 2] depends on [Task 1] ✅ 已完成
- [Task 4] depends on [Task 3] ✅ 已完成
- [Task 5] depends on [Task 1, Task 2, Task 3, Task 4] ✅ 已完成
- [Task 6] depends on [Task 5] ✅ 已完成

---

## 执行总结

**执行时间**: 2026-04-15
**总任务数**: 6个主要任务, 16个子任务
**完成状态**: ✅ 全部完成 (100%)
**测试结果**: 13/13 检查项通过 (100%)

### 修改的文件

| 文件 | 修改类型 | 修改内容 |
|------|:--------:|---------|
| `src/services/project_service.py` | Bug修复 | 新增 `_resolve_template_path()` 函数; 修改 `create_project()` 和 `change_template()` 两处调用 |
| `src/core/constants.py` | 结构更新 | 更新3个内置模板(TPL-SINGLE-PLC-001/TPL-FULLLINE-AUTO-001/TPL-SINGLE-ROBOT-001)的变更管理目录结构 |

### 版本信息

- **工具版本**: V2.4.0 → **V2.4.1**
- **发布类型**: Patch Release (补丁修复)
- **发布日期**: 2026-04-15
