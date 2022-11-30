import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import time
import sys
from video_gui import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import Qt

class OpenCV_Display():
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.ui = Ui_MainWindow()
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui.setupUi(self.MainWindow)
        self.MainWindow.show()
        self.init_variable()
        sys.exit(self.app.exec_())

    def init_variable(self):
        self.ui.btnStart.setText("Start")
        self.exit = False
        self.show_video = False
        self.audio_en = True
        self.ui.btnStart.clicked.connect(self.loop)
        self.ui.btnExit.clicked.connect(self.exit_app)
        self.ui.rbt_audio_en.clicked.connect(self.mute)
        self.hand_detect = HandDetect()



    def loop(self):
        self.show_video = not self.show_video
        # img = self.hand_detect.read_sign()
        # print(img.shape)
        while self.show_video:
            if self.exit:
                print("exit cmd")
                break
            img = self.hand_detect.read_sign()
            img = cv2.resize(img,(640,375))
            cv2.imshow("picture",img)
            cv2.destroyWindow("picture")
            # print(type(img))
            self.image = QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped() #self.image.shape[1], self.image.shape[0]
            self.ui.txtImage.setPixmap(QtGui.QPixmap.fromImage(self.image))
            key = cv2.waitKey(2)
            if key == ord("q"):
                break
        self.ui.txtImage.setText("PAUSE!")
        self.ui.txtImage.setAlignment(QtCore.Qt.AlignCenter)

    def exit_app(self):
        self.exit = True
        print("Exit")
        self.MainWindow.destroy()
        self.app.quit()

    def mute(self):

        self.audio_en = not self.ui.rbt_audio_en.isChecked()
        if self.audio_en:
            print("Audio ON")
        else:
            print("Audio OFF")

class HandDetect():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetector(maxHands=2)
        self.classifier = Classifier("model/keras_model.h5", "model/labels.txt")
        self.offset = 20
        self.imgSize = 224
        self.threshold = 0.95
        self.labels =  ["A", "B", "C", "D", "E", "G", "H", "I", "L", "M", "N", "ILY", "^", "HUYEN", "SAC","_D", "T", "O"]

    def read_sign(self):
        success, img = self.cap.read()
        imgOutput = img.copy()
        hands, img = self.detector.findHands(img)
        if hands:
            for _hand in hands:
                if _hand['type'] == 'Right':
                    # print(_hand)
                    hand = _hand
                    # print(hand)
                    x, y, w, h = hand['bbox']

                    imgWhite = np.ones((self.imgSize, self.imgSize, 3), np.uint8)* 255
                    if (x - self.offset) > 0 and (y- self.offset) > 0:
                        haveHand = True
                        imgCrop = img[y- self.offset:y+ h+ self.offset, x-self.offset:x+ w+ self.offset]
                        imgCropShape = imgCrop.shape
                        # print("img crop shape", imgCropShape)
                        # print(x,y,w,h)
                        aspectRatio = h/w
                        if aspectRatio > 1:
                            k = self.imgSize/h
                            wCal = math.ceil(k*w)
                            # print(wCal)
                            imgResize = cv2.resize(imgCrop, (min(wCal,self.imgSize), self.imgSize))
                            imgResizeShape = imgResize.shape
                            # print("img resize shape:", imgResizeShape)
                            wGap = math.ceil((self.imgSize-wCal)/2)
                            imgWhite[:, wGap:wCal + wGap] = imgResize
                            prediction, index = self.classifier.getPrediction(imgWhite, draw=False)
                            print(prediction, index)
                        else:
                            k = self.imgSize/w
                            hCal = math.ceil(k*h)
                            # print(hCal)
                            imgResize = cv2.resize(imgCrop, (self.imgSize, min(self.imgSize, hCal)))
                            imgResizeShape = imgResize.shape
                            # print("img resize shape:", imgResizeShape)
                            hGap = math.ceil((self.imgSize-hCal)/2)
                            imgWhite[hGap:hCal + hGap, :] = imgResize
                            prediction, index = self.classifier.getPrediction(imgWhite, draw=False)

                        if prediction[index] > self.threshold :
                            try:
                                cv2.rectangle(imgOutput, (x - self.offset, y - self.offset-50),
                                    (x - self.offset+90, y - self.offset-50+50), (255, 0, 255), cv2.FILLED)
                                cv2.putText(imgOutput, self.labels[index], (x, y -26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
                                cv2.rectangle(imgOutput, (x-self.offset, y-self.offset),
                                            (x + w+self.offset, y + h+self.offset), (255, 0, 255), 4)
                            except:
                                pass

                        # cv2.imshow("ImageCrop", imgCrop)
                        # cv2.imshow("ImageWhite", imgWhite)
        return imgOutput

if __name__ == '__main__':
    cv_app = OpenCV_Display()