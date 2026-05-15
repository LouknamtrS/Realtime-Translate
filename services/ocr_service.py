import cv2
import numpy as np
import logging
from paddleocr import PaddleOCR

# Suppress PaddleOCR logging to keep console clean
logging.getLogger("ppocr").setLevel(logging.ERROR)

class OCRService:
    def __init__(self):
        # PaddleOCR initialization
        self.ocr = PaddleOCR(use_angle_cls=False, lang="en")

    def extract_text(self, image, score_threshold=0.7):
        processed = self._preprocess(image)

        try:
            result = self.ocr.ocr(processed)
        except Exception as e:
            print("OCR ERROR:", e)
            return ""

        return self._parse_result(result, score_threshold)

    def _preprocess(self, img):
        # Restore effective preprocessing from the original worker
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast
        gray = cv2.convertScaleAbs(gray, alpha=1.8, beta=10)

        # Adaptive thresholding helps with varying lighting and backgrounds
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            15,
            2
        )

        # PaddleOCR expects a 3-channel BGR image
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)


    def _parse_result(self, result, score_threshold):
        if not result:
            return ""

        text_list = []

        def walk(data):
            """Recursively find all (text, score) tuples in the OCR result."""
            if isinstance(data, list):
                for item in data:
                    walk(item)
            elif isinstance(data, tuple) and len(data) == 2 and isinstance(data[0], str) and isinstance(data[1], (float, int)):
                txt, score = data
                clean = txt.strip()
                if score > score_threshold and len(clean) > 1:
                    text_list.append(clean)
            elif isinstance(data, dict):
                # Handle dictionary format if present
                texts = data.get("rec_texts", [])
                scores = data.get("rec_scores", [])
                for txt, score in zip(texts, scores):
                    clean = txt.strip()
                    if score > score_threshold and len(clean) > 1:
                        text_list.append(clean)
                for value in data.values():
                    walk(value)

        walk(result)
        return " ".join(text_list).strip()
