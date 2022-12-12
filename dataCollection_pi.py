import cv2
import sys
import os
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time
from folder_and_file import delete_all_file, creat_folder
from save_image_ui import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import Qt

# select camera source
use_picam2 = True

if use_picam2:
    # Use camera of raspberry #####################################################
    from picamera2 import Picamera2, Preview
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (680, 400)}))
    picam2.start()


dir_path = os.path.dirname(os.path.realpath(__file__))
labels = ['A','B','C','D','Đ','E','G','H','I','K','L','M','N','O','P','Q','R','S','T','U','V','X','Y',"SAC","HUYEN", "HOI","NGA","NANG","CACH","CHAM", "HI","ILY","MU","RAU"]

class CollectionImage():
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.ui = Ui_MainWindow()
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui.setupUi(self.MainWindow)
        self.MainWindow.show()
        self.init_variable()
        sys.exit(self.app.exec_())

    def init_variable(self):
        if not use_picam2:
            # Use laptop camera ####################################################
            self.cap = cv2.VideoCapture(0)

        ask_num = 1
        self.ui.cbbFolder.addItems(labels)
        self.find_hand_en = True
        self.saving_img = False
        self.exit = False
        self.train_path = os.path.join(dir_path,"train")

        self.msg_box_name = QtWidgets.QMessageBox()
        # Xử lý sự kiện
        self.ui.btnOnCam.clicked.connect(self.loop)
        self.ui.btnExit.clicked.connect(self.exit_app)
        self.ui.btnSave.pressed.connect(self.save_img)
        self.ui.btnSave.released.connect(self.stop_save_img)
        self.ui.btnDelete.clicked.connect(self.show_warning_msg)

    def exit_app(self):
        self.exit = True
        self.find_hand_en = False
        print("Exit")
        # cv2.destroyAllWindows()
        # self.cap.release()
        # self.MainWindow.destroy()
        # self.MainWindow.close()
        self.app.quit()

    def show_warning_msg(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)

        # setting message for Message Box
        msg.setText("Warning")

        # setting Message box window title
        msg.setWindowTitle("Warning MessageBox")

        # declaring buttons on Message Box
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        # start the app
        msg.buttonClicked.connect(self.delete_img)
        retval = msg.exec_()
        print("reval: ",retval)

    def save_img(self):
        self.saving_img = True
        # print("button save is press!")

    def stop_save_img(self):
        self.saving_img = False
        # print("button save is release!")

    def delete_img(self, bnt_select):
        del_confirm =  bnt_select.text()
        if "OK" in del_confirm:

            self.img_path = os.path.join(self.train_path, self.ui.cbbFolder.currentText())
            delete_all_file(self.img_path)

    def loop(self):

        detector = HandDetector(maxHands=2)
        offset = 20
        imgSize = 224
        counter = 0
        haveHand = False
        print("bnt is down: ",self.ui.btnSave.isDown())
        try:
            while self.find_hand_en:
                # print("find_hand_en: ",self.find_hand_en)
                if self.exit:
                    break

                if use_picam2:
                    # Use camera Pi ##############################################
                    img = picam2.capture_array()
                else:
                    # Use camera laptop  #######################################
                    success, img = self.cap.read()

                self.img_path = os.path.join(self.train_path, self.ui.cbbFolder.currentText())

                # print("capture...")

                self.ui.txtImgcount.setText(str(len(os.listdir(self.img_path))))

                hands, img = detector.findHands(img)
                if hands:
                    for _hand in hands:
                        if _hand['type'] == 'Right':
                            # print(_hand)
                            hand = _hand
                            # print(hand)
                            x, y, w, h = hand['bbox']

                            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8)* 255
                            if (x - offset) > 0 and (y- offset) > 0:
                                haveHand = True
                                imgCrop = img[y- offset:y+ h+ offset, x-offset:x+ w+ offset]
                                imgCropShape = imgCrop.shape
                                # print("img crop shape", imgCropShape)
                                # print(x,y,w,h)
                                aspectRatio = h/w
                                if aspectRatio > 1:
                                    k = imgSize/h
                                    wCal = math.ceil(k*w)
                                    # print(wCal)
                                    if wCal < imgSize:
                                        imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                                        imgResizeShape = imgResize.shape
                                        # print("img resize shape:", imgResizeShape)
                                        wGap = math.ceil((imgSize-wCal)/2)
                                        imgWhite[:, wGap:wCal + wGap] = imgResize
                                else:
                                    k = imgSize/w
                                    hCal = math.ceil(k*h)
                                    # print(hCal)
                                    if hCal < imgSize:
                                        imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                                        imgResizeShape = imgResize.shape
                                        # print("img resize shape:", imgResizeShape)
                                        hGap = math.ceil((imgSize-hCal)/2)
                                        imgWhite[hGap:hCal + hGap, :] = imgResize

                                # cv2.imshow("Picture crop", imgCrop)
                            # cv2.imshow("Picture White", imgWhite)
                            qt_image = QtGui.QImage(imgWhite, imgWhite.shape[1], imgWhite.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped() #self.image.shape[1], self.image.shape[0]
                            self.ui.txtImgHand.setPixmap(QtGui.QPixmap.fromImage(qt_image))


                imgShow = cv2.resize(img, (450,300))
                cv2.imshow("Picture", imgShow)
                cv2.moveWindow("Picture",350,50)
                key = cv2.waitKey(1)
                if self.saving_img  and haveHand:
                    counter +=1
                    cv2.imwrite(f'{self.img_path}/Image_{time.time()}.jpg', imgWhite)
                    print(counter)
                haveHand = False

                if key == ord("q"):
                    break

        except KeyboardInterrupt:
            print("Keyboard exception!")

        cv2.destroyAllWindows()
        self.cap.release()

if __name__ == '__main__':
    CollectionImage()