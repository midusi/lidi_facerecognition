from PyQt5.QtCore import (Qt)
from PyQt5 import QtGui
from PyQt5.QtWidgets import QFrame,QWidget,QLabel,QApplication, QHBoxLayout, QVBoxLayout,QGraphicsDropShadowEffect,\
    QSizePolicy, QGridLayout,QLayout
from backend.tracking import TrackingStatus

from .avatar import AvatarLabel

class SimplePersonWidget(QFrame):

    def __init__(self, name, avatar, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.width = 96
        layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        layout.setAlignment(Qt.AlignHCenter or Qt.AlignTop)
        self.avatar_widget = self.generate_avatar_widget(avatar)
        # self.avatar_layout = QGridLayout()
        # self.avatar_layout.addWidget(self.avatar_widget)
        # layout.addLayout(self.avatar_layout)
        layout.addWidget(self.avatar_widget)



        self.name_widget = self.generate_name_widget(name)
        # self.name_layout = QGridLayout()
        # self.name_layout.addWidget(self.name_widget)
        # layout.addLayout(self.name_layout)
        #layout.addWidget(self.name_widget)

        self.set_style()


        self.setMaximumSize(self.sizeHint())


    def set_style(self):
        # sp = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # sp.setHorizontalStretch(0)
        # sp.setVerticalStretch(0)
        # self.setSizePolicy(sp)


        self.setStyleSheet("SimplePersonWidget {"
                           "margin:5px;"
                           # "padding:5px; " 
                           # "border: 1px solid black; "
                           #"background-color:white;"
                           "color: black;"
                           "}")

        # shadow = QGraphicsDropShadowEffect()
        # shadow.setOffset(0)
        # shadow.setBlurRadius(20)
        # shadow.setColor(QtGui.QColor(128, 128, 128))
        # self.setGraphicsEffect(shadow)

    def generate_avatar_widget(self,avatar):
        self.pixmap = self.pil2pixmap(avatar)

        avatar_widget = AvatarLabel(self.pixmap,size=self.width)

        avatar_widget.setStyleSheet("AvatarLabel{ border-bottom:none;"
                                         "margin:0px;"
                                         "padding:0px;"
                                         f"width:{self.width}px;"
                                         "}")



        avatar_widget.setAlignment(Qt.AlignHCenter)
        return avatar_widget

    def set_size_policy_minimum(self,widget):
        sp = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        widget.setSizePolicy(sp)

    def generate_name_widget(self, name):
        person_label = QLabel()
        person_label.setWordWrap(True)

        #self.set_size_policy_minimum(person_label)
        #person_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        #person_label.setAlignment(Qt.AlignCenter)

        person_label.setStyleSheet("QLabel {"
                                   "font-size:10px;"
                                   "color:black;"
                                    "margin:0px;"
                                   "margin-top:5px;"
                                   
                                    "padding:0px; "
                                   f"max-width:{self.width}px;"
                                   "}")

        person_label.setText(name)
        return person_label

        # container = QFrame()
        # container.setStyleSheet("QFrame {margin-left:0px;color:black;}")
        #
        # name_layout = QVBoxLayout()
        # container.setLayout(name_layout)
        #name_layout.addWidget(person_label, 0, Qt.AlignCenter)
        #return container

    def pil2pixmap(self, im):
        if im.mode == "RGB":
            pass
        elif im.mode == "L":
            im = im.convert("RGBA")
        data = im.convert("RGBA").tobytes("raw", "RGBA")
        qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_RGBA8888)
        pixmap = QtGui.QPixmap.fromImage(qim)
        return pixmap



