import cv2
from PyQt5.QtCore import (QThread, Qt, pyqtSignal,pyqtSlot)
from PyQt5.QtGui import (QPixmap, QImage)
from PyQt5.QtWidgets import QWidget,QLabel,QApplication
import sys

class CaptureThread(QThread):

    image_captured = pyqtSignal(object)
    computing=False
    stream_url=0
    # stream_url="rtsp://163.10.22.229/live.sdp"
    # stream_url="http://163.10.22.229/video2.mjpg"

    def run(self):
        cap = cv2.VideoCapture(self.stream_url)
        while True:
            ret, image = cap.read()
            if ret:
                if not self.computing:
                    self.computing = True



                    # fake detections
                    bbox = [10, 50, 35, 12]
                    bboxes = [bbox]
                    self.computing = False
                self.image_captured.emit(image)



class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.title = "Test"

    @pyqtSlot(object)
    def setImage(self, image):
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

        self.capture_thread.image_captured.connect(self.setImage)
        self.capture_thread.start()

    def print_detections(self,bboxes):
        print(bboxes)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())