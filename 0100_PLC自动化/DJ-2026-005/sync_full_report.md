# 文档-代码全量同步报告

> **项目**: DJ-2026-005
> **生成时间**: 2026-05-21 13:39
> **路径**: C:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\DJ-2026-005

## 1. 版本差距矩阵 (L0)


| 模块                     | 代码(.scl)版本 | IFC接口文档 | DSN详细设计 | CHG变更记录 | 状态 |
| ------------------------ | :----------: | :-------: | :------: | :-------: | :--: |
| **FB_1002_SingleLayerConveyor_BufferFraming** | **V7.0.0** | V7.0.0 | V7.0.0 | - | [OK] |
| **FB_1003_PickPlace_BufferFraming** | **V7.0.0** | V7.0.0 | V7.0.0 | V7.0.0 | [OK] |
| **FB_1004_GlueMachineFeeder_BufferFraming** | **V6.0.0** | V6.0.0 | V4.1.0 | V6.0.0 | [X] |
| **FB_2001_CommonAlarm_AllStation** | **V2.1.0** | V6.0.0 | V6.0.0 | V6.0.0 | [OK] |
| **FB_ExternalDeviceInteraction** | **V4.1.0** | V4.1.0 | V4.1.0 | V6.0.0 | [OK] |
| **GlobalVars** | **V7.1.1** | V6.0.0 | - | V3.0.0 | [X] |
| **OB1** | **V7.1.1** | V7.1.1 | V7.0.0 | V7.1.1 | [X] |

> 总计: 7 个模块 | [OK]已同步: 4 | [X]滞后: 3 | [?]无法判断: 0
> 生成时间: 2026-05-21 13:39

## 2. DSN 详细设计文档覆盖度 (L2)

| FB模块 | 代码版本 | DSN版本 | DSN文件 | 状态 |
|--------|:------:|:------:|---------|:--:|
| FB_1002_SingleLayerConveyor_BufferFraming | V7.0.0 | V7.0.0 | 详细设计说明书_DSN-FB1002-SingleLayerConveyor-V7.0.0.md | [OK] |
| FB_1003_PickPlace_BufferFraming | V7.0.0 | V7.0.0 | 详细设计说明书_DSN-FB1003-PickPlace-V7.0.0.md | [OK] |
| FB_1004_GlueMachineFeeder_BufferFraming | V6.0.0 | V4.1.0 | 详细设计说明书_DSN-FB1004-GlueMachineFeeder.md | [X] |
| FB_2001_CommonAlarm_AllStation | V2.1.0 | V6.0.0 | 详细设计说明书_DSN-FB2001-CommonAlarm.md | [OK] |
| FB_ExternalDeviceInteraction | V4.1.0 | V4.1.0 | 详细设计说明书_DSN-FB-ExternalDeviceInteraction.md | [OK] |
| GlobalVars | V7.1.1 |  | - | [MISSING] |
| OB1 | V7.1.1 | V7.0.0 | 详细设计说明书_DSN-OB1.md | [X] |
| DJ-2026-005 | - | V2.0.0 | 详细设计说明书_DSN-DJ-2026-005-V2.0.0.md | [?] |

## 3. UM 使用手册覆盖度 (L2)

| FB模块 | 代码版本 | UM版本 | UM文件 | 状态 |
|--------|:------:|:------:|--------|:--:|
| FB_1002_SingleLayerConveyor_BufferFraming | V7.0.0 |  | - | [MISSING] |
| FB_1003_PickPlace_BufferFraming | V7.0.0 |  | - | [MISSING] |
| FB_1004_GlueMachineFeeder_BufferFraming | V6.0.0 | V6.0.0 | 使用说明_UM-FB1004-GlueMachineFeeder-V6.0.0.md | [OK] |
| FB_2001_CommonAlarm_AllStation | V2.1.0 | V6.0.0 | 使用说明_UM-FB2001-CommonAlarm-V6.0.0.md | [OK] |
| FB_ExternalDeviceInteraction | V4.1.0 |  | - | [MISSING] |
| GlobalVars | V7.1.1 |  | - | [MISSING] |
| OB1 | V7.1.1 |  | - | [MISSING] |

## 4. 变更台帐聚合 (L2)

| 日期 | 变更摘要 | 影响范围 | 状态 |
|------|----------|----------|------|
| 2026-05-21 | .scltest断言注释规范: basic_test.scltest全部27条ASSERT行追加//中文后缀注释(来源G | - | - |

> 共 1 条变更记录 (来源: PM_SESSION)

## 5. 同步行动建议

1. [P0] GlobalVars 缺少 DSN 详细设计文档 — 需新建
2. [P1] FB_1002_SingleLayerConveyor_BufferFraming 缺少 UM 使用手册 — 需新建
3. [P1] FB_1003_PickPlace_BufferFraming 缺少 UM 使用手册 — 需新建
4. [P1] FB_ExternalDeviceInteraction 缺少 UM 使用手册 — 需新建
5. [P1] GlobalVars 缺少 UM 使用手册 — 需新建
6. [P1] OB1 缺少 UM 使用手册 — 需新建
7. [P1] FB_1004_GlueMachineFeeder_BufferFraming DSN 版本滞后 (~2个大版本): V4.1.0 -> V6.0.0
8. [P1] OB1 DSN 版本滞后 (1个版本): V7.0.0 -> V7.1.1
9. [P1] FB_1004_GlueMachineFeeder_BufferFraming IFC/DSN/CHG 版本不一致 — 运行 generate-ifc / generate-chg
10. [P1] GlobalVars IFC/DSN/CHG 版本不一致 — 运行 generate-ifc / generate-chg
11. [P1] OB1 IFC/DSN/CHG 版本不一致 — 运行 generate-ifc / generate-chg

---
> 报告由 SW-2026-005 sync_report.py 自动生成