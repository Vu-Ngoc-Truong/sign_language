import tensorflow as tf
import numpy as np
import keras
from PIL import Image
import glob
from cvzone.ClassificationModule import Classifier

classifier = Classifier("model/my_h5_model.h5", "model/labels.txt")
# model =  keras.models.load_model("model/my_h5_model.h5")

data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
for file_name in glob.glob(r'data/A/*.jpg'): #assuming all jpg

    imgTest = np.array(Image.open(file_name))
    print(file_name)
    prediction, index = classifier.getPrediction(imgTest, draw=False)
    print(prediction, index)

    # image_array = np.asarray(imgTest)

    # Normalize the image
    # normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    # # Load the image into the array
    # data[0] = image_array
    # print(model.predict(data))
