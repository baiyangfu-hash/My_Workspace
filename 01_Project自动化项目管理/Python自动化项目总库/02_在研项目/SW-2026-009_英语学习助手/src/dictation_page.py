"""
听写练习页面
支持单词听写、句子听写、对话听写三种模式
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from fsrs_engine import FSRSEngine, FSRSState
from tts_engine import TTSEngine


class DictationPage(QWidget):
    """听写练习页面"""

    MODES = [
        ("word", "单词听写"),
        ("sentence", "句子听写"),
        ("dialog", "对话听写"),
    ]

    def __init__(self, dictionary, database, parent=None):
        super().__init__(parent)
        self.dictionary = dictionary
        self.database = database
        self.tts = TTSEngine()
        self.fsrs = FSRSEngine()

        self.current_mode = "word"
        self.current_question = None
        self.current_index = 0
        self.total_questions = 10
        self.correct_count = 0
        self.wrong_words = []
        self.play_count = 0
        self.max_plays = 3
        self.has_submitted = False

        self._setup_ui()
        self._start_round()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 30)

        # 标题栏
        header = QHBoxLayout()
        self.title_label = QLabel("听写练习")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        header.addWidget(self.title_label)
        header.addStretch()
        self.progress_label = QLabel("第 1/10 题")
        self.progress_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        header.addWidget(self.progress_label)
        layout.addLayout(header)

        # 模式切换标签
        tabs = QHBoxLayout()
        tabs.setSpacing(0)
        self.mode_buttons = []
        for mode_id, mode_name in self.MODES:
            btn = QPushButton(mode_name)
            btn.setCheckable(True)
            btn.setProperty("mode", mode_id)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 20px;
                    border: none;
                    border-bottom: 2px solid transparent;
                    background: transparent;
                    color: #7f8c8d;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover { color: #2c3e50; }
                QPushButton:checked {
                    color: #4a90d9;
                    border-bottom-color: #4a90d9;
                }
            """)
            btn.clicked.connect(lambda checked, m=mode_id: self._switch_mode(m))
            tabs.addWidget(btn)
            self.mode_buttons.append(btn)
        tabs.addStretch()
        layout.addLayout(tabs)

        # TTS 状态
        self.tts_status = QLabel(f"TTS: {self.tts.get_status()}")
        self.tts_status.setStyleSheet("font-size: 11px; color: #95a5a6;")
        layout.addWidget(self.tts_status)

        # 播放区域
        play_frame = QFrame()
        play_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        play_layout = QVBoxLayout(play_frame)
        play_layout.setAlignment(Qt.AlignCenter)

        self.play_btn = QPushButton("🔊 播放发音")
        self.play_btn.setStyleSheet("""
            QPushButton {
                padding: 14px 40px;
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 50px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #357abd; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        self.play_btn.clicked.connect(self._play_audio)
        play_layout.addWidget(self.play_btn, alignment=Qt.AlignCenter)

        self.play_hint = QLabel("点击播放，最多可播放 3 次")
        self.play_hint.setStyleSheet("color: #95a5a6; font-size: 12px; margin-top: 8px;")
        self.play_hint.setAlignment(Qt.AlignCenter)
        play_layout.addWidget(self.play_hint)

        layout.addWidget(play_frame)

        # 输入区域
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        input_layout = QVBoxLayout(input_frame)

        input_label = QLabel("请输入你听到的内容：")
        input_label.setStyleSheet("font-size: 14px; color: #2c3e50; margin-bottom: 8px;")
        input_layout.addWidget(input_label)

        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                color: #2c3e50;
            }
            QLineEdit:focus { border-color: #4a90d9; }
            QLineEdit.correct { border-color: #27ae60; background: #f0fdf4; }
            QLineEdit.wrong { border-color: #e74c3c; background: #fef2f2; }
        """)
        self.input_field.setPlaceholderText("在此输入...")
        self.input_field.returnPressed.connect(self._submit_answer)
        input_layout.addWidget(self.input_field)

        # 判分结果显示
        self.result_area = QFrame()
        self.result_area.setStyleSheet("""
            QFrame {
                background-color: #fffbeb;
                border: 1px solid #fde68a;
                border-radius: 8px;
                padding: 12px;
                margin-top: 12px;
            }
        """)
        result_layout = QVBoxLayout(self.result_area)

        self.result_title = QLabel("")
        self.result_title.setStyleSheet("font-size: 13px; font-weight: bold;")
        result_layout.addWidget(self.result_title)

        self.result_detail = QLabel("")
        self.result_detail.setStyleSheet("font-size: 14px; font-family: 'Consolas', monospace; letter-spacing: 2px;")
        self.result_detail.setWordWrap(True)
        result_layout.addWidget(self.result_detail)

        self.result_correct = QLabel("")
        self.result_correct.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        result_layout.addWidget(self.result_correct)

        self.result_area.hide()
        input_layout.addWidget(self.result_area)

        layout.addWidget(input_frame)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.submit_btn = QPushButton("提交答案")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 32px;
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #357abd; }
        """)
        self.submit_btn.clicked.connect(self._submit_answer)
        btn_layout.addWidget(self.submit_btn)

        self.next_btn = QPushButton("下一题 →")
        self.next_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 32px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #219a52; }
        """)
        self.next_btn.clicked.connect(self._next_question)
        self.next_btn.hide()
        btn_layout.addWidget(self.next_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 本轮错词
        self.wrong_area = QFrame()
        self.wrong_area.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                margin-top: 8px;
            }
        """)
        wrong_layout = QVBoxLayout(self.wrong_area)

        wrong_title = QLabel("本轮错词")
        wrong_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        wrong_layout.addWidget(wrong_title)

        self.wrong_list = QLabel("暂无")
        self.wrong_list.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        self.wrong_list.setWordWrap(True)
        wrong_layout.addWidget(self.wrong_list)

        self.wrong_area.hide()
        layout.addWidget(self.wrong_area)

        # 完成面板
        self.complete_panel = QFrame()
        self.complete_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #27ae60;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        complete_layout = QVBoxLayout(self.complete_panel)
        complete_layout.setAlignment(Qt.AlignCenter)

        self.complete_title = QLabel("🎉 本轮完成！")
        self.complete_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #27ae60;")
        self.complete_title.setAlignment(Qt.AlignCenter)
        complete_layout.addWidget(self.complete_title)

        self.complete_stats = QLabel("")
        self.complete_stats.setStyleSheet("font-size: 16px; color: #2c3e50; margin: 16px 0;")
        self.complete_stats.setAlignment(Qt.AlignCenter)
        complete_layout.addWidget(self.complete_stats)

        restart_btn = QPushButton("再来一轮")
        restart_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 40px;
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #357abd; }
        """)
        restart_btn.clicked.connect(self._start_round)
        complete_layout.addWidget(restart_btn, alignment=Qt.AlignCenter)

        self.complete_panel.hide()
        layout.addWidget(self.complete_panel)

        layout.addStretch()

    def _switch_mode(self, mode):
        """切换听写模式"""
        self.current_mode = mode
        for btn in self.mode_buttons:
            btn.setChecked(btn.property("mode") == mode)
        self._start_round()

    def _start_round(self):
        """开始新一轮听写"""
        self.current_index = 0
        self.correct_count = 0
        self.wrong_words = []
        self.questions = self._generate_questions()

        self.complete_panel.hide()
        self.wrong_area.hide()
        self.result_area.hide()
        self.next_btn.hide()
        self.submit_btn.show()
        self.input_field.show()
        self.input_field.setEnabled(True)
        self.input_field.setText("")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                color: #2c3e50;
            }
            QLineEdit:focus { border-color: #4a90d9; }
        """)

        self._load_question()

    def _generate_questions(self):
        """生成听写题目"""
        questions = []

        if self.current_mode == "word":
            # 单词模式：从词典取随机单词
            words = self.dictionary.get_random_words(self.total_questions)
            for w in words:
                questions.append({
                    "text": w.get("word", ""),
                    "display": w.get("word", ""),
                    "hint": f"/{w.get('phonetic', '')}/ {w.get('translation', '')}",
                })

        elif self.current_mode == "sentence":
            # 句子模式：从对话中提取句子
            import random

            from dialogs_data import DIALOGS
            all_sentences = []
            for dialog in DIALOGS.values():
                for line in dialog.get("lines", []):
                    text = line.get("text", "")
                    if text and len(text.split()) >= 3:
                        all_sentences.append({
                            "text": text,
                            "display": text,
                            "hint": line.get("translation", ""),
                        })
            random.shuffle(all_sentences)
            questions = all_sentences[:self.total_questions]

        else:  # dialog
            # 对话模式：连续 2-3 句
            import random

            from dialogs_data import DIALOGS
            all_dialogs = []
            for dialog in DIALOGS.values():
                lines = dialog.get("lines", [])
                for i in range(len(lines) - 1):
                    combined = lines[i]["text"] + " " + lines[i+1]["text"]
                    all_dialogs.append({
                        "text": combined,
                        "display": combined,
                        "hint": dialog.get("title", ""),
                    })
            random.shuffle(all_dialogs)
            questions = all_dialogs[:self.total_questions]

        # 如果题目不够，用随机单词补齐
        while len(questions) < self.total_questions:
            words = self.dictionary.get_random_words(self.total_questions - len(questions))
            for w in words:
                questions.append({
                    "text": w.get("word", ""),
                    "display": w.get("word", ""),
                    "hint": f"/{w.get('phonetic', '')}/",
                })

        return questions

    def _load_question(self):
        """加载当前题目"""
        if self.current_index >= len(self.questions):
            self._show_complete()
            return

        self.current_question = self.questions[self.current_index]
        self.play_count = 0
        self.has_submitted = False

        self.progress_label.setText(f"第 {self.current_index + 1}/{self.total_questions} 题")
        self.play_hint.setText(f"点击播放，最多可播放 {self.max_plays} 次")
        self.input_field.setText("")
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self.result_area.hide()
        self.submit_btn.show()
        self.next_btn.hide()
        self.play_btn.setEnabled(True)

    def _play_audio(self):
        """播放发音"""
        if not self.current_question:
            return

        if self.play_count >= self.max_plays:
            self.play_hint.setText("已达到最大播放次数")
            return

        text = self.current_question["text"]
        self.tts.speak(text, callback=self._on_play_done)
        self.play_count += 1
        remaining = self.max_plays - self.play_count
        self.play_hint.setText(f"已播放 {self.play_count} 次，还剩 {remaining} 次")
        self.play_btn.setEnabled(False)

    def _on_play_done(self):
        """播放完成回调"""
        self.play_btn.setEnabled(True)

    def _submit_answer(self):
        """提交答案"""
        if self.has_submitted or not self.current_question:
            return

        user_input = self.input_field.text().strip()
        if not user_input:
            QMessageBox.information(self, "提示", "请输入你听到的内容")
            return

        correct_answer = self.current_question["text"]
        is_correct = self._check_answer(user_input, correct_answer)
        self.has_submitted = True

        # 显示结果
        self._show_result(user_input, correct_answer, is_correct)

        # 更新统计
        if is_correct:
            self.correct_count += 1
            self.input_field.setStyleSheet("""
                QLineEdit {
                    padding: 12px 16px;
                    border: 2px solid #27ae60;
                    border-radius: 8px;
                    font-size: 16px;
                    color: #2c3e50;
                    background: #f0fdf4;
                }
            """)
        else:
            self.wrong_words.append({
                "user": user_input,
                "correct": correct_answer,
            })
            self.input_field.setStyleSheet("""
                QLineEdit {
                    padding: 12px 16px;
                    border: 2px solid #e74c3c;
                    border-radius: 8px;
                    font-size: 16px;
                    color: #2c3e50;
                    background: #fef2f2;
                }
            """)

            # 错词加入复习队列
            word = correct_answer.split()[0] if " " in correct_answer else correct_answer
            word = word.strip(".,!?;:\"'")
            self._add_wrong_word_to_review(word)

        # 记录到数据库
        self.database.add_study_record(
            correct_answer[:50],  # 截断避免太长
            "dictation",
            "correct" if is_correct else "wrong"
        )

        self.submit_btn.hide()
        self.next_btn.show()
        self.input_field.setEnabled(False)

        # 更新错词显示
        if self.wrong_words:
            self._update_wrong_list()

    def _check_answer(self, user_input, correct_answer):
        """检查答案"""
        # 忽略大小写和首尾空格
        user = user_input.strip().lower()
        correct = correct_answer.strip().lower()

        if self.current_mode == "word":
            # 单词模式：精确匹配
            return user == correct
        else:
            # 句子/对话模式：忽略标点
            import re
            user_clean = re.sub(r'[^\w\s]', '', user)
            correct_clean = re.sub(r'[^\w\s]', '', correct)
            return user_clean == correct_clean

    def _show_result(self, user_input, correct_answer, is_correct):
        """显示判分结果"""
        self.result_area.show()

        if is_correct:
            self.result_area.setStyleSheet("""
                QFrame {
                    background-color: #f0fdf4;
                    border: 1px solid #86efac;
                    border-radius: 8px;
                    padding: 12px;
                    margin-top: 12px;
                }
            """)
            self.result_title.setText("✅ 正确！")
            self.result_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #27ae60;")
            self.result_detail.setText("")
            self.result_correct.setText(f"正确答案: {correct_answer}")
        else:
            self.result_area.setStyleSheet("""
                QFrame {
                    background-color: #fef2f2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                    padding: 12px;
                    margin-top: 12px;
                }
            """)
            self.result_title.setText("❌ 错误")
            self.result_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #dc2626;")

            # 逐字母/逐词对比
            detail = self._generate_diff(user_input, correct_answer)
            self.result_detail.setText(detail)
            self.result_correct.setText(f"正确答案: {correct_answer}")

    def _generate_diff(self, user_input, correct_answer):
        """生成差异对比文本"""
        if self.current_mode == "word":
            # 逐字母对比
            result = []
            user = user_input.lower()
            correct = correct_answer.lower()
            max_len = max(len(user), len(correct))

            for i in range(max_len):
                if i < len(user) and i < len(correct) and user[i] == correct[i]:
                    result.append(f'<span style="color:#27ae60;">{correct_answer[i]}</span>')
                elif i < len(correct):
                    result.append(f'<span style="color:#dc2626;font-weight:bold;text-decoration:underline;">{correct_answer[i]}</span>')

            return "".join(result)
        else:
            # 逐词对比
            import re
            user_words = re.findall(r'\b\w+\b', user_input.lower())
            correct_words = re.findall(r'\b\w+\b', correct_answer.lower())

            result = []
            for i, word in enumerate(correct_words):
                if i < len(user_words) and user_words[i] == word:
                    result.append(f'<span style="color:#27ae60;">{word}</span>')
                else:
                    result.append(f'<span style="color:#dc2626;font-weight:bold;">{word}</span>')

            return " ".join(result)

    def _add_wrong_word_to_review(self, word):
        """将错词加入复习队列"""
        user_word = self.database.get_or_create_user_word(word)
        fsrs_state = FSRSState.from_json(user_word.get('fsrs_state'))

        # 设置为"重来"，缩短间隔
        new_state, due_date = self.fsrs.review(fsrs_state, 'again')

        self.database.update_user_word(
            word,
            status='learning',
            fsrs_state=new_state.to_json(),
            due_date=due_date.isoformat()
        )

    def _update_wrong_list(self):
        """更新错词列表显示"""
        self.wrong_area.show()
        texts = []
        for item in self.wrong_words:
            texts.append(f"{item['user']} → {item['correct']}")
        self.wrong_list.setText("  |  ".join(texts))

    def _next_question(self):
        """下一题"""
        self.current_index += 1
        self._load_question()

    def _show_complete(self):
        """显示完成面板"""
        self.input_field.hide()
        self.submit_btn.hide()
        self.next_btn.hide()
        self.result_area.hide()
        self.play_btn.setEnabled(False)

        rate = round(self.correct_count / self.total_questions * 100)
        self.complete_stats.setText(
            f"正确: {self.correct_count}/{self.total_questions} ({rate}%)<br>"
            f"错误: {len(self.wrong_words)} 个"
        )

        # 更新每日统计
        self.database.update_daily_stats(
            correct_count=self.correct_count,
            total_count=self.total_questions
        )

        self.complete_panel.show()
