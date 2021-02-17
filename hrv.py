#HRV Application

import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets
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
        self.resize(1024, 768)
        self.setWindowTitle('HRV Analitic')
        self.setWindowIcon(QtGui.QIcon("favicon.svg"))

    def init_window(self):
        self.button = QPushButton('Abrir', self)
        self.button.clicked.connect(self.abrir_archivo)
        self.button.move(150, 260)
        self.button.resize(120, 40)
        self.button.setStyleSheet("background-color: #FFCC00; color: #1E1E1E")
        self.ruta= QLabel(self)

        self.pushButton_10.clicked.connect(self.abrir_archivo)

        
        #Esto muestra la ventana
        self.showMaximized()

        #barra de menús
        # self.actionAbrir = QtWidgets.QAction(self)
        # self.actionAbrir.setObjectName("actionAbrir")
        # self.actionAbrir.setText("Open")
        # self.actionAbrir.triggered.connect(self.abrir_archivo)
        # self.actionGuardar = QtWidgets.QAction(self)
        # self.actionGuardar.setObjectName("actionGuardar")
        # self.actionGuardar.setText("Save")
        # self.actionExportar = QtWidgets.QAction(self)
        # self.actionExportar.setObjectName("actionExportar")
        # self.actionExportar.setText("Export to PDF")
        # self.actionSalir = QtWidgets.QAction(self)
        # self.actionSalir.setObjectName("actionSalir")
        # self.actionSalir.setText("Exit")
        # menuBar = self.menuBar()
        # # Creating menus using a QMenu object
        # fileMenu = QMenu("&File", self)
        # fileMenu.addAction(self.actionAbrir)
        # fileMenu.addAction(self.actionGuardar)
        # fileMenu.addAction(self.actionExportar)
        # fileMenu.addAction(self.actionSalir)
        # menuBar.addMenu(fileMenu)
        # # Creating menus using a title
        # editMenu = menuBar.addMenu("&Edit")
        # helpMenu = menuBar.addMenu("&Help")

    def abrir_archivo(self):
        self.file = QFileDialog.getOpenFileName(self, "Selecciona un archivo", "/home/", "PDF Files (*.dat)")[0]
        self.pushButton_10.clicked.connect(self.abrir_archivo)
        #self.ruta.setText(os.path.(self.file))
        self.ruta.setText(self.file)
        record = wfdb.rdrecord(self.file[:-4]) 
        signals, fields = wfdb.rdsamp(self.file[:-4], channels=[0])
        record = wfdb.rdrecord(self.file[:-4], channels=[0])
        signal=signals.reshape(record.sig_len)
        sc = MplCanvas(self, width=35, height=3, dpi=50)
        sc.axes.plot(signal)
        toolbar = NavigationToolbar(sc, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
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