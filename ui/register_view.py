import re
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton
)

from core.user_repository import user_exists, create_user
from core.session_manager import login
from utils.hash_utils import hash_password

# Validation methods for username / password / email

def is_valid_username(username: str) -> bool:
    # 3–16 letters, no numbers or symbols
    return bool(re.fullmatch(r"[A-Za-z]{3,16}", username))

def is_valid_password(password: str) -> bool:
    if len(password) < 6:
        return False
    has_letter = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)
    return has_letter and has_digit

def is_valid_email(email: str) -> bool:
    return bool(
        re.fullmatch(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            email
        )
    )

class RegisterView(QWidget):
    def __init__(self, auth_view):
        super().__init__()
        self.auth = auth_view

        self.setWindowTitle("Register")
        self.setFixedSize(400, 400)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Error label
        self.error_label = QLabel("")
        self.error_label.setVisible(False)
        self.error_label.setStyleSheet("color: red; font-size: 11px;")
        layout.addWidget(self.error_label)

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

        # Password strength-indicator
        self.strength_layout = QHBoxLayout()

        self.strength_bar_1 = QLabel()
        self.strength_bar_2 = QLabel()
        self.strength_bar_3 = QLabel()

        for bar in (self.strength_bar_1, self.strength_bar_2, self.strength_bar_3):
            bar.setFixedSize(30, 6)
            bar.setStyleSheet("background-color: #333; border-radius: 3px;")

        self.strength_layout.addWidget(self.strength_bar_1)
        self.strength_layout.addWidget(self.strength_bar_2)
        self.strength_layout.addWidget(self.strength_bar_3)

        layout.addLayout(self.strength_layout)

        # Listen for password changes
        self.password_input.textChanged.connect(self.update_password_strength)

        # Confirm password
        confirm_password_label = QLabel("Password")
        confirm_password_label.setProperty("role", "title")

        layout.addWidget(confirm_password_label)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input)

        # Email
        email_label = QLabel("Email")
        email_label.setProperty("role", "title")

        layout.addWidget(email_label)
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)

        # Buttons
        button_layout = QHBoxLayout()

        self.create_button = QPushButton("Create account")
        self.create_button.clicked.connect(self.register_on_clicked)
        self.create_button.setEnabled(False)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.on_back_clicked)

        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.back_button)

        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

    # on clicked methods and password-strength indicator
    def register_on_clicked(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        email = self.email_input.text().strip()

        self.error_label.setVisible(False)

        # Username validation
        if not is_valid_username(username):
            self.show_error(
                "Username must be 3–16 letters.\nNo numbers or special characters."
            )
            return

        # Password validation
        if not is_valid_password(password):
            self.show_error(
                "Password must be at least 6 characters\nand contain at least one number."
            )
            return

        if password != confirm_password:
            self.show_error("Passwords do not match.")
            return

        # Email validation
        if not is_valid_email(email):
            self.show_error("Please enter a valid email address.")
            return

        # Existing user
        if user_exists(username):
            self.show_error("Username already exists.")
            return

        # Create user
        password_hash = hash_password(password)
        create_user(username, password_hash, email)

        # Auto-login
        success, message = login(username, password, remember=True)

        if success:
            self.auth.open_main_app(username)
        else:
            self.show_error(message)

    def on_back_clicked(self):
        # Clear all inputs
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.email_input.clear()

        # Reset error state
        self.error_label.clear()
        self.error_label.setVisible(False)

        # Reset password strength bars (optional but recommended)
        for bar in [self.strength_bar_1, self.strength_bar_2, self.strength_bar_3]:
            bar.setStyleSheet("background-color: #333; border-radius: 3px;")

        # Disable create button again
        self.create_button.setEnabled(False)

        # Go back to login
        self.auth.show_login()

    def show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def update_password_strength(self, password: str):
        strength = 0

        if len(password) >= 6:
            strength += 1
        if any(c.isdigit() for c in password):
            strength += 1
        if any(c.isalpha() for c in password):
            strength += 1

        # Reset all bars
        bars = [self.strength_bar_1, self.strength_bar_2, self.strength_bar_3]
        for bar in bars:
            bar.setStyleSheet("background-color: #333; border-radius: 3px;")

        if strength >= 1:
            self.strength_bar_1.setStyleSheet(
                "background-color: #d9534f; border-radius: 3px;"
            )
        if strength >= 2:
            self.strength_bar_2.setStyleSheet(
                "background-color: #f0ad4e; border-radius: 3px;"
            )
        if strength >= 3:
            self.strength_bar_3.setStyleSheet(
                "background-color: #5cb85c; border-radius: 3px;"
            )
        self.create_button.setEnabled(strength >= 2)