from PyQt5.QtGui import (QPixmap, QPainter,QPainterPath)
from PyQt5.QtWidgets import QLabel,QGraphicsDropShadowEffect
from PyQt5.QtCore import (Qt)
from PyQt5 import QtGui

class AvatarLabel(QLabel):
    def __init__(self, p,size=96,*args, antialiasing=True, use_shadow=True, **kwargs):
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
        self.setAlignment(Qt.AlignHCenter)
        if use_shadow:
            shadow = QGraphicsDropShadowEffect()
            shadow.setOffset(0)
            shadow.setBlurRadius(20)
            shadow.setColor(QtGui.QColor(128, 128, 128))
            self.setGraphicsEffect(shadow)
