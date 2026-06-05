# PM_SESSION 执行跟踪附录模板

适用技能：
- `pm-workflow`
- `fullstack-engineer`
- `plc-electrical-engineer`

用途：
- 在项目已有 `PM_SESSION_<项目编号>.md` 的基础上，补齐执行日志、验证日志、交接摘要和下一步动作
- 用于保证跨会话、跨角色、跨阶段的持续协作

## 推荐追加区块

```markdown
## 6. Implementation Log
- <YYYY-MM-DD> | skill=<pm-workflow/fullstack-engineer/plc-electrical-engineer> | mode=<模式>
  - goal: <本次目标>
  - changed_files:
    - <文件路径或无>
  - artifacts:
    - <文档/测试/导出物或无>
  - impact: <影响范围>
  - risks: <风险或遗留问题>

## 7. Verification Log
- <YYYY-MM-DD>
  - verified:
    - <已验证项>
  - not_verified:
    - <未验证项>
  - method:
    - <测试/人工检查/规范核对方式>
  - blocker:
    - <阻塞项或无>

## 8. Handoff Notes
- <YYYY-MM-DD> | from=<技能名>
  - current_state: <当前状态>
  - next_focus: <下次优先处理>
  - watchouts:
    - <注意事项>
  - read_first:
    - <下次优先阅读的文件>

## 9. Next Actions
- [P1] <下一步动作> | precondition=<前置条件> | done_when=<完成标准>
- [P2] <下一步动作> | precondition=<前置条件> | done_when=<完成标准>
- [P3] <下一步动作> | precondition=<前置条件> | done_when=<完成标准>
```

## 使用原则

- 每次执行任务结束后都追加，不覆盖历史
- 没有改代码也要写分析结论和交接摘要
- `read_first` 只保留最关键的 2-5 个文件
- `next_actions` 必须足够具体，不能写成“继续优化”“后续完善”

## 软件项目填写提示

- `mode` 常见取值：
  - `前端模式`
  - `后端模式`
  - `全栈联调模式`
  - `评审模式`
  - `调试模式`
- `verified` 优先写：
  - 单元测试
  - 集成测试
  - 手工冒烟
  - 页面状态检查

## PLC/电气项目填写提示

- `mode` 常见取值：
  - `PLC编程模式`
  - `规范检查模式`
  - `程序文档模式`
  - `IO/变量/报警模式`
  - `现场调试模式`
  - `交付资料模式`
- `verified` 优先写：
  - 源码与文档一致性
  - 规范核对
  - 变更记录追溯
  - 测试/一致性报告核查
- `not_verified` 必须诚实写出：
  - 现场未验证项
  - 安全相关未复核项
  - 上机前仍需人工确认项
