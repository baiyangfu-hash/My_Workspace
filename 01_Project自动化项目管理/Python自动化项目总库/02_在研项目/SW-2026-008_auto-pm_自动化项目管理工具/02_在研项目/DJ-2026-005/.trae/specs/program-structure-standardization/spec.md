# DJ-2026-005 项目程序结构规范化修订 Spec

## Why
DJ-2026-005 边框缓存机项目存在以下关键问题：
1. **LSP插件识别异常**: FB_1003_PickPlace 的4个TIME类型输出变量(`q_e放料完成保持_Elapsed`等)被LSP报告为"Unknown pin"，但实际在VAR_OUTPUT中明确定义
2. **接口匹配历史遗留**: 虽然V2.0.0版本修复了146处接口不匹配，但LSP仍显示部分引脚不可用，说明存在索引或定义不一致问题
3. **项目结构复杂度风险**: 相比参考项目DJ-2026-000（1个FB），本项目包含6个功能块，接口总数超过400个，维护难度高
4. **需要建立标准化基准**: 以正常运行的DJ-2026-000为参照，建立可验证的程序结构和质量标准

## What Changes
- [ ] 全面审计DJ-2026-005所有6个功能块的VAR_INPUT/VAR_OUTPUT定义完整性
- [ ] 对比OB1.scl中每个功能块调用与实际FB定义的100%匹配度
- [ ] 验证GlobalVars.db数据结构与所有FB接口的完整映射关系
- [ ] 诊断并解决LSP索引/缓存导致的"Unknown pin"问题
- [ ] 建立基于DJ-2026-000参考项目的标准化检查清单
- [ ] **BREAKING**: 可能需要调整FB_1003_PickPlace的输出接口设计以兼容LSP限制

## Impact
- Affected specs: 所有现有specs（st-program-refactor, variable-unify-fix, timer-standardization等）
- Affected code:
  - `02_PLC程序/通用ST程序及变量表/OB1/OB1.scl` - 主程序组织块
  - `02_PLC程序/通用ST程序及变量表/DB1/GlobalVars.db` - 全局变量数据块
  - `02_PLC程序/通用ST程序及变量表/pickplace/FB_1003_PickPlace_BufferFraming.scl` - 取放料机构功能块（重点）
  - `02_PLC程序/通用ST程序及变量表/conveyor/FB_1001_Conveyor4Layer_BufferFraming.scl` - 四层输送机容器块
  - `02_PLC程序/通用ST程序及变量表/conveyor/FB_1002_SingleLayerConveyor_BufferFraming.scl` - 单层输送机功能块
  - `02_PLC程序/通用ST程序及变量表/feeder/FB_1004_GlueMachineFeeder_BufferFraming.scl` - 打胶机送料机构功能块
  - `02_PLC程序/通用ST程序及变量表/external/FB_ExternalDeviceInteraction.scl` - 外部设备交互功能块
  - `02_PLC程序/通用ST程序及变量表/common/FB_2001_CommonAlarm_AllStation.scl` - 公共报警管理功能块

## ADDED Requirements

### Requirement: 功能块接口完整性验证
系统 SHALL 提供自动化机制验证每个功能块的接口定义符合以下规则：
1. 每个FB必须有完整的FUNCTION_BLOCK声明
2. VAR_INPUT、VAR_OUTPUT、VAR三个区域必须正确闭合（END_VAR）
3. 变量命名遵循801_PLC规范：i_xxx(输入)、o_xxx(输出)、q_xxx(调试输出)、s_xxx(内部)
4. 数据类型必须明确指定（BOOL/INT/REAL/TIME/ARRAY等）
5. 注释必须包含中文说明和用途描述

#### Scenario: FB_1003_PickPlace接口验证
- **WHEN** 审计工具扫描FB_1003_PickPlace_BufferFraming.scl文件
- **THEN** 应检测到：
  - ✅ FUNCTION_BLOCK声明在第57行
  - ✅ VAR_INPUT包含58个输入变量（8系统控制+14手动操作+6工艺参数+26传感器+4上游）
  - ✅ VAR_OUTPUT包含30个输出变量（13执行器+3伺服+1下游+7状态+1报警+4定时器调试）
  - ✅ VAR包含内部状态变量和定时器实例
  - ✅ 第250节的4个TIME类型输出变量标记为[OUTPUT]

#### Scenario: LSP兼容性验证
- **WHEN** LSP插件解析FB_1003_PickPlace的调用时
- **THEN** 不应产生"Unknown pin"错误：
  - `q_e放料完成保持_Elapsed : TIME`
  - `q_e动作_Elapsed : TIME`
  - `q_e产品检测稳定_Elapsed : TIME`
  - `q_e初始化_Elapsed : TIME`

