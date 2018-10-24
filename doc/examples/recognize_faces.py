import face_recognition
import cv2
import os
import numpy as np
from PIL import Image
import pickle
import sklearn

import skimage,skimage.io,skimage.exposure

from PIL import Image, ImageTk

import argparse
import datetime
import cv2
import os


import time
from sklearn.externals import joblib
import settings
data=np.load(settings.training_data_file)
x_train,y_train=data["x_train"],data["y_train"]
person_to_id,id_to_person=data["person_to_id"].item(),data["id_to_person"].item()

face_classification_model=joblib.load(settings.model_path)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
cap.set(cv2.CAP_PROP_FPS,30)
fw,fh=cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"Capturing at {fw}x{fh}@{fps}")

DEF equalize(image):
    img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)

    # equalize the histogram of the Y channel
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])

    # convert the YUV image back to RGB format
    return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)


downsampling=1
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    small_frame = cv2.resize(frame, (0, 0), fx=1/downsampling, fy=1/downsampling)
# Our operations on the frame come here
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_locations = face_recognition.face_locations(small_frame,number_of_times_to_upsample=1)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    for bbox,encoding in zip(face_locations,face_encodings):
        bbox = np.array(bbox)*downsampling

        (top, right, bottom, left) = bbox
        matches=face_recognition.compare_faces(x_train,encoding)

        # person="Desconocido"
        # if True in matches:
        #     first_match_index = matches.index(True)
        #     id=y_train[first_match_index]
        #     person= id_to_person[id]
        id=face_classification_model.predict(encoding.reshape(1,-1))
        person=id_to_person[id[0]]

        color = (255, 0, 0)  # BGR 0-255
        stroke = 2
        cv2.rectangle(frame, (left, top), (right, bottom), color, stroke)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, person, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


    # Display the resulting frame
    cv2.imshow('frame',frame)
    #cv2.imshow('gray',gray)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
