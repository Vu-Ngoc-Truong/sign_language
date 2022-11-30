import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=2)
offset = 20
offset1 = 10
off_gap = math.ceil(offset/2)
imgSize = 224
folder = "data/T"
counter = 0
haveHand = False
labels = ["A", "B", "C", "D", "_D", "E"]

while True:
    success, img = cap.read()
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
                    imgCrop = img[y- offset:y+ h+ offset, x-offset:x+ w+ offset]
                    imgCropShape = imgCrop.shape
                    # print("img crop shape", imgCropShape)
                    # print(x,y,w,h)
                    aspectRatio = h/w
                    if aspectRatio > 1:
                        k = (imgSize - offset1)/h
                        wCal = math.ceil(k*w)
                        # print(wCal)
                        if wCal <= imgSize:
                            haveHand = True
                            imgResize = cv2.resize(imgCrop, (wCal, imgSize - offset1))
                            imgResizeShape = imgResize.shape
                            # print("img resize shape:", imgResizeShape)
                            wGap = math.ceil((imgSize - wCal)/2)
                            imgWhite[ :imgSize - offset1, wGap:wCal + wGap] = imgResize
                    else:
                        k = (imgSize -offset1)/w
                        hCal = math.ceil(k*h)
                        # print(hCal)
                        if hCal <= imgSize:
                            haveHand = True
                            imgResize = cv2.resize(imgCrop, (imgSize -offset1 , hCal))
                            imgResizeShape = imgResize.shape
                            # print("img resize shape:", imgResizeShape)
                            hGap = math.ceil((imgSize - hCal)/2)
                            imgWhite[hGap:hCal + hGap, :imgSize-offset1] = imgResize


                    # cv2.imshow("Picture crop", imgCrop)
                cv2.imshow("Picture White", imgWhite)

    cv2.imshow("Picture", img)
    key = cv2.waitKey(1)
    if key == ord("s") and haveHand:
        counter +=1
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', imgWhite)
        print(counter)
    haveHand = False

    if key == ord("q"):
        break