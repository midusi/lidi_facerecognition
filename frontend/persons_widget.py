from PyQt5.QtCore import (QThread, Qt, pyqtSignal,pyqtSlot)
from PyQt5.QtGui import (QPixmap, QImage,QPainter,QPainterPath)
from PyQt5.QtWidgets import QFrame,QWidget,QLabel,QApplication, QHBoxLayout, QVBoxLayout,QGraphicsDropShadowEffect,\
    QSizePolicy
from PyQt5 import QtGui,QtCore,QtWidgets
import cv2
from PIL import Image
from backend.tracking import TrackingStatus


class AvatarLabel(QLabel):
    def __init__(self, p,size=96,*args, antialiasing=True, **kwargs):
        super(AvatarLabel, self).__init__(*args, **kwargs)
        self.Antialiasing = antialiasing
        self.setMaximumSize(size,size)
        self.setMinimumSize(size,size)
        self.radius = size//2

        self.target = QPixmap(self.size())
        self.target.fill(Qt.transparent)

        p = p.scaled(
            size,size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        painter = QPainter(self.target)
        if self.Antialiasing:
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        path = QPainterPath()
        path.addRoundedRect(
            0, 0, self.width(), self.height(), self.radius, self.radius)

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, p)
        self.setPixmap(self.target)


class PersonsPanel(QFrame):
    def __init__(self,person_db,parent=None):
        super().__init__(parent=parent)
        self.persons_widget=PersonsWidget(person_db,"",self)




class PersonsWidget(QFrame):
    def __init__(self,person_db,title,parent=None):
        super().__init__(parent=parent)
        self.person_db=person_db
        self.title=title
        self.persons_detected_layout = QVBoxLayout()
        self.setStyleSheet("PersonsWidget {width:100%;"
                           # "margin-top:30px;"
                           "background-color:#333333;"
                            "background-color:#332222;"
                           "padding:0px;"
                           "}")
        self.persons_detected_layout.setAlignment(Qt.AlignTop)
        self.persons_detected_layout.setSpacing(0)
        self.persons_detected_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.persons_detected_layout)
        sp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sp.setHorizontalStretch(1)
        sp.setVerticalStretch(1)
        self.setSizePolicy(sp)

    def update_persondb(self,persondb):
        self.person_db=persondb

    def remove_all_widgets(self, layout):
        for i in reversed(range(layout.count())):
            widgetToRemove = layout.itemAt(i).widget()
            # remove it from the layout list
            layout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

class RecognizedPersonsWidget(PersonsWidget):
    def __init__(self, person_db, title, parent=None):
        super().__init__(person_db,title,parent=parent)

    def get_object_data(self, tracked_object):
        return "asd"

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



class PersonWidget(QFrame):

    def __init__(self,name,description,avatar,status,parent=None):
        super().__init__(parent=parent)
        layout= QHBoxLayout()
        self.setLayout(layout)
        self.set_style()


        self.profile_pixmap = self.pil2pixmap(avatar)

        self.profile_photo= AvatarLabel(self.profile_pixmap)
        self.profile_photo.setStyleSheet("AvatarLabel{ border-bottom:none;"
                                         "margin:0px;"
                                         "padding:0px;"
                                         "}")
        layout.addWidget(self.profile_photo)
        self.name_widget = self.generate_name_widget(name,description)
        layout.addWidget(self.name_widget)
        self.status_icon, self.status_icon_pixmap=self.generate_status_icon(status)
        #layout.addStretch()
        # layout.addWidget(self.logo)

    def generate_status_icon(self, status):
        # for animations https://stackoverflow.com/questions/10261265/showing-a-gif-animation-in-qlabel
        if status==TrackingStatus.Recognized:
            recognition_icon = "img/recognized.png"
        elif status==TrackingStatus.Warmup:
            recognition_icon = "img/warmup.png"
        elif status == TrackingStatus.Unrecognized:
            recognition_icon = "img/unrecognized.png"
        else:
            raise ValueError(status)
        status_icon = QLabel()
        status_icon.setStyleSheet("QLabel { border-bottom:none;margin:0px;padding:0px;}")
        status_icon_pixmap = QPixmap(recognition_icon).scaledToHeight(96,mode=Qt.SmoothTransformation)

        status_icon.setPixmap(status_icon_pixmap)

        status_icon.setAlignment(Qt.AlignRight or Qt.AlignVCenter)
        return status_icon,status_icon_pixmap

    def set_style(self):
        sp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sp.setHorizontalStretch(10)
        self.setSizePolicy(sp)

        self.setStyleSheet("PersonWidget {margin:0px; padding:10px; "
                           # "border-radius:3px;"
                           #"border: 1px solid black; "
                            "border-bottom: 2px solid black; "
                           "background-color:white;"
                           "color: black;"
                           "min-width:120px;"
            
                            "}")
        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(0)
        shadow.setBlurRadius(13)
        shadow.setColor(QtGui.QColor(128,128,128))

        self.setGraphicsEffect(shadow)

    def generate_name_widget(self, name,description):
        container=QFrame()
        container.setStyleSheet("QFrame {margin-left:0px;}")

        name_layout= QVBoxLayout()
        container.setLayout(name_layout)

        person_label = QLabel()
        person_label.setStyleSheet("QLabel {font-size:28px;}")
        person_label.setText(name)
        name_layout.addWidget(person_label, 0, Qt.AlignLeft)

        jobs_label = QLabel()
        jobs_label.setText(description)
        name_layout.addWidget(jobs_label, 0, Qt.AlignLeft)
        return container

    def pil2pixmap(self,im):
        if im.mode == "RGB":
            pass
        elif im.mode == "L":
            im = im.convert("RGBA")
        data = im.convert("RGBA").tobytes("raw", "RGBA")
        qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_RGBA8888)
        pixmap = QtGui.QPixmap.fromImage(qim)
        return pixmap



