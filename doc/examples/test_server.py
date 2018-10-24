import socket
import threading
import logging
import pickle
import time
# TEST SENDING OBJECT TRACKED OBJECTS

logging.getLogger().setLevel(logging.DEBUG)

bind_ip = '0.0.0.0'
bind_port = 9876

some_object={"server_foo":1,"server_bar":(2,3,"asd")}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

logging.info('Listening on {}:{}'.format(bind_ip, bind_port))


def handle_client_connection(client_socket):
    # request = pickle.loads(client_socket.recv(1024))
    try:
        for i in range(20):
            time.sleep(1)
            client_socket.send(pickle.dumps(some_object))
            logging.debug('Sent '+str(some_object)+ "to "+str(client_socket.getsockname()))

    client_socket.send(pickle.dumps("asd"))
    client_socket.send(pickle.dumps("close"))

    client_socket.close()

while True:
    client_sock, address = server.accept()

    logging.info('Accepted connection from {}:{}'.format(address[0], address[1]))
    client_handler = threading.Thread(
        target=handle_client_connection,
        args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
    )
    client_handler.setDaemon(True)

    client_handler.start()