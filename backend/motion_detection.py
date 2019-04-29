
import cv2 as cv
import numpy as np

from datetime import datetime
import time

class AdaptativeContourDetector():

    def __init__(self, threshold=0.25):

        self.threshold = threshold
        self.clear()

    def clear(self):
        self.gray_frame = None
        self.absdiff_frame = None
        self.previous_frame = None
        self.contour_area = 0
        self.contours = None
        self.dilate_kernel = np.ones((5, 5), np.uint8)
        self.erode_kernel = np.ones((5, 5), np.uint8)

    def update(self, frame):
        if not self.gray_frame:

            self.gray_frame = np.zeros(frame.shape, np.uint8)
            self.gray_frame = np.zeros(frame.shape, np.uint8)
            self.average_frame = np.zeros(frame.shape, np.float32)
            self.image_area = frame.shape[0] * frame.height.shape[1]

        cv.GaussianBlur(frame,dst=frame)# Remove false positives

        if not self.absdiff_frame:  # For the first time put values in difference, temp and moving_average
            self.absdiff_frame = frame.copy()
            self.previous_frame = frame.copy()
            self.average_frame[:]=frame[:] # Should convert because after runningavg take 32F pictures
        else:
            alpha=0.95
            cv.accumulateWeighted(frame,self.average_frame,0.05)# Compute the average
            #self.average_frame= self.average_frame*alpha+frame*(1-alpha)


        cv.Convert(self.average_frame, self.previous_frame)  # Convert back to 8U frame

        cv.absdiff(frame, self.previous_frame, self.absdiff_frame)  # moving_average - curframe
        cv.convert

        cv.CvtColor(self.absdiff_frame, self.gray_frame, cv.CV_RGB2GRAY)  # Convert to gray otherwise can't do threshold
        cv.Threshold(self.gray_frame, self.gray_frame, 50, 255, cv.CV_THRESH_BINARY)
        cv.dilate(self.gray_frame,15,dst=self.gray_frame)
        cv.erode(self.gray_frame, 10, dst=self.gray_frame)


        cv.Dilate(self.gray_frame, self.gray_frame, None, 15)  # to get object blobs
        cv.Erode(self.gray_frame, self.gray_frame, None, 10)
    def update_and_detect(self,image):
        self.update(image)
        return self.detect()
    def detect(self):

        # Find contours
        storage = cv.CreateMemStorage(0)
        contours = cv.FindContours(self.gray_frame, storage, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_SIMPLE)

        self.contours = contours  # Save contours

        self.contour_area = 0  # Put back the current surface to 0
        while contours:  # For all contours compute the area
            self.contour_area += cv.ContourArea(contours)
            contours = contours.h_next()

        contour_area_percentage = self.contour_area / self.image_area  # Calculate the average of contour area on the total size


        return contour_area_percentage > self.threshold


