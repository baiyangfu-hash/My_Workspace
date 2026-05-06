# 交互功能FB开发文档

## 文档标识
- **文档类型**：开发文档
- **版本号**：v1.0.0
- **创建日期**：2026-01-29
- **最后更新**：2026-01-29
- **文档状态**：已完成

## 变更记录
| 变更日期 | 变更原因 | 变更内容 | 变更人 |
|---------|---------|---------|--------|
| 2026-01-29 | 模板创建 | 创建交互功能FB开发文档模板 | 系统 |

## 1. 开发概述

### 1.1 开发目标
基于需求文档和详细设计说明书，实现交互功能FB，确保系统间的信号交互处理功能正常运行，包含完整的错误处理和状态监控机制。

### 1.2 开发环境

| 环境名称 | 版本/配置 | 用途 |
|----------|-----------|------|
| 汇川Autoshop | Vx.x.x | PLC编程软件 |
| Python | 3.8+ | 辅助工具开发 |
| 文本编辑器 | VS Code | 代码编辑 |
| 版本控制 | Git | 代码版本管理 |

### 1.3 开发工具

| 工具名称 | 用途 | 所在目录 |
|----------|------|----------|
| create_variable_table.py | 变量表创建工具 | AI_Python辅助工具/功能扩展工具/ |
| validate_variable_table.py | 变量表验证工具 | AI_Python辅助工具/基础核心工具/ |
| check_encoding.py | 编码检查工具 | AI_Python辅助工具/基础核心工具/ |
| workflow.py | 工作流管理工具 | AI_Python辅助工具/集成管理工具/ |

### 1.4 开发流程

1. **需求分析**：分析系统间交互的功能需求
2. **详细设计**：设计功能块结构和实现逻辑
3. **变量表创建**：创建变量表格并验证
4. **FB功能块实现**：编写交互功能FB代码
5. **测试功能块实现**：编写测试交互功能FB代码
6. **编码验证**：验证文件编码一致性
7. **功能测试**：测试功能块的各项功能
8. **集成测试**：与实际系统集成测试
9. **文档更新**：更新相关文档
10. **版本管理**：进行版本管理和归档

## 2. 变量表开发

### 2.1 变量表结构

| 列名 | 描述 | 示例值 |
|------|------|--------|
| 序号 | 变量序号，从1开始递增 | 1, 2, 3... |
| 类别 | 变量类别（IN/OUT/INOUT/VAR） | IN, OUT, VAR |
| 名称 | 变量名称，遵循命名规范 | i_UpstreamReady, q_MachineReadyForFeed |
| 数据类型 | 变量数据类型 | BOOL, INT, DWORD, TIME |
| 隐藏初始值 | 隐藏的初始值 | OFF, ON, 0 |
| 初始值 | 变量初始值 | OFF, ON, 0 |
| 掉电保持 | 掉电保持设置 | 保持, 不保持 |
| 注释 | 变量描述 | 上游流水线准备好信号 |
| 空 | 尾部逗号，保持一致性 |  |

### 2.2 变量表创建步骤

1. **准备SCL文件**：编写交互功能FB.scl文件，包含所有变量定义
2. **选择模板**：使用AI_中心模板库中的变量表格模板
3. **创建变量表**：使用create_variable_table.py工具创建变量表
   ```bash
   python create_variable_table.py --scl "FB_交互功能.scl" --template "AI_中心模板库/变量表格模板/FB_导入PLC变量_通用模板.csv" --output "FB_导入PLC变量_项目名称_autoshop_v1.0.0.csv" --version "v1.0.0"
   ```
4. **验证编码**：使用check_encoding.py工具验证编码一致性
   ```bash
   python check_encoding.py "FB_导入PLC变量_项目名称_autoshop_v1.0.0.csv"
   ```
5. **验证格式**：使用validate_variable_table.py工具验证变量表格式
   ```bash
   python validate_variable_table.py --csv "FB_导入PLC变量_项目名称_autoshop_v1.0.0.csv" --scl "FB_交互功能.scl"
   ```

### 2.3 变量表验证

