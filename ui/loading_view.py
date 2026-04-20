from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer


class LoadingScreen(QWidget):
    def __init__(self, on_finished):
        super().__init__()
        self.on_finished = on_finished

        self.setWindowTitle("Loading")
        self.setFixedSize(400, 250)
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Connecting to server...")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #d4af37;
            font-size: 16px;
            font-weight: bold;
        """)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFixedWidth(260)
        self.progress.setTextVisible(False)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.progress)

        # Timer for fake loading
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance)
        self.timer.start(30)

    def advance(self):
        value = self.progress.value() + 1
        self.progress.setValue(value)

        if value >= 100:
            self.timer.stop()
            self.close()
            self.on_finished()