import tensorflow as tf
import numpy as np
from tensorflow import keras
from PIL import Image
import glob
import time

training_images = []
training_labels = []
labels =  ["A", "B", "C", "D", "_D", "E"]
file_label = 0

for file_name in glob.glob(r'data/*/*.jpg'): #assuming all jpg
    str_label = file_name.split('/')[1]
    id = int()
    for id in range(len(labels)):
        if str_label == labels[id] :
            file_label = id
    im = Image.open(file_name)
    im_arr = np.array(im)
    normalized_image_array = (im_arr.astype(np.float32) / 127.0) - 1
    training_images.append(normalized_image_array)
    training_labels.append(file_label)
    # print(file_label)
    # im.show(file_label)
    # time.sleep(2)
print(len(training_images))
print(len(training_labels))
# print(training_images[0].shape)
training_images = np.array(training_images)
training_labels = np.array(training_labels)


model = keras.models.Sequential()
model.add(keras.layers.Flatten())
model.add(keras.layers.Dense(128, activation='relu'))
model.add(keras.layers.Dense(len(labels), activation='softmax'))

model.compile(optimizer = tf.keras.optimizers.Adam(),
                loss = 'sparse_categorical_crossentropy',
                metrics=['accuracy'])

model.fit(training_images, training_labels, epochs=10)
model.save("model/my_h5_model.h5")
# imgTest = np.array(Image.open("data1/test/1.jpg"))
# model.predict(imgTest)