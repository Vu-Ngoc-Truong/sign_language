import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import time

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=2)
classifier = Classifier("model/keras_model.h5", "model/labels.txt")
offset = 20
imgSize = 300
folder = "data/D"
counter = 0
haveHand = False
threshold = 0.95
labels =  ["A", "B", "C", "D", "E", "G", "H", "I", "L", "M", "N", "ILY", "^", "HUYEN", "SAC","_D", "T", "O"]

while True:
    success, img = cap.read()
    imgOutput = img.copy()
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
                        imgResize = cv2.resize(imgCrop, (min(wCal,imgSize), imgSize))
                        imgResizeShape = imgResize.shape
                        # print("img resize shape:", imgResizeShape)
                        wGap = math.ceil((imgSize-wCal)/2)
                        imgWhite[:, wGap:wCal + wGap] = imgResize
                        prediction, index = classifier.getPrediction(imgWhite, draw=False)
                        print(prediction, index)
                    else:
                        k = imgSize/w
                        hCal = math.ceil(k*h)
                        # print(hCal)
                        imgResize = cv2.resize(imgCrop, (imgSize, min(imgSize, hCal)))
                        imgResizeShape = imgResize.shape
                        # print("img resize shape:", imgResizeShape)
                        hGap = math.ceil((imgSize-hCal)/2)
                        imgWhite[hGap:hCal + hGap, :] = imgResize
                        prediction, index = classifier.getPrediction(imgWhite, draw=False)

                    if prediction[index] > threshold :
                        try:
                            cv2.rectangle(imgOutput, (x - offset, y - offset-50),
                                (x - offset+90, y - offset-50+50), (255, 0, 255), cv2.FILLED)
                            cv2.putText(imgOutput, labels[index], (x, y -26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
                            cv2.rectangle(imgOutput, (x-offset, y-offset),
                                        (x + w+offset, y + h+offset), (255, 0, 255), 4)
                        except:
                            pass

                    # cv2.imshow("ImageCrop", imgCrop)
                    # cv2.imshow("ImageWhite", imgWhite)


    cv2.imshow("Sign Language", imgOutput)
    key = cv2.waitKey(1)

    if key == ord("q"):
        break