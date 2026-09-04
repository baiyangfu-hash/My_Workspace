# 技术方案文档

## 文档基础信息

| 字段 | 值 |
|------|-----|
| 项目编号 | SW-2026-006 |
| 版本 | V1.1.0 |
| 日期 | 2026-05-25 |

---

## 1. 架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────┐
│                 Presentation Layer                    │
│  ┌───────────────────┐   ┌────────────────────────┐  │
│  │   CLI (click)      │   │   GUI (PySide6)        │  │
│  │   specmgr check    │   │   specmgr gui          │  │
│  │   specmgr index    │   │   仪表盘/检查/索引/...  │  │
│  │   specmgr front... │   │                        │  │
│  │   specmgr report   │   │                        │  │
│  └────────┬──────────┘   └───────────┬────────────┘  │
└───────────┼──────────────────────────┼───────────────┘
            │                          │
┌───────────▼──────────────────────────▼───────────────┐
│                  Service Layer                        │
│  services/check_svc.py      - 健康检查服务            │
│  services/index_svc.py      - 索引生成服务            │
│  services/frontmatter_svc.py - Frontmatter管理服务    │
│  services/report_svc.py     - 报告生成服务            │
└──────────────────────────┬───────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────┐
│                    Core Layer                         │
│  core/registry.py      - 注册表读写/查询              │
│  core/scanner.py       - 规范文件扫描                 │
│  core/checker_base.py  - 检查器基类 + 8个检查器       │
│  core/config.py        - 工作空间配置                 │
└──────────────────────────┬───────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────┐
│                    Data Layer                         │
│  spec_registry.json  - 规范注册表(唯一真相源)         │
│  规范文件(.md)       - 各目录下的规范文件              │
└──────────────────────────────────────────────────────┘
```

### 1.2 目录结构

```
SW-2026-006_规范管理工具/
├── 01_需求与设计/
│   ├── 01-产品需求文档_PRD-V1.1.0.md
│   └── 02-技术方案文档_DES-V1.1.0.md
├── 02_源代码/
│   ├── specmgr/
│   │   ├── __init__.py              # 版本号
│   │   ├── cli.py                   # click CLI入口
│   │   ├── gui.py                   # GUI入口 (specmgr gui)
│   │   ├── commands/                # CLI命令层 (调用services)
│   │   │   ├── __init__.py
│   │   │   ├── check.py            # specmgr check
│   │   │   ├── index.py            # specmgr index
│   │   │   ├── frontmatter.py      # specmgr frontmatter
│   │   │   └── report.py           # specmgr report
│   │   ├── services/                # 业务服务层
│   │   │   ├── __init__.py
│   │   │   ├── check_svc.py        # 检查服务
│   │   │   ├── index_svc.py        # 索引服务
│   │   │   ├── frontmatter_svc.py  # Frontmatter服务
│   │   │   └── report_svc.py       # 报告服务
│   │   ├── gui/                     # GUI模块
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py      # 主窗口(侧边栏+内容区)
│   │   │   ├── dashboard.py        # 仪表盘页
│   │   │   ├── check_page.py       # 健康检查页
│   │   │   ├── index_page.py       # 索引生成页
│   │   │   ├── frontmatter_page.py # Frontmatter管理页
│   │   │   ├── report_page.py      # 报告生成页
│   │   │   ├── settings_page.py    # 设置页
│   │   │   ├── models.py           # Qt数据模型(QAbstractTableModel)
│   │   │   └── workers.py          # QThread工作线程
│   │   └── core/                    # 核心层 (已有)
│   │       ├── __init__.py
│   │       ├── registry.py         # 注册表读写
│   │       ├── scanner.py          # 规范文件扫描
│   │       ├── checker_base.py     # 检查器基类
│   │       └── config.py           # 工作空间配置
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py             # pytest fixtures
│   │   ├── test_registry.py
│   │   ├── test_scanner.py
│   │   ├── test_check.py
│   │   ├── test_index.py
│   │   ├── test_frontmatter.py
│   │   ├── test_report.py
│   │   └── test_services.py        # Service层测试
│   ├── pyproject.toml
│   └── README.md
├── 03_交付/
│   └── dist/                        # PyInstaller输出目录
└── PM_SESSION_SW-2026-006.md
```

## 2. 技术选型

| 组件 | 选型 | 理由 |
|------|------|------|
| CLI框架 | **click** | 比argparse更简洁，支持子命令、选项、彩色输出；轻量 |
| GUI框架 | **PySide6** | Qt官方Python绑定，LGPL协议可商用，比PyQt6许可友好 |
| 数据格式 | JSON (spec_registry.json) | 机器可读，Python标准库支持，与现有格式兼容 |
| 测试框架 | pytest | 项目标准，已有conftest.py模式 |
| 包管理 | pyproject.toml | 现代Python打包标准，支持pip install -e . |
| 打包工具 | **PyInstaller** | 成熟稳定，支持单文件exe，支持PySide6 |
| 异步处理 | **QThread + Signal/Slot** | Qt原生异步机制，GUI中耗时操作不阻塞UI |
| Python版本 | >=3.9 | 与SW-2026-005保持一致 |

## 3. 核心模块设计

### 3.1 core/registry.py — 注册表管理

```python
class SpecRegistry:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.path = workspace / "00_Obsidian_Base全局规范文件仓库" / "spec_registry.json"
        self.data: dict = {}

    def load(self) -> bool: ...
    def save(self) -> None: ...
    def get_spec(self, spec_id: str) -> Optional[SpecInfo]: ...
    def list_specs(self, domain: str = None, lifecycle: str = None) -> List[SpecInfo]: ...
    def add_spec(self, spec_id: str, info: SpecInfo) -> None: ...
    def update_spec(self, spec_id: str, info: SpecInfo) -> None: ...
    def get_deprecated(self) -> List[SpecInfo]: ...
    def get_replacement_chain(self, spec_id: str) -> List[str]: ...

