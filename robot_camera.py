import cv2
import numpy as np

class LaptopCamera():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        # success, self.img = self.cap.read()

class PiCamera():
    def __init__(self):
        from picamera2 import Picamera2, Preview
        self.picam2 = Picamera2()
        # self.picam2.start_preview(Preview.QTGL)
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 375)}))
        self.picam2.start()

        self.img = self.picam2.capture_array()
