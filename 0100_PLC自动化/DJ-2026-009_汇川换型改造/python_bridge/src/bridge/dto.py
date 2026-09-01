from pydantic import BaseModel, ConfigDict


class ST_Station1_Control(BaseModel):
    bAutoEnable: bool = False
    bManualStart: bool = False
    bReset: bool = False
    bPause: bool = False
    bSingleStepMode: bool = False

    model_config = ConfigDict(frozen=True)

class ST_Sensors(BaseModel):
    bCylinderUp: bool = False
    bCylinderDown: bool = False
    bMaterialPresent: bool = False
    model_config = ConfigDict(frozen=True)

class ST_Actuators(BaseModel):
    bCylinderLift: bool = False
    bCylinderPush: bool = False
    model_config = ConfigDict(frozen=True)

class ST_Station1_Status(BaseModel):
    iStep: int = 0
    bRunning: bool = False
    bDone: bool = False
    bAlarm: bool = False
    iAlarmCode: int = 0
    bWaitMaterial: bool = False
    bProcessing: bool = False
    stSensors: ST_Sensors = ST_Sensors()
    stActuators: ST_Actuators = ST_Actuators()

    model_config = ConfigDict(frozen=True)

class ST_Station1(BaseModel):
    control: ST_Station1_Control = ST_Station1_Control()
    status: ST_Station1_Status = ST_Station1_Status()

    model_config = ConfigDict(frozen=True)
