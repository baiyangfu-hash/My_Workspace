# FB\_1014\_StationConveyor V4.3.0 修复方案

## 问题诊断

当前 V4.2.0 设计存在以下缺陷：

| 编号 | 问题                                      | 影响                        |
| -- | --------------------------------------- | ------------------------- |
| P1 | A侧缺少**拍正气缸**（对齐气缸），阻挡气缸实际是装在拍正气缸之上的物理结构 | 进料后物料无法拍正对齐，加工精度无法保证      |
| P2 | 状态机缺少**对齐步骤**，INFEED 完成后直接进入 PROCESSING | 缺少"拍正→A侧气缸下降→拍正气缸收回"的完整时序 |
| P3 | 所有气缸缺少**磁环到位信号**反馈                      | 无法确认气缸实际位置，程序是"盲操"        |
| P4 | 停止/手动模式下缺少拍正气缸的处理                       | 安全状态不完整                   |

## 物理布局理解

```
A侧（入料/出料侧）:
  ┌─────────────────┐
  │  阻挡气缸        │  ← 装在拍正气缸上，可独立升降
  │  q_yInfeedCyl    │
  ├─────────────────┤
  │  拍正气缸        │  ← 底座，默认状态：伸出
  │  q_yAlignCyl     │
  └─────────────────┘

B侧（出料/入料侧）:
  │  出料气缸        │
  │  q_yDischargeCyl │
```

## 修复范围

需要修改 **5 个文件**（4 份文档 + 1 份源码）：

| 文件  | 路径                                                 | 类型        |
| --- | -------------------------------------------------- | --------- |
| IFC | `PRD/接口文档_IFC-FB1014-StationConveyor-V4.3.0.md`    | 新建 V4.3.0 |
| PRD | `PRD/需求文档_PRD-FB1014-StationConveyor-V4.3.0.md`    | 新建 V4.3.0 |
| PFL | `PRD/工艺流程_PFL-FB1014-StationConveyor-V4.3.0.md`    | 新建 V4.3.0 |
| DSN | `PRD/详细设计说明书_DSN-FB1014-StationConveyor-V4.3.0.md` | 新建 V4.3.0 |
| SCL | `FB_1014_StationConveyor.scl`                      | 直接修改      |

***

## 一、状态机变更（Breaking Change）

### 新增 ST\_ALIGN 状态

在 INFEED(2) 和 PROCESSING(3) 之间插入 ALIGN 状态，状态号整体后移：

| 状态值   | 常量名            | V4.2.0→V4.3.0 |
| ----- | -------------- | ------------- |
| 0     | ST\_IDLE       | 不变            |
| 1     | ST\_READY      | 不变            |
| 2     | ST\_INFEED     | 不变            |
| **3** | **ST\_ALIGN**  | **新增**        |
| 4     | ST\_PROCESSING | 原 3           |
| 5     | ST\_DISCHARGE  | 原 4           |
| 6     | ST\_COMPLETE   | 原 5           |
| 7     | ST\_PAUSE      | 原 6           |
| 8     | ST\_FAULT      | 原 7           |

### 对齐态（ST\_ALIGN）执行流程

```
进入 ALIGN:
  1. 马达停止（q_yRevCmd=FALSE, q_ySlowCmd=FALSE）
  2. 拍正气缸保持伸出（q_yAlignCylinder=FALSE，默认就已伸出）
  3. q_yDischargeCylinder=TRUE（B侧入料气缸保持放下）
  4. 启动对齐延时定时器 tAlignDelay
  5. 等待对齐确认（磁环 i_xAlignExtended=TRUE AND tAlignDelay.Q）

对齐确认后:
  6. A侧阻挡气缸下降 → q_yInfeedCylinder := TRUE
  7. 等待下降到位 → i_xInfeedCylLowered=TRUE
  8. 拍正气缸收回 → q_yAlignCylinder := TRUE
  9. 等待收回到位 → i_xAlignRetracted=TRUE
  10. → ST_PROCESSING
```