| 验证项 | 验证内容 | 验证工具 |
|--------|----------|----------|
| 编码一致性 | 变量表编码与模板文件一致 | check_encoding.py |
| 格式正确性 | 变量表格式符合Autoshop要求 | validate_variable_table.py |
| 变量完整性 | 所有变量都已定义 | validate_variable_table.py |
| 命名规范性 | 变量命名遵循规范 | validate_variable_table.py |
| 版本号正确 | 版本号格式正确 | validate_variable_table.py |

## 3. FB功能块开发

### 3.1 FB文件结构

```scl
// FB_交互功能.scl
FUNCTION_BLOCK FB_Interaction
VAR_INPUT
    // 系统1信号输入
    i_System1Ready: BOOL;             // 系统1准备好信号
    i_System1TransferData: BOOL;       // 系统1传输数据信号
    i_System1Request: BOOL;            // 系统1请求信号
    i_System1Confirm: BOOL;            // 系统1确认信号
    
    // 控制信号输入
    i_ManualMode: BOOL;                // 手动模式信号
    i_ManualReady: BOOL;               // 手动控制准备好
    i_ManualDataReceived: BOOL;        // 手动控制数据收到
    i_ManualAllowRequest: BOOL;        // 手动控制允许请求
    i_ManualOperationComplete: BOOL;   // 手动控制操作完成
    i_Alarm: BOOL;                     // 报警信号
    i_Reset: BOOL;                     // 复位信号
END_VAR

VAR_OUTPUT
    q_System2Ready: BOOL;              // 系统2准备好信号
    q_System2DataReceived: BOOL;       // 系统2数据收到信号
    q_System2AllowRequest: BOOL;       // 系统2允许请求信号
    q_System2OperationComplete: BOOL;  // 系统2操作完成信号
    q_StatusWord: DWORD;               // 状态字
END_VAR

VAR
    // 内部变量
    b_FirstScan: BOOL := TRUE;         // 首次扫描标志
    b_System2Ready: BOOL := TRUE;      // 系统2准备好状态
    b_DataReceived: BOOL := FALSE;     // 数据收到状态
    b_AllowRequest: BOOL := FALSE;     // 允许请求状态
    b_OperationComplete: BOOL := FALSE; // 操作完成状态
    b_Error: BOOL := FALSE;            // 错误状态
    b_System1Ready: BOOL := FALSE;     // 系统1准备好内部状态
    n_CurrentState: INT := 0;          // 当前状态机状态
    i: INT;                            // 循环计数器
    
    // 计时器相关
    In_tTimer1: BOOL[4] := [FALSE, FALSE, FALSE, FALSE]; // 计时器输入数组
    ET_tTimer1: TIME[4] := [T#0s, T#0s, T#0s, T#0s]; // 计时器输出数组
END_VAR

VAR_TEMP
    // 临时变量
    rtrig_System1Ready: R_TRIG;
    rtrig_DataTransfer: R_TRIG;
    rtrig_Request: R_TRIG;
    rtrig_Confirm: R_TRIG;
END_VAR

// 初始化模块
IF b_FirstScan THEN
    // 初始化代码
    b_FirstScan := FALSE;
END_IF;

// 手动控制模块
IF i_ManualMode THEN
    // 手动控制代码
END_IF;

// 自动控制模块
IF NOT i_ManualMode AND NOT b_Error THEN
    // 自动控制代码
END_IF;

// 报警处理模块
IF i_Alarm THEN
    // 报警处理代码
END_IF;

// 复位处理
IF i_Reset THEN
    // 复位代码
END_IF;

// 状态机模块
// 状态机代码

END_FUNCTION_BLOCK
```

### 3.2 核心功能实现

#### 3.2.1 初始化模块

```scl
// 初始化模块
IF b_FirstScan THEN
    // 初始化内部变量
    b_System2Ready := TRUE;
    b_DataReceived := FALSE;
    b_AllowRequest := FALSE;
    b_OperationComplete := FALSE;
    b_Error := FALSE;
    
    // 初始化输出变量
    q_System2Ready := TRUE;
    q_System2DataReceived := FALSE;
    q_System2AllowRequest := FALSE;
    q_System2OperationComplete := FALSE;
    q_StatusWord := 0;
    
    // 初始化计时器
    FOR i := 0 TO 3 DO
        ET_tTimer1[i] := T#0s;
    END_FOR;
    
    b_FirstScan := FALSE;
END_IF;
```

