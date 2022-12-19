import cv2
from cvzone.HandTrackingModule import HandDetector
# from cvzone.ClassificationModule import Classifier
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
from image_train_knn import image_encoding, predict
import HandTrackingModule as htm

#######################
dir_path = os.path.dirname(os.path.realpath(__file__))

# select camera source
use_picam2 = True

if use_picam2:
    # Use raspberry pi camera #########################################
    from picamera2 import Picamera2, Preview

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 370)}))
    picam2.start()

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
        self.have_image = False
        self.have_img_hand = False
        self.cv_image = None
        self.hand_image = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.display_video)
        self.fps = 0
        self.pre_time = time.time()

        self.timer_hand = QtCore.QTimer()
        self.timer_hand.timeout.connect(self.loop)

        if not use_picam2:
            # use camera laptop  ###################################################
            self.camera_source = LaptopCamera()

        self.ui.btnStart.clicked.connect(self.start_stop)
        self.ui.btnExit.clicked.connect(self.exit_app)
        self.ui.rbt_audio_en.clicked.connect(self.mute)
        self.ui.btnReply.clicked.connect(self.reply_sign)
        self.hand_detect = HandDetect()
        self.language = 'vi'
        self.video_enable = True
        self.last_indexs = ""

        self.count_threshold = 20  # số ảnh cần đọc được để quyết định
        self.labels_char =    ['a','b','c','d','đ','e','h','i','l','m','n','o','t','u','v','x','y',"^","w","'","`"," "]
        # self.labels_speech =  ['A','B','C','D','Đ','E','H','I','L','M','N','O','T','U','V','X','Y',"Mũ","Râu","Sắc","Huyền","Cách"]
        self.dict_labels_word = {"_d":'đ', 'sp':" ", "hi":""}
        self.dict_labels_speech = {"'": "sắc", "`": "huyền","?": "hỏi", "~": "ngã", "*": "nặng", "w": "râu", "^": "mũ", "_d":"đ", 'sp':"cách", "hi":"xin chào"}
        self.dict_image_name = {"'": "sac", "`": "huyen","?": "hoi", "~": "nga", "*": "nang", "w": "rau", "^": "mu", "đ":"_d"}

    def display_video(self):
        global use_picam2
        if not use_picam2:
            # Use camera in laptop  ################################################
            success, img = self.camera_source.cap.read()
            if not success:
                print("Can't read video!")
                return

        if use_picam2:
            # Use camera in raspberry pi #########################################
            img = picam2.capture_array()

        self.fps += 1
        self.cv_image = img
        self.have_image = True
        # print(self.cv_image.shape)
        img_display = self.cv_image
        if self.have_img_hand:
            img_display = self.hand_image
        img_display = cv2.resize(img_display,(640,370))
        self.image = QtGui.QImage(img_display, img_display.shape[1], img_display.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped() #self.image.shape[1], self.image.shape[0]
        self.ui.txtImage.setPixmap(QtGui.QPixmap.fromImage(self.image))
        self.have_img_hand = False
        # key = cv2.waitKey(1)

        # Calculating the fps
        if(time.time() - self.pre_time) >= 1.0:
            # print("fps = {}".format(self.fps))
            self.fps = 0
            self.pre_time = time.time()

    def start_stop(self):
        self.show_video = not self.show_video
        if self.show_video:
            self.ui.btnStart.setText("Stop")
            self.timer.start()
            self.timer_hand.start()
            self.prev_frame_time = time.time()
            self.result_list = []
            self.count_label = 0
            self.result_string = ""
            self.result_string_list = [""]
        else:
            # Dung doc tu camera
            self.ui.btnStart.setText("Start")
            self.last_indexs = ""
            self.timer.stop()
            self.timer_hand.stop()
            self.ui.txtImage.setText("PAUSE!")
            self.have_image = False

    def loop(self):
        # print("loop start")
        if not (self.video_enable and self.have_image):
            print("not display video")
            return

        if self.exit:
            print("exit cmd")
            self.timer.stop()
            self.timer_hand.stop()

        indexs = ""
        # print(self.cv_image.shape)
        try:
            self.hand_image, indexs = self.hand_detect.read_sign(self.cv_image)
            self.have_image = False
            self.have_img_hand = True
            # print("indexs: ", indexs)
            # self.image = QtGui.QImage(self.hand_image, self.hand_image.shape[1], self.hand_image.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped() #self.image.shape[1], self.image.shape[0]
            # self.ui.txtImage.setPixmap(QtGui.QPixmap.fromImage(self.image))
            if (not indexs == ""):
                # Luu ket qua vao list result
                self.result_list.append(indexs)
                self.count_label += 1
                # print("counter: ", self.count_label)

            # Doc nhan dien cua 15 anh
            if self.count_label > self.count_threshold:
                # Lay ky tu xuat hien nhieu nhat
                ct = Counter(self.result_list)
                print(ct)
                print("==================================================")
                # Counter({"A": 116, "B": 8, "C": 7})

                # Dat lai so dem va list ket qua
                self.count_label = 0
                self.result_list.clear()

                # Lay gia tri xuat hien nhieu nhat
                most_index = ct.most_common()[0][0]
                # doi index ra chu thuong va dang ky tu cho word
                most_index = most_index.lower()
                if most_index in self.dict_labels_word:
                    most_index = self.dict_labels_word[most_index]
                # Neu gia tri moi khac voi gia tri cu
                if not most_index == self.last_indexs:

                    # Hien thi va phat am ky tu doc duoc
                    self.last_indexs = most_index
                    str_result =  char_to_word(self.result_string_list[-1], most_index)
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
                            indexs_speech = self.dict_labels_speech[most_index] if most_index in self.dict_labels_speech else most_index
                            text_to_speech(indexs_speech)
                        except:
                            print("Loi phat am ky tu trong thu vien")

                    input_string =""
                    for c in self.result_string_list:
                        input_string += c
                    print("input string: ",input_string)
                    self.ui.txtResult.setText(input_string)
                    # Gap dau "." la het cau
                    if (most_index == " ") or len(self.result_string_list) > 10:
                        # phat ca cau
                        try:
                            text_to_speech(input_string)
                            self.ui.txtResult.setText("")
                            # self.ui.txtResult.setText(input_string)
                        except:
                            print("Loi phat am ky tu trong thu vien")
                        # Dat lai chuoi
                        self.result_string_list = [""]
        except:
            # print("Loi khi phat hien ban tay")
            pass

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
                time.sleep(1.0)
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
        global use_picam2
        self.detector = htm.handDetector(maxHands=2, detectionCon=0.7)
        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.model_path =  os.path.join(dir_path,"model", "trained_knn_model.clf")
        # self.classifier  = Classifier(os.path.join(dir_path,"model", "keras_model.h5"),  os.path.join(dir_path,"model", "labels.txt"))
        # self.classifier1 = Classifier(os.path.join(dir_path,"model", "keras_model1.h5"), os.path.join(dir_path,"model", "labels1.txt"))
        # self.classifier2 = Classifier(os.path.join(dir_path,"model", "keras_model2.h5"), os.path.join(dir_path,"model", "labels2.txt"))
        # self.classifier3 = Classifier(os.path.join(dir_path,"model", "keras_model3.h5"), os.path.join(dir_path,"model", "labels3.txt"))
        # self.list_classifier = [self.classifier, self.classifier1, self.classifier2, self.classifier3]

        self.offset = 20
        self.imgSize = 224
        self.threshold = 0.99
        self.dict_labels_folder = {"HI":"Hi","CACH":'SP','CHAM':'.', 'SAC':"'", 'HUYEN':"`", 'HOI':"?", 'NGA':"~",'NANG':'*', 'MU':"^",'RAU':'W'}
        # self.labels =  ['A','B','C','D','E','H','I','O','T','U','Y','L',"^","W","'","`","SP","*"]
        # self.labels =  ['A','B','C','D','_D','E','H','I','L','M','N','O','T','U','V','X','Y',"^","W","'","`","SP"]
        # self.labels  =  ['A','B','C','D']
        # self.labels1 =  ['_D','E','H','I','L','M']
        # self.labels2 =  ['N', 'O','T','U','V','X']
        # self.labels3 =  ['Y',"^","W","'","`","SP"]
        # self.list_labels = [self.labels, self.labels1, self.labels2, self.labels3]
        # print("hand detect init done")

    def read_sign(self, img):
        # print("capture")
        # print("have image")
        imgOutput = img.copy()
        # print("read sign: ", img.shape)
        hands, img = self.detector.findHands(img)
        label_result = ""
        dict_result = {}
        # print("find hand")
        if hands:
            for _hand in hands:
                if _hand['type'] == 'Right':
                    # print(_hand)
                    hand = _hand
                    x, y, w, h = hand['bbox']
                    # print(hand)
                    # encoding = image_encoding(img)

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
                        if (list_point[0][0] >= list_point[1][0]):
                            encoding.append(1)
                        else:
                            encoding.append(-1)

                        if (list_point[0][1] >= list_point[1][1]):
                            encoding.append(1)
                        else:
                            encoding.append(-1)
                    print("enc_img", encoding)
                    # prediction image ####################################
                    predictions, distance = predict(encoding, model_path= self.model_path)
                    print(predictions)
                    print( distance)

                    # imgWhite = np.ones((self.imgSize, self.imgSize, 3), np.uint8)* 255
                    # if (x - self.offset) > 0 and (y- self.offset) > 0:
                    #     haveHand = True
                    #     imgCrop = img[y- self.offset:y+ h+ self.offset, x-self.offset:x+ w+ self.offset]
                    #     imgCropShape = imgCrop.shape
                    #     # print("img crop shape", imgCropShape)
                    #     # print(x,y,w,h)
                    #     aspectRatio = h/w

                    #     if aspectRatio > 1:
                    #         k = self.imgSize/h
                    #         wCal = math.ceil(k*w)
                    #         # print(wCal)
                    #         imgResize = cv2.resize(imgCrop, (min(wCal,self.imgSize), self.imgSize))
                    #         # imgResizeShape = imgResize.shape
                    #         # print("img resize shape:", imgResizeShape)
                    #         wGap = math.ceil((self.imgSize-wCal)/2)
                    #         imgWhite[:, wGap:wCal + wGap] = imgResize
                    #         # imgWhite  = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2RGB)
                    #         # cv2.imshow("hand1",imgWhite)

                    #         # predict model
                    #         for num in range(len(self.list_classifier)):
                    #             classifier = self.list_classifier[num]
                    #             prediction, index = classifier.getPrediction(imgWhite, draw=False)
                    #             # print(prediction, index)
                    #             # print("index_w: ", index, prediction[index], sep="  ")
                    #             if prediction[index] > self.threshold :
                    #                 dict_result[self.list_labels[num][index]] = prediction[index]

                    #     else:
                    #         k = self.imgSize/w
                    #         hCal = math.ceil(k*h)
                    #         # print(hCal)
                    #         imgResize = cv2.resize(imgCrop, (self.imgSize, min(self.imgSize, hCal)))
                    #         # imgResizeShape = imgResize.shape
                    #         # print("img resize shape:", imgResizeShape)
                    #         hGap = math.ceil((self.imgSize-hCal)/2)
                    #         imgWhite[hGap:hCal + hGap, :] = imgResize
                    #         # imgWhite  = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2RGB)
                    #         # cv2.imshow("hand1",imgWhite)

                    #         # predict model
                    #         for num in range(len(self.list_classifier)):
                    #             classifier = self.list_classifier[num]
                    #             prediction, index = classifier.getPrediction(imgWhite, draw=False)
                    #             # print(prediction, index)
                    #             # print("index_w: ", index, prediction[index], sep="  ")
                    #             if prediction[index] > self.threshold :
                    #                 dict_result[self.list_labels[num][index]] = prediction[index]

                    label_result = ""
                    if distance < 55:
                        # print(distance)
                        label_result = predictions[0]
                        if label_result in self.dict_labels_folder:
                            label_result = self.dict_labels_folder[label_result]
                        try:
                            # max_result = 0
                            # for label in dict_result:
                            #     if dict_result[label] >  max_result:
                            #         label_result = label
                            #         max_result = dict_result[label]
                            print("ky tu hop le la: ____________ ", label_result)
                            cv2.rectangle(imgOutput, (x - self.offset, y - self.offset-50),
                                (x - self.offset+90, y - self.offset-50+50), (255, 0, 255), cv2.FILLED)
                            # cv2.putText(imgOutput, self.labels[index], (x, y -26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
                            cv2.putText(imgOutput, label_result, (x, y -26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
                            cv2.rectangle(imgOutput, (x-self.offset, y-self.offset),
                                        (x + w+self.offset, y + h+self.offset), (255, 0, 255), 4)
                        except:
                            pass
                    else:
                        print("Khong dat nguong")
                # print("indexs: ", label_result)
        # cv2.imshow("hand",imgWhite)
        # cv2.waitKey(1)
        return imgOutput, label_result

if __name__ == '__main__':
    cv_app = OpenCV_Display()


################################