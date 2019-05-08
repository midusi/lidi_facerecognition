from PyQt5.QtCore import (Qt)

from PyQt5.QtWidgets import QFrame,QLabel, QVBoxLayout,QSizePolicy,QLayout,QScrollArea,QWidget

from backend.tracking import TrackingStatus

from .person import PersonWidget
import time

from .. import qtutils

class LastSeenPeople:
    def __init__(self,max_persons_in_display=5,time_limit=20):
        self.last_seen_timestamp = {}
        self.max_persons_in_display = max_persons_in_display
        self.time_limit = time_limit
        self.ids = []

    def update_timestamps(self, tracked_objects):
        timestamp = time.time()
        for tracked_object in tracked_objects:
            if tracked_object.get_status() == TrackingStatus.Recognized:
                self.last_seen_timestamp[tracked_object.class_id()] = timestamp

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

    def get_last_seen_times(self):
        now=time.time()
        return dict([(id,(now-timestamp)/60) for (id,timestamp) in self.last_seen_timestamp.items()])

    def update(self, tracked_objects):
        self.update_timestamps(tracked_objects)
        self.ids=self.latest_person_ids(self.max_persons_in_display,self.time_limit)

class QScrollWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent=parent)


class TrackedPersonsWidget(QFrame):

    def __init__(self,person_db,title,avatar_size=96,parent=None):
        super().__init__(parent=parent)
        self.update_persondb(person_db)
        self.last_seen_people=LastSeenPeople()
        self.main_layout=self.generate_main_layout()

        self.title=self.generate_title(title)

        self.persons_layout=self.generate_persons_layout()
        self.persons_scroll_area = QScrollArea()
        self.persons_scroll_area.setWidgetResizable(True)

        self.persons_scroll_area_widget=QScrollWidget()
        self.persons_scroll_area_widget.setStyleSheet("QScrollWidget{"
                                                      "width:100%;"
                                                      "border:2px solid red;"
                                                      "background-color:blue;"
                                                      "}")

        self.persons_scroll_area.horizontalScrollBar().setStyleSheet("QScrollBar {height:0px;}");
        self.persons_scroll_area.verticalScrollBar().setStyleSheet("QScrollBar {width:0px;}");

        sp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sp.setHorizontalStretch(1)
        sp.setVerticalStretch(1)
        self.persons_scroll_area_widget.setSizePolicy(sp)

        self.persons_scroll_area.setWidget(self.persons_scroll_area_widget)
        self.persons_scroll_area_widget.setLayout(self.persons_layout)

        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.persons_scroll_area)


        self.setup_style()


    def setup_style(self):
        self.setStyleSheet("TrackedPersonsWidget {width:100%;"
                           "border:none;"
                           "padding:5px;"
                           "}")
        qtutils.add_drop_shadow(self)


        sp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.setSizePolicy(sp)

        self.setLayout(self.main_layout)

    def generate_persons_layout(self):
        persons_detected = QVBoxLayout()
        persons_detected.setAlignment(Qt.AlignTop)
        persons_detected.setSpacing(0)
        persons_detected.setContentsMargins(0,0,0,0)

        return persons_detected

    def generate_main_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        return main_layout

    def generate_title(self,title):
        title_widget = QLabel()
        title_widget.setStyleSheet("QLabel {font-size:24px;"
                                   "background-color:white;"
                                   "margin-bottom:5px;"
                                   "color:black;"
                                   "padding:5px;"
                                   "}")
        title_widget.setText(title)
        title_widget.setAlignment(Qt.AlignRight)
        qtutils.add_drop_shadow(title_widget)
        return title_widget

    def update_persondb(self,person_db):
        self.person_db = person_db
        def person_to_widget(person):
            w =PersonWidget(person.full_name(), person.description(), person.avatar,TrackingStatus.Recognized)
            w.setMinimumSize(w.minimumSizeHint())

            return w
        self.person_widgets = {id:person_to_widget(person)  for (id, person) in
                               person_db.items()}



    def update_tracked_objects(self, tracked_objects,image):
        old_ids=self.last_seen_people.ids
        self.last_seen_people.update(tracked_objects)
        for id in old_ids:
            if not id in self.last_seen_people.ids:
                self.persons_layout.removeWidget(self.person_widgets[id])
                modified=True
        # add widget for new ids
        for id in self.last_seen_people.ids:
            if not id in old_ids:
                person_widget=self.person_widgets[id]
                self.persons_layout.insertWidget(0,person_widget,stretch=1)
                modified = True

        last_seen_time_per_id=self.last_seen_people.get_last_seen_times()
        for id,last_seen_time in last_seen_time_per_id.items():
            self.person_widgets[id].update_last_seen_time(last_seen_time)




