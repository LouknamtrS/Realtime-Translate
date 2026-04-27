from PyQt5.QtWidgets import QWidget, QHBoxLayout, QToolButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon


class ToolbarOverlay(QWidget):
    def __init__(self, state, overlay, crop_selector, settings_panel, config):
        super().__init__()

        self.state = state
        self.overlay = overlay
        self.crop_selector = crop_selector
        self.settings_panel = settings_panel
        self.config = config

        self.dragging = False
        self.drag_position = None
        self.setCursor(Qt.OpenHandCursor)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.setFixedHeight(90)
        self.setObjectName("ToolbarOverlay")

        self.update_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(16)

        self.btn_crop = self.create_button("icons/crop.svg", "Crop")
        self.btn_toggle = self.create_button("icons/eye-off.svg", "Hide")
        self.btn_stop = self.create_button("icons/pause.svg", "Pause")
        self.btn_settings = self.create_button("icons/settings.svg", "Settings")
        self.btn_close = self.create_button("icons/power.svg", "Exit")

        layout.addWidget(self.btn_crop)
        layout.addWidget(self.btn_toggle)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_settings)
        layout.addWidget(self.btn_close)
 
        self.btn_crop.clicked.connect(self.open_crop)
        self.btn_toggle.clicked.connect(self.toggle_translation)
        self.btn_stop.clicked.connect(self.stop_translation)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_close.clicked.connect(self.close_app)

        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setChecked(True)

        self.btn_stop.setCheckable(True)
        self.btn_stop.setChecked(False)

        self.show()

    def create_button(self, icon_path, text):
        btn = QToolButton()
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(22, 22))
        btn.setText(text)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(56, 56)
        return btn

    def open_crop(self):
        self.crop_selector.show()

    def toggle_translation(self, checked):
        if checked:
            self.overlay.show()
            self.btn_toggle.setIcon(QIcon("icons/eye-off.svg"))
            self.btn_toggle.setText("Hide")

        else:
            self.overlay.hide()
            self.btn_toggle.setIcon(QIcon("icons/eye.svg"))
            self.btn_toggle.setText("Show")

    def stop_translation(self, checked):
        if checked:
            self.state.translation_enabled = False
            self.btn_stop.setIcon(QIcon("icons/play.svg"))
            self.btn_stop.setText("Resume")

        else:
            self.state.translation_enabled = True
            self.btn_stop.setIcon(QIcon("icons/pause.svg"))
            self.btn_stop.setText("Pause")

    def open_settings(self):
        if self.settings_panel:
            self.settings_panel.show()

    def close_app(self):
        self.state.running = False
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.drag_position)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.setCursor(Qt.OpenHandCursor)

    def update_style(self):
        color = self.config.bg_color
        rgba = f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"

        self.setStyleSheet(f"""
        QWidget#ToolbarOverlay {{
            background-color: {rgba};
            border-radius: 20px;
        }}

        QToolButton {{
            border: none;
            color: white;
            font-size: 12px;
        }}

        QToolButton:hover {{
            background-color: rgba(255,255,255,0.1);
        }}
        """)