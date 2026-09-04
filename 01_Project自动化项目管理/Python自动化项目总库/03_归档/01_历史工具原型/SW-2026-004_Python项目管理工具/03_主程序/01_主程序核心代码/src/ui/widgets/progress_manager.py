# -*- coding: utf-8 -*-
"""
项目进度管理控件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QProgressBar,
    QPushButton, QLineEdit, QComboBox, QLabel,
    QDialog, QFormLayout, QDateEdit, QTextEdit,
    QMessageBox, QGroupBox, QGridLayout, QScrollArea,
    QFrame, QHeaderView
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QBrush

from src.services.progress_service import ProgressService
from src.services.project_service import ProjectService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

STATUS_COLORS = {
    "pending": "#9E9E9E",
    "in_progress": "#2196F3",
    "completed": "#4CAF50",
    "delayed": "#F44336"
}

STATUS_NAMES = {
    "pending": "待开始",
    "in_progress": "进行中",
    "completed": "已完成",
    "delayed": "已延期"
}

PRIORITY_NAMES = {
    "high": "高",
    "medium": "中",
    "low": "低"
}

class ProgressManagerWidget(QWidget):
    """项目进度管理控件"""
    
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
        
        stats_group = QGroupBox("进度统计")
        stats_layout = QGridLayout(stats_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("总体进度: %p%")
        stats_layout.addWidget(self.progress_bar, 0, 0, 1, 4)
        
        self.ms_stats_label = QLabel("里程碑: 总计 0 | 待开始 0 | 进行中 0 | 已完成 0")
        stats_layout.addWidget(self.ms_stats_label, 1, 0, 1, 2)
        
        self.task_stats_label = QLabel("任务: 总计 0 | 待开始 0 | 进行中 0 | 已完成 0")
        stats_layout.addWidget(self.task_stats_label, 1, 2, 1, 2)
        
        layout.addWidget(stats_group)
        
        toolbar = QHBoxLayout()
        
        self.new_ms_btn = QPushButton("新建里程碑")
        self.new_ms_btn.clicked.connect(self._on_new_milestone)
        toolbar.addWidget(self.new_ms_btn)
        
        self.new_task_btn = QPushButton("新建任务")
        self.new_task_btn.clicked.connect(self._on_new_task)
        toolbar.addWidget(self.new_task_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._load_data)
        toolbar.addWidget(self.refresh_btn)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_tree = QTreeWidget()
        self.progress_tree.setHeaderLabels(["名称", "状态", "进度", "开始日期", "结束日期"])
        self.progress_tree.setColumnWidth(0, 200)
        self.progress_tree.setColumnWidth(1, 80)
        self.progress_tree.setColumnWidth(2, 100)
        self.progress_tree.setColumnWidth(3, 100)
        self.progress_tree.setColumnWidth(4, 100)
        self.progress_tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        left_layout.addWidget(self.progress_tree)
        
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.gantt_scroll = QScrollArea()
        self.gantt_scroll.setWidgetResizable(True)
        self.gantt_scroll.setMinimumWidth(400)
        
        self.gantt_widget = QWidget()
        self.gantt_layout = QVBoxLayout(self.gantt_widget)
        self.gantt_scroll.setWidget(self.gantt_widget)
        
        right_layout.addWidget(QLabel("甘特图"))
        right_layout.addWidget(self.gantt_scroll)
        
        splitter.addWidget(right_widget)
        
        splitter.setSizes([500, 500])
        
        layout.addWidget(splitter)
        
        self._load_projects()
    
    def _load_projects(self):
        """加载项目列表"""
        self.project_combo.clear()
        
        projects, _ = ProjectService.list_projects(status="active", size=100)
        for project in projects:
            self.project_combo.addItem(f"{project.code} - {project.name}", project.project_id)
        
        if self.project_combo.count() > 0:
            self.current_project_id = self.project_combo.currentData()
            self._load_data()
    
    def _on_project_changed(self, index: int):
        """项目变更"""
        self.current_project_id = self.project_combo.currentData()
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        self.progress_tree.clear()
        
        if not self.current_project_id:
            return
        
        self._load_progress_tree()
        self._load_gantt_chart()
        self._update_statistics()
    
    def _load_progress_tree(self):
        """加载进度树"""
        milestones = ProgressService.list_milestones(self.current_project_id)
        
        for ms in milestones:
            ms_item = QTreeWidgetItem([
                ms.name,
                STATUS_NAMES.get(ms.status, ms.status),
                f"{ms.progress}%",
                ms.start_date.strftime("%Y-%m-%d") if ms.start_date else "-",
                ms.end_date.strftime("%Y-%m-%d") if ms.end_date else "-"
            ])
            ms_item.setData(0, Qt.UserRole, {"type": "milestone", "id": ms.milestone_id})
            ms_item.setForeground(1, QBrush(QColor(STATUS_COLORS.get(ms.status, "#000"))))
            ms_item.setFont(0, QFont("Microsoft YaHei", 10, QFont.Bold))
            self.progress_tree.addTopLevelItem(ms_item)
            
            tasks = ProgressService.list_tasks(self.current_project_id, ms.milestone_id)
            for task in tasks:
                task_item = QTreeWidgetItem([
                    task.name,
                    STATUS_NAMES.get(task.status, task.status),
                    f"{task.progress}%",
                    task.start_date.strftime("%Y-%m-%d") if task.start_date else "-",
                    task.end_date.strftime("%Y-%m-%d") if task.end_date else "-"
                ])
                task_item.setData(0, Qt.UserRole, {"type": "task", "id": task.task_id})
                task_item.setForeground(1, QBrush(QColor(STATUS_COLORS.get(task.status, "#000"))))
                ms_item.addChild(task_item)
            
            ms_item.setExpanded(True)
    
    def _load_gantt_chart(self):
        """加载甘特图"""
        while self.gantt_layout.count():
            item = self.gantt_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                pass
        
        gantt_data = ProgressService.get_gantt_data(self.current_project_id)
        
        if not gantt_data["milestones"]:
            self.gantt_layout.addWidget(QLabel("暂无数据，请先创建里程碑和任务"))
            return
        
        all_dates = []
        for ms in gantt_data["milestones"]:
            if ms["start_date"]:
                all_dates.append(ms["start_date"])
            if ms["end_date"]:
                all_dates.append(ms["end_date"])
        for task in gantt_data["tasks"]:
            if task["start_date"]:
                all_dates.append(task["start_date"])
            if task["end_date"]:
                all_dates.append(task["end_date"])
        
        if not all_dates:
            self.gantt_layout.addWidget(QLabel("暂无日期数据"))
            return
        
        from datetime import datetime
        all_dates = [datetime.fromisoformat(d).date() for d in all_dates]
        min_date = min(all_dates)
        max_date = max(all_dates)
        
        date_range = (max_date - min_date).days + 1

        # 修复P2-#16: 动态计算显示范围，最大不超过90天，避免硬编码30天限制
        display_range = min(date_range, 90)

        header = QHBoxLayout()
        header.addWidget(QLabel(""))
        for i in range(display_range):
            day = min_date + __import__('datetime').timedelta(days=i)
            header.addWidget(QLabel(day.strftime("%m/%d")))
        self.gantt_layout.addLayout(header)
        
        for ms in gantt_data["milestones"]:
            ms_row = QHBoxLayout()
            ms_row.addWidget(QLabel(f"【里程碑】{ms['name']}"))
            
            if ms["start_date"] and ms["end_date"]:
                start = datetime.fromisoformat(ms["start_date"]).date()
                end = datetime.fromisoformat(ms["end_date"]).date()
                
                for i in range(display_range):
                    current_date = min_date + __import__('datetime').timedelta(days=i)
                    bar = QFrame()
                    bar.setFixedHeight(20)
                    
                    if start <= current_date <= end:
                        bar.setStyleSheet(f"background-color: {STATUS_COLORS.get(ms['status'], '#2196F3')}; border-radius: 3px;")
                    else:
                        bar.setStyleSheet("background-color: transparent;")
                    
                    ms_row.addWidget(bar)
            
            self.gantt_layout.addLayout(ms_row)
            
            ms_tasks = [t for t in gantt_data["tasks"] if t["milestone_id"] == ms["id"]]
            for task in ms_tasks:
                task_row = QHBoxLayout()
                task_row.addWidget(QLabel(f"  └ {task['name']}"))
                
                if task["start_date"] and task["end_date"]:
                    start = datetime.fromisoformat(task["start_date"]).date()
                    end = datetime.fromisoformat(task["end_date"]).date()
                    
                    for i in range(display_range):
                        current_date = min_date + __import__('datetime').timedelta(days=i)
                        bar = QFrame()
                        bar.setFixedHeight(15)
                        
                        if start <= current_date <= end:
                            bar.setStyleSheet(f"background-color: {STATUS_COLORS.get(task['status'], '#4CAF50')}; border-radius: 2px;")
                        else:
                            bar.setStyleSheet("background-color: transparent;")
                        
                        task_row.addWidget(bar)
                
                self.gantt_layout.addLayout(task_row)
        
        self.gantt_layout.addStretch()
    
    def _update_statistics(self):
        """更新统计信息"""
        if not self.current_project_id:
            return
        
        stats = ProgressService.get_statistics(self.current_project_id)
        
        self.progress_bar.setValue(stats.get("overall_progress", 0))
        
        ms_stats = stats.get("milestones", {})
        self.ms_stats_label.setText(
            f"里程碑: 总计 {ms_stats.get('total', 0)} | "
            f"待开始 {ms_stats.get('pending', 0)} | "
            f"进行中 {ms_stats.get('in_progress', 0)} | "
            f"已完成 {ms_stats.get('completed', 0)}"
        )
        
        task_stats = stats.get("tasks", {})
        self.task_stats_label.setText(
            f"任务: 总计 {task_stats.get('total', 0)} | "
            f"待开始 {task_stats.get('pending', 0)} | "
            f"进行中 {task_stats.get('in_progress', 0)} | "
            f"已完成 {task_stats.get('completed', 0)}"
        )
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """双击编辑"""
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        
        if data["type"] == "milestone":
            self._edit_milestone(data["id"])
        elif data["type"] == "task":
            self._edit_task(data["id"])
    
    def _edit_milestone(self, milestone_id: str):
        """编辑里程碑"""
        milestone = ProgressService.get_milestone(milestone_id)
        if not milestone:
            return
        
        dialog = MilestoneDialog(self.current_project_id, milestone, self)
        if dialog.exec_() == QDialog.Accepted:
            self._load_data()
    
    def _edit_task(self, task_id: str):
        """编辑任务"""
        task = ProgressService.get_task(task_id)
        if not task:
            return
        
        dialog = TaskDialog(self.current_project_id, task.milestone_id, task, self)
        if dialog.exec_() == QDialog.Accepted:
            self._load_data()
    
    def _on_new_milestone(self):
        """新建里程碑"""
        if not self.current_project_id:
            QMessageBox.warning(self, "提示", "请先选择项目")
            return
        
        dialog = MilestoneDialog(self.current_project_id, None, self)
        if dialog.exec_() == QDialog.Accepted:
            self._load_data()
    
    def _on_new_task(self):
        """新建任务"""
        if not self.current_project_id:
            QMessageBox.warning(self, "提示", "请先选择项目")
            return
        
        milestones = ProgressService.list_milestones(self.current_project_id)
        if not milestones:
            QMessageBox.warning(self, "提示", "请先创建里程碑")
            return
        
        milestone_id = milestones[0].milestone_id
        dialog = TaskDialog(self.current_project_id, milestone_id, None, self)
        if dialog.exec_() == QDialog.Accepted:
            self._load_data()


class MilestoneDialog(QDialog):
    """里程碑对话框"""
    
    def __init__(self, project_id: str, milestone=None, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.milestone = milestone
        self.setWindowTitle("编辑里程碑" if milestone else "新建里程碑")
        self.setMinimumSize(400, 300)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入里程碑名称")
        if self.milestone:
            self.name_input.setText(self.milestone.name)
        form.addRow("名称*:", self.name_input)
        
        self.status_combo = QComboBox()
        for status, name in STATUS_NAMES.items():
            self.status_combo.addItem(name, status)
        if self.milestone:
            index = self.status_combo.findData(self.milestone.status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        form.addRow("状态:", self.status_combo)
        
        self.progress_input = QLineEdit()
        self.progress_input.setPlaceholderText("0-100")
        if self.milestone:
            self.progress_input.setText(str(self.milestone.progress))
        else:
            self.progress_input.setText("0")
        form.addRow("进度%:", self.progress_input)
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        if self.milestone and self.milestone.start_date:
            self.start_date.setDate(QDate(
                self.milestone.start_date.year,
                self.milestone.start_date.month,
                self.milestone.start_date.day
            ))
        form.addRow("开始日期:", self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addDays(7))
        if self.milestone and self.milestone.end_date:
            self.end_date.setDate(QDate(
                self.milestone.end_date.year,
                self.milestone.end_date.month,
                self.milestone.end_date.day
            ))
        form.addRow("结束日期:", self.end_date)
        
        layout.addLayout(form)
        
        layout.addWidget(QLabel("描述:"))
        self.description_input = QTextEdit()
        if self.milestone:
            self.description_input.setText(self.milestone.description or "")
        layout.addWidget(self.description_input)
        
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
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入里程碑名称")
            return
        
        data = {
            "name": name,
            "status": self.status_combo.currentData(),
            "progress": int(self.progress_input.text() or 0),
            "start_date": self.start_date.date().toPyDate(),
            "end_date": self.end_date.date().toPyDate(),
            "description": self.description_input.toPlainText()
        }
        
        if self.milestone:
            ms, error = ProgressService.update_milestone(self.milestone.milestone_id, data)
        else:
            ms, error = ProgressService.create_milestone(
                project_id=self.project_id,
                name=name,
                description=data["description"],
                start_date=data["start_date"],
                end_date=data["end_date"]
            )
        
        if ms:
            QMessageBox.information(self, "成功", "保存成功")
            self.accept()
        else:
            QMessageBox.warning(self, "失败", error)


class TaskDialog(QDialog):
    """任务对话框"""
    
    def __init__(self, project_id: str, milestone_id: str = None, task=None, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.milestone_id = milestone_id
        self.task = task
        self.setWindowTitle("编辑任务" if task else "新建任务")
        self.setMinimumSize(400, 350)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入任务名称")
        if self.task:
            self.name_input.setText(self.task.name)
        form.addRow("名称*:", self.name_input)
        
        self.milestone_combo = QComboBox()
        milestones = ProgressService.list_milestones(self.project_id)
        for ms in milestones:
            self.milestone_combo.addItem(ms.name, ms.milestone_id)
        if self.task and self.task.milestone_id:
            index = self.milestone_combo.findData(self.task.milestone_id)
            if index >= 0:
                self.milestone_combo.setCurrentIndex(index)
        elif self.milestone_id:
            index = self.milestone_combo.findData(self.milestone_id)
            if index >= 0:
                self.milestone_combo.setCurrentIndex(index)
        form.addRow("所属里程碑:", self.milestone_combo)
        
        self.assignee_input = QLineEdit()
        self.assignee_input.setPlaceholderText("请输入负责人")
        if self.task:
            self.assignee_input.setText(self.task.assignee or "")
        form.addRow("负责人:", self.assignee_input)
        
        self.status_combo = QComboBox()
        for status, name in STATUS_NAMES.items():
            self.status_combo.addItem(name, status)
        if self.task:
            index = self.status_combo.findData(self.task.status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        form.addRow("状态:", self.status_combo)
        
        self.priority_combo = QComboBox()
        for priority, name in PRIORITY_NAMES.items():
            self.priority_combo.addItem(name, priority)
        if self.task:
            index = self.priority_combo.findData(self.task.priority)
            if index >= 0:
                self.priority_combo.setCurrentIndex(index)
        form.addRow("优先级:", self.priority_combo)
        
        self.progress_input = QLineEdit()
        self.progress_input.setPlaceholderText("0-100")
        if self.task:
            self.progress_input.setText(str(self.task.progress))
        else:
            self.progress_input.setText("0")
        form.addRow("进度%:", self.progress_input)
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        if self.task and self.task.start_date:
            self.start_date.setDate(QDate(
                self.task.start_date.year,
                self.task.start_date.month,
                self.task.start_date.day
            ))
        form.addRow("开始日期:", self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addDays(3))
        if self.task and self.task.end_date:
            self.end_date.setDate(QDate(
                self.task.end_date.year,
                self.task.end_date.month,
                self.task.end_date.day
            ))
        form.addRow("结束日期:", self.end_date)
        
        layout.addLayout(form)
        
        layout.addWidget(QLabel("描述:"))
        self.description_input = QTextEdit()
        if self.task:
            self.description_input.setText(self.task.description or "")
        layout.addWidget(self.description_input)
        
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
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入任务名称")
            return
        
        data = {
            "name": name,
            "milestone_id": self.milestone_combo.currentData(),
            "assignee": self.assignee_input.text().strip(),
            "status": self.status_combo.currentData(),
            "priority": self.priority_combo.currentData(),
            "progress": int(self.progress_input.text() or 0),
            "start_date": self.start_date.date().toPyDate(),
            "end_date": self.end_date.date().toPyDate(),
            "description": self.description_input.toPlainText()
        }
        
        if self.task:
            t, error = ProgressService.update_task(self.task.task_id, data)
        else:
            t, error = ProgressService.create_task(
                project_id=self.project_id,
                name=name,
                milestone_id=data["milestone_id"],
                description=data["description"],
                assignee=data["assignee"],
                start_date=data["start_date"],
                end_date=data["end_date"],
                priority=data["priority"]
            )
        
        if t:
            QMessageBox.information(self, "成功", "保存成功")
            self.accept()
        else:
            QMessageBox.warning(self, "失败", error)
