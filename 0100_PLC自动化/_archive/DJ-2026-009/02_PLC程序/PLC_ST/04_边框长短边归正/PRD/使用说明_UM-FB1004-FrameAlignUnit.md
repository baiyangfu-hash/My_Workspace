---
title: "使用说明 - FB_1004_FrameAlignUnit"
version: "V1.0.0"
spec_id: "UM"
project_id: "DJ-2026-009"
---

# 使用说明 - FB_1004_FrameAlignUnit

## 1. 调用方法 (SCL)

```scl
inst_FB_1004_FrameAlignUnit(
    i_bEnable       := GlobalVars.stControl.bMainPowerOn,
    i_bAutoMode     := GlobalVars.stControl.bAutoRunning,
    i_bResetCmd     := GlobalVars.stControl.bFaultReset,
    i_bEmergencyStop:= GlobalVars.stSafety.bEStopOk,
    q_bRunning      => GlobalVars.stStation.FrameAlignUnit.bRunning,
    q_bDone         => GlobalVars.stStation.FrameAlignUnit.bDone,
    q_bError        => GlobalVars.stStation.FrameAlignUnit.bError,
    q_wErrorCode    => GlobalVars.stStation.FrameAlignUnit.wErrorCode
);
```
