from PyQt5.QtGui import (QPixmap, QImage,QPainter,QPainterPath)
from .avatar import AvatarLabel
from PyQt5.QtCore import (Qt)
from PyQt5 import QtGui
from PyQt5.QtWidgets import QFrame,QWidget,QLabel,QApplication, QHBoxLayout, QVBoxLayout,QGraphicsDropShadowEffect,\
    QSizePolicy
from backend.tracking import TrackingStatus
from .. import qtutils
class PersonWidget(QFrame):

    def __init__(self, name, description, avatar, status, parent=None):
        super().__init__(parent=parent)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.set_style()

        self.profile_pixmap = self.pil2pixmap(avatar)

        self.profile_photo = AvatarLabel(self.profile_pixmap)
        self.profile_photo.setStyleSheet("AvatarLabel{ border-bottom:none;"
                                         "margin:0px;"
                                         "padding:0px;"
                                         "}")
        layout.addWidget(self.profile_photo)
        self.name_widget = self.generate_name_widget(name, description)
        layout.addWidget(self.name_widget)
        self.status_icon, self.status_icon_pixmap = self.generate_status_icon(status)
        layout.addStretch()

        self.last_seen_time=QLabel()
        self.last_seen_time.setStyleSheet("QLabel{"
                                          "font-size:24px;"
                                          "color:black;"
                                          "}")
        layout.addWidget(self.last_seen_time)

    def update_last_seen_time(self,minutes):
        minutes=int(minutes)
        if minutes>0:
            self.last_seen_time.setText(f"{minutes}m")
        else:
            self.last_seen_time.setText(f"")

    def generate_status_icon(self, status):
        # for animations https://stackoverflow.com/questions/10261265/showing-a-gif-animation-in-qlabel

        if status == TrackingStatus.Recognized:
            recognition_icon = "img/recognized.png"
        elif status == TrackingStatus.Warmup:
            recognition_icon = "img/warmup.png"
        elif status == TrackingStatus.Unrecognized:
            recognition_icon = "img/unrecognized.png"
        else:
            raise ValueError(status)
        status_icon = QLabel()
        status_icon.setStyleSheet("QLabel { border-bottom:none;margin:0px;padding:0px;}")
        status_icon_pixmap = QPixmap(recognition_icon).scaledToHeight(96, mode=Qt.SmoothTransformation)

        status_icon.setPixmap(status_icon_pixmap)

        status_icon.setAlignment(Qt.AlignRight or Qt.AlignVCenter)
        return status_icon, status_icon_pixmap

    def set_style(self):
        sp = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sp.setHorizontalStretch(10)
        self.setSizePolicy(sp)

        self.setStyleSheet("PersonWidget {margin:0px; padding:5px; "
                           # "border-radius:3px;"
                           # "border: 1px solid black; "
                           #"border-bottom: 2px solid black; "
                           "margin-bottom:2px;"
                           "background-color:white;"
                           "color: black;"
                           #"min-height:100px;"
                           #"width:100%"
                           "}")

        qtutils.add_drop_shadow(self)


    def generate_name_widget(self, name, description):
        container = QFrame()
        container.setStyleSheet("QFrame {margin-left:0px;"
                                "color:black;}")

        name_layout = QVBoxLayout()
        container.setLayout(name_layout)

        person_label = QLabel()
        person_label.setStyleSheet("QLabel {"
                                   "font-size:24px;}")
        person_label.setText(name)
        name_layout.addWidget(person_label, 0, Qt.AlignLeft)

        jobs_label = QLabel()
        jobs_label.setText(description)
        name_layout.addWidget(jobs_label, 0, Qt.AlignLeft)
        return container

    def pil2pixmap(self, im):
        if im.mode == "RGB":
            pass
        elif im.mode == "L":
            im = im.convert("RGBA")
        data = im.convert("RGBA").tobytes("raw", "RGBA")
        qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_RGBA8888)
        pixmap = QtGui.QPixmap.fromImage(qim)
        return pixmap



