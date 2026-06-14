# SW-2026-004 项目启动完整流程图

**项目名称**：Python项目管理工具
**当前版本**：V2.8.0
**编制日期**：2026-06-14

---

## 1. 项目全生命周期总览

```mermaid
graph LR
    A[项目启动] --> B[规划过程]
    B --> C[执行过程]
    C --> D[监控和控制]
    D -->|反馈/变更| B
    D -->|交付/收尾| E[项目收尾]

    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#9C27B0,color:#fff
    style E fill:#607D8B,color:#fff
```

---

## 2. 启动过程详细流程

```mermaid
graph TD
    subgraph 启动触发["① 启动触发"]
        PAIN[痛点识别<br/>Python项目管理无标准化工具<br/>变更管控缺失/版本混乱] --> PROPOSAL[项目立项<br/>SW-2026-004]
    end

    subgraph 章程制定["② 项目章程制定"]
        PROPOSAL --> CHARTER[编制项目章程<br/>006_产品化项目章程_PM.md]
        CHARTER --> VISION[明确产品愿景<br/>自动化领域全生命周期项目管理工具]
        CHARTER --> SCOPE[界定项目范围<br/>GUI+CLI双模式/总库管理/变更管控]
        CHARTER --> GOAL[设定项目目标<br/>业务/技术/质量/进度/成本5维目标]
        CHARTER --> ROLE[分配项目角色<br/>项目经理/技术负责人/开发/测试/文档]
    end

    subgraph 路线图规划["③ 产品路线图规划"]
        VISION --> ROADMAP[编制产品路线图<br/>007_产品路线图_PM.md]
        ROADMAP --> VERSION[版本演进规划<br/>V1.x基础→V2.x增强→V3.0企业级]
        ROADMAP --> MARKET[目标市场定位<br/>自动化开发团队/PLC工程师/项目经理]
    end

    subgraph 基线建立["④ 存量资产基线建立"]
        SCOPE --> BASELINE[编制基线清单<br/>01_存量资产基线清单_BASELINE.md]
        BASELINE --> CODE_BASE[代码资产盘点<br/>100+文件/15000行/24个Service/16个Model]
        BASELINE --> DOC_BASE[文档资产盘点<br/>启动/规划/执行/监控4组文档]
        BASELINE --> TECH_BASE[技术栈确认<br/>PyQt5 5.15+/Flask 3.1.2/SQLAlchemy 2.x/SQLite]
        BASELINE --> TEMPLATE_BASE[模板资产盘点<br/>5个YAML内置模板/继承机制/版本管理]
    end

    subgraph 启动验收["⑤ 启动验收"]
        CODE_BASE --> REVIEW[启动文档评审]
        DOC_BASE --> REVIEW
        TECH_BASE --> REVIEW
        TEMPLATE_BASE --> REVIEW
        REVIEW --> APPROVE{章程/路线图/<br/>基线是否通过?}
        APPROVE -->|是| KICKOFF[项目启动完成<br/>进入规划过程]
        APPROVE -->|否| CHARTER
    end

    style PAIN fill:#FFCDD2,color:#333
    style KICKOFF fill:#4CAF50,color:#fff
    style APPROVE fill:#FFF9C4,color:#333
```

---

## 3. 规划过程详细流程

