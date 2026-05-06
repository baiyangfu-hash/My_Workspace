# 单机测试 PLC变量定义文档

## 文档信息
| 项目 | 内容 |
|------|------|
| 项目编号 | DJ-2026-001 |
| 版本 | V1.0.0 |
| 编制日期 | 2026-04-27 |
| 编程规范 | IEC 61131-3 |
| 架构模型 | Device-Logic-Main 三层架构 |

---

## 1. 变量命名规范

### 1.1 前缀规则

| 前缀 | 含义 | 适用范围 | 示例 |
|:----:|------|----------|------|
| `i_` | 输入变量 | VAR_INPUT | i_bEnable, i_rPosition |
| `o_` | 输出变量 | VAR_OUTPUT | o_bDone, o_rActualPos |
| `s_` | 静态变量(状态) | VAR(内部) | s_eState, s_nStep |
| `fb` | 功能块实例 | VAR | fbServoAxis, fbSafety |
| `tmr` | 计时器实例 | VAR | tmrDelay, tmrTimeout |

### 1.2 类型标识符

| 标识符 | 数据类型 | 示例 |
|:------:|----------|------|
| `b` | BOOL | bEnable, bFault |
| `n/i` | INT/DINT | nCount, iIndex |
| `r` | REAL | rSpeed, rPosition |
| `e` | INT(枚举) | eState, eMode |
| `t` | TIME/TON/TOF | tDelay, tmrTimeout |

### 1.3 命名格式
```
[作用域]_[功能]_[含义]
示例:
- i_bHomeReturnRequest  (输入_布尔_回原点请求)
- o_bAxisRunning       (输出_布尔_轴运行中)
- s_eSystemState       (静态_枚举_系统状态)
- o_rCurrentPosition   (输出_实数_当前位置)
```

## 2. IO地址分配原则

### 2.1 CPU本体IO分配
| 地址范围 | 用途 | 说明 |
|----------|------|------|
| X0-X7 | 安全+关键传感器 | 原点、限位、急停(X16)、复位(X17) |
| X10-X17 | 伺服报警+安全门 | 每轴故障、门锁信号 |
| Y0-Y7 | 状态指示灯+关键输出 | 运行灯(Y0)、故障灯(Y1) |
| Y10-Y17 | 伺服使能+方向 | 脉冲/方向输出 |

### 2.2 扩展模块分配
| 模块 | 地址范围 | 用途 |
|------|----------|------|
| DI1 | X10-X17 | 扩展输入1(传感器组) |
| DI2-DI4 | X0-X17 | 工艺传感器(分料/到位/放料完成) |
| DO1-DO2 | Y0-Y15 | 电磁阀/中间继电器 |
| 远程站 | X0-XF, Y10-Y15 | 分布式IO(取料机构等) |

## 3. 数据块(DB)规划

| DB编号 | 名称 | 类型 | 用途 |
|:------:|------|------|------|
| DB1 | System_Param | 全局DB | 系统参数(速度/位置/延时) |
| DB2 | Recipe_Data | 全局DB | 配方数据(可选) |
| DB3 | Production_Data | 全局DB | 生产统计(计数/时间) |
| DB10+ | FB_Instance_DB | 实例DB | 各FB的背景数据块 |

## 4. 功能块组织结构

### Device层 (02_PLC程序/通用ST程序及变量表/Device/)
| 文件 | 功能块 | 职责 |
|------|--------|------|
| FB_Device_IOMapping_V1.0.0.st | FB_Device_IOMapping | 物理IO→符号变量映射 |
| FB_Device_Layer_V1.0.0.st | FB_Device_ServoAxis | 单轴控制(4态状态机) |
| ^ | FB_Device_Conveyor | 输送线控制(3态) |
| ^ | FB_Device_Cylinder | 气缸控制(6态+超时) |
| ^ | FB_Device_Safety | 安全系统(急停/门锁) |

### Logic层 (02_PLC程序/通用ST程序及变量表/Logic/)
| 文件 | 功能块 | 职责 |
|------|--------|------|
| FB_Logic_Layer_V1.0.0.st | FB_Logic_ServoControl | 伺服逻辑封装 |
| ^ | FB_Logic_ConveyorControl | 输送线逻辑封装 |
| ^ | FB_Logic_SequenceStep | N步顺序步进 |

### Main层 (02_PLC程序/通用ST程序及变量表/Main/)
| 文件 | 功能块 | 职责 |
|------|--------|------|
| FB_Main_Control_V1.0.0.st | FB_Main_SystemControl | 7态系统状态机 |
| ^ | FB_Main_SafetyManager | 安全协调管理 |
| ^ | FB_Main_AlarmManager | 报警代码+蜂鸣器 |
| FB_Main_Initialization_V1.0.0.st | FB_Main_Initialization | 5步初始化序列 |
| MainProgram_V1.0.0.st | MainProgram | OB1主程序(集成调用) |

---

## 修订记录
| 版本 | 日期 | 修订人 | 修订内容 |
|:----:|:----:|--------|----------|
| V1.0.0 | 2026-04-27 | | 初版(基于TPL-SINGLE-PLC-001 V2.0.0模板生成) |