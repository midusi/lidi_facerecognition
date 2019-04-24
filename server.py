
from server.capture import CaptureWorker
from server.recognition import RecognitionWorker
from server.serve import ServerWorker

from backend import facedb
from backend.face_recognizer import FaceEmbeddingClassifier, FaceRecognizer

import settings
import multiprocessing

import time, threading,sys
import atexit
import logging


def setup_thread(function, name):
    thread = threading.Thread(target=function,name=name)
    thread.setDaemon(True)
    thread.start()
    return thread




def setup_process(function, name):
    process = multiprocessing.Process(target=function,name=name)
    process.start()
    return process


if __name__ == '__main__':
    import os
    print(os.getcwd(),"\n",__file__)

    def cleanup():
        logging.info("cleaning up...")
        server_process.terminate()
        recognition_process.terminate()
        capture_process.terminate()

        capture_worker.stop=True
        recognition_worker.stop = True
        server.stop=True

        logging.info("finished cleaning up.")


    #logging.getLogger().setLevel(logging.INFO)

    manager = multiprocessing.Manager()
    shared_list = manager.list()

    persondb = facedb.load_persondb(settings.face_database_path)

    face_classifier = FaceEmbeddingClassifier(settings)
    face_recognizer = FaceRecognizer(settings, face_classifier)

    capture_worker = CaptureWorker(settings)
    capture_process=setup_process(capture_worker.run, "Capture Thread")

    recognition_worker  = RecognitionWorker(face_recognizer,settings,persondb,capture_worker)
    recognition_process = setup_process(recognition_worker.run, "Recognition Thread")

    server=ServerWorker(settings,recognition_worker)
    server_thread = setup_process(server.run,"Server Thread")

    atexit.register(cleanup)

    try:
        while True:
            time.sleep(30)
    except (KeyboardInterrupt, SystemExit):
        # cleanup()
        sys.exit()
