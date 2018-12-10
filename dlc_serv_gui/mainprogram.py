import locale   # language settings for date/time
import os       # allows file operations and direct command line execution
import sys      # command line arguments
import paramiko

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

        # Train->Connect
        self.gui.connectConnectButton.clicked.connect(lambda: self.connectServ())

    def zoomFont(self, mag):
        self.fontSize += mag
        app.setFont(QtGui.QFont("Comic Sans", self.fontSize))


    def loadPathLocal(self):
        self.pathLocal = QtWidgets.QFileDialog.getExistingDirectory(caption="Open Local Project Folder", directory="~/")
        self.gui.pathsLocalLineEdit.setText(self.pathLocal)

    def loadPathNetwork(self):
        self.pathNetwork = QtWidgets.QFileDialog.getExistingDirectory(caption="Open Network Folder with Videos", directory="~/")
        self.gui.pathsNetworkVideoLineEdit.setText(self.pathNetwork)

    def loadPathImport(self):
        self.pathImport = QtWidgets.QFileDialog.getExistingDirectory(caption="Open Existing project folder to import settings", directory="~/")
        self.gui.pathsImportLineEdit.setText(self.pathImport)

    def text2html(self, text, color):
        return "<font color=\""+color+"\">" + text + "</font><br>"

    def connectServ(self):
        self.connectParam = {
            "username": self.gui.connectUsernameLineEdit.text(),
            "hostname": self.gui.connectHostnameLineEdit.text(),
            "password": self.gui.connectPasswordLineEdit.text()
        }

        self.gui.logTextEdit.insertHtml(self.text2html("Attempting to connect to host...", "Blue"))
        self.sshClient = paramiko.SSHClient()
        self.sshClient.load_system_host_keys()
        self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshClient.connect(**self.connectParam)

        self.gui.logTextEdit.insertHtml(self.text2html("Checking GPU status...", "Blue"))
        ssh_stdin, ssh_stdout, ssh_stderr = self.sshClient.exec_command("nvidia-smi")
        self.gui.logTextEdit.insertPlainText("".join(ssh_stdout.readlines()))

        self.gui.logTextEdit.insertHtml(self.text2html("Closing connection...", "Blue"))
        self.sshClient.close()

        # FOR CONTINUOUS OUTPUT, BELOW WILL RUN UNTIL EOF, AND WAIT IF EOF DOES NOT YET EXIST
        # for line in iter(lambda: stdout.readline(2048), ""): print(line, end="")


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