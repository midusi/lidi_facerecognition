from http.server import HTTPServer
from server.handlers import RecognitionRequestHandler
import time

import logging,socket
import pickle

import threading

def setup_thread(function, name):
    thread = threading.Thread(target=function,name=name)
    thread.setDaemon(True)
    return thread



class ServerWorker:

    def __init__(self,settings,recognition_worker):
        self.stop=False
        self.settings=settings
        logging.getLogger().setLevel(logging.INFO)
        self.recognition_worker=recognition_worker

        self.http_server = HTTPServer(('', 8000), RecognitionRequestHandler)
        self.http_server.server_worker = self
        self.http_server_thread = setup_thread(self.http_server.serve_forever, "HTTPServer Thread")



    def run(self):
        logging.info("Starting server worker..")
        # initialize the tracked_objects and image variables
        self.tracked_objects, self.image = self.recognition_worker.tracked_objects_queue.get()

        #  start the http_server_thread from here so that it shares memory with this process and can read
        # the self.tracked_objects and self.image variables
        self.http_server_thread.start()

        # continuously run and get & update the latest image and tracked objects
        while True:
            self.tracked_objects, self.image = self.recognition_worker.tracked_objects_queue.get()







# class ServerWorker:
#
#     def __init__(self,settings,recognition_worker):
#         self.stop=False
#         self.settings=settings
#         logging.getLogger().setLevel(logging.DEBUG)
#         self.recognition_worker=recognition_worker
#
#         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server.bind((settings.bind_ip, settings.bind_port))
#         self.server.listen(5)  # max backlog of connections
#
#         logging.info('Listening on {}:{}'.format(settings.bind_ip, settings.bind_port))
#
#     def handle_client_connection(self,client_socket,address):
#         address_str=f"{address[0]}:{address[1]}"
#         logging.info(f'Thread spawned to handle connections from to {address_str}')
#
#         try:
#             while not self.stop:
#                 time.sleep(1)
#                 objects=self.recognition_worker.tracked_objects
#                 pickled_objects=pickle.dumps(objects)
#                 client_socket.send(pickled_objects)
#                 logging.debug('Sent ' + str(objects) + "to " + str())
#             client_socket.close()
#         except socket.timeout:
#             logging.debug('Connection to {address_str} timed out.')
#
#
#     def run(self):
#         logging.info("Starting server worker..")
#
#         while True:
#             client_sock, address = self.server.accept()
#
#             logging.info('Accepted connection from {}:{}'.format(address[0], address[1]))
#             print('Accepted connection from {}:{}'.format(address[0], address[1]))
#             client_handler = threading.Thread(
#                 target=self.handle_client_connection,
#                 args=(client_sock,address)
#                 # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
#             )
#             client_handler.setDaemon(True)
#
#             client_handler.start()
