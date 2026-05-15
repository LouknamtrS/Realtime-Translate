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
            background-color: #f5f5f5;
            color: #333;
            border: 1px solid #ccc;
            padding: 6px 12px;
            border-radius: 6px;
            min-height: 24px;
        }

        QPushButton:hover {
            background-color: #e8e8e8;
            border-color: #bbb;
        }

        QComboBox, QFontComboBox, QSpinBox {
            background-color: #f5f5f5;
            color: #333;
            border: 1px solid #ccc;
            padding: 4px 8px;
            border-radius: 6px;
            min-width: 150px;
            min-height: 24px;
        }

        QComboBox:hover, QSpinBox:hover {
            background-color: #e8e8e8;
            border-color: #bbb;
        }

        QComboBox::drop-down {
            background-color: transparent;
            width: 24px;
            border-left: 1px solid #ccc;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }

        QComboBox::drop-down:hover {
            background-color: #ddd;
        }

        QComboBox::down-arrow {
            border-left: 4px solid none;
            border-right: 4px solid none;
            border-top: 5px solid #555;
            width: 0;
            height: 0;
        }

        QSpinBox::up-button, QSpinBox::down-button {
            background-color: transparent;
            width: 20px;
            border-left: 1px solid #ccc;
        }

        QSpinBox::up-button {
            border-top-right-radius: 6px;
        }

        QSpinBox::down-button {
            border-bottom-right-radius: 6px;
        }

        QSpinBox::up-arrow, QSpinBox::down-arrow {
            width: 8px;
            height: 8px;
        }

        QSpinBox::up-arrow { border-left: 4px solid none; border-right: 4px solid none; border-bottom: 5px solid #555; width: 0; height: 0; }
        QSpinBox::down-arrow { border-left: 4px solid none; border-right: 4px solid none; border-top: 5px solid #555; width: 0; height: 0; }

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
        overlay_layout = QFormLayout(overlay_tab)
        self.tabs.addTab(overlay_tab, "Text Settings")

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

        self.bg_opacity_slider = QSlider(Qt.Horizontal)
        self.bg_opacity_slider.setRange(0, 255)
        self.bg_opacity_slider.setValue(self.overlay_config.opacity)
        self.bg_opacity_slider.valueChanged.connect(self.change_bg_opacity)

        self.text_opacity_slider = QSlider(Qt.Horizontal)
        self.text_opacity_slider.setRange(0, 255)
        self.text_opacity_slider.setValue(self.overlay_config.text_opacity)
        self.text_opacity_slider.valueChanged.connect(self.change_text_opacity)

        self.align_box = QComboBox()
        self.align_box.addItem("Left")
        self.align_box.addItem("Center")
        self.align_box.addItem("Right")
        self.align_box.currentIndexChanged.connect(self.change_alignment)

        overlay_layout.addRow("Font:", self.font_box)
        overlay_layout.addRow("Size:", self.size_box)
        overlay_layout.addRow("Text Color:", self.text_color_btn)
        overlay_layout.addRow("Text Opacity:", self.text_opacity_slider)
        overlay_layout.addRow("Background:", self.bg_color_btn)
        overlay_layout.addRow("BG Opacity:", self.bg_opacity_slider)
        overlay_layout.addRow("Alignment:", self.align_box)

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
        color = QColorDialog.getColor(self.overlay_config.text_color)
        if color.isValid():
            color.setAlpha(self.overlay_config.text_opacity)
            self.overlay_config.text_color = color
            self.overlay.update()

    def change_bg_color(self):
        color = QColorDialog.getColor(self.overlay_config.bg_color)
        if color.isValid():
            # Use at least 1 alpha to keep window clickable
            actual_opacity = max(1, self.overlay_config.opacity)
            color.setAlpha(actual_opacity)
            self.overlay_config.bg_color = color
            self.overlay.update()

    def change_bg_opacity(self, value):
        self.overlay_config.opacity = value
        self.overlay_config.bg_color.setAlpha(max(1, value))
        self.overlay.update()

    def change_text_opacity(self, value):
        self.overlay_config.text_opacity = value
        self.overlay_config.text_color.setAlpha(value)
        self.overlay.update()
        

    def change_toolbar_bg(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.toolbar_config.bg_color = color
            self.toolbar_config.opacity = max(1, color.alpha())
            self.toolbar_config.bg_color.setAlpha(self.toolbar_config.opacity)
            self.toolbar.update()

    def change_toolbar_opacity(self, value):
        self.toolbar_config.opacity = value
        self.toolbar_config.bg_color.setAlpha(max(1, value))
        self.toolbar.update()

    def change_alignment(self, index):
        if index == 0:
            self.state.text_alignment = Qt.AlignLeft | Qt.AlignTop
        elif index == 1:
            self.state.text_alignment = Qt.AlignHCenter | Qt.AlignTop
        elif index == 2:
            self.state.text_alignment = Qt.AlignRight | Qt.AlignTop

        self.overlay.update()