from PyQt5.QtGui import QColor

class OverlayConfig:
    def __init__(self):
        self.text_color = QColor(255, 255, 255)
        self.bg_color = QColor(255, 255, 255,0.1)
        self.font_family = "Arial"
        self.font_size = 16
        self.opacity = 0.1
        self.text_opacity = 255


class ToolbarConfig:
    def __init__(self):
        self.bg_color = QColor(30, 30, 30, 100)
        self.opacity =  200
        self.border_radius = 16