---
title: "接口文档 - FB_1001_DualInfeedConveyor"
version: "V1.0.0"
spec_id: "IFC"
project_id: "DJ-2026-009"
---

# 接口文档 - FB_1001_DualInfeedConveyor

## 1. 模块职责简述
双路边框型材进料输送、光电计数与暂存控制。

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