```mermaid
graph TD
    subgraph 需求分析["① 需求分析"]
        REQ[需求规格说明书<br/>01_需求规格说明书_REQ.md] --> FR[功能需求梳理<br/>FR-001~FR-017]
        REQ --> NFR[非功能需求定义<br/>性能/安全/可用性/兼容性]
        REQ --> DM[数据模型设计<br/>项目/模板/变更/缺陷/库/审批等16个Model]
    end

    subgraph 架构设计["② 架构设计"]
        ARCH[架构设计文档<br/>07_架构设计文档_ARCH.md] --> LAYER[分层架构设计<br/>表现层→服务层→DAO层→模型层→工具层]
        ARCH --> DI[依赖注入容器<br/>core/container.py]
        ARCH --> DECOUPLE[模块解耦策略<br/>TemplateService统一访问/避免直接DAO]
    end

    subgraph 技术方案["③ 技术方案"]
        DEV[总库管理技术方案<br/>03_总库管理技术方案_DEV.md] --> TECH[技术选型确认<br/>PyQt5/Flask/SQLAlchemy/Alembic/Click]
        DEV --> IMPL[实现路径规划<br/>模块开发顺序/接口定义]
        DEV --> MIGRATE[数据库迁移策略<br/>Alembic版本管理]
    end

    subgraph 详细设计["④ 详细设计"]
        DES[详细设计文档<br/>08_详细设计文档_DES.md] --> ER[ER图设计<br/>16个ORM实体关系]
        DES --> SEQ[序列图设计<br/>核心业务流程交互]
        DES --> API[API接口设计<br/>06_API文档_INT.md]
    end

    subgraph 风险管理["⑤ 风险管理"]
        REP[风险登记册<br/>05_风险登记册_REP.md] --> RISK[风险识别与评估<br/>TR-001~TR-005 + SR-001~SR-002]
        REP --> MITIGATE[应对措施制定<br/>已关闭3项/监控2项/减轻2项]
    end

    subgraph 规划验收["⑥ 规划验收"]
        FR --> PLAN_REVIEW[规划文档评审]
        NFR --> PLAN_REVIEW
        LAYER --> PLAN_REVIEW
        TECH --> PLAN_REVIEW
        ER --> PLAN_REVIEW
        RISK --> PLAN_REVIEW
        PLAN_REVIEW --> PLAN_APPROVE{规划是否<br/>通过?}
        PLAN_APPROVE -->|是| EXEC[进入执行过程]
        PLAN_APPROVE -->|否| REQ
    end

    style EXEC fill:#FF9800,color:#fff
    style PLAN_APPROVE fill:#FFF9C4,color:#333
```

---

## 4. 执行过程详细流程

```mermaid
graph TD
    subgraph 开发实施["① 开发实施"]
        CODING[代码开发] --> CORE[核心模块<br/>app/config/constants/container]
        CODING --> MODELS[数据模型层<br/>16个SQLAlchemy ORM Model]
        CODING --> DAO[数据访问层<br/>15个DAO模块]
        CODING --> SERVICES[服务层<br/>24个Service模块]
        CODING --> UI[GUI界面层<br/>PyQt5 9个Tab页签]
        CODING --> API_LAYER[API层<br/>Flask 8个Blueprint + JWT]
        CODING --> PLUGINS[插件系统<br/>3个内置插件]
    end

    subgraph 文档编写["② 文档编写"]
        MAN[用户操作手册<br/>01_用户操作手册_MAN.md V2.8.0]
        QUICK_PM[PM快速入门<br/>05_PM快速入门指南_PM.md]
        QUICK_PLC[PLC工程师快速入门<br/>06_PLC工程师快速入门指南_PLC.md]
    end

    subgraph 测试验证["③ 测试验证"]
        TEST[测试计划执行<br/>03_测试计划_TEST.md V2.8.0] --> UNIT[单元测试<br/>PyTest 8.0+]
        TEST --> INTEGRATION[集成测试<br/>模块间交互验证]
        TEST --> SYSTEM[系统测试<br/>GUI端到端验证]
        TEST --> ACCEPT[验收测试<br/>需求覆盖率验证]
    end

    subgraph 打包发布["④ 打包发布"]
        BUILD[构建打包<br/>PyInstaller 6.4.0 目录模式] --> EXE[可执行文件<br/>Python项目管理工具.exe ~120MB]
        EXE --> DELIVERY[交付物整理<br/>02_发布说明/01_交付清单_DEL.md]
    end

    CORE --> TEST
    MODELS --> TEST
    DAO --> TEST
    SERVICES --> TEST
    UI --> TEST
    API_LAYER --> TEST
    PLUGINS --> TEST
    UNIT --> BUILD
    INTEGRATION --> BUILD
    SYSTEM --> BUILD
    ACCEPT --> BUILD

    style BUILD fill:#FF9800,color:#fff
    style DELIVERY fill:#4CAF50,color:#fff
```

---

