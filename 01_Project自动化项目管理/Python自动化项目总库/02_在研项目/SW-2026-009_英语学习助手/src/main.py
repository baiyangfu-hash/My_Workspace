"""
英语学习助手 - 主程序入口
"""
import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from cefr_tagger import CEFRTagger
from course_page import CoursePage
from database import Database
from dialog_importer import DialogImporter
from dialog_importer import ImportError as DialogImportError
from dialogs_data import get_all_dialogs, get_dialog
from dictation_page import DictationPage
from dictionary import Dictionary
from fsrs_engine import FSRSEngine, FSRSState
from grammar_practice_page import GrammarPracticePage
from roleplay_page import RolePlayPage
from study_tracker import StudyTracker
from tts_engine import TTSEngine
from us_travel_dialogs import get_all_us_dialogs, get_us_dialog


class WordCard(QFrame):
    """单词卡片组件"""
    def __init__(self, word_data, parent=None):
        super().__init__(parent)
        self.word_data = word_data
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            WordCard {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
            }
            WordCard:hover {
                border: 1px solid #4a90d9;
            }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(12, 12, 12, 12)

        # 单词
        word_label = QLabel(self.word_data.get('word', ''))
        word_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(word_label)

        # 音标
        phonetic = self.word_data.get('phonetic', '')
        if phonetic:
            phonetic_label = QLabel(f"/{phonetic}/")
            phonetic_label.setStyleSheet("font-size: 13px; color: #7f8c8d;")
            layout.addWidget(phonetic_label)

        # 释义
        translation = self.word_data.get('translation', '')
        if translation:
            trans_label = QLabel(translation)
            trans_label.setStyleSheet("font-size: 13px; color: #34495e;")
            trans_label.setWordWrap(True)
            layout.addWidget(trans_label)

        # 词性
        pos = self.word_data.get('pos', '')
        if pos:
            pos_label = QLabel(pos)
            pos_label.setStyleSheet("font-size: 11px; color: #95a5a6;")
            layout.addWidget(pos_label)

        self.setMaximumWidth(280)

class DictionaryPage(QWidget):
    """词典页面"""
    def __init__(self, dictionary, parent=None):
        super().__init__(parent)
        self.dictionary = dictionary
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入单词查询...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4a90d9;
            }
        """)
        self.search_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton("查询")
        search_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        search_btn.clicked.connect(self._on_search)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        # 随机单词按钮
        random_btn = QPushButton("随机单词")
        random_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        random_btn.clicked.connect(self._on_random)
        layout.addWidget(random_btn, alignment=Qt.AlignLeft)

        # 结果区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.results_container = QWidget()
        self.results_layout = QGridLayout(self.results_container)
        self.results_layout.setSpacing(8)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.results_container)
        layout.addWidget(scroll)

        # 详情区域
        self.detail_area = QTextEdit()
        self.detail_area.setReadOnly(True)
        self.detail_area.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        self.detail_area.setMaximumHeight(200)
        self.detail_area.hide()
        layout.addWidget(self.detail_area)

    def _on_search(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            return

        # 清空之前的结果
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.detail_area.hide()

        # 精确查询
        result = self.dictionary.lookup(keyword)
        if isinstance(result, dict):
            # 显示详情
            self._show_detail(result)
        elif isinstance(result, list) and result:
            # 显示模糊匹配结果
            self._show_word_list(result)
        else:
            # 尝试搜索
            results = self.dictionary.search(keyword)
            if results:
                self._show_word_list(results)
            else:
                self.detail_area.setText(f"未找到单词: {keyword}")
                self.detail_area.show()

    def _show_detail(self, word_data):
        """显示单词详情"""
        text = f"""
<b style="font-size:20px">{word_data.get('word', '')}</b>  <span style="color:#7f8c8d">{word_data.get('pos', '')}</span>

<font color="#7f8c8d">音标: /{word_data.get('phonetic', '')}/</font>

<b>释义:</b>
{word_data.get('translation', '暂无释义')}

<b>英文释义:</b>
{word_data.get('definition', '暂无')}

<font color="#95a5a6" size="2">变形: {word_data.get('exchange', '无')}</font>
        """
        self.detail_area.setHtml(text)
        self.detail_area.show()

    def _show_word_list(self, words):
        """显示单词列表"""
        for i, word_data in enumerate(words):
            card = WordCard(word_data)
            card.mousePressEvent = lambda e, w=word_data: self._show_detail(w)
            row = i // 3
            col = i % 3
            self.results_layout.addWidget(card, row, col)

    def _on_random(self):
        """随机单词"""
        words = self.dictionary.get_random_words(6)
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.detail_area.hide()
        self._show_word_list(words)

class DialogLineWidget(QFrame):
    """对话行组件"""
    def __init__(self, line_data, dict_lookup_func, parent=None):
        super().__init__(parent)
        self.line_data = line_data
        self.dict_lookup = dict_lookup_func
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            DialogLineWidget {
                background-color: #ffffff;
                border: 1px solid #e8e8e8;
                border-radius: 10px;
                padding: 12px;
                margin: 4px 8px;
            }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(16, 12, 16, 12)

        # 说话人
        speaker = self.line_data.get('speaker', '')
        speaker_label = QLabel(f"🧑 {speaker}:")
        speaker_label.setStyleSheet("font-weight: bold; color: #4a90d9; font-size: 13px;")
        layout.addWidget(speaker_label)

        # 英文文本（可点击查词）
        text = self.line_data.get('text', '')
        text_layout = QHBoxLayout()
        text_layout.setSpacing(4)

        words = text.split()
        for word in words:
            # 去除标点
            clean_word = word.strip('.,!?;:"').lower()
            btn = QPushButton(word)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    color: #2c3e50;
                    font-size: 15px;
                    padding: 2px 4px;
                    border: none;
                    background: transparent;
                }
                QPushButton:hover {
                    color: #4a90d9;
                    background-color: #e8f4fc;
                    border-radius: 4px;
                }
            """)
            btn.clicked.connect(lambda checked, w=clean_word: self._on_word_click(w))
            text_layout.addWidget(btn)

        text_layout.addStretch()
        layout.addLayout(text_layout)

        # 中文翻译
        translation = self.line_data.get('translation', '')
        trans_label = QLabel(translation)
        trans_label.setStyleSheet("color: #7f8c8d; font-size: 13px; padding-left: 8px;")
        layout.addWidget(trans_label)

    def _on_word_click(self, word):
        """点击单词查词"""
        self.dict_lookup(word)

