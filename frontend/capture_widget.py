
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
from frontend.cv2utils import draw_cut_rectangle,overlay_image_alpha

import settings
import time

def get_epochtime_ms():
    return round(datetime.utcnow().timestamp() * 1000)

class CaptureWidget(QFrame):

    def __init__(self,persondb,parent=None):
        super().__init__(parent=parent)
        self.settings=settings
        self.persondb=persondb

        self.face_background_color = (7, 15, 15)
        self.face_border_color=(9, 80, 30)
        self.face_corner_color=(12, 70, 30)
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
                #color=(255,255,255)
                color = (12, 106, 106)
                #self.draw_person_label(image, tracked_object, person, color)
            else:
                color = (142, 11, 55)
            self.draw_box(tracked_object,image,color)

            #self.draw_landmarks(tracked_object,image,color)
        self.draw_detections(tracked_objects,image)



    def draw_detections(self,tracked_objects,image):
        index=0
        height=50
        width=200
        padding = 20
        y=image.shape[0]-height-padding

        x=padding
        for tracked_object in tracked_objects:
            self.draw_detection(tracked_object, image,x,y,width,height)
            x+=width+padding
            index+=1

    def draw_detection(self,tracked_object,image,x,y,width,height):
        overlay = image.copy()
        stroke = 4
        linetype = cv2.LINE_4

        top,left=y,x
        bottom,right=top+height,left+width
        # if tracked_object.tracking_converged() and tracked_object.recognized():
        pad = 3
        cut_rectangle_bbox = (top - pad, right + pad, bottom + pad, left - pad)
        p1 = (cut_rectangle_bbox[3], cut_rectangle_bbox[0])
        p2 = (cut_rectangle_bbox[1], cut_rectangle_bbox[2])
        cv2.rectangle(overlay, (left, top), (right, bottom), self.face_background_color, cv2.FILLED,
                      lineType=linetype)

        cv2.rectangle(overlay, p1, p2, self.face_border_color,cv2.FILLED)
        #draw_cut_rectangle(overlay, cut_rectangle_bbox, self.face_corner_color, stroke, linetype)

        person=self.persondb[tracked_object.class_id()]
        avatar=np.asarray(person.avatar)
        
        resized_face_image=cv2.resize(avatar,(32,32))

        alpha_mask=np.ones(resized_face_image.shape[0:2])
        overlay_image_alpha(overlay,resized_face_image,(x+9,y+9),alpha_mask)


        alpha = 0.95
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)




    def draw_landmarks(self,tracked_object,image,color):
        alpha=0.05
        full_overlay = image.copy()
        linetype = cv2.LINE_4
        for landmark,position in tracked_object.landmarks().items():
            if len(position)==1:
                center=position[0]
                cv2.circle(full_overlay,center,3,color,lineType=linetype)
            else:
                (left, bottom), (right, top) = position
                cv2.rectangle(full_overlay, (left, top), (right, bottom), color, cv2.FILLED,lineType=linetype)
        cv2.addWeighted(full_overlay, alpha, image, 1 - alpha, 0, image)


    def draw_box(self, tracked_object, image, color):
        alpha = 0.95
        overlay = image.copy()
        stroke = 6
        linetype = cv2.LINE_4
        full_overlay = image.copy()
        (top, right, bottom, left) = tracked_object.bbox()

        #if tracked_object.tracking_converged() and tracked_object.recognized():
        pad = 0
        cut_rectangle_bbox=(top-pad, right+pad, bottom+pad, left-pad)
        p1=(cut_rectangle_bbox[3],cut_rectangle_bbox[0])
        p2 = (cut_rectangle_bbox[1], cut_rectangle_bbox[2])

        #draw_cut_rectangle(overlay, cut_rectangle_bbox, self.face_corner_color, stroke, linetype)
        cv2.rectangle(overlay, p1, p2, self.face_border_color, thickness=4)
        #alpha = math.sqrt(tracked_object.score())
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)


        #rectangle_color = (255, 255, 255)
        cv2.rectangle(full_overlay, (left , top ), (right , bottom ), self.face_background_color, cv2.FILLED,
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
