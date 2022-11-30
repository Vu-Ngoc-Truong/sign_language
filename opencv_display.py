import cv2
import numpy as np
import sys
import time
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
        self.cap = cv2.VideoCapture(0)
        self.ui.btnStart.clicked.connect(self.loop)
        self.ui.btnExit.clicked.connect(self.exit_app)
        self.ui.rbt_audio_en.clicked.connect(self.mute)


    def loop(self):
        self.show_video = not self.show_video
        success, img = self.cap.read()
        print(img.shape)
        while self.show_video:
            if self.exit:
                print("exit cmd")
                break
            success, img = self.cap.read()
            img = cv2.resize(img,(640,400))
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




if __name__ == '__main__':
    cv_app = OpenCV_Display()