class DialogPage(QWidget):
    """情景对话页面"""
    def __init__(self, dictionary, parent=None):
        super().__init__(parent)
        self.dictionary = dictionary
        self.current_dialog = None
        self._importer = DialogImporter()
        self._custom_dialogs = {}  # 存储导入的自定义对话
        self._custom_counter = 0
        self._setup_ui()
        self._load_dialog_list()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # 左侧对话列表
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #f5f6fa;")
        left_panel.setMaximumWidth(280)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 12, 12, 12)

        list_title = QLabel("📚 情景对话")
        list_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        left_layout.addWidget(list_title)

        self.dialog_list = QListWidget()
        self.dialog_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
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
        self.dialog_list.itemClicked.connect(self._on_dialog_selected)
        left_layout.addWidget(self.dialog_list)

        # 导入对话按钮
        import_btn = QPushButton("导入对话")
        import_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 16px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        import_btn.clicked.connect(self._on_import_dialog)
        left_layout.addWidget(import_btn)

        layout.addWidget(left_panel)

        # 右侧对话内容
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        # 标题栏
        self.title_label = QLabel("选择一个对话开始学习")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        right_layout.addWidget(self.title_label)

        # 查词结果区域
        self.lookup_result = QTextEdit()
        self.lookup_result.setReadOnly(True)
        self.lookup_result.setMaximumHeight(120)
        self.lookup_result.setStyleSheet("""
            QTextEdit {
                background-color: #fff8e1;
                border: 1px solid #ffe082;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        self.lookup_result.hide()
        right_layout.addWidget(self.lookup_result)

        # 对话内容滚动区
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.dialog_container = QWidget()
        self.dialog_layout = QVBoxLayout(self.dialog_container)
        self.dialog_layout.setSpacing(8)
        self.dialog_layout.setContentsMargins(0, 0, 0, 0)
        self.dialog_layout.addStretch()
        scroll.setWidget(self.dialog_container)
        right_layout.addWidget(scroll)

        layout.addWidget(right_panel)

    def _load_dialog_list(self):
        """加载对话列表（基础 + 美国出差）"""
        self._all_dialogs = []

        # 基础对话
        for d in get_all_dialogs():
            self._all_dialogs.append(d)

        # 美国出差对话
        for d in get_all_us_dialogs():
            self._all_dialogs.append(d)

        for dialog in self._all_dialogs:
            item_text = f"{dialog['title']}\n{dialog['title_en']} | {dialog['difficulty']}"
            self.dialog_list.addItem(item_text)

    def _on_dialog_selected(self, item):
        """选择对话"""
        index = self.dialog_list.row(item)
        if index < len(self._all_dialogs):
            dialog_id = self._all_dialogs[index]['id']
            self._show_dialog(dialog_id)

    def _show_dialog(self, dialog_id):
        """显示对话内容"""
        # 先从基础对话找，再从美国出差对话找，最后从自定义对话找
        dialog = get_dialog(dialog_id) or get_us_dialog(dialog_id) or self._custom_dialogs.get(dialog_id)
        if not dialog:
            return

        self.current_dialog = dialog
        self.title_label.setText(f"{dialog['title']} - {dialog['title_en']}")

        # 清空之前的对话行
        while self.dialog_layout.count() > 1:
            item = self.dialog_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 添加对话行
        for line in dialog['lines']:
            line_widget = DialogLineWidget(line, self._lookup_word)
            self.dialog_layout.insertWidget(self.dialog_layout.count() - 1, line_widget)

    def _lookup_word(self, word):
        """查词并显示"""
        result = self.dictionary.lookup(word)
        if isinstance(result, dict):
            text = f"<b>{result.get('word', word)}</b> /{result.get('phonetic', '')}/ {result.get('pos', '')}<br>{result.get('translation', '暂无释义')}"
            self.lookup_result.setHtml(text)
            self.lookup_result.show()
        else:
            self.lookup_result.hide()

    def _on_import_dialog(self):
        """导入对话文件"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "选择对话文件",
            "",
            "对话文件 (*.json *.txt);;JSON 文件 (*.json);;文本文件 (*.txt);;所有文件 (*)"
        )
        if not filepath:
            return

        try:
            dialog = self._importer.import_file(filepath)

            # 生成唯一 ID
            self._custom_counter += 1
            dialog_id = f"custom_{self._custom_counter}"
            self._custom_dialogs[dialog_id] = dialog

            # 添加到列表
            dialog_info = {
                'id': dialog_id,
                'title': dialog['title'],
                'title_en': dialog['title_en'],
                'category': dialog['category'],
                'difficulty': dialog['difficulty'],
                'line_count': len(dialog['lines']),
            }
            self._all_dialogs.append(dialog_info)
            item_text = f"{dialog_info['title']}\n{dialog_info['title_en']} | {dialog_info['difficulty']}"
            self.dialog_list.addItem(item_text)

            # 自动选中新导入的对话
            self.dialog_list.setCurrentRow(len(self._all_dialogs) - 1)
            self._show_dialog(dialog_id)

            QMessageBox.information(self, "导入成功",
                                    f"成功导入对话: {dialog['title']}\n共 {len(dialog['lines'])} 行")
        except DialogImportError as e:
            QMessageBox.warning(self, "导入失败", f"导入对话失败:\n{str(e)}")

