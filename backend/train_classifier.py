import matplotlib.pyplot as plt
import numpy as np
from sklearn import svm
from sklearn.externals import joblib
from sklearn.metrics import classification_report, confusion_matrix

import settings
from backend import facedb


def plot_classification_results(y_train,y_pred,person_information):
    report = classification_report(y_train, y_pred)
    print(report)

    mat=confusion_matrix(y_train,y_pred)

    f,((a1,a2),(a3,a4))=plt.subplots(2,2)
    classes=y_train.astype("int").max()
    class_count= np.bincount(y_train.astype("int"))
    indices=np.arange(classes+1)

    font_size=8
    person_names=[person_information[i].lastname for i in sorted(person_information.keys())]
    width=0.3
    a1.bar(indices,class_count,width)
    a1.set_xticks(indices+ width / 2)
    a1.set_xticklabels(person_names, rotation='vertical',fontsize=font_size)
    #a2.plot(y_train)
    a1.set_title("Class Histogram")

    n=y_train.shape[0]
    sigma_jitter=0.2
    a2.scatter(y_train+np.random.normal(0,sigma_jitter,n),y_pred+np.random.normal(0,sigma_jitter,n),s=2,c=y_train)
    a2.set_title("Ground truth vs predictions")
    a2.set_xticks(indices)
    a2.set_xticklabels(person_names, rotation='vertical',fontsize=font_size)
    a2.set_yticks(indices)
    a2.set_yticklabels(person_names,fontsize=font_size)

    a3.imshow(mat)
    a3.set_title("confusion matrix")
    a3.set_xticks(indices)
    a3.set_xticklabels(person_names, rotation='vertical',fontsize=font_size)
    a3.set_yticks(indices)
    a3.set_yticklabels(person_names,fontsize=font_size)
    plt.subplots_adjust(wspace=0.2, hspace=0.4)

    plt.show()

def train_face_classifier(x_train,y_train,persondb ):
    n,d=x_train.shape
    print("Training classifier from encodings.")
    person_names=[p.name for p in persondb .values()]
    print(f"Persons in dataset: {person_names}")
    print(f"{n} sample image files")
    print(f"x.shape: ",x_train.shape," y.shape: ",y_train.shape)

    # model=neighbors.KNeighborsClassifier(n_neighbors=5)#, algorithm='ball_tree')
    # model= svm.LinearSVC(class_weight="balanced")
    model= svm.SVC(class_weight="balanced",kernel="linear",probability=True)
    model.fit(x_train,y_train)

    y_pred=model.predict(x_train)
    accuracy= (y_train==y_pred).mean()

    print("Final accuracy:",accuracy)

    return y_pred,model


def update(settings,persondb,x_train, y_train):
    y_pred, model = train_face_classifier(x_train, y_train, persondb)

    joblib.dump(model, settings.model_path)
    return y_pred,model

if __name__ == '__main__':
    data = np.load(settings.training_data_file)
    x_train, y_train = data["x_train"], data["y_train"]
    x_train, y_train = data["x_train"], data["y_train"]

    persondb = facedb.load_persondb(settings.face_database_path)
    y_pred,model=update(settings,persondb,x_train, y_train)
    plot_classification_results(y_train,y_pred,persondb)