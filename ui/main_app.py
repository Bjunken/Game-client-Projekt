from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel
)
from PySide6.QtCore import Qt
from ui.widgets.slideshow_widget import SlideShowWidget
from ui.widgets.friend_system_widget import FriendSystemWidget
from core.friend_manager import FriendManager

class MainApp(QWidget):

    def __init__(self, username: str):
        super().__init__()

        self.username = username

        self.setWindowTitle("Game Client")
        self.resize(1200, 700)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self._drag_pos = None

        # Initialise the friend manager scoped to the logged-in user
        self.friend_manager = FriendManager(username)

        self.setup_ui()

    def setup_ui(self):
        # Huvudlayouten (vertical)
        self.main_layout = QVBoxLayout(self)
        window_bar = self.create_window_bar()
        # Top bar
        top_bar = self.create_top_bar()

        # Body
        body = self.create_body()

        self.main_layout.addWidget(window_bar)
        self.main_layout.addWidget(top_bar)
        self.main_layout.addLayout(body)

    # Create topbar
    def create_top_bar(self):

        top_bar = QWidget()
        top_bar.setFixedHeight(60)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        # Navigation
        nav = self.create_navigation()

        # Party slots
        party = self.create_party_slots()

        # Player info
        player = self.create_player_info()

        # Quit button
        quit_btn = QPushButton("QUIT GAME")

        layout.addWidget(nav, 3)
        layout.addWidget(party, 2)
        layout.addStretch(3)
        layout.addWidget(player, 1)
        layout.addWidget(quit_btn, 1)

        return top_bar
    
    def create_window_bar(self):

        bar = QWidget()
        bar.setFixedHeight(36)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 0, 10, 0)

        title = QLabel("Game Client")

        minimize = QPushButton("_")
        minimize.setFixedSize(30, 30)
        minimize.clicked.connect(self.showMinimized)

        close = QPushButton("X")
        close.setFixedSize(30, 30)
        close.clicked.connect(self.close)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(minimize)
        layout.addWidget(close)

        return bar
    
    # Skapar navigation knapparna
    def create_navigation(self):

        nav_widget = QWidget()
        layout = QHBoxLayout(nav_widget)
        layout.setSpacing(8)

        play = QPushButton("PLAY")
        battlepass = QPushButton("BATTLEPASS")
        social = QPushButton("SOCIAL")
        settings = QPushButton("SETTINGS")

        layout.addWidget(play)
        layout.addWidget(battlepass)
        layout.addWidget(social)
        layout.addWidget(settings)

        play.setFixedHeight(30)
        battlepass.setFixedHeight(30)
        social.setFixedHeight(30)
        settings.setFixedHeight(30)

        return nav_widget

    # Skapar party slots
    def create_party_slots(self):
        party_widget = QWidget()
        layout = QHBoxLayout(party_widget)

        for i in range(5):

            if i == 0:
                slot = QPushButton("●")
            else:
                slot = QPushButton("+")

            slot.setFixedSize(30, 30)

            layout.addWidget(slot)

        return party_widget

    # Skapar player info
    def create_player_info(self):
        player_widget = QWidget()
        layout = QHBoxLayout(player_widget)

        self.username_label = QLabel(self.username)
        self.username_label.setStyleSheet("color: #d4af37; font-weight: bold;")

        layout.addWidget(self.username_label)

        return player_widget
    
    # Skapar mitten layouten
    def create_body(self):
        body_layout = QHBoxLayout()

        # example: to follow each image's ratio without cropping, set
        # dynamic_ratio=True and leave expand_and_center False
        slideshow = SlideShowWidget(dynamic_ratio=True)
        friends = self.create_friends_panel()

        body_layout.addWidget(slideshow, 3)
        body_layout.addWidget(friends, 1)

        return body_layout
    
    # Slideshow
    
    # Skapar friend panel
    def create_friends_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Player profile section
        profile_section = QWidget()
        profile_section.setFixedHeight(70)
        profile_layout = QHBoxLayout(profile_section)
        profile_layout.setContentsMargins(10, 8, 10, 8)

        profile_circle = QPushButton("●")
        profile_circle.setFixedSize(40, 40)

        username_label = QLabel(self.username)
        username_label.setStyleSheet("font-weight: bold; color: #d4af37;")

        profile_layout.addWidget(profile_circle)
        profile_layout.addWidget(username_label)
        profile_layout.addStretch()

        # The real friend system widget
        self.friend_system = FriendSystemWidget(self.friend_manager)

        layout.addWidget(profile_section)
        layout.addWidget(self.friend_system)

        return panel
    
    # Drag-able fönster
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