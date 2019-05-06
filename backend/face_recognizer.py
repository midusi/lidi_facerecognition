import face_recognition #https://github.com/ageitgey/face_recognition

from sklearn.externals import joblib

import numpy as np
import cv2
import utils
import logging

class PersonDetection:
    def __init__(self,class_id,bbox,class_probabilities,face_image,landmarks):
        self.class_id=class_id
        self.bbox=bbox
        self.class_probabilities=class_probabilities
        self.face_image=face_image
        self.landmarks=landmarks

class FaceEmbeddingClassifier:
    def __init__(self,settings):
        self.settings=settings
        self.face_classification_model = joblib.load(settings.model_path)

    def classify(self,embedding):
        probabilities=self.face_classification_model.predict_proba(embedding)
        return id,probabilities[0,:]

    def update_face_classification_model(self, model):
        self.face_classification_model=model



class FaceRecognizer:
    def __init__(self,settings,face_classifier):
        self.settings=settings
        self.face_classifier=face_classifier
    def update_face_classification_model(self,model):
        self.face_classifier.update_face_classification_model(model)

    def detect_and_embeddings(self,image):
        face_locations = face_recognition.face_locations(image,                                                        number_of_times_to_upsample=self.settings.number_of_times_to_upsample)
        face_landmarks= face_recognition.face_landmarks(image,face_locations,model="small")

        face_encodings = face_recognition.face_encodings(image, face_locations)
        return face_locations,face_encodings,face_landmarks

    def recognize(self,image):
        def extend_bboxes(image,bboxes,scale):
            h, w, c = image.shape
            def extend_bbox(bbox):
                top,right,bottom,left=bbox
                pw,ph=(right-left)*scale,(bottom-top)*scale
                pw,ph=int(pw),int(ph)
                bbox=[max(0, top - ph), min(w, right + pw), min(bottom + pw, h), max(0, left - pw)]
                return np.array(bbox,dtype="int")
            return list(map(extend_bbox,bboxes))

        profiler=utils.Profiler()
        profiler.event("resize")
        downsampled_image= cv2.resize(image, (0, 0), fx=1 / self.settings.recognition.downsampling,
                                     fy=1 / self.settings.recognition.downsampling)
        profiler.event("detect and calc embeddings")
        face_locations,face_embeddings,face_landmarks=self.detect_and_embeddings(downsampled_image)
        profiler.event("adapt bounding boxes")
        face_locations=[np.array(bbox) * self.settings.recognition.downsampling for bbox in face_locations]
        face_locations_extended=extend_bboxes(image,face_locations,
                                              self.settings.recognition.face_image_extension_factor)
        face_images= [image[top:bottom, left:right] for (top, right, bottom, left) in face_locations_extended]
        profiler.event("svm")
        persons=self.recognize_bboxes(face_locations,face_embeddings,face_landmarks,face_images)
        profiler.event("end")
        logging.debug(profiler.summary())
        return persons


    def recognize_bboxes(self,face_locations,face_encodings,face_landmarks,face_images):
        person_detections=[]
        for bbox, encoding, landmarks, face_image in zip(face_locations, face_encodings,face_landmarks,face_images):
            id,class_probabilities= self.face_classifier.classify(encoding.reshape(1, -1))

            person_detection = PersonDetection(id,bbox,class_probabilities,face_image,landmarks)
            person_detections.append(person_detection)
        return person_detections

