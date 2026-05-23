# SW-2026-005 PLC项目管理工具 — 业务逻辑与功能域详细文档

**文档版本**: V1.0  
**审查日期**: 2026-05-23  
**关联文档**: GUI技术架构审查报告_V1.0.md  
**输出类型**: 纯业务逻辑分析（不含代码修改）

---

## 0. 文档概述

### 0.1 目的

本文档从**业务逻辑角度**全面描述SW-2026-005 PLC项目管理工具的：
- 各功能域的完整业务流程
- 数据模型与状态机
- GUI交互→Service层调用链
- 异常处理策略
- 边界条件与校验规则

### 0.2 功能域总览

| 功能域ID | 名称 | 优先级 | 完成度 | 复杂度 |
|----------|------|--------|--------|--------|
| F01 | 项目管理 | P0 | 90% | 中 |
| F02 | 文档生成 | P0 | 95% | 高 |
| F03 | 变更管理-Sync | P0 | 98% | 高 |
| F04 | 规范检查 | P0 | 95% | 中 |
| F05 | 诊断分析 | P1 | 85% | 高 |
| F06 | ST编辑器 | P2 | 70% | 低 |
| F07 | 仪表盘 | P1 | 85% | 低 |
| F08 | **变更管理-变更单UI** | **P0** | **95%** | **高** ⭐ |

---

## 1. F08: 变更管理-变更单UI (核心功能) ⭐

### 1.1 功能定位

**用户故事**: 作为PLC项目管理者，我希望在GUI中直观地查看、创建、审核和管理变更请求，以便追踪项目变更的全生命周期。

**核心价值**: 将变更管理从命令行/文件操作提升为可视化GUI工作流。

### 1.2 数据模型

#### 1.2.1 ChangeRequest (变更请求实体)

```python
# 来源: src/models/change_request.py
class ChangeRequest:
    change_id: str          # 变更单唯一编号 (如 "CHG-20260523-001")
    title: str              # 变更标题
    description: str        # 详细描述
    category: ChangeCategory # 变更分类枚举
    status: ChangeStatus     # 当前状态枚举
    created_at: str          # 创建时间
    updated_at: str          # 最后更新时间
    approver: str | None     # 审核人 (仅APPROVED后)
    affected_paths: List[str] # 影响的文件路径列表
```

#### 1.2.2 ChangeStatus (状态枚举)

```python
# 来源: src/core/constants.py
class ChangeStatus(Enum):
    DRAFT = "draft"           # 草稿 - 初始状态
    REVIEW = "review"         # 审核中 - 提交审核
    APPROVED = "approved"     # 已批准 - 审核通过
    ANALYZING = "analyzing"   # 分析中 - 技术分析
    IN_PROGRESS = "in_progress" # 进行中 - 实施中
    IMPLEMENTED = "implemented" # 已实施 - 代码完成
    VERIFYING = "verifying"   # 验证中 - 测试验证
    COMPLETED = "completed"   # 已完成 - 验证通过
    CANCELLED = "cancelled"   # 已取消 - 终止流程
```

#### 1.2.3 ChangeCategory (分类枚举)

```python
class ChangeCategory(Enum):
    DOCU = "DOCU"  # 文档变更
    PLC = "PLC"    # PLC程序变更
    HMI = "HMI"    # HMI界面变更
    ELEC = "ELEC"  # 电气变更
    SAFE = "SAFE"  # 安全变更
    MECH = "MECH"  # 机械变更
    SCPT = "SCPT"  # 脚本/配置变更
```

### 1.3 状态机 (State Machine)

#### 1.3.1 状态转换图

```
                    ┌─────────────┐
                    │   DRAFT     │ ← 初始状态
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │  REVIEW  │  │CANCELLED │  │          │
       │ (审核中)  │  │(已取消)  │  │          │
       └────┬─────┘  └──────────┘  │          │
            │                      │          │
      ┌─────┴─────┐               │          │
      │           │               │          │
      ▼           ▼               │          │
┌──────────┐ ┌────────┐          │          │
│ APPROVED  │ │ DRAFT  │          │          │
│(已批准)   │ │(退回草稿)│         │          │
└────┬─────┘ └────────┘          │          │
     │                           │          │
     ├──────────┬───────────────┤          │
     │          │               │          │
     ▼          ▼               │          │
┌──────────┐ ┌─────────────┐    │          │
│ ANALYZING │ │  CANCELLED  │    │          │
│(分析中)   │ │  (已取消)    │    │          │
└────┬─────┘ └─────────────┘    │          │
     │                           │          │
     ▼                           │          │
┌──────────────┐                 │          │
│ IN_PROGRESS  │                 │          │
│(进行中)       │                 │          │
└────┬─────────┘                 │          │
     │                           │          │
     ▼                           │          │
┌──────────────┐                 │          │
│ IMPLEMENTED  │                 │          │
│(已实施)       │                 │          │
└────┬─────────┘                 │          │
     │                           │          │
     ▼                           │          │
┌──────────────┐                 │          │
│  VERIFYING   │                 │          │
│(验证中)       │                 │          │
└────┬─────────┘                 │          │
     │                           │          │
     ├──────────┐                │          │
     │          │                │          │
     ▼          ▼                │          │
┌──────────┐ ┌─────────────┐    │          │
│COMPLETED │ │ IN_PROGRESS  │    │          │
│(已完成)   │ │(退回进行中)   │    │          │
└──────────┘ └─────────────┘    │          │
                                   │          │
                              终态 │          │
```

