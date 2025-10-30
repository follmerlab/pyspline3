#!/usr/bin/env python3
import sys
import os
from PyQt5 import QtWidgets

# Import from the local minimal_app/src package
from src.pyspline import PySpline


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = PySpline()
    win.show()
    result = app.exec_()
    # On macOS, Qt cleanup can cause benign segfaults during interpreter shutdown.
    # Exit immediately with os._exit to skip Python cleanup and prevent spurious crashes.
    os._exit(result)


if __name__ == "__main__":
    main()
