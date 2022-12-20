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
from image_train_knn import image_encoding, train
import HandTrackingModule as htm
import re
import math
from sklearn import neighbors
import pickle
import json
# select camera source
use_picam2 = True

if use_picam2:
    # Use camera of raspberry #####################################################
    from picamera2 import Picamera2, Preview
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (680, 400)}))
    picam2.start()


dir_path = os.path.dirname(os.path.realpath(__file__))
labels = ['A','B','C','D','_D','E','G','H','I','K','L','M','N','O','P','Q','R','S','T','U','V','X','Y',"SAC","HUYEN", "HOI","NGA","NANG","CACH","CHAM", "HI","ILY","MU","RAU"]

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
        self.train_path = os.path.join(dir_path,"image")
        # Datalist
        self.datalist_path = os.path.join(dir_path,"datalist","data_encoding.json")

        self.current_char = self.ui.cbbFolder.currentText()
        if os.path.isfile(self.datalist_path):

            with open(self.datalist_path, 'r') as openfile:
                # Reading from json file
                self.dict_encoding = json.load(openfile)
        else:
            self.dict_encoding = {}
            for chr in labels:
                self.dict_encoding[chr] = []
        self.detector = htm.handDetector(maxHands=2, detectionCon=0.7)

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
        # Writing to sample.json
        with open(self.datalist_path, "w") as outfile:
            json.dump(self.dict_encoding, outfile)

        model_save_path = os.path.join(dir_path, "model","trained_knn_model.clf")
        self.train_model(model_save_path=model_save_path, n_neighbors=2)

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

            # self.img_path = os.path.join(self.train_path, self.ui.cbbFolder.currentText())
            # delete_all_file(self.img_path)
            self.dict_encoding[self.ui.cbbFolder.currentText()] = []

    def loop(self):

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

                self.current_char = self.ui.cbbFolder.currentText()
                self.img_path = os.path.join(self.train_path, self.current_char)

                # print("capture...")
                # Count image save in folder
                # self.ui.txtImgcount.setText(str(len(os.listdir(self.img_path))))
                self.ui.txtImgcount.setText(str(len(self.dict_encoding[self.current_char])))

                img_save = img.copy()
                hands, img = self.detector.findHands(img)
                if hands:
                    for _hand in hands:
                        if _hand['type'] == 'Right':
                            # print(_hand)
                            hand = _hand
                            # print(hand)
                            x, y, w, h = hand['bbox']
                            # Get encoding
                            if self.saving_img:

                                # find hand, return hands and img
                                lmList, bbox = self.detector.findPosition(img, draw=False)
                                encoding = []
                                if len(lmList) != 0:
                                    # print(lmList[4], lmList[8])
                                    list_point = []

                                    for (id, cx, cy) in lmList:
                                        if (id % 4) == 0:
                                            cv2.circle(img, (cx, cy), 15, (10*id, 0, 255-10*id), cv2.FILLED)
                                            list_point.append([cx,cy])
                                    # print(list_point)


                                    for i in range(len(list_point)):
                                        for j in range((i+1),len(list_point)):
                                            encoding.append(math.hypot(list_point[i][0] - list_point[j][0], list_point[i][1] - list_point[j][1]))
                                    # print(len(encoding))
                                    # print(encoding)
                                    for k in range(len(encoding)):
                                        encoding[k] = encoding[k] / encoding[0]

                                    # Dimension value
                                    for i in range(len(list_point)-1):
                                        if (list_point[0][0] >= list_point[i+1][0]):
                                            encoding.append(1)
                                        else:
                                            encoding.append(-1)

                                        if (list_point[0][1] >= list_point[i+1][1]):
                                            encoding.append(1)
                                        else:
                                            encoding.append(-1)
                                print("enc_img", encoding)
                                self.dict_encoding[self.current_char].append(encoding)


                            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8)* 255
                            if (x - offset) > 0 and (y- offset) > 0:
                                haveHand = True
                                imgCrop = img_save[y- offset:y+ h+ offset, x-offset:x+ w+ offset]
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
                # cv2.moveWindow("Picture",350,50)
                key = cv2.waitKey(1)
                # if self.saving_img  and haveHand:
                #     counter +=1
                #     cv2.imwrite(f'{self.img_path}/Image_{time.time()}.jpg', imgWhite)
                #     print(counter)
                haveHand = False

                if key == ord("q"):
                    break
            print(len(self.dict_encoding))

        except KeyboardInterrupt:
            print("Keyboard exception!")

        cv2.destroyAllWindows()
        self.cap.release()

    def train_model(self, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
        """
        Trains a k-nearest neighbors classifier for face recognition.
        :param model_save_path: (optional) path to save model on disk
        :param n_neighbors: (optional) number of neighbors to weigh in classification. Chosen automatically if not specified
        :param knn_algo: (optional) underlying data structure to support knn.default is ball_tree
        :param verbose: verbosity of training
        :return: returns knn classifier that was trained on the given data.
        """

        X = []
        y = []

        # Loop through each training image for the current person
        for char in labels:
            list_encoding = self.dict_encoding[char]
            if len(list_encoding) > 0:

                for img_encoding in list_encoding:
                    X.append(img_encoding)
                    y.append(char)

        # print(X)
        # print(y)
        # Determine how many neighbors to use for weighting in the KNN classifier
        if n_neighbors is None:
            n_neighbors = int(round(math.sqrt(len(X))))
            if verbose:
                print("Chose n_neighbors automatically:", n_neighbors)

        # Create and train the KNN classifier
        knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
        knn_clf.fit(X, y)

        # Save the trained KNN classifier
        if model_save_path is not None:
            with open(model_save_path, 'wb') as f:
                pickle.dump(knn_clf, f)

if __name__ == '__main__':
    CollectionImage()