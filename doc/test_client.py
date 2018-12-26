import socket
import logging
import pickle
import backend

logging.getLogger().setLevel(logging.DEBUG)

some_object={"foo":1,"bar":(2,3)}

# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
# client.connect((target, port))
client.connect(('0.0.0.0', 9876))

# send some data (in this case a HTTP GET request)


# receive the response data (4096 is recommended buffer size)

while True:
    responses=[]
    response= client.recv(4096)
    while response:
        responses.append(response)
        response = client.recv(4096)

    joined_response=b"".join(responses)
    message= pickle.loads(response)
    if isinstance(message, str):
        if  message=="close":
            logging.info("Closing connection")
            break
        else:
            logging.warning("Unknown commmand:" + str(message))
    else:
        logging.info("Received data: " + str(message)+" from "+str(client.getpeername()))



client.shutdown(socket.SHUT_RDWR)
client.close()
logging.info("Connection closed.")