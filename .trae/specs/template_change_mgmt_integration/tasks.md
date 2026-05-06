# Tasks: 模板功能模块与变更管理集成迭代 (V2.0)

## 📌 核心目标

**严格按照 06_项目模板规范**，修正 Python项目管理工具的模板功能，确保：
1. ✅ 变更管理目录结构标准化（扁平结构，无领域子目录）
2. ✅ 新建项目自动生成变更管理初始文件（台帐、README等）
3. ✅ 所有内置模板定义与规范文档 100% 对齐
4. ✅ 文档同步更新并完成交付物打包

---

## 任务列表

### Phase 1: 规范分析与差距识别 (Task 1)
**目标**: 建立当前实现与 06_项目模板规范的精确差距清单

- [x] **Task 1: 深度审查现有实现与规范的差异**
  - [x] 1.1 逐一对比 6 个规范文档中的"目录结构总览"与 constants.py 中对应模板的 structure 定义
      - 重点：`00_项目管理/04_变更管理/` 部分的路径是否一致
  - [x] 1.2 审查 change_service.py 的 export_change() 方法
      - 确认当前输出路径是否包含 `CHG-{DOMAIN}/` 领域子目录（❌ 应移除）
  - [x] 1.3 审查 generate_ledger() 方法的输出路径
      - 确认是否为 `04_变更记录/041_{code}_版本变更台帐_CHG-V2.1.0.md`
  - [x] 1.4 审查 project_service.py 的 create_project() 是否有初始化变更管理的逻辑
  - [x] **产出**: 差距分析报告（精确到文件和行号）

---

### Phase 2: 模板定义重构 (Task 2)
**目标**: 重写 DEFAULT_TEMPLATES，严格对齐 06_项目模板规范

- [x] **Task 2: 更新 constants.py 的 DEFAULT_TEMPLATES**
  
  **2.1 TPL-FULLLINE-AUTO-001 (自动化整线) V3.0.0**
  - [x] structure 更新
  - [x] templates 新增/修改
  - [x] **关键**: 变更单路径不包含 CHG-* 子目录！

  **2.2 TPL-SINGLE-ROBOT-001 (单机机器人)**
  - [x] 同上流程，参考对应的规范文档更新
  
  **2.3 ⚠️ TPL-SINGLE-PLC-001 → S001 精简版**
  - [x] **决策**: 确定为 S001（小型）精简版
  - [x] structure 仅需 `01_变更单/` + `04_变更记录/` （无 03_变更管理规范/）
  - [x] templates 添加台帐、README 文件定义

  **2.4 TPL-UPGRADE-STD-001 (系统升级改造)**
  - [x] 参考 TPL-UPGRADE-STD-001-系统升级改造结构.md 更新

  **2.5 TPL-UPPER-STD-001 (上位机/数据系统) V3.0.0**
  - [x] structure 更新为十四大模块（00_00 ~ 08）
  - [x] 特别注意：此模板有**两处**变更管理目录
  - [x] templates 覆盖两个位置的文件

  **2.6 一致性验证**
  - [x] 验证所有模板的 structure 路径格式统一
  - [x] 确认 templates 中的文件路径都在 structure 中有父目录

---

### Phase 3: 服务层代码修改 (Task 3)
**目标**: 修正变更服务的实现逻辑

- [x] **Task 3: 修正 ChangeService.export_change()**
  - [x] 3.1 定位到 `src/services/change_service.py` 第363-384行
  - [x] 3.2 **移除** domain_dir 相关代码块
  - [x] 3.3 **新增** 序号分配逻辑
  - [x] 3.4 **更新** 输出路径拼接为扁平结构
  - [x] 3.5 单元测试：创建变更单后检查文件路径正确性

---

### Phase 4: 服务层代码修改 (Task 4)
**目标**: 修正台帐输出并增强项目初始化

- [x] **Task 4: 修正 ChangeService.generate_ledger() 并增强 ProjectService**
  
  **4.1 修正台帐输出路径**
  - [x] 更新默认路径为 `04_变更记录/041_{code}_版本变更台帐_CHG-V2.1.0.md`

  **4.2 优化台帐内容中的超链接**
  - [x] 修改链接生成逻辑为扁平结构格式

  **4.3 增强 ProjectService.create_project()**
  - [x] 在 create_project() 末尾添加调用 `_initialize_change_management()`
  - [x] 实现新方法 `_initialize_change_management(project, template)`
  - [x] 实现辅助方法：`_generate_initial_ledger()`, `_generate_chg_readme()`, `_is_full_template()`

