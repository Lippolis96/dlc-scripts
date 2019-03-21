import os
import json
import deeplabcut

# Disable GUI
os.environ["DLClight"]="True"

# Load videos and config file
with open('settings.json') as json_file:  
    settings = json.load(json_file)
    
deeplabcut.analyze_videos(settings['pwd_config'], settings['pwd_videos'])