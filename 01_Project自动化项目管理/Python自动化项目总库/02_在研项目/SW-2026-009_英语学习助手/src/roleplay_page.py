"""
角色扮演对话练习页面
用户选择对话场景和角色，逐句进行对话练习
支持打字输入和语音输入，使用 AnswerMatcher 进行答案评估
"""
import re

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from answer_matcher import AnswerMatcher, AnswerSpec, MatchResult
from asr_engine import ASREngine
from dialogs_data import get_all_dialogs, get_dialog
from tts_engine import TTSEngine
from us_travel_dialogs import get_all_us_dialogs, get_us_dialog

# ---------------------------------------------------------------------------
# 停用词集合（用于自动提取关键词）
# ---------------------------------------------------------------------------
_STOP_WORDS = {
    'i', 'me', 'my', 'you', 'your', 'he', 'she', 'it', 'we', 'they',
    'a', 'an', 'the', 'is', 'am', 'are', 'was', 'were', 'be', 'been',
    'do', 'does', 'did', 'have', 'has', 'had', 'can', 'could', 'will',
    'would', 'should', 'may', 'might', 'shall', 'to', 'of', 'in',
    'for', 'on', 'at', 'with', 'from', 'by', 'about', 'and', 'or',
    'but', 'not', 'no', 'so', 'if', 'that', 'this', 'please',
    'yes', 'here', 'there', 'what', 'how', 'when', 'where', 'who',
    'like', 'want', 'need', 'get', 'got',
    'very', 'much', 'just', 'also', 'too', 'well',
}


def _extract_keywords(text: str, max_keywords: int = 3) -> list:
    """从英文句子中自动提取最重要的内容词作为关键词。"""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    content_words = [w for w in words if w not in _STOP_WORDS and len(w) > 2]
    # 去重并保持顺序
    seen = set()
    unique = []
    for w in content_words:
        if w not in seen:
            seen.add(w)
            unique.append(w)
    return unique[:max_keywords]


def _generate_alternatives(text: str) -> list:
    """根据原始文本生成 2-3 个合理的替代答案。

    策略：
    - 简短版：去掉修饰语，保留核心意思
    - 口语版：用更口语化的表达
    - 同义替换：替换部分词汇
    """
    alternatives = []
    lower = text.lower().strip()
    lower_stripped = lower.rstrip('.,!?;')

    # --- 策略 1: 简短回答 ---
    # 如果句子较长，尝试提取核心部分
    if len(lower_stripped.split()) > 4:
        words = lower_stripped.split()
        # 去掉首尾的填充词
        core_start = 0
        for i, w in enumerate(words):
            if w not in ('yes', 'no', 'well', 'oh', 'sure', 'okay', 'ok', 'great', 'please'):
                core_start = i
                break
        core = ' '.join(words[core_start:])
        if core != lower_stripped and len(core.split()) >= 2:
            alternatives.append(core)

    # --- 策略 2: 简单同义替换 ---
    replacements = {
        'i would like': "i'll take",
        'i will': "i'll",
        'i would': "i'd",
        'i have': "i've",
        'i am': "i'm",
        'i will have': "i'll have",
        'i would like to': "i want to",
        'could you': "can you",
        'thank you': "thanks",
        'thank you very much': "thanks a lot",
        'here you are': "here you go",
        'that is': "that's",
        'that is all': "that's all",
        'do you have': "have you got",
        'let me': "let's",
        'of course': "sure",
        'excuse me': "sorry",
        'i am looking for': "i need",
        'how much is': "what is the price of",
        'i will take': "i'll take",
        'i will have': "i'll have",
        'nice to meet you': "pleased to meet you",
        'good morning': "morning",
        'good evening': "evening",
        'good afternoon': "afternoon",
    }

    alt = lower_stripped
    for old, new in replacements.items():
        if old in alt:
            alt = alt.replace(old, new, 1)
            break  # 只做一处替换
    if alt != lower_stripped and alt not in alternatives:
        alternatives.append(alt)

    # --- 策略 3: 极简版（针对短句）---
    if len(lower_stripped.split()) <= 5:
        # 尝试生成更口语化的版本
        short_map = {
            'yes please': "yes",
            'yes i do': "yes",
            'no i don\'t': "no",
            'no i do not': "no",
            'yes i would': "yes",
            'yes i will': "yes",
            'of course': "sure",
            'yes thank you': "yes thanks",
            'that is all thank you': "that is all",
            'thank you very much': "thanks a lot",
            'i will take it': "i will take it",
            'yes please thank you': "yes please",
            'this fits well how much is it': "how much is this",
        }
        for pattern, short in short_map.items():
            if pattern in lower_stripped:
                if short not in alternatives:
                    alternatives.append(short)
                break

    # 去重并限制数量
    seen_alt = {lower_stripped}
    unique_alts = []
    for a in alternatives:
        a_clean = a.strip()
        if a_clean and a_clean not in seen_alt:
            seen_alt.add(a_clean)
            unique_alts.append(a_clean)
    return unique_alts[:3]


