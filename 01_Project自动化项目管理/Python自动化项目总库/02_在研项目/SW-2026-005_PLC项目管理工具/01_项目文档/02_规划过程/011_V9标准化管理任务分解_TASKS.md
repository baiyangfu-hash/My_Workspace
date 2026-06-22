# SW-2026-005 V9.0.0 标准化管理 任务分解

> 关联PRD: V9.0.0
> 关联方案: 010_PLC标准化管理功能方案_PLAN.md
> 创建日期: 2026-06-19

## 任务总览

| Phase | 任务数 | 优先级 | 状态 |
|-------|--------|--------|------|
| STD-1 Service层 | 5 | P0 | 进行中 |
| STD-2 Bridge+GUI | 5 | P0 | 待办 |
| STD-3 集成验证 | 3 | P0 | 待办 |

---

## Phase STD-1: Service 层扩展（CLI 优先）

### STD-1.1 扩展 check_workspace 扫描深度和项目识别

**目标**: 覆盖 SysLib/actuator/FB_xxx 三级嵌套项目

**变更文件**:
- `src/services/plc_project_service.py`

**变更点**:
1. `check_workspace(scan_depth=2)` 默认值改为 `scan_depth=4`
2. `_scan_and_check` 增强项目识别逻辑：
   - 现有：.plc.json / PM_SESSION / FB_前缀
   - 新增：.scl文件存在性识别（SysLib FB项目特征）
   - 新增：PRD目录存在性识别
3. CLI `plc-check --all` 默认 depth=4

**验收**: AC-05.4（扫描深度默认4层，覆盖三级嵌套）

---

### STD-1.2 实现 repair_project() 自动修复方法

**目标**: 自动修复 plc-check 发现的 FAIL 项

**变更文件**:
- `src/services/plc_project_service.py`

**新增数据结构**:
```python
@dataclass
class RepairAction:
    item: str
    action: str
    destructive: bool
    status: str  # "fixed" / "skipped" / "failed"
    detail: str

@dataclass
class RepairResult:
    project_path: str
    actions: list[RepairAction]
    fixed_count: int
    skipped_count: int
    failed_count: int
    before_check: CheckResult
    after_check: CheckResult
```

**新增方法**:
```python
def repair_project(self, project_path: str, dry_run: bool = False,
                   rename_confirm: bool = False) -> RepairResult:
    """自动修复项目结构问题"""
```

**修复规则实现**:
1. 先调用 `check_project()` 获取 `before_check`
2. 遍历 `before_check.items`，对每个 FAIL 项执行修复：
   - .plc.json 缺失 → 生成模板（含 libraries 自动计算）
   - .plc.json 字段不完整 → 补全缺失字段
   - PM_SESSION 缺失 → 生成模板
   - PRD 目录缺失 → 创建目录
   - PRD/REQ/INT/DSN/TEC 缺失 → 生成模板文档
   - LSP-907 目录缺失 → 创建标准目录
   - PRD 文档命名非标准 → 重命名（需 `rename_confirm=True`）
3. 破坏性操作（重命名）默认跳过，记录为 `skipped`
4. 重命名前自动备份（.bak 后缀）
5. 修复后调用 `check_project()` 获取 `after_check`

**验收**: AC-07.1~07.8

---

### STD-1.3 实现 standardize_docs() 文档标准化方法

**目标**: 检测并修正 PRD 文档的非标准命名

**变更文件**:
- `src/services/plc_project_service.py`

**新增数据结构**:
```python
@dataclass
class RenamePlan:
    old_path: str
    new_path: str
    doc_type: str  # "REQ" / "INT" / "DSN" / "TEC"
    applied: bool
    backup_path: str

@dataclass
class StandardizeResult:
    project_path: str
    plans: list[RenamePlan]
    applied_count: int
    skipped_count: int
    reference_updates: list[str]
```

**新增方法**:
```python
def standardize_docs(self, project_path: str, apply: bool = False) -> StandardizeResult:
    """检测并修正PRD文档命名"""
```

**命名规范映射**:
```python
NAMING_RULES = {
    "需求分析文档_REQ.md": {
        "prefix": "需求",
        "patterns": [r"需求文档_PRD-.*\.md", r".*_REQ\.md"],
    },
    "接口文档_INT.md": {
        "prefix": "接口",
        "patterns": [r"接口文档_IFC-.*\.md", r".*_INT\.md"],
    },
    "详细设计说明书_DSN.md": {
        "prefix": "详细设计",
        "patterns": [r"详细设计说明书_DSN-.*\.md", r".*_DSN\.md"],
    },
    "技术方案文档_TEC.md": {
        "prefix": "技术方案",
        "patterns": [r"技术方案文档_TEC-.*\.md", r".*_TEC\.md"],
    },
}
```

**实现流程**:
1. 扫描 PRD/ 目录下所有 .md 文件
2. 对每个文件匹配 NAMING_RULES 中的 patterns
3. 生成 RenamePlan（原路径 → 新路径）
4. 若 `apply=True`：
   - 备份原文件（.bak）
   - 执行重命名
   - 扫描文档内容更新关联引用
5. 返回 StandardizeResult

**验收**: AC-08.1~08.4

---

### STD-1.4 CLI 新增 plc-repair / plc-standardize 命令

**目标**: 暴露 repair/standardize 能力到命令行

**变更文件**:
- `src/cli.py`