#### 1.3.2 valid_transitions() 实现

```python
# 有效转换规则表
transitions = {
    DRAFT: [REVIEW, CANCELLED],
    REVIEW: [APPROVED, DRAFT, CANCELLED],
    APPROVED: [ANALYZING, IN_PROGRESS, CANCELLED],
    ANALYZING: [IN_PROGRESS, CANCELLED],
    IN_PROGRESS: [IMPLEMENTED, CANCELLED],
    IMPLEMENTED: [VERIFYING],
    VERIFYING: [COMPLETED, IN_PROGRESS],  # 可退回重测
    COMPLETED [],                       # 终态
    CANCELLED [],                       # 终态
}
```

**关键设计决策**:
- ✅ 从VERIFYING可退回到IN_PROGRESS (允许修复bug后重新验证)
- ❌ COMPLETED和CANCELLED为终态，无出边
- ✅ 从REVIEW可退回DRAFT (允许补充信息)

### 1.4 GUI交互流程

#### 1.4.1 面板初始化流程

```
MainWindow.__init__()
    ↓
_build_right_panel()
    ↓
RightPanelBuilder._create_change_management_tab()
    ↓
ChangeManagementPanel.__init__()
    ↓
_setup_ui()
    ├── 创建工具栏 (新建/刷新按钮)
    ├── 创建QTableWidget (5列, 0行)
    ├── 创建详情区域 (标题+内容+操作按钮)
    └── _update_action_buttons(None) → 禁用所有操作按钮
    ↓
[面板就绪，等待数据]
```

#### 1.4.2 项目绑定与数据加载

```
用户打开项目 (通过菜单/仪表盘/项目树)
    ↓
EventBus.project_opened.emit(path)
    ↓
MainWindow._on_project_opened(path)
    ↓
_change_mgmt_panel.set_project_path(path)
    ↓
ChangeManagementPanel.set_project_path()
    ├── self._project_path = path
    └── self.refresh()
        ↓
    refresh():
    ├── _table.setRowCount(0)  // 清空表格
    ├── 检查 project_path (为空则显示"请先打开项目")
    ↓
    try:
    │   requests = ChangeService.list_change_requests(project_path)
    │   ↓
    │   遍历requests列表:
    │   ├── 插入行 → 设置5列数据
    │   └── 状态列应用颜色编码 + 加粗字体
    │
    except Exception as e:
    │   显示"加载失败"
    │
    更新详情标题: "共 N 个变更单"
```

#### 1.4.3 新建变更单流程

```
用户点击 [📝 新建变更单] 按钮
    ↓
_on_create():
    ├── 检查 project_path (为空则警告返回)
    ↓
[步骤1] 选择变更分类
QInputDialog.getItem(
    title: "新建变更单",
    label: "选择变更分类:",
    items: ["DOCU", "PLC", "HMI", "ELEC", "SAFE", "MECH", "SCPT"]
)
    ↓ 用户取消? → 返回
    ↓
[步骤2] 输入变更标题
QInputDialog.getText(
    title: "新建变更单",
    label: "变更标题:"
)
    ↓ 用户取消 或 标题为空? → 返回
    ↓
[步骤3] 输入变更描述 (可选)
QInputDialog.getText(
    title: "新建变更单",
    label: "变更描述(可选):"
)
    ↓
try:
    category_enum = ChangeCategory(category)
    req, error = ChangeService.create_change_request(
        project_path,
        category_enum,
        title.strip(),
        description.strip() if ok else ""
    )
    ↓
    if error:
        QMessageBox.warning("⚠️ 创建失败", error)
        return
    
    self.refresh()  // 刷新列表
    self.status_changed.emit()  // 通知外部
    QMessageBox.information("✅ 成功", f"变更单 {req.change_id} 已创建")
    
except Exception as e:
    QMessageBox.critical("❌ 错误", f"创建变更单失败: {e}")
```

#### 1.4.4 行选中与详情查看

