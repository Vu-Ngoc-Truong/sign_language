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
        self.ui.txtImage.setAlignment(QtCore.Qt.AlignCenter)
        self.cap = cv2.VideoCapture(0)
        self.prev_frame_time = time.time()
        self.ui.btnStart.clicked.connect(self.loop)
        self.ui.btnExit.clicked.connect(self.exit_app)
        self.ui.rbt_audio_en.clicked.connect(self.mute)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.display_video)
        # self.timer.start()

    def display_video(self):
        success, img = self.cap.read()
        if success:
            img = cv2.resize(img,(640,400))

        else:
            print("Can't read video!")
            return
        # cv2.imshow("picture",img)
        # cv2.destroyWindow("picture")

        # time when we finish processing for this frame


        # print(type(img))
        self.image = QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped() #self.image.shape[1], self.image.shape[0]
        self.ui.txtImage.setPixmap(QtGui.QPixmap.fromImage(self.image))
        key = cv2.waitKey(2)

        # Calculating the fps
        new_frame_time = time.time()
        fps = 1/(new_frame_time-self.prev_frame_time)
        self.prev_frame_time = new_frame_time
        print(fps)

    def loop(self):
        self.show_video = not self.show_video
        if self.show_video:
            self.timer.start(20)
            self.prev_frame_time = time.time()
        else:
            self.timer.stop()
            self.ui.txtImage.setText("PAUSE!")
        if self.exit:
            print("exit cmd")
            self.timer.stop()

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
