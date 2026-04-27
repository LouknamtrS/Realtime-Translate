from PyQt5.QtCore import Qt
class AppState:
    def __init__(self):
        self.selected_region = None
        self.selected_region_display = None

        self.overlay_position = None
        self.overlay_locked = False
        self.overlay_size = (400, 200)
        self.auto_expand = True

        self.translated_text = ""
        self.last_text = ""
        self.text_alignment = Qt.AlignLeft | Qt.AlignTop

        self.running = False
        self.translation_enabled = True 