def _build_answer_spec(text: str) -> AnswerSpec:
    """根据对话原始文本自动构建 AnswerSpec。"""
    keywords = _extract_keywords(text)
    alternatives = _generate_alternatives(text)
    return AnswerSpec(
        primary_answer=text.strip(),
        alternative_answers=alternatives,
        keywords=keywords,
    )


# ---------------------------------------------------------------------------
# 对话气泡组件
# ---------------------------------------------------------------------------
class _ChatBubble(QFrame):
    """单条对话气泡（左侧=对方，右侧=用户）。"""

    def __init__(self, speaker: str, text: str, translation: str,
                 is_user: bool = False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self._setup_ui(speaker, text, translation)

    def _setup_ui(self, speaker, text, translation):
        self.setFrameStyle(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        container = QVBoxLayout(self)
        container.setSpacing(4)
        container.setContentsMargins(0, 0, 0, 0)

        # 对齐方向
        if self.is_user:
            container.setAlignment(Qt.AlignRight)
        else:
            container.setAlignment(Qt.AlignLeft)

        # 气泡主体
        bubble = QFrame()
        if self.is_user:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: #4a90d9;
                    border-radius: 12px;
                    padding: 10px 14px;
                    max-width: 380px;
                }
            """)
        else:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 12px;
                    padding: 10px 14px;
                    max-width: 380px;
                }
            """)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setSpacing(4)
        bubble_layout.setContentsMargins(12, 10, 12, 10)

        # 说话人标签
        speaker_label = QLabel(speaker)
        if self.is_user:
            speaker_label.setStyleSheet(
                "font-size: 12px; font-weight: bold; color: #ffffff;")
        else:
            speaker_label.setStyleSheet(
                "font-size: 12px; font-weight: bold; color: #4a90d9;")
        bubble_layout.addWidget(speaker_label)

        # 英文文本
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        if self.is_user:
            text_label.setStyleSheet(
                "font-size: 15px; color: #ffffff; line-height: 1.4;")
        else:
            text_label.setStyleSheet(
                "font-size: 15px; color: #2c3e50; line-height: 1.4;")
        bubble_layout.addWidget(text_label)

        # 中文翻译
        if translation:
            trans_label = QLabel(translation)
            trans_label.setWordWrap(True)
            if self.is_user:
                trans_label.setStyleSheet(
                    "font-size: 12px; color: #d4e6f9;")
            else:
                trans_label.setStyleSheet(
                    "font-size: 12px; color: #95a5a6;")
            bubble_layout.addWidget(trans_label)

        container.addWidget(bubble)