**关键设计要点**：

* 拍正气缸默认伸出（弹簧复位型），FALSE=伸出，TRUE=收回

* 对齐动作是"利用已伸出的拍正气缸将物料推到位"的确认过程

* 对齐完成后：先降阻挡气缸，再收拍正气缸（保证物料不会移位）

***

## 二、接口变更

### 新增 VAR\_INPUT（4个信号）

| 名称                       | 类型   | 默认值   | 说明             |
| ------------------------ | ---- | ----- | -------------- |
| i\_xAlignExtended        | BOOL | FALSE | 拍正气缸伸出到位（磁环）   |
| i\_xAlignRetracted       | BOOL | FALSE | 拍正气缸收回到位（磁环）   |
| i\_xInfeedCylLowered     | BOOL | FALSE | A侧阻挡气缸下降到位（磁环） |
| i\_xDischargeCylExtended | BOOL | FALSE | B侧气缸伸出到位（磁环）   |

### 新增 VAR\_INPUT（1个参数）

| 名称               | 类型   | 默认值 | 说明         |
| ---------------- | ---- | --- | ---------- |
| i\_dAlignDelayMs | DINT | 500 | 拍正对齐延时(ms) |

### 新增 VAR\_OUTPUT（1个输出）

| 名称                | 类型   | 默认值   | 说明                         |
| ----------------- | ---- | ----- | -------------------------- |
| q\_yAlignCylinder | BOOL | FALSE | 拍正气缸（FALSE=伸出/默认, TRUE=收回） |

### 接口统计变更

| 项目                 | V4.2.0 | V4.3.0 |   变化   |
| ------------------ | :----: | :----: | :----: |
| VAR\_INPUT (控制+参数) | 9+2=11 | 9+3=12 |   +1   |
| VAR\_INPUT (传感器)   |    4   |    8   |   +4   |
| VAR\_OUTPUT (驱动)   |    7   |    8   |   +1   |
| VAR\_OUTPUT (诊断)   |    4   |    4   |    0   |
| **总计**             | **26** | **32** | **+6** |

***

## 三、各文档修改清单

### 3.1 IFC（接口文档）

| 章节                   | 修改内容                                         |
| -------------------- | -------------------------------------------- |
| 0. 版本号               | V4.2.0 → V4.3.0                              |
| 0. 变更摘要              | 新增 V4.3.0 变更说明（新增拍正气缸 + 磁环信号 + ST\_ALIGN 状态） |
| 2.1 主状态机             | 状态值从 0-7 变为 0-8，新增 ST\_ALIGN=3               |
| 3.1 VAR\_INPUT 控制信号  | 新增 i\_dAlignDelayMs                          |
| 3.2 VAR\_INPUT 传感器信号 | 新增 4 个磁环信号                                   |
| 3.3 VAR\_OUTPUT 驱动输出 | 新增 q\_yAlignCylinder，更新 q\_iState 范围说明 (0-8) |
| 4. 功能切换表             | 新增 ALIGN 态气缸/传感器功能说明                         |
| 5. 接口统计              | 更新统计数字                                       |

### 3.2 PRD（需求文档）

| 章节             | 修改内容                                              |
| -------------- | ------------------------------------------------- |
| 0. 版本号         | V4.2.0 → V4.3.0                                   |
| 0. V4.3.0 变更摘要 | 新增（拍正气缸、磁环信号、ST\_ALIGN）                           |
| 2. FR-03       | 更新：8态→9态，新增 ST\_ALIGN 步骤                          |
| 2. 新增 FR-17    | **拍正对齐功能**：INFEED→ALIGN→对齐确认→气缸下降→拍正收回→PROCESSING |
| 2. 新增 FR-18    | **气缸磁环到位信号**：3组气缸各配磁环反馈，确认到位后才切换                  |
| 2. 更新 FR-08    | 入料/出料延时之上追加对齐延时                                   |
| 2. 更新 FR-09    | 停止/暂停动作中增加 q\_yAlignCylinder 处理                   |
| 2. 更新 FR-12    | 手动模式增加 q\_yAlignCylinder 清零                       |
| 4. 接口需求汇总      | 更新 I/O 信号数量                                       |
| 6. 需求追溯矩阵      | 新增 FR-17/FR-18 映射                                 |

