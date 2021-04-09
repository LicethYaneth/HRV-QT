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
from hrvanalysis import get_time_domain_features
from hrvanalysis import get_frequency_domain_features,get_geometrical_features
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
        self.pushBaseLineCorrection.clicked.connect(self.baseline_correct)
        self.pushNormalGraphic.clicked.connect(self.normal_plot)
        self.pushRPeaks.clicked.connect(self.peaks)
        self.ui.showMaximized()

        ## ESTE ES EL BOTON DEL DIALOGO ##
        self.pushMetadata.clicked.connect(self.mostrarDialogo)

    def mostrarDialogo(self):
        dialog = Dialog(self)  # self hace referencia al padre
        dialog.show()
        dialog.metadata(self=self)

        #self.ruta= QLabel(self)

    def abrir_archivo(self):
        self.windowFile = QFileDialog()
        self.windowFile.setStyleSheet("QWidget {background-color: #ffffff}")
        self.file = QFileDialog.getOpenFileName(self.windowFile, "Selecciona un archivo", "/home/", "PDF Files (*.dat)")[0]
        self.ui.progressBar.setVisible(True)
        self.ui.titleProgress.setVisible(True)
        record = wfdb.rdrecord(self.file[:-4]) 
        signals, fields = wfdb.rdsamp(self.file[:-4], channels=[0])
        self.record = wfdb.rdrecord(self.file[:-4], channels=[0])
        signal=signals.reshape(self.record.sig_len)
        filename = QFileInfo(self.file).fileName()

        self.ui.fileNameText.setText(self.file)
        self.ui.recordNameText.setText(filename)
        self.ui.fsText.setText(str(self.record.__dict__['fs']))
        self.ui.lenghtSignalText.setText(str(self.record.__dict__['sig_len']))
    


        
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
        self.record = wfdb.rdrecord(self.file[:-4], channels=[0])
        self.signal=signals.reshape(self.record.sig_len)
        signal_bas=baseline_als(self.signal[:int(len(self.signal)/2)],100,0.001)
        signal_bas_2=baseline_als(self.signal[int(len(self.signal)/2):int(len(self.signal))],100,0.001)
        sub_1=np.subtract(self.signal[:int(len(self.signal)/2)],signal_bas)
        sub_2=np.subtract(self.signal[int(len(self.signal)/2):int(len(self.signal))],signal_bas_2)
        self.signal_com=np.concatenate((sub_1,sub_2),None)
        
        signal_prep=pd.DataFrame(self.signal_com)
        self.signal_prep_w=signal_prep.rolling(10).mean() 
        x=self.signal_prep_w.values.reshape(self.record.sig_len)
        self.peaks_1, _ = find_peaks(x, height=(0.7))
        self.desv=np.std(self.signal_prep_w.values[self.peaks_1])
        self.meanp=np.mean(self.signal_prep_w.values[self.peaks_1])
        self.peaks_out=[]
        self.peaks_pos=[]
        self.peaks_fpos=[]
        self.peaks_fout=[]
        self.peaks_out_min=[]
        self.peaks_pos_min=[]
        print(self.desv)
        for i in range(len(self.peaks_1)):
            if self.signal_prep_w.values[self.peaks_1[i]]>self.meanp+2*self.desv:
                self.peaks_out.append(self.signal_prep_w.values[self.peaks_1[i]])
                self.peaks_pos.append(self.peaks_1[i])
            else:
                self.peaks_fpos.append(self.peaks_1[i])
                self.peaks_fout.append(self.signal_prep_w.values[self.peaks_1[i]])

        #------ SDANN --------   
        num_seg=int(record.sig_len/(200*60*5))
        time_5min=200*60*5 
        Useg_5min=np.zeros(num_seg)
        seg_5min=np.zeros(num_seg)
        temp=0
        for i in range(num_seg):
            Useg_5min[i]=temp
            temp=temp+time_5min   
        
        for j in range(len(Useg_5min)-1):
            picos=np.array(self.peaks_fpos)[(np.array(self.peaks_fpos)>Useg_5min[j]) & (Useg_5min[j+1]>=np.array(self.peaks_fpos))]
            intervalosNN5 = np.zeros(picos.shape)
            for i in range(len(picos)-1):
                intervalosNN5[i]=picos[i+1]-picos[i]
            seg_5min[j]=np.mean(intervalosNN5)

        self.sdann=st.stdev(seg_5min)
        #-------- SDNN INDEX -------
        seg_5min_sd=np.zeros(num_seg)
        for j in range(num_seg-1):
            picos=self.peaks_1[(self.peaks_1>Useg_5min[j]) & (Useg_5min[j+1]>=self.peaks_1)]
            intervalosNN5 = np.zeros(picos.shape)
            for i in range(len(picos)-1):
                intervalosNN5[i]=picos[i+1]-picos[i]
            if len(intervalosNN5)!=0:
                seg_5min_sd[j]=st.stdev(intervalosNN5)
        self.sdnn_index= np.mean(seg_5min_sd)

        self.ui.progressBar.setVisible(False)
        self.ui.titleProgress.setVisible(False)
        self.normal_plot()
        self.metrics()
    



    def normal_plot(self):
        
        self.sc1 = MplCanvas(self, width=30, height=18, dpi=50)
        self.sc1.axes.plot(self.signal)
        self.toolbar1 = NavigationToolbar(self.sc1, self)
        self.ui.ventanaGraficas.addWidget(self.toolbar1)
        self.ui.ventanaGraficas.replaceWidget(self.ui.widgetToolbarBig, self.toolbar1)
        self.ui.toolbar1.setFixedHeight(38)
        self.ui.toolbar1.setStyleSheet('background-color: white')
        self.ui.ventanaGraficas.replaceWidget(self.ui.widgetBig, self.sc1)
        self.show()
    

        
    def baseline_correct(self):
        self.sc1.axes.plot(self.signal_com)
        self.sc.axes.plot(self.signal_com)

    def peaks(self):
            
        #np.delete(self.peaks_1,list(self.peaks_pos))
        self.sc2 = MplCanvas(self, width=30, height=18, dpi=50)
        self.sc2.axes.plot(self.signal_prep_w)
        self.sc2.axes.plot(self.peaks_fpos, self.signal_prep_w.values[self.peaks_fpos], "o")
        #self.sc2.axes.plot(self.peaks_pos,self.peaks_out,'o',color='green')
        
        self.toolbar2 = NavigationToolbar(self.sc2, self)
        self.ui.ventanaGraficas.addWidget(self.toolbar2)
        self.ui.ventanaGraficas.replaceWidget(self.toolbar1,self.toolbar2)
        self.ui.toolbar2.setFixedHeight(38)
        self.ui.toolbar2.setStyleSheet('background-color: white')
        self.ui.ventanaGraficas.replaceWidget(self.sc1,self.sc2)
        plt.show()

    def metrics(self):
        import pyhrv.tools as tools
        intervalosNN = tools.nn_intervals(self.peaks_fpos)
        time_domain_features = get_time_domain_features(intervalosNN[intervalosNN!=0])
        frecuency_domain_features= get_frequency_domain_features(intervalosNN)
        geometrical_features= get_geometrical_features(intervalosNN)


        self.ui.scrollAreaFeatures.setStyleSheet('background-color: white')

        layout = QHBoxLayout()   
        label = QLabel('<h3>Time Domain Features<h3>')
        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        label.setStyleSheet("color: rgb(59,59,59)")
        label.setMaximumWidth(290)        
        layout.addWidget(label)
        self.ui.verticalLayout_features.addLayout(layout)


        time_domain_features_to_show={'SDNN':time_domain_features['sdnn'],'SDSD':time_domain_features['sdsd'],'SDANN':self.sdann,'RMSSD':time_domain_features['rmssd']}
        time_domain_features_to_show2={'NN20 Count':time_domain_features['nni_20'],'NN50 Count':time_domain_features['nni_50'],'PNN50 Count':time_domain_features['pnni_50'],'PNN20 Count':time_domain_features['pnni_20']}

        for key,value in time_domain_features_to_show.items():
            layout = QVBoxLayout()
            label = QLabel('<h4>'+str(key)+':</h4>')
            label.setStyleSheet("color: rgb(59,59,59)")
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label.setMaximumWidth(122)        
            layout.addWidget(label)
            label1 = QLabel("{:.4f}".format(value))
            label1.setStyleSheet("padding: 5px; border: 1px solid #cccccc; border-radius: 5px; background-color:#cccccc;")
            label1.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label1.setMaximumWidth(122)        
            layout.addWidget(label1)
            self.ui.verticalLayout_features1.addLayout(layout)

        for key,value in time_domain_features_to_show2.items():
            layout = QVBoxLayout()
            label = QLabel('<h4>'+str(key)+':</h4>')
            label.setStyleSheet("color: rgb(59,59,59)")
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label.setMaximumWidth(122)        
            layout.addWidget(label)
            label1 = QLabel("{:.4f}".format(value))
            label1.setStyleSheet("padding: 5px; border: 1px solid #cccccc; border-radius: 5px; background-color:#cccccc;")
            label1.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label1.setMaximumWidth(122)        
            layout.addWidget(label1)
            self.ui.verticalLayout_features2.addLayout(layout)

        frecuency_domain_features_to_show={'LF':frecuency_domain_features['lf'],'HF':frecuency_domain_features['hf'],'VLF':frecuency_domain_features['vlf']}
        frecuency_domain_features_to_show2={'LF norm':frecuency_domain_features['vlf'],'HF norm':frecuency_domain_features['hfnu'],'Total power':frecuency_domain_features['total_power']}
        
        layout = QHBoxLayout()         
        label = QLabel('<h3>Frecuency Domain Features</h3>')
        label.setStyleSheet("color: rgb(59,59,59)")
        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        label.setMaximumWidth(290)        
        layout.addWidget(label)
        self.ui.verticalLayout_features3.addLayout(layout)
        
        for key,value in frecuency_domain_features_to_show.items():
            layout = QVBoxLayout()        
            label = QLabel('<h4>'+str(key)+':</h4>')
            label.setStyleSheet("color: rgb(59,59,59)")
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label.setMaximumWidth(122)        
            layout.addWidget(label)
            label1 = QLabel("{:.4f}".format(value))
            label1.setStyleSheet("padding: 5px; border: 1px solid #cccccc; border-radius: 5px; background-color:#cccccc;")
            label1.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label1.setMaximumWidth(122)        
            layout.addWidget(label1)
            self.ui.verticalLayout_features4.addLayout(layout)
        for key,value in frecuency_domain_features_to_show2.items():
            layout = QVBoxLayout()        
            label = QLabel('<h4>'+str(key)+':</h4>')
            label.setStyleSheet("color: rgb(59,59,59)")
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label.setMaximumWidth(122)        
            layout.addWidget(label)
            label1 = QLabel("{:.4f}".format(value))
            label1.setStyleSheet("padding: 5px; border: 1px solid #cccccc; border-radius: 5px; background-color:#cccccc;")
            label1.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label1.setMaximumWidth(122)        
            layout.addWidget(label1)
            self.ui.verticalLayout_features5.addLayout(layout)
        
        geometrical_features_to_show={'TINN':geometrical_features['tinn']}
        geometrical_features_to_show2={'Triangular Index':geometrical_features['triangular_index']}

        layout = QHBoxLayout() 
        label = QLabel('<h3>Geometrical Domain Features</h3>')
        label.setStyleSheet("color: rgb(59,59,59)")
        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        label.setMaximumWidth(290)        
        layout.addWidget(label)
        self.ui.verticalLayout_features6.addLayout(layout)

        for key,value in geometrical_features_to_show2.items():
            layout = QVBoxLayout()        
            label = QLabel('<h4>'+str(key)+':</h4>')
            label.setStyleSheet("color: rgb(59,59,59)")
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label.setMaximumWidth(122)        
            layout.addWidget(label)
            label1 = QLabel("{:.4f}".format(value))
            label1.setStyleSheet("padding: 5px; border: 1px solid #cccccc; border-radius: 5px; background-color:#cccccc;")
            label1.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label1.setMaximumWidth(122)        
            layout.addWidget(label1)
            self.ui.verticalLayout_features7.addLayout(layout)
        for key,value in geometrical_features_to_show.items():
            layout = QVBoxLayout()        
            label = QLabel('<h4>'+str(key)+':</h4>')
            label.setStyleSheet("color: rgb(59,59,59)")
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label.setMaximumWidth(122)        
            layout.addWidget(label)
            label1 = QLabel(str(value))
            label1.setStyleSheet("padding: 5px; border: 1px solid #cccccc; border-radius: 5px; background-color:#cccccc;")
            label1.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label1.setMaximumWidth(122)        
            layout.addWidget(label1)
            self.ui.verticalLayout_features8.addLayout(layout)
        
        from hrvanalysis import plot_psd
        #plot_psd(intervalosNN, method="welch")
   



class Dialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(Dialog, self).__init__(*args, **kwargs)
        self.uiMetadataModal = uic.loadUi('metadataModal.ui',self)
        self.uiMetadataModal.setWindowTitle("Resumen del archivo {{fileName}}")
        self.uiMetadataModal.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        #self.uiMetadataModal.buttonBox.accepted.connect(self)
        self.uiMetadataModal.buttonBox.rejected.connect(self.closeModal)

    def metadata(dialog,self):
        layout = QHBoxLayout()
        label = QLabel('<center><b>Record metadata</b></center>')
        layout.addWidget(label)
        dialog.uiMetadataModal.verticalitemsmetadata.addLayout(layout)
        
        for key,value in self.record.__dict__.items():
            layout = QHBoxLayout()
            label = QLabel('<b>'+str(key)+'</b>')
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            label.setMaximumWidth(200)
            layout.addWidget(label)
            label = QLabel(str(value))
            label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignVCenter)
            layout.addWidget(label)
            dialog.uiMetadataModal.verticalitemsmetadata.addLayout(layout)
           
    

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
