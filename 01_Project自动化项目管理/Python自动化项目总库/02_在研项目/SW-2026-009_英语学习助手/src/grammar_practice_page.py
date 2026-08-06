"""
语法练习页面 - 互动语法练习 UI
高内聚低耦合：通过 GrammarPracticeEngine 接口交互
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from grammar_engine import GrammarEngine
from grammar_practice import GrammarPracticeEngine


class GrammarPracticePage(QWidget):
    """语法练习页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.practice_engine = GrammarPracticeEngine()
        self.grammar_engine = GrammarEngine()
        self.current_level = "A1"
        self.current_point = None
        self.current_exercises = []
        self.current_exercise_idx = 0
        self.score = 0
        self.total_answered = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        # 标题
        title_layout = QHBoxLayout()
        title = QLabel("📖 语法练习")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        self.score_label = QLabel("正确: 0/0")
        self.score_label.setStyleSheet("font-size: 14px; color: #27ae60; font-weight: bold;")
        title_layout.addWidget(self.score_label)
        layout.addLayout(title_layout)

        # 两栏布局
        two_col = QHBoxLayout()
        two_col.setSpacing(16)

        # 左栏：语法点列表
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #f5f6fa; border-radius: 12px;")
        left_panel.setMaximumWidth(280)
        left_panel.setMinimumWidth(240)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(8)

        # 等级选择
        level_layout = QHBoxLayout()
        level_label = QLabel("等级:")
        level_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        level_layout.addWidget(level_label)

        self.level_combo = QListWidget()
        self.level_combo.setMaximumHeight(30)
        self.level_combo.setStyleSheet("""
            QListWidget { background: white; border: 1px solid #d0d0d0; border-radius: 6px; font-size: 12px; }
            QListWidget::item { padding: 4px 8px; }
            QListWidget::item:selected { background: #4a90d9; color: white; }
        """)
        for lv in ["A1", "A2", "B1"]:
            self.level_combo.addItem(lv)
        self.level_combo.setCurrentRow(0)
        self.level_combo.currentRowChanged.connect(self._on_level_changed)
        level_layout.addWidget(self.level_combo)
        left_layout.addLayout(level_layout)

        # 语法点列表
        self.point_list = QListWidget()
        self.point_list.setStyleSheet("""
            QListWidget { background: transparent; border: none; font-size: 13px; }
            QListWidget::item { padding: 10px 8px; border-radius: 6px; margin: 2px 0; }
            QListWidget::item:selected { background-color: #4a90d9; color: white; }
            QListWidget::item:hover { background-color: #e8f4fc; }
        """)
        self.point_list.itemClicked.connect(self._on_point_selected)
        left_layout.addWidget(self.point_list)

        # 语法点说明
        self.point_info = QLabel("选择一个语法点开始练习")
        self.point_info.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 8px;")
        self.point_info.setWordWrap(True)
        self.point_info.hide()
        left_layout.addWidget(self.point_info)

        two_col.addWidget(left_panel)

        # 右栏：练习区域
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.content_stack = QStackedWidget()

        # 欢迎页
        self.welcome_widget = QWidget()
        wl = QVBoxLayout(self.welcome_widget)
        wl.setAlignment(Qt.AlignCenter)
        welcome_label = QLabel("👈 从左侧选择一个语法点\n开始练习")
        welcome_label.setStyleSheet("font-size: 18px; color: #bdc3c7;")
        welcome_label.setAlignment(Qt.AlignCenter)
        wl.addWidget(welcome_label)
        self.content_stack.addWidget(self.welcome_widget)

        # 练习页
        self.practice_widget = QWidget()
        self._setup_practice_ui()
        self.content_stack.addWidget(self.practice_widget)

        # 结果页
        self.result_widget = QWidget()
        self._setup_result_ui()
        self.content_stack.addWidget(self.result_widget)

        right_layout.addWidget(self.content_stack)
        two_col.addWidget(right_panel, 1)

        layout.addLayout(two_col)

        # 加载初始列表
        self._load_point_list("A1")

    def _setup_practice_ui(self):
        """练习 UI"""
        layout = QVBoxLayout(self.practice_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # 进度
        self.exercise_progress = QProgressBar()
        self.exercise_progress.setStyleSheet("""
            QProgressBar { border: none; border-radius: 4px; background: #e0e0e0; height: 6px; text-align: center; }
            QProgressBar::chunk { background: #e67e22; border-radius: 4px; }
        """)
        self.exercise_progress.setMaximumHeight(6)
        self.exercise_progress.setTextVisible(False)
        layout.addWidget(self.exercise_progress)

        # 语法点标题
        self.practice_title = QLabel("")
        self.practice_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        self.practice_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.practice_title)

        # 题目类型标签
        self.exercise_type_label = QLabel("")
        self.exercise_type_label.setStyleSheet("font-size: 12px; color: #95a5a6;")
        self.exercise_type_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.exercise_type_label)

        # 题目卡片
        self.question_frame = QFrame()
        self.question_frame.setStyleSheet("QFrame { background: white; border: 2px solid #e0e0e0; border-radius: 12px; padding: 30px; }")
        self.question_frame.setMinimumSize(500, 300)
        qf_layout = QVBoxLayout(self.question_frame)
        qf_layout.setSpacing(16)
        qf_layout.setAlignment(Qt.AlignCenter)

        self.question_label = QLabel("")
        self.question_label.setStyleSheet("font-size: 16px; color: #2c3e50;")
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setWordWrap(True)
        qf_layout.addWidget(self.question_label)

        # 选项区域（动态填充）
        self.options_container = QWidget()
        self.options_layout = QVBoxLayout(self.options_container)
        self.options_layout.setSpacing(10)
        self.options_layout.setAlignment(Qt.AlignCenter)
        qf_layout.addWidget(self.options_container)

        # 反馈
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.feedback_label.hide()
        qf_layout.addWidget(self.feedback_label)

        layout.addWidget(self.question_frame, alignment=Qt.AlignCenter)

        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(12)

        self.next_btn = QPushButton("下一题 →")
        self.next_btn.setStyleSheet("QPushButton { padding: 10px 30px; background: #4a90d9; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; } QPushButton:hover { background: #357abd; }")
        self.next_btn.clicked.connect(self._on_next_exercise)
        self.next_btn.hide()
        btn_layout.addWidget(self.next_btn)

        self.skip_btn = QPushButton("跳过")
        self.skip_btn.setStyleSheet("QPushButton { padding: 10px 20px; background: #95a5a6; color: white; border: none; border-radius: 8px; font-size: 13px; } QPushButton:hover { background: #7f8c8d; }")
        self.skip_btn.clicked.connect(self._on_next_exercise)
        btn_layout.addWidget(self.skip_btn)

        layout.addLayout(btn_layout)

    def _setup_result_ui(self):
        """结果 UI"""
        layout = QVBoxLayout(self.result_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        result_frame = QFrame()
        result_frame.setStyleSheet("QFrame { background: white; border: 2px solid #e0e0e0; border-radius: 16px; padding: 40px; }")
        result_frame.setMinimumSize(400, 300)
        rf_layout = QVBoxLayout(result_frame)
        rf_layout.setAlignment(Qt.AlignCenter)
        rf_layout.setSpacing(16)

        self.result_icon = QLabel("🎉")
        self.result_icon.setStyleSheet("font-size: 48px;")
        self.result_icon.setAlignment(Qt.AlignCenter)
        rf_layout.addWidget(self.result_icon)

        self.result_title = QLabel("练习完成！")
        self.result_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        self.result_title.setAlignment(Qt.AlignCenter)
        rf_layout.addWidget(self.result_title)

        self.result_score = QLabel("")
        self.result_score.setStyleSheet("font-size: 18px; color: #27ae60;")
        self.result_score.setAlignment(Qt.AlignCenter)
        rf_layout.addWidget(self.result_score)

        self.result_detail = QLabel("")
        self.result_detail.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        self.result_detail.setAlignment(Qt.AlignCenter)
        rf_layout.addWidget(self.result_detail)

        layout.addWidget(result_frame, alignment=Qt.AlignCenter)

        back_btn = QPushButton("返回选择语法点")
        back_btn.setStyleSheet("QPushButton { padding: 12px 30px; background: #4a90d9; color: white; border: none; border-radius: 8px; font-size: 14px; } QPushButton:hover { background: #357abd; }")
        back_btn.clicked.connect(self._on_back_to_list)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

    def _load_point_list(self, level):
        """加载语法点列表"""
        self.point_list.clear()
        categories = self.grammar_engine.get_categories_by_level(level)
        for cat in categories:
            # 添加分类标题
            cat_item = f"📌 {cat['name']} ({cat['count']})"
            self.point_list.addItem(cat_item)
            for point in cat['points']:
                self.point_list.addItem(f"    {point['name']}")

    def _on_level_changed(self, row):
        """切换等级"""
        levels = ["A1", "A2", "B1"]
        if 0 <= row < len(levels):
            self.current_level = levels[row]
            self._load_point_list(self.current_level)

    def _on_point_selected(self, item):
        """选择语法点"""
        text = item.text().strip()
        if text.startswith('📌'):
            return  # 跳过分类标题

        # 提取语法点名称
        name = text.strip()
        points = self.grammar_engine.get_points_by_level(self.current_level)
        for p in points:
            if p['name'] == name:
                self.current_point = p
                self.point_info.setText(f"📖 {p['name']}\n{p['explanation']}")
                self.point_info.show()
                self._start_practice(p)
                return

    def _start_practice(self, point):
        """开始练习"""
        self.current_point = point
        self.current_exercises = self.practice_engine.generate_exercises(point)
        self.current_exercise_idx = 0
        self.score = 0
        self.total_answered = 0

        if not self.current_exercises:
            self.question_label.setText("该语法点暂无练习题\n（例句不足，无法自动生成）")
            self.options_container.hide()
            self.feedback_label.hide()
            self.skip_btn.hide()
            self.next_btn.setText("返回")
            self.next_btn.show()
            self.content_stack.setCurrentIndex(1)
            return

        self.exercise_progress.setMaximum(len(self.current_exercises))
        self.exercise_progress.setValue(0)
        self.practice_title.setText(f"📖 {point['name']}")
        self.content_stack.setCurrentIndex(1)
        self._show_exercise()

    def _show_exercise(self):
        """显示当前练习题"""
        if self.current_exercise_idx >= len(self.current_exercises):
            self._show_result()
            return

        ex = self.current_exercises[self.current_exercise_idx]
        self.exercise_progress.setValue(self.current_exercise_idx)

        type_names = {'fill': '📝 填空题', 'choice': '✅ 选择题', 'correct': '🔧 改错题', 'order': '🔄 排序题'}
        self.exercise_type_label.setText(type_names.get(ex['type'], ''))

        self.feedback_label.hide()
        self.next_btn.hide()
        self.skip_btn.show()

        # 清空选项
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if ex['type'] == 'fill':
            self._show_fill_exercise(ex)
        elif ex['type'] == 'choice':
            self._show_choice_exercise(ex)
        elif ex['type'] == 'correct':
            self._show_correct_exercise(ex)
        elif ex['type'] == 'order':
            self._show_order_exercise(ex)

    def _show_fill_exercise(self, ex):
        """填空题"""
        self.question_label.setText(ex['question'])
        self.options_container.show()

        for opt in ex['options']:
            btn = QPushButton(opt)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { padding: 10px 20px; border: 2px solid #e0e0e0; border-radius: 8px;
                    background: white; color: #2c3e50; font-size: 15px; font-weight: bold; min-width: 80px; }
                QPushButton:hover { border-color: #4a90d9; background: #f8fbfe; }
            """)
            btn.clicked.connect(lambda checked, o=opt, a=ex['answer']: self._check_answer(o, a))
            self.options_layout.addWidget(btn)

    def _show_choice_exercise(self, ex):
        """选择题"""
        self.question_label.setText(ex['question'])
        self.options_container.show()

        for opt in ex['options']:
            btn = QPushButton(opt)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { padding: 10px 16px; border: 2px solid #e0e0e0; border-radius: 8px;
                    background: white; color: #2c3e50; font-size: 13px; text-align: left; }
                QPushButton:hover { border-color: #4a90d9; background: #f8fbfe; }
            """)
            btn.clicked.connect(lambda checked, o=opt, a=ex['answer']: self._check_answer(o, a))
            self.options_layout.addWidget(btn)

    def _show_correct_exercise(self, ex):
        """改错题"""
        self.question_label.setText(ex['question'])
        self.options_container.show()

        for opt in ex['options']:
            btn = QPushButton(opt)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { padding: 10px 20px; border: 2px solid #e0e0e0; border-radius: 8px;
                    background: white; color: #2c3e50; font-size: 14px; font-weight: bold; min-width: 100px; }
                QPushButton:hover { border-color: #e67e22; background: #fef5e7; }
            """)
            btn.clicked.connect(lambda checked, o=opt, a=ex['answer']: self._check_answer(o, a))
            self.options_layout.addWidget(btn)

    def _show_order_exercise(self, ex):
        """排序题"""
        self.question_label.setText(ex['question'])
        self.options_container.show()

        # 显示打乱的单词作为按钮
        words_container = QWidget()
        words_layout = QHBoxLayout(words_container)
        words_layout.setSpacing(6)
        words_layout.setAlignment(Qt.AlignCenter)

        for w in ex['options']:
            btn = QPushButton(w)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(60, 36)
            btn.setStyleSheet("""
                QPushButton { border: 2px solid #4a90d9; border-radius: 6px; background: #e8f4fc;
                    color: #2c3e50; font-size: 13px; font-weight: bold; }
                QPushButton:hover { background: #d0e8f7; }
            """)
            words_layout.addWidget(btn)

        self.options_layout.addWidget(words_container)

        # 显示正确答案提示
        hint = QLabel(f"正确答案: {ex['answer']}")
        hint.setStyleSheet("font-size: 13px; color: #7f8c8d; font-style: italic;")
        hint.setAlignment(Qt.AlignCenter)
        self.options_layout.addWidget(hint)

        # 自动标记为需要复习（排序题作为展示）
        self.total_answered += 1
        self._update_score_label()
        QTimer.singleShot(3000, self._on_next_exercise)

    def _check_answer(self, selected, answer):
        """检查答案"""
        self.total_answered += 1
        is_correct = (selected.strip().lower() == answer.strip().lower())

        # 禁用所有按钮
        for i in range(self.options_layout.count()):
            w = self.options_layout.itemAt(i).widget()
            if isinstance(w, QPushButton):
                w.setEnabled(False)
                if w.text().strip().lower() == answer.strip().lower():
                    w.setStyleSheet("QPushButton { padding: 10px 16px; border: 2px solid #27ae60; border-radius: 8px; background: #d5f5e3; color: #27ae60; font-size: 14px; }")
                elif w.text().strip().lower() == selected.strip().lower() and not is_correct:
                    w.setStyleSheet("QPushButton { padding: 10px 16px; border: 2px solid #e74c3c; border-radius: 8px; background: #fadbd8; color: #e74c3c; font-size: 14px; }")

        self.feedback_label.show()
        if is_correct:
            self.score += 1
            self.feedback_label.setText("✅ 正确！")
            self.feedback_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        else:
            self.feedback_label.setText(f"❌ 正确答案: {answer}")
            self.feedback_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")

        self.skip_btn.hide()
        self.next_btn.show()
        self._update_score_label()

    def _on_next_exercise(self):
        """下一题"""
        self.current_exercise_idx += 1
        if self.current_exercise_idx >= len(self.current_exercises):
            self._show_result()
        else:
            self._show_exercise()

    def _show_result(self):
        """显示结果"""
        total = len(self.current_exercises)
        pct = round(self.score / total * 100) if total > 0 else 0

        if pct >= 80:
            self.result_icon.setText("🎉")
            self.result_title.setText("太棒了！")
        elif pct >= 60:
            self.result_icon.setText("👍")
            self.result_title.setText("不错！")
        else:
            self.result_icon.setText("💪")
            self.result_title.setText("继续加油！")

        self.result_score.setText(f"正确率: {self.score}/{total} ({pct}%)")
        self.result_detail.setText(f"语法点: {self.current_point['name']}\n建议: {'已掌握，可以进入下一个' if pct >= 80 else '建议复习后再练习'}")

        self.content_stack.setCurrentIndex(2)

    def _on_back_to_list(self):
        """返回列表"""
        self.content_stack.setCurrentIndex(0)
        self.point_info.hide()

    def _update_score_label(self):
        """更新分数显示"""
        self.score_label.setText(f"正确: {self.score}/{self.total_answered}")

    def refresh(self):
        """外部调用刷新"""
        self._load_point_list(self.current_level)
