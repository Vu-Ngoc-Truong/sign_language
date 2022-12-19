import cv2
import time
import numpy as np
import HandTrackingModule as htm
import os
import re
import math
from sklearn import neighbors
import pickle

dir_path = os.path.dirname(os.path.realpath(__file__))
train_dir = os.path.join(dir_path, "image")

detector = htm.handDetector(detectionCon=0.7)

# ############FUNCTION##################
def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

def image_encoding(img):
    """encoding image with 15 dimension

    Args:
        img (image BGR): image have hand from cv2
    Return:
        list() : 15 dimension
    """
    # find hand, return hands and img
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=False)

    # print("lmList:", lmList) # return self.lmList, bbox
    # self.lmList = (id, cx, cy) : id la vi tri diem theo doi tren ban tay ( 0 - 20)
    # [[0, 169, 430], [1, 230, 416], [2, 279, 378], [3, 307, 338], [4, 321, 301], [5, 256, 307], [6, 285, 260], [7, 304, 230], [8, 321, 202], [9, 228, 293], [10, 254, 239], [11, 273, 202], [12, 290, 169], [13, 198, 290], [14, 219, 236], [15, 237, 201], [16, 254, 169], [17, 165, 296], [18, 178, 252], [19, 191, 223], [20, 205, 195]]

    # bbox = xmin, ymin, xmax, ymax
    # print("bbox: ", bbox)
    # (165, 169, 321, 430)

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


    return encoding

##############################################################

def train(train_dir, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    """
    Trains a k-nearest neighbors classifier for face recognition.

    :param train_dir: directory that contains a sub-directory for each known person, with its name.
    :param model_save_path: (optional) path to save model on disk
    :param n_neighbors: (optional) number of neighbors to weigh in classification. Chosen automatically if not specified
    :param knn_algo: (optional) underlying data structure to support knn.default is ball_tree
    :param verbose: verbosity of training
    :return: returns knn classifier that was trained on the given data.
    """

    X = []
    y = []
    # Loop through each person in the training set
    for class_dir in os.listdir(train_dir):
        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue

        # Loop through each training image for the current person
        for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
            img = cv2.imread(img_path)
            img_encoding = image_encoding(img)
            if len(img_encoding) > 0:
                X.append(img_encoding)
                y.append(class_dir)

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


# Predict
def predict(encoding, knn_clf=None, model_path=None, distance_threshold=0.4):
    """
    Recognizes faces in given image using a trained KNN classifier

    :param image :  encoding of image
    :param knn_clf: (optional) a knn classifier object. if not specified, model_save_path must be specified.
    :param model_path: (optional) path to a pickled knn classifier. if not specified, model_save_path must be knn_clf.
    :param distance_threshold: (optional) distance threshold for face classification. the larger it is, the more chance
            of mis-classifying an unknown person as a known one.
    :return: a list of names and face locations for the recognized faces in the image: [(name, bounding box), ...].
        For faces of unrecognized persons, the name 'unknown' will be returned.
    """

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

    # Load a trained KNN model (if one was passed in)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    # encoding = image_encoding(image)
    # If no faces are found in the image, return an empty result.
    if len(encoding) == 0:
        return []

    # Use the KNN model to find the best matches for the test face
    _distances = knn_clf.kneighbors([encoding], n_neighbors=1)
    closest_distances = _distances[0][0][0]
    predict = knn_clf.predict([encoding])
    print("knn predict:", predict)
    # are_matches = closest_distances[0][i][0] <= distance_threshold
    # Predict classes and remove classifications that aren't within the threshold
    return predict, closest_distances