```
用户点击表格某一行
    ↓
_table.cellClicked(row, col) → _on_row_selected(row)
    ↓
_on_row_selected(row):
    ├── row < 0?
    │   ├── 清空当前选中ID
    │   ├── 清空详情内容
    │   ├── 禁用所有操作按钮
    │   └── return
    │
    ├── 获取ID列的QTableWidgetItem
    │   └── 为空? → return
    │
    ├── self._current_change_id = id_item.text()
    ├── emit change_request_selected(change_id, project_path)
    │
    ├── 解析当前行的状态值 (显示文本 → 枚举值查找)
    │   └── 遍历 STATUS_DISPLAY 反向匹配
    │
    ├── _update_action_buttons(current_status)
    │   └── 基于valid_transitions动态启用/禁用按钮
    │
    └── _load_change_detail(change_id)
        ↓
        file_path = ChangeService._find_change_file(project_path, change_id)
        ↓ 文件不存在?
        → 显示 "<p style='color:#9E9E9E'>文件未找到</p>"
        
        content = file_path.read_text(encoding="utf-8")
        _detail_content.setPlainText(content)
```

#### 1.4.5 审核批准流程

```
用户点击 [✅ 批准] 按钮 (仅在有效时启用)
    ↓
_on_approve():
    ├── 检查 _current_change_id 和 _project_path (为空则return)
    ↓
[输入审核人]
QInputDialog.getText(
    title: "审核通过",
    label: "审核人姓名:"
)
    ↓ 用户取消? → return
    ↓
try:
    success = ChangeService.approve_change_request(
        project_path,
        _current_change_id,
        approver.strip() if approver else ""
    )
    ↓
    if success:
        self.refresh()
        self.status_changed.emit()
        QMessageBox.information("✅ 成功", "变更单已审核通过")
    
    else:
        QMessageBox.warning("⚠️ 失败", "审核操作未成功，请检查变更单状态")
        
except Exception as e:
    QMessageBox.critical("❌ 错误", f"审核操作失败: {e}")
```

**业务规则**: `approve_change_request()` 内部会校验 valid_transitions，只有当前状态允许转换到APPROVED时才执行。

#### 1.4.6 状态推进流程

```
用户点击 [⏩ 推进] 按钮
    ↓
_on_advance():
    ├── 检查 _current_change_id 和 _project_path
    ↓
    file_path = ChangeService._find_change_file(...)
    ↓ 文件不存在? → return
    
    current_status = ChangeService._read_status(file_path)
    current_enum = ChangeService._status_from_value(current_status)
    ↓ 无法解析? → return
    
    valid_next = ChangeStatus.valid_transitions(current_enum)
    ↓
    [过滤推进选项]
    advance_options = [
        s for s in valid_next 
        if s not in (CANCELLED, APPROVED)  // 排除取消和批准(有独立按钮)
    ]
    ↓ 无可用选项?
    → QMessageBox.information("ℹ️ 提示", "当前状态无可推进的目标状态")
    
    [构建选项列表]
    options = [
        f"{STATUS_DISPLAY[s.value]} ({s.value})" for s in advance_options
    ]
    ↓
[用户选择目标状态]
QInputDialog.getItem(
    title: "推进状态",
    label: "选择目标状态:",
    items: options
)
    ↓ 用户取消? → return
    
    [解析选择结果]
    target_value = choice.split("(")[-1].rstrip(")")  // 提取枚举值
    target_enum = ChangeService._status_from_value(target_value)
    ↓ 无法解析? → return
    
    try:
        success = ChangeService.update_status(
            project_path, _current_change_id, target_enum
        )
        ↓ (同上: 刷新+通知+提示)
```

#### 1.4.7 取消变更单流程

```
用户点击 [❌ 取消] 按钮
    ↓
_on_cancel():
    ├── 检查 _current_change_id 和 _project_path
    ↓
[二次确认]
QMessageBox.question(
    title: "❓ 确认取消",
    text: f"确定要取消变更单 {_current_change_id} 吗?",
    buttons: Yes | No, default: No
)
    ↓ 用户选No? → return
    
    try:
        success = ChangeService.update_status(
            project_path, _current_change_id, ChangeStatus.CANCELLED
        )
        ↓ (同上: 刷新+通知+提示)
```

### 1.5 Service层接口

#### 1.5.1 ChangeService 公开API

