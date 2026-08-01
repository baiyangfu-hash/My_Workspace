# 使用说明 GlobalVars.db

## 1. 功能

边框缓存机全局变量数据块，OB1 与各 FB 的数据交换中心。所有功能块通过 VAR_IN_OUT 结构体整块传递，无需逐引脚接线。

## 2. 结构体使用

| 结构体 | 传递给 | 传递方式 |
|--------|--------|----------|
| stConveyor | FB_1002 | VAR_IN_OUT io_stLayer |
| stPickPlace | FB_1003 | VAR_IN_OUT io_stZAxis, io_stX1Axis |
| stGlueFeeder | FB_1004 | VAR_IN_OUT io_stX2Axis |
| stAlarm | FB_2001 | VAR_INPUT |
| stExternal | FB_External | VAR_INPUT |

## 3. OB1 调度示例

```scl
// Step 1: 输送机
FB_1002(io_stLayer := "GlobalVars".stConveyor);

// Step 2: 取放料
FB_1003(io_stZAxis := "GlobalVars".stPickPlace.stZAxis,
        io_stX1Axis := "GlobalVars".stPickPlace.stX1Axis);

// Step 3: 打胶送料
FB_1004(io_stX2Axis := "GlobalVars".stGlueFeeder.stX2Axis);

// Step 4: 公共报警
FB_2001(stAlarm := "GlobalVars".stAlarm);

// Step 5: 外部设备
FB_External(stExternal := "GlobalVars".stExternal);
```

## 4. 调试要点

1. 修改结构体字段后需同步更新对应 FB 的 VAR_IN_OUT 接口定义
2. 结构体字段命名遵循 LSP-905 前缀规范（i_=输入, q_=输出, st=结构体）
3. 新增 FB 实例时在 GlobalVars.db 中声明对应的 STRUCT 类型
4. 报警码类型为 WORD（16#0000=无报警）