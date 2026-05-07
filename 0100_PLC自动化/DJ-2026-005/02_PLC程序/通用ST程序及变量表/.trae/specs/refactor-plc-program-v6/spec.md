# PLC程序全面重构 Spec (V6.0.0)

## Why
当前PLC程序虽然经过V5.0.0的变量名英文化重写，但仍存在以下**严重问题**：

1. **❌ FB_1003_PickPlace 变量名未英文化**（最严重）
   - 接口变量：55个中文变量名（如 `i_b使能`, `s_i步序`）
   - 内部变量：30+个中文变量名
   - 与OB1.scl V5.0.0调用不匹配 → **编译错误 TC001/TC002**

2. **⚠️ FB_1004 内部变量未完全英文化**
   - 接口变量：✅ 已完成（32个英文）
   - 内部变量：❌ 19个中文变量（如 `s_i步序`, `s_bX2轴请求前移`）
   - 代码混用中英文（如 `o_b允许抓料` vs `o_bAllowPickup`）

3. **⚠️ FB_ExternalDeviceInteraction 完全未英文化**
   - 接口变量：27个中文输入 + 20个中文输出 = 47个
   - 内部变量：2个中文
   - 与OB1调用完全不匹配

4. **🔧 架构层面问题**
   - 输出清零逻辑重复（每个FB都有大量重复的归零代码）
   - 状态机缺少统一模板
   - 手动模式控制代码冗余
   - 缺少统一的错误处理机制

## What Changes
- **BREAKING**: 所有剩余**变量名**替换为英文（符合801规范V1.0.5）
- **✅ 保留**: 所有**注释**使用中文（便于国内工程师理解和维护）
- 重构FB_1003接口+内部变量（~85处）
- 重构FB_1004内部变量（~19处）
- 重构FB_ExternalDeviceInteraction接口+内部变量（~49处）
- 提取通用输出清零子程序（可选优化）
- 统一状态机编程模板（文档层面）

### ⚠️ 重要原则：变量名英文化 + 注释中文化

**必须替换的（Variable Names）**:
```scl
// ❌ 错误：变量名使用中文
VAR_INPUT
    i_b使能 : BOOL;           // 编译器无法识别中文标识符
    s_i步序 : INT;
END_VAR

// ✅ 正确：变量名英文 + 注释中文
VAR_INPUT
    i_bEnable : BOOL;          // 总使能信号(主控系统就绪后置位)
    i_bAutoMode : BOOL;        // 自动运行模式选择
    s_iCurrentStep : INT;      // 当前状态机步序(0~10)
END_VAR
```

**必须保留的（Comments）**:
```scl
// ✅ 正确：注释使用中文描述功能和用途
i_bEnable : BOOL;              // 总使能信号(主控系统就绪后置位)
i_bZAxis_JogUp : BOOL;        // 手动-Z轴向上点动

(* ============================================================================
 功能块名称: FB_1003_PickPlace_BufferFraming
 功能描述: 边框缓存机 - 取放料机构纯逻辑功能块
 核心工艺: 一次取两根边框(前后夹紧同时动作), 4层循环取2次
 ============================================================================ *)
```

**命名规范示例**:
| 类别 | 中文（❌禁止） | 英文（✅必须） | 注释（✅保留中文） |
|------|--------------|---------------|------------------|
| 系统控制 | `i_b使能` | `i_bEnable` | `// 总使能信号` |
| 手动操作 | `i_bZ轴点动上` | `i_bLx_ZAxis_JogUp` | `// 手动-Z轴向上点动` |
| 状态输出 | `o_i当前状态` | `o_iCurrentState` | `// 当前状态机步序` |
| 内部变量 | `s_i步序` | `s_iCurrentStep` | `// 当前步序号` |
| 常量 | `STP_空闲` | `STP_Idle` | `// 空闲/待机位置` |

## Impact
- Affected specs: 无（这是首次针对V6.0.0的规格）
- Affected code:
  - [pickplace/FB_1003_PickPlace_BufferFraming.scl](../pickplace/FB_1003_PickPlace_BufferFraming.scl) - **核心修改**
  - [feeder/FB_1004_GlueMachineFeeder_BufferFraming.scl](../feeder/FB_1004_GlueMachineFeeder_BufferFraming.scl) - 内部变量修复
  - [external/FB_ExternalDeviceInteraction.scl](../external/FB_ExternalDeviceInteraction.scl) - 全面重写
  - [OB1/OB1.scl](../OB1/OB1.scl) - 可能需要微调（如果FB接口名变化）
  - [DB1/GlobalVars.db](../DB1/GlobalVars.db) - 可能需要微调

## ADDED Requirements

### Requirement: 变量名100%英文化 + 注释中文化
The system SHALL ensure all **variable names** in FB_1003, FB_1004, and FB_ExternalDeviceInteraction follow the 801 naming convention V1.0.5, while **preserving all Chinese comments** for maintainability.

