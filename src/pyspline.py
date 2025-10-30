# main.py -- the main PySpline class used for the program
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

#generated with the help of Qt Designer

#os specific things
import sys
from os.path import exists
from time import localtime,asctime

from .qt_compat import (
    QWidget, QMainWindow, QDialog, QApplication, QPrinter, QPainter, QPixmap, QColor, QFontMetrics, QFont, QRect, QFileDialog, QMessageBox, QAction, QToolBar, QMenuBar, QMenu, QTextEdit, QPushButton, QSpacerItem, QSizePolicy, QString, SIGNAL, PYSIGNAL, qApp, translate,
    QSize, QPen, Qt
)
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStyle, QInputDialog
from .qwt_compat import QwtPlot

# program files (use package-relative imports)
from .rawplot import RawPlot
from .dataplot import DataPlot
from .normplot import NormPlot
from .fftplot import FFTPlot
from .kplot import KPlot
from .i0plot import I0Plot
from .bounds import bounds, toKSpace, KEV
from .edge import EdgeDialog
from .poly import Polynomial
from .aboutbox import AboutBox
from .comments import Comments
from .icons import (image0_data, image1_data, image2_data, image3_data,
                   image4_data, image5_data, image6_data, image7_data,
                   image8_data, image9_data)
from . import calc

#math libraries
from math import sqrt,pi
from numpy import *
import numpy.linalg as LinearAlgebra
import numpy.fft as FFT

import string

KEV=0.5123143 #conversion between eV and k
HC=12398.5471 #conversion between eV and lambda

#Canvas class is for printing
class Canvas(QWidget):
    #def __init__(self,windows,filename,E0,title="",comments="",parent = None, name = None,fl = 0):
    def __init__(self,parent,name=None,fl= 0):
        QWidget.__init__(self,None,name,fl)
        
        self.resize(640,480)
        #self.windows=windows
        
        time=localtime()
        text=asctime(time)
        
        #self.header=QString(title+": "+filename+" -- E0: "+str(E0)+" eV -- "+text)
        #self.footer=comments
        
        self.parent=parent
        
        try:
            self.setBackgroundColor(Qt.white)
        except AttributeError:
            try:
                self.setPaletteBackgroundColor(Qt.white)
            except AttributeError:
                print("Error setting background color to white")
                
        self.show()
        
    def paintEvent(self,e):
        
        painter=QPainter(self)
        self.parent.printPlot(painter)
        painter.end()
        
        return
        width=self.geometry().width()
        height=self.geometry().height()
        
        fm=QFontMetrics(self.font())
        
        fontheight=fm.height()
        fontleading=fm.leading()
        lines=len(self.footer)
        hcomment=lines*fontheight+(lines-1)*fontleading
        
        #get parameters for raw curve
        rorder=self.windows[0].getSpinBoxValue()
        rleft=self.windows[0].plot.knots[0].getPosition()
        rright=self.windows[0].plot.knots[1].getPosition()
        
        #build string for raw
        rstr="Background: %.3f (%i) %3.f"%(rleft,rorder,rright)

        #get parameters for norm curve
        segs=self.windows[1].getSegs()
        nstr="Spline: %.3f (%i) %.3f"%(segs[0][1],segs[0][0]-1,segs[0][2])
        for i in range(1,len(segs)):
            nstr+=" (%i) %.3f"%(segs[i][0]-1,segs[i][2])
            
        #build string for kspace
        kleft=self.windows[2].plot.knots[0].getPosition()
        kright=self.windows[2].plot.knots[1].getPosition()
        kstr="Window: %.3f-%.3f"%(kleft,kright)
        xmargin=width/60
        ymargin=height/60
        xpadding=width/120
        ypadding=height/30
        
        plotwidth=(width-2*xmargin-2*xpadding)/2 #border of 10 on each side
        plotheight=(height-2*ymargin-2*fontheight-5*ypadding-hcomment)/2 #30 for text height and padding      
        
        painter=QPainter(self)
        #paint name and date
        painter.drawText(xmargin,ymargin+fontheight,self.header)
        

#paint raw
        tempcolor=QColor(self.windows[0].plot.canvasBackground())
        self.windows[0].plot.setCanvasBackground(Qt.white)
            
        x=xmargin
        y=ymargin+fontheight+ypadding
        self.windows[0].plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.windows[0].plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight
        painter.drawText(x,y,rstr)
        
#paint norm
        tempcolor=QColor(self.windows[1].plot.canvasBackground())
        self.windows[1].plot.setCanvasBackground(Qt.white)
            
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding
        self.windows[1].plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.windows[1].plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        oldfont=self.font()
        newfont=self.font()
        
        while(fm.width(nstr)>=plotwidth):
            newfont.setPointSize(newfont.pointSize()-1)
            fm=QFontMetrics(newfont)
            
        painter.setFont(newfont)
        
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding+plotheight+fontheight
        painter.drawText(x,y,nstr)
        
        painter.setFont(oldfont)
        
#paint kspace
        tempcolor=QColor(self.windows[2].plot.canvasBackground())
        self.windows[2].plot.setCanvasBackground(Qt.white)
            
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight+ypadding*2
        self.windows[2].plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.windows[2].plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight+2*ypadding+plotheight+fontheight
        painter.drawText(x,y,kstr)
        
#paint rspace

        tempcolor=QColor(self.windows[3].plot.canvasBackground())
        self.windows[3].plot.setCanvasBackground(Qt.white)
            
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding+plotheight+fontheight+ypadding*2
        self.windows[3].plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.windows[3].plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
#paint comments

        yoffset=xmargin+fontheight+ypadding+plotheight+fontheight+ypadding*1.5+plotheight+ypadding+fontheight+ypadding
        
        for line in self.footer:
            painter.drawText(xmargin,yoffset,line)
            yoffset+=(fontheight)
            
        painter.end()
        
        
