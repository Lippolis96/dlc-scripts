import locale   # language settings for date/time
import os       # allows file operations and direct command line execution
import sys      # command line arguments

from PyQt5 import QtGui, QtCore, QtWidgets

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

from dlc_serv_gui.dlc_serv_gui.dlcgui import Ui_dlcgui






#######################################################
# Main Window
#######################################################
class DLC_SERV_GUI () :
    def __init__(self, dialog):
        self.dialog = dialog
        self.gui = Ui_dlcgui()
        self.gui.setupUi(dialog)

        # React to active elements
        self.gui.pathsLocalButton.clicked.connect(lambda: self.loadPathLocal())
        self.gui.pathsNetworkVideoButton.clicked.connect(lambda: self.loadPathNetwork())
        self.gui.pathsImportButton.clicked.connect(lambda: self.loadPathImport())


    def loadPathLocal(self):
        pass

    def loadPathNetwork(self):
        pass

    def loadPathImport(self):
        pass


#######################################################
## Start the QT window
#######################################################
if __name__ == '__main__' :
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(QtGui.QFont("Comic Sans", 20))
    mainwindow = QtWidgets.QMainWindow()
    locale.setlocale(locale.LC_TIME, "en_GB.utf8")
    pth1 = DLC_SERV_GUI(mainwindow)
    mainwindow.show()
    sys.exit(app.exec_())