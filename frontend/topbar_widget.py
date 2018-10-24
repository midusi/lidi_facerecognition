from PyQt5.QtCore import (QThread, Qt, pyqtSignal,pyqtSlot)
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import (QPixmap, QImage)
from PyQt5.QtWidgets import QFrame,QWidget,QLabel,QApplication, QHBoxLayout, QVBoxLayout,QGraphicsDropShadowEffect,\
    QSizePolicy
import logging
from PyQt5 import QtCore

class BottomBarWidget(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.setLayout(QHBoxLayout())
        self.setStyleSheet("BottomBarWidget {"
                           "background-color:#710100;"
                           "min-height:20px;"
                           "border-top:10px solid #A10100;"

                           "}")
        sp = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sp.setHorizontalStretch(1)
        sp.setVerticalStretch(1)
        self.setSizePolicy(sp)

        self.notes_label= QLabel()
        self.notes_label.setStyleSheet(".QLabel { font-size:8px;"
                                       "border-bottom:none;"
                                       "margin-left:1px;"
                                       "padding:0px; "
                                       "color:white; }")
        self.notes_label.setText("Version alpha")
        self.notes_label.setAlignment(Qt.AlignVCenter or Qt.AlignRight)
        self.layout().addStretch()
        self.layout().addWidget(self.notes_label)
        size=24
        self.online_pixmap = QPixmap('img/online.png').scaled(size,size, transformMode=QtCore.Qt.SmoothTransformation)
        self.offline_pixmap = QPixmap('img/offline.png').scaled(size,size,transformMode=QtCore.Qt.SmoothTransformation)
        self.server_status = QLabel()
        self.server_status.setStyleSheet(".QLabel { width:64px; height:64px;"
                                         "border-bottom:none;margin-left:10px;"
                                         "padding:0px; "
                                         " color:white; }")

        self.server_status.setAlignment(Qt.AlignVCenter or Qt.AlignRight)
        self.layout().addWidget(self.server_status)

        # sp = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # sp.setHorizontalStretch(1)
        # sp.setVerticalStretch(0)
        # self.setSizePolicy(sp)

    def update_server_status(self, status):
        if status == "online":
            self.server_status.setPixmap(self.online_pixmap)
        elif status == "offline":
            self.server_status.setPixmap(self.offline_pixmap)
        else:
            logging.warning(f"Unknown server status: {status}")


class TopBarWidget(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.setLayout(QHBoxLayout())

        self.setStyleSheet("QFrame {"
                           "background-color:#710100;"
                           "min-height:100px;"
                           "border-bottom:10px solid #A10100;"

                           "}")

        self.logo = QLabel()
        self.logo_pixmap= QPixmap('img/logo_chico.png')
        self.logo.setPixmap(self.logo_pixmap)
        self.logo.setAlignment(Qt.AlignVCenter or Qt.AlignLeft)
        self.logo.setStyleSheet(".QLabel { font-size:64px;"
                                "border-bottom:none;margin-left:10px;"
                                "padding:0px; "
                                " color:white; }")
        self.layout().addWidget(self.logo)


        self.logo_text= QLabel()
        self.logo_text.setStyleSheet(".QLabel { font-size:64px;border-bottom:none;margin-left:1px;padding:0px; "
                                "margin-left:20px; color:white; }")
        self.logo_text.setText("III-LIDI")
        self.logo_text.setAlignment(Qt.AlignVCenter or Qt.AlignLeft)
        self.layout().addWidget(self.logo_text)

        self.layout().addStretch()

        self.title= QLabel()
        self.title.setText("Bienvenido")

        self.title.setStyleSheet(".QLabel {font-size:48px;"
                                 " color:white;border-bottom:none;"
                                 "margin-right:10px;}")
        self.title.setAlignment(Qt.AlignVCenter or Qt.AlignRight)
        self.layout().addWidget(self.title)





