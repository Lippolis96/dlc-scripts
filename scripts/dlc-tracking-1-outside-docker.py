import json
from lib.qt_wrapper import gui_fname, gui_fnames, gui_fpath

# GUI: Select config file of the current DLC project
data = {}

data["pwd_config"] = gui_fname("Select config file...", "./", "Config Files (*.yaml)")

print("Using config file", data["pwd_config"])

# GUI: Select videos for training
data['pwd_videos'] = []
add_videos_done = False
while not add_videos_done:
    print("Adding more videos")
    data['pwd_videos'] += gui_fnames("Select video files to track...", "./", "Video Files (*.avi)")
    print("Currently using videos:", data['pwd_videos'])
    add_videos_done = input("Add more videos? (y/n) :") != "y"

with open('settings.json', 'w') as outfile:  
    json.dump(data, outfile)
    
print("Done!")