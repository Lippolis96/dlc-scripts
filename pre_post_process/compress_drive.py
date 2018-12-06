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
# localFolder = os.path.basename(os.path.dirname(inputpath))
localFolder = os.path.basename(inputpath)
outputpath = os.path.join(path, localFolder + "_compressed")

print("Copying structure from")
print("  ", inputpath)
print("to")
print("  ", outputpath)
print("---------------------------------------")

for dirpath, dirnames, filenames in os.walk(inputpath):
    # Get current relative path
    relpath = os.path.relpath(dirpath, inputpath)
    if relpath == ".":
        relpath = ""

    # Make a new folder
    newfolderoutpath = os.path.join(outputpath, relpath)

    if not os.path.isdir(newfolderoutpath):
        print("Making directory:", newfolderoutpath)
        os.mkdir(newfolderoutpath)
    else:
        print("-->Warning: skipping existing directory", newfolderoutpath)

    # List all filenames in that folder
    for filename in filenames:
        if os.path.splitext(filename)[1] == ".avi":
            inFilePathName = os.path.join(dirpath, filename)
            outFilePathName = os.path.join(os.path.join(outputpath, relpath), filename)

            # print("converting file", inFilePathName, "to", outFilePathName)

            if os.path.isfile(outFilePathName):
                print("--->Warning: skipping already existing file", outFilePathName)
            else:
                convert(inFilePathName, outFilePathName)
