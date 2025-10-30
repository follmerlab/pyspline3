#!/usr/bin/env python
# comments.py -- a class implementing a dialog for adding comments

# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

#generated using Qt Designer

import sys
from .qt_compat import (
    QWidget, QMainWindow, QDialog, QApplication, QPrinter, QPainter, QPixmap, QColor,
    QFontMetrics, QFont, QRect, QFileDialog, QMessageBox, QAction, QToolBar, QMenuBar,
    QMenu, QTextEdit, QPushButton, QSpacerItem, QSizePolicy, QString, SIGNAL, PYSIGNAL,
    qApp, translate, QSize, QGridLayout
)

# Legacy alias: map QMultiLineEdit to QTextEdit for PyQt5 environments
QMultiLineEdit = QTextEdit


class Comments(QDialog):
    def __init__(self, parent=None, name=None, modal=True, fl=0):
        # PyQt5: QDialog(parent, flags)
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(str(name))
        else:
            self.setObjectName("Comments")

        self.setMaximumSize(QSize(460, 240))

        # PyQt5: QGridLayout(parent)
        CommentsLayout = QGridLayout(self)

        self.textEdit1 = QTextEdit(self)
        self.textEdit1.setObjectName("textEdit1")
        # PyQt5: addWidget(widget, row, col, rowSpan, colSpan)
        CommentsLayout.addWidget(self.textEdit1, 0, 0, 1, 3)

        self.cancelButton = QPushButton(self)
        self.cancelButton.setObjectName("cancelButton")
        CommentsLayout.addWidget(self.cancelButton, 1, 2)

        self.okButton = QPushButton(self)
        self.okButton.setObjectName("okButton")
        CommentsLayout.addWidget(self.okButton, 1, 1)
        
        spacer1 = QSpacerItem(251, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        CommentsLayout.addItem(spacer1, 1, 0)

        self.languageChange()

        self.resize(QSize(460, 233).expandedTo(self.minimumSizeHint()))

        # PyQt5: use new-style signals
        try:
            self.okButton.clicked.connect(self.accept)
            self.cancelButton.clicked.connect(self.reject)
        except Exception:
            pass


    def languageChange(self):
        self.setWindowTitle(self.__tr("Edit Comments..."))
        self.cancelButton.setText(self.__tr("&Cancel"))
        self.okButton.setText(self.__tr("&OK"))

    def __tr(self, s, c=None):
        return qApp.translate("Comments", s, c)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    comments = Comments()
    result = comments.exec_()

    if result == QDialog.Rejected:
        print("Rejected!!")
    elif result == QDialog.Accepted:
        text = comments.textEdit1.toPlainText()
        print(text.split("\n"))
