######################################################
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





# GUI: Select source and target files
src_name = gui_fname("Select vid file...", "./", "Video Files (*.avi)")
tmp_pwd = os.path.dirname(src_name)
trg_name = gui_fsave("Save result file...", tmp_pwd, "H265 MPEG-4 (*.mp4)")

# FFMPEG - run compression
#ffmpeg -i omgbestvideva.avi -c:v libx265 -x265-params lossless=1 output2.mp4
subprocess.run(["ffmpeg","-i", src_name, "-vf", "format=gray", "-c:v", "libx265", "-preset", "slow", "-x265-params", "crf=22", trg_name])
