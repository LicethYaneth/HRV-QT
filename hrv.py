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
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
import pandas as pd
import statistics as st
from scipy.signal import find_peaks


from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

matplotlib.use('QT5Agg')


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=18, height=3, dpi=2):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = uic.loadUi('interfaz.ui',self)
        self.init_window()
        self.showMaximized() 
        

    def init_window(self):
        self.ui = uic.loadUi('interfaz.ui',self)
        self.ui.progressBar.setVisible(False)
        self.ui.titleProgress.setVisible(False)
        #self.pushButtonOpen.setStyleSheet("QWidget { background-color: white }")
        self.pushButtonOpen.clicked.connect(self.abrir_archivo)
        self.baseLineCorrection.clicked.connect(self.baseline_correct)
        self.normalGraphic.clicked.connect(self.normal_plot)
        self.RPeaks.clicked.connect(self.peaks)
        self.ui.showMaximized()

        ## ESTE ES EL BOTON DEL DIALOGO ##
        self.metadata.clicked.connect(self.mostrarDialogo)

    def mostrarDialogo(self):
        dialog = Dialog(self)  # self hace referencia al padre
        dialog.show()

        #self.ruta= QLabel(self)

    def abrir_archivo(self):
        self.ui.progressBar.setVisible(True)
        self.ui.titleProgress.setVisible(True)
        self.windowFile = QFileDialog()
        self.windowFile.setStyleSheet("QWidget {background-color: #ffffff}")
        self.file = QFileDialog.getOpenFileName(self.windowFile, "Selecciona un archivo", "/home/", "PDF Files (*.dat)")[0]

        record = wfdb.rdrecord(self.file[:-4]) 
        signals, fields = wfdb.rdsamp(self.file[:-4], channels=[0])
        record = wfdb.rdrecord(self.file[:-4], channels=[0])
        signal=signals.reshape(record.sig_len)
        filename = QFileInfo(self.file).fileName()

        self.ui.fileNameText.setText(self.file)
        self.ui.recordNameText.setText(filename)
        self.ui.fsText.setText(str(record.__dict__['fs']))
        self.ui.lenghtSignalText.setText(str(record.__dict__['sig_len']))


        
        def baseline_als(y, lam, p, niter=10):
            L = len(y)
            D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
            D = lam * D.dot(D.transpose()) # Precompute this term since it does not depend on `w`
            w = np.ones(L)
            W = sparse.spdiags(w, 0, L, L)
            for i in range(niter):
                W.setdiag(w) # Do not create a new matrix, just update diagonal values
                Z = W + D
                z = spsolve(Z, w*y)
                w = p * (y > z) + (1-p) * (y < z)
            return z 
        
        record = wfdb.rdrecord(self.file[:-4]) 
        signals, fields = wfdb.rdsamp(self.file[:-4], channels=[0])
        record = wfdb.rdrecord(self.file[:-4], channels=[0])
        self.signal=signals.reshape(record.sig_len)
        signal_bas=baseline_als(self.signal[:int(len(self.signal)/2)],100,0.001)
        signal_bas_2=baseline_als(self.signal[int(len(self.signal)/2):int(len(self.signal))],100,0.001)
        sub_1=np.subtract(self.signal[:int(len(self.signal)/2)],signal_bas)
        sub_2=np.subtract(self.signal[int(len(self.signal)/2):int(len(self.signal))],signal_bas_2)
        self.signal_com=np.concatenate((sub_1,sub_2),None)
        
        signal_prep=pd.DataFrame(self.signal_com)
        self.signal_prep_w=signal_prep.rolling(10).mean() 
        x=self.signal_prep_w.values.reshape(record.sig_len)
        self.peaks_1, _ = find_peaks(x, height=(0.75))
        self.desv=np.std(self.signal_prep_w.values[self.peaks_1])
        self.meanp=np.mean(self.signal_prep_w.values[self.peaks_1])
        self.peaks_out=[]
        self.peaks_pos=[]
        self.peaks_out_min=[]
        self.peaks_pos_min=[]
        print(self.desv)
        for i in range(len(self.peaks_1)):
            if self.signal_prep_w.values[self.peaks_1[i]]>self.meanp+2*self.desv:
                self.peaks_out.append(self.signal_prep_w.values[self.peaks_1[i]])
                self.peaks_pos.append(self.peaks_1[i])
        
        self.ui.progressBar.setVisible(False)
        self.ui.titleProgress.setVisible(False)
    



    def normal_plot(self):
        
        self.sc1 = MplCanvas(self, width=20, height=8, dpi=50)
        self.sc1.axes.plot(self.signal)
        self.sc = MplCanvas(self, width=35, height=2, dpi=50)
        self.sc.axes.plot(self.signal)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.toolbar1 = NavigationToolbar(self.sc1, self)
        self.ui.ventanaGraficas.addWidget(self.toolbar1)
        self.ui.ventanaGraficas.replaceWidget(self.ui.widgetToolbarBig, self.toolbar1)
        self.ui.toolbar1.setFixedHeight(38)
        self.ui.toolbar1.setStyleSheet('background-color: white')
        self.ui.ventanaGraficas.replaceWidget(self.ui.widgetBig, self.sc1)
        self.ui.ventanaGraficas.addWidget(self.toolbar)
        self.ui.ventanaGraficas.replaceWidget(self.ui.widgetToolbarSmall, self.toolbar)
        self.ui.toolbar.setFixedHeight(38)
        self.ui.toolbar.setStyleSheet('background-color: white')
        self.ui.ventanaGraficas.replaceWidget(self.ui.widgetSmall, self.sc)
        self.ui.sc.setFixedHeight(200)
        self.show()
    

        
    def baseline_correct(self):
        self.sc1.axes.plot(self.signal_com)
        self.sc.axes.plot(self.signal_com)

    def peaks(self):
        self.sc2 = MplCanvas(self, width=20, height=8, dpi=50)
        self.sc2.axes.plot(self.signal_prep_w)
        self.sc2.axes.plot(self.peaks_1, self.signal_prep_w.values[self.peaks_1], "o")
        self.sc2.axes.plot(self.peaks_pos,self.peaks_out,'o',color='green')
        self.sc3 = MplCanvas(self, width=35, height=2, dpi=50)
        self.sc3.axes.plot(self.signal_prep_w)
        self.sc3.axes.plot(self.peaks_1, self.signal_prep_w.values[self.peaks_1], "o")
        self.sc3.axes.plot(self.peaks_pos,self.peaks_out,'o',color='green')
        
        self.toolbar2 = NavigationToolbar(self.sc2, self)
        self.toolbar3 = NavigationToolbar(self.sc3, self)
        self.ui.ventanaGraficas.addWidget(self.toolbar2)
        self.ui.ventanaGraficas.replaceWidget(self.toolbar1,self.toolbar2)
        self.ui.toolbar2.setFixedHeight(38)
        self.ui.toolbar2.setStyleSheet('background-color: white')
        self.ui.ventanaGraficas.replaceWidget(self.sc1,self.sc2)
        self.ui.ventanaGraficas.addWidget(self.toolbar3)
        self.ui.ventanaGraficas.replaceWidget(self.toolbar,self.toolbar3)
        self.ui.toolbar3.setFixedHeight(38)
        self.ui.toolbar3.setStyleSheet('background-color: white')
        self.ui.ventanaGraficas.replaceWidget(self.sc,self.sc3)
        self.ui.sc3.setFixedHeight(200)
        plt.show()

class Dialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(Dialog, self).__init__(*args, **kwargs)
        self.uiMetadataModal = uic.loadUi('metadataModal.ui',self)
        self.uiMetadataModal.setWindowTitle("Resumen del archivo {{fileName}}")
        self.uiMetadataModal.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        #self.uiMetadataModal.buttonBox.accepted.connect(self)
        self.uiMetadataModal.buttonBox.rejected.connect(self.closeModal)

    def closeModal(self):
        self.close()

def main():
    app = QApplication(sys.argv)
    root = Root()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setStyle('Adwaita')
    win = Window()
    win.show()
    sys.exit(app.exec_())
