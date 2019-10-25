import numpy as np
import subprocess
import cv2
import matplotlib.image as mpimg


# Convert video from LOSSLESS AVI to MJPG or XVID
def convert_cv2(inPathName, outPathName, FOURCC='MJPG', crop=None, isColor=False):
    if FOURCC not in ['MJPG', 'XVID']:
        raise ValueError("Unexpected target encoding", FOURCC)
    
    # Reader
    capture = cv2.VideoCapture(inPathName)
    nFrame = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    if crop is not None:
        xmin, xmax, ymin, ymax = crop
        width = xmax - xmin
        height = ymax - ymin

    # Writer
    frameShape = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*FOURCC)
    out = cv2.VideoWriter(outPathName, fourcc, fps, frameShape, isColor=isColor)

    print("Converting file", inPathName, "to", outPathName)
    print("total frames", nFrame, "shape", frameShape, "fps", fps)

    # Convert
    while True:
        ret, frame = capture.read()
        if ret:
            if crop is not None:
                frame = frame[xmin:xmax,ymin:ymax]

            if not isColor:
                frame = frame[:,:,0]

            out.write(frame)
        else:
            break


    # Release everything if job is finished
    out.release()
    

# Convert video from any AVI to any other
def convert_ffmpeg_h265(src_name, trg_name, lossless=False, crf=22, gray=False, crop=None):    
    task = ["ffmpeg","-i", src_name]
    
    # Determine color
    if gray:
        task += ["-vf", "format=gray"]
        
    # Crop if necessary
    if crop is not None:
        xmin, xmax, ymin, ymax = crop
        out_w = xmax - xmin
        out_h = ymax - ymin
        task += ["-vf", "crop="+str(out_w)+":"+str(out_h)+":"+str(xmin)+":"+str(ymin)] #"--filter:v"
    
    # VCodec
    task += ["-c:v", "libx265"]
    
    # Determine quality
    if lossless:
        task += ["-x265-params", "lossless=1"]
    else:
        task += ["-preset", "slow", "-x265-params", "crf=22"]
        
    # Target must appear at the end of the task
    task += [trg_name]
    
    # Run
    subprocess.run(task)


# Convert a set of images to a video
def merge_images_cv2(srcPaths, trgPathName, fps=30, FOURCC='MJPG', isColor=False):
    print("Writing video to", trgPathName)

    if FOURCC not in ['MJPG', 'XVID']:
        raise ValueError("Unexpected target encoding", FOURCC)

    # Load 1 picture to get its shape
    img = mpimg.imread(srcPaths[0])

    # Convert between standards of different libraries
    shape2Dcv = (img.shape[1], img.shape[0])   # OpenCV uses column-major or sth
    colorReorder = np.array([2, 1, 0])         # OpenCV and Matplotlib seem to disagree about color order in RGB

    # Initialize writer
    fourcc = cv2.VideoWriter_fourcc(*FOURCC)
    out = cv2.VideoWriter(trgPathName, fourcc, fps, shape2Dcv, isColor=isColor)

    for iSrc, srcPath in enumerate(srcPaths):
        print('Processing image[%d]\r' % iSrc, end="")
        img = np.uint8(255*mpimg.imread(srcPath))
        img = img[:, :, colorReorder] if isColor else img[:,:,0]
        out.write(img)

    print("\n Done")

    out.release()