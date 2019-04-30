from PyQt5.QtCore import (QThread, Qt, pyqtSignal,pyqtSlot)

from PyQt5.QtWidgets import QFrame,QWidget,QLabel,QApplication, QHBoxLayout, QVBoxLayout,QGraphicsDropShadowEffect,\
    QSizePolicy
from PyQt5 import QtGui,QtCore,QtWidgets
import cv2
from PIL import Image
from backend.tracking import TrackingStatus

from .person import PersonWidget,SimplePersonWidget


class PersonsWidget(QFrame):
    def __init__(self,person_db,title,parent=None,orientation="vertical"):
        super().__init__(parent=parent)
        self.person_db=person_db
        self.title=title
        self.main_layout=self.generate_main_layout()

        self.title=self.generate_title(title)
        self.main_layout.addChildWidget(self.title)

        self.persons_detected_layout=self.generate_persons_detected_layout(orientation)

        self.setStyleSheet("PersonsWidget {width:100%;"
                           # "margin-top:30px;"
                           "background-color:#333333;"
                            "background-color:#332222;"
                           "padding:0px;"
                           "}")

        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        sp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sp.setHorizontalStretch(1)
        sp.setVerticalStretch(1)
        self.setSizePolicy(sp)
        self.main_layout.addChildLayout(self.persons_detected_layout)
        self.setLayout(self.main_layout)

    def generate_persons_detected_layout(self,orientation):
        if orientation=="vertical":
            persons_detected_layout = QVBoxLayout()
        else:
            persons_detected_layout = QHBoxLayout()

        persons_detected_layout.setAlignment(Qt.AlignTop)
        persons_detected_layout.setSpacing(0)
        #persons_detected_layout.setContentsMargins(10, 10, 10, 10)

        return persons_detected_layout

    def generate_main_layout(self):
        main_layout = QVBoxLayout()

        return main_layout

    def generate_title(self,title):
        title_layout = QLabel()
        title_layout.setStyleSheet("QLabel {font-size:24px;}")
        title_layout.setText(title)
        return title_layout

    def update_persondb(self,persondb):
        self.person_db=persondb

    def remove_all_widgets(self, layout):
        for i in reversed(range(layout.count())):
            widgetToRemove = layout.itemAt(i).widget()
            # remove it from the layout list
            layout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

class LastSeenWidget(PersonsWidget):
    def __init__(self, person_db, title, last_seen_limit=5, parent=None):
        super().__init__(person_db,title,parent=parent)
        self.last_seen=[]
        self.last_seen_ids=[]

        self.last_seen_limit=last_seen_limit

    def check_new_persons(self,tracked_objects):
        new_persons={}
        for tracked_object in tracked_objects:
            if tracked_object.get_status() == TrackingStatus.Recognized:
                id=tracked_object.class_id()
                person = self.person_db[id]
                new_persons[id]=person
        return new_persons

    def update_last_seen(self,new_persons):
        for id,person in new_persons.items():
            try:
                index=self.last_seen_ids.index(id)
                self.last_seen.pop(index)
                self.last_seen_ids.pop(index)
            except:
                pass

            self.last_seen.append(person)
            self.last_seen_ids.append(id)
        if len(self.last_seen)>self.last_seen_limit:
            extra = len(self.last_seen)-self.last_seen_limit
            self.last_seen = self.last_seen[extra:]
            self.last_seen_ids = self.last_seen_ids[extra:]




    def update_persons(self, tracked_objects):

        new_persons=self.check_new_persons(tracked_objects)
        if len(new_persons)>0:
            self.update_last_seen(new_persons)

            self.remove_all_widgets(self.persons_detected_layout)

            for person in self.last_seen:
                status = TrackingStatus.Recognized
                name = person.full_name()
                description = person.description()
                image = person.avatar
                person_widget=SimplePersonWidget(name,image)
                self.persons_detected_layout.addWidget(person_widget)


class TrackedPersonsWidget(PersonsWidget):
    def __init__(self, person_db, title, parent=None):
        super().__init__(person_db, title, parent=parent)

    def cv_to_pil(self,image):
        image = cv2.cvtColor(image , cv2.COLOR_BGR2RGB)
        return Image.fromarray(image )

    def update_persons(self, tracked_objects):
        self.remove_all_widgets(self.persons_detected_layout)
        for tracked_object in tracked_objects:
            name,description,image,status=self.get_object_data(tracked_object)
            # print(f"Recognized {name}")
            person_widget=PersonWidget(name,description,image,status)
            self.persons_detected_layout.addWidget(person_widget)

    def get_object_data(self,tracked_object):
        status=tracked_object.get_status()
        if status == TrackingStatus.Warmup:
            description=""
            name="Analizando..."
            image = self.cv_to_pil(tracked_object.face_image())
        elif status==TrackingStatus.Recognized:
            person=self.person_db[tracked_object.class_id()]
            name=person.full_name()
            description=person.description()
            image=person.avatar
        elif status == TrackingStatus.Unrecognized:
            description = ""
            name = "Persona desconocida"
            image = self.cv_to_pil(tracked_object.face_image())
        else:
            raise ValueError(status)

        return name,description,image,status


