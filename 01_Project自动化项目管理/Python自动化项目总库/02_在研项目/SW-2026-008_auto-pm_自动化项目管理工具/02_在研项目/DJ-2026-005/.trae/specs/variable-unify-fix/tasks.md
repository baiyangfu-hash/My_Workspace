# PLC变量命名全面统一修复 - Tasks

## [x] Task 1: 修复主控程序VAR声明区14处不一致变量
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - `b允许抓料` → `q_b允许抓料` (VAR_OUTPUT, 行191)
  - `b安全区信号` → `q_b安全区信号` (VAR_OUTPUT, 行192)
  - `bLx_阻挡下降[1..4]` → `i_bLx_阻挡下降[1..4]` (VAR, 行264)
  - `bLx_阻挡上升[1..4]` → `i_bLx_阻挡上升[1..4]` (VAR, 行265)
  - `bLx_分料推出[1..4]` → `i_bLx_分料推出[1..4]` (VAR, 行266)
  - `bLx_分料复位[1..4]` → `i_bLx_分料复位[1..4]` (VAR, 行267)
  - `bLx_输送正转[1..4]` → `i_bLx_输送正转[1..4]` (VAR, 行268)
  - `bLx_输送反转[1..4]` → `i_bLx_输送反转[1..4]` (VAR, 行269)
  - `b急停按钮` → `i_b急停按钮` (VAR_INPUT, 行292)
  - `b前门锁定` → `i_b前门锁定` (VAR_INPUT, 行294)
  - `b后门锁定` → `i_b后门锁定` (VAR_INPUT, 行295)
  - `b安全继电器启动` → `q_b安全继电器启动` (VAR_OUTPUT, 行298)

## [x] Task 2: 修复主控程序Step 8输出映射赋值引用
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  - `b安全继电器启动 := TRUE` → `q_b安全继电器启动 := TRUE` (行884)
  - `b安全继电器启动 := FALSE` → `q_b安全继电器启动 := FALSE` (行889)

## [x] Task 3: 全局验证 — 零残留检查
- **Priority**: P0
- **Depends On**: Tasks 1, 2
- **Description**:
  - Grep搜索所有ST文件，确认无旧名残留 ✅
  - 确认VAR声明、IO映射、FB调用三处变量名完全一致 ✅

## [x] Task 4: 同步PLC变量定义文档 (REQ-3)
- **Priority**: P0
- **Description**:
  - DI变量: `b急停/前门/后门` → `i_b急停/前门/后门` (3处) ✅
  - DO变量: `b允许抓料/安全区信号/安全继电器启动` → `q_b_xxx` (3处) ✅
  - FB名称: 5个旧FB名→新801规范名 (93处) ✅

## [x] Task 5: 同步报警码定义文档 (REQ-4)
- **Priority**: P0
- **Description**: 已确认无需修改 ✅

## [x] Task 6: 同步程序架构文档+详细设计说明书 (REQ-5)
- **Priority**: P0
- **Description**:
  - 详细设计说明书: 5处修复(FB名+变量名) ✅
  - 程序架构文档: 已确认无需修改 ✅

## [x] Task 7: 额外发现 — 3个FBD使用说明.md旧FB名修复
- **Priority**: P0
- **Description**:
  - 四层输送机/FBD使用说明.md: 31处 ✅
  - 打胶机送料机构/FBD使用说明.md: 14处 ✅
  - 取放料机构/FBD使用说明.md: 17处 ✅
