from operator import index
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QFontComboBox, QSpinBox, QColorDialog,
    QLabel, QGroupBox, QFormLayout, QSlider,
    QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QComboBox

class SettingsPanel(QWidget):
    def __init__(self, overlay_config, toolbar_config, overlay, state, toolbar):
        super().__init__()
        self.overlay_config = overlay_config
        self.toolbar_config = toolbar_config
        self.overlay = overlay
        self.state = state
        self.toolbar = toolbar

        self.setWindowTitle("Settings")
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedWidth(500)
        
        self.setObjectName("SettingsPanel")

        self.setStyleSheet("""
        QWidget#SettingsPanel {
            background-color: #ffffff;
            color: #333;
            font-size: 14px;
        }

        QGroupBox {
            border: 1px solid #444;
            border-radius: 8px;
            margin-top: 10px;
            padding: 10px;
        }

        QGroupBox:title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
        }

        QPushButton {
            background-color: #333;
            color: white;
            border: none;
            padding: 6px;
            border-radius: 6px;
        }

        QPushButton:hover {
            background-color: #444;
        }

        QComboBox, QSpinBox {
            background-color: white;
            color: black;
            border: 1px solid #ccc;
            padding: 4px;
        }

        QComboBox QAbstractItemView {
            background-color: white;
            color: black;
            selection-background-color: #ddd;
            selection-color: black;
        }

        QTabWidget::pane {
            border: none;
        }

        QTabBar::tab {
            background: #eee;
            padding: 6px;
        }

        QTabBar::tab:selected {
            background: #ddd;
        }
        """)

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        overlay_tab = QWidget()
        overlay_layout = QVBoxLayout(overlay_tab)
        self.tabs.addTab(overlay_tab, "Text Settings")
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()

        self.font_box = QFontComboBox()
        self.font_box.currentFontChanged.connect(self.change_font)

        self.size_box = QSpinBox()
        self.size_box.setRange(10, 60)
        self.size_box.setValue(self.overlay_config.font_size)
        self.size_box.valueChanged.connect(self.change_size)

        self.text_color_btn = QPushButton("Choose Text Color")
        self.text_color_btn.clicked.connect(self.change_text_color)

        self.bg_color_btn = QPushButton("Choose Background Color")
        self.bg_color_btn.clicked.connect(self.change_bg_color)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(self.overlay_config.opacity)
        self.opacity_slider.valueChanged.connect(self.change_opacity)

        self.align_box = QComboBox()
        self.align_box.addItem("Left")
        self.align_box.addItem("Center")
        self.align_box.addItem("Right")
        self.align_box.currentIndexChanged.connect(self.change_alignment)

        appearance_layout.addRow("Font:", self.font_box)
        appearance_layout.addRow("Size:", self.size_box)
        appearance_layout.addRow("Text Color:", self.text_color_btn)
        appearance_layout.addRow("Background:", self.bg_color_btn)
        appearance_layout.addRow("Opacity:", self.opacity_slider)
        appearance_layout.addRow("Alignment:", self.align_box)

        appearance_group.setLayout(appearance_layout)

        # ===== Behavior Group =====
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout()

        self.lock_checkbox = QCheckBox("Lock translation position")
        self.lock_checkbox.stateChanged.connect(self.toggle_lock)

        behavior_layout.addWidget(self.lock_checkbox)

        behavior_group.setLayout(behavior_layout)

        overlay_layout.addWidget(appearance_group)
        overlay_layout.addWidget(behavior_group)
        overlay_layout.addStretch()

        toolbar_tab = QWidget()
        toolbar_layout = QFormLayout(toolbar_tab)

        self.toolbar_bg_btn = QPushButton("Choose Toolbar Background")
        self.toolbar_bg_btn.clicked.connect(self.change_toolbar_bg)

        self.toolbar_opacity_slider = QSlider(Qt.Horizontal)
        self.toolbar_opacity_slider.setRange(0, 255)
        self.toolbar_opacity_slider.setValue(self.toolbar_config.opacity)
        self.toolbar_opacity_slider.valueChanged.connect(self.change_toolbar_opacity)

        toolbar_layout.addRow("Background:", self.toolbar_bg_btn)
        toolbar_layout.addRow("Opacity:", self.toolbar_opacity_slider)

        self.tabs.addTab(toolbar_tab, "Toolbar")

    def change_font(self, font):
        self.overlay_config.font_family = font.family()
        self.overlay.update()

    def change_size(self, size):
        self.overlay_config.font_size = size
        self.overlay.update()

    def change_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.overlay_config.text_color = color
            self.overlay.update()

    def change_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.overlay_config.bg_color = color
            self.overlay.update()

    def change_opacity(self, value):
        self.overlay_config.opacity = value
        self.overlay_config.bg_color.setAlpha(value)
        self.overlay.update()
        

    def toggle_lock(self, state):
        self.state.overlay_locked = bool(state)

    def change_toolbar_bg(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.toolbar_config.bg_color = color
            self.toolbar_config.opacity = color.alpha()
            self.toolbar.update_style()

    def change_toolbar_opacity(self, value):
        self.toolbar_config.opacity = value
        self.toolbar_config.bg_color.setAlpha(value)
        self.toolbar.update_style()

    def change_alignment(self, index):
        if index == 0:
            self.state.text_alignment = Qt.AlignLeft | Qt.AlignTop
        elif index == 1:
            self.state.text_alignment = Qt.AlignHCenter | Qt.AlignTop
        elif index == 2:
            self.state.text_alignment = Qt.AlignRight | Qt.AlignTop

        self.overlay.update()