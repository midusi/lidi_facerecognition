import sys
from backend import facedb

from backend.face_recognizer import FaceEmbeddingClassifier, FaceRecognizer

from PyQt5.QtCore import (QThread, Qt, pyqtSignal)
from PyQt5.QtWidgets import QFrame, QApplication, QHBoxLayout, QVBoxLayout
from frontend.capture_widget import CaptureWidget
from frontend.topbar_widget import TopBarWidget, BottomBarWidget
from frontend.retrain_worker import RetrainWorker
import settings
import logging

from frontend.recognition_worker import RecognitionWorker
from frontend.widgets.persons import TrackedPersonsWidget
from frontend.widgets.last_seen import LastSeenWidget
from frontend.greeting import  GreetingWorker


class RecognitionAndCaptureWidget(QFrame):
    def __init__(self,person_db):
        super().__init__()
        self.capture_widget = CaptureWidget(person_db)
        # # RECOGNITION INFO

        self.persons_widget = TrackedPersonsWidget(person_db, "")
        self.last_seen_widget = LastSeenWidget(person_db, "Últimas personas")

        self.recognition_layout = QVBoxLayout()
        self.recognition_layout.addWidget(self.persons_widget)
        self.recognition_layout.addWidget(self.last_seen_widget)
        self.recognition_layout.setContentsMargins(5, 5, 5, 5)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(self.capture_widget)
        main_layout.addLayout(self.recognition_layout)

        self.setLayout(main_layout)

        self.setStyleSheet("RecognitionAndCaptureWidget {"
                           "background-color:#332222;"
                           "}")



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
        #RETRAIN
        # self.retrain_thread = QThread()
        # self.retrain_worker = RetrainWorker(settings)
        # self.retrain_worker.moveToThread(self.retrain_thread)

        # self.retrain_signal.connect(self.retrain_worker.run)
        # self.retrain_worker.retrained.connect(self.update_model)

        # GREETING
        self.greeting_worker = GreetingWorker(self.person_db, settings)
        self.greeting_thread = QThread()
        self.greeting_worker.moveToThread(self.greeting_thread)

        # CAPTURE
        # self.capture_worker = CaptureWorker(self.face_recognizer, settings, self.person_db)
        #
        # self.capture_thread=QThread()
        # self.capture_worker.moveToThread(self.capture_thread)
        # self.capture_thread.started.connect(self.capture_worker.run)
        # self.capture_worker.update_capture.connect(self.capture_widget.update_capture)

        self.recognition_thread= QThread()
        self.recognition_worker  = RecognitionWorker(self.face_recognizer, settings, self.person_db)
        self.recognition_worker.moveToThread(self.recognition_thread)
        recognition_worker = self.recognition_worker
        self.recognition_thread.started.connect(self.recognition_worker.runHttp)

        recognition_worker.server_status_signal.connect(self.bottom_bar.update_server_status)

        recognition_worker.persons_detected_signal.connect(self.recognition_and_capture_widget.persons_widget.update_persons)
        recognition_worker.persons_detected_signal.connect(self.recognition_and_capture_widget.last_seen_widget.update_persons)
        recognition_worker.persons_detected_signal.connect(self.recognition_and_capture_widget.capture_widget.update_person_detections)
        recognition_worker.persons_detected_signal.connect(self.greeting_worker.update_objects_tracked)

        #START
        # self.capture_thread.start()
        #self.retrain_thread.start()
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

