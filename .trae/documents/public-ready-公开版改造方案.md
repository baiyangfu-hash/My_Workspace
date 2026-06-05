# public-ready 公开版改造方案

## Summary

目标：把当前工作区内的“项目连续性自动化 + 三技能协作”整理成一个适合公开到 GitHub、并让其他人下载后尽量开箱即用的版本。

本次方案采用“方案 B”的公开化方向，目标不是只公开思路，而是尽量让外部用户可以：

1. 克隆仓库
2. 理解支持范围和限制
3. 用统一脚本初始化新项目
4. 在自己的项目里使用 `PM_SESSION + hooks + handoff draft + apply-handoff`

方案优先级：

1. 消除个人/工作区绑定
2. 收敛成可发布的目录结构
3. 明确环境支持边界
4. 提供安装与示例
5. 再考虑跨平台扩展

## Current State Analysis

### 当前已经具备公开价值的部分

- 工作区级 bootstrap 脚本已存在：
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\bin\bootstrap-project-continuity.ps1`
- 工作区级模板已存在：
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\project-bootstrap\README.md`
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\project-bootstrap\software\PM_SESSION_TEMPLATE.md`
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\project-bootstrap\plc\PM_SESSION_TEMPLATE.md`
- 通用 hooks 已存在且已实跑验证：
  - `session-start.ps1`
  - `agent-stop.ps1`
  - `session-end.ps1`
  - `apply-handoff.ps1`
- 三个主技能已具备连续协作规则：
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\pm-workflow\SKILL.md`
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\fullstack-engineer\SKILL.md`
  - `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\SKILL.md`

### 当前不适合直接公开“下载即用”的问题

#### 1. 存在绝对路径

已发现多个公开阻塞点：

- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\README.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\pm-workflow\SKILL.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\fullstack-engineer\SKILL.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\SKILL.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\documents\项目连续性自动化与新项目初始化方案.md`

这些文件中直接写了：

- `c:\Users\fubai\Desktop\My_Workspace\...`
- 工作区内固定脚本路径
- 本地 `file:///...` 链接

这会导致外部用户下载后立即失效。

#### 2. 存在你个人项目和工作区的强绑定

已确认大量内容直接绑定：

- 项目名：`SW-2026-005_PLC项目管理工具`
- 项目名：`DJ-2026-005`
- 工作区名：`My_Workspace`
- 私有项目经验和目录路径

问题不是“不能公开”，而是会让外部用户误以为这些是必须依赖，而不是示例。

#### 3. 当前默认假设是 Windows + PowerShell + Trae 生态

从现有实现可确认：

- hooks 是 `.ps1`
- 初始化脚本是 `.ps1`
- 技能目录依赖 `.trae/skills/`
- hooks 目录依赖 `.github/hooks/`

因此当前方案更接近：

- 支持 `Windows + PowerShell`
- 支持具备 `.trae`/hook 能力的环境

而不是“所有 GitHub 用户直接就能用”。

#### 4. 文档存在“内部方案文档”和“公开文档”混用

目前 `.trae/documents/` 下包含：

- 面向你自己当前工作区的内部方案文档
- 包含真实项目名、真实路径、执行历史的规划文档

这些不适合作为公开仓库的最终文档主体。

### 当前可推导的公开边界

- 公开版首阶段应只承诺：
  - Windows
  - PowerShell 5+
  - 支持 `.trae` 技能与 `.github/hooks/` 的环境
- 不应在首阶段承诺：
  - macOS/Linux 原生支持
  - 完全脱离 Trae/同类 agent 生态的通用性
  - PLC 项目自动验证通过

## Proposed Changes

### Phase 1：提炼可公开仓库结构

目标：把当前工作区形态整理成一个可发布的最小公共仓库结构。

#### 1. 新建公开版根目录规划

建议公开仓库结构：

```text
repo-root/
  README.md
  LICENSE
  .trae/
    skills/
      pm-workflow/
      fullstack-engineer/
      plc-electrical-engineer/
      README.md
    bin/
      bootstrap-project-continuity.ps1
    project-bootstrap/
      README.md
      software/
      plc/
    docs/
      QUICKSTART.md
      ENVIRONMENT.md
      ARCHITECTURE.md
      MIGRATION.md
  examples/
    software-demo/
    plc-demo/
```

为什么：

- 当前 `.trae/documents/` 混有大量内部计划文档，不适合直接暴露
- 公开版需要把“对外文档”和“内部文档”分开

#### 2. 明确哪些内容进入公开仓库

建议保留：

- `.trae/bin/bootstrap-project-continuity.ps1`
- `.trae/project-bootstrap/**`
- `.trae/skills/pm-workflow/**`
- `.trae/skills/fullstack-engineer/**`
- `.trae/skills/plc-electrical-engineer/**`
- `.trae/skills/README.md`
- 通用 hooks README

