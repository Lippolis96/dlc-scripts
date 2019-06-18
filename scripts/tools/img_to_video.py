######################################
# Takes folder with images (RGB) and converts them to .AVI video
#
# How to use:
#
# python3 img_to_video.py <path/to/folder/with/images> <outputfilename.avi>
#
# Author: Aleksejs Fomins
# Last Edit: 18.06.2019
######################################

import numpy as np
import os, sys
import matplotlib
import cv2
from time import time

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

path = sys.argv[1]
outPathName = sys.argv[2]
basenames = os.listdir(path)
fullpaths = [os.path.join(path, base) for base in basenames]

# Load 1 picture to get its shape
img=mpimg.imread(fullpaths[0])

fps = 30
shape = img.shape[:2]
shape = (shape[1], shape[0])
#fourcc = cv2.VideoWriter_fourcc(*'MJPG')
fourcc = cv2.VideoWriter_fourcc(*'XVID')

out = cv2.VideoWriter(outPathName, fourcc, fps, shape, isColor=True)
flip_order = np.array([2, 1, 0])

t_start = time()

for i, fpath in enumerate(fullpaths):
    print('Processing image[%d]\r'%i, end="")
    
    img = mpimg.imread(fpath)
    out.write(img[:, :, flip_order])
    
out.release()

print("Took time:", time() - t_start)