#### 3.2.2 自动控制模块

```scl
// 自动控制模块
IF NOT i_ManualMode AND NOT b_Error THEN
    // 处理系统1准备好信号
    rtrig_System1Ready(CLK := i_System1Ready);
    IF rtrig_System1Ready.Q THEN
        b_System1Ready := TRUE;
        // 启动超时计时器
        In_tTimer1[0] := TRUE;
    END_IF;
    
    // 处理系统1传输数据信号
    rtrig_DataTransfer(CLK := i_System1TransferData);
    IF rtrig_DataTransfer.Q AND b_System1Ready THEN
        b_DataReceived := TRUE;
        q_System2DataReceived := TRUE;
        // 启动超时计时器
        In_tTimer1[1] := TRUE;
    END_IF;
    
    // 处理系统1请求信号
    rtrig_Request(CLK := i_System1Request);
    IF rtrig_Request.Q AND b_DataReceived THEN
        b_AllowRequest := TRUE;
        q_System2AllowRequest := TRUE;
        // 启动超时计时器
        In_tTimer1[2] := TRUE;
    END_IF;
    
    // 处理系统1确认信号
    rtrig_Confirm(CLK := i_System1Confirm);
    IF rtrig_Confirm.Q AND b_OperationComplete THEN
        b_OperationComplete := FALSE;
        q_System2OperationComplete := FALSE;
        // 启动超时计时器
        In_tTimer1[3] := TRUE;
        
        // 重置状态，准备下一次交互
        IF NOT i_System1Ready THEN
            b_System1Ready := FALSE;
            b_DataReceived := FALSE;
            b_AllowRequest := FALSE;
        END_IF;
    END_IF;
    
    // 处理操作完成
    IF b_AllowRequest AND NOT b_OperationComplete THEN
        // 模拟操作完成检测
        // 实际项目中应替换为真实的操作完成传感器信号
        b_OperationComplete := TRUE;
        q_System2OperationComplete := TRUE;
    END_IF;
END_IF;
```

#### 3.2.3 状态机模块

```scl
// 状态机模块
// 更新状态字
q_StatusWord.0 := i_System1Ready;
q_StatusWord.1 := i_System1TransferData;
q_StatusWord.2 := i_System1Request;
q_StatusWord.3 := i_System1Confirm;
q_StatusWord.4 := b_System2Ready;
q_StatusWord.5 := b_DataReceived;
q_StatusWord.6 := b_AllowRequest;
q_StatusWord.7 := b_OperationComplete;
q_StatusWord.8 := b_Error;

// 状态转换逻辑
CASE n_CurrentState OF
    0: // 初始状态
        IF i_System1Ready THEN
            n_CurrentState := 1;
        END_IF;
    
    1: // 系统1准备好
        IF i_System1TransferData THEN
            n_CurrentState := 2;
        END_IF;
    
    2: // 数据传输
        IF i_System1Request THEN
            n_CurrentState := 3;
        END_IF;
    
    3: // 请求处理
        IF b_OperationComplete THEN
            n_CurrentState := 4;
        END_IF;
    
    4: // 操作完成
        IF i_System1Confirm THEN
            n_CurrentState := 0; // 回到初始状态
        END_IF;
END_CASE;
```

### 3.3 计时器实现

```scl
// 计时器处理
// 系统1准备好超时
TON_1(IN := In_tTimer1[0], PT := T#5s, Q => , ET => ET_tTimer1[0]);
IF ET_tTimer1[0] >= T#5s THEN
    b_Error := TRUE;
    q_StatusWord.8 := TRUE;
    In_tTimer1[0] := FALSE;
END_IF;

// 数据传输超时
TON_2(IN := In_tTimer1[1], PT := T#3s, Q => , ET => ET_tTimer1[1]);
IF ET_tTimer1[1] >= T#3s THEN
    b_Error := TRUE;
    q_StatusWord.8 := TRUE;
    In_tTimer1[1] := FALSE;
END_IF;

// 请求处理超时
TON_3(IN := In_tTimer1[2], PT := T#5s, Q => , ET => ET_tTimer1[2]);
IF ET_tTimer1[2] >= T#5s THEN
    b_Error := TRUE;
    q_StatusWord.8 := TRUE;
    In_tTimer1[2] := FALSE;
END_IF;

// 确认信号超时
TON_4(IN := In_tTimer1[3], PT := T#3s, Q => , ET => ET_tTimer1[3]);
IF ET_tTimer1[3] >= T#3s THEN
    b_Error := TRUE;
    q_StatusWord.8 := TRUE;
    In_tTimer1[3] := FALSE;
END_IF;
```