建议不直接带入：

- 当前 `.trae/documents/` 中的内部规划文件
- 带真实项目名与真实路径的大型计划文档
- 任何真实项目的 `PM_SESSION_*`

为什么：

- 公共仓库应以模板、脚本、示例为主，而不是你的真实工作上下文

### Phase 2：去私有化与去路径绑定

目标：让公开版下载后不依赖你的本地路径。

#### 3. 全量替换绝对路径为相对路径或占位符

重点修改文件：

- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\README.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\pm-workflow\SKILL.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\fullstack-engineer\SKILL.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\skills\plc-electrical-engineer\SKILL.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\documents\项目连续性自动化与新项目初始化方案.md`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\project-bootstrap\README.md`

替换原则：

- `c:\Users\fubai\Desktop\My_Workspace\.trae\bin\bootstrap-project-continuity.ps1`
  -> `.trae/bin/bootstrap-project-continuity.ps1`
- `c:\Users\fubai\Desktop\My_Workspace\.trae\project-bootstrap\software`
  -> `.trae/project-bootstrap/software`
- `file:///c:/Users/...`
  -> 普通相对路径引用或纯文本路径

为什么：

- GitHub 公共仓库不能依赖作者个人磁盘路径

#### 4. 把真实项目名降级为“示例项目”

重点修改：

- `pm-workflow\SKILL.md`
- `fullstack-engineer\SKILL.md`
- `plc-electrical-engineer\SKILL.md`
- `project-bootstrap\README.md`

做法：

- 保留“例如软件项目”“例如 PLC 项目”的描述
- 但不把 `SW-2026-005`、`DJ-2026-005` 写成默认理解或隐含依赖
- 对示例统一写成：
  - `software-demo`
  - `plc-demo`
  - 或“例如某 Python/Web 项目”“例如某 PLC/HMI 项目”

为什么：

- 公开版需要通用，不应让外部用户误解这是只适合你的两个项目

#### 5. 清理公开版文档中的内部上下文

处理对象：

- 任何带真实项目实施历史的计划文档
- 任何带真实工作区绝对路径的内部方案

做法：

- 不把这类文档纳入公开仓库
- 如需保留思路，重写成对外说明文档

为什么：

- 内部历史文档对外噪音大，且容易泄露不必要上下文

### Phase 3：补公开版文档与安装体验

目标：让别人“下载后知道怎么用”。

#### 6. 新增公共 README

建议新增：

- `repo-root/README.md`

内容至少包括：

- 这个仓库解决什么问题
- 适合什么项目
- 当前支持的环境
- 最短安装路径
- 软件项目初始化命令
- PLC 项目初始化命令
- hooks 生命周期说明
- `apply-handoff.ps1` 的使用方式
- 风险边界

为什么：

- 现在的说明分散在技能文档和内部文档中，不适合首次用户

#### 7. 新增快速开始文档

建议新增：

- `.trae/docs/QUICKSTART.md`

内容：

- 3 分钟初始化软件 demo
- 3 分钟初始化 PLC demo
- 如何生成 draft
- 如何执行 apply

为什么：

- 外部用户首先需要“最快跑通”，而不是先读完整架构说明

#### 8. 新增环境兼容文档

建议新增：

- `.trae/docs/ENVIRONMENT.md`

内容：

- 当前首发支持：
  - Windows
  - PowerShell 5+
  - `.trae/skills` / `.github/hooks` 支持环境
- 暂不支持：
  - Linux/macOS 原生脚本
  - 无 hooks 能力的纯 GitHub 页面环境

为什么：

- 必须在公开版里明确支持边界，避免误导

#### 9. 新增迁移文档

建议新增：

- `.trae/docs/MIGRATION.md`

内容：

- 如何把已有项目接入这套连续协作机制
- 如何从“旧项目补齐模式”迁移到“bootstrap 模式”

为什么：

- 公开版用户不一定从新项目开始，很多人会先拿旧项目接入

### Phase 4：提供匿名示例项目

目标：让别人 clone 后能马上看到可运行示例。

#### 10. 新增 `examples/software-demo`

建议内容：

- 一个最小目录结构：
  - `src/`
  - `tests/`
  - `ui/`
  - `main.py`
- 一个初始化后的示例 `PM_SESSION`
- 一份简短 README

为什么：

- 当前软件模板虽然已存在，但没有真正对外的匿名 demo

#### 11. 新增 `examples/plc-demo`

建议内容：

- 一个匿名 PLC/HMI 项目骨架：
  - `02_PLC程序/`
  - `03_HMI设计/`
  - `04_现场调试/`
  - `06_文档与交付/`
- 初始化后的示例 `PM_SESSION`
- 一份简短 README

为什么：

- PLC 场景比软件场景更依赖目录骨架，demo 有助于别人快速理解适用边界

