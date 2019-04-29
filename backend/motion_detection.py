
import cv2 as cv
import numpy as np
from skimage import color
from datetime import datetime
import time

class AdaptativeContourDetector():

    def __init__(self, threshold=0.15,running_average_alpha=0.95,bw_threshold=25,gaussian_size=3):

        self.threshold = threshold
        self.alpha=running_average_alpha
        self.bw_threshold=bw_threshold
        self.gaussian_size=gaussian_size
        self.clear()

    def clear(self):
        self.gray_frame = None
        self.absdiff_frame = None
        self.previous_frame = None
        self.contour_area = 0
        self.contours = None
        self.initialized=False

    def update_and_detect(self,image):
        self.update(image)
        return self.detect()

    def update(self, frame):

        cv.GaussianBlur(frame, (self.gaussian_size,self.gaussian_size), 0, dst=frame)  # Remove false positives

        if not self.initialized:
            h,w,c=frame.shape
            self.image_area = h * w
            self.average_frame = np.zeros(frame.shape, np.float32)
            self.average_frame[:] = frame[:]  # don't copy, convert since average_frame is float32
            self.absdiff_frame = frame.copy()
            self.gray_frame = np.zeros((h,w), np.uint8)
            self.thresholded_frame = self.gray_frame.copy()
            erode_size=np.sqrt(self.image_area).astype(np.uint8)//60
            dilate_size=erode_size*3//2
            self.dilate_kernel = np.ones((dilate_size, dilate_size), np.uint8)
            self.erode_kernel = np.ones((erode_size, erode_size), np.uint8)

            self.initialized=True
        else:
            cv.accumulateWeighted(frame, self.average_frame, 1 - self.alpha)  # Compute the average
        cv.absdiff(frame,self.average_frame.astype(np.uint8),dst=self.absdiff_frame)
        cv.cvtColor(self.absdiff_frame,cv.COLOR_BGR2GRAY,dst=self.gray_frame)
        cv.threshold(self.gray_frame, self.bw_threshold, 255, cv.THRESH_BINARY,dst=self.thresholded_frame )

        cv.dilate(self.thresholded_frame, self.dilate_kernel, dst=self.thresholded_frame)
        cv.erode(self.thresholded_frame, self.erode_kernel, dst=self.thresholded_frame)
        self.contours, hierarchy = cv.findContours(self.thresholded_frame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        contours = self.contours  # Save contours
        self.contour_area = 0  # Put back the current surface to 0
        for contour in contours:
            self.contour_area += cv.contourArea(contour)
        self.contour_area_percentage = self.contour_area / self.image_area  # Calculate the average of contour area on the total size

    def detect(self):
        # Find contours
        return self.contour_area_percentage > self.threshold


