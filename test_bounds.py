#!/usr/bin/env python3

# Test script to debug the bounds issue

import sys
sys.path.insert(0, 'src')

from bounds import getClosestIndex

# Simulate the problem
xdata = list(range(0, 510))  # 510 elements, indices 0-509
print(f"xdata length: {len(xdata)}")
print(f"xdata range: {xdata[0]} to {xdata[-1]}")

# Test getClosestIndex
test_values = [
    0,      # First element
    509,    # Last element  
    250,    # Middle
    510,    # Beyond end
    -1,     # Before start
    7121.942,  # Arbitrary value (will find closest)
]

for val in test_values:
    idx = getClosestIndex(val, xdata)
    print(f"getClosestIndex({val}, xdata) = {idx}")
    if 0 <= idx < len(xdata):
        print(f"  -> xdata[{idx}] = {xdata[idx]}")
    else:
        print(f"  -> INDEX OUT OF RANGE!")
