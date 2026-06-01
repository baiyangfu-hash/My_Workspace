from PyQt5.QtWidgets import QTabWidget, QWidget
from PyQt5.QtCore import pyqtSignal

DASHBOARD_TAB_ID = "dashboard"
DASHBOARD_TAB_TITLE = "\U0001F4CA \u4eea\u8868\u76d8"


class TabSystem(QTabWidget):
    tab_changed = pyqtSignal(str, str)
    tab_closed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs = {}
        self._current_tab_id = DASHBOARD_TAB_ID

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)

        self.currentChanged.connect(self._on_current_changed)
        self.tabCloseRequested.connect(self._on_tab_close_requested)

        self._init_dashboard()

    def _init_dashboard(self):
        dashboard_widget = QWidget()
        self.addTab(dashboard_widget, DASHBOARD_TAB_TITLE)
        self._tabs[DASHBOARD_TAB_ID] = {
            "widget": dashboard_widget,
            "title": DASHBOARD_TAB_TITLE,
            "icon": "",
        }

    def _on_current_changed(self, index):
        new_tab_id = self._tab_id_at(index)
        if new_tab_id is None:
            return
        old_tab_id = self._current_tab_id
        self._current_tab_id = new_tab_id
        self.tab_changed.emit(new_tab_id, old_tab_id)

    def _on_tab_close_requested(self, index):
        tab_id = self._tab_id_at(index)
        if tab_id is None or tab_id == DASHBOARD_TAB_ID:
            return
        self.close_tab(tab_id)

    def _tab_id_at(self, index):
        if index < 0 or index >= self.count():
            return None
        tab_widget = self.widget(index)
        for tid, info in self._tabs.items():
            if info["widget"] is tab_widget:
                return tid
        return None

    def _index_of(self, tab_id):
        info = self._tabs.get(tab_id)
        if info is None:
            return -1
        return self.indexOf(info["widget"])

    def _build_title(self, icon, title):
        if icon:
            return f"{icon} {title}"
        return title

    def open_tab(self, tab_id, title, icon, widget):
        if tab_id in self._tabs:
            self.switch_to_tab(tab_id)
            return

        display_title = self._build_title(icon, title)
        index = self.addTab(widget, display_title)
        self._tabs[tab_id] = {
            "widget": widget,
            "title": title,
            "icon": icon,
        }
        self.setCurrentIndex(index)

    def close_tab(self, tab_id):
        if tab_id == DASHBOARD_TAB_ID:
            return
        info = self._tabs.pop(tab_id, None)
        if info is None:
            return
        index = self.indexOf(info["widget"])
        if index >= 0:
            self.removeTab(index)
        info["widget"].deleteLater()
        self.tab_closed.emit(tab_id)

    def switch_to_tab(self, tab_id):
        index = self._index_of(tab_id)
        if index >= 0:
            self.setCurrentIndex(index)

    def get_current_tab_id(self):
        return self._current_tab_id

    def get_widget(self, tab_id):
        info = self._tabs.get(tab_id)
        if info is None:
            return None
        return info["widget"]

    def tab_exists(self, tab_id):
        return tab_id in self._tabs