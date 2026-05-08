# Tasks: 修正DJ-2026-014变更管理目录结构与缺失变更单 (v2精简版)

## 任务列表

- [x] **Task 1: 创建精简版变更管理目录结构**
  - [x] 1.1 创建 `00_项目管理/04_变更管理/01_变更单/` 根目录
  - [x] 1.2 创建7个领域子目录: CHG-ELEC/, CHG-MECH/, CHG-PLC/, CHG-HMI/, CHG-SCPT/, CHG-DOCU/, CHG-SAFE/
  - [x] 1.3 **不创建** `02_变更报告/` 目录 (功能已合并到变更单+台帐, 见spec §Why)
  - [x] 1.4 验证最终目录结构符合精简原则 (PLC=13, DOCU=3, 其他5个=空预留)

- [x] **Task 2: 创建PLC领域变更单 (13份)**
  - [x] 2.1 创建 `CHG-PLC-2026-001.md` ← FB-V2-001 新增状态字输出q_StatusWord (PLC×REQ×MOD)
  - [x] 2.2 创建 `CHG-PLC-2026-002.md` ← FB-V2-003 方向验证逻辑修正 (PLC×DEF×LOC) **P0-Bug**
  - [x] 2.3 创建 `CHG-PLC-2026-003.md` ← FB-V2-004 新增复位按钮i_Reset (PLC×REQ×MOD)
  - [x] 2.4 创建 `CHG-PLC-2026-004.md` ← FB-V2-005 接口重构:启停4→2 ⚠️ **SYSTEM级** (PLC×OPT×SYS) **P0**
  - [x] 2.5 创建 `CHG-PLC-2026-005.md` ← FB-V2-006 补全中间变量 (PLC×DEF×MOD) 关联→004
  - [x] 2.6 创建 `CHG-PLC-2026-006.md` ← FB-V2-008 速度范式改Hz ⚠️ **SYSTEM级** (PLC×OPT×SYS) **P0**
  - [x] 2.7 创建 `CHG-PLC-2026-007.md` ← FB-V2-009 报警清除增强 (PLC+SAFE×OPT×MOD)
  - [x] 2.8 创建 `CHG-PLC-2026-008.md` ← FB-V2-010 修复模式误报警 (PLC×DEF×LOC) **P0-Bug**
  - [x] 2.9 创建 `CHG-PLC-2026-009.md` ← FB-V2-011 【关键Bug】传感器计时器 (PLC×DEF×MOD) **P0**
  - [x] 2.10 创建 `CHG-PLC-2026-010.md` ← FB-V2-012 【关键Bug】初始化复位 (PLC×DEF×MOD) **P0**
  - [x] 2.11 创建 `CHG-PLC-2026-011.md` ← FB-V2-013 速度防呆保护 (PLC×OPT×LOC) 关联→006
  - [x] 2.12 创建 `CHG-PLC-2026-012.md` ← FB-V2-014 报警行为优化 (PLC×OPT×MOD)
  - [x] 2.13 创建 `CHG-PLC-2026-013.md` ← FB-V2-016 状态字位合并 (PLC×OPT×LOC)

- [x] **Task 3: 创建DOCU领域变更单 (3份)**
  - [x] 3.1 创建 `CHG-DOCU-2026-001.md` ← FB-V2-002 状态字注释同步 (DOCU×CFG×LOC) 关联→PLC-001
  - [x] 3.2 创建 `CHG-DOCU-2026-002.md` ← FB-V2-007 时间戳统一 (DOCU×CFG×LOC)
  - [x] 3.3 创建 `CHG-DOCU-2026-003.md` ← FB-V2-015 状态字注释同步(驱动) (DOCU×CFG×LOC) 关联→PLC-006

- [x] **Task 4: 更新版本变更台帐为引用模式**
  - [x] 4.1 将§4.2的FB-V2-001~016内嵌表格替换为引用模式(含超链接到01_变更单/)
  - [x] 4.2 更新§5.1受影响模块表, 增加变更单文件列
  - [x] 4.3 验证所有超链接路径正确

- [x] **Task 5: 更新README.md (精简版)**
  - [x] 5.1 重写为反映精简后的实际目录树(说明为何无02_变更报告/)
  - [x] 5.2 列出7个领域子目录及当前使用情况(有文件/空预留)
  - [x] 5.3 变更单命名规则 + 台帐引用关系说明
  - [x] 5.4 快速开始指南(适合AI自动化工具的最小步骤)

## Task Dependencies

- [Task 1] ✅ 最先完成
- [Task 2] + [Task 3] ✅ 并行执行
- [Task 4] ✅ 在Task 2+3完成后执行
- [Task 5] ✅ 与Task 4并行执行