class _PromptBubble(QFrame):
    """用户需要回答的提示气泡（右侧，带输入区）。"""

    def __init__(self, speaker: str, prompt_text: str, translation: str,
                 on_tts_play=None, parent=None):
        super().__init__(parent)
        self.on_tts_play = on_tts_play
        self._setup_ui(speaker, prompt_text, translation)

    def _setup_ui(self, speaker, prompt_text, translation):
        self.setFrameStyle(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        container = QVBoxLayout(self)
        container.setSpacing(4)
        container.setContentsMargins(0, 0, 0, 0)
        container.setAlignment(Qt.AlignRight)

        # 提示气泡
        bubble = QFrame()
        bubble.setStyleSheet("""
            QFrame {
                background-color: #fff8e1;
                border: 2px dashed #f0c040;
                border-radius: 12px;
                padding: 10px 14px;
                max-width: 380px;
            }
        """)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setSpacing(4)
        bubble_layout.setContentsMargins(12, 10, 12, 10)

        hint_label = QLabel(">> 请用英语说:")
        hint_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #e67e22;")
        bubble_layout.addWidget(hint_label)

        speaker_label = QLabel(speaker)
        speaker_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #b7791f;")
        bubble_layout.addWidget(speaker_label)

        # 显示参考答案（可折叠）
        ref_label = QLabel(prompt_text)
        ref_label.setWordWrap(True)
        ref_label.setStyleSheet("font-size: 14px; color: #92400e; font-style: italic;")
        ref_label.hide()  # 默认隐藏，用户可选择查看
        bubble_layout.addWidget(ref_label)
        self.ref_label = ref_label

        if translation:
            trans_label = QLabel(translation)
            trans_label.setWordWrap(True)
            trans_label.setStyleSheet("font-size: 12px; color: #b7791f;")
            bubble_layout.addWidget(trans_label)

        # 查看参考答案按钮
        self.show_ref_btn = QPushButton("查看参考答案")
        self.show_ref_btn.setFlat(True)
        self.show_ref_btn.setCursor(Qt.PointingHandCursor)
        self.show_ref_btn.setStyleSheet("""
            QPushButton {
                color: #e67e22;
                font-size: 12px;
                padding: 2px 6px;
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                color: #d35400;
                text-decoration: underline;
            }
        """)
        self.show_ref_btn.clicked.connect(self._toggle_reference)
        bubble_layout.addWidget(self.show_ref_btn)

        container.addWidget(bubble)

    def _toggle_reference(self):
        """切换参考答案的显示/隐藏。"""
        if self.ref_label.isVisible():
            self.ref_label.hide()
            self.show_ref_btn.setText("查看参考答案")
        else:
            self.ref_label.show()
            self.show_ref_btn.setText("隐藏参考答案")


class _ResultBubble(QFrame):
    """匹配结果气泡。"""

    def __init__(self, match_result: MatchResult, user_input: str, parent=None):
        super().__init__(parent)
        self._setup_ui(match_result, user_input)

    def _setup_ui(self, result: MatchResult, user_input: str):
        self.setFrameStyle(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        container = QVBoxLayout(self)
        container.setSpacing(4)
        container.setContentsMargins(0, 0, 0, 0)
        container.setAlignment(Qt.AlignRight)

        bubble = QFrame()
        if result.is_correct:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: #f0fdf4;
                    border: 1px solid #86efac;
                    border-radius: 10px;
                    padding: 10px 14px;
                    max-width: 400px;
                }
            """)
        else:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: #fef2f2;
                    border: 1px solid #fecaca;
                    border-radius: 10px;
                    padding: 10px 14px;
                    max-width: 400px;
                }
            """)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setSpacing(6)
        bubble_layout.setContentsMargins(12, 10, 12, 10)

        # 分数
        score_pct = int(result.score * 100)
        score_label = QLabel(f"匹配度: {score_pct}%")
        if result.is_correct:
            score_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: #27ae60;")
        else:
            score_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: #dc2626;")
        bubble_layout.addWidget(score_label)

        # 用户输入
        user_label = QLabel(f"你说: {user_input}")
        user_label.setWordWrap(True)
        user_label.setStyleSheet("font-size: 13px; color: #34495e;")
        bubble_layout.addWidget(user_label)

        # 差异对比
        if result.diff_html:
            diff_label = QLabel(f"对比: {result.diff_html}")
            diff_label.setWordWrap(True)
            diff_label.setStyleSheet(
                "font-size: 13px; font-family: 'Consolas', monospace;")
            bubble_layout.addWidget(diff_label)

        # 最佳答案
        best_label = QLabel(f"最佳匹配: {result.best_answer}")
        best_label.setWordWrap(True)
        best_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        bubble_layout.addWidget(best_label)

        # 反馈
        feedback_label = QLabel(result.feedback)
        feedback_label.setWordWrap(True)
        feedback_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        bubble_layout.addWidget(feedback_label)

        container.addWidget(bubble)


