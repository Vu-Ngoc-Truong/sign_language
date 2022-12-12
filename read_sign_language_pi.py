import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import time
from text_to_speech import text_to_speech
from speech_to_text import listen_audio
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import Qt
from video_gui import Ui_MainWindow
from robot_camera import LaptopCamera , PiCamera
from convert_word import word_to_char, char_to_word
import os
HOME = os.path.expanduser('~')
import threading
from collections import Counter
#######################
dir_path = os.path.dirname(os.path.realpath(__file__))

# # Use raspberry pi camera #########################################
# from picamera2 import Picamera2, Preview

# picam2 = Picamera2()
# picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 370)}))
# picam2.start()

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
        self.ui.btnReply.clicked.connect(self.reply_sign)
        self.hand_detect = HandDetect()
        self.labels_detail =  ['a','b','c','d','e','h','i','o','t','u','y','l',"Mũ","Râu","Sắc","Huyền","Cách","Chấm"]
        self.labels_char =    ['a','b','c','d','e','h','i','o','t','u','y','l',"^","w","'","`"," ","."]
        # self.labels_detail =  ['A','B','C','D','Đ','E','G','H','I','K','L','M','N','O','P','Q','R','S','T','U','V','X','Y',"Mũ","Râu","Sắc","Huyền","Ngã","Nặng","Cách","Chấm", "Xin chào","Tôi yêu bạn"]
        self.language = 'vi'
        self.video_enable = True
        self.last_indexs = ""
        self.dict_image_name = {"'": "sac", "`": "huyen","?": "hoi", "~": "nga", "*": "nang", "w": "rau", "^": "mu", "đ":"_d"}



    def loop(self):

        # print("loop start")
        if not self.video_enable:
            return
        self.show_video = not self.show_video
        if self.show_video:
            self.ui.btnStart.setText("Stop")
        else:
            self.ui.btnStart.setText("Start")
            self.last_indexs = ""
        self.result_list = []
        self.count_label = 0
        self.result_string = ""
        self.result_string_list = [""]
        while self.show_video and self.video_enable:
            if self.exit:
                print("exit cmd")
                break
            img, indexs = self.hand_detect.read_sign()

            if (not indexs == -1):

                # Luu ket qua vao list result
                self.result_list.append(indexs)
                self.count_label += 1
                print("counter: ", self.count_label)

            # Doc nhan dien cua 15 anh
            if self.count_label > 10:
                # Lay ky tu xuat hien nhieu nhat
                ct = Counter(self.result_list)
                print(ct)
                print("==================================================")
                # Counter({4: 116, 3: 8, 5: 7})

                # Dat lai so dem va list ket qua
                self.count_label = 0
                self.result_list.clear()

                # Lay gia tri xuat hien nhieu nhat
                most_index = ct.most_common()[0][0]

                # Neu gia tri moi khac voi gia tri cu
                if not most_index == self.last_indexs:

                    # Hien thi va phat am ky tu doc duoc
                    self.last_indexs = most_index
                    str_result =  char_to_word(self.result_string_list[-1], self.labels_char[most_index])
                    print("str result: ", str_result)
                    # bo ky tu cuoi
                    if len(str_result) == 1:
                        self.result_string_list[-1] = str_result[0]
                    else:
                        self.result_string_list[-1] = str_result[0]
                        self.result_string_list.append(str_result[1])
                    print("list string:", self.result_string_list)


                    if self.audio_en:
                        try:
                            text_to_speech(self.labels_detail[most_index])
                        except:
                            print("Loi phat am ky tu trong thu vien")

                    input_string =""
                    for c in self.result_string_list:
                        input_string += c
                    print("input string: ",input_string)
                    self.ui.txtResult.setText(input_string)
                    # Gap dau "." la het cau
                    if self.labels_char[most_index] == ".":
                        # phat ca cau
                        try:
                            text_to_speech(input_string)
                            # self.ui.txtResult.setText(input_string)
                        except:
                            print("Loi phat am ky tu trong thu vien")
                        # Dat lai chuoi
                        self.result_string_list = [""]

            img = cv2.resize(img,(640,370))
            cv2.imshow("picture",img)
            cv2.destroyWindow("picture")
            # print(type(img))

            self.image = QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped() #self.image.shape[1], self.image.shape[0]
            self.ui.txtImage.setPixmap(QtGui.QPixmap.fromImage(self.image))

            # t2 = threading.Thread(target=self.video_display, args=(img,))
            # t2.start()
            # t2.join()
            key = cv2.waitKey(1)
            # self.ui.txtImage.setText("")
            if key == ord("q"):
                break
        self.ui.txtImage.setText("PAUSE!")

    # def video_display(self, img):


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

    def reply_sign(self):
        def show_image(text):
            text_to_speech(text)
            string_split = word_to_char(text)
            self.ui.txtResult.setText(text)
            # show hinh anh
            for char in string_split:
                if char in self.dict_image_name:

                    img_path = dir_path + "/image_show/" + self.dict_image_name[char] + ".png"
                else:
                    img_path = dir_path + "/image_show/" + char + ".png"

                print(char)
                print(img_path)
                img_resize = QtGui.QImage(img_path).scaledToHeight(370)

                self.ui.txtImage.setPixmap(QtGui.QPixmap.fromImage(img_resize))
            #     print("Hien thi anh")
            #     input()
                time.sleep(1.5)
            self.ui.txtResult.setText("")
            self.ui.txtImage.setText("Done!")

        self.ui.btnReply.setEnabled(False)
        self.ui.btnExit.setEnabled(False)
        print("Tra loi hinh anh")
        self.ui.txtImage.setText("Mời bạn nói!")
        # Disable video
        self.video_enable = False
        self.show_video = False
        self.ui.btnStart.setText("Start")

        # Nhận câu nói từ microphone
        try:
            user_talk = listen_audio(self.language).lower()
            get_anwer_ok = False
            if user_talk == "none":
                print("Không nghe được câu nói!")
                text_to_speech("Xin lỗi chúng tôi không nghe được bạn nói gì.")
            else:
                t1 = threading.Thread(target=show_image, args=(user_talk,))
                t1.start()
            self.video_enable = True


        except:
            print("Lỗi khi xử lý câu trả lời")
            self.video_enable = True
        self.ui.btnReply.setEnabled(True)
        self.ui.btnExit.setEnabled(True)
        print("function done")

