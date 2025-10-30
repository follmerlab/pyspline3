#!/usr/bin/env python

# fftplot.py -- the FFTPlot class used to display the Fourier transform
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from .qt_compat import (QWidget, QMainWindow, QDialog, QApplication, QPrinter,
    QPainter, QPixmap, QColor, QFontMetrics, QFont, QRect, QFileDialog,
    QMessageBox, QAction, QToolBar, QMenuBar, QMenu, QTextEdit, QPushButton,
    QSpacerItem, QSizePolicy, QString, SIGNAL, PYSIGNAL, qApp, translate,
    QToolTip, Qt, QStatusBar, QHBoxLayout, QGridLayout, QPen)
from PyQt5.QtCore import pyqtSignal
from .qwt_compat import QwtPlot, QwtMarker, QwtCurve, QwtPlotItem, QwtPlotGrid, QwtWheel

from .dataplot import DataPlot

class FFTPlot(QWidget):
    # Signal emitted when window is closed
    closed = pyqtSignal()
    
    def __init__(self,parent = None,name = None,fl = 0):
        # PyQt5: ignore name and fl parameters
        QWidget.__init__(self,parent)

        if name:
            self.setObjectName(str(name))
        else:
            self.setObjectName("FFT Data")
    
        #spacer-plot-spacer
        layout=QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        spacer=QSpacerItem(10,10,QSizePolicy.Fixed,QSizePolicy.Fixed)
        layout.addItem(spacer)
        
        self.plot = DataPlot(QColor(Qt.black),self,"frame3")
        self.plot.setAxisScale(QwtPlot.xBottom,0,5)
        
        # Create curve directly using QwtCurve
        self.fftcurve = QwtCurve()
        self.fftcurve.setTitle("fft")
        self.fftcurve.setPen(QPen(QColor(Qt.black), 2))
        self.fftcurve.attach(self.plot)
        
        layout.addWidget(self.plot)
        layout.addItem(spacer)
        
        #spacer-wheel-spacer
        layout2=QHBoxLayout()
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.setSpacing(6)
        
        spacer=QSpacerItem(240,10,QSizePolicy.Fixed,QSizePolicy.Fixed)
        layout2.addItem(spacer)
        
        # Use QSlider if QwtWheel is not available
        if QwtWheel is None:
            from PyQt5.QtWidgets import QSlider
            from PyQt5.QtCore import Qt as QtCore_Qt
            self.wheel = QSlider(QtCore_Qt.Horizontal, self)
            self.wheel.setMinimum(10)
            self.wheel.setMaximum(100)
            self.wheel.setValue(50)
        else:
            self.wheel = QwtWheel(self)
            self.wheel.setValue(50.0)
            
        self.wheel.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed))
        layout2.addWidget(self.wheel)
        
        spacer2=QSpacerItem(200,10,QSizePolicy.Fixed,QSizePolicy.Fixed)
        layout2.addItem(spacer2)
        
        # Set wheel tooltip using modern API
        self.wheel.setToolTip("Adjust R scale")
        
        #add plot and wheel to grid layout
        normDataLayout = QGridLayout(self)
        normDataLayout.setContentsMargins(0, 0, 0, 0)
        normDataLayout.setSpacing(6)
        normDataLayout.addItem(spacer,0,0)
        normDataLayout.addLayout(layout,2,0)
        normDataLayout.addLayout(layout2,3,0)
        
        self.status=QStatusBar(self)
        normDataLayout.addWidget(self.status,4,0)
        
        try:
            # Connect signals using modern API
            self.plot.positionMessage.connect(self.status.showMessage)
            self.wheel.valueChanged.connect(self.wheelValueChanged)
        except Exception:
            pass
        
        self.setWindowTitle("Fourier Transform")

        #self.clearWState(Qt.WState_Polished)
        
    def __tr(self,s,c = None):
        return qApp.translate("normData",s,c)
        
    def closeEvent(self,e):
        self.hide()
        try:
            self.closed.emit()
        except Exception:
            pass
        
    def setShown(self,bool):
        if(bool):
            self.show()
        else:
            self.hide()
            
    def wheelValueChanged(self,value):
        self.plot.setAxisScale(QwtPlot.xBottom,0,value/10+1)
        self.plot.replot()
        
    def setFFTData(self,rdata,fftdata):
        self.rdata=rdata
        self.fftdata=fftdata
        
        try:
            # Use modern curve API
            self.fftcurve.setData(rdata, fftdata)
        except Exception:
            try:
                # Fallback to plot helper method
                self.plot.setCurveData(self.fftcurve, rdata, fftdata)
            except Exception:
                pass
                
        self.plot.replot()
        
if(__name__=='__main__'):
    import sys
    app = QApplication(sys.argv)
    plot = FFTPlot()
    if hasattr(app, 'setMainWidget'):
        app.setMainWidget(plot)
    plot.show()
    app.exec_() # Modern name in PyQt5
    
