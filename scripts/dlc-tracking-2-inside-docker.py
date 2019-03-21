import os

# Disable GUI
os.environ["DLClight"]="True"

import json
import deeplabcut

# Load videos and config file
with open('settings.json') as json_file:  
    settings = json.load(json_file)
    
deeplabcut.analyze_videos(settings['pwd_config'], settings['pwd_videos'])
