# 使用说明 FB_1002_SingleLayerConveyor_BufferFraming

## 1. 功能

单层边框缓存机输送机控制。9 步 Step_S 状态机实现"先输送后分料"工艺流，通过 VAR_IN_OUT io_stLayer 结构体整块传递，内部分配调用 FB_1011 气缸控制和 FB_1012 电机控制。

## 2. 状态机 (Step_S)

| 步号 | 名称 | 动作 |
|------|------|------|
| 0 | STEP_INIT | 反转初始化：所有输出复位，安全门互锁检测 |
| 1 | STEP_WAIT_FRAME | 等待边框到位（传感器冗余一致性检查） |
| 2 | STEP_CONVEYOR_FWD | 输送电机正转，边框前进 |
| 3 | STEP_BLOCK_POSITION | 挡料气缸上升，定位边框 |
| 4 | STEP_SEPARATE | 分料气缸推出，分离单层边框 |
| 5 | STEP_CONVEYOR_SLOW | 输送电机慢速，精确定位 |
| 6 | STEP_FEED_COMPLETE | 送料完成信号 |
| 7 | STEP_RETURN | 所有气缸复位，电机停止 |
| 8 | STEP_FAULT | 故障处理：超时报警 100~103, 130~163 |

## 3. 调试要点

1. STEP_INIT 中安全门互锁检测：任一安全门开→不启动
2. 传感器冗余一致性检查：挡料上/下传感器、分料上/下传感器两两互检
3. 分料超时报警 100~103：分别对应挡料升/降超时、分料推/退超时
4. 输送机故障报警 130~163：电机过载/变频器故障/传感器异常
5. 消抖参数 i_dDebounceMs 控制传感器信号滤波时间