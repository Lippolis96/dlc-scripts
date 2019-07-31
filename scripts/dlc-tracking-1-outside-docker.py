import os
import argparse
import json
from lib.qt_wrapper import gui_fname, gui_fnames, gui_fpath
from lib.os_lib import getfiles_walk

# Parse which method of video selection will be used
typekeys = ["files", "crawler"]
parser = argparse.ArgumentParser(description='Select videos for tracking')
parser.add_argument('--selecttype', type=str, choices=typekeys, default="files", help='Determines method of selecting files')
args = parser.parse_args()

# GUI: Select config file of the current DLC project
data = {}
data["pwd_config"] = gui_fname("Select config file...", "./", "Config Files (*.yaml)")
print("Using config file", data["pwd_config"])

# GUI: Select videos for training
tmp_dir = './'
data['pwd_videos'] = []

# If files method is selected, user will select multiple video files in a directory, manually clicking at each
if args.selecttype == 'files':
    while 1:
        current_videos = gui_fnames("Select video files to track, or cancel to finish", tmp_dir, "Video Files (*.avi)")
        if current_videos == ['']:
            break
        else:
            data['pwd_videos'] += current_videos
            tmp_dir = os.path.dirname(data['pwd_videos'][0])

# If crawler method is selected, user will provide a root folder, and all videos in all subfolders of that folder will automatically be selected
elif args.selecttype == 'crawler':
    while 1:
        root_path = gui_fpath("Select root directory to look for video files, or cancel to finish", tmp_dir)
        
        if root_path == "":
            break
        else:
            tmp_dir = root_path
            walkpaths = getfiles_walk(tmp_dir, [".avi"])
            data['pwd_videos'] += [os.path.join(path, name) for path, name in walkpaths]

else:
    raise ValueError("Unexpected argument", args.selecttype)

# Save obtained video files in JSON
with open('settings.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)
    
print("Done! Check that settings.json looks ok inside")