class PySpline(QMainWindow):
    def __init__(self, parent=None, name=None, fl=0):
        # PyQt5: QMainWindow(parent: QWidget = None, flags: Qt.WindowFlags = Qt.WindowFlags())
        # Ignore 'name' and 'fl' for PyQt5 compatibility
        QMainWindow.__init__(self, parent)
        if name:
            self.setObjectName(str(name))
        self.statusBar()

        # Avoid loading embedded PNGs that produce libpng CRC errors on some systems.
        # We'll use standard Qt icons for actions instead.
        self.image0 = QPixmap()
        self.image1 = QPixmap()
        self.image2 = QPixmap()
        self.image3 = QPixmap()
        self.image4 = QPixmap()
        self.image5 = QPixmap()
        self.image6 = QPixmap()
        self.image7 = QPixmap()
        self.image8 = QPixmap()
        self.image9 = QPixmap()
        if not name:
            self.setObjectName("Form1")

        self.xdata=[]
        self.ydata=[]
        self.i0data=[]
        self.background=[]
        self.filename=""
        self.title=""
        self.comments=[]

        self.raw=RawPlot(self)
        #self.raw.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.raw.resize(500,300)
        self.raw.plot.setAxisScale(QwtPlot.xBottom,0,100)
        self.raw.plot.setAxisTitle(QwtPlot.xBottom, "Energy (eV)")
        
        self.setCentralWidget(self.raw)
        
        self.norm=NormPlot()
        #self.norm.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.norm.resize(600,400)
        self.norm.plot.setAxisScale(QwtPlot.xBottom,0,100)
        self.norm.plot.setAxisTitle(QwtPlot.xBottom, "Energy (eV)")
        self.norm.show()
        
        self.kspace=KPlot()
        self.kspace.resize(600,400)
        self.kspace.plot.setAxisScale(QwtPlot.xBottom,0,100)
        self.kspace.plot.setAxisTitle(QwtPlot.xBottom, "k (1/A)")
        self.kspace.show()
        
        self.fft=FFTPlot()
        self.fft.resize(600,400)
        self.fft.show()
        self.fft.plot.setAxisTitle(QwtPlot.xBottom, "R (A)")
        
        self.i0=I0Plot()
        self.i0.resize(600,400)
        self.i0.plot.setAxisTitle(QwtPlot.xBottom, "Energy (eV)")
        
        try:
            self.raw.plot.positionMessage.connect(self.message)
        except Exception:
            pass

        try:
            # RawPlot now exposes a modern signal when its plot changes
            self.raw.signalPlotChanged.connect(self.updateNormPlot)
        except Exception:
            pass

        try:
            # NormPlot exposes plot_changed
            self.norm.plot_changed.connect(self.updateXAFSPlot)
        except Exception:
            pass

        try:
            # DataPlot exposes signalUpdate
            self.kspace.plot.signalUpdate.connect(self.updateFFTPlot)
        except Exception:
            pass
        
        self.initActions()

    def readArray(self,file):
        arr=[]
        line=file.readline()
        while(line):
            s=line.strip()
            if not s:
                line=file.readline()
                continue
            # Split by comma if present, otherwise whitespace
            if ',' in line:
                tokens=[t.strip() for t in line.strip().split(',') if t.strip()!='']
            else:
                tokens=line.split()
            try:
                sub=[float(t) for t in tokens]
            except ValueError:
                # Skip non-numeric/header lines gracefully
                line=file.readline()
                continue
            arr.append(sub)
            line=file.readline()
        # Return numpy array
        return array(arr)
        
    def fileOpen(self):
    
        self.xdata = []
        self.ydata = []
        self.i0data = []
        self.background = []
        
        fname, _ = QFileDialog.getOpenFileName(self, "Open Data File", "", "Data Files (*.d *.dat *.001);;All Files (*)")
        if not fname:
            return
        
        # Detect file format by examining header
        try:
            with open(fname, 'r') as fh:
                head = ''.join([fh.readline() or '' for _ in range(25)])
            
            # Check for SSRL EXAFS Data Collector format
            if ('SSRL' in head and 'EXAFS Data Collector' in head) or ('Data:' in head and 'Requested Energy' in head):
                self.fileOpenSSRL(fname)
                return
            
            # Check for legacy .d format (has E0, BACKGROUND, SPLINE headers)
            if 'E0' in head and 'BACKGROUND' in head and 'SPLINE' in head:
                self.fileStringOpen(fname)
                return
            
            # Otherwise, it's a simple data file without headers - use Import workflow
            # This handles .dat files with just energy,absorption columns
            self.fileOpenAsImport(fname)
            
        except Exception as e:
            QMessageBox.critical(self, "Open Error", f"Could not read file: {str(e)}")
            return

    def fileOpenSSRL(self, path):
        """Open SSRL EXAFS Data Collector file (.001) and extract energy, I0, and I1.
        Heuristics:
          - Energy: 'Achieved Energy'
          - I0:     'I0'
          - Raw Y:  'I1' (transmission sample)
        E0 is estimated from the maximum derivative of (I1/I0) vs energy.
        """
        energies = []
        i0s = []
        it_s = []
        with open(path, 'r') as f:
            lines = f.readlines()
        # Find the start of numeric data after the 'Data:' section
        start_idx = None
        in_data_names = False
        for idx, line in enumerate(lines):
            if line.strip().startswith('Data:'):
                in_data_names = True
                continue
            if in_data_names:
                # Column names block ends when we encounter a blank line followed by numeric row
                if line.strip() == '':
                    # Next non-empty line should be numeric
                    start_idx = idx + 1
                    break
        if start_idx is None:
            # Fallback: find first line that looks numeric with many columns
            for idx, line in enumerate(lines):
                parts = line.strip().split()
                if len(parts) >= 10:
                    try:
                        _ = [float(p) for p in parts[:10]]
                        start_idx = idx
                        break
                    except Exception:
                        continue
        if start_idx is None:
            QMessageBox.critical(self, "Open Error", "Couldn't locate numeric data block in SSRL file.")
            return
        for line in lines[start_idx:]:
            parts = line.strip().split()
            if len(parts) < 8:
                continue
            try:
                vals = [float(p) for p in parts]
            except Exception:
                continue
            # Indices: 0 RTC, 1 Sum_RTC, 2 Requested, 3 Achieved, 4 I0, 5 I1, 6 I2, 7 I3
            energies.append(vals[3])
            i0s.append(vals[4])
            it_s.append(vals[5])

        if len(energies) < 10:
            QMessageBox.critical(self, "Open Error", "Not enough numeric rows to load SSRL file.")
            return

        xdata = energies
        i0data = i0s
        ydata = it_s

        # Estimate E0 as max derivative point of transmission ratio
        t = array(ydata, float) / (array(i0data, float) + 1e-12)
        x = array(xdata, float)
        # Use central differences via numpy.gradient
        try:
            dt = abs(gradient(t, x))
        except Exception:
            # Fallback: simple finite difference on uniform assumption
            dt = abs(diff(t))
            x = x[:-1]
        idx = int(dt.argmax())
        E0_est = float(x[idx])

        # Prompt user to confirm or adjust E0 estimate
        try:
            val, ok = QInputDialog.getDouble(self, "Set E0", "Estimated E0 (eV):", E0_est, 0.0, 1e9, 3)
            if ok:
                E0_est = float(val)
        except Exception:
            # If dialog is unavailable, continue with estimate
            pass

        self.filename = path
        self.title = QFileInfo(path).baseName()
        self.comments = ["Imported from SSRL .001"]
        self.E0 = E0_est

        self.resetPlots()

        # Choose background window around E0
        lowx = max(min(xdata), E0_est - 200)
        highx = min(max(xdata), E0_est + 200)
        self.setupRawPlot(xdata, ydata, lowx, highx, 2)
        # Norm plot: two segments, starting at E0 to end
        self.setupNormPlot(xdata, [E0_est, xdata[-1]], [2])
        self.i0.setI0Data(xdata, i0data)

        kmax = calc.toKSpace(xdata[-1], self.E0)
        self.setupXAFSPlot(kmax, 0, kmax)
        self.raw.updatePlot()
    def fileStringOpen(self,str):
        
        if str == None:
            return
        
        self.filename=str
        file=open(str)
        
