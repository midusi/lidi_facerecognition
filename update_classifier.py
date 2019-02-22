import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.externals import joblib
from sklearn.metrics import classification_report, confusion_matrix

import settings
from backend import facedb

import backend.train_classifier as tc


if __name__ == '__main__':
    data = np.load(settings.training_data_file)
    x_train, y_train = data["x_train"], data["y_train"]
    x_train, y_train = data["x_train"], data["y_train"]

    persondb = facedb.load_persondb(settings.face_database_path)
    y_pred,model=tc.update(settings,persondb,x_train, y_train)
    tc.plot_classification_results(y_train,y_pred,persondb)