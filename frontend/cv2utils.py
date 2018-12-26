import cv2

def draw_cut_rectangle(image, bbox, color, stroke, linetype):
    (top, right, bottom, left) = bbox
    w, h = right - left, bottom - top
    padw = w // 6
    padh = h // 6

    cv2.rectangle(image, (left, top), (left + padw, top), color, stroke, )
    cv2.rectangle(image, (left, top), (left, top + padh), color, stroke, )
    # tr
    cv2.rectangle(image, (right - padw, top), (right, top), color, stroke, lineType=linetype)
    cv2.rectangle(image, (right, top), (right, top + padh), color, stroke, lineType=linetype)

    # bl
    cv2.rectangle(image, (left, bottom), (left + padw, bottom), color, stroke, lineType=linetype)
    cv2.rectangle(image, (left, bottom - padh), (left, bottom), color, stroke, lineType=linetype)
    # br
    cv2.rectangle(image, (right - padw, bottom), (right, bottom), color, stroke, lineType=linetype)
    cv2.rectangle(image, (right, bottom - padh), (right, bottom), color, stroke, lineType=linetype)
