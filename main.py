import sys
from PyQt5.QtWidgets import QApplication
from app_state import AppState
from config import OverlayConfig
from overlay import TranslateOverlay
from crop_selector import CropSelector
from ocr_worker import OCRWorker
from toolbar import ToolbarOverlay
from setting_panel import SettingsPanel
from config import OverlayConfig, ToolbarConfig

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
    toolbar.worker = OCRWorker(state)

    def handle_text(text):
        state.translated_text = text
        overlay.update()

    toolbar.worker.text_detected.connect(handle_text)
    state.running = True
    toolbar.worker.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()