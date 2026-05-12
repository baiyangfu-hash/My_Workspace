# V2.5.1 交付物问题修复与功能增强 - 实现计划

## [ ] Task 1: 诊断并修复总库管理模块项目数显示问题
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 检查 `project_service.py` 中的项目计数逻辑
  - 检查数据库查询语句是否正确
  - 验证数据库连接是否正常
  - 修复可能的空值处理或计数逻辑问题
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 项目数显示大于0（当有项目存在时）
  - `programmatic` TR-1.2: 项目列表正确加载
- **Notes**: 重点检查数据库查询返回值的处理

## [ ] Task 2: 验证并确保模板定义正确更新
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 检查 `constants.py` 中的模板定义是否正确
  - 验证打包流程是否正确包含模板文件
  - 测试在其他电脑上运行时模板是否可用
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 模板定义包含最新的变更管理目录结构
  - `programmatic` TR-2.2: 打包后的 exe 包含模板文件
- **Notes**: 检查 PyInstaller 打包配置是否包含模板文件

## [ ] Task 3: 修复版本显示异常问题
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 检查版本显示逻辑
  - 验证版本配置文件
  - 确保版本号正确显示为 "V2.5.1"
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 版本号显示为 "V2.5.1"
  - `programmatic` TR-3.2: 版本信息显示完整
- **Notes**: 检查版本配置文件和显示组件

## [ ] Task 4: 实现版本记录功能
- **Priority**: P1
- **Depends On**: None
- **Description**: 
  - 添加版本记录查看功能
  - 读取并显示更新说明文件
  - 确保界面简洁明了
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgment` TR-4.1: 版本记录显示完整
  - `human-judgment` TR-4.2: 界面用户友好
- **Notes**: 可以读取 `02_发布说明` 目录下的更新说明文件

## [ ] Task 5: 重新打包 V2.5.1 交付物
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3, Task 4
- **Description**: 
  - 使用标准打包脚本 `build_delivery.py`
  - 确保所有修复都包含在新的交付物中
  - 验证打包结果
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: 打包过程无错误
  - `programmatic` TR-5.2: 交付物大小合理
  - `programmatic` TR-5.3: 交付物包含所有必要文件
- **Notes**: 严格按照打包规范执行

## [ ] Task 6: 测试验证
- **Priority**: P0
- **Depends On**: Task 5
- **Description**: 
  - 在不同电脑上测试 V2.5.1 交付物
  - 验证所有问题是否修复
  - 确保新功能正常工作
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-6.1: 项目数显示正确
  - `programmatic` TR-6.2: 模板更新到位
  - `programmatic` TR-6.3: 版本显示正确
  - `human-judgment` TR-6.4: 版本记录功能正常
- **Notes**: 重点测试在其他电脑上的运行情况