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
import argparse

# Append base directory
projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)

# local libraries
from lib.qt_wrapper import gui_fname, gui_fsave, gui_fpath
from lib.os_lib import progress_bar, getfiles_walk, copy_folder_structure, move_filepaths
from lib.video_convert_lib import convert_cv2, convert_ffmpeg_h265

# Parse arguments
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--format', type=str, choices=['.avi', '.mp4'], required=True, help='Type of the output video (avi/mp4)')
parser.add_argument('--minsize', type=int, default=None, help='Minimal allowed size of video')
parser.add_argument('--maxsize', type=int, default=None, help='Maximal allowed size of video')
parser.add_argument('--crop', type=int, nargs=4, required=False, help='Cropping')
#parser.add_argument('-l','--list', nargs='+'
args = parser.parse_args()

source_format = '.avi'
target_format = args.format
min_file_size = args.minsize
max_file_size = args.maxsize
crop_coords = args.crop

print(crop_coords)

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
src_fileswalk = getfiles_walk(src_path, [source_format], min_size=min_file_size, max_size=max_file_size)

# Determining new pathnames for files
src_fpaths, trg_fpaths = move_filepaths(src_fileswalk, src_path, trg_path)

# Change file extensions
trg_fpaths = [fpath[:-4] + target_format for fpath in trg_fpaths]

print(src_fpaths)
print(trg_fpaths)

print("Checking if files exist ...")
src_fpaths_unproc = []
trg_fpaths_unproc = []
for src_fpath, trg_fpath in zip(src_fpaths, trg_fpaths):
    if os.path.isfile(trg_fpath):
        print("-- skipping existing file", trg_fpath)
    else:
        src_fpaths_unproc += [src_fpath]
        trg_fpaths_unproc += [trg_fpath]

print("Starting conversion ...")
nFilesTotal = len(src_fileswalk)
nFilesNew = len(trg_fpaths_unproc)
iFiles = nFilesTotal - nFilesNew

print(src_fpaths_unproc)
print(trg_fpaths_unproc)

for src_fpath, trg_fpath in zip(src_fpaths_unproc, trg_fpaths_unproc):
    progress_bar(iFiles, nFilesTotal)
    iFiles += 1
    if target_format == '.avi':
        convert_cv2(src_fpath, trg_fpath, FOURCC='MJPG', crop=crop_coords)
    else:
        convert_ffmpeg_h265(src_fpath, trg_fpath, lossless=False, gray=True, crop=crop_coords)
        #subprocess.run(["ffmpeg","-i", src_fpath, "-vf", "format=gray", "-c:v", "libx265", "-preset", "slow", "-x265-params", "crf=22", trg_fpath])
        
print("Done!")

