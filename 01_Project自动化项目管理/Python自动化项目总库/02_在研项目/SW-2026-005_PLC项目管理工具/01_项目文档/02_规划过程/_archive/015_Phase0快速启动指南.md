# Phase 0 快速启动指南 — V6.1.0 基础重构

> **目标**: 建立稳固的数据模型基础，为后续 UI 实施铺路
> **周期**: Week 1-2 (2026-06-02 ~ 2026-06-15)
> **产出**: 6 个新枚举类 + ChangeRequestV2(50+字段) + ChangeServiceV2 + 编号器 + 模板渲染器
> **代码量**: ~1900 行新增（含测试）

---

## 🚀 立即开始：第一个 Task（5 分钟完成）

### T-2.1.1-01: 新增 ChangeDomain 枚举

**文件**: `src/core/constants.py`  
**位置**: 在现有 `ChangeCategory` 枚举之后（约第 226 行）  
**操作**: 新增以下代码

```python
class ChangeDomain(Enum):
    """技术领域 - 变更属于哪个专业？(PM-042 §3.1)"""
    ELEC = "ELEC"      # 电气设计
    MECH = "MECH"      # 机械结构
    PLC = "PLC"        # PLC程序
    HMI = "HMI"        # HMI程序
    SCPT = "SCPT"      # Python脚本
    DOCU = "DOCU"      # 工程文档
    SAFE = "SAFE"      # 安全功能


class ChangeNature(Enum):
    """业务性质 - 为什么变？(PM-042 §3.2)"""
    REQ = "REQ"        # 需求变更
    DEF = "DEF"        # 缺陷修复
    OPT = "OPT"        # 优化改进
    CFG = "CFG"        # 配置调整
    EMRG = "EMRG"      # 紧急变更


class ChangeScope(Enum):
    """影响范围 - 影响到什么程度？(PM-042 §3.3)"""
    LOCAL = "LOCAL"     # 局部变更
    MODULE = "MODULE"   # 模块级变更
    SYSTEM = "SYSTEM"   # 系统级变更
    CROSS = "CROSS"     # 跨系统变更
    SAFE = "SAFE"       # 安全相关变更


class UrgencyLevel(Enum):
    """紧急程度"""
    NORMAL = "NORMAL"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class ApprovalStage(Enum):
    """审批阶段"""
    INITIAL = "initial"       # 初审
    REVIEW = "review"         # 复审
    FINAL = "final"           # 终审


class ApprovalAction(Enum):
    """审批动作"""
    APPROVE = "approve"       # 通过
    CONDITIONAL = "conditional"  # 有条件通过
    REJECT = "reject"         # 驳回
    DENY = "deny"             # 拒绝
```

**验证**:
```bash
cd 03_主程序/01_主程序核心代码
python -c "from src.core.constants import ChangeDomain; print([d.value for d in ChangeDomain])"
# 预期输出: ['ELEC', 'MECH', 'PLC', 'HMI', 'SCPT', 'DOCU', 'SAFE']
```

---

## 📋 Phase 0 完整 Task 清单（按执行顺序）

### Week 1: 数据模型层（Day 1-3）

| # | Task | 文件 | SP | 验证命令 |
|---|------|------|----|----------|
| **T-1** | ✅ **新增 6 个枚举类** | [constants.py](src/core/constants.py) | 3S | 见上方 |
| **T-2** | 新增 ChangeStatusV2 (12态) | [constants.py](src/core/constants.py) | 5M | `python -c "from src.core.constants import ChangeStatusV2; print(len([s for s in ChangeStatusV2]))"` → 12 |
| **T-3** | 新增 CHANGE_STATUS_TRANSITIONS_V2 矩阵 | [constants.py](src/core/constants.py) | 2S | 覆盖 24 条合法转换路径 |
| **T-4** | 创建 ChangeRequestV2 dataclass (50+字段) | `src/models/change_request_v2.py` (**新建**) | 8L | Pydantic 校验全部字段 |
| **T-5** | 新增 10 个嵌套数据类 (ChangeState/ImpactAnalysis/...) | 同上 | 3S | 单元测试通过 |

### Week 1: Service 层（Day 4-5）

| # | Task | 文件 | SP | 验证方法 |
|---|------|------|----|----------|
| **T-6** | 创建 ChangeNumberGenerator | `src/services/change_number_generator.py` (**新建**) | 3S | 并发创建不冲突 |
| **T-7** | 创建 ChangeTemplateRenderer | `src/services/change_template_renderer.py` (**新建**) | 5M | 输出符合 CHG-040 格式 |
| **T-8** | 创建 ChangeServiceV2 (骨架) | `src/services/change_service_v2.py` (**新建**) | 5M | 7 个公开方法签名正确 |

### Week 2: Service 实现（Day 6-8）

| # | Task | 方法数 | SP | 关键逻辑 |
|---|------|--------|----|----------|
| **T-9** | ChangeServiceV2.create_change_request() | 1 | 50+ 字段校验 + 自动编号 + Markdown 渲染 |
| **T-10** | ChangeServiceV2.transition_status() | 1 | 12 态状态机 + 合法转换验证 |
| **T-11** | ChangeServiceV2.list_change_requests() | 1 | 扫描 + 过滤 + 排序 |
| **T-12** | ChangeServiceV2.get_change_statistics() | 1 | 按领域/状态/时间维度聚合 |
| **T-13** | 向后兼容层 (旧 API 包装) | 4 | @deprecated 标记 + 调用 V2 |

### Week 2: 测试（Day 9-10）

