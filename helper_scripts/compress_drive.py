######################################################
# Video Compressor in BULK
#
# Input path to a folder via command line argument
#
# A new folder will be created in the same parent, called $folder$_compressed
#
# The subfolder structure inside new folder will be copied
#
# All .avi files in the original folder will be compressed and
# saved with the same name in the _compressed folder substructure
######################################################

import sys
import os
import cv2

def convert(inPathName, outPathName):
    # Reader
    capture = cv2.VideoCapture(inPathName)
    nFrame = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frameShape = (width, height)

    # Writer
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(outPathName,fourcc, fps, frameShape, isColor=False)

    print("Converting file", inPathName, "to", outPathName)
    print("total frames", nFrame, "shape", frameShape, "fps", fps)

    # Convert
    while True:
        ret, frame = capture.read()
        if ret:
            out.write(frame[:,:,0])
        else:
            break


    # Release everything if job is finished
    out.release()


# Get path to video folder
inputpath = sys.argv[1]
path = os.path.abspath(os.path.join(inputpath, os.pardir))
localFolder = "".join(inputpath[len(path):].split('/'))
outputpath = path + "/" + localFolder + "_compressed/"

print("Copying structure from")
print("  ", inputpath)
print("to")
print("  ", outputpath)
print("---------------------------------------")

for dirpath, dirnames, filenames in os.walk(inputpath):
    # Get current relative path
    relpath = dirpath[len(inputpath):]
    print("Making directory:", outputpath+relpath)

    # Make a new folder
    newfolderoutpath = os.path.join(outputpath, relpath)
    if not os.path.isdir(newfolderoutpath):
        os.mkdir(newfolderoutpath)
    else:
        print("-->Warning: Directory already exists!")

    # List all filenames in that folder
    for filename in filenames:
        if os.path.splitext(filename)[1] == ".avi":
            inFilePathName = inputpath + relpath + "/" + filename
            outFilePathName = outputpath + relpath + "/" + filename
            convert(inFilePathName, outFilePathName)
