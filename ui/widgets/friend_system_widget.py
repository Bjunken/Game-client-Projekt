from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLineEdit,
    QApplication,
    QMenu
)
from PySide6.QtGui import QColor, QPainter, QAction
from PySide6.QtCore import Qt

from core.friend_manager import FriendManager
from core.friend import Friend

from ui.widgets.add_friend_dialog import AddFriendDialog
from ui.widgets.requests_panel import RequestsPanel

# ---------------------------------------------------------------------------
# StatusDot — small coloured circle indicating online / ingame / offline
# ---------------------------------------------------------------------------

class StatusDot(QWidget):
    def __init__(self, color):
        super().__init__()
        self.color = color
        self.setFixedSize(10, 10)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 10, 10)


# ---------------------------------------------------------------------------
# FriendItemWidget — one row in the friend list
# ---------------------------------------------------------------------------

class FriendItemWidget(QWidget):
    def __init__(self, friend: Friend, manager: FriendManager):
        super().__init__()

        self.friend = friend
        self.manager = manager  # needed for remove action

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Status dot colour
        dot_color = "#44ff44" if friend.is_online else "#333333"
        self.dot = StatusDot(dot_color)

        # Name + sub-status
        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)

        self.name_label = QLabel(friend.username)
        self.name_label.setStyleSheet("font-weight: bold; color: white;")

        self.status_label = QLabel("Ingame" if friend.is_ingame else "")
        self.status_label.setStyleSheet("font-size: 10px; color: gray;")

        text_layout.addWidget(self.name_label)
        text_layout.addWidget(self.status_label)

        layout.addWidget(self.dot)
        layout.addLayout(text_layout)
        layout.addStretch()

        self.setLayout(layout)

        # Enable right-click
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, position):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1f27;
                border: 1px solid #3a3f4a;
                border-radius: 6px;
                padding: 4px;
                color: #e6e6e6;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #242a34;
                color: #d4af37;
            }
            QMenu::item:disabled {
                color: #555;
            }
            QMenu::separator {
                height: 1px;
                background: #3a3f4a;
                margin: 4px 8px;
            }
        """)

        # --- View Profile (always available) ---
        view_action = QAction("View Profile", self)
        view_action.triggered.connect(self._on_view_profile)
        menu.addAction(view_action)

        menu.addSeparator()

        # --- Invite to Party (online only, not if already ingame) ---
        invite_action = QAction("Invite to Party", self)
        invite_action.triggered.connect(self._on_invite_to_party)
        if not self.friend.is_online or self.friend.is_ingame:
            invite_action.setEnabled(False)
        menu.addAction(invite_action)

        # --- Spectate (ingame only) ---
        spectate_action = QAction("Spectate", self)
        spectate_action.triggered.connect(self._on_spectate)
        if not self.friend.is_ingame:
            spectate_action.setEnabled(False)
        menu.addAction(spectate_action)

        menu.addSeparator()

        # --- Remove Friend (always available) ---
        remove_action = QAction("Remove Friend", self)
        remove_action.setStyleSheet("color: #e05c5c;")
        remove_action.triggered.connect(self._on_remove_friend)
        menu.addAction(remove_action)

        # Show menu at cursor position
        menu.exec(self.mapToGlobal(position))

    # --- Action handlers (stubs for now, expanded in later steps) ---

    def _on_view_profile(self):
        print(f"[Profile] Viewing profile of {self.friend.username}")

    def _on_invite_to_party(self):
        print(f"[Party] Inviting {self.friend.username} to party")

    def _on_spectate(self):
        print(f"[Spectate] Spectating {self.friend.username}")

    def _on_remove_friend(self):
        self.manager.remove_friend(self.friend.username)

# ---------------------------------------------------------------------------
# FriendSection — collapsible Online / Offline section
# ---------------------------------------------------------------------------

class FriendSection(QWidget):
    def __init__(self, title: str):
        super().__init__()

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(4)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.header = QPushButton(title)
        self.header.setCheckable(True)
        self.header.setChecked(True)
        self.header.clicked.connect(self._toggle)
        self.header.setStyleSheet("""
            QPushButton {
                text-align: left;
                font-weight: bold;
                color: white;
                background: transparent;
                border: none;
                padding: 6px;
            }
            QPushButton:hover { color: #00c8ff; }
        """)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(2)
        self.container_layout.setContentsMargins(0, 0, 0, 0)

        self._layout.addWidget(self.header)
        self._layout.addWidget(self.container)

    def add_friend(self, widget: FriendItemWidget):
        self.container_layout.addWidget(widget)

    def clear(self):
        """Remove all friend widgets from this section."""
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def set_count(self, count: int):
        """Update the header to show how many friends are in this section."""
        base = self.header.text().split("(")[0].strip()
        self.header.setText(f"{base}  ({count})")

    def _toggle(self):
        visible = self.header.isChecked()
        self.container.setVisible(visible)
        self.container.setMaximumHeight(
            self.container.sizeHint().height() if visible else 0
        )


# ---------------------------------------------------------------------------
# FriendSystemWidget — the full friend panel wired to FriendManager
# ---------------------------------------------------------------------------

class FriendSystemWidget(QWidget):
    def __init__(self, manager: FriendManager):
        super().__init__()

        self.manager = manager

        # Connect signals → rebuild the list whenever data changes
        self.manager.friends_updated.connect(self.rebuild)
        self.manager.requests_updated.connect(self.rebuild)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Search bar
        # Header — Add Friend + Requests buttons
        header_layout = QHBoxLayout()

        title_label = QLabel("FRIENDS")
        title_label.setStyleSheet("font-weight: bold; color: #d4af37; font-size: 13px;")

        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(26, 26)
        self.add_btn.setToolTip("Add Friend")
        self.add_btn.clicked.connect(self._open_add_friend)

        self.requests_btn = QPushButton("Requests")
        self.requests_btn.setFixedHeight(26)
        self.requests_btn.setMinimumWidth(90)
        self.requests_btn.clicked.connect(self._open_requests)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)
        header_layout.addWidget(self.requests_btn)

        layout.addLayout(header_layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search friends...")
        self.search_bar.textChanged.connect(self._filter)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: #1e1e1e;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 6px;
                color: white;
            }
        """)
        layout.addWidget(self.search_bar)

        # Sections
        self.online_section = FriendSection("Online")
        self.offline_section = FriendSection("Offline")

        layout.addWidget(self.online_section)
        layout.addWidget(self.offline_section)
        layout.addStretch()

        # Initial render
        self.rebuild()

    def _open_add_friend(self):
        from core.user_repository import user_exists
        # wrap user_exists in a simple object the dialog can call
        class Repo:
            def user_exists(self, username):
                return user_exists(username)
        dialog = AddFriendDialog(self.manager, Repo(), parent=self)
        dialog.exec()

    def _open_requests(self):
        panel = RequestsPanel(self.manager, parent=self)
        panel.exec()

    def rebuild(self):
        """
        Called whenever friends_updated fires.
        Clears both sections and re-populates from manager.friends.
        """
        self.online_section.clear()
        self.offline_section.clear()

        online_count = 0
        offline_count = 0

        for friend in self.manager.friends:
            widget = FriendItemWidget(friend, self.manager)
            if friend.is_online:
                self.online_section.add_friend(widget)
                online_count += 1
            else:
                self.offline_section.add_friend(widget)
                offline_count += 1

        self.online_section.set_count(online_count)
        self.offline_section.set_count(offline_count)

        # Re-apply any active search filter
        self._filter(self.search_bar.text())

        # Update requests button to show pending count
        count = len(self.manager.requests)
        self.requests_btn.setText(f"Requests ({count})" if count else "Requests")

    def _filter(self, text: str):
        """Show only friends whose name contains the search text."""
        text = text.lower()

        for section in (self.online_section, self.offline_section):
            for i in range(section.container_layout.count()):
                item = section.container_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    name = widget.friend.username.lower()
                    widget.setVisible(text in name)