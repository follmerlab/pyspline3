#!/usr/bin/env python

# bounds.py -- the bounds algorithm used to calculate the matrix
#    needed to solve least squares with constraints
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from numpy import *
import string

KEV=0.5123143

def getClosestIndex(val, arr):
    """Find index of closest value in array to val.
    Works with both lists and numpy arrays.
    Always returns a Python int, not a numpy scalar."""
    if not arr or len(arr) == 0:
        return 0
    
    # Find closest value by linear search
    if val <= arr[0]:
        return 0
    elif val >= arr[len(arr) - 1]:
        return int(len(arr) - 1)
    
    min_diff = float('inf')
    best_idx = 0
    for i in range(len(arr)):
        diff = abs(arr[i] - val)
        if diff < min_diff:
            min_diff = diff
            best_idx = i
    return int(best_idx)  # Ensure we return Python int, not numpy scalar

def bounds(xdata,ydata,segments,e0):

    if(len(xdata) != len(ydata)):
        print("Xdata and Ydata need same order!")
        return None,None
    
    # Guard against empty data
    if len(xdata) == 0 or len(ydata) == 0:
        print("ERROR: bounds() called with empty xdata or ydata!")
        return None,None

    # Ensure xdata and ydata are accessible by index
    # Convert to list if needed for consistent indexing
    if hasattr(xdata, 'tolist'):
        xdata = xdata.tolist()
    if hasattr(ydata, 'tolist'):
        ydata = ydata.tolist()

    #get total number of a_i
    size=0
    for i in segments:
        size=size+i[0]
        
    seg_size=len(segments)
    
    n=size+2*seg_size-2
    
    matrix = zeros([n, n], float)
    vec = zeros([n], float)
    
    cur_pos=0 #which column do we start in?
    temp=0
    
    for arr in segments:
    
        lindex = getClosestIndex(arr[1], xdata)
        hindex = getClosestIndex(arr[2], xdata)
        
        # Ensure indices are within bounds using explicit comparisons
        # (avoid min/max which get overridden by numpy imports)
        if lindex < 0:
            lindex = 0
        if lindex >= len(xdata):
            lindex = len(xdata) - 1
        if hindex < 0:
            hindex = 0
        if hindex >= len(xdata):
            hindex = len(xdata) - 1
            
        tempx=0
        tempy=0
        for row in range(arr[0]):
        
            tempx=0
            tempy=0
            for col in range(arr[0]):
                tempy=0
                tempx=0
                #sum of powers of x, depending on row and column
                # Use explicit comparison instead of min() to avoid numpy override
                upper_limit = hindex + 1
                if upper_limit > len(xdata):
                    upper_limit = len(xdata)
                for i in range(lindex, upper_limit):
                    #tempx=tempx+pow(xdata[i],row+col)
                    #tempy=tempy+pow(xdata[i],row)*ydata[i]
                    tempx=tempx+pow(xdata[i],row+col)*pow(toKSpace(xdata[i],e0),3)
                    tempy=tempy+pow(xdata[i],row)*ydata[i]*pow(toKSpace(xdata[i],e0),3)
                    
                    
                matrix[cur_pos+row][cur_pos+col]=tempx
                vec[cur_pos+row]=tempy
            
            if(arr==segments[-1] and arr==segments[0]):
                continue #only 1 segment present, so there are no lagrange multiplier conds
                
            #calc lagrange multiplier columns for da_i    
            #l1 and l2 are 0th and 1st deriv conditions for previous segment
            #r1 and r2 are 0th and 1st deriv conds for subsequent segment
            
            if(row==0):
                templ1=0
                tempr1=0
                templ2=-0.5
                tempr2=0.5
            elif(row==1):
                templ1=-0.5
                tempr1=0.5
                templ2=-0.5*pow(xdata[lindex],row)
                tempr2=0.5*pow(xdata[hindex],row)
            else:
                templ1=-0.5*pow(xdata[lindex],row-1)*row
                tempr1=0.5*pow(xdata[hindex],row-1)*row
                templ2=-0.5*pow(xdata[lindex],row)
                tempr2=0.5*pow(xdata[hindex],row)
                
            if(arr==segments[-1]): #no right hand bnd conds on last seg, but need left hand
                matrix[cur_pos+row][cur_pos-2]=templ1 #0th deriv
                matrix[cur_pos+row][cur_pos-1]=templ2 #1st deriv
            elif(arr==segments[0]): #no left hand bnd cond on first seg
                matrix[cur_pos+row][cur_pos+arr[0]]=tempr1
                matrix[cur_pos+row][cur_pos+arr[0]+1]=tempr2
            else: #remaining columns have both left and right hand bnds
                matrix[cur_pos+row][cur_pos+arr[0]]=tempr1
                matrix[cur_pos+row][cur_pos+arr[0]+1]=tempr2
                matrix[cur_pos+row][cur_pos-2]=templ1
                matrix[cur_pos+row][cur_pos-1]=templ2
            
        if(arr==segments[-1] and arr==segments[0]):
                continue #only 1 segment
        
        for cols in range(arr[0]):
        
            if(arr==segments[-1]): #last segment doesn't need bottom (high) bnd conds
                matrix[cur_pos-2][cur_pos+cols]=pow(xdata[lindex],cols) #norm
                matrix[cur_pos-1][cur_pos+cols]=pow(xdata[lindex],cols-1)*cols #deriv
            elif(arr==segments[0]): #first segment doesn't need top (low) bnd conds
                matrix[cur_pos+arr[0]][cur_pos+cols]=-1.0*pow(xdata[hindex],cols)
                matrix[cur_pos+arr[0]+1][cur_pos+cols]=-1.0*pow(xdata[hindex],cols-1)*cols
            else: #middle segments need both top and bottom bnd conds
                matrix[cur_pos+arr[0]][cur_pos+cols]=-1.0*pow(xdata[hindex],cols)
                matrix[cur_pos+arr[0]+1][cur_pos+cols]=-1.0*pow(xdata[hindex],cols-1)*cols
                matrix[cur_pos-2][cur_pos+cols]=pow(xdata[lindex],cols)
                matrix[cur_pos-1][cur_pos+cols]=pow(xdata[lindex],cols-1)*cols
        
        cur_pos=cur_pos+arr[0]+2 #2 for the cond spots
        
    return matrix,vec
    

def toKSpace(x,e0):

    #temp=2.0*H_bar/Me*(x-e0)
    #return sqrt(temp)
    if(x<e0):
        return 0
    else:
        return KEV*sqrt(x-e0)
        

    
