import sys
from PySide6.QtWidgets import QApplication
from ui.auth_view import AuthView
from core.session_store import load_session
from ui.main_app import MainApp
from core.session_store import clear_session

def logout(self):
    clear_session()
    self.auth = AuthView()
    self.auth.show()
    self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    session_user = load_session()

    app.setStyleSheet("""
    QWidget {
        background-color: #0e1116;
        color: #e6e6e6;
        font-family: Segoe UI;
        font-size: 13px;
    }

    QLineEdit {
        background-color: #151a21;
        border: 1px solid #2a2f3a;
        padding: 6px;
        border-radius: 6px;
    }

    QLineEdit:focus {
        border: 1px solid #4da3ff;
    }

    QPushButton {
        color: #d4af37;
        background-color: #1a1f27;
        border: 1px solid #3a3f4a;
        padding: 6px;
    }

    QPushButton:hover {
        background-color: #242a34;
    }

    QPushButton:disabled {
        background-color: #444;
        color: #888;
    }

    QLabel[role="title"] {
        color: #d4af37;
        font-size: 14px;
        font-weight: bold;
    }
    """)

    if session_user:
        window = MainApp(session_user)
    else:
        window = AuthView()
    
    window.show()
    sys.exit(app.exec())