```python
class ChangeService:
    @classmethod
    def list_change_requests(project_path: str) -> List[ChangeRequest]:
        """列出项目的所有变更单"""
        # 扫描 <project>/changes/ 目录
        # 解析每个 .json 文件为 ChangeRequest 对象
        # 返回按时间倒序排列的列表
    
    @classmethod
    def create_change_request(
        project_path: str,
        category: ChangeCategory,
        title: str,
        description: str = ""
    ) -> Tuple[Optional[ChangeRequest], Optional[str]]:
        """创建新变更单"""
        # 生成 change_id (CHG-YYYYMMDD-NNN)
        # 创建 JSON 文件
        # 返回 (ChangeRequest实例, None) 或 (None, 错误消息)
    
    @classmethod
    def update_status(
        project_path: str,
        change_id: str,
        new_status: ChangeStatus
    ) -> bool:
        """更新变更单状态"""
        # 校验 valid_transitions
        # 更新 JSON 文件中的 status 字段
        # 更新 updated_at 时间戳
        # 返回 True/False
    
    @classmethod
    def approve_change_request(
        project_path: str,
        change_id: str,
        approver: str
    ) -> bool:
        """审核批准变更单"""
        # 校验当前状态允许转换到 APPROVED
        # 更新 status = "approved"
        # 记录 approver 和 approved_at
        # 返回 True/False
    
    # 以下为私有方法 (被GUI直接调用):
    @staticmethod
    def _find_change_file(project_path, change_id) -> Optional[Path]:
        """定位变更单文件路径"""
    
    @staticmethod
    def _read_status(file_path: Path) -> str:
        """读取当前状态值"""
    
    @staticmethod
    def _status_from_value(value: str) -> Optional[ChangeStatus]:
        """字符串→枚举转换"""
```

### 1.6 异常处理策略

| 场景 | 处理方式 | 用户反馈 |
|------|---------|---------|
| 项目未打开 | 前置检查 | QMessageBox.warning("请先打开项目") |
| 文件不存在 | 返回空/默认值 | 详情区显示"文件未找到" |
| JSON解析失败 | try-except | 详情区显示"读取失败: {错误信息}" |
| 权限不足 | OS异常抛出 | QMessageBox.critical("错误") |
| 状态转换非法 | Service层校验 | QMessageBox.warning("操作未成功") |
| 网络IO超时 | N/A (本地文件系统) | - |

### 1.7 边界条件与校验规则

#### 1.7.1 输入校验

| 输入项 | 校验规则 | 错误提示 |
|--------|---------|---------|
| 变更标题 | 非空且strip()后长度>0 | 不允许创建空标题变更单 |
| 变更分类 | 必须是合法ChangeCategory枚举值 | 由QInputDialog限制 |
| 审核人姓名 | 允许空字符串 | 空字符串作为"匿名审核人" |
| 目标状态 | 必须在valid_transitions列表中 | 动态生成选项列表 |

#### 1.7.2 状态依赖校验

| 操作 | 前置条件 | 后置效果 |
|------|---------|---------|
| **批准** | 当前状态 ∈ {REVIEW} | 状态 → APPROVED |
| **推进** | valid_transitions非空且排除{CANCELLED, APPROVED} | 状态 → 用户选择的目标状态 |
| **取消** | 当前状态 ∉ {COMPLETED, CANCELLED} | 状态 → CANCELLED (终态) |
| **新建** | 项目路径有效 | 创建DRAFT状态变更单 |

---

## 2. F03: 变更管理-Sync (版本检查/CHG/IFC)

### 2.1 功能定位

**用户故事**: 作为PLC工程师，我希望一键检查项目版本一致性、生成标准化的CHG/IFC文档，并能够将生成的文档回写到项目中。

### 2.2 业务流程

#### 2.2.1 版本检查流程

```
用户点击左侧「🔄 版本检查」按钮
    ↓
NavigationController.on_sidebar_action("version_check")
    ↓ 匹配 SIDEBAR_ACTION_MAP["version_check"]
    ↓
sync_handler("version_check")  →  MainWindow._on_sync_action("version_check")
    ↓
SyncController.on_sync_version_check()
    ↓
project_path = self._get_current_project_path()
    ↓ 为空?
→ QMessageBox.information("请先打开一个项目再执行版本检查")
    return

↓
[创建进度对话框]
progress = QProgressDialog("正在执行版本检查...", None, 0, 0)
progress.setWindowTitle("版本一致性检查")
progress.setWindowModality(Qt.WindowModal)  // 模态阻塞
progress.setMinimumDuration(0)  // 立即显示
progress.setCancelButton(None)  // 不可取消
progress.show()

↓
[启动异步Worker]
check_worker = _VersionCheckWorker(project_path, main_window)
check_worker.finished.connect(lambda report: _on_version_check_done(report, progress))
check_worker.error.connect(lambda err: _on_version_check_error(err, progress))
check_worker.start()

↓ [主线程继续事件循环，Worker在后台运行]

═══════════════════════════════════════
           Worker线程 (_VersionCheckWorker.run())
═══════════════════════════════════════
try:
    report = SyncEngine.run_check(self._project_path)
    self.finished.emit(report)  // 发送结果到主线程
except Exception as e:
    self.error.emit(str(e))     // 发送错误到主线程
═══════════════════════════════════════

↓ [主线程接收信号]

[成功回调] _on_version_check_done(report, progress):
    progress.close()
    
    [创建报告对话框]
    dialog = QDialog(main_window)
    dialog.setWindowTitle("版本一致性检查报告")
    dialog.resize(700, 500)
    
    layout = QVBoxLayout(dialog)
    browser = QTextBrowser()
    browser.setOpenExternalLinks(True)
    browser.setHtml(SyncEngine.format_version_report_html(report))  // HTML格式化
    layout.addWidget(browser)
    
    buttons = QDialogButtonBox(QDialogButtonBox.Ok)
    buttons.accepted.connect(dialog.accept)
    layout.addWidget(buttons)
    
    dialog.exec_()

[错误回调] _on_version_check_error(err, progress):
    progress.close()
    logger.error(f"版本检查失败: {err}")
    QMessageBox.critical(main_window, "版本检查失败", err)
```

