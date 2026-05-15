import mss
import numpy as np
import cv2

class ScreenCaptureService:
    def __init__(self):
        self.sct = mss.mss()

    def grab(self, region):
        img = np.array(self.sct.grab(region))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)