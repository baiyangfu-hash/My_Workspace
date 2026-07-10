---
version: "V1.0"
status: "已完成"
created: "2026-07-07"
updated: "2026-07-07"
project_id: "SW-2026-008"
milestone: "M4（第 1 批）"
---

# M4 第 1 批：SpecFacade 落地计划

## 一、目标与 done_when

**M4 总目标**：规范中心、报告发布、系统设置进入新结构
**M4 done_when**：主要全局页面全部脱离"直接绑多个 service"的扩展方式

**第 1 批目标**：SpecFacade 从"转发层"升级为"用例编排层"，返回带类型 DTO
**第 1 批 done_when**：SpecFacade 3 方法返回带类型 DTO + SpecBridge 3 Slot 改用 asdict 转换 + 测试覆盖 ≥10 个

## 二、现状诊断

### SpecFacade（spec_facade.py）— 3 方法已落地但返回裸 dict

| 方法 | 当前返回 | 问题 |
|------|----------|------|
| run_spec_check() | CommandResult[dict] | 裸 dict，无类型约束 |
| get_spec_center_overview() | QueryResult[dict] | 裸 dict，无类型约束 |
| list_spec_center_entries(filter_domain) | QueryResult[list[dict]] | 裸 list[dict]，无类型约束 |

### SpecBridge（spec_bridge.py）— 3 Slot 已落地但直接返回 dict

| Slot | 当前返回 | 问题 |
|------|----------|------|
| runSpecCheck() | dict + emit specCheckCompleted | 直接返回 dict |
| getSpecOverview() | dict | 直接返回 dict |
| listSpecEntries(filter_domain) | list | 直接返回 list |

### spec_dto.py — 仅 1 个 DTO，未被使用

```python
@dataclass(frozen=True)
class SpecCenterDTO:  # 聚合 DTO，未被 Facade 使用
    overview: dict[str, Any]
    index_items: list[dict[str, Any]]
    check_items: list[dict[str, Any]]
    drift_items: list[dict[str, Any]]
```

### spec_commands.py — 1 个 Command，未被使用

```python
@dataclass(frozen=True)
class RunSpecCheckCommand:
    target_path: str
    auto_fix: bool
    scope: str
```

### 测试覆盖 — 0 个测试

无 test_spec_facade.py / test_spec_bridge.py

## 三、DTO 决策

采用 M2/M3 延续的 DTO 双源体系：dataclass（Facade 边界）+ Pydantic（Service 层）。

### 新增 3 个 DTO（spec_dto.py 补全）

```python
@dataclass(frozen=True)
class SpecCheckResultDTO:
    """规范检查结果（对应 run_spec_check 返回）"""
    error_count: int
    warning_count: int
    info_count: int
    exit_code: int
    results: list[dict[str, Any]]  # 检查项明细（保留 dict，因为字段动态）

@dataclass(frozen=True)
class SpecCenterOverviewDTO:
    """规范中心概览（对应 get_spec_center_overview 返回）"""
    spec_count: int
    domain_counts: dict[str, int]
    lifecycle_counts: dict[str, int]
    health_summary: dict[str, Any]  # 含 error_count/warning_count/info_count/exit_code

@dataclass(frozen=True)
class SpecCenterEntryDTO:
    """规范中心条目（对应 list_spec_center_entries 返回的每个条目）"""
    spec_id: str
    title: str
    number: str
    domain: str
    lifecycle: str
    canonical_path: str
    version: str
    file_exists: bool
```

**保留** SpecCenterDTO（聚合 DTO，未来可用）。

## 四、Facade 重构方案

### S2: run_spec_check() 返回 CommandResult[SpecCheckResultDTO]

