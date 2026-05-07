# Tasks

## Task 1: 创建 FB_四层输送机 纯逻辑功能块及FBD使用说明
- **Priority**: P0
- **Depends On**: None
- **Status**: ✅ COMPLETED
- **Description**:
  - 设计并实现四层输送机工站功能块（FB_四层输送机）— **纯逻辑块，不碰任何X/Y/M/D地址**
  - 所有输入来自主控（传感器信号已映射、HMI控制、参数、上游信号）
  - 所有输出给主控（执行器请求、状态、报警）— 由主控判断后驱动Y或回写M/D
  - 包含：4层独立分料状态机(自动)、单层手动操作、初始化流程、块内报警
  - 输入接口分区：使能与模式(BOOL)、控制按钮(BOOL)、手动操作(BOOL)、参数设置(REAL/INT)、传感器输入(BOOL数组)、上游信号(BOOL)
  - 输出接口分区：执行器请求(BOOL数组)、下游信号(BOOL)、状态输出(BOOL/INT/REAL)、报警输出(INT)
  - 文件夹名：`四层输送机/`
- **Deliverables**:
  - [x] `02_PLC程序/通用ST程序及变量表/四层输送机/FB_四层输送机_V4.0.0.st`
  - [x] `02_PLC程序/通用ST程序及变量表/四层输送机/FBD使用说明.md`

## Task 2: 创建 FB_取放料机构 纯逻辑功能块及FBD使用说明
- **Priority**: P0
- **Depends On**: Task 1
- **Status**: ✅ COMPLETED
- **Description**:
  - 设计并实现取放料机构工站功能块（FB_取放料机构）— **纯逻辑块**
  - 管理升降气缸、前/后夹紧气缸、Z/X1/X2伺服轴的逻辑控制
  - 自动模式：取放料状态机，一次取两根，4层循环取2次
  - 接收来自主控的：传感器信号(已映射)、HMI控制、参数(REAL速度/INT时间)、来自输送机的4层放料完成信号
  - 输出给主控的：执行器请求(气缸/伺服)、状态(当前位置REAL/当前层数INT)、报警代码(INT)、给送料机构的放料完成信号
  - 文件夹名：`取放料机构/`
- **Deliverables**:
  - [x] `02_PLC程序/通用ST程序及变量表/取放料机构/FB_取放料机构_V4.0.0.st`
  - [x] `02_PLC程序/通用ST程序及变量表/取放料机构/FBD使用说明.md`

## Task 3: 创建 FB_打胶机送料机构 纯逻辑功能块及FBD使用说明
- **Priority**: P0
- **Depends On**: Task 2
- **Status**: ✅ COMPLETED
- **Description**:
  - 设计并实现打胶机送料机构工站功能块（FB_打胶机送料机构）— **纯逻辑块**
  - 管理X2轴伺服运动 + 打胶机交互协议的逻辑
  - 接收来自主控的：X2轴传感器(已映射)、打胶机信号(X76/X102经映射)、来自取放料的放料完成信号、HMI控制和参数(REAL位置设定)
  - 输出给主控的：允许抓料请求→Y44、安全区信号→Y47、状态和报警
  - 文件夹名：`打胶机送料机构/`
- **Deliverables**:
  - [x] `02_PLC程序/通用ST程序及变量表/打胶机送料机构/FB_打胶机送料机构_V4.0.0.st`
  - [x] `02_PLC程序/通用ST程序及变量表/打胶机送料机构/FBD使用说明.md`

## Task 4: 创建 FB_公共报警 功能块及报警码定义
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3
- **Status**: ✅ COMPLETED
- **Description**:
  - 设计并实现公共报警汇总功能块（FB_公共报警）— **纯逻辑块**
  - 接收3个工站的报警代码输入（INT类型，来自主控转发）
  - 汇总输出到D区规划（全局报警字WORD、当前报警码INT、任何报警激活BOOL）
  - 预留MES通讯扩展（报警队列数组D106~D125、新报警脉冲标志、报警计数）
  - 定义完整报警码体系（输送机1~99、取放料101~199、送料201~299）
  - 文件夹名：`公共服务/`
- **Deliverables**:
  - [x] `02_PLC程序/通用ST程序及变量表/公共服务/FB_公共报警_V4.0.0.st`
  - [x] `02_PLC程序/通用ST程序及变量表/公共服务/报警码定义.md`

## Task 5: 创建 主控程序（IO映射+协调中心）
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3, Task 4
- **Status**: ✅ COMPLETED
- **Description**:
  - 编写主控程序 — **核心组件，承担所有IO映射和协调工作**
  - 职责：
    1. IO映射：X地址→逻辑输入变量（传给各工站）、逻辑输出变量→Y地址（接收自各工站）
    2. HMI数据读取：M/D区→分发给工站（BOOL模式/按钮、REAL速度、INT参数）
    3. 外部信号处理：打胶机X76/X102→传给送料工站
    4. 工站实例化+工站间布尔/INT信号连接
    5. 工站输出汇总→驱动Y地址+回写M/D区给HMI显示
    6. 报警汇总→D区（调用FB_公共报警）
  - 不做任何业务逻辑（自动/手动/初始化/状态机全部在工站内部）
  - 文件夹名：`主控/`
- **Deliverables**:
  - [x] `02_PLC程序/通用ST程序及变量表/主控/主控程序_V4.0.0.st`

## Task 6: 更新 PLC变量定义文档 和 程序设计总文档
- **Priority**: P1
- **Depends On**: Task 1~5 全部完成
- **Status**: ✅ COMPLETED
- **Description**:
  - 更新PLC变量定义文档至V4.0.0（反映新架构的IO分配表、D区规划、M区HMI交互、报警区域）
  - 更新PLC程序设计总文档至V4.0.0（反映新目录结构、功能块列表、主控IO映射关系、工站间连接关系）
- **Deliverables**:
  - [x] `02_PLC程序/通用ST程序及变量表/PLC变量定义文档_VAR-DJ-2026-005-V4.0.0.md`
  - [x] `02_PLC程序/程序文档/016_DJ-2026-005_PLC程序设计总文档_PLC-V4.0.0.md`

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 1], [Task 2], [Task 3]
- [Task 5] depends on [Task 1], [Task 2], [Task 3], [Task 4]
- [Task 6] depends on [Task 1] through [Task 5]
