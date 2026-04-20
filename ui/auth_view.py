from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QGraphicsOpacityEffect, QLabel, QPushButton, QHBoxLayout
from ui.login_view import LoginView
from ui.register_view import RegisterView
from ui.main_app import MainApp
from PySide6.QtCore import QPropertyAnimation, Qt
from ui.loading_view import LoadingScreen

class AuthView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Client")
        self.setFixedSize(400, 450)
        self.setWindowFlags(self.windowFlags()| Qt.FramelessWindowHint)
        self._drag_pos = None

        # Top-bar creation
        top_bar = QWidget()
        top_bar.setFixedHeight(36)
        top_bar.setStyleSheet("background-color: #0b0f14;")

        title = QLabel("Game Client")
        title.setStyleSheet("font-weight: bold; padding-left: 10px;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)

        bar_layout = QHBoxLayout(top_bar)
        bar_layout.addWidget(title)
        bar_layout.addStretch()
        bar_layout.addWidget(close_btn)
        bar_layout.setContentsMargins(0, 0, 5, 0)

        self.stack = QStackedWidget()

        self.login_view = LoginView(self)
        self.register_view = RegisterView(self)

        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.register_view)

        main_layout = QVBoxLayout()
        main_layout.addWidget(top_bar)
        main_layout.addWidget(self.stack)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(main_layout)

        self.show_login()

    def show_login(self):
        self.fade_to(self.login_view)

    def show_register(self):
        self.fade_to(self.register_view)

    def open_main_app(self, username: str):
        self.loading = LoadingScreen(lambda: self.finish_login(username))
        self.loading.show()
        self.close()

    def finish_login(self, username: str):
        self.main = MainApp(username)
        self.main.show()

    # Fade method
    def fade_to(self, widget):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(250)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)

        self.stack.setCurrentWidget(widget)
        animation.start()

        # Keep reference so it doesn't get garbage-collected
        self._animation = animation

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._drag_pos:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None