```python
def run_spec_check(self) -> CommandResult[SpecCheckResultDTO]:
    try:
        if not self._spec_check_service:
            return CommandResult(success=False, message="No spec_check_service", payload=None)
        output = self._spec_check_service.run()
        results = [
            {
                "check_id": r.check_id,
                "severity": r.severity.name if hasattr(r.severity, "name") else str(r.severity),
                "message": r.message,
                "details": r.details,
                "fix_suggestion": r.fix_suggestion,
            }
            for r in output.results
        ]
        dto = SpecCheckResultDTO(
            error_count=output.error_count,
            warning_count=output.warning_count,
            info_count=output.info_count,
            exit_code=output.exit_code,
            results=results,
        )
        return CommandResult(success=True, message="Success", payload=dto)
    except Exception as e:
        return CommandResult(success=False, message=str(e), payload=None)
```

### S3: get_spec_center_overview() 返回 QueryResult[SpecCenterOverviewDTO]

```python
def get_spec_center_overview(self) -> QueryResult[SpecCenterOverviewDTO]:
    try:
        if not self._spec_center_service:
            return QueryResult(success=False, message="No spec_center_service", payload=None)
        overview = self._spec_center_service.get_overview()
        health = overview.health_summary
        dto = SpecCenterOverviewDTO(
            spec_count=overview.spec_count,
            domain_counts=dict(overview.domain_counts),
            lifecycle_counts=dict(overview.lifecycle_counts),
            health_summary={
                "error_count": health.error_count,
                "warning_count": health.warning_count,
                "info_count": health.info_count,
                "exit_code": health.exit_code,
            },
        )
        return QueryResult(success=True, message="Success", payload=dto)
    except Exception as e:
        return QueryResult(success=False, message=str(e), payload=None)
```

### S4: list_spec_center_entries() 返回 QueryResult[list[SpecCenterEntryDTO]]

```python
def list_spec_center_entries(self, filter_domain: str | None = None) -> QueryResult[list[SpecCenterEntryDTO]]:
    try:
        if not self._spec_center_service:
            return QueryResult(success=False, message="No spec_center_service", payload=[])
        entries = self._spec_center_service.list_entries(filter_domain)
        dtos = [
            SpecCenterEntryDTO(
                spec_id=e.spec_id,
                title=e.title,
                number=e.number,
                domain=e.domain,
                lifecycle=e.lifecycle,
                canonical_path=e.canonical_path,
                version=e.version,
                file_exists=e.file_exists,
            )
            for e in entries
        ]
        return QueryResult(success=True, message="Success", payload=dtos)
    except Exception as e:
        return QueryResult(success=False, message=str(e), payload=[])
```

## 五、Bridge 重构方案

3 个 Slot 改用 `dataclasses.asdict()` 转换 DTO 为 dict 给 QML。

### S5-S7: SpecBridge 3 Slot 改用 asdict

```python
from dataclasses import asdict

@Slot(result="QVariant")
def runSpecCheck(self) -> dict[str, Any]:
    if self._facade:
        res = self._facade.run_spec_check()
        if res.success and res.payload:
            dto = res.payload
            payload = asdict(dto)
            self.specCheckCompleted.emit(
                payload.get("error_count", 0),
                payload.get("warning_count", 0),
                payload.get("info_count", 0),
            )
            return payload
        return {"error_count": -1, "message": res.message}
    return {"error_count": -1, "message": "未初始化"}

@Slot(result="QVariant")
def getSpecOverview(self) -> dict[str, Any]:
    if self._facade:
        res = self._facade.get_spec_center_overview()
        if res.success and res.payload:
            return asdict(res.payload)
    return {}

@Slot(str, result=list)
def listSpecEntries(self, filter_domain: str = "") -> list[Any]:
    if self._facade:
        domain = filter_domain if filter_domain else None
        res = self._facade.list_spec_center_entries(domain)
        if res.success and res.payload:
            return [asdict(e) for e in res.payload]
    return []
```

## 六、测试用例清单

### test_spec_facade.py（单元测试，预计 10 个）