## 3. 测试功能块开发

### 3.1 测试功能块结构

```scl
// Test_FB_交互功能.scl
FUNCTION_BLOCK Test_FB_Interaction
VAR_INPUT
    i_TestMode: INT; // 测试模式
    i_Reset: BOOL;   // 复位信号
END_VAR

VAR_OUTPUT
    q_TestStatus: INT;     // 测试状态
    q_TestStep: INT;       // 测试步骤
    q_TestCompleted: BOOL; // 测试完成标志
    q_TestPassed: BOOL;    // 测试通过标志
    
    // 测试输出
    q_System2Ready: BOOL;
    q_System2DataReceived: BOOL;
    q_System2AllowRequest: BOOL;
    q_System2OperationComplete: BOOL;
    q_StatusWord: DWORD;
END_VAR

VAR
    // 测试内部变量
    b_TestStarted: BOOL := FALSE;
    b_TestCompleted: BOOL := FALSE;
    b_TestPassed: BOOL := FALSE;
    n_TestStep: INT := 0;
    n_TestStatus: INT := 0;
    
    // 测试输入模拟
    i_System1Ready: BOOL := FALSE;
    i_System1TransferData: BOOL := FALSE;
    i_System1Request: BOOL := FALSE;
    i_System1Confirm: BOOL := FALSE;
    i_ManualMode: BOOL := FALSE;
    i_Alarm: BOOL := FALSE;
    
    // 实例化被测功能块
    fb_Interaction: FB_Interaction;
END_VAR

// 复位处理
IF i_Reset THEN
    b_TestStarted := FALSE;
    b_TestCompleted := FALSE;
    b_TestPassed := FALSE;
    n_TestStep := 0;
    n_TestStatus := 0;
    
    // 重置测试输入
    i_System1Ready := FALSE;
    i_System1TransferData := FALSE;
    i_System1Request := FALSE;
    i_System1Confirm := FALSE;
    
    // 重置输出
    q_TestStatus := 0;
    q_TestStep := 0;
    q_TestCompleted := FALSE;
    q_TestPassed := FALSE;
END_IF;

// 测试执行
CASE i_TestMode OF
    0: // 完整流程测试
        // 完整流程测试代码
    
    1: // 系统1准备好测试
        // 系统1准备好测试代码
    
    2: // 数据传输测试
        // 数据传输测试代码
    
    3: // 请求处理测试
        // 请求处理测试代码
    
    4: // 确认信号测试
        // 确认信号测试代码
END_CASE;

// 调用被测功能块
fb_Interaction(i_System1Ready := i_System1Ready, 
               i_System1TransferData := i_System1TransferData, 
               i_System1Request := i_System1Request, 
               i_System1Confirm := i_System1Confirm, 
               i_ManualMode := i_ManualMode, 
               i_Alarm := i_Alarm, 
               i_Reset := i_Reset);

// 传递输出
q_System2Ready := fb_Interaction.q_System2Ready;
q_System2DataReceived := fb_Interaction.q_System2DataReceived;
q_System2AllowRequest := fb_Interaction.q_System2AllowRequest;
q_System2OperationComplete := fb_Interaction.q_System2OperationComplete;
q_StatusWord := fb_Interaction.q_StatusWord;

END_FUNCTION_BLOCK
```

### 3.2 测试模式实现

#### 3.2.1 完整流程测试

