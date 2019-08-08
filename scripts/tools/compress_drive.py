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

# System modules
import os, sys, subprocess

# Append base directory
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
libdir = os.path.join(parentdir, "lib")
sys.path.insert(0, libdir)
print("Appended base directory", libdir)

# local libraries
from qt_wrapper import gui_fname, gui_fsave, gui_fpath
from os_lib import progress_bar, getfiles_walk, copy_folder_structure, move_filepaths
from video_convert_lib import convert_cv2, convert_ffmpeg_h265

# Check if only allowed folders are specified
allowed_formats = ['.avi', '.mp4']
if (len(sys.argv) != 2) or (sys.argv[1] not in allowed_formats):
    raise ValueError("Must specify output format from", allowed_formats)
source_format = '.avi'
target_format = sys.argv[1]

# GUI: Select source and target files
src_path = gui_fpath("Select source directory", "./")
tmp_pwd = os.path.dirname(src_path)
trg_parentpath = gui_fpath("Select target directory", tmp_pwd)
src_basename = os.path.basename(src_path)
trg_path = os.path.join(trg_parentpath, src_basename + "_compressed")

print("Copying structure from")
print("  ", src_path)
print("to")
print("  ", trg_path)
print("---------------------------------------")

print("Generating folder structure ...")
copy_folder_structure(src_path, trg_path)

print("Finding all source files of interest ...")
src_fileswalk = getfiles_walk(src_path, [source_format])

print("Checking if files exist ...")
src_fpaths_unproc, trg_fpaths_unproc = move_filepaths(src_fileswalk, src_path, trg_path, skip_exist=True)

# Change extension to target
trg_fpaths_unproc = [fpath[:-4] + target_format for fpath in trg_fpaths_unproc]

print("Starting conversion ...")
nFilesTotal = len(src_fileswalk)
nFilesNew = len(trg_fpaths_unproc)
iFiles = nFilesTotal - nFilesNew

for src_fpath, trg_fpath in zip(src_fpaths_unproc, trg_fpaths_unproc):
    progress_bar(iFiles, nFilesTotal)
    iFiles += 1
    if target_format == '.avi':
        convert_cv2(src_fpath, trg_fpath, FOURCC='MJPG')
    else:
        convert_ffmpeg_h265(src_fpath, trg_fpath, lossless=False, gray=True)
        #subprocess.run(["ffmpeg","-i", src_fpath, "-vf", "format=gray", "-c:v", "libx265", "-preset", "slow", "-x265-params", "crf=22", trg_fpath])
        
print("Done!")

