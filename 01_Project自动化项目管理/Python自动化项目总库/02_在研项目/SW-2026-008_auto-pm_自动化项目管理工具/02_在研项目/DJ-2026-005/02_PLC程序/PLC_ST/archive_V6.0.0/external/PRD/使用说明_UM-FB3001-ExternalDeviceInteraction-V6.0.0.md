# 使用说明 FB_3001_ExternalDeviceInteraction

## 1. 功能

外部设备交互管理。组框机/机器人信号中转 + 8路安全门检测 + 急停 + HMI STOP + 总线健康位。

## 2. 安全信号逻辑

- 急停X101常闭：OFF=按下激活→q_bEStopActive=TRUE→全部停止
- 8安全门X140~X147常闭：OFF=开门→q_bSafetyDoorFault[x]=TRUE
- q_bAnyDoorOpen = OR(q_bSafetyDoorFault[1..8]) → 全局互锁M200
- HMI STOP X77：独立检测，不等价于M3停止

## 3. 总线健康位

- q_bBusUnhealthy占位变量，后续按目标平台绑定(如Profinet诊断/驱动器报警/通讯心跳)
- 当前默认i_bBusHealthy=TRUE(健康)，断开则输出报警码120