#### Scenario: FB_1003 complete English renaming
- **WHEN** developer compiles the project after refactoring
- **THEN** zero TC001/TC002 errors occur
- **AND** all interface variables match GlobalVars.db V3.0.0 structure
- **AND** all internal variables use English names with proper prefixes (i_/o_/s_/q_)
- **AND** all comments remain in Chinese (// 单行注释 and (* 多行注释 *))

#### Scenario: FB_1004 internal variables fixed
- **WHEN** reviewer examines FB_1004 source code
- **THEN** all VAR and VAR_OUTPUT variables use English names
- **AND** no Chinese characters remain in variable declarations or usages
- **AND** comments describing functionality are still in Chinese

#### Scenario: FB_ExternalDeviceInteraction fully rewritten
- **WHEN** OB1 calls fbExternalDevice with English variable names
- **THEN** all 27 inputs and 20 outputs match the FB's interface definition
- **AND** internal logic uses only English variable names
- **AND** code comments use Chinese to explain business logic

### Requirement: Maintain Business Logic Integrity
The system SHALL preserve 100% of existing business logic during refactoring.

#### Scenario: State machine logic unchanged
- **WHEN** FB_1003 state machine executes after refactoring
- **THEN** it produces identical output behavior as before
- **AND** all 11 steps maintain same transition conditions
- **AND** alarm codes, timeout values remain unchanged

#### Scenario: Interface compatibility
- **WHEN** OB1 calls any refactored FB
- **THEN** the number and type of I/O parameters remain identical
- **AND** only parameter names change (Chinese → English)

## MODIFIED Requirements

### Requirement: Code Quality Improvement
The system SHALL improve code maintainability through reduced duplication and consistent patterns.

#### Scenario: Output clearing simplification (optional)
- **WHEN** developer needs to add a new output variable
- **THEN** they only need to update ONE location instead of 5+ locations
- **AND** a centralized output reset mechanism exists (METHOD or inline macro)

#### Scenario: Consistent state machine template
- **WHEN** new developer reads any FB source code
- **THEN** they see uniform structure: Enable→Init→FaultDetect→ModeDispatch→StateMachine→StopReset→Output
- **AND** each section uses consistent comment markers (#region format)

## REMOVED Requirements
None (this is an additive refactoring, no feature removal)

---

## Technical Approach

### Phase 1: FB_1003 PickPlace Complete Rewrite (CRITICAL)
**Priority**: P0 - Must fix immediately  
**Effort**: ~3 hours  
**Risk**: High (largest FB, 1472 lines, 85+ variable replacements)

**Variable Mapping Strategy**:
| Category | Example (Chinese) | Target (English) | Count |
|---------|-------------------|------------------|-------|
| System Control | `i_b使能` | `i_bEnable` | 6 |
| Manual Ops | `i_bZ轴点动上` | `i_bLx_ZAxis_JogUp` | 14 |
| Process Params | `i_r取料速度` | `i_rPickupSpeed` | 6 |
| Sensors | `i_b升降_动点` | `i_bLift_WorkPoint` | 26 |
| Upstream | `i_b输送机_L1_放料完成` | `i_bConveyor_L1_FeedComplete` | 4 |
| Actuators | `o_b升降_上升` | `o_bLift_Up` | 13 |
| Status | `o_i当前状态` | `o_iCurrentState` | 7 |
| Internal | `s_i步序` | `s_iCurrentStep` | 30+ |

**Special Considerations**:
- FB_1003 has complex 11-step state machine with deeply nested logic
- Many duplicate output clearing blocks (opportunity for METHOD extraction)
- Timer usage pattern: `fb_t动作定时器(IN:=..., PT:=..., Q=>, ET=>...)` appears 15+ times
- Internal variable `s_bX1轴_request前移` has inconsistent underscore usage (line 1373)

### Phase 2: FB_1004 Feeder Internal Variables Fix
**Priority**: P0 - Must fix  
**Effort**: ~1 hour  
**Risk**: Medium (only internal vars, interface already done)

**Variables to Replace** (19 locations):
```scl
// Current (Chinese)          -> Target (English)
s_i步序                     -> s_iCurrentStep
s_b运行中                   -> s_bRunning
s_b故障                     -> s_bFault
s_b启动触发                 -> s_bStartTriggered
s_bX2轴请求前移            -> s_bX2Axis_RequestFwd
s_bX2轴请求后移            -> s_bX2Axis_RequestRev
s_bX2轴在待机位           -> s_bX2Axis_AtStandbyPos
s_bX2轴在取料位           -> s_bX2Axis_AtPickupPos
s_b取放料曾工作           -> s_bPickPlaceHasWorked
s_b上次放料完成           -> s_bPrevFeedComplete
s_b等待打胶机响应         -> s_bWaitingGlueMachine
s_b初始化完成             -> s_bInitComplete
s_b初始化中               -> s_bInitializing
s_i活跃报警               -> s_iActiveAlarmCode
s_b手动允许               -> s_bManualAllowed
// Plus output assignments using Chinese names like:
o_b允许抓料               -> o_bAllowPickup
o_b安全区信号             -> o_bSafetyZoneSignal
```

**Inconsistencies Found** (must fix):
- Line 324: `o_b允许抓料 := FALSE;` (should be `o_bAllowPickup`)
- Line 338: `IF i_bX2轴_伺服故障 THEN` (should be `i_bX2Axis_ServoFault`)
- Line 607: `s_bX2轴_request后移   := FALSE;` (inconsistent underscore)
- Line 817: `s_bX2轴_request后移   := FALSE;` (same issue)

### Phase 3: FB_ExternalDeviceInteraction Complete Rewrite
**Priority**: P0 - Must fix  
**Effort**: ~1.5 hours  
**Risk**: Medium-High (47 interface vars + logic)

**Interface Variables** (47 total):
**Inputs (27)**:
| Chinese | English | Purpose |
|---------|---------|---------|
| `i_b使能` | `i_bEnable` | System enable |
| `i_b自动模式` | `i_bAutoMode` | Auto mode |
| `i_b手动模式` | `i_bManualMode` | Manual mode |
| `i_b启动` | `i_bStart` | Start button |
| `i_b停止` | `i_bStop` | Stop button |
| `i_b复位` | `i_bReset` | Reset button |
| `i_b组框机_自动中` | `i_bFrameMachine_AutoRunning` | Frame machine status |
| `i_b组框机_允许送料` | `i_bFrameMachine_AllowFeed` | Feed permission |
| ... (21 more) | ... | ... |

**Outputs (20)**:
| Chinese | English | Purpose |
|---------|---------|---------|
| `q_b组框机_请求送料` | `q_bFrameMachine_RequestFeed` | Request feed |
| `q_b组框机_暂停` | `q_bFrameMachine_Pause` | Pause command |
| ... (18 more) | ... | ... |

**Internal Variables** (2):
- `b安全条件满足` → `bSafetyConditionMet`
- `i外部设备报警码` → `iExternalDeviceAlarmCode`

### Phase 4: Code Quality Improvements (Optional)
**Priority**: P1 - Nice to have  
**Effort**: ~2 hours  
**Risk**: Low (optimization, no logic change)

**4.1 Extract Output Clearing METHOD**
Create reusable METHOD in each FB:
```scl
METHOD OutputClearing : VOID
    // Centralized output reset - call from Enable=FALSE, Stop, Fault, Reset
    o_bLift_Up := FALSE;
    o_bLift_Down := FALSE;
    // ... all other outputs
END_METHOD
```

**Benefits**:
- Reduce code duplication by 40%+
- Single point of maintenance
- Easier to add new outputs

**4.2 Standardize State Machine Template**
Document mandatory structure for all FBs:
```
1. Enable & Init (lines 1-50)
2. Fault Detection (lines 51-100)
3. Mode Dispatch (Auto/Manual) (lines 101-130)
4. Stop/Reset Handling (lines 131-180)
5. State Machine CASE (lines 181-800)
6. Manual Control METHOD (lines 801-1000)
7. Output Summary (lines 1001-1050)
```

**4.3 Add Consistency Validation Script**
Create Grep-based checklist:
```bash
# Search for remaining Chinese variables
grep -P '[\x{4e00}-\x{9fff}]' *.scl | grep -v '^\s*//' | grep -v '^\s*\*'
```

---

## Success Criteria

### Functional Criteria
✅ Zero compilation errors (TC001/TC002) after refactoring  
✅ All 6 FBs pass syntax check in TIA Portal / VS Code  
✅ Interface consistency: GlobalVars ↔ OB1 ↔ FB (100% match)

### Quality Criteria
✅ Zero Chinese characters in **variable names** (validated via Grep, excluding comments)
✅ All variables follow 801 naming convention (prefix_type + SemanticName)
✅ Comment-to-code ratio maintained at current level (~40%)
✅ All code comments remain in Chinese for domestic engineer readability
✅ Grep pattern: `[\x{4e00}-\x{9fff}]` should only match in comment lines (// or * or (*))

### Maintainability Criteria
✅ Duplicate code reduced by ≥30% (if Phase 4 implemented)  
✅ Uniform file structure across all FBs  
✅ Updated documentation (CHG + IFC files for modified components)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Logic error during rename | Medium | High | Line-by-line review + diff comparison |
| Missed variable occurrence | Medium | Medium | Automated Grep validation |
| Interface mismatch with OB1 | Low | High | Cross-reference GlobalVars.db V3.0.0 |
| Regression in state machine | Low | Critical | Unit test each FB independently |
| Documentation out of sync | Medium | Low | Update CHG/IFC docs simultaneously |

---

## Rollback Plan
If critical bug found post-refactoring:
1. Git revert to V5.0.0 tagged commit
2. Re-apply fixes incrementally (one FB at a time)
3. Extended testing period (48h vs normal 24h)

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|-------------|
| Phase 1: FB_1003 Rewrite | 3h | None (start first) |
| Phase 2: FB_1004 Fix | 1h | None (parallel with P1) |
| Phase 3: FB_ExternalDevice | 1.5h | None (parallel with P1/P2) |
| Phase 4: Quality Improvements | 2h | P1+P2+P3 complete |
| Testing & Validation | 1h | All phases complete |
| Documentation Update | 1h | All phases complete |
| **Total** | **~9.5h** | - |

**Recommended Execution Order**: P1 → P2+P3 (parallel) → P4 → Test → Docs