# ---------------------------------------------------------------------------
# 录音指示器
# ---------------------------------------------------------------------------
class _RecordingIndicator(QFrame):
    """录音中的红色脉冲指示器。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pulse_state = True
        self.setFixedSize(16, 16)
        self._update_style()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._toggle_pulse)
        self._timer.setInterval(600)

    def start(self):
        self._pulse_state = True
        self._update_style()
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 8px;
            }
        """)

    def _toggle_pulse(self):
        self._pulse_state = not self._pulse_state
        self._update_style()

    def _update_style(self):
        if self._pulse_state:
            self.setStyleSheet("""
                QFrame {
                    background-color: #e74c3c;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #c0392b;
                    border-radius: 8px;
                }
            """)


# ---------------------------------------------------------------------------
# 主页面
# ---------------------------------------------------------------------------
class RolePlayPage(QWidget):
    """角色扮演对话练习页面。"""

    def __init__(self, dictionary, database, parent=None):
        super().__init__(parent)
        self.dictionary = dictionary
        self.database = database

        # 引擎
        self.tts = TTSEngine()
        self.asr = ASREngine()
        self.matcher = AnswerMatcher()

        # 对话数据
        self._all_dialogs_meta = []  # [{id, title, title_en, ...}, ...]
        self._current_dialog = None  # 原始对话数据
        self._current_dialog_id = None
        self._current_role = "You"
        self._other_role = None

        # 对话进度
        self._line_index = 0
        self._lines = []       # 当前对话的所有行
        self._is_waiting_user = False
        self._has_answered = False
        self._current_answer_spec = None
        self._total_score = 0.0
        self._total_turns = 0

        # 录音指示器
        self._recording_indicator = _RecordingIndicator()

        self._setup_ui()
        self._load_dialog_list()

    # ------------------------------------------------------------------
    # UI 构建
    # ------------------------------------------------------------------
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 30)

        # --- 标题栏 ---
        header = QHBoxLayout()
        self.title_label = QLabel("角色扮演练习")
        self.title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50;")
        header.addWidget(self.title_label)
        header.addStretch()

        self.score_label = QLabel("得分: --")
        self.score_label.setStyleSheet(
            "font-size: 14px; color: #7f8c8d;")
        header.addWidget(self.score_label)

        layout.addLayout(header)

        # --- 选择区域 ---
        select_frame = QFrame()
        select_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        select_layout = QHBoxLayout(select_frame)
        select_layout.setSpacing(16)

        # 对话选择
        select_layout.addWidget(QLabel("选择场景:"))
        self.dialog_combo = QComboBox()
        self.dialog_combo.setMinimumWidth(280)
        self.dialog_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                color: #2c3e50;
                background: white;
            }
            QComboBox:focus { border-color: #4a90d9; }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #4a90d9;
                font-size: 14px;
            }
        """)
        self.dialog_combo.currentIndexChanged.connect(self._on_dialog_changed)
        select_layout.addWidget(self.dialog_combo)

        # 角色选择
        select_layout.addWidget(QLabel("扮演角色:"))
        self.role_combo = QComboBox()
        self.role_combo.setMinimumWidth(120)
        self.role_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                color: #2c3e50;
                background: white;
            }
            QComboBox:focus { border-color: #4a90d9; }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #4a90d9;
                font-size: 14px;
            }
        """)
        self.role_combo.currentIndexChanged.connect(self._on_role_changed)
        select_layout.addWidget(self.role_combo)

        # 开始按钮
        self.start_btn = QPushButton("开始练习")
        self.start_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 28px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #219a52; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        self.start_btn.clicked.connect(self._start_practice)
        select_layout.addWidget(self.start_btn)

        select_layout.addStretch()

        # TTS / ASR 状态
        self.engine_status = QLabel(
            f"TTS: {self.tts.get_status()} | ASR: {self.asr.get_status()}")
        self.engine_status.setStyleSheet("font-size: 11px; color: #95a5a6;")
        select_layout.addWidget(self.engine_status)

        layout.addWidget(select_frame)

        # --- 对话区域 ---
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 30px;
            }
        """)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(8)
        self.chat_layout.setContentsMargins(8, 8, 8, 8)
        self.chat_layout.addStretch()

        self.chat_scroll.setWidget(self.chat_container)
        layout.addWidget(self.chat_scroll, stretch=1)

        # --- 输入区域 ---
        self.input_frame = QFrame()
        self.input_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        input_layout = QVBoxLayout(self.input_frame)
        input_layout.setSpacing(10)

        # 输入行
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("在此输入你的回答...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                color: #2c3e50;
            }
            QLineEdit:focus { border-color: #4a90d9; }
            QLineEdit:disabled { background-color: #f5f5f5; }
        """)
        self.input_field.returnPressed.connect(self._submit_answer)
        input_row.addWidget(self.input_field)

        # 语音输入按钮
        self.voice_btn = QPushButton(" 语音输入")
        self.voice_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 20px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        self.voice_btn.clicked.connect(self._toggle_voice)
        input_row.addWidget(self.voice_btn)

        # 录音指示器
        input_row.addWidget(self._recording_indicator)

        # 提交按钮
        self.submit_btn = QPushButton("提交")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 28px;
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #357abd; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        self.submit_btn.clicked.connect(self._submit_answer)
        input_row.addWidget(self.submit_btn)

        input_layout.addLayout(input_row)

        # 提示标签
        self.input_hint = QLabel("选择场景和角色后点击「开始练习」")
        self.input_hint.setStyleSheet("font-size: 12px; color: #95a5a6;")
        input_layout.addWidget(self.input_hint)

        layout.addWidget(self.input_frame)

        # 默认禁用输入
        self._set_input_enabled(False)

    # ------------------------------------------------------------------
    # 数据加载
    # ------------------------------------------------------------------
    def _load_dialog_list(self):
        """加载所有可用对话到下拉列表。"""
        self._all_dialogs_meta = []

        # 基础对话
        for d in get_all_dialogs():
            self._all_dialogs_meta.append(d)

        # 美国出差对话
        for d in get_all_us_dialogs():
            self._all_dialogs_meta.append(d)

        for dialog in self._all_dialogs_meta:
            label = f"{dialog['title']} ({dialog['title_en']}) [{dialog['difficulty']}]"
            self.dialog_combo.addItem(label)

        if not self._all_dialogs_meta:
            self.dialog_combo.addItem("暂无可用对话")
            self.start_btn.setEnabled(False)

    def _on_dialog_changed(self, index):
        """对话选择变更时更新角色列表。"""
        self.role_combo.clear()
        if index < 0 or index >= len(self._all_dialogs_meta):
            return

        dialog_id = self._all_dialogs_meta[index]['id']
        dialog = get_dialog(dialog_id) or get_us_dialog(dialog_id)
        if not dialog:
            return

        # 收集所有说话人
        speakers = set()
        for line in dialog.get('lines', []):
            speakers.add(line.get('speaker', ''))
        for speaker in sorted(speakers):
            display = speaker if speaker != "You" else "You (你)"
            self.role_combo.addItem(display, speaker)

        # 默认选 "You"
        for i in range(self.role_combo.count()):
            if self.role_combo.itemData(i) == "You":
                self.role_combo.setCurrentIndex(i)
                break

    def _on_role_changed(self, index):
        """角色选择变更。"""
        pass  # 角色在开始练习时读取

    # ------------------------------------------------------------------
    # 练习流程
    # ------------------------------------------------------------------
    def _start_practice(self):
        """开始角色扮演练习。"""
        index = self.dialog_combo.currentIndex()
        if index < 0 or index >= len(self._all_dialogs_meta):
            QMessageBox.information(self, "提示", "请先选择一个对话场景")
            return

        dialog_id = self._all_dialogs_meta[index]['id']
        dialog = get_dialog(dialog_id) or get_us_dialog(dialog_id)
        if not dialog or not dialog.get('lines'):
            QMessageBox.information(self, "提示", "该对话内容为空，请选择其他场景")
            return

        self._current_dialog_id = dialog_id
        self._current_dialog = dialog
        self._lines = dialog['lines']

        role_index = self.role_combo.currentIndex()
        if role_index >= 0:
            self._current_role = self.role_combo.itemData(role_index)
        else:
            self._current_role = "You"

        # 确定对方角色
        other_speakers = set()
        for line in self._lines:
            sp = line.get('speaker', '')
            if sp != self._current_role:
                other_speakers.add(sp)
        self._other_role = other_speakers.pop() if len(other_speakers) == 1 else "Other"

        # 重置状态
        self._line_index = 0
        self._total_score = 0.0
        self._total_turns = 0
        self._is_waiting_user = False
        self._has_answered = False
        self._current_answer_spec = None

        # 更新标题
        self.title_label.setText(
            f"角色扮演: {dialog['title']} - 扮演 {self._current_role}")
        self.score_label.setText("得分: --")

        # 清空聊天区
        self._clear_chat()

        # 禁用选择
        self.dialog_combo.setEnabled(False)
        self.role_combo.setEnabled(False)
        self.start_btn.setEnabled(False)

        # 开始逐句播放
        self._advance_line()

    def _advance_line(self):
        """推进到下一行对话。"""
        if self._line_index >= len(self._lines):
            self._show_complete()
            return

        line = self._lines[self._line_index]
        speaker = line.get('speaker', '')
        text = line.get('text', '')
        translation = line.get('translation', '')

        if speaker == self._current_role:
            # --- 用户的回合 ---
            self._is_waiting_user = True
            self._has_answered = False
            self._current_answer_spec = _build_answer_spec(text)

            # 添加提示气泡
            prompt = _PromptBubble(
                speaker=speaker,
                prompt_text=text,
                translation=translation,
            )
            self._insert_chat_widget(prompt)

            # 启用输入
            self._set_input_enabled(True)
            self.input_field.setFocus()
            self.input_hint.setText("请用英语回答（可打字或语音输入）")
            self.input_field.setText("")

        else:
            # --- 对方的回合 ---
            self._is_waiting_user = False
            self._set_input_enabled(False)

            # 添加对方气泡
            bubble = _ChatBubble(
                speaker=speaker,
                text=text,
                translation=translation,
                is_user=False,
            )

            # TTS 播放按钮行
            tts_row = QHBoxLayout()
            tts_row.setAlignment(Qt.AlignLeft)
            tts_row.setSpacing(8)

            play_btn = QPushButton(" 播放发音")
            play_btn.setFlat(True)
            play_btn.setCursor(Qt.PointingHandCursor)
            play_btn.setStyleSheet("""
                QPushButton {
                    color: #4a90d9;
                    font-size: 13px;
                    padding: 4px 10px;
                    border: 1px solid #4a90d9;
                    border-radius: 6px;
                    background: transparent;
                }
                QPushButton:hover {
                    background-color: #4a90d9;
                    color: white;
                }
                QPushButton:disabled {
                    color: #bdc3c7;
                    border-color: #bdc3c7;
                }
            """)
            play_btn.clicked.connect(
                lambda checked, t=text, b=play_btn: self._play_tts(t, b))

            tts_row.addWidget(play_btn)
            tts_row.addStretch()

            wrapper = QWidget()
            wrapper_layout = QVBoxLayout(wrapper)
            wrapper_layout.setSpacing(4)
            wrapper_layout.setContentsMargins(0, 0, 0, 0)
            wrapper_layout.setAlignment(Qt.AlignLeft)
            wrapper_layout.addWidget(bubble)
            wrapper_layout.addLayout(tts_row)

            self._insert_chat_widget(wrapper)

            # 自动播放 TTS
            self._play_tts(text, play_btn)

            # 延迟后自动前进到下一行
            self._auto_advance_timer = QTimer(self)
            self._auto_advance_timer.setSingleShot(True)
            self._auto_advance_timer.timeout.connect(self._auto_advance)
            self._auto_advance_timer.start(3000)

    def _auto_advance(self):
        """对方台词播放后自动前进。"""
        self._line_index += 1
        self._advance_line()

    def _play_tts(self, text: str, button: QPushButton):
        """播放 TTS 语音。"""
        if not self.tts.available:
            return
        button.setEnabled(False)
        button.setText(" 播放中...")

        def on_done():
            button.setEnabled(True)
            button.setText(" 播放发音")

        self.tts.speak(text, callback=on_done)

    def _submit_answer(self):
        """提交用户回答。"""
        if not self._is_waiting_user or self._has_answered:
            return

        user_input = self.input_field.text().strip()
        if not user_input:
            QMessageBox.information(self, "提示", "请输入你的回答")
            return

        self._has_answered = True
        self._set_input_enabled(False)

        # 停止录音（如果正在录音）
        if self.asr.is_listening:
            self.asr.stop()
            self._recording_indicator.stop()

        # 匹配答案
        result = self.matcher.match(user_input, self._current_answer_spec)

        # 更新分数
        self._total_turns += 1
        self._total_score += result.score
        avg = self._total_score / self._total_turns if self._total_turns > 0 else 0
        self.score_label.setText(f"得分: {int(avg * 100)}%")

        # 显示用户回答气泡
        user_bubble = _ChatBubble(
            speaker=self._current_role,
            text=user_input,
            translation="",
            is_user=True,
        )
        self._insert_chat_widget(user_bubble)

        # 显示结果气泡
        result_bubble = _ResultBubble(result, user_input)
        self._insert_chat_widget(result_bubble)

        # 记录到数据库
        line_text = self._current_answer_spec.primary_answer
        self.database.add_study_record(
            line_text[:50],
            "roleplay",
            "correct" if result.is_correct else "wrong"
        )

        # 延迟后自动前进
        self._auto_advance_timer = QTimer(self)
        self._auto_advance_timer.setSingleShot(True)
        self._auto_advance_timer.timeout.connect(self._after_user_answer)
        self._auto_advance_timer.start(2500)

    def _after_user_answer(self):
        """用户回答后前进到下一行。"""
        self._line_index += 1
        self._advance_line()

    def _toggle_voice(self):
        """切换语音输入。"""
        if not self.asr.available:
            QMessageBox.information(
                self, "提示",
                f"语音识别不可用 ({self.asr.get_status()})\n"
                "请使用打字输入，或安装 Vosk 语音识别引擎。")
            return

        if self.asr.is_listening:
            # 停止录音
            self.asr.stop()
            self._recording_indicator.stop()
            self.voice_btn.setText(" 语音输入")
            self.voice_btn.setStyleSheet("""
                QPushButton {
                    padding: 12px 20px;
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #c0392b; }
            """)
        else:
            # 开始录音
            self._recording_indicator.start()
            self.voice_btn.setText(" 停止录音")
            self.voice_btn.setStyleSheet("""
                QPushButton {
                    padding: 12px 20px;
                    background-color: #c0392b;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #a93226; }
            """)
            self.input_hint.setText("正在录音，请说话...")

            def on_asr_result(text, confidence, error=None):
                """ASR 回调（在主线程外调用，需要用 QTimer 安全更新 UI）。"""
                QTimer.singleShot(0, lambda: self._on_asr_done(text, error))

            self.asr.listen(callback=on_asr_result, duration=10)

    def _on_asr_done(self, text: str, error=None):
        """ASR 识别完成。"""
        self._recording_indicator.stop()
        self.voice_btn.setText(" 语音输入")
        self.voice_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 20px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)

        if error:
            self.input_hint.setText(f"语音识别错误: {error}")
            return

        if text:
            self.input_field.setText(text)
            self.input_hint.setText("语音识别完成，可编辑后提交")
        else:
            self.input_hint.setText("未识别到内容，请重试或手动输入")

    def _show_complete(self):
        """对话练习完成。"""
        self._set_input_enabled(False)
        self.input_hint.setText("练习完成！")

        # 完成面板
        complete = QFrame()
        complete.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #27ae60;
                border-radius: 12px;
                padding: 24px;
            }
        """)
        complete_layout = QVBoxLayout(complete)
        complete_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("练习完成！")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #27ae60;")
        title.setAlignment(Qt.AlignCenter)
        complete_layout.addWidget(title)

        if self._total_turns > 0:
            avg = self._total_score / self._total_turns
            pct = int(avg * 100)
            stats_text = QLabel(
                f"总回合: {self._total_turns} | 平均得分: {pct}%")
            stats_text.setStyleSheet(
                "font-size: 16px; color: #2c3e50; margin: 12px 0;")
            stats_text.setAlignment(Qt.AlignCenter)
            complete_layout.addWidget(stats_text)

            # 更新每日统计
            correct = sum(
                1 for _ in range(self._total_turns)
                if True  # 简化：用总分数近似
            )
            self.database.update_daily_stats(
                correct_count=int(avg * self._total_turns),
                total_count=self._total_turns
            )

        # 重新开始按钮
        restart_btn = QPushButton("重新选择场景")
        restart_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 40px;
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 12px;
            }
            QPushButton:hover { background-color: #357abd; }
        """)
        restart_btn.clicked.connect(self._reset_practice)
        complete_layout.addWidget(restart_btn, alignment=Qt.AlignCenter)

        self._insert_chat_widget(complete)

        # 重新启用选择
        self.dialog_combo.setEnabled(True)
        self.role_combo.setEnabled(True)
        self.start_btn.setEnabled(True)

    def _reset_practice(self):
        """重置练习状态。"""
        self._current_dialog = None
        self._current_dialog_id = None
        self._line_index = 0
        self._is_waiting_user = False
        self._has_answered = False
        self._current_answer_spec = None
        self._total_score = 0.0
        self._total_turns = 0

        self.title_label.setText("角色扮演练习")
        self.score_label.setText("得分: --")
        self.input_hint.setText("选择场景和角色后点击「开始练习」")
        self._set_input_enabled(False)
        self._clear_chat()

        self.dialog_combo.setEnabled(True)
        self.role_combo.setEnabled(True)
        self.start_btn.setEnabled(True)

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------
    def _clear_chat(self):
        """清空聊天区域。"""
        while self.chat_layout.count() > 0:
            item = self.chat_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                # 清理子布局
                sub = item.layout()
                while sub.count() > 0:
                    sub_item = sub.takeAt(0)
                    sw = sub_item.widget()
                    if sw:
                        sw.deleteLater()
        self.chat_layout.addStretch()

    def _insert_chat_widget(self, widget):
        """在 stretch 之前插入聊天组件。"""
        count = self.chat_layout.count()
        # 找到 stretch 的位置（最后一个 item）
        self.chat_layout.insertWidget(count - 1, widget)
        # 滚动到底部
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        """滚动聊天区域到底部。"""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _set_input_enabled(self, enabled: bool):
        """启用或禁用输入区域。"""
        self.input_field.setEnabled(enabled)
        self.submit_btn.setEnabled(enabled)
        self.voice_btn.setEnabled(enabled)
