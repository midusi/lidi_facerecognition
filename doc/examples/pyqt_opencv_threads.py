import cv2
from PyQt5.QtCore import (QThread, Qt, pyqtSignal,pyqtSlot)
from PyQt5.QtGui import (QPixmap, QImage)
from PyQt5.QtWidgets import QWidget,QLabel,QApplication
import sys

class CaptureThread(QThread):

    image_captured = pyqtSignal(object)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, image = cap.read()
            if ret:
                self.image_captured.emit(image)
                print("image read")


class ProcessingThread(QThread):

    people_detected = pyqtSignal(object)
    computing=False

    @pyqtSlot(object)
    def detect_people(self,image):
        #fake processing

        if not self.computing:
            print("detecting")
            self.computing=True

            a = 0
            for i in range(1000000):
                a+=1
            # fake detections
            bbox=[10,50,35,12]
            bboxes=[bbox]
            #self.people_detected.emit(bboxes)
            self.computing = False
        else:
            print("avoiding computation")




class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.title = "Test"

    @pyqtSlot(object)
    def setImage(self, image):
        print("setting image")
        rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
        p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        p = QPixmap.fromImage(p)
        p = p.scaled(640, 480, Qt.KeepAspectRatio)
        self.label.setPixmap(p)

    def initUI(self):
        self.setWindowTitle("Test")
        self.setGeometry(0,0,1000,1000)
        #self.resize(1800, 1200)
        # create a label
        self.label = QLabel(self)
        self.label.move(280, 120)
        self.label.resize(640, 480)
        self.capture_thread = CaptureThread()
        self.capture_thread.moveToThread(self.capture_thread)
        self.processing_thread = ProcessingThread()
        self.processing_thread .moveToThread(self.processing_thread )
        self.capture_thread.image_captured.connect(self.processing_thread.detect_people)
        self.capture_thread.image_captured.connect(self.setImage)


        self.processing_thread.people_detected.connect(self.print_detections)
        self.capture_thread.start()
        self.processing_thread.start()

    def print_detections(self,bboxes):
        print("Detected bboxes: ",bboxes)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())