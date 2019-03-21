import json
import deeplabcut

with open('settings.json') as json_file:  
    settings = json.load(json_file)
    
deeplabcut.analyze_videos(settings['pwd_config'], settings['pwd_videos'])