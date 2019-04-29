
import math
from datetime import datetime
import numpy as np
import cv2

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from PyQt5.QtCore import (Qt,QTimer)
from PyQt5.QtGui import (QPixmap, QImage)
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QSizePolicy
from frontend.cv2utils import draw_cut_rectangle

import settings
import time

def get_epochtime_ms():
    return round(datetime.utcnow().timestamp() * 1000)

class CaptureWidget(QFrame):

    def __init__(self,persondb,parent=None):
        super().__init__(parent=parent)
        self.settings=settings
        self.persondb=persondb


        self.initialize_video_label()

        self.initialize_layout()

        self.tracked_objects=[]
    def initialize_layout(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.video_label)
        self.setStyleSheet("QFrame {background-color: blue;"
                           "margin:0px;"
                           "}")
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        sp = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.setSizePolicy(sp)

    def initialize_video_label(self):
        self.video_label = QLabel()
        w, h = settings.input.capture_resolution
        self.video_label.resize(w, h)
        self.set_blank_image()

    def update_persondb(self,persondb):
        self.person_db=persondb

    def update_person_detections(self,tracked_objects,image):
        self.tracked_objects=tracked_objects
        self.update_capture(image)

    def update_capture(self,image):
        def update_capture_deferred():
            self.draw_person_boxes(self.tracked_objects, image)
            self.set_cv_image(image)
        QTimer.singleShot(self.settings.client.display_delay, update_capture_deferred)

    def set_blank_image(self):
        w, h = self.settings.gui.display_resolution
        rgb_image=np.zeros((w,h,3))
        self.set_image(rgb_image)
    def set_image(self,rgbImage):
        qimage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
        self.set_qimage(qimage)

    def set_qimage(self,qimage):
        w, h = self.settings.gui.display_resolution
        p = qimage.scaled(w, h, Qt.KeepAspectRatio)
        p = QPixmap.fromImage(p)
        self.video_label.setPixmap(p)

    def set_cv_image(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.set_image(rgb_image)



    def draw_person_boxes(self, tracked_objects, image):

        for tracked_object in tracked_objects:
            person=self.persondb[tracked_object.class_id()]
            if tracked_object.tracking_converged():
                color=(255,255,255)
                self.draw_person_label(image, tracked_object, person, color)
            else:
                color=(200,200,200)
            self.draw_box(tracked_object,image,color)




    def draw_box(self, tracked_object, image, color):
        alpha = 0.1
        overlay = image.copy()
        stroke = 1
        linetype = cv2.LINE_4
        full_overlay = image.copy()
        (top, right, bottom, left) = tracked_object.bbox()

        if tracked_object.tracking_converged() and tracked_object.recognized():
            pad = 3
            cut_rectangle_bbox=(top-pad, right+pad, bottom+pad, left-pad)
            draw_cut_rectangle(overlay, cut_rectangle_bbox, color, stroke, linetype)

            alpha = math.sqrt(tracked_object.score())
            cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)


        rectangle_color = (255, 255, 255)
        cv2.rectangle(full_overlay, (left , top ), (right , bottom ), color, cv2.FILLED,
                      lineType=linetype)
        #cv2.rectangle(full_overlay, (left + pad, top + pad), (right - pad, bottom - pad), color, cv2.FILLED,
        # lineType=linetype)
        alpha = 0.2
        cv2.addWeighted(full_overlay, alpha, image, 1 - alpha, 0, image)


    def draw_person_label(self, image, tracked_object, person, color):
        (top, right, bottom, left) = tracked_object.bbox()
        w, h = right - left, bottom - top
        label_height = max(h // 5, 20)

        label_top = bottom + label_height // 3
        label_bottom = label_top + label_height
        extra = 0
        label_left=left - extra
        label_right=right+extra
        linetype = cv2.LINE_AA
        overlay = image.copy()

        cv2.rectangle(overlay, (label_left, label_top), (label_right, label_bottom), color, cv2.FILLED,
                      lineType=linetype)
        alpha=0.95
        # cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
        self.draw_person_text(image, person, tracked_object, (label_top, label_right, label_bottom, label_left))

    def draw_person_text(self, image, person, tracked_object, label_bbox):
        if tracked_object.recognized():
            lastname = person.lastname
            name = person.name
            label = f"{name} {lastname}"
        else:
            return
        n=len(label)

        (label_top, label_right, label_bottom, label_left) = label_bbox
        w, h = label_right - label_left, label_bottom - label_top
        font_size = min(h / (math.sqrt(n)*11),0.5)

        label_height=label_bottom-label_top
        text_pos = (label_left, label_top + label_height // 4 * 3)

        font = cv2.FONT_HERSHEY_SIMPLEX
        linetype = cv2.LINE_AA

        cv2.putText(image, label, text_pos, font, font_size, (255, 255, 255), 1, lineType=linetype)