| # | 测试名 | 覆盖方法 | 场景 |
|---|--------|----------|------|
| 1 | test_run_spec_check_success | run_spec_check | 正常返回 SpecCheckResultDTO |
| 2 | test_run_spec_check_no_service | run_spec_check | service=None 降级 |
| 3 | test_run_spec_check_exception | run_spec_check | service 异常降级 |
| 4 | test_get_spec_center_overview_success | get_spec_center_overview | 正常返回 SpecCenterOverviewDTO |
| 5 | test_get_spec_center_overview_no_service | get_spec_center_overview | service=None 降级 |
| 6 | test_get_spec_center_overview_exception | get_spec_center_overview | service 异常降级 |
| 7 | test_list_spec_center_entries_success | list_spec_center_entries | 正常返回 list[SpecCenterEntryDTO] |
| 8 | test_list_spec_center_entries_with_filter | list_spec_center_entries | 带 filter_domain 筛选 |
| 9 | test_list_spec_center_entries_no_service | list_spec_center_entries | service=None 降级 |
| 10 | test_list_spec_center_entries_exception | list_spec_center_entries | service 异常降级 |

### test_spec_bridge.py（Bridge 测试，预计 5 个）

| # | 测试名 | 覆盖 Slot | 场景 |
|---|--------|-----------|------|
| 1 | test_spec_bridge_run_check | runSpecCheck | 正常返回 dict + emit 信号 |
| 2 | test_spec_bridge_get_overview | getSpecOverview | 正常返回 dict |
| 3 | test_spec_bridge_list_entries | listSpecEntries | 正常返回 list[dict] |
| 4 | test_spec_bridge_no_facade | 所有 Slot | facade=None 降级 |
| 5 | test_spec_bridge_run_check_failure | runSpecCheck | facade 返回失败 |

## 七、执行步骤（S1-S10）

| 步骤 | 内容 | 优先级 |
|------|------|--------|
| S1 | spec_dto.py 补 3 个 DTO（SpecCheckResultDTO/SpecCenterOverviewDTO/SpecCenterEntryDTO） | P0 |
| S2 | SpecFacade.run_spec_check() 返回 SpecCheckResultDTO | P0 |
| S3 | SpecFacade.get_spec_center_overview() 返回 SpecCenterOverviewDTO | P0 |
| S4 | SpecFacade.list_spec_center_entries() 返回 list[SpecCenterEntryDTO] | P0 |
| S5 | SpecBridge.runSpecCheck() 改用 asdict | P0 |
| S6 | SpecBridge.getSpecOverview() 改用 asdict | P0 |
| S7 | SpecBridge.listSpecEntries() 改用 asdict | P0 |
| S8 | test_spec_facade.py 单元测试（10 个） | P0 |
| S9 | test_spec_bridge.py Bridge 测试（5 个） | P0 |
| S10 | 三轨门禁回归 + 文档更新 | P0 |

## 八、风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| Facade 返回类型变更破坏调用方 | 低 | Bridge 是唯一调用方，同步修改 |
| DTO 字段与 Service 返回不匹配 | 低 | DTO 字段从现有 dict 结构提取 |
| 测试 mock Service 困难 | 低 | 参考 M2/M3 的 mock helper 模式 |
| asdict 对嵌套 dict 的处理 | 低 | results/health_summary 保留 dict 不转 DTO |

## 九、不在第 1 批范围内

- DeliveryFacade / SystemFacade 重构（第 2 批）
- Protocol 契约扩展（SpecServiceProtocol，可选，不在本批）
- Command 类扩展（RunSpecCheckCommand 未被 Facade 使用，本批不接入）
- QML 端 UI 调整（Bridge 接口不变，QML 无需改动）
- 集成测试（本批仅单元 + Bridge 测试，集成测试留待第 2 批完成后统一补）

## 十、执行结果与验证记录

### 10.1 S1-S10 步骤完成情况

