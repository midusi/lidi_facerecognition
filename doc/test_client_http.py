import socket
import logging
import pickle
import backend
import requests


logging.getLogger().setLevel(logging.DEBUG)
# send some data (in this case a HTTP GET request)


# receive the response data (4096 is recommended buffer size)

while True:
    logging.debug("Making request")
    r = requests.get('http://localhost:8000/foo')
    logging.debug("done")
    # message = r.text
    # r.encoding="utf-8"
    # # logging.debug("Received response with lenght"+str(len(message)))
    # logging.debug(message[:20])
    # message = message.encode("utf-8")
    # logging.debug("Decoding")
    message= pickle.loads(r.content)


    logging.debug("Received data: " + str(message))

logging.info("Connection closed.")