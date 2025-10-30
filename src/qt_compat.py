"""Qt compatibility shim for PyQt5.

This module provides a small compatibility layer that exposes the most
commonly-used names from the old `qt` wrapper used by the original
PySpline code. It tries to import PyQt5 and map names; where exact
behaviour differs, this shim provides best-effort aliases so the
package can import under Python 3 + PyQt5 and then be further adapted
functionally.

This is intentionally conservative: it exposes class and function names
expected by the code (QWidget, QMainWindow, QPainter, QString, SIGNAL,
PYSIGNAL, etc.). It does not fully emulate deprecated behaviour such as
old-style SIGNAL/SLOT semantics — those should be migrated to new-style
PyQt5 signals for correct runtime behaviour.
"""
from __future__ import annotations

QT_BINDING = None
try:
    # Prefer PyQt5
    from PyQt5 import QtCore, QtGui, QtWidgets
    QT_BINDING = 'PyQt5'
except Exception:
    try:
        # Try PyQt4 (older systems)
        from PyQt4 import QtCore, QtGui
        # PyQt4 doesn't have QtWidgets as a separate module — alias for compatibility
        QtWidgets = QtGui
        QT_BINDING = 'PyQt4'
    except Exception:
        try:
            # Try very old bindings (best-effort). The module name may vary across
            # ancient setups; attempt to import the historic 'qt' package.
            import qt as _qt
            # Provide minimal aliases to avoid immediate import crashes; runtime
            # behavior will likely need manual porting.
            QtCore = _qt
            QtGui = _qt
            QtWidgets = _qt
            QT_BINDING = 'qt'
        except Exception as e:
            raise ImportError("No supported Qt binding found (tried PyQt5, PyQt4, and legacy 'qt'). Install PyQt5 or PyQt4 to use the GUI parts.") from e
# If running under PyQt5, QPrinter is located in QtPrintSupport. Try to
# import that module so we can map QPrinter correctly; otherwise fall back
# to QtGui.QPrinter when available (e.g., PyQt4) or provide a clear
# runtime error placeholder.
QtPrintSupport = None
if QT_BINDING == 'PyQt5':
    try:
        from PyQt5 import QtPrintSupport
    except Exception:
        QtPrintSupport = None

# Basic widget aliases
QWidget = QtWidgets.QWidget
QMainWindow = QtWidgets.QMainWindow
QDialog = QtWidgets.QDialog
QApplication = QtWidgets.QApplication
# Map QPrinter from the correct module depending on binding
if 'QtPrintSupport' in globals() and QtPrintSupport is not None and hasattr(QtPrintSupport, 'QPrinter'):
    QPrinter = QtPrintSupport.QPrinter
else:
    # Try QtGui (PyQt4 / some legacy bindings)
    try:
        QPrinter = QtGui.QPrinter
    except Exception:
        class _MissingPrinter:
            def __init__(self, *args, **kwargs):
                raise RuntimeError('QPrinter is not available in the current Qt binding')
        QPrinter = _MissingPrinter

QPainter = QtGui.QPainter
QPixmap = QtGui.QPixmap
QColor = QtGui.QColor
QFontMetrics = QtGui.QFontMetrics
QFont = QtGui.QFont
QRect = QtCore.QRect

# handy Qt namespace for color/alignment/flags (old code used Qt.white etc.)
Qt = QtCore.Qt

# Common widgets/layouts used across the codebase
QLabel = QtWidgets.QLabel
QHBoxLayout = QtWidgets.QHBoxLayout
QVBoxLayout = QtWidgets.QVBoxLayout
QGridLayout = QtWidgets.QGridLayout
QSpinBox = QtWidgets.QSpinBox
QSize = QtCore.QSize
QStatusBar = QtWidgets.QStatusBar

# Pens / drawing
QPen = QtGui.QPen

# Tooltips
QToolTip = QtWidgets.QToolTip

# Dialogs / file helpers
QFileDialog = QtWidgets.QFileDialog
QMessageBox = QtWidgets.QMessageBox

# Actions / menus / toolbars
QAction = QtWidgets.QAction
QToolBar = QtWidgets.QToolBar
QMenuBar = QtWidgets.QMenuBar
QMenu = QtWidgets.QMenu

# Other widgets
QLineEdit = QtWidgets.QLineEdit
QCheckBox = QtWidgets.QCheckBox
QComboBox = QtWidgets.QComboBox
QTabWidget = QtWidgets.QTabWidget
# QTextView was an older widget; map to QTextEdit for compatibility
QTextView = QtWidgets.QTextEdit

# Layout / widgets
QTextEdit = QtWidgets.QTextEdit
QPushButton = QtWidgets.QPushButton
QSpacerItem = QtWidgets.QSpacerItem
QSizePolicy = QtWidgets.QSizePolicy

# Convenience: map QString -> native str for modern PyQt
QString = str

# Old-style signal helpers (best-effort placeholders)
def SIGNAL(s: str) -> str:
    """Placeholder to mirror old SIGNAL() usage in source. Use new-style
    signal/slot when refactoring GUI code."""
    return s

def PYSIGNAL(s: str) -> str:
    """Placeholder for PYSIGNAL used with emit/connect in old code."""
    return s

# Convenience alias for translate (used by __tr wrappers)
def translate(context, text, comment=None):
    return QtCore.QCoreApplication.translate(context, text, comment)

# qApp should dynamically get the application instance
class _QAppProxy:
    """Proxy object that forwards attribute access to QApplication.instance()"""
    def __getattr__(self, name):
        app = QtWidgets.QApplication.instance()
        if app is None:
            # Return a dummy that won't crash for translate calls
            if name == 'translate':
                return translate
            raise RuntimeError("No QApplication instance available")
        return getattr(app, name)

qApp = _QAppProxy()

__all__ = [
    # QtCore/QtGui/QtWidgets aliases
    "QWidget", "QMainWindow", "QDialog", "QApplication", "QPrinter",
    "QPainter", "QPixmap", "QColor", "QFontMetrics", "QFont", "QRect",
    "QFileDialog", "QMessageBox", "QAction", "QToolBar", "QMenuBar",
    "QMenu", "QTextEdit", "QPushButton", "QSpacerItem", "QSizePolicy",
    "QString", "SIGNAL", "PYSIGNAL", "qApp", "translate",
]
