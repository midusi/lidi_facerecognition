import numpy as np
import skimage
from backend import framediff
import matplotlib.pyplot as plt
import skvideo.io as vio
import os
cwd = os.getcwd()
import progressbar

def evaluate_video(video,distance_functions):
    frames,h,w,c=video.shape
    distances={key:[] for key in distance_functions.keys()}

    for i in progressbar.progressbar(range(1,frames)):
        last=video[i-1,:]
        current=video[i,:]
        for key,df in distance_functions.items():
            distances[key].append(df(last,current))
    return distances

def plot_distances(distances,title):
    f,ax=plt.subplots(1,1,dpi=120)
    labels=[]
    for key,distance in distances.items():
        ax.plot(np.array(distance))
        labels.append(key)
    plt.legend(labels)
    plt.title(title)
    plt.savefig(f"{title}.png",dpi=120)

distance_functions={ "naive":framediff.distance_naive,
                      "erosion_default":lambda last,current: framediff.distance_erosion(last,current),
                      "erosion1":lambda last,current: framediff.distance_erosion(last,current,1),
                      "erosion3":lambda last,current: framediff.distance_erosion(last,current,3),
                      "erosion5":lambda last,current: framediff.distance_erosion(last,current,5),
                      # "gaussian_images0.2": lambda last,current: framediff.distance_gaussian(last,current,0.2),
                      "gaussian_images1": lambda last,current: framediff.distance_gaussian(last,current,1),
                      "gaussian_images3": lambda last,current: framediff.distance_gaussian(last,current,3),
                      "gaussian_images5": lambda last,current: framediff.distance_gaussian(last,current,5),
                        }
files=["active.mp4", "empty.mp4"]

for file in files:
    print(f"Processing video {file}:")
    video = vio.vread(file)
    video=video[:50,:]
    distances = evaluate_video(video, distance_functions)
    plot_distances(distances, file)