@dataclass
class SpecInfo:
    spec_id: str
    title: str
    number: str
    canonical_path: str
    version: str
    type_prefix: str
    domain: str
    lifecycle: str
    sub_domain: str
    tags: List[str]
    replaces: List[str]
    replaced_by: List[str]
```

### 3.2 core/scanner.py — 规范文件扫描

```python
class SpecScanner:
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def scan_all(self) -> Dict[str, List[Path]]: ...
    def scan_by_domain(self, domain: str) -> List[Path]: ...
    def extract_version(self, file_path: Path) -> Optional[str]: ...
    def extract_frontmatter(self, file_path: Path) -> Optional[dict]: ...
    def find_duplicates(self) -> Dict[str, List[Path]]: ...
```

### 3.3 core/checker_base.py — 检查器基类

```python
class Severity(IntEnum):
    ERROR = 3
    WARNING = 2
    INFO = 1

@dataclass
class CheckResult:
    check_id: str
    severity: Severity
    message: str
    details: str = ""
    fix_suggestion: str = ""

class BaseChecker(ABC):
    @abstractmethod
    def check(self, registry: SpecRegistry, scanner: SpecScanner) -> List[CheckResult]: ...

class HealthChecker:
    def __init__(self, workspace: Path):
        self.registry = SpecRegistry(workspace)
        self.scanner = SpecScanner(workspace)
        self.checkers: List[BaseChecker] = []

    def register(self, checker: BaseChecker) -> None: ...
    def run_all(self) -> List[CheckResult]: ...
    def run_by_id(self, check_id: str) -> List[CheckResult]: ...
```

### 3.4 Service层设计（V0.2.0新增）

Service层从Commands中提取业务逻辑，使其可被CLI和GUI共同调用。每个Service方法返回结构化数据，不直接进行I/O输出。

#### 3.4.1 services/check_svc.py — 检查服务

```python
@dataclass
class CheckOutput:
    results: list[CheckResult]
    error_count: int
    warning_count: int
    info_count: int
    exit_code: int

