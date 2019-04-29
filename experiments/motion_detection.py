import cv2
import settings
from backend import motion_detection
import matplotlib.pyplot as plt

stream_url=settings.input.stream_url
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    raise IOError("Cannot open webcam")

motion_detector=motion_detection.AdaptativeContourDetector(threshold=settings.capture.motion_detection_treshold)

f,((a1,a2,a3),(b1,b2,b3))=plt.subplots(2,3)

axes=[a1,a2,a3,b1,b2,b3]
names=["Image","Average Frame","absdiff",
       "gray","tresholded", "contour"]



frame=0
image_handles=[]
while True:
    retval,image=cap.read()
    if not retval:
        print(f"Frame {frame} not ready ")
        continue
    motion_detector.update(image)
    motion_detected=motion_detector.detect()
    # for ax in axes:
    #     ax.clear()
    contour_image=motion_detector.gray_frame.copy()

    cv2.drawContours(contour_image, motion_detector.contours, -1, (0, 255, 0), 3)

    images = [image, motion_detector.average_frame / 255, motion_detector.absdiff_frame,
              motion_detector.gray_frame, motion_detector.thresholded_frame,  contour_image]
    if frame == 0:
        for ax,name,image in zip(axes,names,images):
                handle=ax.imshow(image,vmin=0,vmax=255)
                ax.set_title(name)
                image_handles.append(handle)
    else:
        for ax, name, image,handle in zip(axes, names, images,image_handles):
            handle.set_data(image)
        plt.draw()
        plt.title(f"Motion detected: {motion_detected}, treshold: {motion_detector.threshold}")

    plt.pause(0.00000000000001)
    frame += 1






