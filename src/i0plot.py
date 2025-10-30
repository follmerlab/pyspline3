#!/usr/bin/env python

# i0plot.py -- the I0Plot class used for displaying I0 data
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import sys
from .qt_compat import (QWidget, QMainWindow, QDialog, QApplication, QPrinter,
    QPainter, QPixmap, QColor, QFontMetrics, QFont, QRect, QFileDialog,
    QMessageBox, QAction, QToolBar, QMenuBar, QMenu, QTextEdit, QPushButton,
    QSpacerItem, QSizePolicy, QString, SIGNAL, PYSIGNAL, qApp, translate,
    Qt, QPen, QGridLayout, QHBoxLayout, QStatusBar)
from PyQt5.QtCore import pyqtSignal
from .qwt_compat import QwtPlot, QwtMarker, QwtCurve, QwtPlotItem, QwtPlotGrid

from .dataplot import DataPlot

class I0Plot(QWidget):
    # Signal emitted when the window is closed
    closed = pyqtSignal()
    
    def __init__(self,parent = None,name = None,fl = 0):
        # PyQt5: ignore name and fl parameters
        QWidget.__init__(self,parent)

        if name:
            self.setObjectName(str(name))
        else:
            self.setObjectName("I0 Data")
    
        #spacer-plot-spacer
        layout=QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        spacer=QSpacerItem(10,10,QSizePolicy.Fixed,QSizePolicy.Fixed)
        layout.addItem(spacer)
        
        self.plot = DataPlot(QColor(Qt.black),self,"frame3")
        self.plot.setAxisScale(QwtPlot.xBottom,0,100)
        layout.addWidget(self.plot)
        
        layout.addItem(spacer)
        
        #add everything to grid layout
        #spacer-spinboxes-plots-statusbar
        normDataLayout = QGridLayout(self)
        normDataLayout.setContentsMargins(0, 0, 0, 0)
        normDataLayout.setSpacing(6)
        normDataLayout.addItem(spacer,0,0)
        normDataLayout.addLayout(layout,2,0)
        
        self.status=QStatusBar(self)
        normDataLayout.addWidget(self.status,3,0)
        
        try:
            self.plot.positionMessage.connect(self.status.showMessage)
        except Exception:
            pass
            
        # Create curve directly using QwtCurve
        self.curve = QwtCurve()
        self.curve.setTitle("i0data")
        self.curve.attach(self.plot)
        self.curve.setPen(QPen(QColor(Qt.black), 2))
        
        self.setWindowTitle("I0 Data")

    def setI0Data(self,xdata,ydata):
        self.xdata=xdata
        self.ydata=ydata
        
        try:
            self.curve.setData(xdata, ydata)
        except Exception:
            try:
                # Fallback to plot helper method if needed
                self.plot.setCurveData(self.curve, xdata, ydata)
            except Exception:
                pass
                
        self.plot.setAxisScale(QwtPlot.xBottom,min(xdata),max(xdata))
        self.plot.replot()
        
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
        
    def __tr(self,s,c = None):
        return qApp.translate("IOData",s,c)

if(__name__=='__main__'):
    app=QApplication(sys.argv)
    plot=I0Plot()
    app.setMainWidget(plot)
    plot.show()
    app.exec_loop()
    
