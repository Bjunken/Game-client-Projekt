from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QGraphicsOpacityEffect,
    QApplication
)
from PySide6.QtCore import QPropertyAnimation, Qt, QEvent
from core.session_manager import login


class LoginView(QWidget):
    def __init__(self, auth_view):
        super().__init__()
        self.auth = auth_view

        self.setWindowTitle("Login View")
        self.setFixedSize(400, 400)

        self.setup_ui()

        # AFTER widgets exist
        self.password_input.installEventFilter(self)
        self.password_input.returnPressed.connect(self.login_button.click)
        self.username_input.returnPressed.connect(self.login_button.click)

    # UI Setup

    def setup_ui(self):
        layout = QVBoxLayout()

        # Error label
        self.wrong_login = QLabel("")
        self.wrong_login.setStyleSheet("color: red; font-size: 11px;")
        layout.addWidget(self.wrong_login)

        # Graphics effect
        self.wrong_login = QLabel("")
        self.wrong_login.setStyleSheet("color: red; font-size: 11px;")
        self.wrong_login.setVisible(False)  # Start hidden
        layout.addWidget(self.wrong_login)

        # Hide via opacity ONLY (inte setVisible)
        self.wrong_login.show()

        # Username
        username_label = QLabel("Username")
        username_label.setProperty("role", "title")
        layout.addWidget(username_label)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Password")
        password_label.setProperty("role", "title")
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # Caps lock warning
        self.caps_warning = QLabel("Caps Lock is ON")
        self.caps_warning.setStyleSheet("color: orange; font-size: 11px;")
        self.caps_warning.setVisible(False)
        layout.addWidget(self.caps_warning)

        # Remember me
        self.remember_me = QCheckBox("Remember Me")
        layout.addWidget(self.remember_me)

        # Buttons
        button_layout = QHBoxLayout()

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.on_login_clicked)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.on_register_clicked)

        self.cancel_button = QPushButton("Quit")
        self.cancel_button.clicked.connect(self.auth.close)

        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

    # On clicked methods

    def on_register_clicked(self):
        self.wrong_login.setVisible(False)
        self.auth.show_register()

    def on_login_clicked(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        remember = self.remember_me.isChecked()

        if not username or not password:
            self.show_error("Enter both username and password.")
            return

        success, message = login(username, password, remember)

        if success:
            self.wrong_login.setVisible(False)
            self.auth.open_main_app(username)
        else:
            self.show_error(message)
            self.password_input.clear()
            self.password_input.setFocus()

    # Helper Methods
    def show_error(self, message):
        self.wrong_login.setText(message)
        self.wrong_login.setVisible(True)
    # Capslock check
    def eventFilter(self, obj, event):
        if obj == self.password_input and event.type() == QEvent.KeyPress:
            text = event.text()

            if text.isalpha():
                shift_pressed = bool(event.modifiers() & Qt.ShiftModifier)
                caps_on = text.isupper() and not shift_pressed
                self.caps_warning.setVisible(caps_on)  # Uncomment this!

        return super().eventFilter(obj, event)

