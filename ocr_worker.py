import time
import numpy as np
import cv2
import mss
from paddleocr import PaddleOCR
from deep_translator import GoogleTranslator
from PyQt5.QtCore import QThread, pyqtSignal


class OCRWorker(QThread):
    text_detected = pyqtSignal(str)

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='en',
        )

        self.translator = GoogleTranslator(source='en', target='th')
        self.last_translate_time = 0

    def run(self):
        with mss.mss() as sct:
            while self.state.running:

                if not self.state.translation_enabled:
                    time.sleep(0.3)
                    continue

                if not self.state.selected_region:
                    time.sleep(0.3)
                    continue

                img = np.array(sct.grab(self.state.selected_region))
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                result = self.ocr.ocr(img)

                print("RAW RESULT:", result)

                text_list = []

                if result and isinstance(result, list):
                    for item in result:
                        if "rec_texts" in item:
                            texts = item["rec_texts"]
                            scores = item["rec_scores"]

                            for txt, score in zip(texts, scores):
                                if score > 0.6:
                                    text_list.append(txt)

                text = " ".join(text_list).strip()

                print("OCR RAW:", text)

                if text and text != self.state.last_text:
                    self.state.last_text = text

                    try:
                        translated = self.translator.translate(text)
                        self.text_detected.emit(translated)

                    except Exception as e:
                        print("TRANSLATE ERROR:", e)

                time.sleep(0.5)