import face_recognition
import cv2
import os
import numpy as np
from PIL import Image
import pickle

from time import gmtime, strftime
import time
import settings



print(f"Saving images to {settings.capture_path}.")




cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
cap.set(cv2.CAP_PROP_FPS,30)
fw,fh=cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"Capturing at {fw}x{fh}@{fps}")

downsampling=1
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    small_frame = cv2.resize(frame, (0, 0), fx=1/downsampling, fy=1/downsampling)
    # Our operations on the frame come here
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_locations = face_recognition.face_locations(small_frame)

    for bbox in face_locations:# encoding in zip(face_locations,face_encodings):
        bbox = np.array(bbox)*downsampling

        (top, right, bottom, left) = bbox
        time_in_ms = time.time()
        time_struct=time.localtime(time_in_ms)
        ms=time_in_ms % 1
        time_format='%Y-%m-%d %H:%M:%S:{}'.format( int(ms * 1000))
        timestamp = time.strftime(time_format, time_struct)
        face = frame[top:bottom, left:right]
        image_path = os.path.join(settings.capture_path, f"{timestamp}.png")

        cv2.imwrite(image_path, face)

        color = (255, 0, 0)  # BGR 0-255
        stroke = 2
        cv2.rectangle(frame, (left, top), (right, bottom), color, stroke)

    # Display the resulting frame
    cv2.imshow('frame',frame)
    #cv2.imshow('gray',gray)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()