| # | 测试文件 | 覆盖范围 | 行数 |
|---|----------|----------|------|
| **T-14** | `tests/test_enums_v2.py` | 6 个枚举遍历/序列化 | ~80 |
| **T-15** | `tests/test_change_status_v2.py` | 24+ 转换路径 | ~120 |
| **T-16** | `tests/test_change_request_v2.py` | 全字段构造/校验 | ~150 |
| **T-17** | `tests/test_change_number_generator.py` | 格式/唯一性/并发 | ~80 |
| **T-18** | `tests/test_change_service_v2.py` | E2E 创建→流转→列表 | ~200 |
| **T-19** | `tests/test_change_template_renderer.py` | Markdown 输出比对 | ~80 |

---

## 📁 新建文件清单

```
03_主程序/01_主程序核心代码/
├── src/
│   ├── models/
│   │   └── change_request_v2.py          ← T-4, T-5 (NEW)
│   └── services/
│       ├── change_number_generator.py   ← T-6 (NEW)
│       ├── change_template_renderer.py  ← T-7 (NEW)
│       └── change_service_v2.py         ← T-8~T-13 (NEW)
├── tests/
│   ├── test_enums_v2.py                ← T-14 (NEW)
│   ├── test_change_status_v2.py        ← T-15 (NEW)
│   ├── test_change_request_v2.py       ← T-16 (NEW)
│   ├── test_change_number_generator.py ← T-17 (NEW)
│   ├── test_change_service_v2.py       ← T-18 (NEW)
│   └── test_change_template_renderer.py← T-19 (NEW)
└── templates/
    └── CHG-040-V2.0.0.md               ← 变更单模板 (从全局规范仓库复制)
```

### 修改文件清单

```
├── src/core/
│   └── constants.py                     ← T-1~T-3 (新增枚举, 不删除旧的)
```

---

## ⚠️ 关键注意事项

### 1. 向后兼容（绝对不能破坏）

```python
# ❌ 错误: 删除旧枚举
# del ChangeCategory
# del ChangeStatus

# ✅ 正确: 保留旧枚举，新增 V2 版本
class ChangeCategory(Enum):
    """@deprecated Use ChangeDomain + ChangeNature instead"""
    DOCU = "DOCU"
    PLC = "PLC"
    # ...

class ChangeStatus(Enum):
    """@deprecated Use ChangeStatusV2 instead"""
    DRAFT = "draft"
    # ...
```

### 2. 文件存储路径规范

```python
# 变更单存储位置（遵循 PM-042 §10.6）
CHANGE_ROOT = Path("01_项目管理") / "04_变更管理" / "01_变更单"

# 目录结构
{project_root}/
└── 01_项目管理/
    └── 04_变更管理/
        ├── 01_变更单/
        │   ├── PLC/          ← ChangeDomain.PLC
        │   │   ├── CHG-PLC-2026-001.md
        │   │   └── CHG-PLC-2026-002.md
        │   ├── ELEC/         ← ChangeDomain.ELEC
        │   └── ...
        ├── 04_变更记录/
        │   └── 041_版本变更台帐.md
        └── README.md
```

### 3. 编号生成规则

```python
# 格式: CHG-{DOMAIN}-{YYYY}-{XXX}
# 示例: CHG-PLC-2026-003

def generate(project_path: str, domain: ChangeDomain) -> str:
    year = datetime.now().year
    pattern = f"CHG-{domain.value}-{year}-*.md"
    
    # 查询同域同年最大序号
    existing = list(Path(project_path).rglob(pattern))
    max_seq = max(
        int(f.stem.split("-")[-1]) 
        for f in existing
    , default=0)
    
    return f"CHG-{domain.value}-{year}-{max_seq + 1:03d}"
```

---

## 🔗 相关文档引用

| 文档 | 用途 |
|------|------|
| [PRD-V6.1.0.md](../00_项目基础信息/001_产品需求文档_PRD-V6.1.0.md) | 完整需求定义 |
| [014_DEV-PLAN-V6.1.0.md](./014_V6.1实施计划_DEV-PLAN-V6.1.0.md) | 详细 58 个 Task 分解 |
| [PM_SESSION_SW-2026-005.md](../PM_SESSION_SW-2026-005.md) | 项目状态跟踪 |
| PM-042 通用变更管理流程规范 V2.1.0 | 12 种状态定义 |
| CHG-040 通用变更单模板 V2.0.0 | 50+ 字段数据模型 |

---

## ✅ Phase 0 完成标准（Definition of Done）

- [ ] 6 个新枚举类全部实现并通过单元测试
- [ ] ChangeRequestV2 包含 50+ 字段且 Pydantic 校验通过
- [ ] ChangeNumberGenerator 支持并发安全（文件锁）
- [ ] ChangeTemplateRenderer 输出符合 CHG-040 格式
- [ ] ChangeServiceV2 提供 7 个公开方法 + 4 个兼容方法
- [ ] 状态机覆盖 24+ 条转换路径（合法 + 非法）
- [ ] 测试覆盖率 ≥ 80%（新增模块）
- [ ] 无 breaking changes（旧 API 可用）
- [ ] 代码遵循 CODE-210 规范（命名/类型注解/文档）

---

## 🎯 下一步：Phase 1 准备

Phase 0 完成后，立即开始：

1. **WorkspaceDashboardService** — 项目总览计算逻辑
2. **前端 change-form.js** — 4 步向导式变更单表单
3. **前端 change-center.js** — 变更管理中心容器组件

**预计开始日期**: 2026-06-16 (Week 3 Day 1)

---

*文档版本*: 1.0
*创建日期*: 2026-06-02
*状态*: Ready for Execution
*基于*: 014_V6.1实施计划_DEV-PLAN-V6.1.0.md Phase 0 章节
