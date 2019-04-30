
from server.capture import CaptureWorker
from server.recognition import RecognitionWorker
from server.webserver import WebserverWorker

from backend import facedb
from backend.face_recognizer import FaceEmbeddingClassifier, FaceRecognizer

import settings
import multiprocessing

import time, threading,sys
import atexit
import logging
import setproctitle

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


    def cleanup():
        logging.info("[main] Shutting down...")
        # Stop processes. The stopping order is important since some processes depend on others
        webserver_worker.stop()
        recognition_worker.stop()
        capture_worker.stop()

        logging.info("[main] terminating processes just in case...")
        server_process.terminate()
        recognition_process.terminate()
        capture_process.terminate()

        logging.info("[main] finished cleaning up.")

    #logging.getLogger().setLevel(logging.INFO)

    # set main process title
    process_title = f"[main] {setproctitle.getproctitle()}"
    setproctitle.setproctitle(process_title)

    # load person database, classifier and face recognizer
    persondb = facedb.load_persondb(settings.face_database_path)
    face_classifier = FaceEmbeddingClassifier(settings)
    face_recognizer = FaceRecognizer(settings, face_classifier)

    # register exit function
    atexit.register(cleanup)

    # Generate workers and processes
    capture_worker = CaptureWorker(settings)
    capture_process = setup_process(capture_worker.run, "Capture")

    recognition_worker  = RecognitionWorker(face_recognizer,settings,persondb,capture_worker)
    recognition_process = setup_process(recognition_worker.run, "Recognition")

    webserver_worker = WebserverWorker(settings, recognition_worker, capture_worker)
    server_process = setup_process(webserver_worker.run, "Webserver")

    try:
        #wait for processes to finish
        # server_process.join()
        # recognition_process.join()
        # capture_process.join()
        while True:
            time.sleep(30)
    except (KeyboardInterrupt, SystemExit):
        # cleanup()
        sys.exit()
