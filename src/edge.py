#!/usr/bin/env python

# edge.py -- the edge  class used for selecting the element, edge, and E0
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

#Generated with the help of Qt designer


from .qt_compat import (
    QWidget, QMainWindow, QDialog, QApplication, QPrinter, QPainter, QPixmap, QColor,
    QFontMetrics, QFont, QRect, QFileDialog, QMessageBox, QAction, QToolBar, QMenuBar,
    QMenu, QTextEdit, QPushButton, QSpacerItem, QSizePolicy, QString, SIGNAL, PYSIGNAL,
    qApp, translate, QSize, QGridLayout, QComboBox, QLineEdit, QLabel, QCheckBox,
    QHBoxLayout
)
import sys

haveFile=True

#check to see if we have it
try:
    file=open("edges.dat")
except IOError:
    haveFile=False
    
if haveFile:
    #skip header
    line=file.readline()
    
    data={}
    #each line contains one element and it's edges:energies
    line=file.readline()
    while(line):
        arr=line.split()
        edges={}
        for edge in arr[1:]:
            info=edge.split(":")
            edges[info[0]]=float(info[1])
        data[arr[0]]=edges
        line=file.readline()
    file.close()
    
else:
    data={
    'Chlorine': {'K':2840.0},
    'Chromium': {'K':6005.0},
    'Cobalt': {'K': 7725.0},
    'Copper': {'K': 9000.0},
    'Iron': {'K': 7130.0},
    'Manganese': {'K': 6555.0},
    'Molybdenum': {'K':20025.0, 'L3':2530.0, 'L2':2640.0},
    'Sulfur': {'K':2490.0},
    'Titanium': {'K': 4985.0},
    'Zinc': {'K': 9680.0}
    }

class EdgeDialog(QDialog):
    def __init__(self, parent=None, name=None, modal=1, fl=0):
        # PyQt5: QDialog(parent, flags)
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(str(name))
        else:
            self.setObjectName("edge")

        self.setMaximumSize(QSize(300, 300))

        # PyQt5: QGridLayout(parent)
        edgeLayout = QGridLayout(self)

        self.elementBox = QComboBox(self)
        self.elementBox.setObjectName("comboBox1")
        edgeLayout.addWidget(self.elementBox, 0, 1)

        self.edgeBox = QComboBox(self)
        self.edgeBox.setObjectName("comboBox2")
        self.edgeBox.setEditable(False)
        # setSizeLimit is not in PyQt5 QComboBox; skip
        edgeLayout.addWidget(self.edgeBox, 1, 1)

        self.lineEdit1 = QLineEdit(self)
        self.lineEdit1.setObjectName("lineEdit1")
        self.lineEdit1.setEnabled(False)
        edgeLayout.addWidget(self.lineEdit1, 2, 1)

        self.eleLabel = QLabel(self)
        self.eleLabel.setObjectName("eleLabel")
        edgeLayout.addWidget(self.eleLabel, 0, 0)

        self.edgeLabel = QLabel(self)
        self.edgeLabel.setObjectName("edgeLabel")
        edgeLayout.addWidget(self.edgeLabel, 1, 0)

        self.energyLabel = QLabel(self)
        self.energyLabel.setObjectName("energyLabel")
        edgeLayout.addWidget(self.energyLabel, 2, 0)

        self.titleLabel = QLabel(self)
        self.titleLabel.setObjectName("titleLabel")
        edgeLayout.addWidget(self.titleLabel, 4, 0)

        self.titleEdit = QLineEdit(self)
        self.titleEdit.setObjectName("titleEdit")
        edgeLayout.addWidget(self.titleEdit, 4, 1)

        self.checkBox1 = QCheckBox(self)
        self.checkBox1.setObjectName("checkBox1")
        edgeLayout.addWidget(self.checkBox1, 3, 1)

        self.okButton = QPushButton(self)
        self.okButton.setObjectName("okbutton")
        self.cancelButton = QPushButton(self)
        self.cancelButton.setObjectName("cancelbutton")

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.okButton)
        hlayout.addWidget(self.cancelButton)

        edgeLayout.addLayout(hlayout, 5, 1)

        self.languageChange()

        self.resize(QSize(300, 283).expandedTo(self.minimumSizeHint()))

        self.initData()

        # PyQt5: use new-style signals
        try:
            self.elementBox.activated[str].connect(self.elementChanged)
            self.edgeBox.activated[str].connect(self.edgeChanged)
            self.checkBox1.toggled.connect(self.slotCheckBoxToggled)
            self.okButton.clicked.connect(self.accept)
            self.cancelButton.clicked.connect(self.reject)
        except Exception:
            # Fallback for compatibility
            pass

    def languageChange(self):
        self.setWindowTitle(self.__tr("Choose Edge..."))
        self.eleLabel.setText(self.__tr("Element:"))
        self.edgeLabel.setText(self.__tr("Edge:"))
        self.energyLabel.setText(self.__tr("Energy:"))
        self.titleLabel.setText(self.__tr("Title:"))
        self.checkBox1.setText(self.__tr("Custom Energy Value"))
        self.okButton.setText(self.__tr("&Ok"))
        self.cancelButton.setText(self.__tr("&Cancel"))

    def initData(self):
        for element in sorted(data.keys()):
            self.elementBox.addItem(element)
        # Initialize with first element
        first_element = sorted(data.keys())[0]
        self.elementChanged(first_element)

    def edgeChanged(self, edge):
        # PyQt5: edge is already a string
        element = str(self.elementBox.currentText())
        edges = data[element]
        text = edges[str(edge)]
        self.lineEdit1.setText(str(text))

    def elementChanged(self, element):
        self.edgeBox.clear()
        # PyQt5: element is already a string
        element_str = str(element)
        edges = data[element_str]
        for edge in sorted(edges.keys()):
            self.edgeBox.addItem(edge)
        # Set first edge
        first_edge = sorted(edges.keys())[0]
        self.edgeChanged(first_edge)

    def slotCheckBoxToggled(self, checked):
        element = str(self.elementBox.currentText())
        self.elementChanged(element)
        if not checked:
            edge = str(self.edgeBox.currentText())
            edges = data[element]
            text = edges[edge]
            self.lineEdit1.setText(str(text))
        self.lineEdit1.setEnabled(checked)

    def getValue(self):
        # PyQt5: text() returns a Python string
        return float(self.lineEdit1.text())

    def getTitle(self):
        # PyQt5: text() returns a Python string
        return str(self.titleEdit.text())
    
    def setTitle(self, title):
        self.titleEdit.setText(str(title))

    def setValue(self, val):
        text = "%.3f" % (val,)
        self.lineEdit1.setText(text)

    def __tr(self, s, c=None):
        return qApp.translate("edge", s, c)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    edit = EdgeDialog()
    edit.show()
    sys.exit(app.exec_())