### 3.3 PFL（工艺流程）

| 章节                | 修改内容                                          |
| ----------------- | --------------------------------------------- |
| 0. 版本号            | V4.2.0 → V4.3.0                               |
| 1.2 工艺特征          | 新增"拍正对齐"特征、"磁环到位确认"                           |
| 1.3 物料流向图         | 更新图示，标注拍正气缸位置                                 |
| 2.1 完整工艺时序        | 在 S2(INFEED) 与 S3(PROCESSING) 之间插入 S3a(ALIGN) |
| 2.2 新增 S3a: ALIGN | 详细描述对齐步骤、气缸动作、磁环确认条件                          |
| 3. 功能切换表          | 新增 ALIGN 态功能映射                                |
| 4.1/4.2           | 停止/暂停流程增加 q\_yAlignCylinder 处理                |
| 5. 优先级决策链         | 无变化（对齐在安全链之后执行）                               |
| 6. 状态转换图          | 新增 ST\_ALIGN 节点，更新转换箭头                        |
| 7. 关键时序参数         | 新增 i\_dAlignDelayMs                           |
| 7. 新增对齐时序         | 对齐阶段时序波形图                                     |
| 8. 气缸动作工艺表        | 新增 q\_yAlignCylinder 列，新增 ALIGN 行             |

### 3.4 DSN（详细设计说明书）

| 章节             | 修改内容                                                                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| 0. 版本号         | V4.2.0 → V4.3.0                                                                                                                      |
| 0. V4.3.0 变更摘要 | 新增                                                                                                                                   |
| 1. 设计原则        | 新增第6条"拍正对齐"原则                                                                                                                        |
| 2.3 新增对齐时映射    | ALIGN 态功能切换映射                                                                                                                        |
| 3.1 状态定义表      | 新增 ST\_ALIGN(3) 行，PROCESSING 值从 3→4，后续顺延                                                                                             |
| 4.1 停止/暂停伪代码   | 增加 q\_yAlignCylinder 清零                                                                                                              |
| 4.2 状态机伪代码     | INFEED 出口改为 ST\_ALIGN；新增 ST\_ALIGN CASE 分支；PROCESSING/DISCHARGE/COMPLETE 状态值调整                                                       |
| 5. 时序图         | 插入对齐阶段                                                                                                                               |
| 6. 边界条件        | 新增对齐超时、磁环信号丢失等场景                                                                                                                     |
| 7.1\~7.4 变量定义  | 新增 i\_xAlignExtended/i\_xAlignRetracted/i\_xInfeedCylLowered/i\_xDischargeCylExtended/i\_dAlignDelayMs/q\_yAlignCylinder/tAlignDelay |
| 8. V4.3.0 差异说明 | 新增章节，对比 V4.2.0                                                                                                                       |

### 3.5 SCL（源代码）

