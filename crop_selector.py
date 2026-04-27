from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRect
import mss

class CropSelector(QWidget):
    def __init__(self, state, overlay):
        super().__init__()
        self.state = state
        self.overlay = overlay

        self.start = None
        self.end = None

        self.setWindowOpacity(0.3)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)
        self.setGeometry(self.screen().geometry())
        self.setCursor(Qt.CrossCursor)

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        rect = QRect(self.start, self.end).normalized()
        top_left = self.mapToGlobal(rect.topLeft())

        self.state.selected_region_display = {
            "left": top_left.x(),
            "top": top_left.y(),
            "width": rect.width(),
            "height": rect.height()
        }

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            scale = monitor["width"] / self.screen().geometry().width()

            self.state.selected_region = {
                "left": int(top_left.x() * scale),
                "top": int(top_left.y() * scale),
                "width": int(rect.width() * scale),
                "height": int(rect.height() * scale)
            }

        print("REGION SET:", self.state.selected_region)

        self.state.overlay_position = None
        self.state.overlay_size = None

        self.overlay.update_position_from_crop()
        
        self.hide()
        

    def paintEvent(self, event):
        if self.start and self.end:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2))
            painter.drawRect(QRect(self.start, self.end))