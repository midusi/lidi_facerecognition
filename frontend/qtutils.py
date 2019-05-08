from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5 import QtGui

def add_drop_shadow(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setOffset(0)
    shadow.setBlurRadius(20)
    shadow.setColor(QtGui.QColor(128, 128, 128))
    widget.setGraphicsEffect(shadow)