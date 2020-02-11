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

# Append base directory
projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)

from lib.qt_wrapper import gui_fpath, gui_fsave
from lib.os_lib import get_files
from lib.video_convert_lib import merge_images_cv2

srcPath = gui_fpath("Select path to image files", "./")
outPathName = gui_fsave("Save result to a video", srcPath, "AVI files (*.avi)")

basenames = np.sort(get_files(srcPath, ".png"))
fullpaths = [os.path.join(srcPath, base) for base in basenames]

merge_images_cv2(fullpaths, outPathName, fps=30, FOURCC='XVID', isColor=False)