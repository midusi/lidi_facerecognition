
from PyQt5.QtCore import (QThread, Qt, pyqtSignal,pyqtSlot,QObject)
from backend.tracking import IOUTracker

import time
import logging, requests,pickle

from requests import exceptions


class RecognitionWorker(QObject):

    def __init__(self,face_recognizer,settings,persondb,parent=None):
        super().__init__(parent)
        self.face_recognizer=face_recognizer
        self.persondb=persondb
        self.frame=0
        self.person_detections=[]
        self.settings=settings
        self.tracker=IOUTracker(settings)

    persons_detected_signal = pyqtSignal(object)
    server_status_signal = pyqtSignal(object)

    def runHttp(self):
        url='http://localhost:8000/foo'
        connection_error=True
        self.server_status_signal.emit("offline")
        logging.warning(f"Connecting to server {url}...")

        while True:
            tracked_objects = []
            logging.debug("Making request....")
            try:
                time.sleep(self.settings.client.throttle_requests)
                r = requests.get(url)
                if r:
                    logging.debug("done")

            except exceptions.ConnectionError:
                if not connection_error:
                    connection_error=True
                    logging.warning(f"Server {url} is not available (retrying...).")
                    self.server_status_signal.emit("offline")
            else:
                try:
                    tracked_objects = pickle.loads(r.content)
                    logging.debug("Received data: " + str(tracked_objects))
                    if connection_error:
                        logging.warning(f"Server {url} available again.")
                        connection_error = False
                        self.server_status_signal.emit("online")
                except (EOFError,pickle.UnpicklingError):
                    logging.warning(f"Message from server {url} could not be unpickled.")
                    connection_error = True
                    self.server_status_signal.emit("offline")
            finally:
                self.persons_detected_signal.emit(tracked_objects)
