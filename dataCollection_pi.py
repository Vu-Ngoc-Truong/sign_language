import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time
from picamera2 import Picamera2, Preview

picam2 = Picamera2()
# picam2.start_preview(Preview.QTGL)
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (680, 400)}))
picam2.start()

detector = HandDetector(maxHands=2)
offset = 20
imgSize = 224
folder = "data/E"
counter = 0
haveHand = False
label = ["A", "B", "C", "D", "_D", "E"]

while True:
    img = picam2.capture_array()

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
                        k = imgSize/h
                        wCal = math.ceil(k*w)
                        # print(wCal)
                        if wCal < imgSize:
                            haveHand = True
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

    cv2.imshow("Picture", img)
    key = cv2.waitKey(1)
    if key == ord("s") and haveHand:
        counter +=1
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', imgWhite)
        print(counter)
    haveHand = False

    if key == ord("q"):
        break