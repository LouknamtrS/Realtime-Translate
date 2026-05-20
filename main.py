import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
from core.app_state import AppState
from core.config import OverlayConfig
from ui.overlay import TranslateOverlay
from ui.crop_selector import CropSelector
from ui.toolbar import ToolbarOverlay
from ui.setting_panel import SettingsPanel
from core.config import OverlayConfig, ToolbarConfig

from services.screen_capture_service import ScreenCaptureService
from services.ocr_service import OCRService
from services.translation_service import TranslationService
from workers.translation_worker import TranslationWorker

from pynput import keyboard

class GlobalShortcut(QObject):
    show_toolbar = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.listener = keyboard.GlobalHotKeys({
            '<cmd>+1': self.on_activate
        })
        self.listener.start()

    def on_activate(self):
        self.show_toolbar.emit()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    state = AppState()
    overlay_config = OverlayConfig()
    toolbar_config = ToolbarConfig()

    overlay = TranslateOverlay(state, overlay_config)
    crop = CropSelector(state, overlay)

    toolbar = ToolbarOverlay(
        state,
        overlay,
        crop,
        None,
        toolbar_config
    )

    settings = SettingsPanel(
        overlay_config,
        toolbar_config,
        overlay,
        state,
        toolbar
    )

    toolbar.settings_panel = settings

    capture_service = ScreenCaptureService()
    ocr_service = OCRService()
    translation_service = TranslationService()

    worker = TranslationWorker(
        state,
        capture_service,
        ocr_service,
        translation_service
    )

    toolbar.worker = worker

    def handle_text(text):
        state.translated_text = text
        # Make overlay visible when text arrives, hide if empty
        if text.strip():
            overlay.setWindowOpacity(1.0)
        else:
            overlay.setWindowOpacity(0.0)
        overlay.update()

    toolbar.worker.text_detected.connect(handle_text)
    
    # Global shortcut setup
    shortcut = GlobalShortcut()
    shortcut.show_toolbar.connect(toolbar.show)
    shortcut.show_toolbar.connect(toolbar.raise_)

    state.running = True
    toolbar.worker.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
