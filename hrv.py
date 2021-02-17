#HRV Application

import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class interfaz(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_window()

    def init_window(self):
        self.title = "HRV"
        self.setStyleSheet("background-color: #1E1E1E; color: #D6D6D6; font: 10pt")
        
        #boton de abrir
        self.button = QPushButton('Abrir', self)
        self.button.clicked.connect(self.abrir_archivo)
        self.button.move(150, 260)
        self.button.resize(120, 40)
        self.button.setStyleSheet("background-color: #FFCC00; color: #1E1E1E")
        self.ruta= QLabel(self)
        self.ruta.setText("Buenassssss")
        self.ruta.setStyleSheet("color:white")
        self.ruta.move(500,300)
        self.ruta.resize(900,300)
        #Esto muestra la ventana
        self.showMaximized()

    def abrir_archivo(self):
        self.file = QFileDialog.getOpenFileName(self, "Selecciona un archivo", "/home/", "PDF Files (*.dat)")[0]
        self.button.setText(os.path.basename(self.file))
        #self.ruta.setText(os.path.(self.file))
        self.ruta.setText(self.file)
        
        

def main():
    app = QApplication(sys.argv)
    root = Root()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app = QApplication([])
    window = interfaz()
    # window.show()
    sys.exit(app.exec_())