#### 2.2.2 CHG/IFC文档生成流程

```
用户点击「📝 生成CHG文档」或「📄 生成IFC文档」
    ↓
SyncController.on_sync_generate_chg() 或 on_sync_generate_ifc()
    ↓ (前半部分同版本检查: 校验项目路径 → 进度对话框 → Worker线程)
    
[Worker线程: _GenerateDocWorker.run()]
if doc_type == "chg":
    output_path = SyncEngine.run_generate_chg(project_path)
else:  # ifc
    output_path = SyncEngine.run_generate_ifc(project_path)
self.finished.emit(output_path, doc_type)

↓ [主线程: _on_generate_done]
progress.close()
title = "CHG文档生成结果" / "IFC文档生成结果"
self._show_sync_result(output_path, doc_type, title)

↓
_show_sync_result():
dialog = SyncResultDialog(main_window, output_path, title, doc_type=doc_type)
dialog.exec_()

action = dialog.get_action()
if action == SyncResultDialog.ACTION_WRITEBACK:
    self._do_writeback(output_path, doc_type)

↓ [_do_writeback: 回写到项目]
project_path = self._get_current_project_path()
written = SyncEngine.writeback_to_project(output_path, project_path, doc_type)

if written:
    QMessageBox.information("回写成功", f"已回写 {len(written)} 个文件")
    self._notify_project_tree_refresh()  // 刷新项目树
else:
    QMessageBox.information("回写结果", "源目录无文件可回写")
```

### 2.3 SyncEngine 服务接口

```python
class SyncEngine:
    @classmethod
    def run_check(project_path: str) -> VersionGapReport:
        """执行版本一致性检查"""
        # 扫描PLC源码、文档、配置等资产
        # 比较版本号/时间戳/哈希值
        # 返回 VersionGapReport 对象
    
    @classmethod
    def run_full_report(project_path, output_dir) -> str:
        """生成完整同步报告"""
    
    @classmethod
    def run_generate_chg(project_path, output_dir) -> str:
        """生成CHG变更记录文档"""
        # 使用模板: src/templates/documents/chg_template.md
        # 替换变量: 项目信息/变更列表/版本差异
        # 输出到 <project>/documents/chg/ 目录
    
    @classmethod
    def run_generate_ifc(project_path, output_dir) -> str:
        """生成IFC接口文档"""
        # 使用模板: src/templates/documents/ifc_template.md
        # 输出到 <project>/documents/ifc/ 目录
    
    @classmethod
    def writeback_to_project(source_path, project_path, doc_type) -> List[str]:
        """将生成的文档回写到项目目录"""
        # 复制文件到项目对应位置
        # 更新项目资产索引
        # 返回写入的文件路径列表
    
    @classmethod
    def format_version_report_html(report) -> str:
        """将VersionGapReport格式化为HTML"""
```

### 2.4 异步模式详解

#### 为什么使用QThread?

版本检查和文档生成是**CPU密集型+IO密集型**操作：
- 扫描大量文件 (可能数百个)
- 解析PLC源码 (ST语言语法分析)
- 生成Markdown/PDF文档
- 计算哈希值比对

如果在主线程执行会导致**UI冻结**。

#### Worker实现模式

```python
class _VersionCheckWorker(QThread):
    finished = pyqtSignal(object)   // 发送 VersionGapReport
    error = pyqtSignal(str)        // 发送错误信息
    
    def __init__(self, project_path: str, parent=None):
        super().__init__(parent)
        self._project_path = project_path
    
    def run(self):  // 在独立线程中执行
        try:
            report = SyncEngine.run_check(self._project_path)
            self.finished.emit(report)  // 信号自动跨线程投递
        except Exception as e:
            self.error.emit(str(e))
```

**关键点**:
- pyqtSignal 跨线程安全：Qt自动将信号投递到接收者所在线程的事件队列
- Worker生命周期：由主线程持有引用，任务完成后自动清理
- 取消支持：当前版本不支持中途取消 (CancelButton=None)

