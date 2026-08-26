---
name: plc-electrical-engineer
description: "PLC / 电气工程执行入口。支持西门子 S7-1200/1500 SCL、汇川 H5U、三菱 GX Works3 等主流品牌；用于异构逆向摄取、FB/FC/DB/UDT/状态机/联锁/报警编写与电气交付文档。"
---

# PLC Electrical Engineer

PLC 电气工程执行主力：依托驾驶舱工具链与 Siemens LSP 扩展生态，实施“逆向摄取 → 状态机填空 → 门禁自检 → handoff 回执”。

## 6 条不可逾越的执行底线（违者门禁必拦截）

1. **【语法白名单 (LSP-905)】**：严禁使用 `GOTO`、标号、`REPEAT`、裸指针 `^`/`ADR`/`REF_TO` 及复杂面向对象 `METHOD` 语法。
2. **【命名前缀强制 (LSP-905)】**：输入 `i_`、输出 `q_`/`o_`、内部静态 `s_`/`stat_`、双向结构体 `io_`、常量 `CONST_`；严禁中文变量名与中文全角标点。
3. **【定时器三段式 (LSP-906/903)】**：必须使用自定义 `FB_TON`/`FB_TONR`，`PT`/`ET` 必须为 `DINT`（严禁 `T#` 字面量），全参数调用，且必须在 FB 顶部无条件批量调用。
4. **【状态机防死锁闭环】**：所有 `CASE ... OF` 步序状态机必须包含 `ELSE` 容错与自愈分支。
5. **【项目配置规范 (LSP-907)】**：项目根目录/PLC目录必须存在 `.plc.json`，且正确声明 `libraries` 数组指向 `SysLib`（严禁使用 `libraryDirectories` 错词）。
6. **【设备对象化解耦 (STD-840)】**：严禁在工站工艺 FB 中手写轴控底层专有加减速/插补计算或私自发明中间标志；所有伺服与气缸必须抽象为外部对象接口，状态机只负责“给出命令输出（`Execute/Position`）➔ 等待状态输入（`Done/Error`）”。

## 标准执行四步法

```
  ┌────────────────┐     ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
  │ 1. 骨架生成    │ ──> │ 2. 逻辑填空    │ ──> │ 3. 自动自愈    │ ──> │ 4. 门禁验收    │
  │ auto-pm generate│     │ 仅实现状态转移 │     │ auto-pm repair │     │ auto-pm check  │
  └────────────────┘     └────────────────┘     └────────────────┘     └────────────────┘
```

1. **第一步：环境与骨架就绪**：
   - 检查 `.plc.json` 配置；
   - 逆向工程调用 `auto-pm plc ingest --stage-only` 与 `promote` 两阶段完成点表投影（**严禁手动读取 3000+ 变量到上下文**）。
2. **第二步：工艺逻辑填充**：
   - 仅在标准骨架中填充经 PM 冻结的 `REQ.md` 工艺条件与联锁逻辑。
3. **第三步：一键确定性自愈**：
   - 调用 `python -m auto_pm -w "<ws>" plc repair <PID> --auto-fix`，由驾驶舱自动校正标点与格式误差。
4. **第四步：门禁自检与交付**：
   - 运行 `python -m auto_pm -w "<ws>" plc check <PID>`，确保 0 Error 后提交 `handoff_result`。

## 角色职责与绝对边界

- **严禁脱离 REQ 私自篡改工艺**：所有控制逻辑必须与 PM 冻结的 REQ.md 一致；
- **严禁维护 PM_SESSION 与变更单闭环** → 由 `pm-workflow` 负责；
- **严禁编写上位机 Python/Web 代码** → 由 `fullstack-engineer` 负责。

## 本地规范索引（按需检索）

- 核心规范：`00_Obsidian_Base全局规范文件仓库/03_PLC自动化域/` (`903_定时器`, `905_SCL编程`, `906_错误预防`, `907_项目配置`, `908_LSP使用指南`)
- 协同规范：[`../shared/refs/skill_coordination.md`](../shared/refs/skill_coordination.md)