#check to see if it has a title
        line=file.readline()
        if(line[:5]=='TITLE'):
            self.title=line[6:-1]
            line=file.readline()
            
#check to see if line is a comment
        while(line[0]=='#'):
            self.comments.append(line[2:-1])
            line=file.readline()
            
        # read E0: find a line starting with E0 and parse the numeric value
        while line and not line.lstrip().upper().startswith('E0'):
            line = file.readline()
        if not line:
            QMessageBox.critical(self, "Open Error", "No E0 line found in file.")
            file.close()
            return
        parts = line.split()
        e0 = None
        for tok in parts[1:]:
            t = tok.replace('eV','').replace('EV','')
            try:
                e0 = float(t)
                break
            except ValueError:
                continue
        if e0 is None:
            QMessageBox.critical(self, "Open Error", f"Couldn't parse E0 from line: {' '.join(parts)}")
            file.close()
            return
        self.E0 = e0

        # read background bounds and order
        # Expect a line starting with BACKGROUND lowx (order) highx
        line = file.readline()
        while line and not line.lstrip().upper().startswith('BACKGROUND'):
            line = file.readline()
        if not line:
            QMessageBox.critical(self, "Open Error", "No BACKGROUND line found in file.")
            file.close()
            return
        array = line.split()
        try:
            rawlowx = float(array[1])
            rawhighx = float(array[3])
            raworder = int(array[2].strip('()'))
        except Exception:
            QMessageBox.critical(self, "Open Error", f"Couldn't parse BACKGROUND line: {' '.join(array)}")
            file.close()
            return
        
        # read spline info into markers and orders lists
        # Expect a line starting with: SPLINE m0 (o0) m1 (o1) ... mN
        line = file.readline()
        while line and not line.lstrip().upper().startswith('SPLINE'):
            line = file.readline()
        if not line:
            QMessageBox.critical(self, "Open Error", "No SPLINE line found in file.")
            file.close()
            return
        array = line.split()
        markers = []
        orders = []
        for tok in array[1:]:
            if tok.startswith('(') and tok.endswith(')'):
                try:
                    orders.append(int(tok.strip('()')))
                except Exception:
                    pass
            else:
                try:
                    markers.append(float(tok))
                except Exception:
                    pass
        # Ensure we have at least one more marker than orders (segment count)
        if len(markers) != len(orders) + 1:
            # Best-effort: if last token may include unit, try to strip
            if len(markers) > 0 and isinstance(markers[-1], float):
                pass
            else:
                QMessageBox.warning(self, "Open Warning", "Unexpected SPLINE format; results may be incorrect.")
        
        # check to see if k-window is specified; if not, we'll default later
        line = file.readline()
        window = None
        if line:
            array = line.split()
            if array and array[0].upper() == 'KWIN':
                try:
                    window = (float(array[1]), float(array[2]))
                except Exception:
                    window = None
            else:
                # Keep file pointer where it is for data reading
                file.seek(file.tell() - len(line))
       
        
        # file stream is now data, read it (robust to headers and comma/space)
        arrs = self.readArray(file)
        file.close()

        #arrs looks like:
        # [ [col1 col2 col3 col4]
        #   [col1 col2 col3 col4]
        #   ....
        # ]]
        # transpose to get columns in useful format

        data = transpose(arrs)
        xdata = data[0].tolist()
        i0data = data[2].tolist()
        ydata = data[3].tolist()

        self.resetPlots()
        
        rawlowx=calc.getClosest(rawlowx,xdata)
        rawhighx=calc.getClosest(rawhighx,xdata)
        
        self.setupRawPlot(xdata,ydata,rawlowx,rawhighx,raworder)
        self.setupNormPlot(xdata,markers,orders)
        self.i0.setI0Data(xdata,i0data)
        
        kmax = calc.toKSpace(xdata[-1], self.E0)
        if window is None:
            window = (0.0, kmax)
        self.setupXAFSPlot(kmax, window[0], window[1])
        
        self.raw.updatePlot()
