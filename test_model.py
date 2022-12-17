import tensorflow as tf
import numpy as np
import keras
from PIL import Image
import glob
from cvzone.ClassificationModule import Classifier
from collections import Counter
import cv2
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(dir_path, "model")
classifier = Classifier(os.path.join(model_path,"keras_model1.h5"), os.path.join(model_path,"labels1.txt"))
# model =  keras.models.load_model("model/my_h5_model.h5")

def read_labels(labelsPath):
    # Read labels
    labels_path = labelsPath
    if labels_path:
        label_file = open(labels_path, "r")
        list_labels = []
        for line in label_file:
            stripped_line = line.strip()
            list_labels.append(stripped_line)
        label_file.close()
        print(list_labels)
        print(list_labels[2])
        print(str(list_labels[2]).split(" ")[1])

    else:
        print("No Labels Found")



# read_labels("model/labels.txt")


data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
# list_index = [4, 4, 4, 4, 4, 4, 4, 5, 4, 4, 4, 5, 4, 4, 4, 4, 3, 4, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 4, 3, 4, 4, 4, 3, 4, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 3, 4, 4, 4, 4, 4, 4, 4, 5, 3, 4, 4, 4, 4, 5, 4, 4, 4, 4, 4]
list_index = []
for file_name in glob.glob(r'test/E/*.jpg'): #assuming all jpg

    imgTest = np.array(Image.open(file_name))
    # print(imgTest.shape)
    print(file_name)
    # imgTest = cv2.imread(file_name)
    # cv2.imshow("Image",imgTest)
    # cv2.waitKey(1)
    # imgTest = cv2.cvtColor(imgTest,cv2.COLOR_BGR2RGB)
    prediction, index = classifier.getPrediction(imgTest, draw=False)
    # print(index)
    list_index.append(index)

    # image_array = np.asarray(imgTest)

    # Normalize the image
    # normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    # # Load the image into the array
    # data[0] = image_array
    # print(model.predict(data))

print(list_index)
print(len(list_index))
ct = Counter(list_index)
print(ct)
# Counter({2: 58, 15: 21, 27: 13, 13: 13, 26: 12, 22: 1, 21: 1, 30: 1})
print("most: ", ct.most_common()[0][0])
# most:  2
cv2.destroyAllWindows()
