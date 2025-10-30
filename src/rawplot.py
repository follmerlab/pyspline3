#!/usr/bin/env python

# rawplot.py -- the raw plot class used for displaying raw data and
# the background. Has controls to adjust order of the background
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from .qt_compat import (
    QWidget, QMainWindow, QDialog, QApplication, QPrinter, QPainter, QPixmap, QColor, QFontMetrics, QFont, QRect, QFileDialog, QMessageBox, QAction, QToolBar, QMenuBar, QMenu, QTextEdit, QPushButton, QSpacerItem, QSizePolicy, QString, SIGNAL, PYSIGNAL, qApp, translate,
    QHBoxLayout, QLabel, QSpinBox, QSize, Qt, QPen, QGridLayout, QToolTip
)
from PyQt5.QtCore import pyqtSignal
from .qwt_compat import QwtPlot, QwtMarker, QwtCurve, QwtPlotItem, QwtPlotGrid

from .dataplot import DataPlot
from . import calc
        
class RawPlot(QWidget):
    # Modern signal emitted when the plot data changes
    signalPlotChanged = pyqtSignal()
    def __init__(self, parent=None, name=None, fl=0):
        # PyQt5: QWidget(parent: QWidget = None, flags: Qt.WindowFlags = Qt.WindowFlags())
        # Ignore 'name' and 'fl' for PyQt5 compatibility
        QWidget.__init__(self, parent)
        if name:
            self.setObjectName(str(name))
        if not name:
            self.setObjectName("FFT Data")
        self.xdata = []
        self.ydata = []
        self.background = []
        self.E0 = 0
        
        # Create main layout
        main_layout = QGridLayout(self)
        
        # Create controls layout
        controls_layout = QHBoxLayout()
        self.textLabel1 = QLabel(self)
        self.textLabel1.setText("Order of Background:")
        controls_layout.addWidget(self.textLabel1)
        self.spinBox = QSpinBox(self)
        self.spinBox.setMaximumSize(QSize(50, 25))
        self.spinBox.setValue(2)
        self.spinBox.setMinimum(-1)
        controls_layout.addWidget(self.spinBox)
        spacer = QSpacerItem(100, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        controls_layout.addItem(spacer)

        # Create plot
        self.plot = DataPlot(QColor(Qt.red), self)
        self.plot.setAxisScale(QwtPlot.xBottom, 0, 100)

        # Create QwtCurve objects for raw and background data
        self.rawCurve = QwtCurve()
        self.rawCurve.setTitle("raw data")
        self.rawCurve.attach(self.plot)
        self.rawCurve.setPen(QPen(QColor(Qt.black), 2))

        self.backCurve = QwtCurve()
        self.backCurve.setTitle("background")
        self.backCurve.attach(self.plot)
        self.backCurve.setPen(QPen(QColor(Qt.red), 2))
        
        # Add controls and plot to main layout
        main_layout.addLayout(controls_layout, 0, 0)
        main_layout.addWidget(self.plot, 1, 0)

        self.spinBox.setToolTip("Change Order of Background")

        # PyQt5: New-style signal/slot connections
        self.plot.signalUpdate.connect(self.updatePlot)
        self.spinBox.valueChanged.connect(self.updatePlot)

    def getSpinBoxValue(self):
            return self.spinBox.value()
        
    def __tr(self,s,c = None):
        return qApp.translate("normData",s,c)
    
    def setRawData(self, xdata, ydata, E0):
        self.rawCurve.setData(xdata, ydata)
        self.xdata = xdata
        self.ydata = ydata
        self.E0 = E0
        DataPlot.setData(self.plot, xdata)
        self.plot.setAxisScale(QwtPlot.xBottom, xdata[0], xdata[-1])
        self.plot.replot()
        
    def updatePlot(self, *args):
        # def calcBackground(self,xmin,xmax):
        # Ensure we have two knots before computing background
        if len(self.plot.knots) < 2 or not self.xdata or not self.ydata:
            return
        order = self.getSpinBoxValue() + 1  # need constant!
        temp = self.plot.knots[0].getPosition()
        xmin = calc.getClosest(temp, self.xdata)
        lindex = self.xdata.index(xmin)
        temp = self.plot.knots[1].getPosition()
        xmax = calc.getClosest(temp, self.xdata)
        hindex = self.xdata.index(xmax)
        self.background = calc.calcBackground(self.xdata, self.ydata, lindex, hindex, order, self.E0)
        self.backCurve.setData(self.xdata, self.background)
        ymax = max([max(self.ydata), max(self.background)])
        ymin = min([min(self.ydata), min(self.background)])
        self.plot.setAxisScale(QwtPlot.yLeft, ymin, ymax)
        self.plot.replot()
        # Emit modern PyQt5 signal to notify listeners that the plot changed
        try:
            self.signalPlotChanged.emit()
        except Exception:
            # If for some reason signals aren't available, silently continue
            pass

if(__name__=='__main__'):
    import sys
    app=QApplication(sys.argv)
    plot=RawPlot()
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
    plot.setRawData(xdata,ydata,9200)
    plot.plot.addKnot(xdata[0])
    plot.plot.addKnot(xdata[-1])
    plot.updatePlot()
    plot.show()
    app.exec_loop()
    
