#!/usr/bin/env python

# kplot.py -- the KPlot class used for the kspace (xafs) window
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
    Qt, QToolTip, QStatusBar, QHBoxLayout, QVBoxLayout, QLabel, QPen,
    QGridLayout)
from PyQt5.QtCore import pyqtSignal
from .qwt_compat import QwtPlot, QwtMarker, QwtCurve, QwtPlotItem, QwtPlotGrid

from .dataplot import DataPlot

class KPlot(QWidget):
    # Signal emitted when window is closed
    closed = pyqtSignal()
    
    def __init__(self,parent = None,name = None,fl = 0):
        # PyQt5: ignore name and fl parameters
        QWidget.__init__(self,parent)

        if name:
            self.setObjectName(str(name))
        else:
            self.setObjectName("XAFS Data")
    
        self.kdata=[]
        self.xafsdata=[]
        self.fixedknots=[]
        
        #spacer-plot-spacer
        layout=QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        spacer=QSpacerItem(10,10,QSizePolicy.Fixed,QSizePolicy.Fixed)
        layout.addItem(spacer)
        
        self.plot = DataPlot(QColor(Qt.blue),self,"frame3")
        self.plot.setAxisScale(QwtPlot.xBottom,0,100)
        
        # Create curve directly using QwtCurve
        self.xafsCurve = QwtCurve()
        self.xafsCurve.setTitle("exafs")
        self.xafsCurve.setPen(QPen(QColor(Qt.black), 2))
        self.xafsCurve.attach(self.plot)
        
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
            # Connect positionMessage signal to status bar
            self.plot.positionMessage.connect(self.status.showMessage)
        except Exception:
            pass
        
        self.setWindowTitle("EXAFS")

    def setXAFSData(self,kdata,xafsdata):
        self.plot.setAxisScale(QwtPlot.xBottom,0,kdata[-1])
        
        try:
            self.xafsCurve.setData(kdata, xafsdata)
        except Exception:
            try:
                # Fallback to plot helper
                self.plot.setCurveData(self.xafsCurve, kdata, xafsdata)
            except Exception:
                pass
                
        self.kdata=kdata
        self.xafsdata=xafsdata
        DataPlot.setData(self.plot,kdata)
        
        self.plot.replot()
        
    def clearFixedKnots(self):
        # Detach any previously attached fixed markers
        for marker in self.fixedknots:
            try:
                marker.detach()
            except Exception:
                try:
                    # Legacy fallback
                    self.plot.removeMarker(marker)
                except Exception:
                    pass
        self.fixedknots = []
        
    def addFixedKnot(self, pos):
        # Create a vertical green marker at the given k-space position
        # Use the same QwtPlotMarker pattern as Knot class
        try:
            from .qwt_compat import QwtPlotMarker
            marker = QwtPlotMarker()
            marker.setLineStyle(QwtPlotMarker.VLine)
            marker.setLinePen(QPen(QColor(Qt.darkGreen), 2))
            marker.setXValue(pos)
            marker.setYValue(0.0)
            marker.attach(self.plot)
            self.fixedknots.append(marker)
            self.plot.replot()
        except Exception as e:
            # If marker creation fails, silently continue
            print(f"Could not add fixed knot at {pos}: {e}")
            pass
    
    def closeEvent(self,e):
        self.hide()
        try:
            self.closed.emit()
        except Exception:
            # Handle case where signal isn't available
            pass

    def setShown(self,bool):
        if(bool):
            self.show()
        else:
            self.hide()
        
    def __tr(self,s,c = None):
        return qApp.translate("normData",s,c)

if(__name__=='__main__'):
    app=QApplication(sys.argv)
    plot=KPlot()
    app.setMainWidget(plot)
    
    xdata=[]
    ydata=[]
    file=open(sys.argv[1])
    
    line=file.readline()
    while(line):
        info=line.split()
        xdata.append(float(info[0]))
        ydata.append(float(info[1]))
        line=file.readline()
        
    file.close()
    
    plot.setXAFSData(xdata,ydata)
    plot.addFixedKnot(xdata[0]-0.01)
    plot.addFixedKnot(xdata[-1]+0.01)
    plot.plot.addKnot(xdata[0])
    plot.plot.addKnot(xdata[-1])
    
    plot.show()
    app.exec_loop()
    