class CheckService:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.config = WorkspaceConfig(workspace=workspace)
        self.registry = SpecRegistry(workspace)
        self.scanner = SpecScanner(workspace, self.config)
        self.checker = HealthChecker()

    def run(
        self,
        check_ids: list[str] | None = None,
        min_severity: Severity = Severity.INFO,
    ) -> CheckOutput:
        """运行检查，返回结构化结果"""
        if check_ids:
            results = []
            for cid in check_ids:
                results.extend(self.checker.run_by_id(cid, self.registry, self.scanner))
        else:
            results = self.checker.run_all(self.registry, self.scanner)
        filtered = [r for r in results if r.severity >= min_severity]
        error_count = sum(1 for r in filtered if r.severity == Severity.ERROR)
        warning_count = sum(1 for r in filtered if r.severity == Severity.WARNING)
        info_count = sum(1 for r in filtered if r.severity == Severity.INFO)
        exit_code = 1 if error_count else (2 if warning_count else 0)
        return CheckOutput(
            results=filtered,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            exit_code=exit_code,
        )
```

#### 3.4.2 services/index_svc.py — 索引服务

```python
@dataclass
class IndexOutput:
    generated_files: list[Path]
    errors: list[str]

class IndexService:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.config = WorkspaceConfig(workspace=workspace)

    def run(self, domains: list[str] | None = None) -> IndexOutput:
        """生成索引文件，返回生成结果"""
        ...
```

#### 3.4.3 services/frontmatter_svc.py — Frontmatter服务

```python
@dataclass
class FrontmatterItem:
    spec_id: str
    file_path: Path
    has_frontmatter: bool
    new_frontmatter: str
    status: str

@dataclass
class FrontmatterOutput:
    items: list[FrontmatterItem]
    modified_count: int
    skipped_count: int
    error_count: int

class FrontmatterService:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.config = WorkspaceConfig(workspace=workspace)

    def preview(self, spec_id: str | None = None) -> list[FrontmatterItem]:
        """预览需要添加frontmatter的文件列表"""
        ...

    def apply(self, items: list[FrontmatterItem]) -> FrontmatterOutput:
        """执行frontmatter添加"""
        ...
```

#### 3.4.4 services/report_svc.py — 报告服务

```python
@dataclass
class ReportOutput:
    content: str
    output_path: Path
    format: str

class ReportService:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.config = WorkspaceConfig(workspace=workspace)

    def generate(
        self,
        fmt: str = "markdown",
        output_path: Path | None = None,
    ) -> ReportOutput:
        """生成报告，返回内容和路径"""
        ...
```

### 3.5 Commands层重构（V0.2.0）

Commands层重构为薄壳，仅负责CLI参数解析和输出格式化，业务逻辑委托给Service层。

```python
# commands/check.py (重构后)
@click.command()
@click.option("--workspace", "-w", required=True)
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
@click.option("--check-id", "-c", multiple=True)
@click.option("--severity", type=click.Choice(["error", "warning", "info"]), default="info")
def check(workspace: str, fmt: str, check_id: tuple[str, ...], severity: str) -> None:
    """运行规范健康检查"""
    svc = CheckService(Path(workspace))
    output = svc.run(
        check_ids=list(check_id) or None,
        min_severity=Severity[severity.upper()],
    )
    if fmt == "json":
        _output_json(output.results)
    else:
        _output_table(output.results)
    sys.exit(output.exit_code)
```

### 3.6 GUI模块设计（V0.3.0新增）

#### 3.6.1 gui/main_window.py — 主窗口

```python
class MainWindow(QMainWindow):
    def __init__(self, workspace: Path) -> None:
        super().__init__()
        self.setWindowTitle("SpecMgr - 规范管理工具")
        self.resize(1200, 800)
        self.workspace = workspace

        self._setup_sidebar()
        self._setup_stack()
        self._setup_statusbar()

    def _setup_sidebar(self) -> None:
        """左侧导航栏：仪表盘/检查/索引/Frontmatter/报告/设置"""
        ...

    def _setup_stack(self) -> None:
        """右侧QStackedWidget，切换各页面"""
        ...

    def _setup_statusbar(self) -> None:
        """底部状态栏：工作空间路径、最后检查时间"""
        ...
