from bridge.dto import ST_Sensors, ST_Station1, ST_Station1_Status


def test_dto_instantiation():
    # Verify manual instantiation
    sensors = ST_Sensors(bCylinderUp=True)
    assert sensors.bCylinderUp is True

    status = ST_Station1_Status(
        bRunning=True,
        bWaitMaterial=True,
        stSensors=sensors,
    )
    assert status.bWaitMaterial is True
    assert status.bRunning is True

    station = ST_Station1(status=status)
    assert station.status.bWaitMaterial is True
