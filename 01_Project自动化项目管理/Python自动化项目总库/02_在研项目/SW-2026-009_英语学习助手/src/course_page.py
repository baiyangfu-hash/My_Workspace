"""
课程大纲页面 - 展示分级学习路线和每日任务
高内聚低耦合：通过 CourseManager + GrammarEngine 接口交互
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from cefr_tagger import CEFRPY_AVAILABLE, build_cefr_lexicon
from course_manager import CourseManager
from grammar_engine import GrammarEngine


class CoursePage(QWidget):
    """课程大纲页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.course_mgr = CourseManager()
        self.grammar_engine = GrammarEngine()
        self._setup_ui()
        # 延迟加载数据
        QTimer.singleShot(100, self._refresh_all)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # 标题栏
        title_layout = QHBoxLayout()
        title = QLabel("📋 课程大纲")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        self.level_badge = QLabel("A1")
        self.level_badge.setStyleSheet("""
            QLabel {
                background-color: #4a90d9;
                color: white;
                padding: 6px 16px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(self.level_badge)

        refresh_btn = QPushButton("刷新")
        refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #219a52; }
        """)
        refresh_btn.clicked.connect(self._refresh_all)
        title_layout.addWidget(refresh_btn)

        layout.addLayout(title_layout)

        # 标签页
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                font-size: 14px;
                border: none;
                background: #f0f2f5;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #4a90d9;
                font-weight: bold;
                border-bottom: 2px solid #4a90d9;
            }
        """)

        # Tab 1: 学习概览
        self.overview_tab = QWidget()
        self.tabs.addTab(self.overview_tab, "📊 学习概览")

        # Tab 2: 学习路线
        self.roadmap_tab = QWidget()
        self.tabs.addTab(self.roadmap_tab, "🗺️ 学习路线")

        # Tab 3: 语法课程
        self.grammar_tab = QWidget()
        self.tabs.addTab(self.grammar_tab, "📖 语法课程")

        # Tab 4: 词汇分级
        self.vocab_tab = QWidget()
        self.tabs.addTab(self.vocab_tab, "📝 词汇分级")

        layout.addWidget(self.tabs)

        self._setup_overview_tab()
        self._setup_roadmap_tab()
        self._setup_grammar_tab()
        self._setup_vocab_tab()

    def _setup_overview_tab(self):
        """设置学习概览标签页"""
        layout = QVBoxLayout(self.overview_tab)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # 今日计划卡片
        today_card = QFrame()
        today_card.setStyleSheet("""
            QFrame {
                background-color: #e8f4fc;
                border: 1px solid #bdd7ee;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        today_layout = QVBoxLayout(today_card)

        today_title = QLabel("📅 今日学习计划")
        today_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        today_layout.addWidget(today_title)

        self.today_tasks = QWidget()
        self.today_tasks_layout = QVBoxLayout(self.today_tasks)
        self.today_tasks_layout.setSpacing(8)
        today_layout.addWidget(self.today_tasks)

        layout.addWidget(today_card)

        # 进度卡片
        progress_card = QFrame()
        progress_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        progress_layout = QVBoxLayout(progress_card)

        progress_title = QLabel("📈 学习进度")
        progress_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        progress_layout.addWidget(progress_title)

        # 词汇进度
        vocab_layout = QHBoxLayout()
        vocab_label = QLabel("词汇掌握")
        vocab_label.setStyleSheet("font-size: 14px; color: #34495e; font-weight: bold;")
        vocab_label.setMinimumWidth(100)
        vocab_layout.addWidget(vocab_label)

        self.vocab_progress = QProgressBar()
        self.vocab_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #e9ecef;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4a90d9;
                border-radius: 6px;
            }
        """)
        vocab_layout.addWidget(self.vocab_progress)
        self.vocab_progress_label = QLabel("0/500")
        self.vocab_progress_label.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        self.vocab_progress_label.setMinimumWidth(80)
        vocab_layout.addWidget(self.vocab_progress_label)
        progress_layout.addLayout(vocab_layout)

        # 语法进度
        grammar_layout = QHBoxLayout()
        grammar_label = QLabel("语法掌握")
        grammar_label.setStyleSheet("font-size: 14px; color: #34495e; font-weight: bold;")
        grammar_label.setMinimumWidth(100)
        grammar_layout.addWidget(grammar_label)

        self.grammar_progress = QProgressBar()
        self.grammar_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #e9ecef;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 6px;
            }
        """)
        grammar_layout.addWidget(self.grammar_progress)
        self.grammar_progress_label = QLabel("0/34")
        self.grammar_progress_label.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        self.grammar_progress_label.setMinimumWidth(80)
        grammar_layout.addWidget(self.grammar_progress_label)
        progress_layout.addLayout(grammar_layout)

        layout.addWidget(progress_card)

        # 统计小卡片
        stat_layout = QHBoxLayout()
        stat_layout.setSpacing(12)

        stat_items = [
            ("🔥 连续学习", "0", "天"),
            ("📅 累计学习", "0", "天"),
            ("🎯 目标等级", "B1", ""),
            ("📚 词汇总量", "0", "词"),
        ]
        self.stat_labels = {}

        for label, value, unit in stat_items:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignCenter)
            card_layout.setSpacing(4)

            name_lbl = QLabel(label)
            name_lbl.setStyleSheet("font-size: 12px; color: #7f8c8d;")
            name_lbl.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(name_lbl)

            val_lbl = QLabel(f"{value} {unit}")
            val_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
            val_lbl.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(val_lbl)

            stat_layout.addWidget(card)
            self.stat_labels[label] = val_lbl

        layout.addLayout(stat_layout)
        layout.addStretch()

    def _setup_roadmap_tab(self):
        """设置学习路线标签页"""
        layout = QVBoxLayout(self.roadmap_tab)
        layout.setContentsMargins(20, 20, 20, 20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.roadmap_container = QWidget()
        self.roadmap_layout = QVBoxLayout(self.roadmap_container)
        self.roadmap_layout.setSpacing(16)
        scroll.setWidget(self.roadmap_container)
        layout.addWidget(scroll)

    def _setup_grammar_tab(self):
        """设置语法课程标签页"""
        layout = QHBoxLayout(self.grammar_tab)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # 左侧等级选择
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #f5f6fa;")
        left_panel.setMaximumWidth(200)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 12, 12, 12)

        level_label = QLabel("语法等级")
        level_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        left_layout.addWidget(level_label)

        self.grammar_level_list = QListWidget()
        self.grammar_level_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin: 4px 0;
            }
            QListWidget::item:selected {
                background-color: #4a90d9;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e8f4fc;
            }
        """)
        self.grammar_level_list.addItem("A1 入门 (34个语法点)")
        self.grammar_level_list.addItem("A2 基础 (37个语法点)")
        self.grammar_level_list.addItem("B1 进阶 (42个语法点)")
        self.grammar_level_list.itemClicked.connect(self._on_grammar_level_selected)
        left_layout.addWidget(self.grammar_level_list)

        left_layout.addStretch()
        layout.addWidget(left_panel)

        # 右侧语法详情
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grammar_detail = QWidget()
        self.grammar_detail_layout = QVBoxLayout(self.grammar_detail)
        self.grammar_detail_layout.setSpacing(12)
        scroll.setWidget(self.grammar_detail)
        right_layout.addWidget(scroll)

        layout.addWidget(right_panel)

    def _setup_vocab_tab(self):
        """设置词汇分级标签页"""
        layout = QVBoxLayout(self.vocab_tab)
        layout.setContentsMargins(20, 20, 20, 20)

        # 词汇统计概览
        self.vocab_stats_frame = QFrame()
        self.vocab_stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        self.vocab_stats_layout = QHBoxLayout(self.vocab_stats_frame)
        layout.addWidget(self.vocab_stats_frame)

        # 构建词汇表按钮
        btn_layout = QHBoxLayout()
        self.build_lexicon_btn = QPushButton("🔧 构建 CEFR 词汇表（从词典标注）")
        self.build_lexicon_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        self.build_lexicon_btn.clicked.connect(self._on_build_lexicon)
        btn_layout.addWidget(self.build_lexicon_btn)

        self.build_status = QLabel("")
        self.build_status.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        btn_layout.addWidget(self.build_status)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 分级词汇列表
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.vocab_list_container = QWidget()
        self.vocab_list_layout = QVBoxLayout(self.vocab_list_container)
        self.vocab_list_layout.setSpacing(12)
        scroll.setWidget(self.vocab_list_container)
        layout.addWidget(scroll)

    def _refresh_all(self):
        """刷新所有数据"""
        self._refresh_overview()
        self._refresh_roadmap()
        self._refresh_vocab_stats()
        # 默认选中 A1 语法
        if self.grammar_level_list.currentRow() < 0:
            self.grammar_level_list.setCurrentRow(0)
            self._on_grammar_level_selected(self.grammar_level_list.item(0))

    def _refresh_overview(self):
        """刷新学习概览"""
        progress = self.course_mgr.get_user_progress()

        # 更新等级徽章
        self.level_badge.setText(progress['current_level'])

        # 更新进度条
        self.vocab_progress.setMaximum(progress['vocab_target'])
        self.vocab_progress.setValue(min(progress['vocab_mastered'], progress['vocab_target']))
        self.vocab_progress_label.setText(f"{progress['vocab_mastered']}/{progress['vocab_target']}")

        grammar_total = progress.get('grammar_total', 34)
        self.grammar_progress.setMaximum(grammar_total)
        self.grammar_progress.setValue(min(progress['grammar_completed'], grammar_total))
        self.grammar_progress_label.setText(f"{progress['grammar_completed']}/{grammar_total}")

        # 更新统计卡片
        if "🔥 连续学习" in self.stat_labels:
            self.stat_labels["🔥 连续学习"].setText(f"{progress['streak_days']} 天")
        if "📅 累计学习" in self.stat_labels:
            self.stat_labels["📅 累计学习"].setText(f"{progress['total_days']} 天")
        if "🎯 目标等级" in self.stat_labels:
            self.stat_labels["🎯 目标等级"].setText(progress['target_level'])

        # 词量统计
        vocab_counts = self.course_mgr.get_vocab_stats_by_level()
        total_vocab = sum(vocab_counts.values())
        if "📚 词汇总量" in self.stat_labels:
            self.stat_labels["📚 词汇总量"].setText(f"{total_vocab} 词")

        # 今日计划
        self._refresh_daily_plan()

    def _refresh_daily_plan(self):
        """刷新今日计划"""
        # 清空
        while self.today_tasks_layout.count():
            item = self.today_tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        plan = self.course_mgr.get_daily_plan()

        # 添加任务行
        for task in plan['tasks']:
            task_frame = QFrame()
            task_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px;
                }
            """)
            task_layout = QHBoxLayout(task_frame)
            task_layout.setContentsMargins(12, 8, 12, 8)

            icon = QLabel(task['icon'])
            icon.setStyleSheet("font-size: 20px;")
            task_layout.addWidget(icon)

            task_info = QLabel(f"{task['title']}: {task['description']}")
            task_info.setStyleSheet("font-size: 14px; color: #2c3e50;")
            task_layout.addWidget(task_info)
            task_layout.addStretch()

            self.today_tasks_layout.addWidget(task_frame)

        # 预计时间
        time_label = QLabel(f"⏱️ 预计用时: {plan['estimated_minutes']} 分钟")
        time_label.setStyleSheet("font-size: 13px; color: #7f8c8d; padding-left: 4px;")
        self.today_tasks_layout.addWidget(time_label)

    def _refresh_roadmap(self):
        """刷新学习路线"""
        # 清空
        while self.roadmap_layout.count():
            item = self.roadmap_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        roadmap = self.course_mgr.get_6month_roadmap()

        for phase_key, phase in roadmap.items():
            # 阶段标题
            phase_title = QLabel(f"{phase['title']} ({phase['months']})")
            phase_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 8px 0;")
            self.roadmap_layout.addWidget(phase_title)

            # 月份卡片
            for month_data in phase['months_detail']:
                month_card = QFrame()
                month_card.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border: 1px solid #e0e0e0;
                        border-left: 4px solid #4a90d9;
                        border-radius: 8px;
                        padding: 12px;
                    }
                """)
                card_layout = QVBoxLayout(month_card)
                card_layout.setSpacing(6)

                # 标题行
                header = QLabel(f"第 {month_data['month']} 个月: {month_data['title']}")
                header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a90d9;")
                card_layout.addWidget(header)

                # 详情
                details = f"""
                <table style='width:100%; font-size:13px;'>
                    <tr><td style='color:#7f8c8d; width:80px;'>词汇目标:</td><td>{month_data['vocab_target']}</td></tr>
                    <tr><td style='color:#7f8c8d;'>语法重点:</td><td>{month_data['grammar_focus']}</td></tr>
                    <tr><td style='color:#7f8c8d;'>对话/阅读:</td><td>{month_data['dialogs']}</td></tr>
                    <tr><td style='color:#7f8c8d;'>每日学习:</td><td>{month_data['daily_minutes']} 分钟</td></tr>
                </table>
                """
                detail_label = QLabel(details)
                detail_label.setStyleSheet("font-size: 13px; color: #34495e;")
                card_layout.addWidget(detail_label)

                self.roadmap_layout.addWidget(month_card)

        self.roadmap_layout.addStretch()

    def _on_grammar_level_selected(self, item):
        """选择语法等级"""
        text = item.text()
        level = text[:2]  # A1, A2, B1

        # 清空
        while self.grammar_detail_layout.count():
            child = self.grammar_detail_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 获取分类
        categories = self.grammar_engine.get_categories_by_level(level)

        title = QLabel(f"📖 {level} 语法课程")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        self.grammar_detail_layout.addWidget(title)

        for cat in categories:
            cat_frame = QFrame()
            cat_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
            cat_layout = QVBoxLayout(cat_frame)
            cat_layout.setSpacing(8)

            cat_title = QLabel(f"📌 {cat['name']} ({cat['count']}个语法点)")
            cat_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #e67e22;")
            cat_layout.addWidget(cat_title)

            for point in cat['points']:
                point_text = f"• {point['name']}"
                point_label = QLabel(point_text)
                point_label.setStyleSheet("font-size: 13px; color: #34495e; padding-left: 12px;")
                point_label.setWordWrap(True)
                cat_layout.addWidget(point_label)

            self.grammar_detail_layout.addWidget(cat_frame)

        self.grammar_detail_layout.addStretch()

    def _refresh_vocab_stats(self):
        """刷新词汇统计"""
        # 清空统计
        while self.vocab_stats_layout.count():
            item = self.vocab_stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        vocab_counts = self.course_mgr.get_vocab_stats_by_level()

        level_colors = {
            'A1': '#4a90d9', 'A2': '#27ae60', 'B1': '#e67e22',
            'B2': '#e74c3c', 'C1': '#9b59b6', 'C2': '#2c3e50',
        }

        for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            count = vocab_counts.get(level, 0)
            color = level_colors.get(level, '#7f8c8d')

            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignCenter)
            card_layout.setSpacing(4)

            level_lbl = QLabel(level)
            level_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
            level_lbl.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(level_lbl)

            count_lbl = QLabel(str(count))
            count_lbl.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
            count_lbl.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(count_lbl)

            label_lbl = QLabel("词")
            label_lbl.setStyleSheet("font-size: 11px; color: #7f8c8d;")
            label_lbl.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(label_lbl)

            self.vocab_stats_layout.addWidget(card)

        # 清空词汇列表
        while self.vocab_list_layout.count():
            item = self.vocab_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 显示各等级词汇样例
        if vocab_counts:
            list_title = QLabel("📋 各等级词汇预览")
            list_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-top: 8px;")
            self.vocab_list_layout.addWidget(list_title)

            for level in ['A1', 'A2', 'B1']:
                if vocab_counts.get(level, 0) > 0:
                    words = self.course_mgr.get_words_for_study(level, 10)
                    if words:
                        level_frame = QFrame()
                        level_frame.setStyleSheet("""
                            QFrame {
                                background-color: white;
                                border: 1px solid #e0e0e0;
                                border-radius: 8px;
                                padding: 12px;
                            }
                        """)
                        fl_layout = QVBoxLayout(level_frame)
                        fl_layout.setSpacing(4)

                        fl_title = QLabel(f"{level} ({len(words)} 个词汇样本)")
                        fl_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {level_colors.get(level)};")
                        fl_layout.addWidget(fl_title)

                        word_text = ", ".join([w['word'] for w in words[:15]])
                        word_lbl = QLabel(word_text)
                        word_lbl.setStyleSheet("font-size: 13px; color: #34495e;")
                        word_lbl.setWordWrap(True)
                        fl_layout.addWidget(word_lbl)

                        self.vocab_list_layout.addWidget(level_frame)

        self.vocab_list_layout.addStretch()

    def _on_build_lexicon(self):
        """构建 CEFR 词汇表"""
        if not CEFRPY_AVAILABLE:
            QMessageBox.warning(self, "不可用", "cefrpy 未安装，请先执行: pip install cefrpy")
            return

        self.build_lexicon_btn.setEnabled(False)
        self.build_status.setText("正在标注词汇... 这可能需要几分钟")

        # 使用 QTimer 在后台执行
        def _do_build():
            success, msg = build_cefr_lexicon(limit=5000)
            if success:
                self.build_status.setText(f"✅ {msg}")
                self._refresh_vocab_stats()
            else:
                self.build_status.setText(f"❌ {msg}")
            self.build_lexicon_btn.setEnabled(True)

        QTimer.singleShot(100, _do_build)

    def refresh(self):
        """外部调用刷新"""
        self._refresh_all()
