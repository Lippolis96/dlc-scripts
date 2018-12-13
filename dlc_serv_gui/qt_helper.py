import sys
from PyQt5 import QtGui, QtCore, QtWidgets

# Change current index of the combo box by value
def updateComboBoxByValue(combo, value):
    idx = combo.findData(value)
    if idx != -1:
        combo.setCurrentIndex(idx)
    else:
        raise ValueError("Unexpected combo box value: "  + str(value))
