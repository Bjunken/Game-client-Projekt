from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget
)
from PySide6.QtCore import Qt


class RequestRow(QWidget):
    """A single incoming friend request row with Accept / Decline buttons."""

    def __init__(self, username: str, manager, parent=None):
        super().__init__(parent)

        self.username = username
        self.manager = manager

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)

        name_label = QLabel(username)
        name_label.setStyleSheet("color: white; font-weight: bold;")

        accept_btn = QPushButton("Accept")
        accept_btn.setFixedWidth(70)
        accept_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d6a2d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover { background-color: #3a8a3a; }
        """)
        accept_btn.clicked.connect(self._on_accept)

        decline_btn = QPushButton("Decline")
        decline_btn.setFixedWidth(70)
        decline_btn.setStyleSheet("""
            QPushButton {
                background-color: #6a2d2d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover { background-color: #8a3a3a; }
        """)
        decline_btn.clicked.connect(self._on_decline)

        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(accept_btn)
        layout.addWidget(decline_btn)

    def _on_accept(self):
        self.manager.accept_request(self.username)

    def _on_decline(self):
        self.manager.decline_request(self.username)


class RequestsPanel(QDialog):
    """
    Dialog showing all incoming friend requests.
    Rebuilds automatically when requests_updated fires.
    """

    def __init__(self, manager, parent=None):
        super().__init__(parent)

        self.manager = manager

        self.setWindowTitle("Friend Requests")
        self.setFixedSize(320, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        self._setup_ui()

        # Rebuild whenever requests change
        self.manager.requests_updated.connect(self._rebuild)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header row
        header_layout = QHBoxLayout()

        title = QLabel("Friend Requests")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #d4af37;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #e6e6e6;
                font-size: 14px;
            }
            QPushButton:hover { color: #e05c5c; }
        """)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)

        # Scrollable request list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.scroll_content = QWidget()
        self.requests_layout = QVBoxLayout(self.scroll_content)
        self.requests_layout.setSpacing(4)
        self.requests_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        # Empty state label
        self.empty_label = QLabel("No pending requests.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self.empty_label)

        self._rebuild()

    def _rebuild(self):
        """Clear and repopulate the request list."""

        # Remove all rows (but not the stretch at the end)
        while self.requests_layout.count() > 1:
            item = self.requests_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        has_requests = bool(self.manager.requests)
        self.scroll_area.setVisible(has_requests)
        self.empty_label.setVisible(not has_requests)

        for username in self.manager.requests:
            row = RequestRow(username, self.manager)
            # Insert before the stretch
            self.requests_layout.insertWidget(
                self.requests_layout.count() - 1, row
            )

        # Auto-close if all requests have been handled
        if not has_requests and self.isVisible():
            pass  # keep open so user can see the empty state