---
title: "使用说明 - FB_1001_DualInfeedConveyor"
version: "V1.0.0"
spec_id: "UM"
project_id: "DJ-2026-009"
---

# 使用说明 - FB_1001_DualInfeedConveyor

## 1. 调用方法 (SCL)

```scl
inst_FB_1001_DualInfeedConveyor(
    i_bEnable       := GlobalVars.stControl.bMainPowerOn,
    i_bAutoMode     := GlobalVars.stControl.bAutoRunning,
    i_bResetCmd     := GlobalVars.stControl.bFaultReset,
    i_bEmergencyStop:= GlobalVars.stSafety.bEStopOk,
    q_bRunning      => GlobalVars.stStation.DualInfeedConveyor.bRunning,
    q_bDone         => GlobalVars.stStation.DualInfeedConveyor.bDone,
    q_bError        => GlobalVars.stStation.DualInfeedConveyor.bError,
    q_wErrorCode    => GlobalVars.stStation.DualInfeedConveyor.wErrorCode
);
```