#         self.connect(self.raw.plot,PYSIGNAL('positionMessage()'),self.message)
#         self.connect(self.norm.plot,PYSIGNAL('signalChangedPlot'),self.slotUpdateNormPlot)
#         self.connect(self.kspace.plot,PYSIGNAL('signalChangedPlot'),self.slotUpdateKSpacePlot)
    
    def fileImport(self):

        xdata = []
        ydata = []
        i0data = []
        
        filename, _ = QFileDialog.getOpenFileName(self, "Import Data", "", "Data Files (*.dat);;All Files (*)")
        self.filename = filename
        if not self.filename:
            return
            
        file = open(filename)
        
        line = file.readline()
        while line:
            # Handle both comma and whitespace separated values
            if ',' in line:
                array = [x.strip() for x in line.split(',') if x.strip()]
            else:
                array = line.split()
            
            if not array:
                line = file.readline()
                continue
                
            try:
                # Try to parse as floats; skip header/comment lines
                # assume ev k i0 raw (4 columns)
                if len(array) == 4:
                    xdata.append(float(array[0]))
                    i0data.append(float(array[2]))
                    ydata.append(float(array[3]))
                # assume ev absorption (2 columns)
                elif len(array) == 2:
                    xdata.append(float(array[0]))
                    ydata.append(float(array[1]))
                    i0data.append(1.0)
                # assume ev k (also 2 columns, but we treat as ev absorption)
                else:
                    xdata.append(float(array[0]))
                    ydata.append(float(array[1]))
                    i0data.append(1.0)
            except (ValueError, IndexError):
                # Skip lines that can't be parsed as numbers
                pass
                
            line = file.readline()
        
        file.close()
        
        edgeDialog = EdgeDialog()
        result = edgeDialog.exec_()
        
        if result == QDialog.Rejected:
            return
            
        self.E0 = edgeDialog.getValue()
        self.title = edgeDialog.getTitle()
        
        #check to see if E0 is reasonable!!
        while (self.E0 < xdata[0]) or (self.E0 > xdata[-1]):
            errstr = "There appears to be a problem with E0=" + str(self.E0) + ". This value does not fall in the range of your data."
            QMessageBox.critical(self, "Error with E0", errstr)

            result = edgeDialog.exec_()
            
            if result == QDialog.Rejected:
                return
                
            self.E0 = edgeDialog.getValue()
            self.title = edgeDialog.getTitle()
                
        self.resetPlots()
        self.setupRawPlot(xdata,ydata,xdata[0],xdata[-1],2)
        self.setupNormPlot(xdata,[self.E0,xdata[-1]],[2])
        self.i0.setI0Data(xdata,i0data)
        
        kmax=calc.toKSpace(xdata[-1],self.E0)
        self.setupXAFSPlot(kmax,0,kmax)
        
        self.raw.updatePlot()
    
    def fileOpenAsImport(self, filename):
        """Open a simple data file (like .dat) using the Import workflow with EdgeDialog.
        This is called by fileOpen when it detects a file without E0/BACKGROUND/SPLINE headers.
        """
        try:
            xdata = []
            ydata = []
            i0data = []
            
            self.filename = filename
            
            try:
                file = open(filename)
                
                line = file.readline()
                while line:
                    # Handle both comma and whitespace separated values
                    if ',' in line:
                        array = [x.strip() for x in line.split(',') if x.strip()]
                    else:
                        array = line.split()
                    
                    if not array:
                        line = file.readline()
                        continue
                        
                    try:
                        # Try to parse as floats; skip header/comment lines
                        # assume ev k i0 raw (4 columns)
                        if len(array) == 4:
                            xdata.append(float(array[0]))
                            i0data.append(float(array[2]))
                            ydata.append(float(array[3]))
                        # assume ev absorption (2 columns)
                        elif len(array) == 2:
                            xdata.append(float(array[0]))
                            ydata.append(float(array[1]))
                            i0data.append(1.0)
                        # assume ev k (also 2 columns, but we treat as ev absorption)
                        else:
                            xdata.append(float(array[0]))
                            ydata.append(float(array[1]))
                            i0data.append(1.0)
                    except (ValueError, IndexError):
                        # Skip lines that can't be parsed as numbers
                        pass
                        
                    line = file.readline()
                
                file.close()
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Could not read file: {str(e)}")
                return
            
            if not xdata:
                QMessageBox.critical(self, "Import Error", "No valid data found in file.")
                return
            
            # Show EdgeDialog for E0 selection
            edgeDialog = EdgeDialog()
            result = edgeDialog.exec_()
            
            if result == QDialog.Rejected:
                return
                
            self.E0 = edgeDialog.getValue()
            self.title = edgeDialog.getTitle()
            
            # Check to see if E0 is reasonable
            while (self.E0 < xdata[0]) or (self.E0 > xdata[-1]):
                errstr = "There appears to be a problem with E0=" + str(self.E0) + ". This value does not fall in the range of your data."
                QMessageBox.critical(self, "Error with E0", errstr)

                result = edgeDialog.exec_()
                
                if result == QDialog.Rejected:
                    return
                    
                self.E0 = edgeDialog.getValue()
                self.title = edgeDialog.getTitle()
                    
            self.resetPlots()
            self.setupRawPlot(xdata, ydata, xdata[0], xdata[-1], 2)
            self.setupNormPlot(xdata, [self.E0, xdata[-1]], [2])
            self.i0.setI0Data(xdata, i0data)
            
            kmax = calc.toKSpace(xdata[-1], self.E0)
            self.setupXAFSPlot(kmax, 0, kmax)
            
            self.raw.updatePlot()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Setup Error", f"Error during file open: {type(e).__name__}: {str(e)}")
            return
    
    def resetPlots(self):
        #in the event that we are opening a file when one is open,
        #makers and curves need to be cleared
        
        self.raw.plot.resetPlot()
        self.norm.plot.resetPlot()
        self.kspace.plot.resetPlot()
        self.fft.plot.resetPlot()
        
    def setupRawPlot(self,xdata,ydata,lowx,highx,order):
        
        self.raw.setRawData(xdata,ydata,self.E0)
        self.raw.plot.addKnot(lowx)
        self.raw.plot.addKnot(highx)
        self.raw.spinBox.setValue(order)
       
    def setupNormPlot(self, xdata, markers, orders):

        # Set E0 first so updateKnots doesn't crash with None
        self.norm.setE0(self.E0)
        
        # Set flag to prevent knot redistribution during file loading
        self.norm._loading_from_file = True
        
        # make sure scale of plot is reasonable
        self.norm.plot.setAxisScale(QwtPlot.xBottom, xdata[0], xdata[-1])
        
        # adjust markers to closest data positions
        for i in range(len(markers)):
            temp = calc.getClosest(markers[i], xdata)
            self.norm.plot.addKnot(temp)
            
        # Allow first knot to move down to E0-50 instead of exactly E0
        # This gives more flexibility while still keeping it near the edge
        lower_bound = xdata[0] if xdata[0] > self.E0 - 50 else self.E0 - 50
        self.norm.plot.addBoundsExceptions(0, 0, lower_bound)
        
        # set number of knots in normplot window (this creates order spinboxes)
        self.norm.setNumKnots(len(markers))
        self.norm.setOrders(orders)
        
        # Clear the flag
        self.norm._loading_from_file = False
        
        # NOTE: Don't call norm.updatePlot() here - the data hasn't been set yet!
        # The data will be set when raw.updatePlot() runs and triggers updateNormPlot()
       
    def setupXAFSPlot(self,max,pos1,pos2):
        
        self.kspace.plot.setAxisScale(QwtPlot.xBottom,0,max)

        self.kspace.plot.addKnot(pos1)
        self.kspace.plot.addKnot(pos2)
        
        self.kspace.plot.replot()
        
    def setupI0Curve(self):

        #in the event that we are opening a file when one is open,
        #makers and curves need to be cleared

        self.i0.plot.removeCurves()
        
        self.i0plot=self.i0.plot.insertCurve("I0")
        self.i0.plot.setCurvePen(self.i0plot,QPen(QColor(Qt.black),2))
        self.i0.plot.setAxisScale(QwtPlot.xBottom,self.xdata[0],self.xdata[-1])
        self.i0.plot.setAxisScale(QwtPlot.yLeft,min(self.i0data),max(self.i0data))
        self.i0.plot.setCurveData(self.i0plot,self.xdata,self.i0data)


        
    def fileSave(self):
        # Guard: ensure we have a valid filename before trying to save
        if not hasattr(self, 'filename') or not self.filename:
            self.fileSaveAs()
            return
        try:
            self.save(self.filename)
        except AttributeError:
            self.fileSaveAs()
            
    def fileSaveAs(self):
        qstr, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Data Files (*.d);;All Files (*)")
        if not qstr:
            return
        if exists(qstr):
            reply = QMessageBox.question(self, "File Exists", f"The file named {qstr} exists. Do you want to overwrite this file?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
        self.filename=qstr
        self.save(self.filename)

    def exportFourier(self):
        
        qstr, _ = QFileDialog.getSaveFileName(self, "Export Fourier Transform", "", "FFT Files (*.fft);;All Files (*)")
        if not qstr:
            return
        if exists(qstr):
            reply = QMessageBox.question(self, "File Exists", f"The file named {qstr} exists. Do you want to overwrite this file?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
        file=open(qstr, "w")
        file.write("R FFT\n")

        rdata=self.fft.rdata
        fftdata=self.fft.fftdata
        
        for i in range(len(rdata)):
            file.write("%7.3f %7.3f\n"%(rdata[i],fftdata[i]))
        file.close()
               
    def save(self,string):
        file=open(string,"w")

        #write title and comments
        file.write("TITLE "+self.title+"\n")
        for line in self.comments:
            file.write("# "+line+"\n")
            
        #write E0
        file.write("E0 %.3f\n" % self.E0)

        #get background marker information
        markers=self.raw.plot.knots
        lowx=markers[0].getPosition()
        highx=markers[1].getPosition()
        order=self.raw.getSpinBoxValue()
        
        #write background info
        #file.write("BACKGROUND "+str(lowx)+" ("+str(order)+") "+str(highx)+" eV\n")
        file.write("BACKGROUND %.5f (%i) %.5f eV\n" % (lowx,order,highx))

        #write spline segs info
        file.write("SPLINE ")
        segs=self.norm.getSegs()
        for seg in segs:
            file.write("%.5f" % seg[1]) #lower bound
            file.write(" ("+str(seg[0]-1)+") ") #order
        file.write("%.5f eV\n" % segs[-1][2]) #higher bound of last segment

        #write windowing info
        knots=self.kspace.plot.knots
        min=knots[0].getPosition()
        max=knots[1].getPosition()
        
        file.write("KWIN %.5f %.5f \n" % (min,max))
        
        #header string
        file.write("EV K IO RAW BACKGROND NORMAL SPLINE XAFS\n")

        #actual data, pad kdata and xafsdata with zeros
        xdata=self.raw.xdata
        i0data=self.i0.ydata
        ydata=self.raw.ydata
        background=self.raw.background
        normdata=self.norm.normdata
        splinedata=self.norm.splinedata
        xafsdata=self.kspace.xafsdata
        tempk=self.kspace.kdata
        
        datasize = len(xdata)
        kdata = zeros((datasize), float)
        kdata[-len(tempk):] = tempk
        xafs = zeros((datasize), float)
        xafs[-len(xafsdata):] = xafsdata

        data=[xdata,kdata,i0data,ydata,background,
                    normdata,splinedata,xafs]
        data2=array(data)
        datat=transpose(data2).tolist()

        for row in datat:
            for i in range(len(row)):
                file.write("%.6f" % row[i])
                if (i == len(row) - 1):
                    file.write("\n")
                else:
                    file.write(",")
        
        file.close()
        
    def filePrint(self):

        #keys=[self.raw,self.norm,self.kspace,self.fft]   
        #self.canvas=Canvas(keys,self.filename,self.E0,self.title,self.comments)
        #self.canvas=Canvas(self)
        
        printer=QPrinter()
        printer.setOrientation(QPrinter.Landscape)
        printer.setPageSize(QPrinter.Letter)
        printer.setColorMode(QPrinter.Color)
        printer.setOutputToFile(True)
        
        fileinfo=QFileInfo(self.filename)
        name=str(fileinfo.baseName())+'.ps'
        
        try:
            printer.setOutputFileName(name)
        except Exception:
            pass
        try:
            printer.setResolution(300)
        except Exception:
            pass
        painter=QPainter(printer)
        self.printPlot(painter)
        painter.end()
        
    def printPlot(self, painter):
        device = painter.device()
        width = device.width()
        height = device.height()
        fm = QFontMetrics(painter.font())
        scale = float(device.logicalDpiY() / self.logicalDpiY())
        scalex = float(device.logicalDpiX() / self.logicalDpiX())
        fontheight = fm.height() * scale
        fontleading = fm.leading() * scale
        lines = len(self.comments)
        hcomment = lines * fontheight + (lines - 1) * fontleading

        #build raw string
        time = localtime()
        text = asctime(time)
        header = self.title + ": " + self.filename + " -- E0: " + str(self.E0) + " eV -- " + text

        #get parameters for raw curve
        rorder = self.raw.getSpinBoxValue()
        rleft = self.raw.plot.knots[0].getPosition()
        rright = self.raw.plot.knots[1].getPosition()

        #build string for raw
        rstr = "Background: %.3f (%i) %3.f" % (rleft, rorder, rright)

        #get parameters for norm curve
        segs = self.norm.getSegs()
        nstr = "Spline: %.3f (%i) %.3f" % (segs[0][1], segs[0][0] - 1, segs[0][2])
        for i in range(1, len(segs)):
            nstr += " (%i) %.3f" % (segs[i][0] - 1, segs[i][2])

        #build string for kspace
        kleft = self.kspace.plot.knots[0].getPosition()
        kright = self.kspace.plot.knots[1].getPosition()
        kstr = "Window: %.3f-%.3f" % (kleft, kright)
        xmargin = width / (10 * scalex)
        ymargin = height / (20 * scale)
        xpadding = width / (20 * scalex)
        ypadding = height / (20 * scale)
        plotwidth = (width - 2 * xmargin - 2 * xpadding) / 2
        plotheight = (height - 2 * ymargin - 2 * fontheight - 5 * ypadding - hcomment) / 2
        
        # paint name and date
        painter.drawText(xmargin, ymargin, header)
        

#paint raw
        tempcolor=QColor(self.raw.plot.canvasBackground())
        self.raw.plot.setCanvasBackground(Qt.white)
            
        x=xmargin
        y=ymargin+fontheight+ypadding
        self.raw.plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.raw.plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight
        painter.drawText(x,y,rstr)
        
#paint norm
        tempcolor=QColor(self.norm.plot.canvasBackground())
        self.norm.plot.setCanvasBackground(Qt.white)
            
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding
        self.norm.plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.norm.plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        oldsize = painter.font().pointSize()
        print(painter.font().pointSize(), painter.font().pixelSize())
        newsize = oldsize
        family=painter.font().family()
        
        fm=QFontMetrics(painter.font())
        while(fm.width(nstr)>=plotwidth/(scalex*1.3)):
            
            newfont=QFont(family,newsize-1)
            fm=QFontMetrics(newfont)
            newsize-=1
            
            
        print(fm.width(nstr), plotwidth / scalex)

        painter.setFont(QFont(family, newsize))
        
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding+plotheight+fontheight
        painter.drawText(x,y,nstr)
        
        painter.setFont(QFont(family,oldsize))
        
#paint kspace
        tempcolor=QColor(self.kspace.plot.canvasBackground())
        self.kspace.plot.setCanvasBackground(Qt.white)
            
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight+ypadding*2
        self.kspace.plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.kspace.plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight+2*ypadding+plotheight+fontheight
        painter.drawText(x,y,kstr)
        
#paint rspace

        tempcolor=QColor(self.fft.plot.canvasBackground())
        self.fft.plot.setCanvasBackground(Qt.white)
            
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding+plotheight+fontheight+ypadding*2
        self.fft.plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.fft.plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
#paint comments

        yoffset=xmargin+fontheight+ypadding+plotheight+fontheight+ypadding*1.5+plotheight+ypadding+fontheight+ypadding
        
        for line in self.comments:
            painter.drawText(xmargin,yoffset,line)
            yoffset+=(fontheight+fontleading)
        
    def editParameters(self):
        edgeDialog = EdgeDialog()
        edgeDialog.slotCheckBoxToggled(True)
        edgeDialog.checkBox1.setChecked(True)
        edgeDialog.setTitle(self.title)
        edgeDialog.setValue(self.E0)
        
        result = edgeDialog.exec_()
        
        if result == QDialog.Rejected:
            return
            
        self.E0 = edgeDialog.getValue()
        self.title = edgeDialog.getTitle()
        
        xdata = self.raw.xdata
        
        #check to see if E0 is reasonable!!
        while (self.E0 < xdata[0]) or (self.E0 > xdata[-1]):
            errstr = "There appears to be a problem with E0=" + str(self.E0) + ". This value does not fall in the range of your data."
            QMessageBox.critical(self, "Error with E0", errstr)

            result = edgeDialog.exec_()
            if result == QDialog.Rejected:
                return
                
        self.E0 = edgeDialog.getValue()
        self.title = edgeDialog.getTitle()
        self.norm.plot.addBoundsExceptions(0, 0, self.E0)
        pos = calc.getClosest(self.E0, xdata)
        self.norm.plot.knots[0].setPosition(pos)
        
        kmax = calc.toKSpace(xdata[-1], self.E0)
        kmin = calc.toKSpace(pos, self.E0)
        self.kspace.plot.resetPlot()
        
        self.setupXAFSPlot(kmax, kmin, kmax)
        
        self.updateNormPlot()
            
    def editComments(self):
        com = Comments()
        
        comment_str = ""
        for comment in self.comments:
            comment_str += comment
            comment_str += "\n"
        
        com.textEdit1.setText(comment_str)
        result = com.exec_()
        
        if result == QDialog.Rejected:
            return
            
        # PyQt5: use toPlainText
        text = com.textEdit1.toPlainText()
        self.comments = []
        for line in text.splitlines():
            self.comments.append(line)
        
    def fileExit(self):
        self.close()

##    def helpIndex(self):
##        print "Form1.helpIndex(): Not implemented yet"
##
##    def helpContents(self):
##        print "Form1.helpContents(): Not implemented yet"

    def helpAbout(self):
        self.box=AboutBox()
        self.box.show()
        
    def updateNormPlot(self):
        # Guard: ensure raw plot has computed background first
        ydata = getattr(self.raw, 'ydata', [])
        xdata = getattr(self.raw, 'xdata', [])
        background = getattr(self.raw, 'background', [])
        
        if not ydata or not xdata or not background:
            return
        if len(ydata) != len(background):
            return
            
        tempnorm = []
        for i in range(len(ydata)):
            tempnorm.append(ydata[i] - background[i])
            
        self.norm.setNormData(xdata, tempnorm, self.E0)
        self.norm.updatePlot()
    def updateXAFSPlot(self):
        # Ensure we have at least two knots on the norm plot
        normknots = getattr(self.norm.plot, 'knots', [])
        if len(normknots) < 2:
            return

        self.kspace.clearFixedKnots()

        # Add fixed vertical markers at the same positions in k-space
        for knot in normknots:
            pos = knot.getPosition()
            kpos = calc.toKSpace(pos, self.E0)
            try:
                self.kspace.addFixedKnot(kpos)
            except Exception:
                pass

        xdata = list(getattr(self.raw, 'xdata', []))
        normdata = getattr(self.norm, 'normdata', [])
        splinedata = getattr(self.norm, 'splinedata', [])

        if not xdata or not normdata or not splinedata:
            return

        # generate kdata
        kdata = [calc.toKSpace(x, self.E0) for x in xdata]

        # find index of first x >= E0 safely
        k0index = 0
        while k0index < len(xdata) and xdata[k0index] < self.E0:
            k0index += 1
        if k0index >= len(xdata):
            # E0 is beyond data range
            return

        xafsdata = calc.calcXAFS(normdata[k0index:], splinedata[k0index:], kdata[k0index:])
        if not xafsdata:
            return

        self.kspace.setXAFSData(kdata[k0index:], xafsdata)

        # Trigger FFT update only when K-space data is ready
        try:
            self.updateFFTPlot()
        except Exception:
            pass
        
    def updateFFTPlot(self):
        
        knots=self.kspace.plot.knots
        kmin=knots[0].getPosition()
        kmax=knots[1].getPosition()
        
        kdata=self.kspace.kdata
        xafsdata=self.kspace.xafsdata
        
        fftdata,DR=calc.calcFFT(kdata,xafsdata,kmin,kmax)
        
        rdata=[]
        for i in range(len(fftdata)):
            rdata.append(i*DR)
            
        self.fft.setFFTData(rdata,fftdata)
#         dmax=max(self.fftdata)
#         self.fft.plot.setAxisScale(QwtPlot.yLeft,0,dmax)
        
        
#     def slotUpdateKSpacePlot(self):
#         
#         index=self.k0index
#         self.xafsdata=calc.calcXAFS(self.normdata[index:],self.splinedata[index:],self.kdata)
#         
#         self.kspace.plot.setCurveData(self.xafscurve,self.kdata,self.xafsdata)
#         
#         self.kspace.plot.replot()
#         
#         self.slotUpdateFFTPlot()
        
#     def slotUpdateFFTPlot(self):
#     
#         knots=self.kspace.plot.knots
#         kmin=knots[0].getPosition()
#         kmax=knots[1].getPosition()
#         self.fftdata,DR=calc.calcFFT(self.kdata,self.xafsdata,kmin,kmax)
#         
#         self.rdata=[]
#         for i in range(len(self.fftdata)):
#             self.rdata.append(i*DR)
#             
#         self.fft.plot.setCurveData(self.fftcurve,self.rdata,self.fftdata)
#         dmax=max(self.fftdata)
#         self.fft.plot.setAxisScale(QwtPlot.yLeft,0,dmax)
#         
#         self.fft.plot.replot()
        
#     def slotNumKnotsChanged(self,value):
#     
#         #number of knots equals numbers of segments
#         
#         xpos=self.norm.plot.knots[-1].xValue()
#         if(value==len(self.norm.plot.knots)+1):
#             newpos=calc.getClosest(self.xdata,xpos+100)
#             
#             #before adding knot in norm window, add it to kspace window
#             kpos=toKSpace(newpos,self.E0)
#             marker=self.kspace.plot.insertMarker()
#             self.kspace.plot.setMarkerPen(marker,QPen(QColor(Qt.darkGreen),2))
#             self.kspace.plot.setMarkerLineStyle(marker,QwtMarker.VLine)
#             self.kspace.plot.setMarkerPos(marker,kpos,1.0)
#             self.kmarkers.append(marker)
#             
#             self.norm.plot.addKnot(newpos)
# 
#             
#         elif(value==len(self.norm.plot.knots)-1):
#                 
#             self.norm.plot.removeKnot()
#             marker=self.kmarkers.pop()
#             self.kspace.plot.removeMarker(marker)
#           
#         #hope this still works!! -- should only  happen on first opening a file  
#         #else:
#             #print "something wrong in slotNumKnotsChanged()"
        
    
#     def calcKSpace(self,xarr):
#         kdata=[]
#         
#         for x in xarr:
#             if(x<self.E0):
#                 last=x
#                 continue
#             
#             
#             temp=toKSpace(x,self.E0)
#             kdata.append(temp)
# 
#             #E0 should be in the xrange
#             index=xarr.index(last)
#             
#                 
#         return kdata,index
#     
#     def getClosest(self,val,arr): #replace by bisecting sort later?
#         xmin=0
#         xmax=0
#         
#         for i in range(len(arr)-1):
#             if(arr[i]<= val and val <= arr[i+1]):
#                 xmin=arr[i]
#                 xmax=arr[i+1]
#                 
#         if(xmin==0 and xmax==0):
#             #print "Didn't find",val,"in array"
#             if( arr[-1]-val < val-arr[0]):
#                 return arr[-1]
#             else:
#                 return arr[0]
#         
#         if(val-xmin < xmax-val):
#             return xmin
#         else:
#             return xmax

        
#     def setupKCurve(self,min,max):
# 
#         #convert xdata to kdata and set scale
#         self.kdata,self.k0index=self.calcKSpace(self.xdata)
#         self.k0index=self.k0index+1
#         
#         #get/set kmarkers based on markers and store in list
#         self.kmarkers=[]
# 
#         for knot in self.norm.plot.knots:
#             pos=knot.getPosition()
#             k0=toKSpace(pos,self.E0)
#             kmarker=self.kspace.plot.insertMarker()
#             self.kspace.plot.setMarkerPen(kmarker,QPen(QColor(Qt.darkGreen),2))
#             self.kspace.plot.setMarkerPos(kmarker,k0,1.0)
#             self.kspace.plot.setMarkerLineStyle(kmarker,QwtMarker.VLine)
#             self.kmarkers.append(kmarker)
#         
#         self.kspace.plot.setAxisScale(QwtPlot.xBottom,0,self.kdata[-1])
#         
#         #insert windowing knots
#         self.kspace.plot.addKnot(min)
#         self.kspace.plot.addKnot(max)
        
#     def setupFFTCurve(self):
# 
#         #all setup should be done, but scale axis
#         self.fft.plot.setAxisScale(QwtPlot.xBottom,0,5)

#     def calcVictoreen(self,kdata,C,D,e0):
#         data=[]
#         
#         for k in kdata:
#             ev=fromKSpace(k,e0)
#             Lambda=HC/ev
#             temp=C*pow(Lambda,3)-D*pow(Lambda,4)
#             data.append(temp)
#             
#         return data
    
    def message(self,string):
            try:
                self.statusBar().showMessage(string)
            except Exception:
                # Fallback for older API
                try:
                    self.statusBar().message(string)
                except Exception:
                    pass
            
    def __tr(self,s,c = None):
        return qApp.translate("Form1",s,c)
        
    def initActions(self):
        self.fileImportAction = QAction("Import", self)
        self.fileOpenAction = QAction("Open", self)
        # Use standard Qt icons to avoid PNG decoding issues (with fallbacks across Qt versions)
        try:
            self.fileOpenAction.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        except Exception:
            try:
                self.fileOpenAction.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
            except Exception:
                pass
        self.fileSaveAction = QAction("Save", self)
        try:
            self.fileSaveAction.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        except Exception:
            try:
                self.fileSaveAction.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
            except Exception:
                pass
        self.fileSaveAsAction = QAction("Save As", self)
        self.fileExportFFTAction = QAction("Export FFT", self)
        self.filePrintAction = QAction("Print", self)
        try:
            # Not all Qt versions have SP_DialogPrintButton; use a generic file icon instead
            self.filePrintAction.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        except Exception:
            pass
        self.fileExitAction = QAction("Exit", self)
        self.editParametersAction = QAction("Parameters", self)
        self.editCommentsAction = QAction("Comments", self)
        self.windowNormAction = QAction("Normalized Data", self)
        # Use modern checkable API
        self.windowNormAction.setCheckable(True)
        self.windowNormAction.setChecked(True)
        self.windowXAFSAction = QAction("XAFS", self)
        self.windowXAFSAction.setCheckable(True)
        self.windowXAFSAction.setChecked(True)
        self.windowFFTAction = QAction("FFT", self)
        self.windowFFTAction.setCheckable(True)
        self.windowFFTAction.setChecked(True)
        self.windowI0Action = QAction("I0", self)
        self.windowI0Action.setCheckable(True)
        self.windowI0Action.setChecked(False)
        # self.helpContentsAction = QAction("Contents", self)
        # self.helpIndexAction = QAction("Index", self)
        self.helpAboutAction = QAction("About", self)

        # Build toolbar and menus with modern QMainWindow APIs
        self.toolBar = QToolBar("", self)
        self.addToolBar(self.toolBar)
        self.toolBar.addAction(self.fileOpenAction)
        self.toolBar.addAction(self.fileSaveAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.filePrintAction)

        # Use the native menu bar
        self.MenuBar = self.menuBar()

        self.fileMenu = self.MenuBar.addMenu("File")
        self.fileMenu.addAction(self.fileImportAction)
        self.fileMenu.addAction(self.fileOpenAction)
        self.fileMenu.addAction(self.fileSaveAction)
        self.fileMenu.addAction(self.fileSaveAsAction)
        self.fileMenu.addAction(self.fileExportFFTAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.filePrintAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.fileExitAction)

        self.editMenu = self.MenuBar.addMenu("Edit")
        self.editMenu.addAction(self.editParametersAction)
        self.editMenu.addAction(self.editCommentsAction)

        self.windowMenu = self.MenuBar.addMenu("Windows")
        self.windowMenu.addAction(self.windowNormAction)
        self.windowMenu.addAction(self.windowXAFSAction)
        self.windowMenu.addAction(self.windowFFTAction)
        self.windowMenu.addAction(self.windowI0Action)

        self.helpMenu = self.MenuBar.addMenu("Help")
        self.helpMenu.addAction(self.helpAboutAction)

        self.languageChange()

        self.resize(QSize(644,630).expandedTo(self.minimumSizeHint()))
        #self.clearWState(Qt.WState_Polished)

        # Wire actions using new-style signals
        try:
            self.fileOpenAction.triggered.connect(self.fileOpen)
            self.fileImportAction.triggered.connect(self.fileImport)
            self.fileSaveAction.triggered.connect(self.fileSave)
            self.fileSaveAsAction.triggered.connect(self.fileSaveAs)
            self.fileExportFFTAction.triggered.connect(self.exportFourier)
            self.filePrintAction.triggered.connect(self.filePrint)
            self.fileExitAction.triggered.connect(self.fileExit)

            self.editParametersAction.triggered.connect(self.editParameters)
            self.editCommentsAction.triggered.connect(self.editComments)

            self.windowNormAction.toggled.connect(self.norm.setShown)
            if hasattr(self.norm, 'closed'):
                self.norm.closed.connect(self.slotWindowNormActionToggled)

            self.windowXAFSAction.toggled.connect(self.kspace.setShown)
            if hasattr(self.kspace, 'closed'):
                self.kspace.closed.connect(self.slotWindowXAFSActionToggled)

            self.windowFFTAction.toggled.connect(self.fft.setShown)
            if hasattr(self.fft, 'closed'):
                self.fft.closed.connect(self.slotWindowFFTActionToggled)

            self.windowI0Action.toggled.connect(self.i0.setShown)
            if hasattr(self.i0, 'closed'):
                self.i0.closed.connect(self.slotWindowI0ActionToggled)

            self.helpAboutAction.triggered.connect(self.helpAbout)
        except Exception:
            # If any objects do not support the modern signals yet, continue
            pass


    def closeEvent(self,e):
        self.norm.close()
        self.kspace.close()
        self.fft.close()
        e.accept()
        
    def slotWindowNormActionToggled(self):
        self.windowNormAction.setChecked(False)
            
    def slotWindowXAFSActionToggled(self):
        self.windowXAFSAction.setChecked(False)
            
    def slotWindowFFTActionToggled(self):
        self.windowFFTAction.setChecked(False)
            
    def slotWindowI0ActionToggled(self):
        self.windowI0Action.setChecked(False)
            
    def languageChange(self):
        self.setWindowTitle(self.__tr("Raw Data"))
        
        self.fileImportAction.setText(self.__tr("&Import Raw Data..."))
        
        self.fileOpenAction.setText(self.__tr("&Open..."))
        #self.fileOpenAction.setAccel(self.__tr("Ctrl+O"))
        
        self.fileSaveAction.setText(self.__tr("&Save"))
        #self.fileSaveAction.setAccel(self.__tr("Ctrl+S"))
        
        self.fileSaveAsAction.setText(self.__tr("Save &As..."))
        
        self.fileExportFFTAction.setText(self.__tr("Export Fourier Transform..."))
        
        self.filePrintAction.setText(self.__tr("&Print..."))
        #self.filePrintAction.setAccel(self.__tr("Ctrl+P"))
        
        self.fileExitAction.setText(self.__tr("E&xit"))
        
        self.editParametersAction.setText(self.__tr("Parameters..."))
        self.editCommentsAction.setText(self.__tr("Comments..."))
        
        self.windowNormAction.setText(self.__tr("&Normalized Data"))
        self.windowXAFSAction.setText(self.__tr("&EXAFS"))
        self.windowFFTAction.setText(self.__tr("&Fourier Transform"))
        self.windowI0Action.setText(self.__tr("I0 Data"))
        
        self.helpAboutAction.setText(self.__tr("&About"))
        
        self.toolBar.setWindowTitle(self.__tr("Tools"))
        
 
# def toKSpace(x,e0):
# 
#     #temp=2.0*H_bar/Me*(x-e0)
#     #return sqrt(temp)
#     if(x<e0):
#         return 0
#     else:
#         return KEV*sqrt(x-e0)
#         
# def fromKSpace(k,e0):
# 
#     if(k<0):
#         return e0
#     else:
#         return pow(k/KEV,2)+e0
    
def gauss(x,mean,stdev):
    
    norm=1/(stdev*sqrt(2*pi))
    temp=-1*pow(x-mean,2)/(2*stdev*stdev)
    return norm*exp(temp)
    
