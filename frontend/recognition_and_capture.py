from frontend.widgets.persons import TrackedPersonsWidget
from frontend.widgets.last_seen import LastSeenWidget
from frontend.capture_widget import CaptureWidget
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import (Qt,pyqtSlot)

class RecognitionAndCaptureWidget(QFrame):
    def __init__(self,person_db):
        super().__init__()
        self.capture_widget = CaptureWidget(person_db)
        # # RECOGNITION INFO

        self.persons_widget = TrackedPersonsWidget(person_db, "Recientes")
        #self.last_seen_widget = LastSeenWidget(person_db, "Recientes")

        self.recognition_layout = QVBoxLayout()
        self.recognition_layout.addWidget(self.persons_widget)
        #self.recognition_layout.addWidget(self.last_seen_widget)
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

    @pyqtSlot(object,object)
    def update_tracked_objects(self,tracked_objects,image):
        self.persons_widget.update_tracked_objects(tracked_objects,image)
        self.capture_widget.update_tracked_objects(tracked_objects,image)
