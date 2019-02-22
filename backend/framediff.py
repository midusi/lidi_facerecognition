from skimage.morphology import erosion,square
from skimage.filters import gaussian
import numpy as np


def distance_naive(last,current):
    if len(last.shape)==3:
        last = last.mean(axis=2)
        current = current.mean(axis=2)
    diff = last - current
    distance = np.mean(np.abs(diff))
    return distance


def show_comparison(diff,transformed,title):
    import matplotlib.pyplot as plt
    f, (a1, a2) = plt.subplots(1, 2)
    r1 = a1.imshow(diff)
    plt.colorbar(r1)
    # f.colorbar(r1, ax=a1)
    r2 = a2.imshow(transformed)
    # f.colorbar(r2,diff, ax=a2)
    plt.colorbar(r2)

    plt.title(title)
    plt.show()


def distance_gaussian(last,current,sigma):
    if len(last.shape)==3:
        last = last.mean(axis=2)
        current = current.mean(axis=2)

    last_blurred=gaussian(last, sigma)
    current_blurred=gaussian(current,sigma)
    diff = last_blurred - current_blurred
    #show_comparison(last-current,diff,f"sigma {sigma}")
    distance = np.mean(np.abs(diff))
    return distance

def distance_gaussian(last,current,sigma):
    if len(last.shape)==3:
        last = last.mean(axis=2)
        current = current.mean(axis=2)

    last_blurred=gaussian(last, sigma)
    current_blurred=gaussian(current,sigma)
    diff = last_blurred - current_blurred
    #show_comparison(last-current,diff,f"sigma {sigma}")
    distance = np.mean(np.abs(diff))
    return distance

def distance_erosion(last,current,selem_size=None):
    # if rgb, transform to grayscale
    if len(last.shape)==3:
        last = last.mean(axis=2)
        current = current.mean(axis=2)

    diff = last - current
    diff = np.abs(diff)
    #selem=np.ones((5,5))

    if selem_size==None:
        diff = erosion(diff)
    else:
        selem = square(selem_size)
        diff = erosion(diff, selem)
    #show_comparison(last - current,diff,f"selem {selem_size}")
    distance = np.mean(diff)
    return distance

def image_changed( last, current, threshold):
    return distance_erosion(last, current)>threshold