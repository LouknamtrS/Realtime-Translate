import time
import numpy as np
import cv2
from PyQt5.QtCore import QThread, pyqtSignal


class TranslationWorker(QThread):
    text_detected = pyqtSignal(str)

    def __init__(self, state, capture, ocr, translator):
        super().__init__()
        self.state = state
        self.capture = capture
        self.ocr = ocr
        self.translator = translator

        self.last_frame_hash = None
        self.frame_change_threshold = 0.7
        self.last_translate_time = 0
        self.translate_interval = 0.7

    def run(self):
        print("WORKER STARTED")
        while self.state.running:

            if not self.state.translation_enabled:
                time.sleep(0.2)
                continue

            if not self.state.selected_region:
                time.sleep(0.2)
                continue

            try:
                image = self.capture.grab(self.state.selected_region)

                if not self._frame_changed(image):
                    time.sleep(0.1)
                    continue

                text = self.ocr.extract_text(image)

                if not text:
                    # Clear last text if current screen is empty to allow re-detecting same text later
                    self.state.last_text = ""
                    time.sleep(0.1)
                    continue
                
                if text == self.state.last_text:
                    time.sleep(0.1)
                    continue

                now = time.time()
                if now - self.last_translate_time < self.translate_interval:
                    continue

                self.last_translate_time = now
                self.state.last_text = text

                translated = self.translator.translate(text)
                self.text_detected.emit(translated)
                print(f"TRANSLATED: {text[:20]}... -> {translated[:20]}...")

            except Exception as e:
                print("WORKER LOOP ERROR:", e)

            time.sleep(0.1)
        print("WORKER STOPPED")
            
    def _frame_changed(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (64, 64))

        current_hash = np.mean(small)

        if self.last_frame_hash is None:
            self.last_frame_hash = current_hash
            return True

        diff = abs(current_hash - self.last_frame_hash)
        self.last_frame_hash = current_hash

        if diff > 0.05:
            print(f"DEBUG: Frame Diff: {diff:.3f} (Threshold: {self.frame_change_threshold})")

        return diff > self.frame_change_threshold
