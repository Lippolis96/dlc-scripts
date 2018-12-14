import os
import sys
from subprocess import call
from time import gmtime, strftime

import deeplabcut
from src.yaml_helper import yaml_read_dict, yaml_write_dict



def dlcSampleImages(metadata):
    # Create a new DeepLabCut project
    # writeLog("DeepLabCut is creating a project", logparam["action"])
    deeplabcut.create_new_project(
        metadata["param"]["Task"],
        metadata["param"]["scorer"],
        metadata["path"]["videolist"],
        working_directory = metadata["path"]["local_project"],
        copy_videos=False)

    # Find the new config path
    #self.writeLog("Updating DeepLabCut config file with user settings", self.logparam["action"])
    relTaskFolderName = metadata["param"]["Task"] + "-"
    relTaskFolderName += metadata["param"]["scorer"] + "-"
    relTaskFolderName += strftime("%Y-%m-%d", gmtime())
    relConfigPath = os.path.join(relTaskFolderName, "config.yaml")
    metadata["path"]["configfile"] = os.path.join(metadata["path"]["local_project"], relConfigPath)

    # Read the new config file, update it with user params, and save it again
    # writeLog("Searching for config.yaml in " + metadata["path"]["configfile"], logparam["action"])
    currentParam = yaml_read_dict(metadata["path"]["configfile"])
    currentParam.update(metadata["param"])
    yaml_write_dict(metadata["path"]["configfile"], currentParam)

    #writeLog("Updating DeepLabCut config file with user settings", logparam["action"])
    # Extract frames using DLC algorithm
    deeplabcut.extract_frames(
        metadata["path"]["configfile"],
        metadata["param"]["sampling"],
        metadata["param"]["clustering"],
        crop = metadata["param"]["cropping"])


def dlcCreateCheckLabels(configpath):
    # Run GUI
    # %gui wx
    # FIXME: QT application SEGFAULTS on exit of wxPython app, I have no clue why.
    #   So far I run it as a separate process, but would be good to fix
    #   It appears that it is in general hard to make a GUI run not from the main thread
    call([sys.executable, os.path.join("src/", "dlc_wx_hotfix.py"), configpath])
    #deeplabcut.label_frames(configpath)

    # this creates a subdirectory with the frames + your labels
    deeplabcut.check_labels(configpath)


def dlcCreateTrainingSet(configpath):
    deeplabcut.create_training_dataset(configpath)