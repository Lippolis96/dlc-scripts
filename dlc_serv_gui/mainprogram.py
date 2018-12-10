#######################################################
# Imports
#######################################################

import locale   # language settings for date/time
import os       # allows file operations and direct command line execution
import sys      # command line arguments
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

        # Interface
        shortcutZoomPlus = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Plus), self.dialog, lambda: self.zoomFont(+1))
        shortcutZoomMinus = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Minus), self.dialog, lambda: self.zoomFont(-1))

        # Mark->Paths
        self.gui.pathsLocalButton.clicked.connect(lambda: self.loadPathLocal())
        self.gui.pathsNetworkVideoButton.clicked.connect(lambda: self.loadPathNetwork())
        self.gui.pathsImportButton.clicked.connect(lambda: self.loadPathImport())
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

    def loadPathLocal(self):
        self.pathLocal = QtWidgets.QFileDialog.getExistingDirectory(caption="Open Local Project Folder", directory="~/")
        self.gui.pathsLocalLineEdit.setText(self.pathLocal)

    def loadPathNetwork(self):
        self.pathNetwork = QtWidgets.QFileDialog.getExistingDirectory(caption="Open Network Folder with Videos", directory="~/")
        self.gui.pathsNetworkVideoLineEdit.setText(self.pathNetwork)

    def loadPathImport(self):
        self.pathImport = QtWidgets.QFileDialog.getExistingDirectory(caption="Open Existing project folder to import settings", directory="~/")
        self.gui.pathsImportLineEdit.setText(self.pathImport)
    
    def pathsImportPaths(self):
        self.newProjectName = self.gui.pathsProjectNameLineEdit.text()
        self.newProjectPath = self.gui.pathsLocalLineEdit.text()
        self.newVideoFolderPath = self.gui.pathsNetworkVideoLineEdit.text()
        self.importProjectPath = self.gui.pathsImportLineEdit.text()
        
        # List videos in the video folder
        # Find video size, check that it is the same for all videos
        
        # Find and import config.yaml from the example directory
        # Auto-Fill in params tab
        
    # Read and check all fields on the params tab
    # Create deeplabcut project
    # Fill parameters into new config.yaml
    # Run image sampling
    def paramsSampleImages(self):
        # Enter the path of the config file that was just created from the above step (check the folder)
        #path_config_file = '/home/alfomi/work/DLC_DOCKER/example-pia/Tracking-Pia-2018-12-06/config.yaml'
        
        param = {
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

        print(param)
        
        # deeplabcut.create_new_project(param["Task"], param["scorer"], self.newVideoList, working_directory=self.pathLocal, copy_videos=False)
        
        # deeplabcut.extract_frames(path_config_file, 'automatic', param["cluster"], crop=param["crop"])
    
    
    # Start wxPython GUI to mark frames
    def paramsGUIMark(self):
        
        # Run GUI
        # %gui wx
        deeplabcut.label_frames(path_config_file)
        
        # this creates a subdirectory with the frames + your labels
        deeplabcut.check_labels(path_config_file)
        
    # Create training set using DLC
    # Locate and import marked images into check tab
    def paramsCreateTrainingSet(self):
        deeplabcut.create_training_dataset(path_config_file)
        
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
