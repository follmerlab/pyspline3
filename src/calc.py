# calc.py -- functions for calculating background, spline, etc using
#            passed parameters. Each function *should* be fully independent
#            of PySpline and its graphical interface, so a command-line 
#            interface ought to be nearly trivial to implement
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from math import pi, pow
from numpy import array, reshape, arange, conjugate, sqrt as np_sqrt
from .bounds import bounds, toKSpace, KEV, getClosestIndex
from .poly import Polynomial
import numpy.linalg as LinearAlgebra
import numpy.fft as FFT

DR=0.05 #step size of R
FFTPOINTS=512 #number of FFT points; works best if equal to 2^n
    
def getClosest(val, arr):  # replace by bisecting sort later?
    # Robust against empty or None arrays
    if arr is None or len(arr) == 0:
        return val

    xmin = 0
    xmax = 0

    if val <= arr[0]:
        return arr[0]
    elif val >= arr[-1]:
        return arr[-1]
    
    size = len(arr)
    
    for i in range(size - 1):
        if arr[i] <= val and val <= arr[i + 1]:
            xmin = arr[i]
            xmax = arr[i + 1]
            
    if xmin == 0 and xmax == 0:
        if (val - arr[size - 1] < val - arr[0]):
            return arr[size - 1]
        else:
            return arr[0]

    if (val - xmin < xmax - val):
        return xmin
    else:
        return xmax
    
def calcBackground(xdata,ydata,lindex,hindex,order,E0):
    
    yfit=[]
    
    # build matrix used for least-squares
    # only half needs to be built since it's symmetric
    if order > 0:

        # build "empty" matrix so positions can be accessed by row and col
        matrix = array(range(order * order), float)
        matrix = reshape(matrix, (order, order))

        # build "empty" vector so positions can be accessed later
        vector = array(range(order), float)

        for row in range(order):
            for col in range(row, order):
                tempx = 0
                for i in range(lindex, hindex + 1):
                    tempx += pow(xdata[i], row + col)

                matrix[row][col] = tempx
                matrix[col][row] = tempx

            tempy = 0
            for i in range(lindex, hindex + 1):
                tempy += ydata[i] * pow(xdata[i], row)
            vector[row] = tempy

    elif order == 0:  # ie, is for line of form y=a/x+b

        # variables used to build matrix and vector
        pos00 = 0
        pos01 = 0
        pos11 = 0
        y0 = 0
        y1 = 0

        for i in range(lindex, hindex + 1):
            pos00 += 1
            pos01 += (1 / xdata[i])
            pos11 += pow(xdata[i], -2)
            y0 += ydata[i]
            y1 += (ydata[i] / xdata[i])

        matrix = array([[pos00, pos01], [pos01, pos11]])
        vector = array([y0, y1])

    else:
        print("Not implemented yet! Probably won't be either!")
        
    # Modern NumPy uses solve() instead of solve_linear_equations()
    coeffs = LinearAlgebra.solve(matrix, vector)
    
    background = []
    for x in xdata:
    
        tempx=0
        
        if(order>0):
            for i in range(order):
                tempx=tempx+coeffs[i]*pow(x,i)
        elif(order==0): #actually of form y=a/x+b
            tempx=coeffs[0]+coeffs[1]/x
        else:
            "Not implemented"
            
            
        background.append(tempx)

    #if fit is above edge, adjust background
    if (xdata[hindex] > E0):
        value=min(ydata)
        index=ydata.index(value)
        minpoint=0
        
        #average value around min point in case there is noise
        #5 pts: index-2 index-1 index index+1 index+2
        
        #if that min point is too close to the beginning of data, forget lower part
        #else, do the 5pts
        if (index < 2):
            for val in ydata[0:index+3]:
                minpoint += val
            delta = background[index] - minpoint / len(ydata[0:index+3])
            
        else:
            for val in ydata[index-2:index+3]:
                minpoint+=val
            delta=background[index]-minpoint/len(ydata[index-2:index+3])
            
        for i in range(len(background)):
            background[i] = background[i] - delta
            
    return background