```

#### 3.6.2 gui/dashboard.py — 仪表盘页

```python
class DashboardPage(QWidget):
    def __init__(self, workspace: Path) -> None:
        super().__init__()
        self.workspace = workspace
        self._build_ui()

    def _build_ui(self) -> None:
        """统计卡片 + 最近检查结果摘要"""
        ...

    def refresh(self) -> None:
        """重新加载注册表数据，更新统计"""
        ...
```

#### 3.6.3 gui/check_page.py — 健康检查页

```python
class CheckPage(QWidget):
    check_started = Signal()
    check_finished = Signal(object)

    def __init__(self, workspace: Path) -> None:
        super().__init__()
        self.workspace = workspace
        self._build_ui()

    def _build_ui(self) -> None:
        """运行按钮 + 严重级别筛选 + 结果表格 + 详情面板"""
        ...

    def _run_check(self) -> None:
        """启动QThread执行检查"""
        worker = CheckWorker(self.workspace)
        worker.finished.connect(self._on_check_finished)
        worker.start()

    def _on_check_finished(self, output: CheckOutput) -> None:
        """检查完成，更新表格"""
        ...
```

#### 3.6.4 gui/models.py — Qt数据模型

```python
class CheckResultModel(QAbstractTableModel):
    """检查结果表格模型"""
    COLUMNS = ["检查项", "严重级别", "消息", "详情"]

    def __init__(self, results: list[CheckResult] | None = None) -> None:
        super().__init__()
        self._results = results or []

    def update_results(self, results: list[CheckResult]) -> None:
        self.beginResetModel()
        self._results = results
        self.endResetModel()

    def data(self, index, role) -> Any: ...
    def rowCount(self, parent=QModelIndex()) -> int: ...
    def columnCount(self, parent=QModelIndex()) -> int: ...
```

#### 3.6.5 gui/workers.py — QThread工作线程

```python
class CheckWorker(QThread):
    finished = Signal(object)

    def __init__(self, workspace: Path, check_ids: list[str] | None = None) -> None:
        super().__init__()
        self.workspace = workspace
        self.check_ids = check_ids

    def run(self) -> None:
        svc = CheckService(self.workspace)
        output = svc.run(check_ids=self.check_ids)
        self.finished.emit(output)


class IndexWorker(QThread):
    finished = Signal(object)

    def __init__(self, workspace: Path, domains: list[str] | None = None) -> None:
        super().__init__()
        self.workspace = workspace
        self.domains = domains

    def run(self) -> None:
        svc = IndexService(self.workspace)
        output = svc.run(domains=self.domains)
        self.finished.emit(output)
```

#### 3.6.6 GUI入口 gui.py

```python
def launch_gui(workspace: Path | None = None) -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("SpecMgr")
    app.setStyle("Fusion")

    if workspace is None:
        workspace = Path(".").resolve()

    window = MainWindow(workspace)
    window.show()
    sys.exit(app.exec())
```

CLI入口新增gui子命令：

```python
# cli.py 新增
from specmgr.gui import launch_gui

@cli.command()
@click.option("--workspace", "-w", help="工作空间根目录")
def gui(workspace: str | None) -> None:
    """启动GUI界面"""
    ws = Path(workspace) if workspace else None
    launch_gui(ws)
```

## 4. CLI入口设计

```python
# cli.py
@click.group()
@click.version_option(version="0.1.0")
@click.option("--workspace", "-w", envvar="SPECMGR_WORKSPACE", help="工作空间根目录")
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
@click.pass_context
def cli(ctx, workspace, verbose):
    """SpecMgr - 规范管理体系一站式管理工具"""
    ctx.ensure_object(dict)
    ctx.obj["workspace"] = workspace
    ctx.obj["verbose"] = verbose

cli.add_command(check)
cli.add_command(index)
cli.add_command(frontmatter)
cli.add_command(report)
cli.add_command(gui)
```

使用示例：
```bash
# CLI模式
specmgr check -w "c:\Users\fubai\Desktop\My_Workspace"
specmgr check -w . --format json
specmgr index -w . --domain plc
specmgr frontmatter -w . --dry-run
specmgr report -w .

