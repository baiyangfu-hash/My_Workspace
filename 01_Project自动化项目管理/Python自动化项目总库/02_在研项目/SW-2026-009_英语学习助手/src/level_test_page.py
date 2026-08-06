"""
入级测试页面 - 10题测试判断 CEFR 等级
高内聚低耦合：通过 LevelTestEngine 接口交互
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from level_test import LevelTestEngine


class LevelTestPage(QWidget):
    """入级测试页面"""

    def __init__(self, on_result=None, parent=None):
        super().__init__(parent)
        self.engine = LevelTestEngine()
        self.on_result = on_result  # 回调函数，测试完成后调用
        self.questions = []
        self.current_idx = 0
        self.answers = []
        self._setup_ui()

        # 如果已经测试过，显示结果
        if self.engine.has_taken_test():
            self._show_existing_result()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignCenter)

        # 标题
        title = QLabel("🎯 英语水平测试")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("10 道题，约 5 分钟，帮你确定学习起点")
        subtitle.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # 内容区域
        self.content_stack = []

        # 开始页
        self.start_widget = self._make_start_page()
        layout.addWidget(self.start_widget)

        # 测试页
        self.test_widget = self._make_test_page()
        self.test_widget.hide()
        layout.addWidget(self.test_widget)

        # 结果页
        self.result_widget = self._make_result_page()
        self.result_widget.hide()
        layout.addWidget(self.result_widget)

    def _make_start_page(self):
        """开始页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        info_frame = QFrame()
        info_frame.setStyleSheet("QFrame { background: #f0f7ff; border: 1px solid #bdd7ee; border-radius: 12px; padding: 24px; }")
        info_layout = QVBoxLayout(info_frame)
        info_items = [
            "📝 共 10 道题，包含词汇、语法、阅读理解",
            "⏱️ 预计用时 5 分钟",
            "📊 测试结束后自动推荐学习等级",
            "🔄 可以重新测试",
        ]
        for item in info_items:
            lbl = QLabel(item)
            lbl.setStyleSheet("font-size: 14px; color: #2c3e50; padding: 4px 0;")
            info_layout.addWidget(lbl)
        layout.addWidget(info_frame)

        start_btn = QPushButton("开始测试 →")
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.setStyleSheet("""
            QPushButton { padding: 14px 60px; background: #4a90d9; color: white; border: none;
                border-radius: 10px; font-size: 18px; font-weight: bold; }
            QPushButton:hover { background: #357abd; }
        """)
        start_btn.clicked.connect(self._start_test)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)

        return widget

    def _make_test_page(self):
        """测试页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignCenter)

        # 进度
        progress_layout = QHBoxLayout()
        self.test_progress = QProgressBar()
        self.test_progress.setStyleSheet("""
            QProgressBar { border: none; border-radius: 4px; background: #e0e0e0; height: 8px; text-align: center; }
            QProgressBar::chunk { background: #4a90d9; border-radius: 4px; }
        """)
        self.test_progress.setMaximumHeight(8)
        self.test_progress.setTextVisible(False)
        progress_layout.addWidget(self.test_progress)
        self.progress_label = QLabel("1/10")
        self.progress_label.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)

        # 等级标签
        self.level_tag = QLabel("")
        self.level_tag.setStyleSheet("font-size: 12px; padding: 2px 10px; border-radius: 10px; color: white;")
        self.level_tag.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.level_tag, alignment=Qt.AlignCenter)

        # 题目卡片
        self.question_frame = QFrame()
        self.question_frame.setStyleSheet("QFrame { background: white; border: 2px solid #e0e0e0; border-radius: 16px; padding: 40px; }")
        self.question_frame.setMinimumSize(550, 300)
        qf_layout = QVBoxLayout(self.question_frame)
        qf_layout.setSpacing(20)
        qf_layout.setAlignment(Qt.AlignCenter)

        self.question_label = QLabel("")
        self.question_label.setStyleSheet("font-size: 18px; color: #2c3e50; line-height: 1.6;")
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setWordWrap(True)
        qf_layout.addWidget(self.question_label)

        # 选项
        self.options_layout = QVBoxLayout()
        self.options_layout.setSpacing(10)
        qf_layout.addLayout(self.options_layout)

        layout.addWidget(self.question_frame, alignment=Qt.AlignCenter)

        return widget

    def _make_result_page(self):
        """结果页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        result_frame = QFrame()
        result_frame.setStyleSheet("QFrame { background: white; border: 2px solid #e0e0e0; border-radius: 16px; padding: 40px; }")
        result_frame.setMinimumSize(500, 400)
        rf_layout = QVBoxLayout(result_frame)
        rf_layout.setAlignment(Qt.AlignCenter)
        rf_layout.setSpacing(16)

        self.result_icon = QLabel("🎉")
        self.result_icon.setStyleSheet("font-size: 56px;")
        self.result_icon.setAlignment(Qt.AlignCenter)
        rf_layout.addWidget(self.result_icon)

        self.result_title = QLabel("测试完成！")
        self.result_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        self.result_title.setAlignment(Qt.AlignCenter)
        rf_layout.addWidget(self.result_title)

        self.result_level = QLabel("")
        self.result_level.setStyleSheet("font-size: 32px; font-weight: bold; padding: 8px 24px; border-radius: 12px; color: white;")
        self.result_level.setAlignment(Qt.AlignCenter)
        rf_layout.addWidget(self.result_level)

        self.result_detail = QLabel("")
        self.result_detail.setStyleSheet("font-size: 15px; color: #34495e;")
        self.result_detail.setAlignment(Qt.AlignCenter)
        self.result_detail.setWordWrap(True)
        rf_layout.addWidget(self.result_detail)

        # 分数详情
        self.result_scores = QLabel("")
        self.result_scores.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        self.result_scores.setAlignment(Qt.AlignCenter)
        rf_layout.addWidget(self.result_scores)

        layout.addWidget(result_frame, alignment=Qt.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(12)

        retake_btn = QPushButton("重新测试")
        retake_btn.setStyleSheet("QPushButton { padding: 10px 24px; background: #95a5a6; color: white; border: none; border-radius: 8px; font-size: 14px; } QPushButton:hover { background: #7f8c8d; }")
        retake_btn.clicked.connect(self._start_test)
        btn_layout.addWidget(retake_btn)

        close_btn = QPushButton("开始学习")
        close_btn.setStyleSheet("QPushButton { padding: 10px 24px; background: #4a90d9; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; } QPushButton:hover { background: #357abd; }")
        close_btn.clicked.connect(self._on_close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        return widget

    def _start_test(self):
        """开始测试"""
        self.questions = self.engine.generate_test()
        self.current_idx = 0
        self.answers = []

        self.start_widget.hide()
        self.result_widget.hide()
        self.test_widget.show()

        self.test_progress.setMaximum(len(self.questions))
        self._show_question()

    def _show_question(self):
        """显示当前题目"""
        if self.current_idx >= len(self.questions):
            self._show_result()
            return

        q = self.questions[self.current_idx]
        self.test_progress.setValue(self.current_idx + 1)
        self.progress_label.setText(f"{self.current_idx + 1}/{len(self.questions)}")

        # 等级标签
        level = q.get('level', 'A1')
        colors = {"A1": "#3498db", "A2": "#27ae60", "B1": "#e67e22"}
        c = colors.get(level, "#7f8c8d")
        self.level_tag.setText(level)
        self.level_tag.setStyleSheet(f"font-size: 12px; padding: 2px 10px; border-radius: 10px; background: {c}; color: white;")

        self.question_label.setText(q['question'])

        # 清空选项
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for opt in q['options']:
            btn = QPushButton(opt)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton { padding: 14px 20px; border: 2px solid #e0e0e0; border-radius: 10px;
                    background: white; color: #2c3e50; font-size: 15px; text-align: left; }
                QPushButton:hover { border-color: #4a90d9; background: #f8fbfe; }
                QPushButton:checked { border-color: #4a90d9; background: #e8f4fc; }
            """)
            btn.clicked.connect(lambda checked, o=opt, a=q['answer'], lv=level: self._on_answer(o, a, lv))
            self.options_layout.addWidget(btn)

    def _on_answer(self, selected, answer, level):
        """处理答案"""
        correct = (selected.strip() == answer.strip())
        self.answers.append({"level": level, "correct": correct})

        # 禁用所有按钮并显示对错
        for i in range(self.options_layout.count()):
            w = self.options_layout.itemAt(i).widget()
            if w:
                w.setEnabled(False)
                if w.text() == answer:
                    w.setStyleSheet("QPushButton { padding: 14px 20px; border: 2px solid #27ae60; border-radius: 10px; background: #d5f5e3; color: #27ae60; font-size: 15px; }")
                elif w.text() == selected and not correct:
                    w.setStyleSheet("QPushButton { padding: 14px 20px; border: 2px solid #e74c3c; border-radius: 10px; background: #fadbd8; color: #e74c3c; font-size: 15px; }")

        # 1.5 秒后下一题
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1500, self._next_question)

    def _next_question(self):
        self.current_idx += 1
        if self.current_idx >= len(self.questions):
            self._show_result()
        else:
            self._show_question()

    def _show_result(self):
        """显示结果"""
        result = self.engine.calculate_level(self.answers)
        self.engine.save_result(result)

        self.test_widget.hide()
        self.result_widget.show()

        level = result['estimated_level']
        colors = {"A1": "#3498db", "A2": "#27ae60", "B1": "#e67e22"}
        c = colors.get(level, "#7f8c8d")

        icons = {"A1": "🌱", "A2": "📚", "B1": "🎓"}
        self.result_icon.setText(icons.get(level, "🎉"))
        self.result_title.setText(f"你的英语水平: {level}")
        self.result_level.setText(f"CEFR {level}")
        self.result_level.setStyleSheet(f"font-size: 32px; font-weight: bold; padding: 8px 24px; border-radius: 12px; background: {c}; color: white;")
        self.result_detail.setText(result['detail'])

        scores = result['scores']
        score_text = f"A1 正确率: {result['a1_rate']}% | A2 正确率: {result['a2_rate']}% | B1 正确率: {result['b1_rate']}%"
        self.result_scores.setText(score_text)

        # 回调
        if self.on_result:
            self.on_result(result)

    def _show_existing_result(self):
        """显示已有测试结果"""
        latest = self.engine.get_latest_result()
        if latest:
            self.start_widget.hide()
            self.result_widget.show()

            level = latest['estimated_level']
            colors = {"A1": "#3498db", "A2": "#27ae60", "B1": "#e67e22"}
            c = colors.get(level, "#7f8c8d")
            icons = {"A1": "🌱", "A2": "📚", "B1": "🎓"}

            self.result_icon.setText(icons.get(level, "🎉"))
            self.result_title.setText(f"上次测试结果: CEFR {level}")
            self.result_level.setText(f"{level}")
            self.result_level.setStyleSheet(f"font-size: 32px; font-weight: bold; padding: 8px 24px; border-radius: 12px; background: {c}; color: white;")
            self.result_detail.setText(latest.get('details', ''))
            self.result_scores.setText(
                f"A1: {latest['a1_score']}/{latest['a1_total']} | "
                f"A2: {latest['a2_score']}/{latest['a2_total']} | "
                f"B1: {latest['b1_score']}/{latest['b1_total']}"
            )

    def _on_close(self):
        """关闭测试页"""
        self.start_widget.hide()
        self.test_widget.hide()
        self.result_widget.hide()
        self.start_widget.show()

    def start_new_test(self):
        """外部调用开始新测试"""
        self._start_test()
