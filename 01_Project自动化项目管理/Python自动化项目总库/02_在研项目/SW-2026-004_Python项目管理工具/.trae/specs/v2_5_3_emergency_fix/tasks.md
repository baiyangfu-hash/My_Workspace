# V2.5.3 紧急修复 - 实现计划

## [x] Task 1: 修复版本号配置问题（P0）
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 修改 `src/core/config.py`，移除硬编码的 version 值
  - 添加动态读取 version.py 的逻辑
  - 确保所有使用版本号的地方都从统一来源获取
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: Config.get('version') 返回 "2.5.3"
  - `human-judgment` TR-1.2: 程序标题栏显示 "V2.5.3"
- **Notes**: 这是用户最直观看到的问题，必须首先修复

## [x] Task 2: 修复模板管理 UI 渲染问题（P0）
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 调试 `_display_templates()` 方法为何不渲染表格内容
  - 检查 QTableWidgetItem 创建和设置是否正确
  - 验证 QTableWidget 的配置（列数、行高、可见性等）
  - 可能需要重写或重构显示逻辑
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: _display_templates 方法执行后 table.rowCount() > 0
  - `human-judgment` TR-2.2: 表格可见且包含 5 行数据
  - `human-judgment` TR-2.3: 点击刷新后表格仍正常显示
- **Notes**: 已添加日志，需要实际运行查看日志输出

## [x] Task 3: 修复 GUI 项目创建逻辑（P0）
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 找到 GUI 创建项目的入口（可能是 create_project_dialog.py 或 main_window.py）
  - 追踪调用链：GUI → Service → DAO → 文件系统操作
  - 对比脚本创建项目（正常）和 GUI 创建项目（缺失变更管理）的差异
  - 确保模板的 structure 和 templates 字段被正确传递和应用
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: GUI 创建的项目包含 04_变更管理 目录
  - `programmatic` TR-3.2: 变更管理目录下有正确的子目录和文件
  - `human-judgment` TR-3.3: 用户可通过变更管理模块操作新创建的项目
- **Notes**: 这是最关键的功能性问题

## [x] Task 4: 清理测试数据（P1）
- **Priority**: P1
- **Depends On**: Task 3
- **Description**: 
  - 编写安全的数据清理脚本
  - 删除所有 TEST_ 前缀的项目（SW-2026-002~006, DJ-2026-001~004 等）
  - 删除对应的物理目录（D:\temp_test_projects 及其他测试目录）
  - 验证数据库干净无残留
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 数据库中不存在 TEST_ 前缀项目
  - `programmatic` TR-4.2: 物理磁盘上不存在测试项目目录
  - `programmatic` TR-4.3: 总库管理界面只显示正常项目
- **Notes**: 必须先备份再清理，防止误删

## [x] Task 5: 全面 GUI 测试验证（P0）
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3, Task 4
- **Description**: 
  - 启动程序进行真实 GUI 测试（非脚本模拟）
  - 逐一验证每个修复点：
    1. 版本号显示
    2. 模板管理界面初始加载 + 刷新
    3. 使用每种模板通过 GUI 创建项目
    4. 验证每个新建项目的目录结构
    5. 验证变更管理功能可用性
  - 截图记录每个步骤的结果
  - 输出真实的测试报告（非虚假报告）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `human-judgment` TR-5.1: 所有 GUI 操作符合预期
  - `programmatic` TR-5.2: 文件系统检查确认目录结构正确
  - `human-judgment` TR-5.3: 测试报告真实反映测试结果
- **Notes**: **这是验收的关键环节，必须诚实记录所有问题**

# Task Dependencies
- [Task 2] 无依赖（可与 Task 1 并行）
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
- [Task 5] depends on [Task 1, Task 2, Task 3, Task 4]

## 执行顺序建议
```
Phase 1 (并行): Task 1 (版本号) + Task 2 (UI渲染)
Phase 2 (串行): Task 3 (项目创建) → Task 4 (数据清理)
Phase 3 (最终): Task 5 (全面测试)
```