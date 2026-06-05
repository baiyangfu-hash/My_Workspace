# 本地技能入口说明

当前工作区本地技能已收敛为 `3 个主技能 + 1 个维护技能`。

## 推荐常用入口

### 1. `pm-workflow`

适用场景：
- 需求澄清
- PRD / REQ / DES
- 方案与线框
- 任务拆解
- 迭代推进
- 变更 / 缺陷 / 发布管理

一句话理解：
- 先定义“做什么、为什么做、做到什么程度、怎么拆和怎么跟踪”

### 2. `fullstack-engineer`

适用场景：
- 前端页面
- 后端服务
- API / Bridge / 数据流
- 联调
- 评审
- 调试
- 小程序模式分流

一句话理解：
- 负责现有软件项目的实现、联调、修复与验证

### 3. `plc-electrical-engineer`

适用场景：
- PLC 程序阅读与修改建议
- 规范核对
- IO / 变量 / 报警 / 联锁文档
- 程序设计文档
- 现场调试记录
- 交付资料整理

一句话理解：
- 负责 PLC / HMI / 电气交付项目的程序与技术文档协作

## 维护入口

### `find-skills`

适用场景：
- 查找外部技能
- 评估是否需要安装新技能
- 扩展能力边界

## 不再作为主入口的旧技能

以下技能已从主目录移出，归档到 `.trae/skills_archive/`：

- `breakdown-plan`
- `github-project-management`
- `prd`
- `product-requirements`
- `wireframe-design`
- `wireframe-prototyping`

## 选择原则

- 先做需求、方案、计划：`pm-workflow`
- 先做软件实现、调试、联调：`fullstack-engineer`
- 先做 PLC / 电气程序与文档：`plc-electrical-engineer`
- 需要扩展新能力：`find-skills`

## 持续协作规则

三个主技能现在统一遵循：

- 开始前先读取项目根目录的 `PM_SESSION_<项目编号>.md`
- 结束后必须把执行摘要回写到 `PM_SESSION`
- 不额外创建平行状态文件替代 `PM_SESSION`

推荐使用共享模板：
- [PM_SESSION_EXECUTION_APPENDIX_TEMPLATE.md](file:///c:/Users/fubai/Desktop/My_Workspace/.trae/documents/PM_SESSION_EXECUTION_APPENDIX_TEMPLATE.md)

如果后续你还想继续自动化，可再补一层 hooks：
- `sessionStart` 自动提示读取最新 handoff
- `sessionEnd` 自动提醒补写交接摘要
- `postToolUse` / `sessionEnd` 自动跑 lint、测试或规范检查

## 新项目接入

如果新项目还没有 `PM_SESSION_<项目编号>.md`，不要继续直接开发，先初始化项目连续性。

统一入口：
- `pm-workflow`

统一脚本：

```powershell
powershell -ExecutionPolicy Bypass -File "c:\Users\fubai\Desktop\My_Workspace\.trae\bin\bootstrap-project-continuity.ps1" -ProjectRoot "<项目根目录>" -ProjectId "<项目编号>" -ProjectName "<项目名称>" -ProjectType <software|plc>
```

模板目录：
- `c:\Users\fubai\Desktop\My_Workspace\.trae\project-bootstrap\software`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\project-bootstrap\plc`
