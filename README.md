# PySpline3

PySpline3 is a graphical, cross-platform program for processing X-ray absorption spectroscopy (XAS) and Extended X-ray absorption fine structure (EXAFS) data. It provides an interactive interface for background subtraction, normalization, spline fitting, and Fourier transformation to analyze atomic structure from X-ray absorption measurements.

This is a Python 3 port of the original PySpline by A. Tenderholt.

## What PySpline3 Does

PySpline3 processes XAS/EXAFS data through a complete analysis pipeline:

1. **Raw Data & Background**: Load energy vs. absorption data and fit polynomial backgrounds
2. **Normalization & Spline**: Remove background and fit splines for edge jump normalization  
3. **K-space Conversion**: Transform to momentum space with windowing functions
4. **Fourier Transform**: Convert to R-space to reveal atomic coordination structure

The program displays four interactive plot windows that update in real-time as you adjust parameters, allowing you to see immediately how changes affect your final results.

## Installation

### Prerequisites

PySpline3 requires Python 3.6+ and the following packages:

```bash
pip install PyQt5 numpy PythonQwt
```

### Install PySpline3

1. Clone or download this repository
2. Navigate to the pyspline3 directory
3. Install dependencies as shown above

## Running PySpline3

From the pyspline3 directory, run:

```bash
python run_pyspline.py
```

This will open the main PySpline3 interface with four plot windows.

## Basic Usage

### Loading Data

**File → Open** or **File → Import Raw Data**

PySpline3 supports several file formats:
- **Legacy .d files**: Complete PySpline files with saved parameters
- **SSRL .001 files**: Multi-column EXAFS Data Collector format 
- **Simple .dat files**: Two-column energy/absorption data

For simple data files, you'll need to specify the absorption edge energy (E0) when prompted.

### Processing Workflow

1. **Adjust Background** (Raw Data window): Drag the vertical markers to set the pre-edge region, adjust polynomial order with spinner
2. **Set Spline Segments** (Normalized Data window): Drag green markers to position spline knots, adjust segment orders  
3. **Window K-space Data** (EXAFS window): Drag markers to set the k-range for Fourier transform
4. **View Results** (Fourier Transform window): See the final R-space coordination structure

### Saving Results

- **File → Save**: Save complete PySpline file with all parameters
- **File → Export FFT**: Export R-space data as text file
- **File → Print**: Generate publication-ready four-panel plot

## File Formats

- **.d files**: Native PySpline format with embedded processing parameters
- **.001 files**: SSRL EXAFS Data Collector multi-column format
- **.dat files**: Simple two-column energy/absorption data
- **.fft files**: Exported Fourier transform results

## Requirements

- Python 3.6+
- PyQt5
- NumPy  
- PythonQwt (for plotting widgets)

## Platform Notes

- **macOS**: Uses `os._exit()` to prevent Qt cleanup segfaults
- **Linux/Windows**: Standard Qt cleanup should work normally