---

## 3. F01: 项目管理

### 3.1 业务流程

#### 3.1.1 新建项目

```
用户触发: 菜单/工具栏/仪表盘
    ↓
EventBus.project_created (由MenuManager发射或直接连接)
    ↓
ProjectController.on_project_created(path)
    ↓
ProjectService.create_project(...) 或 ProjectService.create_new_project(...)
    ↓
ProjectTreeWidget.load_project(project)
    ↓
_change_mgmt_panel.set_project_path(path)  // 绑定变更面板
```

#### 3.1.2 打开项目

```
用户触发: 菜单/工具栏/仪表盘/最近项目列表
    ↓
EventBus.project_opened
    ↓
ProjectController.on_project_opened(path)
    ↓
ProjectService.load_project_from_path(path) → (Project, error)
    ↓
ProjectTreeWidget.load_project(project)
    ↓
[根据项目类型构建不同的树节点]
├── DJ单机项目: _build_dj_project_nodes()
│   ├── 工作流阶段节点
│   ├── 核心资产节点 (artifact_roots)
│   ├── 变更摘要节点 (change_status_summary)
│   └── 文档资产节点 (documents[:20])
│
└── 通用项目: _build_generic_nodes()
    ├── 项目基础信息
    ├── 文档管理
    ├── PLC程序
    ├── HMI配置
    ├── 变量清单
    ├── IO分配表
    ├── 报警定义
    └── ...
```

### 3.2 项目数据模型

```python
class Project:
    name: str                    # 项目名称
    project_id: str             # 项目编号
    project_type: ProjectType   # 项目类型 (GENERIC / DJ_SINGLE_MACHINE)
    business_line: BusinessLine  # 业务线 (SW/DJ/ZD/XT/WX)
    path: Path                   # 项目根目录绝对路径
    description: str             # 项目描述
    plc_brand: PLCBrand          # PLC品牌
    hmi_brand: HMIBrand          # HMI品牌
    workflow_stage: WorkflowStage # 当前工作流阶段
    manager: str                 # 项目经理
    created_at: str              # 创建时间
    updated_at: str              # 最后更新
    
    # DJ单机项目特有属性
    artifact_roots: List[Dict]   # 资产根目录列表
    change_status_summary: Dict  # 变更状态统计
    documents: List[Dict]        # 文档列表
```

---

## 4. F02: 文档生成

### 4.1 业务流程

```
用户触发: 左侧「📄 新建文档」按钮 / 项目树右键菜单
    ↓
action_handler(TAB_DOCUMENT) → navigate_to_tab(2)
    ↓
右侧切换到「📝 文档」Tab → DocumentEditor可见
    ↓
[用户在DocumentEditor中操作]
├── 打开已有文档: 文件对话框 → 读取内容到编辑器
├── 编辑文档内容: 直接在QTextEdit中编辑
├── 保存文档: 写入文件系统
└── 另存为: 另存为新文件
```

### 4.2 TemplateService 接口

```python
class TemplateService:
    @classmethod
    def initialize_builtin_templates() -> None:
        """初始化内置模板 (10种文档模板)"""
    
    @classmethod
    def get_template(template_id) -> Optional[Dict]:
        """获取单个模板定义"""
    
    @classmethod
    def get_all_templates() -> List[Dict]:
        """获取所有模板列表"""
    
    @classmethod
    def apply_template(template_id, target_path, variables) -> Tuple:
        """应用模板生成文档 (变量替换)"""
```

### 4.3 支持的文档类型

| 类型 | 枚举值 | 中文名称 | 模板文件 |
|------|--------|---------|---------|
| REQ | REQ | 需求规格说明书 | req_template.md |
| DSN | DSN | 详细设计文档 | dsn_template.md |
| IFC | IFC | 接口文档 | ifc_template.md |
| UM | UM | 用户操作手册 | um_template.md |
| CHG | CHG | 变更记录 | chg_template.md |
| ALM | ALM | 报警码定义 | alm_template.md |
| VAR | VAR | 变量清单 | var_template.md |
| IO | IO | IO分配表 | io_template.md |
| ARC | ARC | 架构设计文档 | arc_template.md |
| TEST | TEST | 测试报告 | test_template.md |
| SUM | SUM | 项目总结 | sum_template.md |

---

## 5. F04: 规范检查

### 5.1 业务流程