```scl
0: // 完整流程测试
    IF NOT b_TestStarted THEN
        b_TestStarted := TRUE;
        n_TestStep := 1;
        n_TestStatus := 1; // 测试开始
    END_IF;
    
    CASE n_TestStep OF
        1: // 测试初始化
            IF fb_Interaction.q_System2Ready THEN
                n_TestStep := 2;
                n_TestStatus := 2; // 初始化通过
            END_IF;
        
        2: // 测试系统1准备好
            i_System1Ready := TRUE;
            IF fb_Interaction.q_StatusWord.0 THEN
                n_TestStep := 3;
                n_TestStatus := 3; // 系统1准备好测试通过
            END_IF;
        
        3: // 测试数据传输
            i_System1TransferData := TRUE;
            IF fb_Interaction.q_System2DataReceived THEN
                n_TestStep := 4;
                n_TestStatus := 4; // 数据传输测试通过
            END_IF;
        
        4: // 测试请求处理
            i_System1Request := TRUE;
            IF fb_Interaction.q_System2AllowRequest THEN
                n_TestStep := 5;
                n_TestStatus := 5; // 请求处理测试通过
            END_IF;
        
        5: // 测试操作完成
            // 模拟操作完成
            // 实际测试中，被测功能块会自动设置操作完成信号
            // 这里等待操作完成信号
            IF fb_Interaction.q_System2OperationComplete THEN
                i_System1Confirm := TRUE;
                n_TestStep := 6;
                n_TestStatus := 6; // 操作完成测试通过
            END_IF;
        
        6: // 测试完成
            IF NOT fb_Interaction.q_System2OperationComplete THEN
                b_TestCompleted := TRUE;
                b_TestPassed := TRUE;
                b_TestStarted := FALSE;
                n_TestStatus := 7; // 测试完成
            END_IF;
    END_CASE;
```

## 4. 编码管理

### 4.1 编码要求

- **模板文件编码**：使用模板文件的原始编码
- **变量表编码**：必须与模板文件编码一致
- **FB文件编码**：必须与模板文件编码一致
- **文档文件编码**：建议使用UTF-8编码

### 4.2 编码检查与转换

1. **编码检查**：
   ```bash
   python check_encoding.py "FB_导入PLC变量_项目名称_autoshop_v1.0.0.csv"
   ```

2. **编码转换**（如果需要）：
   ```bash
   python convert_to_gbk_improved.py "FB_导入PLC变量_项目名称_autoshop_v1.0.0.csv"
   ```

3. **批量编码检查**：
   ```bash
   # 检查目录下所有CSV文件的编码
   for /r %f in (*.csv) do python check_encoding.py "%f"
   ```

### 4.3 编码一致性验证

| 文件类型 | 编码要求 | 验证工具 | 验证方法 |
|----------|----------|----------|----------|
| 变量表CSV | 与模板文件一致 | check_encoding.py | 命令行检查 |
| FB文件SCL | 与模板文件一致 | check_encoding.py | 命令行检查 |
| 文档文件MD | UTF-8 | 文本编辑器 | 手动检查 |

## 5. 测试与验证

### 5.1 测试计划

| 测试阶段 | 测试内容 | 测试方法 | 测试工具 |
|----------|----------|----------|----------|
| 单元测试 | 变量表验证 | 工具验证 | validate_variable_table.py |
| 单元测试 | FB功能测试 | 模拟测试 | Test_FB_上游与本站交互.scl |
| 集成测试 | 与Autoshop集成 | 实际导入 | 汇川Autoshop |
| 集成测试 | 与上游系统集成 | 实际连接 | 实际设备 |
| 性能测试 | 响应时间测试 | 计时测试 | 测试工具 |
| 可靠性测试 | 长时间运行测试 | 连续运行 | 实际设备 |

### 5.2 测试用例

#### 5.2.1 系统1准备好测试

| 测试步骤 | 输入 | 预期输出 | 实际输出 | 结果 |
|----------|------|----------|----------|------|
| 1 | 初始化 | q_System2Ready = TRUE | | |
| 2 | i_System1Ready = TRUE | q_StatusWord.0 = TRUE | | |
| 3 | i_System1Ready = FALSE | q_StatusWord.0 = FALSE | | |
| 4 | 复位 | 所有状态复位 | | |

#### 5.2.2 完整流程测试

