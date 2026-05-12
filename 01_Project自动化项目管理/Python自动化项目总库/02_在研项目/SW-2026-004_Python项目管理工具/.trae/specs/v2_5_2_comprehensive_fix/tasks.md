# V2.5.2 模板管理与总库管理全面修复 - 实现计划

## [x] Task 1: 全面诊断模板管理模块
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 检查 `constants.py` 中所有模板定义的语法和逻辑正确性
  - 验证每个模板的 structure 字段是否包含变更管理目录
  - 验证每个模板的 templates 字段是否包含变更管理相关文件
  - 检查是否有语法错误（括号不匹配、引号错误等）
  - 对比参考规范 `06_项目模板规范`，找出差异
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: constants.py 无语法错误
  - `programmatic` TR-1.2: 所有模板都包含变更管理目录结构
  - `programmatic` TR-1.3: 模板定义与参考规范一致
- **Notes**: 重点检查 TPL-SINGLE-PLC-S001、TPL-SINGLE-PLC-M001 等常用模板

## [x] Task 2: 全面诊断总库管理模块
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 检查 `project_dao.py` 的 count_by_status 方法实现
  - 检查 `library_manager.py` UI 组件的数据加载逻辑
  - 验证数据库连接和查询语句的正确性
  - 检查缓存机制是否影响统计结果
  - 测试项目数统计功能
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: count_by_status 方法返回正确的数值
  - `programmatic` TR-2.2: 总库管理 UI 正确显示项目数
  - `programmatic` TR-2.3: 缓存机制不影响统计准确性
- **Notes**: 需要实际运行测试脚本验证

## [x] Task 3: 修复模板定义问题
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 根据 Task 1 的诊断结果修复所有发现的问题
  - 更新缺失或不正确的模板定义
  - 确保所有模板都包含完整的变更管理目录结构：
    ```
    00_项目管理/04_变更管理/
    ├── 01_变更单/
    ├── 03_变更管理规范/ (可选)
    └── 04_变更记录/
    ```
  - 确保所有模板都包含必要的变更管理文件模板
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-3.1: 修复后 constants.py 无语法错误
  - `programmatic` TR-3.2: 所有模板的变更管理目录结构完整
  - `programmatic` TR-3.3: 变更管理文件模板内容正确
- **Notes**: 必须严格遵循参考规范的目录结构和文件命名规则

## [x] Task 4: 修复总库管理模块问题
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 根据 Task 2 的诊断结果修复所有发现的问题
  - 修复 count_by_status 方法的逻辑错误（如有）
  - 修复 library_manager.py UI 的数据显示问题
  - 优化缓存策略，确保统计数据准确
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: 项目数统计功能正常
  - `programmatic` TR-4.2: 总库管理模块能正确加载和显示数据
  - `programmatic` TR-4.3: 刷新操作能更新统计数据
- **Notes**: 确保在多种场景下都能正确统计（有/无项目、不同状态等）

## [x] Task 5: 使用每种模板创建测试项目
- **Priority**: P0
- **Depends On**: Task 3, Task 4
- **Description**: 
  - 使用以下每种模板创建测试项目：
    1. TPL-FULLLINE-AUTO-001 (自动化整线)
    2. TPL-SINGLE-PLC-S001 (小型单机设备)
    3. TPL-SINGLE-PLC-M001 (中大型单机设备) - 如存在
    4. TPL-SINGLE-ROBOT-001 (单机机器人)
    5. TPL-UPGRADE-STD-001 (系统升级改造)
    6. TPL-UPPER-STD-001 (上位机/数据系统)
  - 验证每个项目的目录结构是否符合对应模板规范
  - 特别验证变更管理目录和文件是否正确生成
- **Acceptance Criteria Addressed**: AC-2, AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有模板都能成功创建项目
  - `human-judgment` TR-5.2: 生成的目录结构与模板定义一致
  - `programmatic` TR-5.3: 变更管理目录和文件完整且内容正确
- **Notes**: 创建的测试项目应在验证后清理

## [x] Task 6: 全面功能测试与打包
- **Priority**: P0
- **Depends On**: Task 5
- **Description**: 
  - 运行应用程序进行全面功能测试
  - 测试模板管理模块的所有功能（浏览、选择、创建）
  - 测试总库管理模块的所有功能（统计、筛选、刷新）
  - 测试变更管理模块是否能正确识别和使用生成的目录结构
  - 使用标准打包脚本重新打包交付物
  - 验证打包后的交付物包含所有修复
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-6.1: 应用程序无崩溃或严重错误
  - `programmatic` TR-6.2: 打包过程成功完成
  - `programmatic` TR-6.3: 交付物大小合理且包含必要文件
  - `human-judgment` TR-6.4: 所有核心功能正常工作
- **Notes**: 记录测试过程中的所有问题和解决方案

# Task Dependencies
- [Task 3] depends on [Task 1]
- [Task 4] depends on [Task 2]
- [Task 5] depends on [Task 3, Task 4]
- [Task 6] depends on [Task 5]