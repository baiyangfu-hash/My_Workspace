# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)


_TITLEBAR_HEIGHT = 32


class TitleBar(QWidget):

    minimize_requested = pyqtSignal()
    maximize_requested = pyqtSignal()
    close_requested = pyqtSignal()

    def __init__(self, app_title: str = "", parent=None):
        super().__init__(parent)
        self._is_maximized = False
        self._drag_pos = None

        self.setObjectName("TitleBar")
        self.setFixedHeight(_TITLEBAR_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.ArrowCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 0, 0)
        layout.setSpacing(0)

        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(8)

        icon_label = QLabel("\u26A1")
        icon_label.setObjectName("TitleBarIcon")
        icon_label.setFixedSize(16, 16)
        icon_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(icon_label)

        title_font = QFont("Microsoft YaHei UI", 9)
        title_font.setWeight(QFont.DemiBold)

        self._title_label = QLabel(app_title)
        self._title_label.setObjectName("TitleBarTitle")
        self._title_label.setFont(title_font)
        logo_layout.addWidget(self._title_label)

        layout.addLayout(logo_layout)
        layout.addStretch()

        self._btn_min = self._create_window_btn("\u2500", "minimize")
        self._btn_max = self._create_window_btn("\u25A1", "maximize")
        self._btn_close = self._create_window_btn("\u2715", "close")

        layout.addWidget(self._btn_min)
        layout.addWidget(self._btn_max)
        layout.addWidget(self._btn_close)

    def _create_window_btn(self, text: str, role: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName(f"TitleBarBtn_{role}")
        btn.setFixedSize(46, _TITLEBAR_HEIGHT)
        btn.setCursor(Qt.ArrowCursor)
        btn.setProperty("TitleBarBtn", True)
        if role == "close":
            btn.setProperty("CloseBtn", True)
        btn.clicked.connect(lambda: self._on_btn_clicked(role))
        return btn

    def _on_btn_clicked(self, role: str):
        if role == "minimize":
            self.minimize_requested.emit()
        elif role == "maximize":
            self.maximize_requested.emit()
        elif role == "close":
            self.close_requested.emit()

    def set_title(self, title: str):
        self._title_label.setText(title)

    def set_maximized_state(self, maximized: bool):
        self._is_maximized = maximized
        self._btn_max.setText("\u29C9" if maximized else "\u25A1")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.LeftButton:
            if self._is_maximized:
                self.maximize_requested.emit()
                screen = self.window().screen()
                if screen:
                    screen_geo = screen.availableGeometry()
                    ratio = event.pos().x() / self.width()
                    new_width = self.window().normalGeometry().width()
                    new_x = event.globalPos().x() - int(new_width * ratio)
                    new_y = event.globalPos().y() - self._drag_pos.y()
                    new_x = max(screen_geo.left(), min(new_x, screen_geo.right() - new_width))
                    self._drag_pos = event.globalPos() - self.window().pos()
            self.window().move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.maximize_requested.emit()
            event.accept()