def calcSpline(xdata, ydata, E0, segs):
    # Guard against empty or degenerate segments
    if not segs:
        return [0.0] * len(xdata), 1.0
    
    # Check for degenerate segments (lowx == highx causes singular matrix)
    for seg in segs:
        if seg[1] == seg[2]:
            # Return a flat line at mean ydata value
            mean_y = sum(ydata) / max(1, len(ydata))
            return [mean_y] * len(xdata), mean_y
    
    lowx = segs[0][1]
    order = segs[0][0]
    data = []
    
    
    mat,vec=bounds(xdata,ydata,segs,E0)
    
    #handle singular matrices?
    try:
        #soln=scipy.linalg.basic.solve(mat,vec)
        # PyQt5 fix: solve_linear_equations removed, use solve instead
        soln = LinearAlgebra.solve(array(mat), array(vec))
    except LinearAlgebra.LinAlgError:
        print("The spline matrix is singular. Using single line as polynomial estimate")
        
        # Guard against empty data in fallback
        if not xdata or not ydata or len(xdata) == 0 or len(ydata) == 0:
            return [0.0] * max(1, len(xdata)), 1.0
        
        #Get first and last marker position and corresponding indexes of the xdata
        lowx=segs[0][1]
        highx=segs[-1][2]
        lindex=getClosestIndex(lowx, xdata)
        hindex=getClosestIndex(highx, xdata)
        
        #get y-values of the markers
        lowy=ydata[lindex]
        highy=ydata[hindex]
        
        slope=(highy-lowy)/(highx-lowx) if (highx-lowx) != 0 else 0.0
        
        for i in range(len(xdata)):
            dx=xdata[i]-lowx
            dy=slope*dx
            
            data.append(lowy+dy)
        
        # Must return (data, sp_E0) tuple to match normal path
        sp_E0 = lowy + slope * (E0 - lowx) if E0 >= lowx else lowy
        return data, sp_E0
        
    #make polynomials
    polys=[]
    offset=0
    
    for seg in segs:
        order=seg[0]
        
        coeffs=soln[offset:offset+order].tolist()
        
        poly=Polynomial(coeffs)
        polys.append(poly)
        
        offset=offset+order+2
        
    #generate individual spline data for pre-1st segment
    for i in range(0, xdata.index(lowx)): # interate through each point of pre-segment except last
        temp=polys[0].eval(xdata[i])
        data.append(temp)
    
    offset=0
    
    for i in range(len(segs)): # for each of the segments
        lowx=segs[i][1]
        highx=segs[i][2]
        lowindex=xdata.index(lowx)
        highindex=xdata.index(highx)
        
        #iterate through xdata bound by seg ranges
        for j in range(lowindex,highindex): #iterate through each point of segment except last one
        #for i in [0,1]:
            temp=polys[i].eval(xdata[j])
            data.append(temp)
            
        
        
    highx=segs[-1][2]
    order=segs[-1][0]
    
    for i in range(xdata.index(highx),len(xdata)):
        temp=polys[-1].eval(xdata[i])
        data.append(temp)    
        #data.append(1)
     
    sp_E0 = polys[0].eval(E0)
    
    return data,sp_E0
       
def calcXAFS(ydata, splinedata, kdata): # expect only ranges > E0 are given

    data=[]
    if not (len(ydata) == len(splinedata)):
        print("ydata and spline data are not same length")
        print(len(ydata), len(splinedata))
        return data
        
    if not (len(kdata) == len(ydata)):
        print("kdata is different length than ydata,splinedata")
        return data
            
    for i in range(len(ydata)):
        diff = (ydata[i] - splinedata[i])
        data.append(diff * pow(kdata[i], 3))
        
    return data 

def calcFFT(kdata, k3xafsdata, kmin, kmax):
    # Guard against empty data
    if not kdata or not k3xafsdata:
        return [], DR

    #calculate dk
    dk = pi / (FFTPOINTS * DR)
    index = 0
    bindata = []
    weight = []

    #move from righthand point to righthand point in "histogram"
    try:
        max_k = kdata[-1]
    except Exception:
        return [], DR

    for bin in arange(dk, max_k, dk).tolist():
        sum = 0
        last = index
        for k in kdata[index:]:  # only count from last bin
            if k < bin:  # if k falls into bin
                last = kdata.index(k)
                temp = k3xafsdata[last]

                #take into account window
                if (k < kmin or k > kmax):
                    weight = 0
                else:
                    weight = 1
                sum += temp * weight

            else:
                last = kdata.index(k)  # first k that doesn't fall in bin
                break
        # avoid division by zero
        denom = max(1, (last - index + 1))
        bindata.append(sum / denom)
        index = last

    rawfftdata = FFT.fft(bindata, FFTPOINTS)
    conjfftdata = conjugate(rawfftdata)
    # Use numpy.sqrt for element-wise operation on arrays
    fftdata = np_sqrt((rawfftdata * conjfftdata).real)
    fft = fftdata.tolist()
    
    data=[]
    for i in range(len(fft)//2):
        data.append((fft[i] + fft[-i]) * dk * dk / 2.0)
    
    return data,DR
    
def simpleInterpolate(self, x, xdata, ydata):
    
    lindex=0
    hindex=len(xdata)
    
    while (hindex - lindex > 1):
        mindex = (hindex + lindex) // 2
        if(x < xdata[mindex]):
            hindex=mindex
        elif(x > xdata[mindex]):
            lindex=mindex
        
    slope = (ydata[hindex] - ydata[lindex]) / (xdata[hindex] - xdata[lindex])
    
    dx=x-xdata[lindex]
    dy=dx*slope
    
    return ydata[lindex]+dy

def toKSpace(x,e0):

    #temp=2.0*H_bar/Me*(x-e0)
    #return sqrt(temp)
    if(x<e0):
        return 0
    else:
        return KEV*np_sqrt(x-e0)
        
def fromKSpace(k,e0):

    if(k<0):
        return e0
    else:
        return pow(k/KEV,2)+e0
    
