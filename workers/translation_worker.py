import time
import numpy as np
import cv2
import difflib
from collections import deque, Counter
from PyQt5.QtCore import QThread, pyqtSignal


class TranslationWorker(QThread):
    text_detected = pyqtSignal(str)

    def __init__(self, state, capture, ocr, translator):
        super().__init__()
        self.state = state
        self.capture = capture
        self.ocr = ocr
        self.translator = translator

        self.last_frame = None
        self.ocr_buffer = deque(maxlen=2)
        self.ocr_countdown = 0
        self.frame_change_threshold = 0.5  # Lowered for better sensitivity
        self.last_translate_time = 0
        self.translate_interval = 0.5
        self.is_moving = False
        self.last_move_time = 0
        self.heartbeat_interval = 1.5
        self.last_region = None

    def run(self):
        print("WORKER STARTED")
        while self.state.running:
            now = time.time()

            if not self.state.translation_enabled or not self.state.selected_region:
                time.sleep(0.2)
                continue
            
            # Reset if region changed
            if self.state.selected_region != self.last_region:
                self.last_region = self.state.selected_region
                self.last_frame = None
                self.is_moving = False

            try:
                image = self.capture.grab(self.state.selected_region)
                
                frame_changed = self._frame_changed(image)
                
                # Movement logic
                should_ocr = False
                if frame_changed and not self.is_moving:
                    should_ocr = True # first change -> immediate OCR
                
                if frame_changed:
                    self.last_move_time = now
                    self.is_moving = True
                
                if self.is_moving and now - self.last_translate_time >= self.heartbeat_interval:
                    should_ocr = True # heartbeat during movement
                
                if self.is_moving and now - self.last_move_time > 1.0:
                    self.is_moving = False
                
                if should_ocr:
                    self.ocr_countdown = self.ocr_buffer.maxlen
                    self.ocr_buffer.clear()
                
                # Only proceed to OCR if should_ocr is true OR self.ocr_countdown > 0
                if not should_ocr and self.ocr_countdown <= 0:
                    time.sleep(0.05)
                    continue

                if self.ocr_countdown > 0:
                    self.ocr_countdown -= 1

                text = self.ocr.extract_text(image)
                if text:
                    print(f"DEBUG: OCR Raw: '{text[:50]}...'")
                
                self.ocr_buffer.append(text)

                if len(self.ocr_buffer) < self.ocr_buffer.maxlen:
                    continue

                # Fuzzy Stability check: 2/2 using similarity
                text1, text2 = self.ocr_buffer[0], self.ocr_buffer[1]
                
                if not text1 and not text2:
                    if self.state.last_text != "":
                        self.state.last_text = ""
                        self.text_detected.emit("")
                    continue

                # Calculate similarity between consecutive frames
                similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
                
                if similarity < 0.85: # Require 85% similarity for stability
                    continue
                
                # Pick the longer one as the stable text
                stable_text = text1 if len(text1) >= len(text2) else text2

                if stable_text == self.state.last_text:
                    continue

                now = time.time()
                if now - self.last_translate_time < self.translate_interval:
                    continue

                self.last_translate_time = now
                self.state.last_text = stable_text

                translated = self.translator.translate(stable_text)
                self.text_detected.emit(translated)
                print(f"STABLE OCR (Sim: {similarity:.2f}): {stable_text[:30]}...")

            except Exception as e:
                print("WORKER LOOP ERROR:", e)

            time.sleep(0.05)
        print("WORKER STOPPED")
            
    def _frame_changed(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # small = cv2.resize(gray, (32, 32))

        if self.last_frame is None:
            self.last_frame = gray
            return True

        # Pixel-wise difference
        diff = cv2.absdiff(gray, self.last_frame)
        score = np.mean(diff)
        
        self.last_frame = gray

        if score > self.frame_change_threshold:
            print(f"DEBUG: Frame Change Detected! Score: {score:.3f}")
            return True

        return False
