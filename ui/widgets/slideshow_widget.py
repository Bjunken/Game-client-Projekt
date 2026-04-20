from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QProgressBar,
    QSizePolicy
)

from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QPixmap
from dataclasses import dataclass

@dataclass
class Slide:
    image: str
    title: str
    description: str
    button_text: str
    action: callable


class AspectRatioWidget(QWidget):
    """A container that keeps a width:height ratio via heightForWidth.

    The ratio can be changed on the fly (useful for adapting to an
    image's aspect) by calling ``set_ratio``; the widget will then
    re‑layout itself automatically.
    """

    def __init__(self, ratio=16/9, parent=None):
        super().__init__(parent)
        self._ratio = ratio
        # enable heightForWidth support
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def set_ratio(self, ratio: float):
        if ratio <= 0:
            return
        self._ratio = ratio
        self.updateGeometry()  # inform layouts that size hints have changed

    def heightForWidth(self, width: int) -> int:
        return int(width / self._ratio)

    def sizeHint(self):
        # don't request more than current size; base hint purely on ratio
        w = self.width() or super().sizeHint().width() or 160
        h = int(w / self._ratio)
        return QSize(w, h)

    def minimumSizeHint(self):
        # no enforced minimum to avoid forcing the parent to grow
        return QSize(0, 0)


class ClickableLabel(QLabel):

    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class SlideShowWidget(QWidget):

    def __init__(self, parent=None, *, expand_and_center: bool = False, dynamic_ratio: bool = False):
        super().__init__(parent)

        # behaviour flags
        self._expand_and_center = expand_and_center
        # when true, container aspect ratio follows the current image
        self._dynamic_ratio = dynamic_ratio

        self.current_index = 0
        self.progress_value = 0

        self.init_ui()
        self.create_slides()
        self.show_slide()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)


    def init_ui(self):

        main_layout = QVBoxLayout(self)

        # Container för bilden (maintains 16:9 aspect ratio)
        self.image_container = AspectRatioWidget(ratio=16/9)
        self.image_container.setMinimumHeight(200)
        # cap the maximum height so the overall window doesn't balloon
        self.image_container.setMaximumHeight(500)

        container_layout = QVBoxLayout(self.image_container)
        container_layout.setContentsMargins(0,0,0,0)

        # Själva bilden
        self.image_label = ClickableLabel()
        # size should be dictated by the container, not by the pixmap
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.clicked.connect(self.slide_clicked)

        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
        background:black;
        border:2px solid #FFD700;
        border-radius:8px;
        """)

        # Overlay box (svart ruta i hörnet)
        self.overlay = QWidget(self.image_container)

        self.overlay.setStyleSheet("""
        QWidget{
            background-color: rgba(0,0,0,180);
            border:2px solid #FFD700;
            border-radius:12px;
            padding:15px;
        }
        """)

        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setSpacing(12)
        overlay_layout.setContentsMargins(20, 20, 20, 20)

        self.title_label = QLabel()
        self.desc_label = QLabel()
        self.button = QPushButton()

        self.button.setStyleSheet("""
        QPushButton{
            background-color: transparent;
            border:2px solid #FFD700;
            border-radius:6px;
            padding:6px 14px;
            color:#FFD700;
        }

        QPushButton:hover{
            background-color: rgba(255,215,0,40);
        }
        """)

        self.title_label.setWordWrap(True)
        self.desc_label.setWordWrap(True)

        self.title_label.setStyleSheet("""
        color:white;
        font-size:20px;
        font-weight:600;
        """)

        self.desc_label.setStyleSheet("""
        color:#d0d0d0;
        font-size:14px;
        """)

        overlay_layout.addWidget(self.title_label)
        overlay_layout.addWidget(self.desc_label)
        overlay_layout.addWidget(self.button)

        container_layout.addWidget(self.image_label)
        self.overlay.raise_()

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)

        self.progress.setStyleSheet("""
        QProgressBar{
            background:#222;
            border:none;
        }

        QProgressBar::chunk{
            background:#FFD700;
        }
        """)

        main_layout.addWidget(self.image_container)
        main_layout.addWidget(self.progress)

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        # Let the base class and layout adjust sizes first
        super().resizeEvent(event)

        # update image now that container geometry is stable
        self.show_slide()

        # adjust overlay width based on container width
        max_overlay_w = max(0, self.image_container.width() - 60)
        overlay_w = min(420, max_overlay_w)
        self.overlay.setFixedWidth(overlay_w)
        self.overlay.adjustSize()
        overlay_h = self.overlay.height()

        x = 30
        y = self.image_container.height() - overlay_h - 30
        self.overlay.move(x, y)
        self.overlay.raise_()


    def create_slides(self):

        self.slides = [

            Slide(
                "assets/slide1.jpg",
                "Welcome",
                "Connect with friends instantly",
                "Get Started",
                None
            ),

            Slide(
                "assets/slide2.jpg",
                "Chat",
                "Send messages in real time",
                "Open Chat",
                None
            ),

            Slide(
                "assets/slide3.jpg",
                "Add Friends",
                "Find and add new friends",
                "Find Friends",
                None
            )

        ]


    def show_slide(self):
        slide = self.slides[self.current_index]
        pixmap = QPixmap(slide.image)

        # optionally adapt container ratio to image; clamp extreme ratios
        if self._dynamic_ratio and not pixmap.isNull():
            img_ratio = pixmap.width() / max(1, pixmap.height())
            # prevent the widget from becoming ridiculously tall or wide
            min_ratio, max_ratio = 0.5, 2.0  # width/height bounds
            img_ratio = max(min_ratio, min(max_ratio, img_ratio))
            self.image_container.set_ratio(img_ratio)
            # don't manually set fixed height here; let the layout respect the
            # new ratio during its normal sizing pass (triggered by updateGeometry)

        # determine size to scale against (container may have changed)
        target_size = self.image_container.size()

        # scale using target dimensions so label keeps proportions
        if self._expand_and_center:
            expanded = pixmap.scaled(
                target_size,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            cw = target_size.width()
            ch = target_size.height()
            x = max(0, (expanded.width() - cw) // 2)
            y = max(0, (expanded.height() - ch) // 2)
            scaled = expanded.copy(x, y, cw, ch)
        else:
            scaled = pixmap.scaled(
                target_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

        self.image_label.setPixmap(scaled)
        # ensure label itself exactly matches container dimensions
        self.image_label.resize(self.image_container.size())

        self.title_label.setText(slide.title)
        self.desc_label.setText(slide.description)
        self.button.setText(slide.button_text)
        self.button.setCursor(Qt.PointingHandCursor)

        # reflow overlay now that text changed
        self.overlay.adjustSize()
        overlay_h = self.overlay.height()
        x = 30
        y = self.image_container.height() - overlay_h - 30
        self.overlay.move(x, y)
        self.overlay.raise_()

    def next_slide(self):
        self.current_index += 1

        if self.current_index >= len(self.slides):
            self.current_index = 0

        self.show_slide()

    def update_progress(self):
        self.progress_value += 1
        self.progress.setValue(self.progress_value)

        if self.progress_value >= 100:
            self.progress_value = 0
            self.next_slide()


    def slide_clicked(self):
        slide = self.slides[self.current_index]

        if slide.action:
            slide.action()