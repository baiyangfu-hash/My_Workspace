---
title: "接口文档 - FB_1002_StackTransferRobot_XZ"
version: "V1.0.0"
spec_id: "IFC"
project_id: "DJ-2026-009"
---

# 接口文档 - FB_1002_StackTransferRobot_XZ

## 1. 模块职责简述
叠垛移载机械手 X 轴水平与 Z 轴垂直伺服定位取放料。

## 2. 接口引脚定义表

| 引脚名称 | 属性 | 数据类型 | 初始值 | 工程意义与信号描述 |
| :--- | :--- | :--- | :--- | :--- |
| `i_bEnable` | VAR_INPUT | BOOL | FALSE | 功能块总使能信号 |
| `i_bAutoMode` | VAR_INPUT | BOOL | FALSE | 自动运行模式标志 |
| `i_bResetCmd` | VAR_INPUT | BOOL | FALSE | 故障复位指令 |
| `i_bEmergencyStop` | VAR_INPUT | BOOL | FALSE | 安全急停联锁 (常闭触点) |
| `q_bRunning` | VAR_OUTPUT | BOOL | FALSE | 机构工位动作运行中 |
| `q_bDone` | VAR_OUTPUT | BOOL | FALSE | 当前循环工步完成 |
| `q_bError` | VAR_OUTPUT | BOOL | FALSE | 工位报警/超时故障 |
| `q_wErrorCode` | VAR_OUTPUT | WORD | 16#0000 | 报警诊断代码 |
