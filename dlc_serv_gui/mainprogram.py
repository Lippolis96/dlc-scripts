#######################################################
# Imports
#######################################################

import locale   # language settings for date/time
import os       # allows file operations and direct command line execution
import sys      # command line arguments
import glob     # list files in directory
import inspect

# QT
from PyQt5 import QtGui, QtCore, QtWidgets

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# Deeplabcut
# import deeplabcut


# Append base directory
#currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#base_dir = currentdir[:currentdir.index('python')] + 'python/'
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)
print("Appended base directory", dir_path)

from dlc_serv_gui.dlcgui import Ui_dlcgui
from ssh_helper import sshConnectExec1
from opencv_helper import getVideoShape
from yaml_helper import yaml_read_dict, yaml_write_dict


#######################################################
# Main Window
#######################################################
class DLC_SERV_GUI () :
    def __init__(self, dialog, app):
        self.app = app
        self.dialog = dialog
        self.gui = Ui_dlcgui()
        self.gui.setupUi(dialog)
        self.fontSize = 20

        # Logging font parameters
        self.logparam = {
            "output" : {"type" : "plain"},
            "action" : {"type" : "html", "color" : "Blue"},
            "error"  : {"type" : "html", "color" : "Red"}
        }

        # Global project variables
        self.metadata = {  # Dictionary with all project metadata
            "path"  : {},  # All paths
            "param" : {},  # All project parameters
        }

        # Interface
        shortcutZoomPlus = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Plus), self.dialog, lambda: self.zoomFont(+1))
        shortcutZoomMinus = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Minus), self.dialog, lambda: self.zoomFont(-1))

        # Mark->Paths
        self.gui.pathsLocalButton.clicked.connect(
            lambda: self.loadSetDir(self.gui.pathsLocalLineEdit, "Open Local Project Folder", "~/"))
        self.gui.pathsNetworkVideoButton.clicked.connect(
            lambda: self.loadSetDir(self.gui.pathsNetworkVideoLineEdit, "Open Network Folder with Videos", "~/"))
        self.gui.pathsImportButton.clicked.connect(
            lambda: self.loadSetDir(self.gui.pathsImportLineEdit, "Open Existing project folder to import settings", "~/"))
        self.gui.pathsImportPathsButton.clicked.connect(lambda: self.pathsImportPaths())

        # Mark->Params
        self.gui.paramSampleImagesButton.clicked.connect(lambda: self.paramsSampleImages())
        self.gui.paramGuiMarkButton.clicked.connect(lambda: self.paramsGUIMark())
        self.gui.paramCreateTrainingSetButton.clicked.connect(lambda: self.paramsCreateTrainingSet())
        
        # Train->Connect
        self.gui.connectConnectButton.clicked.connect(lambda: self.connectServ())

    # Change global font size of the application
    def zoomFont(self, mag):
        self.fontSize += mag
        app.setFont(QtGui.QFont("Comic Sans", self.fontSize))
        
    # Write colored output to the log QTextEdit widget
    def writeLog(self, text, param):
        if param["type"] == "plain":
            self.gui.logTextEdit.insertPlainText(text)
        elif param["type"] == "html":
            html_text = "<font color=\""+param["color"]+"\">" + text + "</font><br>"
            self.gui.logTextEdit.insertHtml(html_text)
        else:
            raise ValueError("Unknown output type" + param["type"])


    # Open a directory and set its path to a local lineedit
    def loadSetDir(self, lineedit, caption, dir):
        lineedit.setText(QtWidgets.QFileDialog.getExistingDirectory(caption=caption, directory=dir))
    
    def pathsImportPaths(self):
        self.metadata["path"]["local_project"] = self.gui.pathsLocalLineEdit.text()
        self.metadata["path"]["video_folder"] = self.gui.pathsNetworkVideoLineEdit.text()
        self.metadata["path"]["import_project"] = self.gui.pathsImportLineEdit.text()
        
        # List videos in the video folder
        self.metadata["path"]["videolist"] = glob.glob(os.path.join(self.metadata["path"]["video_folder"], '*.avi'))
        if len(self.metadata["path"]["videolist"]) == 0:
            self.writeLog("No suitable .avi files have been found in " + self.metadata["path"]["video_folder"] , self.logparam["error"])
            return 0  # Exit the function

        # Find video size, check that it is the same for all videos
        self.writeLog("Importing videos...", self.logparam["action"])
        vidshapes = {getVideoShape(vidpath) for vidpath in self.metadata["path"]["videolist"]}
        if None in vidshapes:
            self.writeLog("Some video files failed to load: " + str(vidshapes), self.logparam["error"])
            return 0  # Exit the function
        elif len(vidshapes) == 1:
            self.metadata["param"]["video_shape"] = list(vidshapes)[0]
            self.writeLog("Loaded " + str(len(self.metadata["path"]["videolist"])) + " videos with shape " + str(list(vidshapes)[0]), self.logparam["output"])
        else:
            self.writeLog("Provided videos have different shapes" + str(vidshapes), self.logparam["error"])
            return 0  # Exit the function


        # Find and import config.yaml from the example directory
        if self.metadata["path"]["import_project"] != "":
            self.metadata["path"]["import_config_yaml"] = "???"
            importParam = yaml_read_dict(self.metadata["path"]["import_config_yaml"])

            "Task"              : self.gui.paramProjectNameLineEdit.text(),
            "scorer"            : self.gui.paramNameLineEdit.text(),
            "date"              : self.gui.paramDateLineEdit.text(),
            "numframes2pick"    : int(self.gui.paramNumFrameLineEdit.text()),
            "clustering"        : self.gui.paramSelectionComboBox.currentText(),
            "cropping"          : bool(self.gui.paramCroppingCheckBox.checkState()),
            "bodyparts"         : self.gui.paramMarkingsLineEdit.text().replace(" ", "").split(","),



        # Auto-Fill in params tab
        
    # Read and check all fields on the params tab
    # Create deeplabcut project
    # Fill parameters into new config.yaml
    # Run image sampling
    def paramsSampleImages(self):
        # Enter the path of the config file that was just created from the above step (check the folder)
        #path_config_file = '/home/alfomi/work/DLC_DOCKER/example-pia/Tracking-Pia-2018-12-06/config.yaml'

        self.metadata["param"] = {
            "Task"              : self.gui.paramProjectNameLineEdit.text(),
            "scorer"            : self.gui.paramNameLineEdit.text(),
            "date"              : self.gui.paramDateLineEdit.text(),
            "numframes2pick"    : int(self.gui.paramNumFrameLineEdit.text()),
            "clustering"        : self.gui.paramSelectionComboBox.currentText(),
            "cropping"          : bool(self.gui.paramCroppingCheckBox.checkState()),
            "bodyparts"         : self.gui.paramMarkingsLineEdit.text().replace(" ", "").split(","),
            "crop_margins"      : [
                int(self.gui.paramCropMarginsXMin.text()),
                int(self.gui.paramCropMarginsXMax.text()),
                int(self.gui.paramCropMarginsYMin.text()),
                int(self.gui.paramCropMarginsYMax.text())
            ]
        }
        
        # deeplabcut.create_new_project(
        #     self.metadata["param"]["Task"],
        #     self.metadata["param"]["scorer"],
        #     self.metadata["path"]["videolist"],
        #     working_directory=self.metadata["path"]["local"],
        #     copy_videos=False)
        
        # deeplabcut.extract_frames(
        #     self.metadata["path"]["configfile"],
        #     'automatic',
        #     self.metadata["param"]["clustering"],
        #     crop=self.metadata["param"]["cropping"])
    
    
    # Start wxPython GUI to mark frames
    def paramsGUIMark(self):
        
        # Run GUI
        # %gui wx
        deeplabcut.label_frames(self.metadata["path"]["configfile"])
        
        # this creates a subdirectory with the frames + your labels
        deeplabcut.check_labels(self.metadata["path"]["configfile"])
        
    # Create training set using DLC
    # Locate and import marked images into check tab
    def paramsCreateTrainingSet(self):
        deeplabcut.create_training_dataset(self.metadata["path"]["configfile"])
        
    # Connect to server using parameters from GUI, attempt to run nvidia-smi there
    def connectServ(self):
        self.connectParam = {
            "username": self.gui.connectUsernameLineEdit.text(),
            "hostname": self.gui.connectHostnameLineEdit.text(),
            "password": self.gui.connectPasswordLineEdit.text()
        }
        
        sshConnectExec1(self.connectParam, self, "nvidia-smi")


#######################################################
## Start the QT window
#######################################################
if __name__ == '__main__' :
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(QtGui.QFont("Comic Sans", 20))
    mainwindow = QtWidgets.QMainWindow()
    locale.setlocale(locale.LC_TIME, "en_GB.utf8")
    pth1 = DLC_SERV_GUI(mainwindow, app)
    mainwindow.show()
    sys.exit(app.exec_())
