import cv2
import time
from backend.tracking import IOUTracker
import os
import logging,socket, threading
import pickle
from datetime import datetime
import utils
import threading
import multiprocessing
import queue
import numpy as np

from backend import framediff

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
        frame_ready=False
        while not frame_ready:
            frame_ready,image=cap.read()
        last_image=image.copy()
        profiler=utils.Profiler()
        logging.info(f"Capturing at {fw}x{fh}@{fps}, skip={self.settings.capture.frame_skip}")
        while not self.stop:

            cap.grab()
            for i in range(self.settings.capture.frame_skip):
                pass
            profiler.event("read")
            frame_ready = cap.retrieve(image=image)
            profiler.event("finished reading")

            if frame_ready:
                # logging.info(f"L1 distance between images: {distance}")
                if framediff.image_changed(last_image,image,self.settings.capture.different_images_threshold):
                    if self.image_queue.qsize()<self.settings.capture.max_elements_in_queue:
                        self.image_queue.put(image)
                last_image = image.copy()
            else:
                if not self.stop:
                    logging.info("stopped capturing")
                self.stop = True
            profiler.reset()
        logging.info("Stopped capture worker")


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
        self.tracked_objects_queue.put(self.tracked_objects)

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



class ServerWorker:

    def __init__(self,settings,recognition_worker):
        self.stop=False
        self.settings=settings
        logging.getLogger().setLevel(logging.DEBUG)
        self.recognition_worker=recognition_worker

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((settings.bind_ip, settings.bind_port))
        self.server.listen(5)  # max backlog of connections

        logging.info('Listening on {}:{}'.format(settings.bind_ip, settings.bind_port))

    def handle_client_connection(self,client_socket,address):
        address_str=f"{address[0]}:{address[1]}"
        logging.info(f'Thread spawned to handle connections from to {address_str}')

        try:
            while not self.stop:
                time.sleep(1)
                objects=self.recognition_worker.tracked_objects
                pickled_objects=pickle.dumps(objects)
                client_socket.send(pickled_objects)
                logging.debug('Sent ' + str(objects) + "to " + str())
            client_socket.close()
        except socket.timeout:
            logging.debug('Connection to {address_str} timed out.')


    def run(self):
        logging.info("Starting server worker..")

        while True:
            client_sock, address = self.server.accept()

            logging.info('Accepted connection from {}:{}'.format(address[0], address[1]))
            print('Accepted connection from {}:{}'.format(address[0], address[1]))
            client_handler = threading.Thread(
                target=self.handle_client_connection,
                args=(client_sock,address)
                # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
            )
            client_handler.setDaemon(True)

            client_handler.start()