### Requirement: OB1调用一致性保证
OB1.scl SHALL 满足以下要求：
1. 只包含功能块实例化（VAR段）和调用（BEGIN段），不包含业务逻辑
2. 每个FB调用的输入参数数量必须等于该FB的VAR_INPUT变量数
3. 每个FB调用的输出参数数量必须等于该FB的VAR_OUTPUT变量数
4. 所有参数通过GlobalVars.db进行映射，不直接使用物理地址
5. 调用顺序按工艺流程排列（外部设备→输送机→取放料→送料→报警）

#### Scenario: FB_ExternalDeviceInteraction调用验证
- **WHEN** OB1第84行调用fbExternalDevice(
- **THEN** 必须包含：
  - 27个输入参数（:=赋值）匹配VAR_INPUT定义
  - 20个输出参数（=>赋值）匹配VAR_OUTPUT定义
  - 无多余或缺失的引脚

#### Scenario: 全局数据流完整性
- **WHEN** 追踪从FB输入到输出的完整数据链路
- **THEN** 应验证：
  - 上游FB的输出 → GlobalVars中间变量 → 下游FB的输入
  - 例如：Conveyor.o_b放料完成 → GlobalVars.stPickPlace.i_b输送机_Lx_放料完成 → PickPlace输入

### Requirement: GlobalVars.db结构标准化
全局变量数据块 SHALL 采用以下结构模式：
```pascal
DATA_BLOCK GlobalVars
VAR
    stGlobal   : STRUCT ... END_STRUCT;  // 全局控制信号（来自FB_2001输出）
    stExternal : STRUCT ... END_STRUCT;  // 外部设备交互信号
    stConveyor : STRUCT ... END_STRUCT;  // 四层输送机信号
    stPickPlace: STRUCT ... END_STRUCT;  // 取放料机构信号
    stFeeder   : STRUCT ... END_STRUCT;  // 打胶机送料机构信号
END_VAR
END_DATA_BLOCK
```

每个STRUCT内部必须按照以下顺序组织：
1. i_xxx 输入变量（对应FB的VAR_INPUT）
2. o_xxx 输出变量（对应FB的VAR_OUTPUT）
3. q_xxx 调试输出变量（可选，对应FB的调试输出）

#### Scenario: 类型匹配验证
- **WHEN** 对比GlobalVars.stPickPlace.q_e放料完成保持_Elapsed的类型
- **THEN** 必须是TIME类型，且与FB_1003_PickPlace的VAR_OUTPUT定义一致

## MODIFIED Requirements

### Requirement: LSP诊断零错误目标
修改原有"语法检查通过"要求为零容忍标准：

**原要求**: LSP诊断无ERROR级别错误
**新要求**:
1. LSP诊断必须0个ERROR和0个WARNING
2. 所有"Unknown pin"错误必须在编译前解决
3. 类型不匹配（如将TIME赋值给INT）必须消除
4. 未使用的变量应有明确注释说明预留用途

#### Scenario: IDE实时诊断验证
- **WHEN** 开发者在VSCode中打开OB1.scl文件
- **THEN** 编辑器底部的问题面板应显示：
  - ✅ Errors: 0
  - ✅ Warnings: 0
  - ✅ 无红色波浪线或黄色提示

### Requirement: 版本一致性管理
修改版本号管理策略：

**原策略**: 各文件独立版本号
**新策略**: 采用联动版本号机制：
- OB1 V2.0.0 ↔ GlobalVars V2.0.0 ↔ 所有FB V4.2.0（基线版本）
- 当任一FB接口变更时，OB1和GlobalVars必须同步升级版本号
- 变更记录必须引用关联文件的版本号

#### Scenario: FB_1003接口变更影响分析
- **WHEN** FB_1003_PickPlace从V4.1.0升级到V4.2.0（新增4个TIME输出）
- **THEN** 必须同步更新：
  - OB1.scl升级到V2.0.0（添加4个新的输出参数映射）
  - GlobalVars.db升级到V2.0.0（stPickPlace结构体添加4个TIME字段）
  - 接口文档_IFC-FB1003-PickPlace.md更新输出列表
  - 变更记录_CHG-FB1003-PickPlace.md记录V4.2.0变更内容

## REMOVED Requirements

### Requirement: 定时器调试输出（临时移除）
**原因**: LSP插件当前版本可能不完全支持TIME类型作为输出引脚的自动补全和验证
**迁移方案**:
1. 将4个TIME输出变量从VAR_OUTPUT暂时移至VAR内部变量
2. 在OB1中注释掉对应的4行输出参数映射
3. 添加TODO注释标注恢复条件："等待LSP支持TIME输出或升级插件版本"
4. 保留FB内部的ET=>q_e_xxx_Elapsed赋值逻辑不变（仅改变变量作用域）

**恢复计划**:
- 条件1: Siemens LSP插件更新后支持TIME输出
- 条件2: 验证生产环境PLC编译器支持该特性
- 条件3: HMI团队确认需要这些调试数据

#### scenario: 降级兼容性处理
- **WHEN** LSP持续报告q_e放料完成保持_Elapsed为Unknown pin
- **THEN** 执行以下步骤：
  1. 在FB_1003的VAR段新增：`s_e放料完成保持_Elapsed_Internal : TIME;`
  2. 将VAR_OUTPUT中的`q_e放料完成保持_Elapsed : TIME;`注释掉
  3. 修改所有`ET => q_e放料完成保持_Elapsed`为`ET => s_e放料完成保持_Elapsed_Internal`
  4. 在OB1中注释掉4行输出映射，添加`// TODO: [V4.2.1] 恢复TIME输出待LSP支持`
  5. 更新版本号为V4.2.1（临时兼容版本）

## 技术约束与假设

### 约束条件
1. **LSP插件版本**: 假设使用Siemens Language Support Package最新版，但可能存在未知bug
2. **编译器兼容性**: 目标硬件为三菱FX系列或西门子S7-1200（需确认）
3. **SysLib库依赖**: 项目依赖../01_SharedLibraries/SysLib库的FB_TON定时器实现
4. **IDE环境**: VSCode + Siemens LSP插件 + Trae IDE扩展

### 关键假设
1. DJ-2026-000项目的程序结构是**正确的参考基准**
2. FB_1003_PickPlace的V4.2.0版本新增TIME输出是**合理需求**（HMI调试用途）
3. LSP的"Unknown pin"错误是**索引/缓存问题**而非代码逻辑错误
4. 可以通过调整代码结构或等待插件更新来解决兼容性问题

## 成功标准

### 定量指标
- [ ] LSP诊断错误数: **0** (当前: 1个Unknown pin)
- [ ] 功能块接口匹配率: **100%** (输入/输出参数数量完全一致)
- [ ] GlobalVars覆盖率: **100%** (所有FB接口都有对应的全局变量)
- [ ] 代码注释覆盖率: **>90%** (每个变量都有中文注释)

### 定性指标
- [ ] 程序结构清晰度: 达到DJ-2026-000的简洁水平（单一职责原则）
- [ ] 可维护性: 新开发者可在30分钟内理解整体架构
- [ ] 可测试性: 每个FB都可独立进行单元测试（已有.scltest文件支持）
- [ ] 文档同步性: 代码变更24小时内更新相关文档

## 风险评估

### 高风险项
1. **TIME输出兼容性** (影响范围: 中)
   - 风险: 如果LSP确实不支持TIME输出，需牺牲调试功能
   - 缓解: 准备降级方案（移至内部变量）

2. **大规模重构引入回归** (影响范围: 高)
   - 风险: 修改6个FB可能破坏现有业务逻辑
   - 缓解: 逐个FB验证，保留备份，充分测试

### 中风险项
1. **GlobalVars结构变动** (影响范围: 中)
   - 风险: 修改数据块结构可能导致地址偏移
   - 缓解: 仅追加字段，不删除或重排现有字段

2. **版本管理混乱** (影响范围: 低)
   - 风险: 多文件版本不同步导致追踪困难
   - 缓解: 建立版本联动机制和自动化检查脚本

## 后续行动建议

### Phase 1: 诊断与验证（本次任务）
1. 全面审计所有FB接口定义
2. 对比OB1调用与FB定义的差异清单
3. 验证GlobalVars完整性
4. 确定LSP问题的根因（缓存vs兼容性）

### Phase 2: 修复与优化（后续迭代）
1. 根据Phase 1结果选择修复方案（A/B/C）
2. 执行接口修正和结构调整
3. 更新所有相关文档
4. 回归测试确保功能不变

### Phase 3: 标准化建设（长期目标）
1. 建立自动化接口验证脚本
2. 制定FB开发模板和checklist
3. 建立CI/CD流程（LSP检查+编译验证）
4. 编写《DJ-2026-005程序维护手册》