| 位置              | 修改内容                                                                                                       |
| --------------- | ---------------------------------------------------------------------------------------------------------- |
| 文件头注释           | 版本 → V4.3.0，新增变更说明                                                                                         |
| VAR\_INPUT      | 新增 i\_dAlignDelayMs, i\_xAlignExtended, i\_xAlignRetracted, i\_xInfeedCylLowered, i\_xDischargeCylExtended |
| VAR\_OUTPUT     | 新增 q\_yAlignCylinder                                                                                       |
| VAR             | 新增 tAlignDelay : FB\_TON                                                                                   |
| VAR CONSTANT    | 新增 ST\_ALIGN : INT := 3，PROCESSING→4，DISCHARGE→5，COMPLETE→6，PAUSE→7，FAULT→8                                |
| 停止处理块           | 增加 q\_yAlignCylinder := FALSE                                                                              |
| 手动模式块           | 增加 q\_yAlignCylinder := FALSE                                                                              |
| ST\_INFEED 出口   | `iState := ST_PROCESSING` → `iState := ST_ALIGN`                                                           |
| 新增 ST\_ALIGN 分支 | 完整 CASE 分支逻辑                                                                                               |
| ST\_PROCESSING  | 状态常量引用更新                                                                                                   |
| ST\_DISCHARGE   | 状态常量引用更新                                                                                                   |
| ST\_COMPLETE    | 状态常量引用更新                                                                                                   |
| ST\_PAUSE       | 状态常量引用更新                                                                                                   |
| ST\_FAULT       | 状态常量引用更新 + 增加 q\_yAlignCylinder 清零                                                                         |

***

## 四、ST\_ALIGN 伪代码

```pascal
ST_ALIGN:
    // 马达停止
    q_yRevCmd := FALSE;
    q_ySlowCmd := FALSE;
    
    // 拍正气缸保持伸出（默认状态就是 FALSE=伸出）
    q_yAlignCylinder := FALSE;
    
    // B侧入料气缸保持放下
    q_yDischargeCylinder := TRUE;
    
    // A侧阻挡气缸保持抬起（与INFEED一致）
    q_yInfeedCylinder := FALSE;
    
    q_bInfeedActive := TRUE;
    
    // 对齐延时
    tAlignDelay(IN := TRUE, PT := DINT_TO_TIME(i_dAlignDelayMs));
    
    // 拍正确认：拍正气缸伸出到位磁环 + 延时到
    IF i_xAlignExtended AND tAlignDelay.Q THEN
        // 拍正结束，A侧阻挡气缸下降
        q_yInfeedCylinder := TRUE;
        
        // 等待阻挡气缸下降到位
        IF i_xInfeedCylLowered THEN
            // 拍正气缸收回
            q_yAlignCylinder := TRUE;
            
            // 等待拍正气缸收回到位
            IF i_xAlignRetracted THEN
                iState := ST_PROCESSING;
                q_yDischargeCylinder := FALSE;
                q_bInfeedActive := FALSE;
                tAlignDelay(IN := FALSE);
            END_IF;
        END_IF;
    END_IF;
```

**设计说明**：

* 拍正气缸默认 FALSE=伸出（弹簧复位单作用气缸），TRUE=主动收回

* 对齐步骤分三段确认：①拍正延时确认 → ②阻挡气缸下降到位 → ③拍正气缸收回到位

* 三段均依赖磁环信号，确保机械到位后才切换状态

***

## 五、影响评估

| 维度   | 影响                                                         |
| ---- | ---------------------------------------------------------- |
| 向下兼容 | **Breaking Change**：状态号 3\~7 变为 4\~8，外部依赖 q\_iState 的逻辑需更新 |
| 接口兼容 | **Breaking Change**：新增 6 个接口信号，旧调用方无法直接使用                  |
| 硬件影响 | 需增加：1 个拍正气缸执行器 + 4 个磁环传感器 + 对应 IO 点                        |
| 文档兼容 | 关联文档（IFC/PRD/PFL/DSN）全部升级至 V4.3.0                          |

***

## 六、实施顺序

1. **IFC**（接口文档）：先定义接口变更，作为后续文档的基础
2. **PRD**（需求文档）：以 IFC 为依据，编写功能需求
3. **PFL**（工艺流程）：以 PRD 为依据，编写详细工艺流程
4. **DSN**（详细设计）：以 PFL 为依据，编写伪代码和时序
5. **SCL**（源代码）：以 DSN 为依据，实现 SCL 程序

