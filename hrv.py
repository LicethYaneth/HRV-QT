#HRV Application

import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import wfdb
import matplotlib.pyplot as plt, mpld3
import matplotlib
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=18, height=3, dpi=2):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(411)
        self.axes = fig.add_subplot(414)
        super(MplCanvas, self).__init__(fig)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = uic.loadUi('interfaz.ui',self)
        self.init_window()
        self.showMaximized()

    def init_window(self):
        self.ui = uic.loadUi('interfaz.ui',self)
        self.actionOpen.triggered.connect(self.abrir_archivo)
        #self.ruta= QLabel(self)

    def abrir_archivo(self):
        self.file = QFileDialog.getOpenFileName(self, "Selecciona un archivo", "/home/", "PDF Files (*.dat)")[0]
        #self.pushButton_10.clicked.connect(self.abrir_archivo)
        #self.ruta.setText(os.path.(self.file))
        record = wfdb.rdrecord(self.file[:-4]) 
        signals, fields = wfdb.rdsamp(self.file[:-4], channels=[0])
        record = wfdb.rdrecord(self.file[:-4], channels=[0])
        signal=signals.reshape(record.sig_len)
        
        sc = MplCanvas(self, width=35, height=3, dpi=50)
        sc.axes.plot(signal)
        
        self.ui.horizontalLayout.addWidget(sc)
        
        toolbar = NavigationToolbar(sc, self)

        #layout = QtWidgets.QVBoxLayout()
        self.ui.horizontalLayout.addWidget(toolbar)
        self.ui.horizontalLayout.addWidget(sc)
        
        
        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(self.horizontalLayout)
        self.setCentralWidget(widget)

        self.show()
        
        

def main():
    app = QApplication(sys.argv)
    root = Root()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())