```
用户触发: 菜单F5 / Dock面板 / 侧边栏按钮
    ↓
SpecCheckPanel.start_check()  [Dock面板版本]
    ↓
SpecCheckerService.check_project(project_path)
    ↓
[内部流程]
1. load_project_rules(project_path)  // 加载项目自定义规则
2. 遍历启用检查器:
   ├── NamingChecker (命名规范检查)
   ├── SyntaxChecker (ST语法检查)
   ├── CommentChecker (注释规范检查)
   ├── ConfigChecker (配置规范检查)
   ├── TimerChecker (定时器规范检查)
   └── VariableChecker (变量规范检查)
3. 汇总 CheckResult 列表
4. 生成 CheckReport
    ↓
[结果显示]
├── 通过/失败/警告统计
├── 问题列表 (文件路径+行号+问题描述+严重级别)
└── 导出报告功能
```

### 5.2 检查器框架

```python
# 所有检查器继承自 BaseChecker
class BaseChecker(ABC):
    @abstractmethod
    def check(self, file_path: str, context: Dict) -> CheckResult:
        """执行检查，返回结果"""
    
    @abstractmethod
    def get_name(self) -> str:
        """返回检查器名称"""
    
    @property
    @abstractmethod
    def rule_id_prefix(self) -> str:
        """规则ID前缀 (如 'NAM' for NamingChecker)"""

# 规则注册表
class RuleRegistry:
    _checkers: Dict[str, Type[BaseChecker]] = {}
    
    @classmethod
    def register(cls, checker_class: Type[BaseChecker]):
        """注册检查器"""
    
    @classmethod
    def get_enabled_checkers(cls) -> List[BaseChecker]:
        """获取所有启用的检查器实例"""
```

---

## 6. F05: 诊断分析

### 6.1 业务流程

```
用户触发: 菜单F6 / Dock面板
    ↓
DiagnosticPanel.run_diagnostic()
    ↓
DiagnosticService.run_full_diagnostic(project_path)
    ↓
[七维度健康评估]
1. 📁 文件结构完整性 (目录/文件是否存在)
2. 📄 文档覆盖率 (必需文档是否齐全)
3. 🔗 交叉引用一致性 (文档间引用是否有效)
4. 📊 版本一致性 (组件版本号是否对齐)
5. ⚙️ 配置规范性 (配置文件是否符合标准)
6. 🧪 测试覆盖度 (测试用例是否充分)
7. 🔒 安全合规性 (敏感信息/权限检查)
    ↓
[LSP兼容性检查] (如果安装了西门子LSP)
    ↓
生成 DiagnosticReport (含HealthMetrics)
    ↓
[UI展示]
├── 总体健康评分 (0-100分)
├── 各维度得分雷达图
├── 问题清单 (按严重程度排序)
└── 建议改进措施
```

---

## 7. 交叉功能域集成点

### 7.1 项目 ↔ 变更管理

```
项目打开/创建
    ↓
MainWindow._on_project_opened / _on_project_created
    ↓
_change_mgmt_panel.set_project_path(path)
    ↓
ChangeManagementPanel 自动刷新变更单列表
```

### 7.2 变更管理 ↔ Sync (文档生成)

```
变更单审批通过 (APPROVED)
    ↓
用户可在变更管理面板看到该变更单
    ↓
[手动触发] 版本检查 / CHG生成 / IFC生成
    ↓
SyncEngine 基于当前项目状态生成文档
    ↓
[可选] 回写到项目 → ProjectTreeWidget刷新
```

### 7.3 诊断 ↔ 源码跳转

```
诊断面板发现代码问题
    ↓
用户点击问题项 (文件路径+行号)
    ↓
MainWindow._jump_to_source(file_path, line_number)
    ↓
NavigationController.navigate_to_tab(TAB_PLC_TOOLS)
    ↓
STEditor.open_file(file_path, line_number)
    ↓
[光标定位到指定行]
```

### 7.4 EventBus 全局事件

```
主题切换
    ↓
EventBus.theme_changed.emit(theme_name)
    ↓
MainWindow._on_theme_changed
    ↓
StyleBuilder.apply(widget, theme)
    ↓
[全局样式刷新]

设置变更
    ↓
EventBus.settings_changed.emit()
    ↓
MainWindow._on_settings_changed
    ↓
[各组件响应设置变更]
```

---

## 8. 数据持久化策略

### 8.1 文件系统布局

```
<project_root>/
├── 00_项目基础信息/
│   └── project.json          # 项目元数据
├── changes/
│   ├── CHG-20260523-001.json  # 变更单文件
│   ├── CHG-20260523-002.json
│   └── ...
├── documents/
│   ├── req/
│   ├── dsn/
│   ├── ifc/
│   ├── chg/
│   └── ... (各类型文档子目录)
├── plc_source/
│   └── *.st, *.scl, *.udt    # PLC源码
├── hmi_source/
│   └── ...                   # HMI源码
└── config/
    └── settings.json         # 项目级配置
```

### 8.2 SettingsManager (全局配置)

```
~/.sw2026-005/settings.json  (用户全局配置)
{
    "theme": "light",
    "sidebar_width": 240,
    "recent_projects": [...],
    "window_geometry": {...},
    "last_opened_project": "...",
    ...
}
```

