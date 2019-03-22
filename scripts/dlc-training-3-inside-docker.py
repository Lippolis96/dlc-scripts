from time import time

# Check CUDA version
# !nvcc --version

# Check TensorFlow version
import tensorflow as tf
print(tf.__version__)

#let's make sure we see a GPU:
#tf.test.gpu_device_name()
#or
from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())

#GUIs don't work on in Docker (or the cloud), so label your data locally on your computer! 
#This notebook is for you to train and run video analysis!
import os
os.environ["DLClight"]="True"

# now we are ready to train!
import deeplabcut
deeplabcut.__version__

# Get path to config file from command line
import sys
path_config_file = sys.argv[1]

# Create training dataset
deeplabcut.create_training_dataset(path_config_file,Shuffles=[1])

# Train the network
time_start = time()
deeplabcut.train_network(path_config_file, shuffle=1, saveiters=1000, displayiters=10)
print("Total Time Taken: ", time() - time_start)