### Phase 5：公开仓库工程化补齐

目标：让公开版看起来像一个真正可发布仓库。

#### 12. 增加许可证

建议新增：

- `LICENSE`

建议：

- 若希望他人广泛复用：`MIT`
- 若更强调专利/贡献保护：`Apache-2.0`

为什么：

- 没有 License，别人默认不清楚能否复用

#### 13. 增加版本与变更说明

建议新增：

- `CHANGELOG.md`

内容：

- 首个 public-ready 版本包含哪些能力
- 哪些能力仍是实验性

为什么：

- 公开后必须可追踪版本变化

#### 14. 增加发布前自检清单

建议新增：

- `.trae/docs/PUBLIC_RELEASE_CHECKLIST.md`

内容：

- 绝对路径是否清理
- 私有项目名是否降级为示例
- README 是否可独立阅读
- 示例项目是否能跑通
- 是否明确 Windows-only 边界

为什么：

- 防止以后再次把私有信息或不可运行内容带进公共版本

## Assumptions & Decisions

### 已锁定决策

- 目标是“别人下载就尽量能用”，不是只公开思路
- 第一版公开版优先支持：
  - Windows
  - PowerShell
  - `.trae` / hooks 兼容环境
- 第一版不做跨平台脚本重写
- 第一版不公开真实项目 `PM_SESSION`
- 第一版用匿名 demo 代替真实项目示例

### 关键假设

- 你愿意把这套内容整理成独立公共仓库或公共子目录
- 允许将部分中文说明保留，但核心安装文档最好中英都可读或至少英文可用
- 公开版可接受“对 Trae/兼容环境有依赖”的前提

## Risks

### 风险 1：公开后别人仍然无法运行

原因：

- 环境差异大
- hooks 生态不统一

缓解：

- README 明确支持矩阵
- 提供 demo
- 快速开始文档只覆盖首发受支持场景

### 风险 2：仍残留私有路径或私有上下文

原因：

- 当前 `.trae` 内部文档很多，容易漏掉

缓解：

- 发布前跑一次全量 grep：
  - `c:\Users\`
  - `My_Workspace`
  - 真实项目编号
- 使用公共发布清单逐项核对

### 风险 3：PLC 场景被误用为“可自动化验证”

原因：

- 外部用户可能把 hooks 误解成“自动验收”

缓解：

- 在 README、ENVIRONMENT、plc skill 中持续强调：
  - 文档一致性不等于可上机
  - 编译、现场、安全相关复核必须人工完成

### 风险 4：技能文档过于依赖 Trae 本地生态

原因：

- `.trae/skills/` 是特定生态目录

缓解：

- 在 README 中明确“这是面向 Trae/兼容 agent 技能环境的公开仓库”
- 不把它包装成通用 IDE 插件

## Verification Steps

### 文档与路径验证

1. 对公开版目录执行 grep，确保不存在：
   - `c:\Users\`
   - `My_Workspace`
   - `SW-2026-005`
   - `DJ-2026-005`
2. 确认 README 与 QUICKSTART 中只出现相对路径或占位符

### 安装与初始化验证

1. 在全新匿名软件目录中执行：
   - `.trae/bin/bootstrap-project-continuity.ps1`
2. 确认生成：
   - `PM_SESSION_<id>.md`
   - `.github/hooks/`
   - `.trae/handoffs/`
3. 在全新匿名 PLC 目录中重复一次

### hooks 验证

1. 在 `software-demo` 中验证：
   - `session-start.ps1`
   - `session-end.ps1`
   - `apply-handoff.ps1`
2. 在 `plc-demo` 中验证：
   - `session-start.ps1`
   - `session-end.ps1`
   - `apply-handoff.ps1`
   - `agent-stop.ps1`

### 公开可读性验证

1. 不看内部计划文档，只看公开版 `README + QUICKSTART`
2. 确认外部用户可以理解：
   - 适用场景
   - 环境要求
   - 初始化方式
   - 风险边界

## Recommended Execution Order

1. 先新建公开版目录结构
2. 再替换绝对路径与真实项目绑定
3. 再补 README / QUICKSTART / ENVIRONMENT / MIGRATION
4. 再增加 `software-demo` 与 `plc-demo`
5. 最后补 `LICENSE / CHANGELOG / PUBLIC_RELEASE_CHECKLIST`

## Done Definition

当以下条件全部满足时，视为 public-ready 改造完成：

- 公开版目录中不再包含个人绝对路径
- 公开版目录中不再依赖真实项目编号或真实项目状态文件
- 外部用户可通过 README 和 QUICKSTART 独立完成初始化
- 软件与 PLC 两类匿名 demo 均能跑通 bootstrap 与 hooks
- 公开版明确说明支持边界和风险边界
- 仓库具备基本发布要素：README、LICENSE、CHANGELOG、示例、环境说明
