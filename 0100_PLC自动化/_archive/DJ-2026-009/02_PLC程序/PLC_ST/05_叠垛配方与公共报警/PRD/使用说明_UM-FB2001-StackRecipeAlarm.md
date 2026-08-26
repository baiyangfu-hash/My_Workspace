---
title: "使用说明 - FB_2001_StackRecipeAlarm"
version: "V1.0.0"
spec_id: "UM"
project_id: "DJ-2026-009"
---

# 使用说明 - FB_2001_StackRecipeAlarm

## 1. 调用方法 (SCL)

```scl
inst_FB_2001_StackRecipeAlarm(
    i_bEnable       := GlobalVars.stControl.bMainPowerOn,
    i_bAutoMode     := GlobalVars.stControl.bAutoRunning,
    i_bResetCmd     := GlobalVars.stControl.bFaultReset,
    i_bEmergencyStop:= GlobalVars.stSafety.bEStopOk,
    q_bRunning      => GlobalVars.stStation.StackRecipeAlarm.bRunning,
    q_bDone         => GlobalVars.stStation.StackRecipeAlarm.bDone,
    q_bError        => GlobalVars.stStation.StackRecipeAlarm.bError,
    q_wErrorCode    => GlobalVars.stStation.StackRecipeAlarm.wErrorCode
);
```