## 5. 监控和控制详细流程

```mermaid
graph TD
    subgraph 变更管理["① 变更管理"]
        CHANGE_REQ[变更请求] --> CHANGE_CLASS[二维分类<br/>Domain×Nature×Scope]
        CHANGE_CLASS --> APPROVAL_LEVEL{影响范围<br/>分级审批}
        APPROVAL_LEVEL -->|LOCAL/MODULE| PM_APPROVE[项目经理审批]
        APPROVAL_LEVEL -->|SYSTEM| LEAD_APPROVE[技术总监审批]
        APPROVAL_LEVEL -->|CROSS| DIRECTOR_APPROVE[技术总监+项目经理]
        APPROVAL_LEVEL -->|SAFE| SAFETY_APPROVE[安全官+高管审批]
        PM_APPROVE --> CHANGE_EXEC[变更执行]
        LEAD_APPROVE --> CHANGE_EXEC
        DIRECTOR_APPROVE --> CHANGE_EXEC
        SAFETY_APPROVE --> CHANGE_EXEC
        CHANGE_EXEC --> CHANGE_LEDGER[更新版本变更台帐<br/>06_版本变更台帐_CHG.md]
    end

    subgraph 版本管控["② 版本管控"]
        VERSION_PLAN[版本规划] --> SEMVER[语义化版本<br/>MAJOR.MINOR.PATCH]
        SEMVER --> VERSION_LOG[版本变更记录<br/>V1.0.0→V2.8.0共12个版本]
        VERSION_LOG --> MIGRATION[数据库迁移<br/>Alembic管理Schema变更]
    end

    subgraph 文档审查["③ 文档审查"]
        DOC_REVIEW[文档审查机制<br/>05_文档审查机制_DOC.md] --> CONSISTENCY[一致性检查<br/>技术栈/版本号/数据模型]
        DOC_REVIEW --> COMPLETENESS[完整性检查<br/>文档覆盖率/字段完整性]
        DOC_REVIEW --> TRACEABILITY[可追溯性检查<br/>需求→设计→代码→测试]
    end

    subgraph 质量监控["④ 质量监控"]
        QUALITY[质量指标监控] --> CODE_QUALITY[代码质量<br/>规范符合率≥90%]
        QUALITY --> TEST_QUALITY[测试质量<br/>通过率≥95%]
        QUALITY --> DOC_QUALITY[文档质量<br/>完整性100%]
    end

    CHANGE_LEDGER --> FEEDBACK{是否需要<br/>调整规划?}
    FEEDBACK -->|是| REPLAN[返回规划过程<br/>更新需求/架构/方案]
    FEEDBACK -->|否| RELEASE[版本发布]
    CONSISTENCY --> FEEDBACK
    COMPLETENESS --> FEEDBACK
    TRACEABILITY --> FEEDBACK
    CODE_QUALITY --> FEEDBACK
    TEST_QUALITY --> FEEDBACK
    DOC_QUALITY --> FEEDBACK

    style CHANGE_REQ fill:#E1BEE7,color:#333
    style RELEASE fill:#4CAF50,color:#fff
    style FEEDBACK fill:#FFF9C4,color:#333
```

---

## 6. 版本演进时间线

```mermaid
graph LR
    subgraph V1x["V1.x 基础阶段"]
        V100["V1.0.0<br/>2026-03-01<br/>初始版本"]
        V101["V1.0.1<br/>2026-03-05<br/>架构文档"]
        V102["V1.0.2<br/>2026-03-10<br/>API文档"]
        V103["V1.0.3<br/>2026-03-15<br/>规范整改"]
        V100 --> V101 --> V102 --> V103
    end

    subgraph V2x["V2.x 增强阶段"]
        V210["V2.1.0<br/>2026-04-12<br/>变更管理升级"]
        V220["V2.2.0<br/>2026-04-12<br/>全面优化"]
        V230["V2.3.0<br/>2026-05-01<br/>缺陷管理"]
        V240["V2.4.0<br/>2026-05-10<br/>库管理"]
        V250["V2.5.0<br/>2026-05-20<br/>PLC插件+市场"]
        V260["V2.6.0<br/>2026-06-10<br/>导入项目"]
        V270["V2.7.0<br/>2026-06-12<br/>文档先行"]
        V280["V2.8.0<br/>2026-06-14<br/>模板管理优化"]
        V210 --> V220 --> V230 --> V240 --> V250 --> V260 --> V270 --> V280
    end

    subgraph V3x["V3.0 规划中"]
        V300["V3.0.0<br/>待规划<br/>GUI端到端验证<br/>模板升级UI<br/>国际化"]
        V280 --> V300
    end

    style V100 fill:#C8E6C9,color:#333
    style V280 fill:#4CAF50,color:#fff
    style V300 fill:#E0E0E0,color:#666
```

