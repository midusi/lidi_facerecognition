from PyQt5.QtCore import (QThread, Qt, pyqtSignal,pyqtSlot,QObject)

from backend import train_classifier,facedb


class RetrainWorker(QObject):

    retrained = pyqtSignal(object)

    def __init__(self,settings):
        super().__init__()
        self.settings=settings

    @pyqtSlot()
    def run(self):
        print("Updating db...")
        persondb, x_train, y_train =facedb.update(self.settings)
        y_pred, model = train_classifier.update(self.settings, persondb, x_train, y_train)
        print("Done")
        self.retrained.emit([model,persondb])