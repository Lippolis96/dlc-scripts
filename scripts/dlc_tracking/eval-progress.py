'''
  This script helps identify current progress of DLC tracking
  Please provide a unique part of a video pathname as the first argument

  If the file is unique, its order in the sequence will be reported. The resulting fraction is current progress
  If file is not unique, you will be informed how many files satisfying this criterion have been found in the queue
'''


import sys
import json

# Load videos and config file
with open('settings.json') as json_file:
    pwd_videos = json.load(json_file)['pwd_videos']

target = sys.argv[1]
strOccurence = [iFile for iFile, fname in enumerate(pwd_videos) if target in fname]

if len(strOccurence) != 1:
    print("substring", target, "occurs in", len(strOccurence), "files")
else:
    print("substring", target, "is at position", strOccurence[0], "/", len(pwd_videos), "in the queue")