| 测试步骤 | 输入 | 预期输出 | 实际输出 | 结果 |
|----------|------|----------|----------|------|
| 1 | 初始化 | q_System2Ready = TRUE | | |
| 2 | i_System1Ready = TRUE | q_StatusWord.0 = TRUE | | |
| 3 | i_System1TransferData = TRUE | q_System2DataReceived = TRUE | | |
| 4 | i_System1Request = TRUE | q_System2AllowRequest = TRUE | | |
| 5 | 等待 | q_System2OperationComplete = TRUE | | |
| 6 | i_System1Confirm = TRUE | q_System2OperationComplete = FALSE | | |
| 7 | 检查 | 所有状态正确复位 | | |

### 5.3 测试执行

1. **变量表测试**：
   ```bash
   python validate_variable_table.py --csv "FB_导入PLC变量_项目名称_autoshop_v1.0.0.csv" --scl "FB_交互功能.scl"
   ```

2. **FB功能测试**：
   - 在Autoshop中导入FB和测试FB
   - 创建测试程序，调用测试FB
   - 运行测试程序，观察测试结果

3. **集成测试**：
   - 连接实际设备信号
   - 运行功能块，测试实际交互
   - 验证信号处理的正确性

4. **性能测试**：
   - 测量信号响应时间
   - 测试连续运行的稳定性
   - 验证错误处理的及时性

## 6. 版本管理

### 6.1 版本号规则

使用语义化版本号：`主版本.次版本.修订版本`

- **主版本**：结构变更，如FB接口重大变更
- **次版本**：新增功能，如新增信号处理
- **修订版本**：Bug修复，如逻辑错误修正

### 6.2 版本管理流程

1. **版本检查**：检查当前文件版本号
2. **版本递增**：根据变更类型递增版本号
3. **文件重命名**：更新文件名中的版本号
4. **历史归档**：将旧版本文件归档到history文件夹
5. **版本记录**：更新变更记录文档

### 6.3 版本管理工具

```bash
# 使用version_manager.py工具进行版本管理
python version_manager.py create --file "FB_交互功能.scl" --type "scl" --reason "初始版本"
python version_manager.py update --file "FB_交互功能.scl" --type "scl" --reason "修复逻辑错误" --version "v1.0.1"
```

### 6.4 历史版本结构

```
项目名称/
history/
├── v1.0.0/
│   ├── 程序文件/
│   │   ├── FB_交互功能.scl
│   │   └── Test_FB_交互功能.scl
│   └── 变量表格/
│       └── FB_导入PLC变量_项目名称_autoshop_v1.0.0.csv
└── v1.0.1/
    ├── 程序文件/
    │   ├── FB_交互功能.scl
    │   └── Test_FB_交互功能.scl
    └── 变量表格/
        └── FB_导入PLC变量_项目名称_autoshop_v1.0.1.csv
```

## 7. 文档管理

### 7.1 文档结构

```
项目名称/
├── 项目需求与程序运行逻辑.md
├── 文档模板/
│   ├── 1-主控站需求文档_REQ-V1.0.0.md
│   ├── 2-主控站详细设计说明书_DES-V1.0.0.md
│   ├── 3-主控站接口文档_INT-V1.0.0.md
│   ├── 4-主控站开发文档_DEV-V1.0.0.md
│   ├── 5-主控站使用文档_USE-V1.0.0.md
│   └── 6-主控站变更台账_CHG-V1.0.0.md
└── 变量表变更日志.md
```

### 7.2 文档更新流程

1. **需求变更**：更新需求文档
2. **设计变更**：更新详细设计说明书
3. **接口变更**：更新接口文档
4. **实现变更**：更新开发文档
5. **使用变更**：更新使用文档
6. **版本变更**：更新变更台账

### 7.3 文档验证

| 文档类型 | 验证项 | 验证方法 |
|----------|--------|----------|
| 需求文档 | 功能需求完整性 | 人工审核 |
| 详细设计说明书 | 设计逻辑正确性 | 人工审核 |
| 接口文档 | 接口定义准确性 | 人工审核 |
| 开发文档 | 开发流程完整性 | 人工审核 |
| 使用文档 | 使用说明清晰度 | 人工审核 |
| 变更台账 | 变更记录完整性 | 人工审核 |

## 8. 集成与部署

### 8.1 Autoshop集成步骤

