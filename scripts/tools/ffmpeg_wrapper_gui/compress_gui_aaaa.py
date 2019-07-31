

###############################
# Import system libraries
###############################
import os, sys, locale
from PyQt5 import QtGui, QtCore, QtWidgets

#######################################
# Compile QT File
#######################################
thisdir = os.path.dirname(os.path.abspath(__file__))
ui_ui_path = os.path.join(os.path.join(thisdir, "ffmpeg_wrapper"), 'ffmpeg_wrapper.ui')
ui_py_path = os.path.join(os.path.join(thisdir, "ffmpeg_wrapper"), 'ffmpeg_wrapper.py')
qtCompilePrefStr = 'pyuic5 ' + ui_ui_path + ' -o ' + ui_py_path
print("Compiling QT GUI file", qtCompilePrefStr)
os.system(qtCompilePrefStr)

#######################################
# Import local libraries
#######################################

from ffmpeg_wrapper.ffmpeg_wrapper import Ui_FFMPEG_WRAPPER


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

        # Listeners
        self.gui.mainQualityCRFSlider.valueChanged.connect(self.react_crf_slider)
        self.gui.mainSourceButton.clicked.connect(self.react_source_button)
        self.gui.mainTargetButton.clicked.connect(self.react_target_button)
        self.gui.mainConvertButton.clicked.connect(self.react_convert_button)

        self.dialog.wheelEvent = self.wheelEvent


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
    def wheelEvent(self, event):
        print("New font size", self.fontsize)
        self.fontsize += event.angleDelta().y() // 120
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
