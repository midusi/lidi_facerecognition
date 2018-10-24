import cv2
import os
import numpy as np
from PIL import Image
import pickle

from time import gmtime, strftime
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
recorded_images_path = os.path.join(BASE_DIR, "images")
print(f"Saving images to {recorded_images_path}.")
face_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_alt2.xml')
profile_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_profileface.xml')
cascades=[face_cascade,profile_cascade]


#recognizer = cv2.face.LBPHFaceRecognizer_create()



cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
cap.set(cv2.CAP_PROP_FPS,30)
fw,fh=cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"Capturing at {fw}x{fh}@{fps}")
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces=np.empty((0,4),dtype='uint8')
    for cascade in cascades:
        cascade_faces = face_cascade.detectMultiScale(frame, scaleFactor=1.5, minNeighbors=5)

        if len(cascade_faces)>0:
            faces=np.vstack([faces,cascade_faces])



    for (x, y, w, h) in faces:
        color = (255, 0, 0)  # BGR 0-255
        stroke = 2
        end_cord_x = x + w
        end_cord_y = y + h
        cv2.rectangle(frame, (x, y), (end_cord_x, end_cord_y), color, stroke)
        time_in_ms=time.time()
        timestamp=time.strftime('%Y-%m-%d %H:%M:%S:{}'.format(time_in_ms % 1000), time.gmtime(time_in_ms / 1000.0))

        face = frame[y:y + h, x:x + w]
        image_path=os.path.join(recorded_images_path,f"{timestamp}.png")
        print(image_path)
        cv2.imwrite(image_path,face)



    # Display the resulting frame
    cv2.imshow('frame',frame)
    #cv2.imshow('gray',gray)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()


