import cv2
import numpy as np
from paddleocr import PaddleOCR


class OCRService:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang="en")

    def extract_text(self, image, score_threshold=0.75):
        processed = self._preprocess(image)

        try:
            result = self.ocr.ocr(processed)
        except Exception as e:
            print("OCR ERROR:", e)
            return ""

        return self._parse_result(result, score_threshold)

    def _preprocess(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=5)

        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            15,
            5
        )

        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)


    def _parse_result(self, result, score_threshold):
        if not result:
            return ""

        text_list = []

        for item in result:
            texts = item.get("rec_texts", [])
            scores = item.get("rec_scores", [])

            for txt, score in zip(texts, scores):
                clean = txt.strip()
                if score > score_threshold and len(clean) > 2:
                    text_list.append(clean)

        return " ".join(text_list).strip()