---

## 9. 错误处理全景

### 9.1 分层异常处理策略

```
┌─────────────────────────────────────────────┐
│           GUI Layer (Widgets/Dialogs)        │
│  • 捕获所有Exception                         │
│  • 显示用户友好的QMessageBox                  │
│  • 记录logger.exception()                     │
│  • 不向上抛出 (终端处理点)                    │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┘
│          Controller Layer                    │
│  • 捕获业务逻辑异常                          │
│  • 转换为用户可理解的错误消息                 │
│  • 可选: emit error signal给上层              │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┘
│           Service Layer                      │
│  • 捕获IO/FileSystem异常                     │
│  • 返回 (result, error) 元组                  │
│  • 校验前置条件 (guard clauses)               │
└─────────────────────────────────────────────┘
```

### 9.2 异常分类

| 类别 | 示例 | 处理方式 | 用户反馈 |
|------|------|---------|---------|
| **输入无效** | 空标题/非法路径 | 前置检查 + return | warning对话框 |
| **文件缺失** | 项目不存在/文件未找到 | try-except + 默认值 | 界面显示占位符 |
| **权限不足** | 无法写入/读取 | OS异常捕获 | critical对话框 |
| **状态非法** | 无效的状态转换 | Service层校验 | warning对话框 |
| **网络超时** | N/A (本地应用) | - | - |
| **模板缺失** | 模板文件不存在 | fallback到通用模板 | info提示 |

---

## 10. 性能特征与优化建议

### 10.1 当前性能特征

| 操作 | 耗时估算 | 瓶颈点 | 是否需要优化 |
|------|---------|--------|-------------|
| 启动加载 | 1-2秒 | 模板初始化+设置加载 | ⚠️ 可接受 |
| 项目打开 | 0.5-1秒 | 文件扫描+树构建 | ✅ 已够快 |
| 变更单列表刷新 | 0.1-0.3秒 | 文件IO (取决于数量) | ✅ 已够快 |
| 版本检查 | 3-10秒 | 全量文件扫描+哈希计算 | ✅ 已异步化 |
| CHG/IFC生成 | 2-5秒 | 模板渲染+变量替换 | ✅ 已异步化 |
| 诊断分析 | 5-15秒 | 七维度深度扫描 | ✅ 已异步化 |

### 10.2 优化建议 (不实施，仅供参考)

1. **增量刷新**: 变更单列表支持增量更新而非全量reload
2. **缓存机制**: 缓存项目文件列表和哈希值
3. **懒加载**: 项目树节点展开时才加载子节点
4. **虚拟滚动**: 大型变更单列表使用QTableView+Model

---

## 附录A: 完整调用链索引

| GUI入口 | Widget | Signal/Event | Controller | Service | 数据存储 |
|---------|-------|-------------|------------|---------|-----------|
| 新建项目 | MenuManager | action.triggered | → EventBus | ProjectService.create_* | project.json |
| 打开项目 | MenuManager | action.triggered | → EventBus | ProjectService.load_* | project.json |
| 新建文档 | LeftPanelBuilder btn | clicked(int) | navigate_to_tab | DocumentEditor | filesystem |
| 新建变更单 | ChangeMgmtPanel btn | clicked | → _on_create | ChangeService.create_* | changes/*.json |
| 审核变更 | ChangeMgmtPanel btn | clicked | → _on_approve | ChangeService.approve_* | changes/*.json |
| 推进状态 | ChangeMgmtPanel btn | clicked | → _on_advance | ChangeService.update_status | changes/*.json |
| 取消变更 | ChangeMgmtPanel btn | clicked | → _on_cancel | ChangeService.update_status | changes/*.json |
| 版本检查 | LeftPanelBuilder btn | clicked(str) | on_sidebar_action | SyncController → SyncEngine | memory/report |
| CHG生成 | LeftPanelBuilder btn | clicked(str) | on_sidebar_action | SyncController → SyncEngine | documents/chg/ |
| IFC生成 | LeftPanelBuilder btn | clicked(str) | on_sidebar_action | SyncController → SyncEngine | documents/ifc/ |
| 规范检查 | SpecCheckPanel | start_check | → SpecCheckerService | check_project | memory/report |
| 深度诊断 | DiagnosticPanel | run_diagnostic | → DiagnosticService | run_full_diagnostic | memory/report |
| 主题切换 | MenuManager | action.triggered | → EventBus | StyleBuilder.apply | settings.json |
| 源码跳转 | DiagnosticPanel | jump_requested | _jump_to_source | STEditor.open_file | filesystem |

---

**文档完成** ✅

*本报告为纯业务逻辑分析文档，不包含任何代码修改建议的实施。*
*关联文档: GUI技术架构审查报告_V1.0.md*