---

## 7. 系统架构与启动流程映射

```mermaid
graph TD
    subgraph 用户入口["用户入口"]
        USER[用户] --> GUI[PyQt5 GUI<br/>9个Tab页签]
        USER --> CLI[Click CLI<br/>create-project等]
        USER --> REST[Flask REST API<br/>8个Blueprint]
    end

    subgraph 核心业务流["核心业务流"]
        GUI --> PS[ProjectService<br/>项目创建/导入/管理]
        GUI --> TS[TemplateService<br/>模板加载/继承/版本]
        GUI --> CS[ChangeService<br/>变更单/审批/传播链]
        CLI --> PS
        REST --> PS
        REST --> TS
        REST --> CS

        PS -->|创建项目| TS
        TS -->|加载模板| YAML[(YAML模板文件<br/>config/templates/)]
        PS -->|记录变更| CS
        CS -->|分级审批| AS[ApprovalService]
    end

    subgraph 数据层["数据层"]
        PS --> DAO[DAO层<br/>15个DAO模块]
        TS --> DAO
        CS --> DAO
        AS --> DAO
        DAO --> DB[(SQLite<br/>project_manager.db)]
        DAO --> MIGRATE[Alembic迁移<br/>Schema版本管理]
    end

    style USER fill:#4CAF50,color:#fff
    style DB fill:#FFD54F,color:#333
    style YAML fill:#81D4FA,color:#333
```

---

## 8. 关键文档与流程节点对应关系

| 流程节点 | 关键文档 | 当前版本 | 状态 |
|----------|---------|---------|------|
| 项目立项 | 006_产品化项目章程_PM.md | PM-V1.0.0 | 历史文档（已标注） |
| 路线图 | 007_产品路线图_PM.md | PM-V1.0.0 | 历史文档（已标注） |
| 基线盘点 | 01_存量资产基线清单_BASELINE.md | V2.8.0 | ✅ 已更新 |
| 需求分析 | 01_需求规格说明书_REQ.md | V2.8.0 | ✅ 已更新 |
| 架构设计 | 07_架构设计文档_ARCH.md | V2.8.0 | ✅ 已更新 |
| 技术方案 | 03_总库管理技术方案_DEV.md | V2.8.0 | ✅ 已更新 |
| 详细设计 | 08_详细设计文档_DES.md | V2.8.0 | ✅ 已更新 |
| API设计 | 06_API文档_INT.md | V2.8.0 | ✅ 已更新 |
| 风险管理 | 05_风险登记册_REP.md | V2.8.0 | ✅ 已更新 |
| 用户手册 | 01_用户操作手册_MAN.md | V2.8.0 | ✅ 已更新 |
| 测试计划 | 03_测试计划_TEST.md | V2.8.0 | ✅ 已更新 |
| 变更管理 | 01_变更管理技术方案_DEV.md | V2.1.0 | ✅ 已更新 |
| 版本台帐 | 06_版本变更台帐_CHG.md | V2.8.0 | ✅ 已更新 |
| 文档审查 | 05_文档审查机制_DOC.md | V2.8.0 | ✅ 已更新 |
| 模板优化 | 07_模板管理优化技术方案_DEV.md | V2.8.0 | ✅ 新增 |
| 项目会话 | PM_SESSION_SW-2026-004.md | V2.8.0 | ✅ 活跃 |

---

*文档生成时间：2026-06-14*