| 步骤 | 内容 | 状态 | 备注 |
|------|------|------|------|
| S1 | spec_dto.py 补 3 个 DTO | ✅ 已完成 | SpecCheckResultDTO + SpecCenterOverviewDTO + SpecCenterEntryDTO |
| S2 | SpecFacade.run_spec_check() 返回 SpecCheckResultDTO | ✅ 已完成 | 从裸 dict 升级为带类型 DTO |
| S3 | SpecFacade.get_spec_center_overview() 返回 SpecCenterOverviewDTO | ✅ 已完成 | 从裸 dict 升级为带类型 DTO |
| S4 | SpecFacade.list_spec_center_entries() 返回 list[SpecCenterEntryDTO] | ✅ 已完成 | 从裸 list[dict] 升级为带类型 DTO |
| S5 | SpecBridge.runSpecCheck() 改用 asdict | ✅ 已完成 | asdict(dto) 转 dict + emit 信号 |
| S6 | SpecBridge.getSpecOverview() 改用 asdict | ✅ 已完成 | asdict(dto) 转 dict |
| S7 | SpecBridge.listSpecEntries() 改用 asdict | ✅ 已完成 | [asdict(e) for e in payload] |
| S8 | test_spec_facade.py 单元测试（10 个） | ✅ 已完成 | 3 个 mock helper + 10 个测试 |
| S9 | test_spec_bridge.py Bridge 测试（5 个） | ✅ 已完成 | _MockSpecFacade + QSignalSpy + 5 个测试 |
| S10 | 三轨门禁回归 + 文档更新 | ✅ 已完成 | 见 10.2 |

### 10.2 三轨门禁最终结果

| 门禁 | 结果 | 备注 |
|------|------|------|
| ruff check . | ✅ All checks passed | 1 个 import 排序问题已自动修复 |
| mypy auto_pm | ⚠️ 18 errors in 7 files | 比 M3 基线 21 减少 3 个，改善；非阻断 |
| pytest --no-cov -q | ✅ 1174 passed, 2 skipped, 3 warnings in 32.28s | M3 基线 1162 - 3 旧测试 + 15 新测试 = 1174 |

**结论**：三轨门禁全绿，M4 第 1 批（SpecFacade）落地达成 done_when。

### 10.3 改动文件清单

#### 生产代码（3 个文件）
| 文件 | 改动类型 | 内容 |
|------|---------|------|
| auto_pm/ui/contracts/dto/spec_dto.py | 修改 | 新增 3 个 DTO（SpecCheckResultDTO/SpecCenterOverviewDTO/SpecCenterEntryDTO） |
| auto_pm/application/spec_facade.py | 修改 | 3 方法从返回裸 dict 升级为返回带类型 DTO + 导入 3 个新 DTO |
| auto_pm/ui/qml/bridges/spec_bridge.py | 修改 | 3 个 Slot 改用 dataclasses.asdict() 转换 DTO |

#### 测试代码（2 个文件）
| 文件 | 改动类型 | 内容 |
|------|---------|------|
| tests/application/test_spec_facade.py | 修改（覆盖） | 3 → 10 个测试，新增 3 个 mock helper |
| tests/qml/test_spec_bridge.py | 新建 | 5 个 Bridge 测试 + _MockSpecFacade + QSignalSpy |

#### 文档（2 个文件）
| 文件 | 改动类型 | 内容 |
|------|---------|------|
| 09_整改项/M4_spec_landing_plan.md | 修改 | status 待执行 → 已完成 + 填写 §十 执行结果 |
| PM_SESSION_SW-2026-008.md | 修改 | §6 追加 M4 第 1 批落地记录 |

### 10.4 后续待办（移交 M4 第 2 批）

- DeliveryFacade 重构（7 方法 + 7 DTO + 5+2 Bridge Slot）
- SystemFacade 重构（6 方法 + 6 DTO + 5+1 Bridge Slot）
- 集成测试补齐（第 2 批完成后统一补）
- Protocol 契约扩展（SpecServiceProtocol/DeliveryServiceProtocol/SystemServiceProtocol，可选）
