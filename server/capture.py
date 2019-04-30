import multiprocessing
from backend import framediff
from backend import motion_detection
import cv2
import logging
import utils
from .worker import Worker

class CaptureWorker(Worker):

    def __init__(self,settings):
        super().__init__("capture")
        logging.getLogger().setLevel(logging.INFO)
        self.image_queue=multiprocessing.Queue()
        self.image_processing_queue=multiprocessing.Queue()
        self.image_queue_lock=multiprocessing.Lock()
        self.settings=settings

    def work(self):
        # improve memory managment and grabbing
        # https://www.chiefdelphi.com/forums/archive/index.php/t-123390.html
        # https://stackoverflow.com/questions/30032063/opencv-videocapture-lag-due-to-the-capture-buffer

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
        logging.info(self.tag(f"Capturing at {fw}x{fh}@{fps}, skip={self.settings.capture.frame_skip}"))
        # initialize queues
        self.image_processing_queue.put(image)
        self.image_queue.put(image)

        profiler = utils.Profiler()
        motion_detector = motion_detection.AdaptativeContourDetector(
            threshold=self.settings.capture.motion_detection_treshold)

        while not self.stopped:
            profiler.event("capture")
            cap.grab()
            # for i in range(self.settings.capture.frame_skip):
            #     pass
            profiler.event("read")
            frame_ready = cap.retrieve(image=image)

            if frame_ready:
                self.image_queue.put(image)
                if self.image_queue.qsize() < self.settings.capture.max_elements_in_queue:
                    profiler.event("motion detect")
                    if motion_detector.update_and_detect(image):
                        self.image_processing_queue.put(image)
                    profiler.event("finished")
            else:
                if not self.stopped:
                    logging.info(self.tag("stopped capturing"))
                self.stop()
            #logging.info(self.tag(profiler.summary()))
            profiler.reset()