class HandDetect():
    def __init__(self):
        self.detector = HandDetector(maxHands=2)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.classifier = Classifier(dir_path+ "/model/keras_model.h5", dir_path + "/model/labels.txt")
        self.offset = 20
        self.imgSize = 224
        self.threshold = 0.6
        self.labels =  ['A','B','C','D','E','H','I','O','T','U','Y','L',"^","W","'","`","SP","*"]
        # self.labels =  ['A','B','C','D','_D','E','G','H','I','K','L','M','N','O','P','Q','R','S','T','U','V','X','Y',"^","Rau","'","`","~","*","CACH","Cham", "HI","ILY"]
        # use camera laptop  ###################################################
        self.camera_source = LaptopCamera()

    def read_sign(self):
        # Use camera in laptop  ################################################
        success, img = self.camera_source.cap.read()

        # # Use camera in raspberry pi #########################################
        # img = picam2.capture_array()

        # print("capture")
        imgOutput = img.copy()
        hands, img = self.detector.findHands(img)
        label_result = -1
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
                            imgWhite  = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2RGB)
                            # cv2.imshow("hand1",imgWhite)
                            prediction, index = self.classifier.getPrediction(imgWhite, draw=False)
                            # print(prediction, index)
                            print("index_w: ", index, prediction[index], sep="\t")
                        else:
                            k = self.imgSize/w
                            hCal = math.ceil(k*h)
                            # print(hCal)
                            imgResize = cv2.resize(imgCrop, (self.imgSize, min(self.imgSize, hCal)))
                            imgResizeShape = imgResize.shape
                            # print("img resize shape:", imgResizeShape)
                            hGap = math.ceil((self.imgSize-hCal)/2)
                            imgWhite[hGap:hCal + hGap, :] = imgResize
                            imgWhite  = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2RGB)
                            # cv2.imshow("hand1",imgWhite)

                            prediction, index = self.classifier.getPrediction(imgWhite, draw=False)
                            print("index_h: ", index, prediction[index], sep="/t")

                        if prediction[index] > self.threshold :
                            try:
                                label_result = index
                                cv2.rectangle(imgOutput, (x - self.offset, y - self.offset-50),
                                    (x - self.offset+90, y - self.offset-50+50), (255, 0, 255), cv2.FILLED)
                                cv2.putText(imgOutput, self.labels[index], (x, y -26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
                                cv2.rectangle(imgOutput, (x-self.offset, y-self.offset),
                                            (x + w+self.offset, y + h+self.offset), (255, 0, 255), 4)
                            except:
                                pass
                        else:
                            label_result = -1
                            print("Khong dat nguong")
                        # cv2.imshow("ImageCrop", imgCrop)
                        # cv2.imshow("ImageWhite", imgWhite)
        return imgOutput, label_result

if __name__ == '__main__':
    cv_app = OpenCV_Display()


################################