# GUI模式
specmgr gui
specmgr gui -w "c:\Users\fubai\Desktop\My_Workspace"
```

## 5. 配置文件设计

`specmgr.yaml`（可选，不创建则使用命令行参数或默认值）：

```yaml
workspace: "c:\\Users\\fubai\\Desktop\\My_Workspace"
registry_path: "00_Obsidian_Base全局规范文件仓库/spec_registry.json"
spec_dirs:
  - "00_Obsidian_Base全局规范文件仓库/01_项目管理域"
  - "0100_PLC自动化/00_通用规范"
  - "01_Project自动化项目管理/00_通用规范"
archive_dir: "00_Obsidian_Base全局规范文件仓库/_archive"
output:
  pm_index: "00_Obsidian_Base全局规范文件仓库/00_INDEX_全局规范索引_V2.0.0.md"
  plc_readme: "0100_PLC自动化/00_通用规范/README.md"
  python_readme: "01_Project自动化项目管理/00_通用规范/README.md"
  report: "00_Obsidian_Base全局规范文件仓库/规范元数据汇总报告.md"
gui:
  window_width: 1200
  window_height: 800
  remember_geometry: true
```

## 6. 迁移策略

从00_Obsidian_Base中的4个脚本迁移到specmgr：

| 原脚本 | 迁移目标 | 处理方式 |
|--------|----------|----------|
| spec_health_checker.py | commands/check.py + core/checker_base.py | 重构为模块化检查器 |
| generate_index.py | commands/index.py | 直接迁移，微调接口 |
| add_frontmatter.py | commands/frontmatter.py | 直接迁移，微调接口 |
| generate_metadata_report.py | commands/report.py | 直接迁移，微调接口 |
| spec_registry.json | 保留原位置，specmgr通过路径引用 | 不移动 |

迁移后，原脚本头部添加废弃声明：
```python
# ⚠️ 此脚本已废弃，请使用 specmgr CLI工具
# 安装: pip install -e <specmgr路径>
# 用法: specmgr check --workspace <path>
```

## 7. 测试策略

| 测试类型 | 范围 | 工具 |
|----------|------|------|
| 单元测试 | core/ + services/ | pytest + tmp_path fixture |
| 集成测试 | commands/ 全流程 | pytest + 临时workspace |
| CLI测试 | click.testing.CliRunner | pytest |
| GUI测试 | 关键交互流程 | pytest-qt |
| 回归测试 | 确保迁移后行为与原脚本一致 | pytest |
| 打包测试 | exe运行验证 | 手动测试 |

测试用例关键场景：
- 空workspace（无注册表）
- 注册表JSON格式错误
- 规范文件版本漂移
- Obsidian链接断裂
- frontmatter已存在/不存在
- dry-run模式不修改文件
- Service层返回结构化数据
- GUI启动和页面切换

## 8. 依赖清单

```toml
[project]
name = "specmgr"
version = "0.1.0"
description = "规范管理体系一站式管理工具（CLI + GUI）"
requires-python = ">=3.9"
dependencies = [
    "click>=8.0",
    "PySide6>=6.5",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-qt>=4.0",
]
pack = [
    "pyinstaller>=6.0",
]

[project.scripts]
specmgr = "specmgr.cli:cli"
```

运行时依赖3个（click + PySide6 + pyyaml），保持轻量。

## 9. 打包方案（V0.5.0）

### 9.1 PyInstaller配置

```python
# specmgr.spec (PyInstaller spec文件)
a = Analysis(
    ['specmgr/gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['specmgr.core', 'specmgr.services', 'specmgr.gui'],
    name='SpecMgr',
    console=False,
    icon='specmgr/gui/assets/icon.ico',
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SpecMgr',
    debug=False,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    name='SpecMgr',
)
```

### 9.2 打包命令

```bash
pyinstaller specmgr.spec --clean --noconfirm
```

### 9.3 打包注意事项

- PySide6需要排除不必要的Qt模块（QtWebEngine等）以控制体积
- 使用`console=False`隐藏控制台窗口
- 需要提供应用图标(icon.ico)
- 打包后需在干净Windows环境验证
