import cv2
from backend.tracking import IOUTracker
import os
import multiprocessing
import cv2
import logging
import time
import utils
import threading
import queue


class RecognitionWorker:

    def __init__(self,face_recognizer,settings,persondb,capture_worker):
        print("init of "+str(self))
        self.recognitions=0
        self.capture_worker=capture_worker
        self.stop = False
        self.tracked_objects_queue = multiprocessing.Queue()
        # self.last_frame=0
        self.settings=settings
        self.face_recognizer = face_recognizer
        self.persondb = persondb
        # self.frame = 0
        self.person_detections = []
        self.tracked_objects= []
        self.tracker = IOUTracker(settings)


    def save_images_worker(self):
        while not self.stop:
            # image,tracked_objects=self.image_saving_queue.get()
            # self.save_unrecognized_peoples_faces(image, tracked_objects)
            filepath, face_image= self.image_saving_queue.get()
            cv2.imwrite(filepath, face_image)

    def run(self):
        logging.info("Started recognition worker")
        while self.capture_worker.image_queue.empty():
            time.sleep(0.1)
        self.image_saving_queue=queue.Queue()
        self.image_saving_thread=threading.Thread(target=self.save_images_worker)
        self.image_saving_thread.setDaemon(True)
        self.image_saving_thread.start()

        while not self.stop:

            # image=self.capture_worker.image.copy()
            # self.capture_worker.image_queue_lock.acquire()

            # logging.debug(f"queue size: {self.capture_worker.image_queue.qsize()}")
            while not self.capture_worker.image_queue.empty():
                image = self.capture_worker.image_queue.get()
            self.process_image(image)
            # if not self.capture_worker.image_queue.empty():
            #     image=self.capture_worker.image_queue.get()
            #     self.process_image(image)
            # self.capture_worker.image_queue_lock.release()
            # self.recognitions_queue.put(self.tracked_objects)


        logging.info("Stopped recognition worker")

    def process_image(self,image):
        profiler=utils.Profiler()
        profiler.event("facerec")
        self.person_detections = self.face_recognizer.recognize(image)
        # logging.debug(f"{len(self.person_detections)} detections")
        if self.person_detections:
            bbox = self.person_detections[0].bbox
            # logging.info(f"Person detected at {bbox}")
        profiler.event("tracking")

        self.tracker.update(self.person_detections)
        self.tracked_objects = self.tracker.get_tracked_objects()
        profiler.event("queue")
        self.tracked_objects_queue.put((self.tracked_objects,image))

        # logging.info(f"{len(self.tracked_objects)} objects")
        if self.settings.learning.save_unrecognized_peoples_faces:
            profiler.event("saving")
            self.save_unrecognized_peoples_faces(image, self.tracked_objects)
        profiler.event("end")
        # logging.info(profiler.summary())

    def create_folders(self):
        time_in_ms = time.time()
        time_struct = time.localtime(time_in_ms)
        ms = time_in_ms % 1
        time_microseconds = int(ms * 1000)
        folder_format = '%Y-%m-%d'.format(time_microseconds)
        foldername = time.strftime(folder_format, time_struct)
        folderpath = os.path.join(self.settings.capture_path, foldername)
        recognized_subfolder = "recognized"
        recognized_folderpath = os.path.join(folderpath, recognized_subfolder)
        if not os.path.exists(folderpath):
            logging.info(f"Creating folder {folderpath}...")
            os.mkdir(folderpath)
            os.mkdir(recognized_folderpath)
        file_format = '%Y-%m-%d_%H:%M:%S:{}'.format(time_microseconds)
        filename = time.strftime(file_format, time_struct)

        return folderpath,recognized_folderpath,filename

    def save_unrecognized_peoples_faces(self,image,tracked_objects):

        for detection in tracked_objects:
            recognized=detection.recognized()
            save_recognized=  recognized and self.settings.learning.save_recognized_peoples_faces
            save_unrecognized = (not recognized) and self.settings.learning.save_unrecognized_peoples_faces

            if save_unrecognized  or save_recognized:

                top, right, bottom, left = detection.bbox()
                w, h = right - left, bottom - top
                if w>10 and h>10:

                    #get folderpath and create if non existent
                    folderpath, recognized_folderpath,filename =self.create_folders()
                    if recognized:
                        class_id, probability = detection.maximum_a_posteriori()
                        person=self.persondb[class_id]

                        recognized_folderpath=os.path.join(recognized_folderpath,person.foldername)
                        if not os.path.exists(recognized_folderpath):
                            os.mkdir(recognized_folderpath)
                        filename=f"{filename}_p{probability:0.2}"

                    save_folderpath = recognized_folderpath if recognized else folderpath
                    #generate filepath
                    filepath = os.path.join(save_folderpath, f"{filename}.png")
                    #get face subimage
                    face_image=image[top:bottom,left:right,:]

                    face_image=face_image.copy()
                    #self.image_saving_queue.put((image, self.tracked_objects))
                    self.image_saving_queue.put((filepath,face_image))
                    #save image
                    #cv2.imwrite(filepath, face_image)
                    if self.settings.learning.save_full_images:
                        full_image_filepath = os.path.join(save_folderpath, f"{filename}_full_{[top,left,w,h]}.png")
                        cv2.imwrite(full_image_filepath , image)

