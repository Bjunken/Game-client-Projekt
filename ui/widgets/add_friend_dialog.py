from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton
)
from PySide6.QtCore import Qt


class AddFriendDialog(QDialog):
    """
    Small dialog that lets the user type a username and send a friend request.
    """

    def __init__(self, manager, user_repository, parent=None):
        super().__init__(parent)

        self.manager = manager
        self.user_repository = user_repository  # to validate the username exists

        self.setWindowTitle("Add Friend")
        self.setFixedSize(320, 170)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Add Friend")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #d4af37;")
        layout.addWidget(title)

        # Input
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter username...")
        self.input.textChanged.connect(self._on_text_changed)
        self.input.returnPressed.connect(self._on_send)
        layout.addWidget(self.input)

        # Error label — word wrap so long messages don't get clipped
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e05c5c; font-size: 11px;")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.send_button = QPushButton("Send Request")
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self._on_send)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.send_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _on_text_changed(self, text: str):
        # Only enable send button if there is actual input
        self.send_button.setEnabled(bool(text.strip()))
        self.error_label.setVisible(False)

    def _on_send(self):
        username = self.input.text().strip()

        if not username:
            return

        # Check not adding yourself
        if username == self.manager.username:
            self._show_error("You can't add yourself.")
            return

        # Check the user actually exists
        if not self.user_repository.user_exists(username):
            self._show_error("User not found.")
            return

        # Check not already a friend
        if self.manager.get_friend(username):
            self._show_error("Already in your friend list.")
            return

        # Check not a duplicate request
        if username in self.manager.requests:
            self._show_error("Request already sent.")
            return

        self.manager.add_request(username)
        self.accept()

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(True)