#HRV Application

import sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_window()
        self.showMaximized()

    def init_window(self):
        self.ui = uic.loadUi('interfaz.ui',self)
        self.actionOpen.triggered.connect(self.abrir_archivo)
    #     self.button = QPushButton('Abrir', self)
    #     self.button.clicked.connect(self.abrir_archivo)
    #     self.button.move(150, 260)
    #     self.button.resize(120, 40)
    #     self.button.setStyleSheet("background-color: #323e62; color: #e6e6e6")

    #     #barra de menús
    #     self.actionAbrir = QtWidgets.QAction(self)
    #     self.actionAbrir.setObjectName("actionAbrir")
    #     self.actionAbrir.setText("Open")
    #     self.actionAbrir.triggered.connect(self.abrir_archivo)
    #     self.actionGuardar = QtWidgets.QAction(self)
    #     self.actionGuardar.setObjectName("actionGuardar")
    #     self.actionGuardar.setText("Save")
    #     self.actionExportar = QtWidgets.QAction(self)
    #     self.actionExportar.setObjectName("actionExportar")
    #     self.actionExportar.setText("Export to PDF")
    #     self.actionSalir = QtWidgets.QAction(self)
    #     self.actionSalir.setObjectName("actionSalir")
    #     self.actionSalir.setText("Exit")
    #     menuBar = self.menuBar()
    #     # Creating menus using a QMenu object
    #     fileMenu = QMenu("&File", self)
    #     fileMenu.addAction(self.actionAbrir)
    #     fileMenu.addAction(self.actionGuardar)
    #     fileMenu.addAction(self.actionExportar)
    #     fileMenu.addAction(self.actionSalir)
    #     menuBar.addMenu(fileMenu)
    #     # Creating menus using a title
    #     editMenu = menuBar.addMenu("&Edit")
    #     helpMenu = menuBar.addMenu("&Help")

    def abrir_archivo(self):
        self.file = QFileDialog.getOpenFileName(self, "Selecciona un archivo", "/home/", "PDF Files (*.dat, *.hea)")[0]
        self.actionOpen.setText(os.path.basename(self.file))

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    root = Root()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())