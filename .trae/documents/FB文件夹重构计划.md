# FB文件夹重构计划

## 1. 项目现状分析

### 1.1 当前文件结构
当前项目结构如下：
- **通用ST程序及变量表/**
  - **Device/**
    - FB_Device_IOMapping_V3.0.0.st
    - FB_Device_Layer_V3.0.0.st
    - FB_Device_ServoAxis_V3.0.0.st
    - FB_Device_Conveyor_V3.0.0.st
    - FB_Device_Safety_V3.0.0.st
  - **Logic/**
    - FB_Logic_ConveyorControl_V3.0.0.st
    - FB_Logic_GlueMachineInterface_V3.0.0.st
    - FB_Logic_LayerFeed_V3.0.0.st
    - FB_Logic_Layer_V3.0.0.st
    - FB_Logic_PickPlace_V3.0.0.st
    - FB_Logic_ServoControl_V3.0.0.st
  - **Main/**
    - FB_Main_AlarmManager_V3.0.0.st
    - FB_Main_Control_V3.0.0.st
    - FB_Main_Initialization_V3.0.0.st
    - FB_Main_LayerCoordinator_V3.0.0.st
    - FB_Main_SafetyManager_V3.0.0.st
    - FB_Main_SystemControl_V3.0.0.st
    - MainProgram_V3.0.0.st
  - PLC变量定义文档_VAR-DJ-2026-005-V3.0.0.md
- **程序文档/**
  - **FB使用文档/**
    - FB_Device_Conveyor使用文档.md
    - FB_Device_IOMapping使用文档.md
    - FB_Device_Safety使用文档.md
    - FB_Device_ServoAxis使用文档.md
    - FB_Logic_ConveyorControl使用文档.md
    - FB_Logic_LayerFeed使用文档.md
    - FB_Logic_PickPlace使用文档.md
    - FB_Logic_ServoControl使用文档.md
    - FB_Main_AlarmManager使用文档.md
    - FB_Main_LayerCoordinator使用文档.md
    - FB_Main_SafetyManager使用文档.md
    - FB_Main_SystemControl使用文档.md
  - 015_DJ-2026-005_IO分配表_IO-V3.0.0.md
  - 016_DJ-2026-005_PLC程序设计总文档_PLC-V3.0.0.md

### 1.2 存在的问题
- FB文件和文档分离在不同目录，不利于管理
- 每个FB缺少详细设计文档和接口文档
- 缺少FB变更记录（变更单和变更台帐）
- 不符合用户要求的"每个FB单独文件夹，文件夹包含相关文档"的结构

## 2. 重构目标

### 2.1 目标结构
每个FB单独一个文件夹，文件夹包含以下内容：
- FB使用说明
- FB详细设计文档
- FB接口文档
- FB变更记录（变更单和变更台帐）

### 2.2 具体要求
- 保持三层架构（设备层、逻辑层、主控层）
- 每个FB文件夹包含完整的文档体系
- 变更记录符合全局规范
- 确保文件命名和版本号的一致性

## 3. 重构方案

### 3.1 文件夹结构设计

```
02_PLC程序/
├── 通用ST程序及变量表/
│   ├── Device/
│   │   ├── FB_Device_IOMapping/
│   │   │   ├── FB_Device_IOMapping_V3.0.0.st
│   │   │   ├── FB_Device_IOMapping使用说明.md
│   │   │   ├── FB_Device_IOMapping详细设计文档.md
│   │   │   ├── FB_Device_IOMapping接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Device_Layer/
│   │   │   ├── FB_Device_Layer_V3.0.0.st
│   │   │   ├── FB_Device_Layer使用说明.md
│   │   │   ├── FB_Device_Layer详细设计文档.md
│   │   │   ├── FB_Device_Layer接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Device_ServoAxis/
│   │   │   ├── FB_Device_ServoAxis_V3.0.0.st
│   │   │   ├── FB_Device_ServoAxis使用说明.md
│   │   │   ├── FB_Device_ServoAxis详细设计文档.md
│   │   │   ├── FB_Device_ServoAxis接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Device_Conveyor/
│   │   │   ├── FB_Device_Conveyor_V3.0.0.st
│   │   │   ├── FB_Device_Conveyor使用说明.md
│   │   │   ├── FB_Device_Conveyor详细设计文档.md
│   │   │   ├── FB_Device_Conveyor接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   └── FB_Device_Safety/
│   │       ├── FB_Device_Safety_V3.0.0.st
│   │       ├── FB_Device_Safety使用说明.md
│   │       ├── FB_Device_Safety详细设计文档.md
│   │       ├── FB_Device_Safety接口文档.md
│   │       └── 变更记录/
│   │           ├── 变更单.md
│   │           └── 变更台帐.md
│   ├── Logic/
│   │   ├── FB_Logic_ConveyorControl/
│   │   │   ├── FB_Logic_ConveyorControl_V3.0.0.st
│   │   │   ├── FB_Logic_ConveyorControl使用说明.md
│   │   │   ├── FB_Logic_ConveyorControl详细设计文档.md
│   │   │   ├── FB_Logic_ConveyorControl接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Logic_GlueMachineInterface/
│   │   │   ├── FB_Logic_GlueMachineInterface_V3.0.0.st
│   │   │   ├── FB_Logic_GlueMachineInterface使用说明.md
│   │   │   ├── FB_Logic_GlueMachineInterface详细设计文档.md
│   │   │   ├── FB_Logic_GlueMachineInterface接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Logic_LayerFeed/
│   │   │   ├── FB_Logic_LayerFeed_V3.0.0.st
│   │   │   ├── FB_Logic_LayerFeed使用说明.md
│   │   │   ├── FB_Logic_LayerFeed详细设计文档.md
│   │   │   ├── FB_Logic_LayerFeed接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Logic_Layer/
│   │   │   ├── FB_Logic_Layer_V3.0.0.st
│   │   │   ├── FB_Logic_Layer使用说明.md
│   │   │   ├── FB_Logic_Layer详细设计文档.md
│   │   │   ├── FB_Logic_Layer接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Logic_PickPlace/
│   │   │   ├── FB_Logic_PickPlace_V3.0.0.st
│   │   │   ├── FB_Logic_PickPlace使用说明.md
│   │   │   ├── FB_Logic_PickPlace详细设计文档.md
│   │   │   ├── FB_Logic_PickPlace接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   └── FB_Logic_ServoControl/
│   │       ├── FB_Logic_ServoControl_V3.0.0.st
│   │       ├── FB_Logic_ServoControl使用说明.md
│   │       ├── FB_Logic_ServoControl详细设计文档.md
│   │       ├── FB_Logic_ServoControl接口文档.md
│   │       └── 变更记录/
│   │           ├── 变更单.md
│   │           └── 变更台帐.md
│   ├── Main/
│   │   ├── FB_Main_AlarmManager/
│   │   │   ├── FB_Main_AlarmManager_V3.0.0.st
│   │   │   ├── FB_Main_AlarmManager使用说明.md
│   │   │   ├── FB_Main_AlarmManager详细设计文档.md
│   │   │   ├── FB_Main_AlarmManager接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Main_Control/
│   │   │   ├── FB_Main_Control_V3.0.0.st
│   │   │   ├── FB_Main_Control使用说明.md
│   │   │   ├── FB_Main_Control详细设计文档.md
│   │   │   ├── FB_Main_Control接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Main_Initialization/
│   │   │   ├── FB_Main_Initialization_V3.0.0.st
│   │   │   ├── FB_Main_Initialization使用说明.md
│   │   │   ├── FB_Main_Initialization详细设计文档.md
│   │   │   ├── FB_Main_Initialization接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Main_LayerCoordinator/
│   │   │   ├── FB_Main_LayerCoordinator_V3.0.0.st
│   │   │   ├── FB_Main_LayerCoordinator使用说明.md
│   │   │   ├── FB_Main_LayerCoordinator详细设计文档.md
│   │   │   ├── FB_Main_LayerCoordinator接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Main_SafetyManager/
│   │   │   ├── FB_Main_SafetyManager_V3.0.0.st
│   │   │   ├── FB_Main_SafetyManager使用说明.md
│   │   │   ├── FB_Main_SafetyManager详细设计文档.md
│   │   │   ├── FB_Main_SafetyManager接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   ├── FB_Main_SystemControl/
│   │   │   ├── FB_Main_SystemControl_V3.0.0.st
│   │   │   ├── FB_Main_SystemControl使用说明.md
│   │   │   ├── FB_Main_SystemControl详细设计文档.md
│   │   │   ├── FB_Main_SystemControl接口文档.md
│   │   │   └── 变更记录/
│   │   │       ├── 变更单.md
│   │   │       └── 变更台帐.md
│   │   └── MainProgram/
│   │       ├── MainProgram_V3.0.0.st
│   │       ├── MainProgram使用说明.md
│   │       ├── MainProgram详细设计文档.md
│   │       ├── MainProgram接口文档.md
│   │       └── 变更记录/
│   │           ├── 变更单.md
│   │           └── 变更台帐.md
│   └── PLC变量定义文档_VAR-DJ-2026-005-V3.0.0.md
└── 程序文档/
    ├── 015_DJ-2026-005_IO分配表_IO-V3.0.0.md
    └── 016_DJ-2026-005_PLC程序设计总文档_PLC-V3.0.0.md
```

### 3.2 实施步骤

#### 3.2.1 准备工作
1. 检查当前文件结构，确认所有FB文件和文档的位置
2. 备份现有文件，确保数据安全
3. 制定详细的实施计划，明确每个步骤的任务和时间

#### 3.2.2 文件夹创建
1. 为每个FB创建单独的文件夹
2. 在每个FB文件夹中创建变更记录子文件夹

#### 3.2.3 文件迁移
1. 将FB程序文件移动到对应的文件夹中
2. 将现有的使用文档移动到对应的文件夹中，并重命名为"使用说明.md"

#### 3.2.4 文档创建
1. 为每个FB创建详细设计文档
2. 为每个FB创建接口文档
3. 为每个FB创建变更记录（变更单和变更台帐）

#### 3.2.5 验证与测试
1. 验证所有文件是否正确迁移
2. 验证所有文档是否完整
3. 验证文件夹结构是否符合要求

## 4. 文档模板

### 4.1 FB使用说明模板
```markdown
# [FB名称] 使用说明

## 1. 功能概述

## 2. 接口定义

## 3. 使用方法

## 4. 维护与故障排除

## 5. 版本历史
```

### 4.2 FB详细设计文档模板
```markdown
# [FB名称] 详细设计文档

## 1. 功能描述

## 2. 设计思路

## 3. 状态机设计

## 4. 实现细节

## 5. 测试用例
```

### 4.3 FB接口文档模板
```markdown
# [FB名称] 接口文档

## 1. 输入参数

## 2. 输出参数

## 3. 内部变量

## 4. 调用关系
```

### 4.4 变更单模板
```markdown
# [FB名称] 变更单

## 1. 变更基本信息

## 2. 变更内容

## 3. 影响分析

## 4. 验证计划

## 5. 审批流程
```

### 4.5 变更台帐模板
```markdown
# [FB名称] 变更台帐

## 变更记录
| 变更编号 | 变更日期 | 变更内容 | 变更原因 | 责任人 | 审批人 |
|----------|----------|----------|----------|--------|--------|
```

## 5. 风险评估

### 5.1 潜在风险
1. 文件迁移过程中可能出现文件丢失
2. 文档创建过程中可能出现内容不完整
3. 文件夹结构变更可能影响现有程序的引用

### 5.2 风险应对措施
1. 迁移前备份所有文件，确保数据安全
2. 迁移过程中逐步进行，每完成一个FB的迁移就验证一次
3. 迁移完成后，检查所有程序文件的引用路径是否正确

## 6. 时间计划

| 步骤 | 时间 | 任务 |
|------|------|------|
| 准备工作 | 2026-04-23 | 检查文件结构，备份现有文件 |
| 文件夹创建 | 2026-04-23 | 为每个FB创建文件夹和变更记录子文件夹 |
| 文件迁移 | 2026-04-23 | 移动FB程序文件和使用文档 |
| 文档创建 | 2026-04-24 | 创建详细设计文档、接口文档和变更记录 |
| 验证与测试 | 2026-04-24 | 验证文件迁移和文档创建的完整性 |

## 7. 预期成果

1. 每个FB都有单独的文件夹，包含完整的文档体系
2. 文件夹结构清晰，符合用户要求
3. 文档内容完整，符合全局规范
4. 变更记录齐全，便于后续维护和管理
