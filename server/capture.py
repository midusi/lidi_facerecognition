import multiprocessing
from backend import framediff
from backend import motion_detection
import cv2
import logging
import utils

class CaptureWorker:

    def __init__(self,settings):

        self.stop = False

        self.image_queue=multiprocessing.Queue()
        self.image_queue_lock=multiprocessing.Lock()
        self.settings=settings

    def run(self):
        # improve memory managment and grabbing
        # https://www.chiefdelphi.com/forums/archive/index.php/t-123390.html
        # https://stackoverflow.com/questions/30032063/opencv-videocapture-lag-due-to-the-capture-buffer
        logging.info("Starting capture worker..")
        cap = cv2.VideoCapture(self.settings.input.stream_url)
        w, h = self.settings.input.capture_resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        cap.set(cv2.CAP_PROP_EXPOSURE, 0)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 10)

        fw, fh = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)

        # read frames until ready for the first time
        frame_ready=False
        while not frame_ready:
            frame_ready,image=cap.read()

        profiler=utils.Profiler()
        motion_detector=motion_detection.AdaptativeContourDetector(threshold=self.settings.capture.motion_detection_treshold)
        logging.info(f"Capturing at {fw}x{fh}@{fps}, skip={self.settings.capture.frame_skip}")
        while not self.stop:

            cap.grab()
            # for i in range(self.settings.capture.frame_skip):
            #     pass
            profiler.event("read")
            frame_ready = cap.retrieve(image=image)
            profiler.event("finished reading")

            if frame_ready:
                # logging.info(f"L1 distance between images: {distance}")
                if self.image_queue.qsize() < self.settings.capture.max_elements_in_queue:
                    if motion_detector.update_and_detect(image):
                        self.image_queue.put(image)
            else:
                if not self.stop:
                    logging.info("stopped capturing")
                self.stop = True
            profiler.reset()
        logging.info("Stopped capture worker")
