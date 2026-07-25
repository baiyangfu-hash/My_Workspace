# 使用说明 FB_1003_PickPlace_BufferFraming

## 1. 功能

取放料机构控制。Z轴升降+X1轴横移+4组夹爪。6步S20~S25，一次取两根边框。

## 2. 实例化

```
VAR
  fbPickPlace : FB_1003_PickPlace_BufferFraming;
END_VAR
```

## 3. 取料层循环

OB1循环 L1→L2→L3→L4→L1→... 设置 i_iPickLayer，每次循环完成两次取放。

## 4. 教导点位

| 点位 | D区 | 说明 |
|------|-----|------|
| 取片教点 | D514 | Z轴取料高度 |
| 前放料点 | D520 | X1轴 L1/L3 放料位置 |
| 后放料点 | D540 | X1轴 L2/L4 放料位置 |
| 放片教点 | D524 | Z轴放料高度 |

## 5. 调试要点

1. S22步需4夹紧+4光电全确认（缺一则认为夹紧/取料失败）
2. 夹紧确认时间(i_iClampConfirmTime)超时置报警码101
3. 放料完成信号(q_bPlaceDoneToFeeder)为脉冲，触发FB_1004的D760=0→1
4. 边框检测(q_bFrameOnPickupPlatform)用于回原点阻塞条件
