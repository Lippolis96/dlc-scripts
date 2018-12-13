# TODO: Allow import existing project and skip params part
# TODO: add @pyqtSlot() decorator to all methods implementing the log write
# TODO: Pass all logging output through myReceiver to avoid threading problems
# TODO: Disable GUI every time a long process is started
# TODO: Ensure all threads exit normally
# TODO: Ensure stderr is also ported to logbox correctly


#######################################################
# Imports
#######################################################

import locale   # language settings for date/time
import os       # allows file operations and direct command line execution
import sys      # command line arguments
import glob     # list files in directory
import inspect
from queue import Queue

# QT
from PyQt5 import QtGui, QtCore, QtWidgets

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.image as mpimg
# from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

# Append base directory
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)
print("Appended base directory", dir_path)

# Local libraries
from dlc_serv_gui.dlcgui import Ui_dlcgui
from ssh_helper import sshConnectExec1
from opencv_helper import getVideoShape
from yaml_helper import yaml_read_dict, yaml_write_dict
from qt_helper import updateComboBoxByValue
from qthread_helper import WriteStream, createRunThread, MyReceiver, ObjectFunction
from dlc_helper import dlcSampleImages, dlcCreateCheckLabels, dlcCreateTrainingSet

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
        self.gui.pathsLocalButton.clicked.connect(lambda: self.loadSetDir(
            self.gui.pathsLocalLineEdit, "Open Local Projects Folder", "~/"))
        self.gui.pathsVideoButton.clicked.connect(lambda: self.loadSetDir(
            self.gui.pathsVideoLineEdit, "Open Videos Folder", "~/"))
        self.gui.pathsImportButton.clicked.connect(lambda: self.loadSetFile(
            self.gui.pathsImportLineEdit, "Import existing project", "~/", "yaml files (*.yaml)"))
        self.gui.pathsImportPathsButton.clicked.connect(lambda: self.pathsImportPaths())

        # Mark->Params
        self.gui.paramSampleImagesButton.clicked.connect(lambda: self.paramsSampleImages())
        self.gui.paramGuiMarkButton.clicked.connect(lambda: self.paramsGUIMark())
        self.gui.paramCreateTrainingSetButton.clicked.connect(lambda: self.paramsCreateTrainingSet())

        # Mark->Check
        self.gui.checkFrameLoadButton.clicked.connect(lambda: self.checkFindFrames())
        self.gui.checkFrameSlider.valueChanged.connect(lambda: self.checkLoadFrame())

        # Train->Connect
        self.gui.connectConnectButton.clicked.connect(lambda: self.connectServ())


        # Create canvas for checking
        self.checkCanvasFig = plt.figure()
        self.checkStaticCanvas = FigureCanvasQTAgg(self.checkCanvasFig)  # figsize=(5, 3)
        self.gui.checkCanvasLayout.addWidget(self.checkStaticCanvas)
        self.checkStaticCanvas.draw()
        toolbar = NavigationToolbar2QT(self.checkStaticCanvas, self.gui.checkCanvasWidget, coordinates=True)
        self.gui.checkCanvasLayout.addWidget(toolbar)
        #self.checkStaticAxis = self.checkStaticCanvas.figure.subplots()

        # self.checkDynamicCanvas = FigureCanvas(Figure()) # figsize=(5, 3)
        # self.gui.checkCanvasLayout.addWidget(self.checkDynamicCanvas)
        # self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar2QT(self.checkDynamicCanvas, self))
        # self.checkDynamicAxis = self.checkDynamicCanvas.figure.subplots()


    # Destructor
    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__

    # Change global font size of the application
    def zoomFont(self, mag):
        self.fontSize += mag
        self.app.setFont(QtGui.QFont("Comic Sans", self.fontSize))
        
    # Write colored output to the log QTextEdit widget
    def writeLog(self, text, param):
        if param["type"] == "plain":
            self.gui.logTextEdit.insertPlainText(text+"\n")
        elif param["type"] == "html":
            html_text = "<font color=\""+param["color"]+"\">" + text + "</font><br>"
            self.gui.logTextEdit.insertHtml(html_text)
        else:
            raise ValueError("Unknown output type" + param["type"])


    # Open a directory and set its path to a local lineedit
    def loadSetFile(self, lineedit, caption, dir, filter):
        lineedit.setText(QtWidgets.QFileDialog.getOpenFileName(caption=caption, directory=dir, filter=filter)[0])

    # Open a directory and set its path to a local lineedit
    def loadSetDir(self, lineedit, caption, dir):
        lineedit.setText(QtWidgets.QFileDialog.getExistingDirectory(caption=caption, directory=dir))

    #
    def pathsImportPaths(self):
        self.metadata["path"]["local_project"] = self.gui.pathsLocalLineEdit.text()
        self.metadata["path"]["video_folder"] = self.gui.pathsVideoLineEdit.text()
        self.metadata["path"]["import_yaml"] = self.gui.pathsImportLineEdit.text()
        
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

        # Set initial cropping parameters to the current video shape
        self.gui.paramCropMarginsXMin.setText("0")
        self.gui.paramCropMarginsXMax.setText(str(self.metadata["param"]["video_shape"][0]))
        self.gui.paramCropMarginsYMin.setText("0")
        self.gui.paramCropMarginsYMax.setText(str(self.metadata["param"]["video_shape"][1]))

        # If import folder provided
        if self.metadata["path"]["import_yaml"] != "":
            # Find and import config.yaml from the example directory
            importParam = yaml_read_dict(self.metadata["path"]["import_yaml"])

            # Auto-Fill in params tab
            self.gui.paramProjectNameLineEdit.setText(importParam["Task"])
            self.gui.paramNameLineEdit.setText(importParam["scorer"])
            self.gui.paramNumFrameLineEdit.setText(str(importParam["numframes2pick"]))
            #self.gui.paramSelectionComboBox.currentText()
            self.gui.paramCroppingCheckBox.setCheckState(2 * int(importParam["cropping"]))
            self.gui.paramMarkingsLineEdit.setText(",".join(importParam["bodyparts"]))
            self.gui.paramTimeCropStartLineEdit.setText(str(importParam["start"]))
            self.gui.paramTimeCropStopLineEdit.setText(str(importParam["stop"]))

            # Auto-fill manual parameters, that are not in DLC config by default
            if "sampling" in importParam.keys():
                updateComboBoxByValue(self.gui.paramSamplingComboBox, importParam["sampling"])
            if "clustering" in importParam.keys():
                updateComboBoxByValue(self.gui.paramClusteringComboBox, importParam["clustering"])

            self.writeLog("Parameters from import file were loaded", self.logparam["action"])
        else:
            self.writeLog("Import file was not provided, so it was not loaded", self.logparam["action"])

        
    # Read and check all fields on the params tab
    # Create deeplabcut project
    # Fill parameters into new config.yaml
    # Run image sampling
    def paramsSampleImages(self):

        # Read all fields on the params tab
        self.metadata["param"] = {
            "Task"              : self.gui.paramProjectNameLineEdit.text(),
            "scorer"            : self.gui.paramNameLineEdit.text(),
            "numframes2pick"    : int(self.gui.paramNumFrameLineEdit.text()),
            "sampling"          : self.gui.paramSamplingComboBox.currentText(),
            "clustering"        : self.gui.paramClusteringComboBox.currentText(),
            "cropping"          : bool(self.gui.paramCroppingCheckBox.checkState()),
            "bodyparts"         : self.gui.paramMarkingsLineEdit.text().replace(" ", "").split(","),
            "start"             : int(self.gui.paramTimeCropStartLineEdit.text()),
            "stop"              : int(self.gui.paramTimeCropStopLineEdit.text())
            # "crop_margins"      : [
            #     int(self.gui.paramCropMarginsXMin.text()),
            #     int(self.gui.paramCropMarginsXMax.text()),
            #     int(self.gui.paramCropMarginsYMin.text()),
            #     int(self.gui.paramCropMarginsYMax.text())
            # ]
        }

        # Create a new DeepLabCut project
        self.writeLog("DeepLabCut is creating a project", self.logparam["action"])
        self.dlc_sample_obj = ObjectFunction(lambda : dlcSampleImages(self.metadata))
        self.dlc_create_thread = createRunThread(self.dlc_sample_obj)
    
    
    # Start wxPython GUI to mark frames
    def paramsGUIMark(self):
        self.writeLog("Mark frames using wxPython interface", self.logparam["action"])
        self.dlc_mark_check_obj = ObjectFunction(lambda : dlcCreateCheckLabels(self.metadata["path"]["configfile"]))
        self.dlc_mark_check_thread = createRunThread(self.dlc_mark_check_obj)



    # Create training set using DLC
    # Locate and import marked images into check tab
    def paramsCreateTrainingSet(self):
        self.writeLog("DeepLabCut is creating a training set", self.logparam["action"])
        self.dlc_create_training_obj = ObjectFunction(lambda : dlcCreateTrainingSet(self.metadata["path"]["configfile"]))
        self.dlc_create_training_thread = createRunThread(self.dlc_create_training_obj)


    def checkFindFrames(self):
        # Find frames directory
        imagesDir = QtWidgets.QFileDialog.getExistingDirectory(caption="Find images", directory="~/")

        # Load list of images
        self.metadata["path"]["checkimages"] = glob.glob(os.path.join(imagesDir, '*.png'))

        if len(self.metadata["path"]["checkimages"]):
            # Set slider properties based on image quantity
            self.gui.checkFrameSlider.setMinimum(0)
            self.gui.checkFrameSlider.setMaximum(len(self.metadata["path"]["checkimages"]) - 1)
            self.gui.checkFrameSlider.setValue(0)

            # Load first image
            self.gui.checkFrameSlider.setEnabled(True)
            self.checkLoadFrame(init=True)
        else:
            self.writeLog("No images found", self.logparam["error"])

    def checkLoadFrame(self, init=False):
        imageIdx = self.gui.checkFrameSlider.value()
        img = mpimg.imread(self.metadata["path"]["checkimages"][imageIdx])
        if init:
            plt.figure(self.checkCanvasFig.number)
            self.checkCurrentImage = plt.imshow(img)
            plt.axis('off')
        else:
            self.checkCurrentImage.set_data(img)
        self.checkStaticCanvas.draw()


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

    # Create Queue and redirect sys.stdout to this queue
    logOutQueue = Queue()
    sys.stdout = WriteStream(logOutQueue)

    # Create thread that will listen on the other end of the queue, and send the text to the textedit in our application
    receiverObj = MyReceiver(logOutQueue, lambda text: pth1.writeLog(text, pth1.logparam["output"]))
    receiverThread = createRunThread(receiverObj)

    mainwindow.show()
    sys.exit(app.exec_())