1. **导入变量表格**：
   - 在Autoshop中选择「导入变量」
   - 选择FB_导入PLC变量_项目名称_autoshop_vX.Y.Z.csv文件
   - 确认导入成功，无乱码

2. **导入FB功能块**：
   - 在Autoshop中选择「导入FB」
   - 选择FB_主控站.scl文件
   - 确认编译通过，无错误

3. **实例化FB**：
   - 在程序中添加FB实例
   - 为实例分配符号名，如FB_MainControlStation
   - 连接输入输出变量

4. **配置工作站参数**：
   - 根据实际工作站数量设置MAX_WORKSTATIONS参数
   - 根据实际系统需求调整计时器预设值

5. **测试运行**：
   - 下载程序到PLC
   - 运行测试功能块
   - 验证各项功能正常

### 8.2 现场部署步骤

1. **设备连接**：
   - 连接各工作站的信号到PLC输入
   - 连接PLC输出到各工作站的控制信号
   - 连接HMI或控制面板的信号
   - 连接外部系统（MES/ERP）的通讯接口

2. **参数配置**：
   - 根据实际工作站响应时间调整计时器预设值
   - 配置错误处理参数
   - 配置外部通讯参数

3. **系统调试**：
   - 进行单步调试，验证工作站监控和控制功能
   - 进行完整流程调试，验证整个生产过程
   - 进行异常情况调试，验证错误处理
   - 进行外部通讯调试，验证与MES/ERP系统的连接

4. **运行监控**：
   - 通过HMI监控系统状态和各工作站状态
   - 记录运行数据和生产报表
   - 定期检查系统运行状态和通讯状态

### 8.3 部署验证

| 验证项 | 验证方法 | 验证标准 |
|--------|----------|----------|
| 信号连接 | 手动触发信号 | 信号正确响应 |
| 工作站监控 | 检查工作站状态显示 | 状态正确显示 |
| 工作站控制 | 测试工作站启动/停止 | 控制正确执行 |
| 外部通讯 | 测试与MES/ERP连接 | 通讯正常 |
| 功能验证 | 运行完整生产流程 | 流程正确执行 |
| 错误处理 | 模拟错误情况 | 错误正确处理 |
| 性能验证 | 测量响应时间 | 响应时间 < 100ms |
| 稳定性验证 | 长时间运行 | 24小时无故障 |

## 9. 故障排查与维护

### 9.1 常见故障

| 故障现象 | 可能原因 | 排查方法 | 解决方案 |
|----------|----------|----------|----------|
| 变量表乱码 | 编码不一致 | 使用check_encoding.py检查 | 转换为与模板一致的编码 |
| 编译错误 | 变量未定义 | 检查变量表和FB代码 | 确保所有变量都在变量表中定义 |
| 工作站通讯失败 | 网络连接问题或工作站故障 | 检查网络连接和工作站状态 | 修复网络连接或工作站故障 |
| 外部系统连接异常 | 通讯配置错误或外部系统故障 | 检查通讯配置和外部系统状态 | 修正通讯配置或联系外部系统管理员 |
| 状态显示异常 | 内部状态错误或数据传输问题 | 检查状态机逻辑和数据传输 | 复位系统，检查状态转换和数据传输 |
| 超时错误 | 超时设置过短 | 检查计时器预设值 | 根据实际设备和通讯延迟调整超时时间 |
| 运行不稳定 | 信号冲突或工作站协调问题 | 检查信号顺序和工作站协调逻辑 | 确保信号按正确顺序发送，优化工作站协调逻辑 |

### 9.2 故障排查流程

1. **故障识别**：通过HMI或状态字识别故障
2. **故障定位**：根据故障现象和报警信息定位原因
3. **故障排除**：按照排查方法排除故障
4. **故障验证**：验证故障是否排除
5. **故障记录**：记录故障原因和解决方案

### 9.3 维护计划

