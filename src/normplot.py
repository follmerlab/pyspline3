#!/usr/bin/env python
# normplot.py -- the NormPlot class used for displaying normalized data
#    and the spline. Has widgets to control number of knots and order of segments
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import sys
from PyQt5.QtWidgets import (QWidget, QApplication, QSpacerItem, QSizePolicy,
                             QVBoxLayout, QHBoxLayout, QStatusBar, QLabel,
                             QSpinBox)
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from .qwt_compat import QwtPlot, QwtCurve

from .dataplot import DataPlot
from . import calc

class NormSpin(QWidget):
    # Signal definitions
    knots_update = pyqtSignal()
    num_knots_update = pyqtSignal()

    def __init__(self, parent=None, name=None, fl=0):
        super(NormSpin, self).__init__(parent)
        if name:
            self.setObjectName(str(name))

        self.orders = []
        self.layout = QHBoxLayout(self)

        self.textLabel1 = QLabel(self)
        self.layout.addWidget(self.textLabel1)

        # set up spin box that controls number of knots
        self.spinBox1 = QSpinBox(self)
        self.spinBox1.setMaximumSize(QSize(50, 25))
        self.spinBox1.setMaximum(10)
        self.spinBox1.setMinimum(2)
        self.spinBox1.setValue(2)
        self.layout.addWidget(self.spinBox1)
        self.spinBox1.setToolTip("Number of spline knots (green vertical lines)\nIncrease to add more knots, decrease to remove\nDrag knots to adjust spline fit")

        # spacer between knots and orders
        self.spacer = QSpacerItem(21, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout.addItem(self.spacer)

        self.textLabel2 = QLabel(self)
        self.layout.addWidget(self.textLabel2)
        self.textLabel2.setToolTip("Polynomial order for each spline segment\nHigher order = more flexible fit\nOne spinbox per segment (# knots - 1)")

        # set up spin boxes that control orders, and set default value
        spinBox2 = QSpinBox(self)
        spinBox2.setMaximumSize(QSize(50, 25))
        spinBox2.setMaximum(10)
        spinBox2.setValue(3)
        self.layout.addWidget(spinBox2)
        self.orders.append(spinBox2)
        spinBox2.valueChanged.connect(self.slotKnotUpdate)

        # connect slots
        self.spinBox1.valueChanged.connect(self.slotNumKnotsChanged)

        self.languageChange()

    def slotNumKnotsChanged(self, val):
        val = val - 1  # segments = knots -1
        if val == len(self.orders) + 1:
            spinBox2 = QSpinBox(self)
            spinBox2.setMaximumSize(QSize(50, 25))
            spinBox2.setMaximum(10)
            spinBox2.setValue(3)
            self.layout.addWidget(spinBox2)
            spinBox2.show()
            self.orders.append(spinBox2)
            spinBox2.valueChanged.connect(self.slotKnotUpdate)

        elif val == len(self.orders) - 1:
            spinBox = self.orders.pop()
            spinBox.hide()

        self.num_knots_update.emit()

    def initializeSlots(self):
        for spinBox in self.orders:
            spinBox.valueChanged.connect(self.slotKnotUpdate)

    def slotKnotUpdate(self, *args):
        self.knots_update.emit()

    def getOrders(self):
        return self.orders

    def setNumKnots(self, value):
        while len(self.orders) > 0:
            spinBox = self.orders.pop()
            spinBox.hide()
            spinBox.deleteLater()
            self.num_knots_update.emit()

        for i in range(value - 1):
            spinBox = QSpinBox(self)
            spinBox.setMaximumSize(QSize(50, 25))
            spinBox.setMaximum(10)
            spinBox.setValue(2)
            self.layout.addWidget(spinBox)
            spinBox.show()
            self.orders.append(spinBox)
            spinBox.valueChanged.connect(self.slotKnotUpdate)

        self.spinBox1.setValue(value)

    def setOrders(self, orders):
        for i in range(len(self.orders)):
            self.orders[i].setValue(orders[i])

    def languageChange(self):
        self.textLabel1.setText(self.__tr("# of Knots:"))
        self.textLabel2.setText(self.__tr("Order of Segments:"))

    def __tr(self, s, c=None):
        return QApplication.translate("normData", s, c)
        
class NormPlot(QWidget):
    """Widget that shows normalized data and the fitted spline.

    Exposes methods:
      setNormData(xdata, ydata, E0)
      setE0(E0)
      setNumKnots(n)
      getOrders()

    Signals:
      plot_changed() - emitted after plot is updated
      closed() - emitted when widget is closed
    """
    plot_changed = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super(NormPlot, self).__init__(parent)

        self.xdata = []
        self.ydata = []
        self.spline = []
        self.E0 = None
        self._loading_from_file = False  # Flag to skip knot redistribution during file load

        # main layout
        main_layout = QVBoxLayout(self)

        # controls (spinboxes)
        controls_layout = QHBoxLayout()
        controls_layout.addSpacing(10)
        self.spinBoxes = NormSpin(self)
        controls_layout.addWidget(self.spinBoxes)
        controls_layout.addSpacing(10)
        main_layout.addLayout(controls_layout)

        # plot area
        plot_layout = QHBoxLayout()
        plot_layout.addSpacing(10)
        self.plot = DataPlot(QColor(Qt.darkGreen), self)
        # set a default x range until data is provided
        try:
            self.plot.setAxisScale(QwtPlot.xBottom, 0, 100)
        except Exception:
            pass
        plot_layout.addWidget(self.plot)
        plot_layout.addSpacing(10)
        main_layout.addLayout(plot_layout)

        # Create curves using QwtCurve directly
        self.normCurve = QwtCurve()
        self.normCurve.setTitle("norm")
        self.normCurve.setPen(QPen(QColor(Qt.black), 2))
        self.normCurve.attach(self.plot)

        self.splineCurve = QwtCurve()
        self.splineCurve.setTitle("spline")
        self.splineCurve.setPen(QPen(QColor(Qt.darkGreen), 2))
        self.splineCurve.attach(self.plot)

        # status bar
        self.status = QStatusBar(self)
        main_layout.addWidget(self.status)

        # wire signals
        # DataPlot defines positionMessage and signalUpdate
        try:
            self.plot.positionMessage.connect(self.status.showMessage)
        except Exception:
            pass

        try:
            self.plot.signalUpdate.connect(self.updatePlot)
        except Exception:
            pass

        self.spinBoxes.knots_update.connect(self.updatePlot)
        self.spinBoxes.num_knots_update.connect(self.updateKnots)
        self.spinBoxes.initializeSlots()

    # API
    def getOrders(self):
        return [sb.value() for sb in self.spinBoxes.getOrders()]

    def setOrders(self, orders):
        self.spinBoxes.setOrders(orders)

    def setE0(self, E0):
        self.E0 = E0

    def setNumKnots(self, value):
        self.spinBoxes.setNumKnots(value)

    def getNumKnotsBox(self):
        return self.spinBoxes.spinBox1

    def setNormData(self, xdata, ydata, E0):
        """Provide raw data to the plot and initialize curves."""
        self.xdata = list(xdata)
        self.ydata = list(ydata)
        self.E0 = E0
        # Ensure DataPlot has the x-axis data for snapping knots
        try:
            self.plot.setData(self.xdata)
        except Exception:
            pass

        # set data on norm curve (normalized later in updatePlot)
        try:
            self.normCurve.setData(self.xdata, self.ydata)
        except Exception:
            try:
                self.plot.setCurveData(self.normCurve, self.xdata, self.ydata)
            except Exception:
                pass

        # set axis range
        try:
            self.plot.setAxisScale(QwtPlot.xBottom, self.xdata[0], self.xdata[-1])
        except Exception:
            pass

    def updateKnots(self):
        """Recompute knot positions based on current number of knots."""
        # Skip redistribution if we're loading from a file
        if getattr(self, '_loading_from_file', False):
            return
            
        if not getattr(self.plot, 'knots', None):
            return
        
        # Guard: Don't try to update if we don't have data yet
        if not self.xdata or len(self.xdata) == 0:
            return

        minpos = self.plot.knots[0].getPosition()
        maxpos = self.plot.knots[-1].getPosition()

        kmin = calc.toKSpace(minpos, self.E0)
        kmax = calc.toKSpace(maxpos, self.E0)

        self.plot.resetPlot()
        size = self.spinBoxes.spinBox1.value()

        if size < 2:
            return

        div = (kmax - kmin) / float(size - 1)

        self.plot.addKnot(minpos)
        self.plot.addBoundsExceptions(0, 0, self.E0)

        for i in range(1, size - 1):
            temp = calc.fromKSpace(kmin + i * div, self.E0)
            temp2 = calc.getClosest(temp, self.xdata)
            self.plot.addKnot(temp2)

        self.plot.addKnot(maxpos)

        try:
            self.normCurve.setPen(QPen(QColor(Qt.black), 2))
            self.splineCurve.setPen(QPen(QColor(Qt.darkGreen), 2))
        except Exception:
            pass

        self.updatePlot()

    def updatePlot(self, *args):
        # Guard: Don't try to update if we don't have data yet
        if not self.xdata or not self.ydata or len(self.xdata) == 0 or len(self.ydata) == 0:
            return
            
        segs = self.getSegs()

        if not segs:
            return

        tempspline, sp_E0 = calc.calcSpline(self.xdata, self.ydata, self.E0, segs)

        self.normdata = [y / sp_E0 for y in self.ydata]
        self.splinedata = [s / sp_E0 for s in tempspline]

        # set data on curves
        try:
            self.normCurve.setData(self.xdata, self.normdata)
        except Exception:
            try:
                self.plot.setCurveData(self.normCurve, self.xdata, self.normdata)
            except Exception:
                pass

        try:
            self.splineCurve.setData(self.xdata, self.splinedata)
        except Exception:
            try:
                self.plot.setCurveData(self.splineCurve, self.xdata, self.splinedata)
            except Exception:
                pass

        try:
            self.plot.replot()
        except Exception:
            pass

        self.plot_changed.emit()

    def getSegs(self):
        knots = getattr(self.plot, 'knots', [])
        segs = []
        orders = self.spinBoxes.getOrders()

        # Guard: need at least 2 knots and matching orders
        if len(knots) < 2 or len(orders) < 1:
            return segs

        for i in range(len(knots) - 1):
            temp = knots[i].getPosition()
            xlow = calc.getClosest(temp, self.xdata)

            temp = knots[i + 1].getPosition()
            xhigh = calc.getClosest(temp, self.xdata)

            # Ensure we have a corresponding order spinbox
            order_val = orders[i].value() if i < len(orders) else 2
            seg = (order_val + 1, xlow, xhigh)
            segs.append(seg)

        return segs

    def closeEvent(self, e):
        e.accept()
        self.hide()
        self.closed.emit()

    def setShown(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    def __tr(self, s, c=None):
        return QApplication.translate("normData", s, c)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    plot = NormPlot()
    plot.show()
    sys.exit(app.exec_())
    
