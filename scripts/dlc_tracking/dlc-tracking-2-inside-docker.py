import os

# Disable GUI
os.environ["DLClight"]="True"

import json
import deeplabcut

# Load videos and config file
with open('settings.json') as json_file:  
    settings = json.load(json_file)
    
print("Gonna track videos:", settings['pwd_videos'])

#dest_folder = "/home/hpc_user/projects-dlc/dlc-scripts/results/"

deeplabcut.analyze_videos(settings['pwd_config'], settings['pwd_videos'], save_as_csv=True)

#deeplabcut.create_labeled_video(settings['pwd_config'], settings['pwd_videos'])
