from time import time
import os, sys

#GUIs don't work on in Docker (or the cloud), so label your data locally on your computer!
#This notebook is for you to train and run video analysis!
os.environ["DLClight"]="True"

import tensorflow as tf
from tensorflow.python.client import device_lib
import deeplabcut

#print("CUDA version:", !nvcc --version)
print("Tensorflow: version:", tf.__version__)
print("Tensorflow: Checking GPU:", tf.test.gpu_device_name())
print("Tensorflow: Checking Local Devices:", device_lib.list_local_devices())
print("DeepLabCut version:", deeplabcut.__version__)


# Get path to config file from command line
path_config_file = sys.argv[1]

# Create training dataset
deeplabcut.create_training_dataset(path_config_file,Shuffles=[1])

# Train the network
time_start = time()
deeplabcut.train_network(path_config_file, shuffle=1, saveiters=1000, displayiters=10)
print("Total Time Taken: ", time() - time_start)