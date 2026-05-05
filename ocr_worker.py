import time
import difflib
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
            use_angle_cls=False,
            lang="en",
        )

        self.translator = GoogleTranslator(source="en", target="th")

        self.loop_delay = 0.1

        self.translate_interval = 0.7

        self.last_translate_time = 0
        self.similarity_threshold = 0.92

        self.last_frame_hash = None
        self.frame_change_threshold = 8.0

    def preprocess(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        gray = cv2.convertScaleAbs(gray, alpha=1.8, beta=10)

        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)


    def frame_changed(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (64, 64))

        current_hash = np.mean(small)

        if self.last_frame_hash is None:
            self.last_frame_hash = current_hash
            return True

        diff = abs(current_hash - self.last_frame_hash)
        self.last_frame_hash = current_hash

        return diff > self.frame_change_threshold
    

    def run(self):
        with mss.mss() as sct:
            while self.state.running:

                if not self.state.translation_enabled or not self.state.selected_region:
                    time.sleep(self.loop_delay)
                    continue

                img = np.array(sct.grab(self.state.selected_region))
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                if not self.frame_changed(img):
                    time.sleep(self.loop_delay)
                    continue

                img = self.preprocess(img)
                text = self.perform_ocr(img)

                if not text:
                    time.sleep(self.loop_delay)
                    continue

                similarity = difflib.SequenceMatcher(
                    None,
                    text,
                    self.state.last_text
                ).ratio()

                if similarity > self.similarity_threshold:
                    time.sleep(self.loop_delay)
                    continue

                now = time.time()
                if now - self.last_translate_time < self.translate_interval:
                    time.sleep(self.loop_delay)
                    continue

                self.last_translate_time = now

                try:
                    translated = self.translator.translate(text)
                    self.state.last_text = text
                    self.text_detected.emit(translated)
                except Exception as e:
                    print("Translate error:", e)

                time.sleep(self.loop_delay)

    def perform_ocr(self, img):
        try:
            result = self.ocr.ocr(img)
        except Exception as e:
            print("OCR error:", e)
            return ""

        if not result:
            return ""

        text_list = []

        print("OCR RAW:", result)

        for item in result:
            if isinstance(item, dict):
                texts = item.get("rec_texts", [])
                scores = item.get("rec_scores", [])

                for txt, score in zip(texts, scores):
                    clean_txt = txt.strip()

                    if (
                        score > 0.75 and
                        len(clean_txt) > 3
                    ):
                        text_list.append(clean_txt)

        return " ".join(text_list).strip()