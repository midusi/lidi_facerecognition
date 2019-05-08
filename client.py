import sys
import settings
import logging

from backend import facedb
from backend.face_recognizer import FaceEmbeddingClassifier, FaceRecognizer

from PyQt5.QtCore import (QThread, Qt, pyqtSignal)
from PyQt5.QtWidgets import QFrame, QApplication, QVBoxLayout

from frontend.topbar_widget import TopBarWidget, BottomBarWidget
from frontend.recognition_and_capture import RecognitionAndCaptureWidget

from frontend.recognition_worker import RecognitionWorker
from frontend.greeting import GreetingWorker




class App(QFrame):

    retrain_signal=pyqtSignal()

    def __init__(self,face_recognizer,person_db):
        super().__init__()
        self.person_db=person_db
        self.title = settings.gui.application_name
        self.setObjectName('App')
        self.face_recognizer=face_recognizer
        self.initUI()



    def initUI(self):

        self.topbar=TopBarWidget()
        self.topbar.layout().setAlignment(Qt.AlignTop)


        # CONTAINER
        self.container = QVBoxLayout()
        self.container.addWidget(self.topbar)
        # self.container.addStretch()
        self.recognition_and_capture_widget=RecognitionAndCaptureWidget(person_db)
        self.container.addWidget(self.recognition_and_capture_widget)
        self.container.addStretch()

        self.bottom_bar=BottomBarWidget()
        self.container.addWidget(self.bottom_bar)


        self.setLayout(self.container)
        self.container.setSpacing(0)
        self.container.setContentsMargins(0, 0, 0, 0)

        self.initialize_threads()
        self.set_window_style()

    def set_window_style(self):
        # self.setWindowTitle(settings.application_name)
        self.showFullScreen()
        self.setStyleSheet("App {background-color: black;"
                           "margin:0px;"
                           "padding:0px;"
                           "}")
        self.autoFillBackground()
        self.setContentsMargins(0, 0, 0, 0)

    def initialize_threads(self):
        # GREETING
        self.greeting_worker = GreetingWorker(self.person_db, settings)
        self.greeting_thread = QThread()
        self.greeting_worker.moveToThread(self.greeting_thread)

        self.recognition_thread= QThread()
        self.recognition_worker  = RecognitionWorker(self.face_recognizer, settings, self.person_db)
        self.recognition_worker.moveToThread(self.recognition_thread)
        self.recognition_thread.started.connect(self.recognition_worker.runHttp)

        recognition_worker = self.recognition_worker
        recognition_worker.server_status_signal.connect(self.bottom_bar.update_server_status)
        recognition_worker.persons_detected_signal.connect(self.recognition_and_capture_widget.update_tracked_objects)
        recognition_worker.persons_detected_signal.connect(self.greeting_worker.update_tracked_objects)

        #START
        self.greeting_thread.start()
        self.recognition_thread.start()


    def update_model(self,data):
        model, persondb=data
        self.face_recognizer.update_face_classification_model(model)
        self.persons_widget.update_persondb(persondb)
        self.last_seen_widget.update_persondb(persondb)
        self.capture_widget.update_persondb(persondb)
        self.greeting_worker.update_person_db(persondb)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R:
            # here accept the event and do something
            #self.retrain_signal.emit()
            event.accept()
        else:
            event.ignore()



if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    person_db=facedb.load_persondb(settings.face_database_path)

    face_classifier=FaceEmbeddingClassifier(settings)
    face_recognizer=FaceRecognizer(settings,face_classifier)
    app = QApplication(sys.argv)
    ex = App(face_recognizer,person_db)
    ex.show()
    sys.exit(app.exec_())

