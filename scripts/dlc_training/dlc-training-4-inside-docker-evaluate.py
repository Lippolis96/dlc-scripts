import os, sys

#GUIs don't work on in Docker (or the cloud), so label your data locally on your computer!
#This notebook is for you to train and run video analysis!
os.environ["DLClight"]="True"

import deeplabcut

# Get path to config file from command line
path_config_file = sys.argv[1]

# Create training dataset and evaluate performance
deeplabcut.evaluate_network(path_config_file)