class StudyPage(QWidget):
    """单词学习页面 - CEFR分级 + 三种学习模式 + 间隔重复"""
    def __init__(self, dictionary, database, tts=None, parent=None):
        super().__init__(parent)
        self.dictionary = dictionary
        self.database = database
        self.tts = tts
        self.fsrs = FSRSEngine()
        self.cefr_tagger = CEFRTagger()
        self.current_word = None
        self.current_word_data = None
        self.showing_answer = False
        self.current_cefr = "全部"
        self.current_mode = "card"
        self._level_words = []
        self._level_word_idx = 0
        self._setup_ui()
        self._load_next_card()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        # 顶部信息栏
        info_layout = QHBoxLayout()
        self.progress_label = QLabel("今日新词: 0 | 待复习: 0")
        self.progress_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        info_layout.addWidget(self.progress_label)
        info_layout.addStretch()
        self.streak_label = QLabel("🔥 连续学习: 0 天")
        self.streak_label.setStyleSheet("font-size: 14px; color: #e67e22;")
        info_layout.addWidget(self.streak_label)
        layout.addLayout(info_layout)

        # CEFR 等级筛选
        self._setup_cefr_tabs(layout)

        # 学习模式切换
        self._setup_mode_tabs(layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: none; border-radius: 4px; background-color: #e0e0e0; height: 6px; text-align: center; }
            QProgressBar::chunk { background-color: #4a90d9; border-radius: 4px; }
        """)
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # 学习内容区域（三种模式共用一个容器，切换显示）
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack, 1)

        # 卡片模式
        self.card_widget = QWidget()
        self._setup_card_mode_ui()
        self.content_stack.addWidget(self.card_widget)

        # 选择题模式
        self.quiz_widget = QWidget()
        self._setup_quiz_mode_ui()
        self.content_stack.addWidget(self.quiz_widget)

        # 拼写模式
        self.spell_widget = QWidget()
        self._setup_spell_mode_ui()
        self.content_stack.addWidget(self.spell_widget)

    def _setup_cefr_tabs(self, parent_layout):
        """CEFR 等级筛选标签"""
        cefr_layout = QHBoxLayout()
        cefr_layout.setSpacing(4)
        self.cefr_buttons = []
        levels = [("全部", "全部"), ("A1 入门", "A1"), ("A2 基础", "A2"), ("B1 进阶", "B1")]
        colors = {"全部": "#4a90d9", "A1": "#3498db", "A2": "#27ae60", "B1": "#e67e22"}
        for label, level in levels:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(level == "全部")
            btn.setCursor(Qt.PointingHandCursor)
            c = colors.get(level, "#4a90d9")
            btn.setStyleSheet(f"""
                QPushButton {{ padding: 6px 16px; border: 2px solid {c}; border-radius: 16px;
                    background: transparent; color: {c}; font-size: 13px; font-weight: bold; }}
                QPushButton:checked {{ background: {c}; color: white; }}
                QPushButton:hover {{ background: {c}22; }}
            """)
            btn.clicked.connect(lambda checked, lv=level: self._on_cefr_tab(lv))
            cefr_layout.addWidget(btn)
            self.cefr_buttons.append((btn, level))
        cefr_layout.addStretch()
        parent_layout.addLayout(cefr_layout)

    def _setup_mode_tabs(self, parent_layout):
        """学习模式切换"""
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(4)
        self.mode_buttons = []
        modes = [("🃏 卡片模式", "card"), ("✅ 选择题", "quiz"), ("⌨️ 拼写模式", "spell")]
        for label, mode in modes:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(mode == "card")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { padding: 6px 14px; border: 1px solid #d0d0d0; border-radius: 6px;
                    background: transparent; color: #555; font-size: 12px; }
                QPushButton:checked { background: #2c3e50; color: white; border-color: #2c3e50; }
                QPushButton:hover { background: #f0f0f0; }
            """)
            btn.clicked.connect(lambda checked, m=mode: self._on_mode_tab(m))
            mode_layout.addWidget(btn)
            self.mode_buttons.append((btn, mode))
        mode_layout.addStretch()
        parent_layout.addLayout(mode_layout)

    def _setup_card_mode_ui(self):
        """卡片模式 UI"""
        layout = QVBoxLayout(self.card_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("QFrame { background: white; border: 2px solid #e0e0e0; border-radius: 16px; padding: 40px; }")
        self.card_frame.setMinimumSize(550, 320)
        self.card_frame.setMaximumSize(650, 420)
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignCenter)

        # 单词行（含 CEFR 标签 + 发音按钮）
        word_row = QHBoxLayout()
        word_row.setAlignment(Qt.AlignCenter)
        self.word_label = QLabel("Loading...")
        self.word_label.setStyleSheet("font-size: 38px; font-weight: bold; color: #2c3e50;")
        word_row.addWidget(self.word_label)

        self.cefr_badge = QLabel("")
        self.cefr_badge.setStyleSheet("font-size: 11px; padding: 2px 8px; border-radius: 10px; color: white;")
        self.cefr_badge.hide()
        word_row.addWidget(self.cefr_badge)

        self.speak_btn = QPushButton("🔊")
        self.speak_btn.setFixedSize(36, 36)
        self.speak_btn.setCursor(Qt.PointingHandCursor)
        self.speak_btn.setStyleSheet("QPushButton { border: none; background: #e8f4fc; border-radius: 18px; font-size: 16px; } QPushButton:hover { background: #d0e8f7; }")
        self.speak_btn.clicked.connect(self._on_speak)
        word_row.addWidget(self.speak_btn)
        card_layout.addLayout(word_row)

        # 音标
        self.phonetic_label = QLabel("")
        self.phonetic_label.setStyleSheet("font-size: 18px; color: #7f8c8d;")
        self.phonetic_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.phonetic_label)

        # 词频
        self.collins_label = QLabel("")
        self.collins_label.setStyleSheet("font-size: 12px; color: #bdc3c7;")
        self.collins_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.collins_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #e0e0e0;")
        line.setMaximumWidth(380)
        card_layout.addWidget(line, alignment=Qt.AlignCenter)

        # 答案区域
        self.answer_area = QWidget()
        ans_layout = QVBoxLayout(self.answer_area)
        ans_layout.setSpacing(8)
        ans_layout.setAlignment(Qt.AlignCenter)

        self.pos_label = QLabel("")
        self.pos_label.setStyleSheet("font-size: 14px; color: #95a5a6;")
        self.pos_label.setAlignment(Qt.AlignCenter)
        ans_layout.addWidget(self.pos_label)

        self.translation_label = QLabel("")
        self.translation_label.setStyleSheet("font-size: 20px; color: #34495e;")
        self.translation_label.setAlignment(Qt.AlignCenter)
        self.translation_label.setWordWrap(True)
        ans_layout.addWidget(self.translation_label)

        self.definition_label = QLabel("")
        self.definition_label.setStyleSheet("font-size: 13px; color: #7f8c8d; font-style: italic;")
        self.definition_label.setAlignment(Qt.AlignCenter)
        self.definition_label.setWordWrap(True)
        ans_layout.addWidget(self.definition_label)

        self.example_label = QLabel("")
        self.example_label.setStyleSheet("font-size: 13px; color: #8e44ad; padding: 6px 12px; background: #f5eef8; border-radius: 6px;")
        self.example_label.setAlignment(Qt.AlignCenter)
        self.example_label.setWordWrap(True)
        self.example_label.hide()
        ans_layout.addWidget(self.example_label)

        card_layout.addWidget(self.answer_area)
        self.answer_area.hide()
        layout.addWidget(self.card_frame, alignment=Qt.AlignCenter)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(10)

        self.show_btn = QPushButton("显示答案")
        self.show_btn.setStyleSheet("QPushButton { padding: 12px 50px; background: #4a90d9; color: white; border: none; border-radius: 8px; font-size: 15px; font-weight: bold; } QPushButton:hover { background: #357abd; }")
        self.show_btn.clicked.connect(self._show_answer)
        btn_layout.addWidget(self.show_btn)

        self.rating_buttons = []
        for rating, text, color in [("again", "重来", "#e74c3c"), ("hard", "困难", "#e67e22"), ("good", "一般", "#4a90d9"), ("easy", "简单", "#27ae60")]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"QPushButton {{ padding: 10px 18px; background: {color}; color: white; border: none; border-radius: 8px; font-size: 13px; font-weight: bold; }} QPushButton:hover {{ opacity: 0.8; }}")
            btn.setProperty("rating", rating)
            btn.clicked.connect(lambda checked, r=rating: self._on_rating(r))
            btn.hide()
            btn_layout.addWidget(btn)
            self.rating_buttons.append(btn)

        layout.addLayout(btn_layout)

    def _setup_quiz_mode_ui(self):
        """选择题模式 UI"""
        layout = QVBoxLayout(self.quiz_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.quiz_frame = QFrame()
        self.quiz_frame.setStyleSheet("QFrame { background: white; border: 2px solid #e0e0e0; border-radius: 16px; padding: 40px; }")
        self.quiz_frame.setMinimumSize(500, 380)
        self.quiz_frame.setMaximumSize(600, 450)
        qf_layout = QVBoxLayout(self.quiz_frame)
        qf_layout.setSpacing(16)
        qf_layout.setAlignment(Qt.AlignCenter)

        self.quiz_word_label = QLabel("")
        self.quiz_word_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #2c3e50;")
        self.quiz_word_label.setAlignment(Qt.AlignCenter)
        qf_layout.addWidget(self.quiz_word_label)

        self.quiz_phonetic_label = QLabel("")
        self.quiz_phonetic_label.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        self.quiz_phonetic_label.setAlignment(Qt.AlignCenter)
        qf_layout.addWidget(self.quiz_phonetic_label)

        qf_layout.addWidget(self._make_separator())

        self.quiz_prompt = QLabel("选择正确的中文释义：")
        self.quiz_prompt.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        self.quiz_prompt.setAlignment(Qt.AlignCenter)
        qf_layout.addWidget(self.quiz_prompt)

        self.quiz_options_layout = QVBoxLayout()
        self.quiz_options_layout.setSpacing(10)
        qf_layout.addLayout(self.quiz_options_layout)

        self.quiz_feedback = QLabel("")
        self.quiz_feedback.setAlignment(Qt.AlignCenter)
        self.quiz_feedback.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.quiz_feedback.hide()
        qf_layout.addWidget(self.quiz_feedback)

        layout.addWidget(self.quiz_frame, alignment=Qt.AlignCenter)

    def _setup_spell_mode_ui(self):
        """拼写模式 UI"""
        layout = QVBoxLayout(self.spell_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.spell_frame = QFrame()
        self.spell_frame.setStyleSheet("QFrame { background: white; border: 2px solid #e0e0e0; border-radius: 16px; padding: 40px; }")
        self.spell_frame.setMinimumSize(500, 350)
        self.spell_frame.setMaximumSize(600, 420)
        sf_layout = QVBoxLayout(self.spell_frame)
        sf_layout.setSpacing(16)
        sf_layout.setAlignment(Qt.AlignCenter)

        self.spell_hint = QLabel("")
        self.spell_hint.setStyleSheet("font-size: 20px; color: #34495e;")
        self.spell_hint.setAlignment(Qt.AlignCenter)
        self.spell_hint.setWordWrap(True)
        sf_layout.addWidget(self.spell_hint)

        self.spell_speak_btn = QPushButton("🔊 再听一次")
        self.spell_speak_btn.setStyleSheet("QPushButton { padding: 8px 20px; background: #e8f4fc; color: #4a90d9; border: none; border-radius: 8px; font-size: 14px; } QPushButton:hover { background: #d0e8f7; }")
        self.spell_speak_btn.clicked.connect(self._on_speak)
        sf_layout.addWidget(self.spell_speak_btn, alignment=Qt.AlignCenter)

        sf_layout.addWidget(self._make_separator())

        self.spell_input = QLineEdit()
        self.spell_input.setPlaceholderText("输入英文单词...")
        self.spell_input.setAlignment(Qt.AlignCenter)
        self.spell_input.setStyleSheet("QLineEdit { padding: 12px; font-size: 24px; border: 2px solid #e0e0e0; border-radius: 8px; text-align: center; } QLineEdit:focus { border-color: #4a90d9; }")
        self.spell_input.returnPressed.connect(self._on_spell_submit)
        sf_layout.addWidget(self.spell_input)

        self.spell_result = QLabel("")
        self.spell_result.setAlignment(Qt.AlignCenter)
        self.spell_result.setStyleSheet("font-size: 18px;")
        self.spell_result.hide()
        sf_layout.addWidget(self.spell_result)

        self.spell_submit_btn = QPushButton("提交")
        self.spell_submit_btn.setStyleSheet("QPushButton { padding: 10px 40px; background: #4a90d9; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; } QPushButton:hover { background: #357abd; }")
        self.spell_submit_btn.clicked.connect(self._on_spell_submit)
        sf_layout.addWidget(self.spell_submit_btn, alignment=Qt.AlignCenter)

        layout.addWidget(self.spell_frame, alignment=Qt.AlignCenter)

    def _make_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #e0e0e0;")
        line.setMaximumWidth(350)
        return line

    # --- CEFR / Mode 切换 ---
    def _on_cefr_tab(self, level):
        self.current_cefr = level
        for btn, lv in self.cefr_buttons:
            btn.setChecked(lv == level)
        self._level_words = []
        self._level_word_idx = 0
        self._load_next_card()

    def _on_mode_tab(self, mode):
        self.current_mode = mode
        for btn, m in self.mode_buttons:
            btn.setChecked(m == mode)
        mode_idx = {"card": 0, "quiz": 1, "spell": 2}[mode]
        self.content_stack.setCurrentIndex(mode_idx)
        self._load_next_card()

    # --- 加载单词 ---
    def _load_next_card(self):
        word_data = self._get_next_word()
        if not word_data:
            self._show_complete()
            return
        self.current_word = word_data.get('word', '')
        self.current_word_data = word_data
        self.showing_answer = False

        if self.current_mode == "card":
            self._show_card_mode()
        elif self.current_mode == "quiz":
            self._show_quiz_mode()
        elif self.current_mode == "spell":
            self._show_spell_mode()

        self._update_progress()

    def _get_next_word(self):
        """根据当前筛选获取下一个单词"""
        import os
        import random
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')

        if self.current_cefr != "全部":
            # 从 vocab_cefr 表获取该等级的单词
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT vc.word, vc.cefr_level FROM vocab_cefr vc
                    LEFT JOIN user_words uw ON vc.word = uw.word
                    WHERE vc.cefr_level = ? AND (uw.due_date IS NULL OR uw.due_date <= datetime('now') OR uw.status = 'new')
                    ORDER BY uw.due_date ASC NULLS FIRST
                    LIMIT 100
                ''', (self.current_cefr,))
                rows = cursor.fetchall()
                conn.close()
                if rows:
                    # 优先选未学过的
                    new_words = [r for r in rows]
                    random.shuffle(new_words)
                    word = new_words[0]['word']
                    result = self.dictionary.lookup(word)
                    if isinstance(result, dict):
                        return result
            except sqlite3.OperationalError:
                pass

        # 默认行为：到期复习 + 随机新词
        due_words = self.database.get_due_words(limit=10)
        if not due_words:
            random_words = self.dictionary.get_random_words(10)
            for wd in random_words:
                self.database.get_or_create_user_word(wd['word'])
            due_words = self.database.get_due_words(limit=10)
        if due_words:
            word = due_words[0]['word']
            result = self.dictionary.lookup(word)
            if isinstance(result, dict):
                return result
        return None

    def _show_complete(self):
        msg = "🎉 今日学习完成！"
        if self.current_mode == "card":
            self.word_label.setText(msg)
            self.phonetic_label.setText("明天再来吧")
            self.show_btn.hide()
            for b in self.rating_buttons:
                b.hide()
        elif self.current_mode == "quiz":
            self.quiz_word_label.setText(msg)
            self.quiz_phonetic_label.setText("")
        elif self.current_mode == "spell":
            self.spell_hint.setText(msg)
            self.spell_input.hide()
            self.spell_submit_btn.hide()

    # --- 卡片模式 ---
    def _show_card_mode(self):
        self.content_stack.setCurrentIndex(0)
        self.answer_area.hide()
        self.show_btn.show()
        for b in self.rating_buttons:
            b.hide()

        d = self.current_word_data or {}
        self.word_label.setText(d.get('word', ''))
        self.phonetic_label.setText(f"/{d.get('phonetic', '')}/" if d.get('phonetic') else "")

        # CEFR 标签
        if self.cefr_tagger.available:
            level = self.cefr_tagger.get_level(d.get('word', ''))
            if level:
                colors = {"A1": "#3498db", "A2": "#27ae60", "B1": "#e67e22", "B2": "#e74c3c", "C1": "#9b59b6", "C2": "#2c3e50"}
                c = colors.get(str(level), "#7f8c8d")
                self.cefr_badge.setText(str(level))
                self.cefr_badge.setStyleSheet(f"font-size: 11px; padding: 2px 8px; border-radius: 10px; background: {c}; color: white;")
                self.cefr_badge.show()
            else:
                self.cefr_badge.hide()
        else:
            self.cefr_badge.hide()

        # Collins 星级
        collins = d.get('collins', '')
        if collins and str(collins).isdigit():
            stars = int(collins)
            self.collins_label.setText("⭐" * min(stars, 5) + f"  Collins {stars}星")
            self.collins_label.show()
        else:
            self.collins_label.hide()

    def _show_answer(self):
        self.showing_answer = True
        self.show_btn.hide()
        d = self.current_word_data or {}
        self.pos_label.setText(d.get('pos', ''))
        self.translation_label.setText(d.get('translation', '暂无释义'))
        self.definition_label.setText(d.get('definition', ''))
        self.answer_area.show()

        # 例句
        detail = d.get('detail', '')
        example = self._extract_example(detail)
        if example:
            self.example_label.setText(f"💬 {example}")
            self.example_label.show()
        else:
            self.example_label.hide()

        # 评分按钮 + 间隔
        user_word = self.database.get_or_create_user_word(self.current_word)
        fsrs_state = FSRSState.from_json(user_word.get('fsrs_state'))
        intervals = self.fsrs.get_rating_intervals(fsrs_state)
        texts = {'again': '重来', 'hard': '困难', 'good': '一般', 'easy': '简单'}
        for btn in self.rating_buttons:
            r = btn.property("rating")
            btn.setText(f"{texts[r]}\n< {intervals.get(r, 1)}天")
            btn.show()

    def _extract_example(self, detail):
        """从 detail 字段提取例句"""
        if not detail:
            return ""
        import re
        # detail 格式通常是 " 〈例句〉text\n 〈例句〉text" 或类似
        matches = re.findall(r'[A-Za-z].*?[.!?]', detail)
        for m in matches:
            if len(m) > 15 and len(m) < 200 and ' ' in m:
                return m.strip()
        return ""

    def _on_speak(self):
        if self.tts and self.tts.available and self.current_word:
            self.tts.speak(self.current_word)

    # --- 选择题模式 ---
    def _show_quiz_mode(self):
        self.content_stack.setCurrentIndex(1)
        d = self.current_word_data or {}
        self.quiz_word_label.setText(d.get('word', ''))
        self.quiz_phonetic_label.setText(f"/{d.get('phonetic', '')}/" if d.get('phonetic') else "")
        self.quiz_feedback.hide()

        # 清空旧选项
        while self.quiz_options_layout.count():
            item = self.quiz_options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        correct = d.get('translation', '暂无释义')
        options = self._generate_quiz_options(correct)

        import random
        random.shuffle(options)

        for i, opt in enumerate(options):
            btn = QPushButton(opt)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { padding: 12px 20px; border: 2px solid #e0e0e0; border-radius: 8px;
                    background: white; color: #2c3e50; font-size: 14px; text-align: left; }
                QPushButton:hover { border-color: #4a90d9; background: #f8fbfe; }
            """)
            is_correct = (opt == correct)
            btn.clicked.connect(lambda checked, o=opt, c=is_correct: self._on_quiz_answer(o, c))
            self.quiz_options_layout.addWidget(btn)

    def _generate_quiz_options(self, correct_translation):
        """生成 4 个选择题选项"""
        import os
        import random
        import sqlite3
        options = [correct_translation]
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            if self.current_cefr != "全部":
                cursor.execute('SELECT word FROM vocab_cefr WHERE cefr_level = ? AND word != ? LIMIT 20',
                               (self.current_cefr, self.current_word))
            else:
                cursor.execute("SELECT word FROM stardict WHERE word != ? ORDER BY RANDOM() LIMIT 20",
                               (self.current_word,))
            candidates = [r[0] for r in cursor.fetchall()]
            conn.close()
            random.shuffle(candidates)
            for w in candidates[:3]:
                result = self.dictionary.lookup(w)
                if isinstance(result, dict) and result.get('translation'):
                    t = result['translation'].split('\n')[0][:50]
                    if t not in options:
                        options.append(t)
        except Exception:
            pass
        # 补足 4 个
        fillers = ["一个东西", "做某事", "某种状态", "描述属性"]
        while len(options) < 4:
            options.append(fillers[len(options) - 1])
        return options[:4]

    def _on_quiz_answer(self, selected, is_correct):
        # 禁用所有按钮
        for i in range(self.quiz_options_layout.count()):
            w = self.quiz_options_layout.itemAt(i).widget()
            if w:
                w.setEnabled(False)
                if w.text() == selected:
                    color = "#27ae60" if is_correct else "#e74c3c"
                    w.setStyleSheet(f"QPushButton {{ padding: 12px 20px; border: 2px solid {color}; border-radius: 8px; background: {color}22; color: {color}; font-size: 14px; }}")

        self.quiz_feedback.show()
        if is_correct:
            self.quiz_feedback.setText("✅ 正确！")
            self.quiz_feedback.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
            self._record_and_advance("good")
        else:
            d = self.current_word_data or {}
            self.quiz_feedback.setText(f"❌ 正确答案: {d.get('translation', '')}")
            self.quiz_feedback.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
            self._record_and_advance("again")

        # 2 秒后下一题
        QTimer.singleShot(2000, self._load_next_card)

    # --- 拼写模式 ---
    def _show_spell_mode(self):
        self.content_stack.setCurrentIndex(2)
        d = self.current_word_data or {}
        self.spell_hint.setText(d.get('translation', '暂无释义'))
        self.spell_input.setText("")
        self.spell_input.show()
        self.spell_submit_btn.show()
        self.spell_result.hide()
        self.spell_input.setFocus()
        # 自动播放发音
        if self.tts and self.tts.available:
            self.tts.speak(self.current_word)

    def _on_spell_submit(self):
        user_input = self.spell_input.text().strip().lower()
        correct = self.current_word.lower()
        if not user_input:
            return

        self.spell_result.show()
        if user_input == correct:
            self.spell_result.setText("✅ 完全正确！")
            self.spell_result.setStyleSheet("font-size: 18px; color: #27ae60; font-weight: bold;")
            self._record_and_advance("good")
            QTimer.singleShot(1500, self._load_next_card)
        else:
            # 逐字母对比
            html = self._build_spell_comparison(user_input, correct)
            self.spell_result.setText(html)
            self.spell_result.setStyleSheet("font-size: 20px; font-weight: bold; letter-spacing: 2px;")
            self._record_and_advance("again")
            QTimer.singleShot(2500, self._load_next_card)

    def _build_spell_comparison(self, user_input, correct):
        """构建逐字母对比 HTML"""
        result = []
        max_len = max(len(user_input), len(correct))
        for i in range(max_len):
            if i < len(user_input) and i < len(correct):
                if user_input[i] == correct[i]:
                    result.append(f'<span style="color:#27ae60">{user_input[i]}</span>')
                else:
                    result.append(f'<span style="color:#e74c3c;text-decoration:underline">{user_input[i] if i < len(user_input) else "_"}</span>')
            elif i < len(correct):
                result.append(f'<span style="color:#e74c3c">_{correct[i]}</span>')
        return "你的答案: " + "".join(result) + f"<br><span style='color:#7f8c8d;font-size:14px'>正确: {correct}</span>"

    # --- 通用方法 ---
    def _on_rating(self, rating):
        if not self.current_word:
            return
        self._record_and_advance(rating)
        self._load_next_card()

    def _record_and_advance(self, rating):
        """统一记录学习并更新 FSRS"""
        if not self.current_word:
            return
        user_word = self.database.get_or_create_user_word(self.current_word)
        fsrs_state = FSRSState.from_json(user_word.get('fsrs_state'))
        new_state, due_date = self.fsrs.review(fsrs_state, rating)
        status = 'learning' if new_state.state in [1, 3] else 'review'
        self.database.update_user_word(self.current_word, status=status, fsrs_state=new_state.to_json(), due_date=due_date.isoformat())
        self.database.add_study_record(self.current_word, 'review', rating)
        is_new = user_word.get('status') == 'new'
        self.database.update_daily_stats(new_words=1 if is_new else 0, review_words=0 if is_new else 1, correct_count=1 if rating != 'again' else 0, total_count=1)

    def _update_progress(self):
        stats = self.database.get_daily_stats()
        due_count = len(self.database.get_due_words(limit=100))
        self.progress_label.setText(f"今日新词: {stats['new_words']} | 待复习: {due_count}")
        self.progress_bar.setValue(min(stats['new_words'] + stats['review_words'], 50))
        self.progress_bar.setMaximum(50)


class StatsPage(QWidget):
    """学习统计页面"""
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self._setup_ui()
        self._load_stats()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 标题
        title = QLabel("📊 学习统计")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        # 今日概览卡片
        overview = QFrame()
        overview.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        overview_layout = QHBoxLayout(overview)
        overview_layout.setSpacing(30)

        self.stat_labels = {}
        stat_items = [
            ("new_words", "📝 新词", "#4a90d9"),
            ("review_words", "🔄 复习", "#27ae60"),
            ("correct_rate", "✅ 正确率", "#e67e22"),
            ("study_minutes", "⏱️ 分钟", "#9b59b6"),
        ]

        for key, label, color in stat_items:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setAlignment(Qt.AlignCenter)

            value_label = QLabel("0")
            value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
            value_label.setAlignment(Qt.AlignCenter)
            item_layout.addWidget(value_label)

            name_label = QLabel(label)
            name_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
            name_label.setAlignment(Qt.AlignCenter)
            item_layout.addWidget(name_label)

            overview_layout.addWidget(item_widget)
            self.stat_labels[key] = value_label

        layout.addWidget(overview)

        # 学习记录
        records_title = QLabel("📋 最近学习记录")
        records_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 20px;")
        layout.addWidget(records_title)

        self.records_text = QTextEdit()
        self.records_text.setReadOnly(True)
        self.records_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        self.records_text.setMaximumHeight(200)
        layout.addWidget(self.records_text)

        # 刷新按钮
        refresh_btn = QPushButton("刷新统计")
        refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        refresh_btn.clicked.connect(self._load_stats)
        layout.addWidget(refresh_btn, alignment=Qt.AlignLeft)

        layout.addStretch()

    def _load_stats(self):
        """加载统计数据"""
        stats = self.database.get_daily_stats()

        self.stat_labels['new_words'].setText(str(stats['new_words']))
        self.stat_labels['review_words'].setText(str(stats['review_words']))

        correct_rate = 0
        if stats['total_count'] > 0:
            correct_rate = round(stats['correct_count'] / stats['total_count'] * 100)
        self.stat_labels['correct_rate'].setText(f"{correct_rate}%")

        self.stat_labels['study_minutes'].setText(str(stats['study_minutes']))

        # 加载最近记录
        conn = self.database.conn
        cursor = conn.cursor()
        cursor.execute(
            'SELECT word, action, result, created_at FROM study_records ORDER BY created_at DESC LIMIT 20'
        )
        records = cursor.fetchall()

        text = "<table style='width:100%; border-collapse:collapse;'>"
        text += "<tr style='background:#f5f5f5;'><th style='padding:8px;text-align:left;'>单词</th><th style='padding:8px;text-align:left;'>操作</th><th style='padding:8px;text-align:left;'>结果</th><th style='padding:8px;text-align:left;'>时间</th></tr>"

        for row in records:
            word, action, result, created_at = row
            result_text = result or '-'
            text += f"<tr><td style='padding:6px;border-bottom:1px solid #eee;'><b>{word}</b></td><td style='padding:6px;border-bottom:1px solid #eee;'>{action}</td><td style='padding:6px;border-bottom:1px solid #eee;'>{result_text}</td><td style='padding:6px;border-bottom:1px solid #eee;color:#999;'>{created_at}</td></tr>"

        text += "</table>"
        self.records_text.setHtml(text)


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("英语学习助手")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
        """)

        # 初始化数据
        self.dictionary = Dictionary()
        self.database = Database()

        self._setup_ui()

    def _setup_ui(self):
        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # 侧边栏导航
        sidebar = QWidget()
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
            }
        """)
        sidebar.setMaximumWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 16, 0, 16)
        sidebar_layout.setSpacing(4)

        # 标题
        title = QLabel("📖 英语学习\n助手")
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 16px;
            text-align: center;
        """)
        title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title)

        sidebar_layout.addSpacing(20)

        # 导航按钮
        self.nav_buttons = []
        nav_items = [
            ("📋 课程大纲", 0),
            ("📚 情景对话", 1),
            ("🔍 词典查询", 2),
            ("📝 单词学习", 3),
            ("🎧 听写练习", 4),
            ("📖 语法练习", 5),
            ("🎭 角色扮演", 6),
            ("📊 学习统计", 7),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    color: #bdc3c7;
                    font-size: 14px;
                    padding: 14px 20px;
                    border: none;
                    text-align: left;
                    background: transparent;
                }
                QPushButton:hover {
                    color: white;
                    background-color: #34495e;
                }
                QPushButton:checked {
                    color: white;
                    background-color: #4a90d9;
                }
            """)
            btn.clicked.connect(lambda checked, i=index: self._switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # 激励信息栏
        self.motivation_frame = QFrame()
        self.motivation_frame.setStyleSheet("QFrame { background: #f0f7ff; border-radius: 8px; margin: 8px; padding: 10px; }")
        mot_layout = QVBoxLayout(self.motivation_frame)
        mot_layout.setSpacing(4)
        mot_layout.setContentsMargins(10, 8, 10, 8)

        self.points_label = QLabel("⭐ 今日积分: 0")
        self.points_label.setStyleSheet("font-size: 12px; color: #2c3e50; font-weight: bold;")
        mot_layout.addWidget(self.points_label)

        self.streak_label = QLabel("🔥 连续学习: 0 天")
        self.streak_label.setStyleSheet("font-size: 12px; color: #e67e22;")
        mot_layout.addWidget(self.streak_label)

        self.badge_count_label = QLabel("🏅 徽章: 0/14")
        self.badge_count_label.setStyleSheet("font-size: 12px; color: #9b59b6;")
        mot_layout.addWidget(self.badge_count_label)

        sidebar_layout.addWidget(self.motivation_frame)

        # 版本信息
        version = QLabel("v1.6.0")
        version.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 8px;")
        version.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(version)

        layout.addWidget(sidebar)

        # 内容区域
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #f0f2f5;")

        # 页面1: 课程大纲
        self.course_page = CoursePage()
        self.stack.addWidget(self.course_page)

        # 页面2: 情景对话
        self.dialog_page = DialogPage(self.dictionary)
        self.stack.addWidget(self.dialog_page)

        # 页面3: 词典查询
        self.dict_page = DictionaryPage(self.dictionary)
        self.stack.addWidget(self.dict_page)

        # 页面4: 单词学习
        self.tts = TTSEngine()
        self.study_tracker = StudyTracker()
        self.study_page = StudyPage(self.dictionary, self.database, self.tts)
        self.stack.addWidget(self.study_page)

        # 页面5: 听写练习
        self.dictation_page = DictationPage(self.dictionary, self.database)
        self.stack.addWidget(self.dictation_page)

        # 页面6: 角色扮演
        self.roleplay_page = RolePlayPage(self.dictionary, self.database)
        self.stack.addWidget(self.roleplay_page)

        # 页面7: 语法练习
        self.grammar_practice_page = GrammarPracticePage()
        self.stack.addWidget(self.grammar_practice_page)

        # 页面8: 学习统计
        self.stats_page = StatsPage(self.database)
        self.stack.addWidget(self.stats_page)

        layout.addWidget(self.stack)

        # 默认选中第一个
        self.nav_buttons[0].setChecked(True)

    def _switch_page(self, index):
        """切换页面"""
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self._refresh_motivation()

    def _refresh_motivation(self):
        """刷新激励信息"""
        try:
            today_pts = self.study_tracker.get_today_points()
            streak = self.study_tracker.get_streak_days()
            badges = self.study_tracker.get_earned_badges()
            self.points_label.setText(f"⭐ 今日积分: {today_pts}")
            self.streak_label.setText(f"🔥 连续学习: {streak} 天")
            self.badge_count_label.setText(f"🏅 徽章: {len(badges)}/14")
        except Exception:
            pass

    def closeEvent(self, event):
        """关闭时清理资源"""
        self.dictionary.close()
        self.database.close()
        event.accept()

def main():
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine

    # 确保 Windows 终端 UTF-8
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass

    app = QGuiApplication(sys.argv)

    # 实例 QML 桥接单例
    from ui.qml_bridge import QmlBridge
    bridge = QmlBridge()

    engine = QQmlApplicationEngine()
    engine.warnings.connect(lambda warnings: [print("QML Warning:", w.toString()) for w in warnings])
    qml_dir = os.path.join(os.path.dirname(__file__), 'ui', 'qml')
    engine.addImportPath(qml_dir)
    engine.rootContext().setContextProperty("qmlBridge", bridge)

    main_qml = os.path.join(qml_dir, 'main.qml')
    engine.load(QUrl.fromLocalFile(main_qml))

    if not engine.rootObjects():
        print("❌ QML 界面加载失败: 无法找到根对象")
        sys.exit(-1)

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
