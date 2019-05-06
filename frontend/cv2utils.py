import cv2


def overlay_image_alpha(img, img_overlay, pos, alpha_mask):
    """Overlay img_overlay on top of img at the position specified by
    pos and blend using alpha_mask.

    Alpha mask must contain values within the range [0, 1] and be the
    same size as img_overlay.
    """

    x, y = pos

    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to do
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    channels = img.shape[2]

    alpha = alpha_mask[y1o:y2o, x1o:x2o]
    alpha_inv = 1.0 - alpha

    for c in range(channels):
        img[y1:y2, x1:x2, c] = (alpha * img_overlay[y1o:y2o, x1o:x2o, c] +
                                alpha_inv * img[y1:y2, x1:x2, c])

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
