import sys

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

from PyQt5 import QtGui, QtCore, QtWidgets

# Change current index of the combo box by value
def updateComboBoxByValue(combo, value):
    idx = combo.findData(value)
    if idx != -1:
        combo.setCurrentIndex(idx)
    else:
        raise ValueError("Unexpected combo box value: "  + str(value))

# Embed a matplotlib plot into a QT application
# Requires a horizontal qtLayout inside a qtWidget on the qt form
# FIXME: Operate with axis instead of figures - more thread-safe
# TODO: Automatically create a layout inside provided widget - will require less design effort
def embedQTPlot(qtLayout, qtWidget):
    fig = plt.figure()
    canvas = FigureCanvasQTAgg(fig)  # figsize=(5, 3)
    qtLayout.addWidget(canvas)
    # canvas.draw()
    toolbar = NavigationToolbar2QT(canvas, qtWidget) #, coordinates=True)
    canvas.addWidget(toolbar)
    return fig, canvas