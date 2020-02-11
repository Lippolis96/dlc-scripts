###############################
# Import system libraries
###############################
import os, sys, locale
from PyQt5 import QtGui, QtCore, QtWidgets

###############################
# Export Root Directory
###############################
thisdir = os.path.dirname(os.path.abspath(__file__))
rootdir = os.path.dirname(thisdir)
sys.path.append(rootdir)

#######################################
# Compile QT File
#######################################
ui_ui_path = os.path.join(thisdir, "video_process_gui_files", 'ffmpeg_wrapper.ui')
ui_py_path = os.path.join(thisdir, "video_process_gui_files", 'ffmpeg_wrapper.py')
qtCompilePrefStr = 'pyuic5 ' + ui_ui_path + ' -o ' + ui_py_path
print("Compiling QT GUI file", qtCompilePrefStr)
os.system(qtCompilePrefStr)

#######################################
# Import local libraries
#######################################

import numpy as np
from video_processing.video_process_gui_files.ffmpeg_wrapper import Ui_FFMPEG_WRAPPER
from lib.os_lib import getfiles_walk, sizeToString
import lib.video_convert_lib as video_lib


#######################################################
# Main Window
#######################################################
class CompressGUI():
    def __init__(self, dialog):

        # Init
        self.dialog = dialog
        self.gui = Ui_FFMPEG_WRAPPER()
        self.gui.setupUi(dialog)

        # GUI-Constants
        self.fontsize = 15

        # User variables
        self.source_path = None
        self.target_path = None

        # Listeners - Info Crawl
        self.gui.infoCrawlGetRootButton.clicked.connect(self.react_info_crawl)
        self.gui.infoCrawlTableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Listeners - Video Compression
        self.gui.mainQualityCRFSlider.valueChanged.connect(self.react_crf_slider)
        self.gui.mainSourceButton.clicked.connect(self.react_source_button)
        self.gui.mainTargetButton.clicked.connect(self.react_target_button)
        self.gui.mainConvertButton.clicked.connect(self.react_convert_button)

        # Listeners - UI
        #self.dialog.wheelEvent = self.wheelEvent
        self.dialog.keyPressEvent = self.keyPressEvent


    # Get directory, then get all subfiles in that directory, then get their statistics
    def react_info_crawl(self):
        # Get root directory
        print("Reading files")
        rootCrawlDir = QtWidgets.QFileDialog.getExistingDirectory(None, "Get root directory to inspect", "./")

        # Get all files and their sizes
        fileswalk = getfiles_walk(rootCrawlDir)
        filesByExt = {}

        self.gui.infoCrawlProgressBar.setEnabled(True)
        self.gui.infoCrawlProgressBar.setMaximum(len(fileswalk))

        for iFile, (path, name) in enumerate(fileswalk):
            self.gui.infoCrawlProgressBar.setValue(iFile)

            thisExt = os.path.splitext(name)[1]
            isVideo = thisExt in ['.avi', '.mp4']
            fname = os.path.join(path, name)
            fsize = os.path.getsize(fname)

            if thisExt not in filesByExt.keys():
                filesByExt[thisExt] = []

            rezThis = [fsize]

            if isVideo:
                vidInfos = video_lib.get_info_cv2(fname)
                rezThis += [vidInfos['shape'], vidInfos['nFrame'], vidInfos['fps'], vidInfos['fourcc']]

            filesByExt[thisExt] += [rezThis]
        self.gui.infoCrawlProgressBar.setEnabled(False)

        print("Computing statistics")
        # Summarize statistics by extension
        statByExt = []
        for ext, data in filesByExt.items():
            totalFileSizes = sizeToString(np.sum(d[0] for d in data))
            stat = [ext, len(data), totalFileSizes]
            for iData in range(1, len(data[0])):
                stat += [list(set([d[iData] for d in data]))]
            statByExt += [stat]

        print("Filling up table")
        #write results to table
        self.gui.infoCrawlTableWidget.setRowCount(0)
        for iRow, extStat in enumerate(statByExt):
            self.gui.infoCrawlTableWidget.insertRow(iRow)
            for iCol, stat in enumerate(extStat):
                self.gui.infoCrawlTableWidget.setItem(iRow, iCol, QtWidgets.QTableWidgetItem(str(stat)))

        # self.gui.infoCrawlTableWidget.resizeColumnsToContents()


    # Store relevant state variables into dictionary
    def get_gui_state(self):
        return {
            "MainMode"  : self.gui.mainModeComboBox.itemText(),
            "Encoding"  : self.gui.mainEncodingComboBox.itemText(),
            "Grayscale" : self.gui.mainGrayscaleCheckBox.isChecked(),
            "Lossless"  : self.gui.mainLosslessCheckBox.isChecked(),
            "Q_CRF"     : int(self.gui.mainQualityCRFSlider.value()),
        }


    # Update displayed slider value
    def react_crf_slider(self):
        self.gui.mainQuality2Label.setText(str(self.gui.mainQualityCRFSlider.value()))

    def react_source_button(self):
        state = self.get_gui_state()
        if state["MainMode"] == "Single Video":
            aaa = QtWidgets.QFileDialog.getOpenFileName(self, "Load video file for compression", "./", filter="Video Files (*.avi, *.mp4)")
            print(aaa)
        elif state["MainMode"] == "Folder Crawler":
            aaa = QtWidgets.QFileDialog.getExistingDirectory(self, "Load folder containing video files", "./")
            print(aaa)
        else:
            raise ValueError("Unexpected operation mode", state["MainMode"])

    def react_target_button(self):
        state = self.get_gui_state()

        if state["Encoding"] == "AVI":
            filterThis = "AVI Files (*.avi)"
        elif state["Encoding"] == "MP4 (H265)":
            filterThis = "MP4 Files (*.mp4)"
        else:
            raise ValueError("Unexpected encoding", state["Encoding"])

        if state["MainMode"] == "Single Video":
            aaa = QtWidgets.QFileDialog.getSaveFileName(self, "Choose name for resulting video", "./", filter=filterThis)
            print(aaa)
        elif state["MainMode"] == "Folder Crawler":
            aaa = QtWidgets.QFileDialog.getExistingDirectory(self, "Select directory where results will be saved", "./")
            print(aaa)
        else:
            raise ValueError("Unexpected operation mode", state["MainMode"])

    def react_convert_button(self):
        pass


    # Change font size of all items on the form
    #def wheelEvent(self, event):
        # print("New font size", self.fontsize)
        # self.fontsize += event.angleDelta().y() // 120
        # self.gui.centralWidget.setStyleSheet("font-size: " + str(self.fontsize) + "pt;")
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Plus or e.key() == QtCore.Qt.Key_Minus:
            self.fontsize += int(e.key() == QtCore.Qt.Key_Plus) - int(e.key() == QtCore.Qt.Key_Minus)
            print("New font size", self.fontsize)
            self.gui.centralWidget.setStyleSheet("font-size: " + str(self.fontsize) + "pt;")




#######################################################
## Start the QT window
#######################################################
if __name__ == '__main__' :
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = QtWidgets.QMainWindow()
    locale.setlocale(locale.LC_TIME, "en_GB.utf8")
    pth1 = CompressGUI(mainwindow)
    mainwindow.show()
    sys.exit(app.exec_())