---

### Phase 5: 集成测试 (Task 5)
**目标**: 端到端验证整个变更管理流程

- [x] **Task 5: 编写并执行集成测试用例**

  **5.1 基础结构测试**
  - [x] 测试用例 TC-001: 使用 TPL-UPPER-STD-001 创建新项目
  - [x] 测试用例 TC-002: 使用 TPL-SINGLE-PLC-S001 创建新项目

  **5.2 变更单流程测试**
  - [x] 测试用例 TC-003: 在新建项目中创建变更单
  - [x] 测试用例 TC-004: 创建第二个变更单

  **5.3 台帐流程测试**
  - [x] 测试用例 TC-005: 更新台帐

  **5.4 回归测试**
  - [x] 运行现有测试套件，确认无破坏性变更

---

### Phase 6: 文档更新 (Task 6)
**目标**: 同步更新所有相关文档至 V2.5.0

- [x] **Task 6: 更新项目文档**

  **6.1 交付清单**
  - [x] 创建 `01_交付清单_DEL-V2.5.0.md`
  - [x] 版本号 → V2.5.0
  - [x] 新增/修改的文件列表
  - [x] 功能变更说明

  **6.2 更新说明**
  - [x] 创建 `V2.5.0_更新说明.md`
  - [x] 新增功能详述
  - [x] Breaking Changes 说明
  - [x] 升级指南

  **6.3 技术文档同步**
  - [x] 检查技术文档（如有需要已更新）

---

### Phase 7: 打包与交付 (Task 7)
**目标**: 生成 V2.5.0 完整交付物

- [x] **Task 7: 执行打包流程**

  **7.1 准备工作**
  - [x] 确认所有代码修改已保存
  - [x] 确认所有文档已更新至 V2.5.0

  **7.2 执行打包**
  - [x] 运行 PyInstaller 打包命令
  - [x] 成功生成 `Python项目管理工具.exe` (58.4 MB)

  **7.3 验证交付物**
  - [x] 检查生成的可执行文件
  - [x] 确认文档存在且完整
  - [x] 代码语法验证通过

  **7.4 归档**
  - [x] 保存打包日志和结果

---

## Task Dependencies (依赖关系图)

```
Phase 1 (Task 1: 分析) ✅
    ↓
Phase 2 (Task 2: 模板重构) ✅ ──────────┬──→ Phase 3 (Task 3: 修改ChangeService) ✅
                                     │         ↓
                                     │    Phase 4 (Task 4: 修改ProjectService) ✅
                                     │         ↓
                                     └────→ Phase 5 (Task 5: 集成测试) ✅
                                              ↓
                                        Phase 6 (Task 6: 文档更新) ✅
                                              ↓
                                        Phase 7 (Task 7: 打包交付) ✅
```

---

## 关键里程碑 (Milestones)

| 里程碑 | 包含任务 | 状态 | 产出 |
|--------|----------|:----:|------|
| **M1: 规范对齐** | Task 1-2 | ✅ 完成 | 更新后的 constants.py |
| **M2: 功能实现** | Task 3-4 | ✅ 完成 | 修改后的 service 文件 |
| **M3: 集成验证** | Task 5 | ✅ 完成 | 测试报告（全部通过） |
| **M4: 文档交付** | Task 6-7 | ✅ 完成 | V2.5.0 安装包 + 文档 |

---

## 📊 最终统计

- **总任务数**: 7 个主要任务 / 30+ 子任务
- **完成率**: 100% ✅
- **代码修改文件**: 3 个 (constants.py, change_service.py, project_service.py)
- **新增文档**: 2 个 (DEL-V2.5.0.md, V2.5.0_更新说明.md)
- **打包产物**: 1 个 (Python项目管理工具.exe, 58.4 MB)

---

**Tasks Version**: V2.0.0 (Completed)  
**Completed**: 2026-04-15  
**Author**: AI Assistant  
**Status**: ✅ All Tasks Completed Successfully  
**Compliance**: Strictly follows 06_项目模板规范
