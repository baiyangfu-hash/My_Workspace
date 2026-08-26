---
title: "使用说明 - FB_1003_PaperHolder_Z"
version: "V1.0.0"
spec_id: "UM"
project_id: "DJ-2026-009"
---

# 使用说明 - FB_1003_PaperHolder_Z

## 1. 调用方法 (SCL)

```scl
inst_FB_1003_PaperHolder_Z(
    i_bEnable       := GlobalVars.stControl.bMainPowerOn,
    i_bAutoMode     := GlobalVars.stControl.bAutoRunning,
    i_bResetCmd     := GlobalVars.stControl.bFaultReset,
    i_bEmergencyStop:= GlobalVars.stSafety.bEStopOk,
    q_bRunning      => GlobalVars.stStation.PaperHolder_Z.bRunning,
    q_bDone         => GlobalVars.stStation.PaperHolder_Z.bDone,
    q_bError        => GlobalVars.stStation.PaperHolder_Z.bError,
    q_wErrorCode    => GlobalVars.stStation.PaperHolder_Z.wErrorCode
);
```
