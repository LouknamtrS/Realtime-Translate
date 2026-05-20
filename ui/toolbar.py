from PyQt5.QtWidgets import QWidget, QHBoxLayout, QToolButton, QApplication
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QPainter, QColor


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
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Window |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Keep on top timer
        self.top_timer = QTimer(self)
        self.top_timer.timeout.connect(self.stay_on_top)


        self.setFixedHeight(90)
        self.setFixedWidth(520)
        self.setObjectName("ToolbarOverlay")

        self.update_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(16)

        self.btn_crop = self.create_button("icons/crop.svg", "Crop")
        self.btn_lock = self.create_button("icons/lock.svg", "Lock")
        self.btn_toggle = self.create_button("icons/eye-off.svg", "Hide Text")
        self.btn_stop = self.create_button("icons/pause.svg", "Pause")
        self.btn_hide_toolbar = self.create_button("icons/minus.svg", "Hide Bar")
        self.btn_settings = self.create_button("icons/settings.svg", "Settings")
        self.btn_close = self.create_button("icons/power.svg", "Exit")

        layout.addWidget(self.btn_crop)
        layout.addWidget(self.btn_lock)
        layout.addWidget(self.btn_toggle)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_hide_toolbar)
        layout.addWidget(self.btn_settings)
        layout.addWidget(self.btn_close)
 
        self.btn_crop.clicked.connect(self.open_crop)
        self.btn_lock.clicked.connect(self.toggle_lock)
        self.btn_toggle.clicked.connect(self.toggle_translation)
        self.btn_stop.clicked.connect(self.stop_translation)
        self.btn_hide_toolbar.clicked.connect(self.hide)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_close.clicked.connect(self.close_app)

        self.btn_lock.setCheckable(True)
        self.btn_lock.setChecked(False)

        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setChecked(True)

        self.btn_stop.setCheckable(True)
        self.btn_stop.setChecked(False)

        # Re-show toolbar after cropping
        self.crop_selector.cropped.connect(self.on_cropped)

        # Center on top of screen by default
        screen = self.screen().geometry()
        self.move((screen.width() - self.width()) // 2, 50)

        self.show()
        self.raise_()

    def on_cropped(self):
        self.show()
        self.raise_()

    def stay_on_top(self):
        if self.isVisible():
            self.raise_()

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

    def toggle_lock(self, checked):
        self.state.overlay_locked = checked
        if checked:
            self.btn_lock.setIcon(QIcon("icons/lock_unlock.svg"))
            self.btn_lock.setText("Unlock")
        else:
            self.btn_lock.setIcon(QIcon("icons/lock.svg"))
            self.btn_lock.setText("Lock")

    def toggle_translation(self, checked):
        if checked:
            self.overlay.show()
            #self.overlay.raise_()
            self.btn_toggle.setIcon(QIcon("icons/eye-off.svg"))
            self.btn_toggle.setText("Hide Text")

        else:
            self.overlay.hide()
            self.btn_toggle.setIcon(QIcon("icons/eye.svg"))
            self.btn_toggle.setText("Show Text")

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
        QApplication.instance().quit()

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
        self.setStyleSheet("""
        QToolButton {
            border: none;
            color: white;
            font-size: 12px;
        }

        QToolButton:hover {
            background-color: rgba(255,255,255,0.1);
        }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Smooth background rendering
        painter.setBrush(self.config.bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)
