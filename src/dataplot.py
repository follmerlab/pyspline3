#!/usr/bin/env python

# data.py -- the DataPlot class used as a parent class to handle 
#   the plots and tracking/marker mouse movements
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import sys
from .qt_compat import QWidget, QMainWindow, QDialog, QApplication, QPrinter, QPainter, QPixmap, QColor, QFontMetrics, QFont, QRect, QFileDialog, QMessageBox, QAction, QToolBar, QMenuBar, QMenu, QTextEdit, QPushButton, QSpacerItem, QSizePolicy, QString, SIGNAL, PYSIGNAL, qApp, translate
from .qwt_compat import QwtPlot, QwtMarker, QwtCurve, QwtPlotItem, QwtPlotGrid
from PyQt5.QtCore import pyqtSignal

from .knot import Knot
from . import calc

class DataPlot(QwtPlot):
    # Define custom signals
    signalUpdate = pyqtSignal()
    signalChangedPlot = pyqtSignal()
    positionMessage = pyqtSignal(str)

    def __init__(self, color, *args):
        # Filter out old-style string name parameters for PyQt5 compatibility
        # DataPlot(color, parent, name) -> DataPlot(color, parent)
        filtered_args = []
        for arg in args:
            if not isinstance(arg, str):
                filtered_args.append(arg)
        
        QwtPlot.__init__(self, *filtered_args)
        
        self.mode='NONE'
        
        self.knots=[]
        self.color=color
        self.excepts=[]
        self.data=[]
        
        # Connect mouse events
        self.canvas().setMouseTracking(True)
        self.canvas().mousePressEvent = self.slotMousePressed
        self.canvas().mouseMoveEvent = self.slotMouseMoved
        self.canvas().mouseReleaseEvent = self.slotMouseReleased
    
    def addKnot(self, pos, lock=False):
        
        # Get axis bounds - use axisInterval for PythonQwt compatibility
        try:
            # PythonQwt uses axisInterval()
            interval = self.axisInterval(QwtPlot.xBottom)
            dmin = interval.minValue()
            dmax = interval.maxValue()
        except Exception:
            # Fallback: try legacy canvasMap with s1/s2
            try:
                scale_map = self.canvasMap(QwtPlot.xBottom)
                dmin = scale_map.s1()
                dmax = scale_map.s2()
            except Exception:
                # Last resort: use plot axis scale
                dmin = self.axisScaleDiv(QwtPlot.xBottom).lowerBound()
                dmax = self.axisScaleDiv(QwtPlot.xBottom).upperBound()
        
        # if no other knots, just add and set boundary to be max and min
        if len(self.knots) == 0:
            knot = Knot(pos, self.color, self)
            knot.setBoundary(dmin, dmax)
            
            # insertMarker doesn't exist in PythonQwt, knot is already attached via Knot.__init__
            try:
                self.insertMarker(knot)
            except Exception:
                pass  # Already attached in Knot.__init__
                
            self.knots.append(knot)
            knot.setLock(lock)
            return
            
        # make sure new position is reasonable
        last = self.knots[-1]
        lastpos = last.getPosition()
        
        if pos < lastpos:
            print("New knot position is lower than previous knots")
            return
        
        xmax = dmax
        if pos > xmax:
            pos = xmax
        
        xmin = dmin
        if pos < xmin:
            pos = xmin
        
        # create and add knot, adding boundary of previous knot
        knot = Knot(pos, self.color, self)
        knot.setLock(lock)
        # Set wide boundaries: previous knot position to axis max
        # Allow ~1 eV minimum separation for stability
        knot.setBoundary(lastpos + 1.0, xmax)
        
        try:
            self.insertMarker(knot)
        except Exception:
            pass  # Already attached in Knot.__init__
            
        self.knots.append(knot)
        
        # Update previous knot boundary: axis min to new knot position
        # This allows knots to move freely within the data range
        bndy = last.getBoundary()
        bndy[1] = pos - 1.0
        last.setBoundary(bndy[0], bndy[1])
        
        self.fixKnotsBounds()
        self.signalChangedPlot.emit()
        self.replot()
    
    def removeKnot(self):
        if self.knots:
            # Remove the last knot's marker from the plot
            last_knot = self.knots[-1]
            try:
                # Try to detach the marker (PythonQwt method)
                last_knot.detach()
            except Exception:
                # Fallback: try legacy removeMarker if available
                try:
                    keys = self.markerKeys()
                    if keys:
                        self.removeMarker(keys[-1])
                except Exception:
                    pass
            
            self.knots.pop()
            self.fixKnotsBounds()
            self.signalChangedPlot.emit()
            self.replot()
    
    def resetPlot(self):
        """Clear all knots and markers from the plot."""
        # Remove all knot markers
        for knot in self.knots:
            try:
                # Try PythonQwt method
                knot.detach()
            except Exception:
                # Fallback for legacy Qwt
                try:
                    self.removeMarker(knot)
                except Exception:
                    pass
        self.knots = []
        self.replot()
            
    def addBoundsExceptions(self,knot,bnd,value):
        bounds=self.knots[knot].getBoundary()
        bounds[bnd]=value
        self.knots[knot].setBoundary(bounds[0],bounds[1])
        
        self.excepts.append((knot,bnd,value))
        
    def slotMousePressed(self,event):
        self.oldx = self.invTransform(QwtPlot.xBottom, event.x())
        self.oldy = self.invTransform(QwtPlot.yLeft, event.y())
        # Find nearest knot to the mouse in pixel space
        self.movingMarker = None
        if self.knots:
            px = event.x()
            py = event.y()
            best_knot = None
            best_dist = 1e9
            for k in self.knots:
                kx = self.transform(QwtPlot.xBottom, k.xValue())
                ky = self.transform(QwtPlot.yLeft, k.yValue()) if hasattr(k, 'yValue') else self.transform(QwtPlot.yLeft, 0.0)
                # Use distance in x-direction only for vertical markers
                d = abs(kx - px)
                if d < best_dist:
                    best_dist = d
                    best_knot = k
            # Use a generous threshold (30 pixels) but only select the single closest knot
            if best_dist < 30:
                self.movingMarker = best_knot
        
        #does it exist?
        if(self.movingMarker==None):
            return
        
        #is it in the list of knots?
        if not self.knots.__contains__(self.movingMarker):
            return
            
        if not self.movingMarker.isLocked():
            self.mode='MOVING_MARKER'
            
        else:
            self.mode='NONE'
            status="Trying to move an unmovable marker"
            self.positionMessage.emit(status)
        
    def slotMouseMoved(self,event):
        #print "enter slotMouseMoved",self.mode
        
        self.newx=self.invTransform(QwtPlot.xBottom,event.x())
        self.newy=self.invTransform(QwtPlot.yLeft,event.y())
        
        if(self.mode=='NONE'):
            xpos=self.invTransform(QwtPlot.xBottom,event.x())
            temp="x: %.3f" % self.newx+", y: %.3f" %self.newy 
            
            if(len(self.knots)>0):
                temp+="; [ "
                for knot in self.knots[:-1]:
                    temp+=str(knot.getPosition())
                    temp+=", "
                    
                temp+=str(self.knots[-1].getPosition())
                temp+=" ]"
                
                self.positionMessage.emit(temp)
            return
            
        temp=''
        #print self.movingMarker,self.movingMarker.getPosition(),self.movingMarker.getBoundary()
        #marker, dist=self.closestMarker(event.x(),event.y())
        if (self.mode=='MOVING_MARKER'):
            xpos=self.movingMarker.xValue()
        
            diffx=self.newx-self.oldx
            newxpos=xpos+diffx
            
            bounds=self.movingMarker.getBoundary()
            if(newxpos < bounds[0]):
                temp="Moving marker can't move any farther"
                
                #find data point closest to self.newx that is above lowest boundary
                #newxpos=self.findPointAbove(bounds[0])
                newxpos=bounds[0]
                self.oldx=newxpos
                
            elif(newxpos > bounds[1]):
                temp="Moving marker can't move any farther"
                
                #find data point closest to self.newx that is below highest boundary
                newxpos=bounds[1]
                self.oldx=newxpos
                
            else:
                
                self.oldx=self.newx
                temp="Moving marker at %.3f" % newxpos
                
            #newpos=self.getClosest(newxpos)
            self.movingMarker.setPosition(newxpos)
            
            self.fixKnotsBounds()
            
            self.replot()

            self.signalUpdate.emit()
            
            status = temp
            
            self.positionMessage.emit(status)
            
    def slotMouseReleased(self,event):
        self.mode='NONE'
        xpos=self.invTransform(QwtPlot.xBottom,event.x())
        temp="x: %.3f" % self.newx+", y: %.3f" %self.newy 
            
        if(len(self.knots)>0):
            temp+="; [ "
            for knot in self.knots[:-1]:
                #tempnum=knot.getPosition()
                tempnum=calc.getClosest(knot.getPosition(),self.data)
                knot.setPosition(tempnum)
                temp+="%.3f, "%(tempnum,)
                    
            #temp+=str(self.knots[-1].getPosition())
            tempnum=calc.getClosest(self.knots[-1].getPosition(),self.data)
            self.knots[-1].setPosition(tempnum)
            temp+="%.3f ]"%(tempnum,)
                
        self.positionMessage.emit(temp)
        self.signalUpdate.emit()
        self.replot()
        
    def setData(self, data):
        self.data = data

    # The following methods are now obsolete and replaced by direct QwtCurve usage in RawPlot.
    # They are kept for compatibility but do nothing.
    def insertCurve(self, *args, **kwargs):
        raise NotImplementedError("insertCurve is obsolete; use QwtCurve directly.")
    def setCurvePen(self, *args, **kwargs):
        pass
    def setCurveData(self, *args, **kwargs):
        pass
    
    def fixKnotsBounds(self):
        
        if len(self.knots) == 0 or len(self.knots) == 1:
            return
        
        # Get axis bounds using PythonQwt compatible method
        try:
            interval = self.axisInterval(QwtPlot.xBottom)
            axis_min = interval.minValue()
            axis_max = interval.maxValue()
        except Exception:
            try:
                scale_map = self.canvasMap(QwtPlot.xBottom)
                axis_min = scale_map.s1()
                axis_max = scale_map.s2()
            except Exception:
                axis_min = self.axisScaleDiv(QwtPlot.xBottom).lowerBound()
                axis_max = self.axisScaleDiv(QwtPlot.xBottom).upperBound()
        
        max_bound = self.knots[1].xValue() - 0.01
        self.knots[0].setBoundary(axis_min, max_bound)
        
        for i in range(1, len(self.knots) - 1):
            self.knots[i].setBoundary(self.knots[i - 1].xValue() + 0.01,
                                      self.knots[i + 1].xValue() - 0.01)
    
        min_bound = self.knots[-2].xValue() + 0.01
        self.knots[-1].setBoundary(min_bound, axis_max)
        
        for ex in self.excepts:
            bnd = self.knots[ex[0]].getBoundary()
            bnd[ex[1]] = ex[2]
            self.knots[ex[0]].setBoundary(bnd[0], bnd[1])
    
    def getClosest(self,val): #replace by bisecting sort later?
        
        keys=self.curveKeys()
        
        if(len(keys)==0):
            return val
        
        curve=self.curve(keys[0])
        size=curve.dataSize()
        
        xmin=0
        xmax=0
        
        for i in range(size):
            if(curve.x(i) <= val and val <= curve.x(i+1)):
                xmin=curve.x(i)
                xmax=curve.x(i+1)
                
        if(xmin==0 and xmax==0):
            if( val-curve.x(size-1) < val-curve.x(0)):
                return curve.x(size-1)
            else:
                return curve.x(0)
        
        if(val-xmin < xmax-val):
            return xmin
        else:
            return xmax
            
    def findPointAbove(self,pos):
        
        keys=self.curveKeys()
        if(len(keys)==0):
            return pos
            
        curve=self.curve(1)
        
        size=curve.dataSize()
        
        for i in range(size):
        
            if(curve.x(i)>pos):
                return curve.x(i)
                
        return curve.x(size-1)
        
    def findPointBelow(self,pos):
        
        keys=self.curveKeys()
        if(len(keys)==0):
            return pos
        
        curve=self.curve(1)
        
        size=curve.dataSize()
        
        i=size-1
        while(i>=0):
        #for i in range(size).reverse():
        
            if(curve.x(i)<pos):
                return curve.x(i)
            i-=1
        
        return curve.x(0)
    
if(__name__=="__main__"):
    import sys
    from .qt_compat import Qt
    app=QApplication(sys.argv)
    plot=DataPlot(QColor(Qt.red))
    plot.setAxisScale(QwtPlot.xBottom,0,1000)
    plot.addKnot(200)
    plot.addKnot(400)
    plot.addKnot(600)
    app.setMainWidget(plot)
    plot.show()
    app.exec_loop()
    

    