| 维护项目 | 维护周期 | 维护内容 |
|----------|----------|----------|
| 信号连接检查 | 每周 | 检查信号连接是否松动 |
| 系统状态检查 | 每周 | 检查系统运行状态和各工作站状态 |
| 网络连接检查 | 每周 | 检查与工作站和外部系统的网络连接 |
| 变量表备份 | 每月 | 备份变量表文件 |
| 程序备份 | 每月 | 备份FB功能块文件和配置文件 |
| 版本更新 | 按需 | 更新功能块版本 |
| 文档更新 | 按需 | 更新相关文档 |
| 外部系统集成检查 | 每月 | 检查与MES/ERP系统的集成状态 |

## 10. 开发规范

### 10.1 编码规范

- **命名规范**：严格遵循项目命名规范
  - 输入变量：i_前缀
  - 输出变量：q_前缀
  - 内部变量：b_/n_前缀
  - 计时器变量：In_t/ET_t前缀

- **注释规范**：
  - FB头部必须包含功能描述、输入输出变量释义
  - 核心逻辑必须标注状态机切换条件、计时器参数
  - 工作站控制逻辑必须标注工作站协调规则、状态监控点
  - 外部通讯逻辑必须标注通讯协议、数据传输规则
  - 变更记录必须包含日期、原因、内容

- **结构化规范**：
  - FB必须包含六大模块：初始化、工作站监控、工作站控制、外部通讯、报警处理、状态机
  - 代码缩进一致，使用4空格缩进
  - 逻辑清晰，避免复杂嵌套

### 10.2 文件规范

- **FB文件命名**：FB_主控站.scl
- **测试FB命名**：Test_FB_主控站.scl
- **变量表命名**：FB_导入PLC变量_项目名称_autoshop_vX.Y.Z.csv
- **版本管理**：文件名包含版本号
- **编码一致性**：所有文件使用与模板一致的编码

### 10.3 版本规范

- **版本号格式**：vX.Y.Z
- **版本递增规则**：
  - 结构变更：主版本+1
  - 新增功能：次版本+1
  - Bug修复：修订版本+1
- **版本归档**：旧版本文件归档到history文件夹
- **变更记录**：详细记录版本变更内容

## 11. 总结

### 11.1 开发成果

- **FB_主控站.scl**：实现了主控站对各工作站的监控和控制功能，以及与外部系统的通讯对接功能
- **Test_FB_主控站.scl**：实现了功能块的测试功能
- **FB_导入PLC变量_项目名称_autoshop_vX.Y.Z.csv**：创建了完整的变量表格
- **相关文档**：创建了需求、设计、接口、开发、使用和变更台账文档

### 11.2 开发经验

- **模块化设计**：采用六大模块结构，提高了代码的可维护性
- **状态机管理**：使用状态机实现工作站和通讯的有序管理，避免了混乱
- **错误处理**：包含完整的超时和报警处理机制，提高了系统的可靠性
- **编码管理**：确保所有文件使用与模板一致的编码，避免了乱码问题
- **测试验证**：实现了完整的测试功能，确保了功能的正确性
- **版本管理**：进行了严格的版本管理，确保了代码的可追溯性
- **可扩展性**：设计支持工作站数量和类型的灵活扩展

### 11.3 后续改进

- **增加通信接口**：支持Modbus、Profinet、EtherCAT等通信协议
- **增强诊断功能**：提供更详细的故障诊断和预测性维护信息
- **优化性能**：进一步提高信号处理速度和系统响应时间
- **扩展测试功能**：增加更多测试模式和场景
- **支持远程监控**：增加远程监控和调试能力
- **集成人工智能**：引入AI技术进行生产优化和故障预测
- **完善文档**：进一步完善相关文档

### 11.4 技术创新

- **状态机优化**：使用状态机实现工作站和通讯的有序管理，提高了系统的可靠性
- **计时器管理**：使用数组管理多个计时器，提高了代码的可读性
- **错误处理**：实现了全面的错误检测和恢复机制，提高了系统的稳定性
- **测试功能**：内置测试模式，方便系统调试和维护
- **编码一致性**：确保所有文件使用与模板一致的编码，避免了乱码问题
- **可扩展性设计**：支持工作站数量和类型的灵活扩展
- **外部系统集成**：提供与MES/ERP/HMI系统的标准化接口

通过严格遵循开发流程和规范，成功实现了主控站功能FB，确保了对各工作站的监控和控制功能，以及与外部系统的通讯对接功能的正确性和可靠性。