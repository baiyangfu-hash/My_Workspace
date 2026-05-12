# -*- coding: utf-8 -*-
"""
变更管理控件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLineEdit, QComboBox, QLabel,
    QDialog, QFormLayout, QTextEdit, QMessageBox,
    QGroupBox, QGridLayout, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

import os
from src.services.change_service import ChangeService
from src.services.project_service import ProjectService
from src.services.impact_service import ImpactService
from src.services.approval_service import ApprovalService
from src.core.constants import (
    ChangeStatus, ChangeType, Domain, Nature, Scope,
    DOMAIN_NAMES, NATURE_NAMES, SCOPE_NAMES,
    SCOPE_APPROVAL_MAP,
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

CHANGE_TYPES = ["代码变更", "配置变更", "依赖变更", "文档变更", "结构变更", "模板变更", "插件变更"]

CHANGE_STATUS_NAMES = {
    ChangeStatus.DRAFT: "草稿",
    ChangeStatus.PENDING: "待审批",
    ChangeStatus.APPROVED: "已批准",
    ChangeStatus.REJECTED: "已拒绝",
    ChangeStatus.IMPLEMENTING: "实施中",
    ChangeStatus.COMPLETED: "已完成",
    ChangeStatus.CANCELLED: "已取消"
}

CHANGE_STATUS_COLORS = {
    ChangeStatus.DRAFT: "#9E9E9E",
    ChangeStatus.PENDING: "#FF9800",
    ChangeStatus.APPROVED: "#4CAF50",
    ChangeStatus.REJECTED: "#F44336",
    ChangeStatus.IMPLEMENTING: "#2196F3",
    ChangeStatus.COMPLETED: "#8BC34A",
    ChangeStatus.CANCELLED: "#607D8B"
}

# V2.1.0: 领域/性质/范围选择项
DOMAIN_OPTIONS = [(d, DOMAIN_NAMES[d]) for d in Domain]
NATURE_OPTIONS = [(n, NATURE_NAMES[n]) for n in Nature]
SCOPE_OPTIONS = [(s, SCOPE_NAMES[s]) for s in Scope]

# 范围颜色 (用于表格高亮)
SCOPE_COLORS = {
    Scope.LOCAL: "#4CAF50",
    Scope.MODULE: "#FF9800",
    Scope.SYSTEM: "#F44336",
    Scope.CROSS: "#9C27B0",
    Scope.SAFE: "#000000",
}

class ChangeManagerWidget(QWidget):
    """变更管理控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_project_id = None
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        project_bar = QHBoxLayout()
        
        project_bar.addWidget(QLabel("项目:"))
        
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(300)
        self.project_combo.currentIndexChanged.connect(self._on_project_changed)
        project_bar.addWidget(self.project_combo)
        
        project_bar.addStretch()
        
        layout.addLayout(project_bar)
        
        stats_group = QGroupBox("变更统计")
        stats_layout = QHBoxLayout(stats_group)
        
        self.stat_labels = {}
        for status in [ChangeStatus.DRAFT, ChangeStatus.PENDING, ChangeStatus.APPROVED, 
                       ChangeStatus.IMPLEMENTING, ChangeStatus.COMPLETED, ChangeStatus.REJECTED]:
            label = QLabel(f"{CHANGE_STATUS_NAMES[status]}: 0")
            label.setStyleSheet(f"color: {CHANGE_STATUS_COLORS[status]}; font-weight: bold;")
            stats_layout.addWidget(label)
            self.stat_labels[status] = label
        
        layout.addWidget(stats_group)
        
        toolbar = QHBoxLayout()

        # V2.1.0: 领域筛选 (新增)
        self.domain_filter = QComboBox()
        self.domain_filter.addItem("全部领域", None)
        for domain, name in DOMAIN_OPTIONS:
            self.domain_filter.addItem(name, domain)
        self.domain_filter.currentIndexChanged.connect(self._load_changes)
        toolbar.addWidget(QLabel("领域:"))
        toolbar.addWidget(self.domain_filter)

        # V2.1.0: 性质筛选 (新增)
        self.nature_filter = QComboBox()
        self.nature_filter.addItem("全部性质", None)
        for nature, name in NATURE_OPTIONS:
            self.nature_filter.addItem(name, nature)
        self.nature_filter.currentIndexChanged.connect(self._load_changes)
        toolbar.addWidget(QLabel("性质:"))
        toolbar.addWidget(self.nature_filter)

        # V2.1.0: 范围筛选 (新增)
        self.scope_filter = QComboBox()
        self.scope_filter.addItem("全部范围", None)
        for scope, name in SCOPE_OPTIONS:
            self.scope_filter.addItem(name, scope)
        self.scope_filter.currentIndexChanged.connect(self._load_changes)
        toolbar.addWidget(QLabel("范围:"))
        toolbar.addWidget(self.scope_filter)

        # 原有: 状态筛选
        self.status_filter = QComboBox()
        self.status_filter.addItem("全部状态", None)
        for status in ChangeStatus:
            self.status_filter.addItem(CHANGE_STATUS_NAMES[status], status.value)
        self.status_filter.currentIndexChanged.connect(self._load_changes)
        toolbar.addWidget(QLabel("状态:"))
        toolbar.addWidget(self.status_filter)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索变更...")
        self.search_input.textChanged.connect(self._load_changes)
        toolbar.addWidget(self.search_input)
        
        self.new_btn = QPushButton("新建变更")
        self.new_btn.clicked.connect(self._on_new_change)
        toolbar.addWidget(self.new_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._load_changes)
        toolbar.addWidget(self.refresh_btn)
        
        layout.addLayout(toolbar)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.change_table = QTableWidget()
        self.change_table.setColumnCount(9)
        self.change_table.setHorizontalHeaderLabels([
            "序号", "→ 变更单", "领域", "性质", "范围", "标题", "优先级", "状态", "日期"
        ])
        self.change_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.change_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.change_table.setSelectionMode(QTableWidget.SingleSelection)
        self.change_table.itemSelectionChanged.connect(self._on_change_selected)
        splitter.addWidget(self.change_table)
        
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        
        self.detail_tabs = QTabWidget()
        
        self.detail_tab = QWidget()
        detail_tab_layout = QVBoxLayout(self.detail_tab)
        
        self.detail_info = QLabel("请选择变更单查看详情")
        self.detail_info.setWordWrap(True)
        detail_tab_layout.addWidget(self.detail_info)
        
        self.detail_content = QTextEdit()
        self.detail_content.setReadOnly(True)
        detail_tab_layout.addWidget(self.detail_content)
        
        self.detail_tabs.addTab(self.detail_tab, "变更详情")
        
        self.flow_tab = QWidget()
        flow_tab_layout = QVBoxLayout(self.flow_tab)
        
        self.flow_info = QLabel("变更流程状态")
        flow_tab_layout.addWidget(self.flow_info)
        
        self.flow_buttons = QWidget()
        flow_buttons_layout = QHBoxLayout(self.flow_buttons)
        
        self.btn_submit = QPushButton("提交审批")
        self.btn_submit.clicked.connect(self._on_submit)
        flow_buttons_layout.addWidget(self.btn_submit)
        
        self.btn_approve = QPushButton("审批通过")
        self.btn_approve.clicked.connect(self._on_approve)
        flow_buttons_layout.addWidget(self.btn_approve)
        
        self.btn_reject = QPushButton("驳回")
        self.btn_reject.clicked.connect(self._on_reject)
        flow_buttons_layout.addWidget(self.btn_reject)
        
        self.btn_implement = QPushButton("开始实施")
        self.btn_implement.clicked.connect(self._on_start_implement)
        flow_buttons_layout.addWidget(self.btn_implement)
        
        self.btn_complete = QPushButton("完成")
        self.btn_complete.clicked.connect(self._on_complete)
        flow_buttons_layout.addWidget(self.btn_complete)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self._on_cancel)
        flow_buttons_layout.addWidget(self.btn_cancel)
        
        flow_tab_layout.addWidget(self.flow_buttons)
        flow_tab_layout.addStretch()
        
        self.detail_tabs.addTab(self.flow_tab, "流程操作")
        
        self.impact_tab = QWidget()
        impact_tab_layout = QVBoxLayout(self.impact_tab)
        
        self.impact_info = QLabel("影响分析")
        impact_tab_layout.addWidget(self.impact_info)
        
        self.impact_content = QTextEdit()
        self.impact_content.setReadOnly(True)
        impact_tab_layout.addWidget(self.impact_content)
        
        self.detail_tabs.addTab(self.impact_tab, "影响分析")
        
        self.approval_tab = QWidget()
        approval_tab_layout = QVBoxLayout(self.approval_tab)
        
        self.approval_info = QLabel("审批历史")
        approval_tab_layout.addWidget(self.approval_info)
        
        self.approval_table = QTableWidget()
        self.approval_table.setColumnCount(4)
        self.approval_table.setHorizontalHeaderLabels(["审批人", "动作", "意见", "审批时间"])
        self.approval_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        approval_tab_layout.addWidget(self.approval_table)
        
        self.detail_tabs.addTab(self.approval_tab, "审批历史")
        
        # 添加变更台帐标签页
        self.ledger_tab = QWidget()
        ledger_tab_layout = QVBoxLayout(self.ledger_tab)
        
        self.ledger_info = QLabel("变更台帐")
        ledger_tab_layout.addWidget(self.ledger_info)
        
        self.ledger_content = QTextEdit()
        self.ledger_content.setReadOnly(True)
        ledger_tab_layout.addWidget(self.ledger_content)
        
        self.ledger_buttons = QWidget()
        ledger_buttons_layout = QHBoxLayout(self.ledger_buttons)
        
        self.btn_generate_ledger = QPushButton("生成台帐")
        self.btn_generate_ledger.clicked.connect(self._on_generate_ledger)
        ledger_buttons_layout.addWidget(self.btn_generate_ledger)
        
        self.btn_view_ledger = QPushButton("查看台帐文件")
        self.btn_view_ledger.clicked.connect(self._on_view_ledger)
        ledger_buttons_layout.addWidget(self.btn_view_ledger)
        
        ledger_tab_layout.addWidget(self.ledger_buttons)
        
        self.detail_tabs.addTab(self.ledger_tab, "变更台帐")
        
        detail_layout.addWidget(self.detail_tabs)
        
        splitter.addWidget(detail_widget)
        
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
        
        self._load_projects()
        self._update_flow_buttons(None)
    
    def _load_projects(self):
        """加载项目列表"""
        self.project_combo.clear()
        
        # 不指定status参数，获取所有项目
        projects, _ = ProjectService.list_projects(size=100)
        for project in projects:
            self.project_combo.addItem(f"{project.code} - {project.name}", project.project_id)
        
        if self.project_combo.count() > 0:
            self.current_project_id = self.project_combo.currentData()
            self._load_changes()
    
    def _on_project_changed(self, index: int):
        """项目变更"""
        self.current_project_id = self.project_combo.currentData()
        self._load_changes()
    
    def _load_changes(self):
        """V2.1.0: 加载变更列表 (支持domain/nature/scope筛选 + 9列显示)"""
        self.change_table.setRowCount(0)

        if not self.current_project_id:
            return

        status = self.status_filter.currentData()
        keyword = self.search_input.text()

        changes, total = ChangeService.list_changes(
            project_id=self.current_project_id,
            status=status
        )

        if keyword:
            changes = [c for c in changes if keyword.lower() in c.title.lower()]

        # V2.1.0: 应用领域筛选
        domain_filter = self.domain_filter.currentData()
        if domain_filter:
            changes = [c for c in changes if hasattr(c, 'domain') and c.domain == domain_filter]

        # V2.1.0: 应用性质筛选
        nature_filter = self.nature_filter.currentData()
        if nature_filter:
            changes = [c for c in changes if hasattr(c, 'nature') and c.nature == nature_filter]

        # V2.1.0: 应用范围筛选
        scope_filter = self.scope_filter.currentData()
        if scope_filter:
            changes = [c for c in changes if hasattr(c, 'scope') and c.scope == scope_filter]

        for row, change in enumerate(changes):
            self.change_table.insertRow(row)

            # 序号
            self.change_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))

            # → 变更单 (带超链接样式)
            link_item = QTableWidgetItem(f"→ {change.change_id}")
            link_item.setForeground(QColor("#2196F3"))
            link_item.setToolTip(f"点击查看详情: {change.change_id}")
            self.change_table.setItem(row, 1, link_item)

            # 领域 (中文名)
            domain_name = DOMAIN_NAMES.get(change.domain, str(change.domain.value)) if hasattr(change, 'domain') else '-'
            self.change_table.setItem(row, 2, QTableWidgetItem(domain_name))

            # 性质 (中文名)
            nature_name = NATURE_NAMES.get(change.nature, str(change.nature.value)) if hasattr(change, 'nature') else '-'
            self.change_table.setItem(row, 3, QTableWidgetItem(nature_name))

            # 范围 (带警告标记)
            if hasattr(change, 'get_scope_display'):
                scope_display = change.get_scope_display()
            else:
                scope_display = SCOPE_NAMES.get(change.scope, '-') if hasattr(change, 'scope') else '-'
            scope_item = QTableWidgetItem(scope_display)
            if hasattr(change, 'needs_reviewer') and change.needs_reviewer():
                scope_item.setBackground(QColor("#FFF3E0"))
            self.change_table.setItem(row, 4, scope_item)

            # 标题
            self.change_table.setItem(row, 5, QTableWidgetItem(change.title))

            # 优先级 (带颜色)
            prio_item = QTableWidgetItem(change.priority or "P2")
            if change.priority == "P0":
                prio_item.setForeground(QColor("#F44336"))
            elif change.priority == "P1":
                prio_item.setForeground(QColor("#FF9800"))
            self.change_table.setItem(row, 6, prio_item)

            # 状态 (带颜色)
            status_item = QTableWidgetItem(CHANGE_STATUS_NAMES.get(change.status, str(change.status)))
            status_item.setForeground(QColor(CHANGE_STATUS_COLORS.get(change.status, "#000000")))
            self.change_table.setItem(row, 7, status_item)

            # 日期
            self.change_table.setItem(row, 8, QTableWidgetItem(
                change.created_at.strftime("%Y-%m-%d") if change.created_at else ""
            ))

        self._update_statistics()
    
    def _update_statistics(self):
        """更新统计信息"""
        if not self.current_project_id:
            return
        
        stats = ChangeService.get_statistics(self.current_project_id)
        
        for status, label in self.stat_labels.items():
            count = stats.get(status.value if hasattr(status, 'value') else status, 0)
            label.setText(f"{CHANGE_STATUS_NAMES[status]}: {count}")
    
    def _on_change_selected(self):
        """选择变更"""
        selected = self.change_table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        change_id = self.change_table.item(row, 1).text()
        
        change = ChangeService.get_change(change_id)
        if change:
            self._show_change_detail(change)
            self._update_flow_buttons(change)
    
    def _show_change_detail(self, change):
        """V2.1.0: 显示变更详情 (使用domain/nature/scope字段)"""
        # 尝试使用V2.1.0字段，fallback到V1.x字段
        if hasattr(change, 'to_v2_dict'):
            d = change.to_v2_dict()
        else:
            d = {
                'domain': getattr(change, 'domain', None),
                'domain_name': DOMAIN_NAMES.get(getattr(change, 'domain', None), '-'),
                'nature': getattr(change, 'nature', None),
                'nature_name': NATURE_NAMES.get(getattr(change, 'nature', None), '-'),
                'scope': getattr(change, 'scope', None),
                'scope_display': SCOPE_NAMES.get(getattr(change, 'scope', None), '-'),
                'priority': getattr(change, 'priority', 'P2'),
                'approval_level': getattr(change, 'get_approval_level_name', lambda: '-')(),
                'reviewer': getattr(change, 'reviewer', ''),
            }

        needs_review = hasattr(change, 'needs_reviewer') and change.needs_reviewer()

        info = f"""
<h3>{change.title}</h3>
<p><b>变更编号:</b> {change.change_id}</p>
<p><b>技术领域:</b> {d['domain_name']} ({d['domain']})</p>
<p><b>业务性质:</b> {d['nature_name']} ({d['nature']})</p>
<p><b>影响范围:</b> {d['scope_display']}</p>
<p><b>优先级:</b> {d['priority']}</p>
<p><b>审批层级:</b> {d['approval_level']}</p>
{'<p><b>⚠️ 复审人:</b> ' + (d['reviewer'] or '待指定') + ' <span style="color:red">(必需)</span></p>' if needs_review else ''}
<p><b>当前状态:</b> <span style="color: {CHANGE_STATUS_COLORS.get(change.status, '#000')}">{CHANGE_STATUS_NAMES.get(change.status, str(change.status))}</span></p>
<p><b>提出人:</b> {change.proposer or '-'}</p>
<p><b>审批人:</b> {change.approver or '-'}</p>
<p><b>实施人:</b> {change.implementer or '-'}</p>
<p><b>创建时间:</b> {change.created_at.strftime('%Y-%m-%d %H:%M') if change.created_at else '-'}</p>
</hr>
<h4>变更原因</h4>
<p>{change.reason or '无'}</p>
<h4>V1.x遗留字段 (兼容)</h4>
<p><b>旧类型:</b> {change.type or '(无)'}</p>
<p><b>旧影响:</b> {change.impact or '(无)'}</p>
<h4>变更前后对比</h4>
<b>变更前 (Before):</b><pre>{getattr(change, 'content_before', None) or '(无详细记录)'}</pre>
<b>变更后 (After):</b><pre>{getattr(change, 'content_after', None) or '(无详细记录)'}</pre>
"""
        self.detail_info.setText(info)
        self.detail_content.setText(change.description or "")

        # 显示影响分析
        self._show_impact_analysis(change)

        # 显示审批历史
        self._show_approval_history(change)

        # 显示变更台帐信息
        self._show_ledger_info(change)
    
    def _show_impact_analysis(self, change):
        """显示影响分析"""
        try:
            impact_result = ImpactService.analyze_impact(change.change_id)
            
            if "error" in impact_result:
                self.impact_content.setText(f"影响分析失败: {impact_result['error']}")
                return
            
            # 格式化影响分析结果
            components = impact_result.get("affected_components", [])
            risk_level = impact_result.get("risk_level", "未知")
            mitigation_plan = impact_result.get("mitigation_plan", "")
            
            # 风险等级颜色
            risk_colors = {"low": "#4CAF50", "medium": "#FF9800", "high": "#F44336"}
            risk_color = risk_colors.get(risk_level, "#000000")
            
            # 受影响组件列表
            components_text = "\n".join([
                f"- {comp.get('description', comp.get('type', ''))}" 
                for comp in components
            ])
            
            impact_info = f"""
<h4>影响分析结果</h4>
<p><b>风险等级:</b> <span style="color: {risk_color}; font-weight: bold;">{risk_level.upper()}</span></p>
<h4>受影响组件</h4>
<p>{components_text or '无'}</p>
<h4>缓解措施</h4>
<p>{mitigation_plan or '无'}</p>
<p><b>分析时间:</b> {impact_result.get('analysis_time', '')}</p>
"""
            self.impact_content.setText(impact_info)
            
        except Exception as e:
            logger.exception(f"显示影响分析失败: {e}")
            self.impact_content.setText(f"显示影响分析失败: {str(e)}")
    
    def _show_approval_history(self, change):
        """显示审批历史"""
        try:
            histories = ApprovalService.get_approval_history(change.change_id)
            
            self.approval_table.setRowCount(0)
            
            for row, history in enumerate(histories):
                self.approval_table.insertRow(row)
                
                # 审批人
                self.approval_table.setItem(row, 0, QTableWidgetItem(history.approver or ""))
                
                # 动作
                action_text = "通过" if history.action == "approve" else "驳回"
                action_color = "#4CAF50" if history.action == "approve" else "#F44336"
                action_item = QTableWidgetItem(action_text)
                action_item.setForeground(QColor(action_color))
                self.approval_table.setItem(row, 1, action_item)
                
                # 意见
                self.approval_table.setItem(row, 2, QTableWidgetItem(history.comment or ""))
                
                # 审批时间
                time_text = history.approved_at.strftime("%Y-%m-%d %H:%M") if history.approved_at else ""
                self.approval_table.setItem(row, 3, QTableWidgetItem(time_text))
            
            if not histories:
                self.approval_table.insertRow(0)
                self.approval_table.setItem(0, 0, QTableWidgetItem("暂无审批历史"))
                self.approval_table.setSpan(0, 0, 1, 4)
            
        except Exception as e:
            logger.exception(f"显示审批历史失败: {e}")
            self.approval_table.setRowCount(0)
            self.approval_table.insertRow(0)
            self.approval_table.setItem(0, 0, QTableWidgetItem(f"加载审批历史失败: {str(e)}"))
            self.approval_table.setSpan(0, 0, 1, 4)
    
    def _on_generate_ledger(self):
        """生成变更台帐"""
        if not self.current_project_id:
            QMessageBox.warning(self, "提示", "请先选择项目")
            return
        
        try:
            from src.services.change_service import ChangeService
            
            result, error = ChangeService.generate_ledger(self.current_project_id)
            if result:
                QMessageBox.information(self, "成功", f"变更台帐生成成功: {result}")
                self._load_ledger_content()
            else:
                QMessageBox.warning(self, "失败", f"生成变更台帐失败: {error}")
        except Exception as e:
            logger.exception(f"生成变更台帐失败: {e}")
            QMessageBox.warning(self, "错误", f"生成变更台帐失败: {str(e)}")
    
    def _on_view_ledger(self):
        """查看台帐文件"""
        if not self.current_project_id:
            QMessageBox.warning(self, "提示", "请先选择项目")
            return
        
        try:
            from src.services.project_service import ProjectService
            project = ProjectService.get_project(self.current_project_id)
            if not project:
                QMessageBox.warning(self, "错误", "项目不存在")
                return
            
            ledger_path = os.path.join(
                project.path,
                "00_项目管理",
                "04_变更管理",
                f"{project.name}_版本变更台帐.md"
            )
            
            if os.path.exists(ledger_path):
                os.startfile(ledger_path)
            else:
                QMessageBox.warning(self, "提示", "变更台帐文件不存在，请先生成")
        except Exception as e:
            logger.exception(f"查看台帐文件失败: {e}")
            QMessageBox.warning(self, "错误", f"查看台帐文件失败: {str(e)}")
    
    def _load_ledger_content(self):
        """加载变更台帐内容"""
        if not self.current_project_id:
            return
        
        try:
            from src.services.project_service import ProjectService
            project = ProjectService.get_project(self.current_project_id)
            if not project:
                return
            
            ledger_path = os.path.join(
                project.path,
                "00_项目管理",
                "04_变更管理",
                f"{project.name}_版本变更台帐.md"
            )
            
            if os.path.exists(ledger_path):
                with open(ledger_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.ledger_content.setText(content)
            else:
                self.ledger_content.setText("变更台帐文件不存在，请点击'生成台帐'按钮生成")
        except Exception as e:
            logger.exception(f"加载台帐内容失败: {e}")
            self.ledger_content.setText(f"加载台帐内容失败: {str(e)}")
    
    def _show_ledger_info(self, change):
        """显示变更台帐信息"""
        self._load_ledger_content()
    
    def _update_flow_buttons(self, change):
        """更新流程按钮状态"""
        self.btn_submit.setEnabled(False)
        self.btn_approve.setEnabled(False)
        self.btn_reject.setEnabled(False)
        self.btn_implement.setEnabled(False)
        self.btn_complete.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        
        if not change:
            return
        
        status = change.status
        
        if status == ChangeStatus.DRAFT:
            self.btn_submit.setEnabled(True)
            self.btn_cancel.setEnabled(True)
        elif status == ChangeStatus.PENDING:
            self.btn_approve.setEnabled(True)
            self.btn_reject.setEnabled(True)
        elif status == ChangeStatus.APPROVED:
            self.btn_implement.setEnabled(True)
            self.btn_cancel.setEnabled(True)
        elif status == ChangeStatus.IMPLEMENTING:
            self.btn_complete.setEnabled(True)
    
    def _on_new_change(self):
        """新建变更"""
        if not self.current_project_id:
            QMessageBox.warning(self, "提示", "请先选择项目")
            return
        
        dialog = NewChangeDialog(self.current_project_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self._load_changes()
    
    def _on_submit(self):
        """提交审批"""
        selected = self.change_table.selectedItems()
        if not selected:
            return
        
        change_id = self.change_table.item(selected[0].row(), 1).text()

        reply = QMessageBox.question(
            self, "确认", "确定要提交审批吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, error = ChangeService.submit_change(change_id)
            if success:
                QMessageBox.information(self, "成功", "变更单已提交审批")
                self._load_changes()
            else:
                QMessageBox.warning(self, "失败", error)

    def _on_approve(self):
        """审批通过"""
        selected = self.change_table.selectedItems()
        if not selected:
            return

        change_id = self.change_table.item(selected[0].row(), 1).text()
        
        reply = QMessageBox.question(
            self, "确认", "确定要审批通过吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = ChangeService.approve_change(change_id, "当前用户")
            if success:
                QMessageBox.information(self, "成功", "变更单已审批通过")
                self._load_changes()
            else:
                QMessageBox.warning(self, "失败", error)
    
    def _on_reject(self):
        """驳回"""
        selected = self.change_table.selectedItems()
        if not selected:
            return
        
        change_id = self.change_table.item(selected[0].row(), 1).text()

        from PyQt5.QtWidgets import QInputDialog
        reason, ok = QInputDialog.getText(self, "驳回原因", "请输入驳回原因:")

        if ok and reason:
            success, error = ChangeService.reject_change(change_id, "当前用户", reason)
            if success:
                QMessageBox.information(self, "成功", "变更单已驳回")
                self._load_changes()
            else:
                QMessageBox.warning(self, "失败", error)

    def _on_start_implement(self):
        """开始实施"""
        selected = self.change_table.selectedItems()
        if not selected:
            return

        change_id = self.change_table.item(selected[0].row(), 1).text()
        
        reply = QMessageBox.question(
            self, "确认", "确定要开始实施吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = ChangeService.start_implement(change_id, "当前用户")
            if success:
                QMessageBox.information(self, "成功", "变更单开始实施")
                self._load_changes()
            else:
                QMessageBox.warning(self, "失败", error)
    
    def _on_complete(self):
        """完成"""
        selected = self.change_table.selectedItems()
        if not selected:
            return
        
        change_id = self.change_table.item(selected[0].row(), 1).text()

        reply = QMessageBox.question(
            self, "确认", "确定变更已完成吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, error = ChangeService.complete_change(change_id)
            if success:
                QMessageBox.information(self, "成功", "变更单已完成")
                self._load_changes()
            else:
                QMessageBox.warning(self, "失败", error)

    def _on_cancel(self):
        """取消"""
        selected = self.change_table.selectedItems()
        if not selected:
            return

        change_id = self.change_table.item(selected[0].row(), 1).text()
        
        reply = QMessageBox.question(
            self, "确认", "确定要取消此变更吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = ChangeService.cancel_change(change_id)
            if success:
                QMessageBox.information(self, "成功", "变更单已取消")
                self._load_changes()
            else:
                QMessageBox.warning(self, "失败", error)


class NewChangeDialog(QDialog):
    """新建变更对话框"""
    
    def __init__(self, project_id: str, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.setWindowTitle("新建变更单")
        self.setMinimumSize(500, 400)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("请输入变更标题")
        form.addRow("标题*:", self.title_input)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(CHANGE_TYPES)
        form.addRow("类型*:", self.type_combo)
        
        self.proposer_input = QLineEdit()
        self.proposer_input.setPlaceholderText("请输入提出人")
        form.addRow("提出人:", self.proposer_input)
        
        layout.addLayout(form)
        
        layout.addWidget(QLabel("变更描述:"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("请输入变更描述")
        layout.addWidget(self.description_input)
        
        layout.addWidget(QLabel("变更原因:"))
        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("请输入变更原因")
        layout.addWidget(self.reason_input)
        
        layout.addWidget(QLabel("影响范围:"))
        self.impact_input = QTextEdit()
        self.impact_input.setPlaceholderText("请输入影响范围")
        layout.addWidget(self.impact_input)
        
        btn_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _on_ok(self):
        """确定"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "请输入变更标题")
            return
        
        change_type = self.type_combo.currentText()
        
        change, error = ChangeService.create_change(
            project_id=self.project_id,
            title=title,
            type=change_type,
            description=self.description_input.toPlainText(),
            reason=self.reason_input.toPlainText(),
            impact=self.impact_input.toPlainText(),
            proposer=self.proposer_input.text().strip()
        )
        
        if change:
            QMessageBox.information(self, "成功", f"变更单创建成功: {change.change_id}")
            self.accept()
        else:
            QMessageBox.warning(self, "失败", error)
