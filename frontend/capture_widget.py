
import math
from datetime import datetime
import numpy as np
import cv2
from skimage import draw
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

        self.face_background_color = (1,2, 40)
        self.face_border_color=(0, 1, 162)

        self.face_corner_color=(1, 12, 160)

        self.label_background_color=(0,1,71)
        self.label_border_color = (0,1,40)
        #self.label_border_color = (0, 1, 160)

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

    def update_tracked_objects(self,tracked_objects,image):
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
                #self.draw_person_label(image, tracked_object, person, color)
                pass
            self.draw_face_box(tracked_object, image)

            #self.draw_landmarks(tracked_object,image,color)
        #self.draw_detections(tracked_objects,image)



    def draw_detections(self,tracked_objects,image):
        h,w,c=image.shape
        index=0
        height=72
        min_width=200
        padding = 20
        y=image.shape[0]-height-padding
        no_more_space_icon_width=100
        x=padding
        if len(tracked_objects)>0:
            for i in range(2):
                tracked_objects.append(tracked_objects[0])

        for tracked_object in tracked_objects:
            if tracked_object.tracking_converged():
                width=self.draw_detection(tracked_object, image,x,y,min_width,height)
                x+=width+padding
                index += 1
                if (x+no_more_space_icon_width>w):
                    #TODO draw no more space icon
                    break

    def draw_detection_box(self,overlay,x,y,width,height):
        linetype = cv2.LINE_4

        top, left = y, x
        bottom, right = top + height, left + width
        # if tracked_object.tracking_converged() and tracked_object.recognized():
        pad = 1
        cut_rectangle_bbox = (top - pad, right + pad, bottom + pad, left - pad)
        p1 = (cut_rectangle_bbox[3], cut_rectangle_bbox[0])
        p2 = (cut_rectangle_bbox[1], cut_rectangle_bbox[2])
        cv2.rectangle(overlay, (left, top), (right, bottom), self.label_background_color, cv2.FILLED,
                      lineType=linetype)

        cv2.rectangle(overlay, p1, p2, self.label_border_color, thickness=1)
        # draw_cut_rectangle(overlay, cut_rectangle_bbox, self.face_corner_color, stroke, linetype)

    def draw_detection_avatar(self,overlay,avatar,x,y,height,avatar_size):
        # convert from PIL to numpy
        avatar = np.asarray(avatar)
        # remove alpha
        avatar = avatar[:, :, :3]
        # rgb to bgr
        avatar = avatar[..., ::-1]
        # resize to desired size


        resized_face_image = cv2.resize(avatar, (avatar_size, avatar_size))
        alpha_mask = np.zeros(resized_face_image.shape[0:2])
        radius = avatar_size // 2
        center = (radius, radius)
        cv2.circle(alpha_mask, center, radius - 4, 1, cv2.FILLED, lineType=cv2.LINE_AA)
        cv2.GaussianBlur(alpha_mask,(5,5),1,dst=alpha_mask)

        padding_background = 4
        background = np.zeros((avatar_size + padding_background, avatar_size + padding_background, 3))
        background_alpha = np.zeros((avatar_size + padding_background, avatar_size + padding_background))
        cv2.circle(background_alpha, center, radius, (1, 1, 1), cv2.FILLED)

        background_show = np.zeros((avatar_size + padding_background, avatar_size + padding_background, 3))
        background_show[:,:,0]=background_alpha
        background_show[:, :, 1] = background_alpha
        background_show[:, :, 2] = background_alpha
        cv2.GaussianBlur(background_alpha, (5, 5), 0, dst=background_alpha)


        padding = (height - avatar_size) // 2
        #overlay_image_alpha(overlay, background, (x + padding - 1, y + padding - 1), background_alpha)
        overlay_image_alpha(overlay, resized_face_image, (x + padding, y + padding), alpha_mask)



    def draw_detection_text(self,overlay,person,x,y,width,height,avatar_size):

        pad_x=30
        x_text=x+avatar_size+pad_x
        y_text=y+(height//2)
        text=person.name

        cv2.putText(overlay,text,(x_text,y_text),cv2.FONT_HERSHEY_DUPLEX,0.4,(255,255,255),lineType=cv2.LINE_AA)

    def draw_detection(self, tracked_object, image, x, y, min_width, height):
        overlay = image.copy()

        person = self.persondb[tracked_object.class_id()]
        width=min_width
        avatar_size = 64
        self.draw_detection_box(overlay,x,y,width,height)
        self.draw_detection_avatar(overlay,person.avatar,x,y,height,avatar_size )
        self.draw_detection_text(overlay,person,x,y,width,height,avatar_size )
        alpha = 0.99
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
        return width

    def draw_landmarks(self,tracked_object,image,color):
        alpha=0.05
        full_overlay = image.copy()
        linetype = cv2.LINE_4
        for landmark,position in tracked_object.landmarks().items():
            if len(position)==1:
                center=position[0]
                cv2.circle(full_overlay,center,3,color,cv2.FILLED,lineType=linetype)
            else:
                (left, bottom), (right, top) = position
                cv2.rectangle(full_overlay, (left, top), (right, bottom), color, cv2.FILLED,lineType=linetype)
        cv2.addWeighted(full_overlay, alpha, image, 1 - alpha, 0, image)


    def draw_face_box(self, tracked_object, image):
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
        cv2.rectangle(overlay, p1, p2, self.face_border_color, thickness=3)
        #alpha = math.sqrt(tracked_object.score())
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)


        #rectangle_color = (255, 255, 255)
        cv2.rectangle(full_overlay, (left , top ), (right , bottom ), self.face_background_color, cv2.FILLED,
                      lineType=linetype)
        #cv2.rectangle(full_overlay, (left + pad, top + pad), (right - pad, bottom - pad), color, cv2.FILLED,
        # lineType=linetype)
        alpha = 0.2
        cv2.addWeighted(full_overlay, alpha, image, 1 - alpha, 0, image)


    def draw_face_label(self, image, tracked_object, person, color):
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
        self.draw_face_text(image, person, tracked_object, (label_top, label_right, label_bottom, label_left))

    def draw_face_text(self, image, person, tracked_object, label_bbox):
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
