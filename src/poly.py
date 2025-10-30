#!/usr/bin/env python

# poly.py -- a simple class for evaluation of polynomials
#    needed to solve least squares with constraints
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.


class Polynomial:
    def __init__(self,coeffs):
        self.coeffs=coeffs
        
    def eval(self,x):
    
        sum=0
        for i in range(len(self.coeffs)):
            sum+=self.coeffs[i]*pow(x,i)
            
        return sum
        
