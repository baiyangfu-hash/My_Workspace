# plc-electrical-engineer refs 索引

本目录用于存放“默认不加载、按需读取”的长参考材料；`SKILL.md` 只保留路由与硬规则。

## 使用方式

1. 先判定任务类型（Bug修复/功能开发/架构重写/规范检查/熟悉分析）与对象（气缸/真空/输送/状态机/报警联锁等）。
2. 按 `SKILL.md` 的路由表读取最小 refs 集合，禁止把 refs 全部读一遍。

## refs 目录

| 文件 | 何时读取 | 主要内容 |
|---|---|---|
| `platform-and-tia-basics.md` | 涉及 TIA 平台判断：实例化/调用、扫描周期、实例DB、优化访问、导入导出、生成块、兼容性 | 平台事实与工程上下文要点 |
| `control-skeleton.md` | 新建/重构设备类 FB，需要给结构骨架 | 通用控制骨架与阶段树（初始化/自动/手动/复位/互锁/报警/超时） |
| `scenario-families.md` | 气缸/真空阀/夹具/输送/握手/步序/状态机/报警联锁等场景 | 场景族速查与输出骨架 |
| `review-and-safety.md` | 评审/规范检查/交付审查/安全边界提示 | 反模式、检查清单、人工复核边界、证据标签 |

## 既有 documents（同样建议按需读取）

| 文件 | 适用 |
|---|---|
| [plc-electrical-engineer-tia-资料基线.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/documents/plc-electrical-engineer-tia-资料基线.md) | 需要确认本技能的“事实基线/已读规范/已知冲突点” |
| [plc-electrical-engineer-tia-编程前必要文档.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/documents/plc-electrical-engineer-tia-编程前必要文档.md) | 需要输出“编程前最小文档集/输出模板”时 |
| [plc-状态机模板对照表.md](file:///C:/Users/fubai/Desktop/My_Workspace/.trae/documents/plc-状态机模板对照表.md) | 状态机/步序类任务的实证对照与模板约束 |

