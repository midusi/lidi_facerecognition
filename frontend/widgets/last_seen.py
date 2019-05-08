from backend.tracking import TrackingStatus
from .simple_person import SimplePersonWidget
from PyQt5.QtCore import (QThread, Qt, pyqtSignal,pyqtSlot,)
import time
from PyQt5.QtWidgets import QFrame,QWidget,QLabel,QApplication, QHBoxLayout, QVBoxLayout,QGraphicsDropShadowEffect,\
    QSizePolicy
from PyQt5 import QtGui

from .persons import PersonWidget

from ..flow_layout import FlowLayout

class QHLine(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class LastSeenWidget(QFrame):

    def __init__(self, person_db, title, max_persons_in_display=5, time_limit=20, parent=None):
        '''
            @time_limit Time limit in minutes
        '''
        super().__init__(parent=parent)
        self.last_seen_timestamp={}
        self.max_persons_in_display=max_persons_in_display
        self.time_limit=time_limit
        self.avatar_size=96
        self.person_db = person_db
        self.person_widgets={ id:SimplePersonWidget(person.full_name(), person.avatar) for (id,person) in person_db.items()}
        self.currently_displayed_id=[]
        self.title = title
        self.setup_widgets()

    def setup_widgets(self):
        self.main_layout = self.generate_main_layout()


        #self.main_layout.addWidget(QHLine())

        self.persons_detected_layout = self.generate_persons_detected_layout()
        self.main_layout.addLayout(self.persons_detected_layout)


        self.title_widget = self.generate_title(self.title)
        self.main_layout.addWidget(self.title_widget)

        self.setStyleSheet("LastSeenWidget {width:100%;"
                           "background-color:white;"
                           "padding:0px;"
                           "margin:0px;"
                           f"min-height:{self.avatar_size*3//2}px;"
                           "}")

        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(0)
        shadow.setBlurRadius(20)
        shadow.setColor(QtGui.QColor(128, 128, 128))
        self.setGraphicsEffect(shadow)

        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0,0,0,0)

        sp = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # sp.setHorizontalStretch(1)
        # sp.setVerticalStretch(0.25)
        self.setSizePolicy(sp)


        self.setLayout(self.main_layout)

    def generate_persons_detected_layout(self):
        persons_detected_layout = FlowLayout()
        persons_detected_layout.setSpacing(0)
        persons_detected_layout.setContentsMargins(5,5,5,5)
        persons_detected_layout.setAlignment(Qt.AlignCenter)
        return persons_detected_layout



    def generate_main_layout(self):
        main_layout = QVBoxLayout()
        return main_layout

    def generate_title(self,title):

        title_layout = QLabel()
        title_layout.setStyleSheet("QLabel {"
                                   "font-size:16px;"
                                   "color:BA1234;"
                                   #"border-right:5px solid black;"
                                   #"border-bottom:5px solid black;"
                                   "width:100%;"
                                   "margin:5px;"
                                   "padding:0px;"
                                   #"min-height:64px;"
                                   "}")
        title_layout.setText(title)
        #title_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title_layout.setAlignment(Qt.AlignCenter)

        return title_layout

    def update_timestamps(self,tracked_objects):
        timestamp=time.time()
        for tracked_object in tracked_objects:
            if tracked_object.get_status() == TrackingStatus.Recognized:
                self.last_seen_timestamp[tracked_object.class_id()]=timestamp

    def latest_person_ids(self,max_persons_in_display,time_limit):
        person_ids_sorted_by_timestamp=sorted(self.last_seen_timestamp.items(), key =
             lambda kv:(kv[1], kv[0]))
        delta=time_limit*60
        timestamp_limit = time.time()-delta

        # get ids and limit persons of the last @time_limit minutes
        person_ids_sorted_by_timestamp = [id for (id, timestamp) in person_ids_sorted_by_timestamp if timestamp>timestamp_limit]

        # limit to @max_persons_in_display results
        if len(person_ids_sorted_by_timestamp)>max_persons_in_display:
            person_ids_sorted_by_timestamp=person_ids_sorted_by_timestamp[:max_persons_in_display]

        return person_ids_sorted_by_timestamp

    def update_persons(self, tracked_objects):

        self.update_timestamps(tracked_objects)
        ids=self.latest_person_ids(self.max_persons_in_display,self.time_limit)
        ids+=[2,6,8]

        modified=False
        # remove widgets for stale ids
        for id in self.currently_displayed_id:
            if not id in ids:
                self.persons_detected_layout.removeWidget(self.person_widgets[id])
                modified=True
        # add widget for new ids
        for id in ids:
            if not id in self.currently_displayed_id:
                person_widget=self.person_widgets[id]
                self.persons_detected_layout.addWidget(person_widget)
                modified = True

        # update currently displayed ids
        self.currently_displayed_id=ids
