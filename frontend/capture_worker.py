import cv2
from PyQt5.QtCore import (QThread, Qt, pyqtSignal,pyqtSlot,QObject)
from backend.tracking import IOUTracker
import os
import time



class CaptureWorker(QObject):

    def __init__(self,face_recognizer,settings,persondb,parent=None):
        super().__init__(parent)
        self.face_recognizer = face_recognizer
        self.persondb = persondb
        self.frame=0
        self.person_detections=[]
        self.settings=settings
        self.tracker=IOUTracker(settings)
        self.stopped_capturing=False

    update_capture = pyqtSignal(object)
    # persons_detected_signal = pyqtSignal(object)

    @pyqtSlot()
    def run(self):
        # multiple processes https: // github.com / umlaeute / v4l2loopback / wiki
        # https://askubuntu.com/questions/165727/is-it-possible-for-two-processes-to-access-the-webcam-at-the-same-time
        cap = cv2.VideoCapture(self.settings.input.stream_url)
        w,h=self.settings.input.capture_resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,w )
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        cap.set(cv2.CAP_PROP_EXPOSURE, 0)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 50)

        fw, fh = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)

        print(f"Capturing at {fw}x{fh}@{fps}")

        while True:
            frame_ready, image = cap.read()
            if frame_ready:
                self.update_capture.emit(image)
            else:
                if not self.stopped_capturing:
                 print("stopped capturing")
                self.stopped_capturing = True
