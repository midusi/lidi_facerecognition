from utils import Clock
import numpy as np
from enum import Enum

class TrackingStatus(Enum):
    Warmup = 1
    Unrecognized = 2
    Recognized = 3


class TrackedObject:
    def __init__(self,settings,max_window_size=30):
        self.detections=[]
        self.times=[]
        self.settings=settings
        self.max_window_size=max_window_size
    def __str__(self):
        last_position=""
        n=len(self.detections)
        if (n>0):
            detection=self.last_detection()
            right, top, left, bottom=detection.bbox

            last_position= f"right:{right}, top={top}, left={left}, bottom={bottom}"
        return f"TrackedObject: {n} frames"+last_position

    def add_frame(self,frame,time):
        self.detections.append(frame)
        self.times.append(time)
        if len(self.detections)>self.max_window_size:
            del self.detections[0]
            del self.times[0]

    def mean_probabilities_per_class(self):
        class_probabilities = np.array([d.class_probabilities for d in self.detections])
        mean_probabilities = class_probabilities.mean(axis=0)
        return mean_probabilities

    def maximum_a_posteriori(self):
        mean_probabilities=self.mean_probabilities_per_class()
        id=mean_probabilities.argmax()
        return id,mean_probabilities[id]

    def score(self):
        class_id,probability=self.maximum_a_posteriori()
        return probability

    def bbox(self):
        return self.last_detection().bbox
    def landmarks(self):
        return self.last_detection().landmarks
    def class_id(self):
        class_id, probability = self.maximum_a_posteriori()
        return class_id

    def face_image(self):
        return self.last_detection().face_image

    def last_time(self):
        return self.times[-1]

    def last_detection(self):
        return self.detections[-1]

    def time_since_last_detection(self,now):
        return now-self.last_time()

    def is_alive(self,now,ttl):
        return self.time_since_last_detection(now)<ttl

    def time_elapsed(self):
        if self.times:
            return self.times[-1]-self.times[0]
        else:
            return 0

    def tracking_converged(self):
        wt = self.settings.warmup_time
        ms = self.settings.minimum_samples
        return self.time_elapsed() >= wt and len(self.detections) >= ms

    def tracking_convergence_progress(self):
        wt = self.settings.warmup_time
        ms = self.settings.minimum_samples
        warmup_progress=min(1,self.time_elapsed()/wt)
        sample_progress=min(1,len(self.detections) /ms)
        return 0.5*warmup_progress+0.5*sample_progress

    def get_status(self):
        if not self.tracking_converged():
            return TrackingStatus.Warmup
        elif self.recognized():
            return TrackingStatus.Recognized
        else:
            return TrackingStatus.Unrecognized

    def recognized(self):
        t=self.settings.face_classification_treshold_proba
        return self.score()>t



class IOUTracker:
    def __init__(self, settings):
        self.settings=settings
        # each element of tracked_bboxes is a list of the latest
        # detections of the "same" bbox or widgets
        self.tracked_objects=[]
        self.clock=Clock()

    def update(self,detections):
        self.clock.update()

        # update old boxes
        detections=detections.copy()
        objects_to_remove=[]

        for i,obj in enumerate(self.tracked_objects):
            if detections:
                ious = self.calculate_ious(detections,obj.last_detection())
                best_match=ious.argmax()
            else:
                ious=np.array([0])
                best_match=0

            if ious[best_match]>self.settings.tracking.iou_threshold:
                obj.add_frame(detections[best_match],self.clock.time)
                del detections[best_match]
            else:
                if not obj.is_alive(self.clock.time,self.settings.tracking.ttl_initial):
                    objects_to_remove.append(i)

        for i in reversed(objects_to_remove):
            del self.tracked_objects[i]

        # add new ones
        for detection in detections:
            tracked_object=TrackedObject(self.settings.tracking)
            tracked_object.add_frame(detection,self.clock.time)
            self.tracked_objects.append(tracked_object)

    def calculate_ious(self,detections,detection):

        bboxA=np.array([d.bbox for d in detections])
        bboxB=detection.bbox[None,:]

        topA,rightA,bottomA,leftA=np.split(bboxA,4,axis=1)
        topB, rightB, bottomB, leftB = np.split(bboxB, 4, axis=1)

        top = np.maximum(topA, topB.T)
        left = np.maximum(leftA, leftB.T)
        right = np.minimum(rightA, rightB.T)
        bottom = np.minimum(bottomA, bottomB.T)

        intersection=np.maximum(0,bottom-top)*np.maximum(0,right-left)

        areaA = (rightA-leftA)*(bottomA-topA)
        areaB = (rightB - leftB) * (bottomB - topB)

        union=areaA+areaB.T-intersection
        iou=intersection/union

        # bboxes[2]-bboxes[0]
        # top, right, bottom, left = bbox

        return iou[:,0]



    def sort_and_remove_repeated_ids(self,tracked_objects):

        def sortkey(o):
            converged=o.tracking_converged()
            id,prob=o.maximum_a_posteriori()
            return (converged,id,prob)

        tracked_objects.sort(key=sortkey)
        i = 1
        while i < len(tracked_objects):
            tracking_converged=tracked_objects[i - 1].tracking_converged()
            same_id=tracked_objects[i - 1].class_id() == tracked_objects[i].class_id()
            if tracking_converged and same_id:
                del tracked_objects[i - 1]
            i += 1

    def get_tracked_objects(self):

        tracked_objects=self.tracked_objects.copy()

        self.sort_and_remove_repeated_ids(tracked_objects)

        return tracked_objects