**新增子命令**:
```python
# plc-repair
subparsers.add_parser("plc-repair", help="自动修复项目结构问题")
# 参数: project_path, --all, --dry-run, --rename-confirm

# plc-standardize
subparsers.add_parser("plc-standardize", help="检测并修正PRD文档命名")
# 参数: project_path, --all, --dry-run, --apply
```

**新增函数**:
- `cmd_plc_repair(args)` - 执行修复并打印结果
- `cmd_plc_standardize(args)` - 执行标准化并打印结果
- `_print_repair_result(result)` - 格式化输出修复结果
- `_print_standardize_result(result)` - 格式化输出标准化结果

**验收**: AC-07.1~07.4, AC-08.1~08.3

---

### STD-1.5 单元测试 repair/standardize 边界用例

**目标**: 验证修复和标准化的边界情况

**变更文件**:
- `tests/test_plc_project_service.py`（新增或扩展）

**测试用例**:
1. `test_repair_missing_plc_json` - 修复缺失的 .plc.json
2. `test_repair_missing_pm_session` - 修复缺失的 PM_SESSION
3. `test_repair_missing_prd_dir` - 修复缺失的 PRD 目录
4. `test_repair_missing_prd_docs` - 修复缺失的 PRD 文档
5. `test_repair_missing_std_dirs` - 修复缺失的标准目录
6. `test_repair_dry_run` - dry-run 模式不实际执行
7. `test_repair_rename_without_confirm` - 未确认时跳过重命名
8. `test_repair_rename_with_confirm` - 确认后执行重命名+备份
9. `test_standardize_detect_only` - 仅检测不执行
10. `test_standardize_apply` - 执行重命名
11. `test_standardize_reference_update` - 更新关联引用
12. `test_check_workspace_depth4` - 扫描深度4层覆盖FB项目

**验收**: 所有测试通过

---

## Phase STD-2: Bridge 层 + GUI 标签页

### STD-2.1 WebViewBridge 新增标准化管理 API

**变更文件**:
- `src/bridge/webview_bridge.py`

**新增API**:
```python
def plc_check_all(self) -> dict
def plc_check_project(self, project_path: str) -> dict
def plc_init_project(self, project_id, project_name, project_type, description) -> dict
def plc_repair_project(self, project_path: str, rename_confirm: bool) -> dict
def plc_standardize_project(self, project_path: str, apply: bool) -> dict
```

**实现要点**:
- 初始化时创建 `self._plc_svc = PlcProjectService(workspace_root)`
- 所有方法通过 `_run_in_thread` 执行，带超时保护
- 返回 dict 格式，便于 JS 消费

---

### STD-2.2 UI 新增 standardize.js 模块和标签页

**变更文件**:
- `ui/index.html` - 导航栏新增「标准化管理」入口
- `ui/js/app.js` - 路由表新增 standardize 路由
- `ui/js/standardize.js` - 新增标准化管理模块（新增）
- `ui/css/style.css` - 新增标准化管理样式

**standardize.js 模块结构**:
```javascript
const StandardizeModule = {
  init() {},
  render() {},
  renderDashboard(stats) {},      // 合规仪表盘
  renderProjectList(results) {},  // 项目列表表格
  renderCheckDetail(result) {},   // 检查详情面板
  onRepairClick(projectPath) {},  // 修复按钮
  onStandardizeClick(projectPath) {}, // 标准化按钮
  onInitClick() {},               // 新建项目向导
};
```

---

### STD-2.3 合规仪表盘 + 项目列表表格

**实现要点**:
- 顶部仪表盘：5个数字卡片（总数/通过/警告/失败/合规率）
- 中部表格：项目名/类型/状态/通过数/警告数/失败数/操作按钮
- 表格行点击展开检查详情

---

### STD-2.4 检查详情面板 + 修复交互

**实现要点**:
- 底部详情面板：逐项显示 pass/warn/fail + 消息
- FAIL 项旁有「修复」按钮
- WARN 项（命名不匹配）旁有「标准化」按钮
- 底部「一键修复全部」按钮
- 破坏性操作弹出确认对话框

---

### STD-2.5 项目初始化向导模态框

**实现要点**:
- 4步向导：类型 → 编号名称 → 库引用 → 确认
- Step 3 显示 dry-run 预览
- Step 4 执行创建并刷新列表

---

## Phase STD-3: 集成验证

### STD-3.1 全量扫描+修复验证

**目标**: 对 `0100_PLC自动化/` 全量验证

**步骤**:
1. `plc-check --all` 扫描所有项目，记录修复前合规率
2. `plc-repair --all` 批量修复
3. `plc-check --all` 重新扫描，记录修复后合规率
4. 验证合规率 ≥80%

---

### STD-3.2 GUI E2E 测试

**目标**: 标准化管理全流程 GUI 验证

**步骤**:
1. 启动 GUI，切换到「标准化管理」标签页
2. 验证仪表盘显示正确
3. 点击项目展开详情
4. 点击「修复」按钮验证修复交互
5. 点击「新建项目」验证向导

---

### STD-3.3 PLC 技能集成验证

**目标**: 验证 PLC 技能自动调用 plc-check

**步骤**:
1. 触发 PLC 技能规范检查任务
2. 验证技能自动调用 `plc-check` CLI
3. 验证技能整合结果到验证报告
4. 验证上下文消耗降低

---

## 执行顺序

```
STD-1.1 → STD-1.2 → STD-1.3 → STD-1.4 → STD-1.5
                                                ↓
STD-2.1 → STD-2.2 → STD-2.3 → STD-2.4 → STD-2.5
                                                ↓
STD-3.1 → STD-3.2 → STD-3.3
```

**当前进度**: STD-1.1 进行中
