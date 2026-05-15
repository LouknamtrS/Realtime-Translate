from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QFontMetrics

class TranslateOverlay(QWidget):
    def __init__(self, state, config):
        super().__init__()
        self.state = state
        self.config = config

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Window |
            Qt.WindowDoesNotAcceptFocus
        )

        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set default opacity to 0 (invisible) until text is detected
        self.setWindowOpacity(0.0)

        self.dragging = False
        self.drag_position = None

        self.resizing = False
        self.resize_margin = 16
        self.min_width = 200
        self.min_height = 100

        # Keep on top timer
        self.top_timer = QTimer(self)
        self.top_timer.timeout.connect(self.stay_on_top)
        # self.top_timer.start(2000)

    def stay_on_top(self):
        if self.isVisible():
            self.raise_()

    def update_position_from_crop(self):
        if self.state.selected_region_display:
            r = self.state.selected_region_display

            # Position the overlay below the selected region to avoid OCR feedback
            offset = 10
            new_left = r["left"]
            new_top = r["top"] + r["height"] + offset

            self.state.overlay_position = (new_left, new_top)
            self.state.overlay_size = (r["width"], r["height"])

            self.setGeometry(new_left, new_top, r["width"], r["height"])
            self.show()
            self.raise_()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        bg = QColor(self.config.bg_color)
        border = QColor(255, 255, 255, 30)

        painter.setBrush(bg)
        painter.setPen(border)
        painter.drawRoundedRect(self.rect(), 18, 18)

        painter.setPen(self.config.text_color)
        font = QFont(self.config.font_family, self.config.font_size)
        painter.setFont(font)

        rect = QRect(24, 24, self.width()-48, self.height()-48) 

        metrics = QFontMetrics(font)

        text = self.state.translated_text

        elided = metrics.elidedText(
            text,
            Qt.ElideRight,
            rect.width() * (rect.height() // metrics.height())
        )

        flags = int(Qt.TextWordWrap) | int(self.state.text_alignment)

        painter.drawText(
            rect,
            flags,
            self.state.translated_text
        )

        handle_size = 12
        painter.setBrush(QColor(255, 255, 255, 80))
        painter.setPen(Qt.NoPen)
        painter.drawRect(
            self.width()-handle_size,
            self.height()-handle_size,
            handle_size,
            handle_size
        )

    def mousePressEvent(self, event):
        if self.state.overlay_locked:
            return

        if event.button() == Qt.LeftButton:
  
            if self._is_on_resize_area(event.pos()):
                self.resizing = True
                self.drag_position = event.globalPos()
            else:
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

            event.accept()


    def mouseMoveEvent(self, event):
        if self.state.overlay_locked:
            return

        if self.resizing:
            delta = event.globalPos() - self.drag_position
            new_width = max(self.width() + delta.x(), self.min_width)
            new_height = max(self.height() + delta.y(), self.min_height)

            self.resize(new_width, new_height)
            self.state.overlay_size = (new_width, new_height)

            self.drag_position = event.globalPos()
            event.accept()

        elif self.dragging:
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            self.state.overlay_position = (new_pos.x(), new_pos.y())
            event.accept()

        else:

            if self._is_on_resize_area(event.pos()):
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.OpenHandCursor)


    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.setCursor(Qt.OpenHandCursor)

    def enterEvent(self, event):
        if not self.state.overlay_locked:
            self.setCursor(Qt.OpenHandCursor)

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)

    def _is_on_resize_area(self, pos):
        return (
            pos.x() >= self.width() - self.resize_margin and
            pos.y() >= self.height() - self.resize_margin
        )
        