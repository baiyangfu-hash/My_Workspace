---
title: "使用说明 - FB_1002_StackTransferRobot_XZ"
version: "V1.0.0"
spec_id: "UM"
project_id: "DJ-2026-009"
---

# 使用说明 - FB_1002_StackTransferRobot_XZ

## 1. 调用方法 (SCL)

```scl
inst_FB_1002_StackTransferRobot_XZ(
    i_bEnable       := GlobalVars.stControl.bMainPowerOn,
    i_bAutoMode     := GlobalVars.stControl.bAutoRunning,
    i_bResetCmd     := GlobalVars.stControl.bFaultReset,
    i_bEmergencyStop:= GlobalVars.stSafety.bEStopOk,
    q_bRunning      => GlobalVars.stStation.StackTransferRobot_XZ.bRunning,
    q_bDone         => GlobalVars.stStation.StackTransferRobot_XZ.bDone,
    q_bError        => GlobalVars.stStation.StackTransferRobot_XZ.bError,
    q_wErrorCode    => GlobalVars.stStation.StackTransferRobot_XZ.wErrorCode
);
```
