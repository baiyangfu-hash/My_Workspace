# pm_session_guide.md — PM_SESSION 管理规程

> 本文档是 pm-workflow 的按需参考文档，仅在执行 PM_SESSION 回写/归档时读取。

## 1. PM_SESSION 双层结构

- **主文件**：活跃快照，**严格 ≤ 150 行**，超过立即触发归档
- **历史目录**：`00_项目管理/06_PM_SESSION历史/YYYY-MM-DD_Vx.x.x.md`

### 主文件保留内容（各节精简规则）

| 章节 | 保留内容 | 删除/归档内容 |
|:---|:---|:---|
| §2 Current Focus | current_focus + milestone | previous_focus 链 |
| §3 Status Summary | in_progress + 最近 3 条 completed + open_questions | 早期 completed（→ 历史目录） |
| §5 Logs | 本轮迭代日志 | 上轮日志（→ 历史目录） |
| §6 Execution Log | 最近 3 条 | 早期（→ CHG-*.md §9 指向） |
| §8 Handoff Notes | current_state + 最新 1 条 skill_handoff + watchouts | 早期 skill_handoff（→ 历史目录） |
| §9 Next Actions | 未完成的 Actions | 已完成的（→ 删除） |

## 2. 归档命令

```powershell
# 归档到历史目录（版本号升级时或主文件超 150 行时触发）
python -m auto_pm -w "<工作空间根>" pm-session archive <项目ID> --version <版本号>
```

## 3. 台账对账（每次 CHG 闭环后必做）

```powershell
python -m auto_pm -w "<工作空间根>" ledger reconcile <项目ID>
# 全量对账（版本号升级前）
python -m auto_pm -w "<工作空间根>" ledger reconcile <项目ID> --auto-fix
```

**禁止**：在台账有差异时升级版本号或开始新 CHG。

## 4. 真源一致性自动检查

```powershell
python -m auto_pm -w "<工作空间根>" spec check --check-id SHC-011,SHC-012,SHC-013,SHC-014
```

| 检查器 | 检查内容 |
|:---|:---|
| SHC-011 | 版本号四件套一致性（pyproject / CHANGELOG / PM_SESSION §2/§8） |
| SHC-012 | 测试数一致性（PM_SESSION §3 / 实际 pytest 结果） |
| SHC-013 | 验证状态标注（§8/§9 未验证结论处理） |
| SHC-014 | 文档索引有效性（§4 Artifacts Index 路径有效） |

**ERROR 级问题必须修复后才能回写 PM_SESSION。**
