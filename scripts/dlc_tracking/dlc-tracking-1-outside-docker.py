'''
This is a preprocess script called outside DeepLabCut Docker.
It is used to find paths to all videos that we wish to track, and save the path list in a settings file

Arguments:
    --selecttype=files    : User manually navigates to a folder to select multiple video files.
                            Then user is asked to repeat this process for another directory.
                            User may click cancel when all desired files have been selected
    --selecttype=crawler  : User provides a root directory. The algorithm automatically finds paths to
                            all video files with desired extension

    --extension=.avi      : Look for AVI videos
    --extension=.mp4      : Look for MP4 videos
'''


import sys
import argparse
import json
from os.path import abspath, dirname, join

projectPath = dirname(dirname(abspath(__file__)))
sys.path.append(projectPath)

from lib.qt_wrapper import gui_fname, gui_fnames, gui_fpath
from lib.os_lib import getfiles_walk

# Parse which method of video selection will be used
typekeys = ["files", "crawler"]
formatkeys = [".avi", ".mp4"]
parser = argparse.ArgumentParser(description='Select videos for tracking')
parser.add_argument('--selecttype', type=str, choices=typekeys, default="files", help='Determines method of selecting files')
parser.add_argument('--extension', type=str, choices=formatkeys, default=".avi", help='Determines video file extension')
args = parser.parse_args()

selectionType = args.selecttype
videoExtension = args.extension

# GUI: Select config file of the current DLC project
data = {}
data["pwd_config"] = gui_fname("Select config file...", "./", "Config Files (*.yaml)")
print("Using config file", data["pwd_config"])

# GUI: Select videos for training
tmp_dir = './'
data['pwd_videos'] = []

# If files method is selected, user will select multiple video files in a directory, manually clicking at each
if selectionType == 'files':
    while 1:
        current_videos = gui_fnames("Select video files to track, or cancel to finish", tmp_dir, "Video Files (*.avi)")
        if current_videos == ['']:
            break
        else:
            data['pwd_videos'] += current_videos
            tmp_dir = dirname(data['pwd_videos'][0])

# If crawler method is selected, user will provide a root folder, and all videos in all subfolders of that folder will automatically be selected
elif selectionType == 'crawler':
    while 1:
        root_path = gui_fpath("Select root directory to look for video files, or cancel to finish", tmp_dir)
        
        if root_path == "":
            break
        else:
            tmp_dir = root_path
            walkpaths = getfiles_walk(tmp_dir, [videoExtension])
            data['pwd_videos'] += [join(path, name) for path, name in walkpaths]

else:
    raise ValueError("Unexpected argument", selectionType)

# Save obtained video files in JSON
with open('settings.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)
    
print("Done! Check that settings.json looks ok inside")
