"""Small shim for Qwt. Tries to import the real qwt (pyqwt) package and
falls back to placeholders that raise informative errors when used.

This shim exists so imports like `from qwt import *` can be redirected
to `from .qwt_compat import *` and not crash at import time if PyQwt is
absent. A real runtime requires PyQwt (or a replacement) and a proper
port of used APIs.
"""
try:
    import qwt
    # Try to import all expected symbols, with fallbacks for PythonQwt/pyqwt differences
    try:
        from qwt import QwtPlot, QwtMarker, QwtCurve, QwtPlotItem, QwtPlotGrid, QwtWheel
    except ImportError:
        # Some forks use lowercase or different names
        QwtPlot = getattr(qwt, 'QwtPlot', None)
        QwtMarker = getattr(qwt, 'QwtMarker', None)
        QwtCurve = getattr(qwt, 'QwtCurve', None)
        QwtPlotItem = getattr(qwt, 'QwtPlotItem', None)
        QwtPlotGrid = getattr(qwt, 'QwtPlotGrid', None)
        QwtWheel = getattr(qwt, 'QwtWheel', None)
    # PythonQwt uses QwtPlotCurve instead of QwtCurve
    if QwtCurve is None:
        QwtCurve = getattr(qwt, 'QwtPlotCurve', None)
    # QwtPlotMarker may be missing; use QwtMarker as fallback
    QwtPlotMarker = getattr(qwt, 'QwtPlotMarker', None) or QwtMarker
    
    # QwtWheel may not be available in all qwt versions; provide None fallback
    if QwtWheel is None:
        QwtWheel = None  # Explicitly mark as unavailable
        
    __all__ = ["QwtPlot", "QwtMarker", "QwtCurve", "QwtPlotItem", "QwtPlotGrid", "QwtPlotMarker", "QwtWheel"]
except Exception:
    # Provide minimal placeholders so the package can be imported.
    class _Placeholder:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("PyQwt (qwt) not available: install PythonQwt (pip install PythonQwt) or adapt code to a supported plotting library")

    QwtPlot = _Placeholder
    QwtMarker = _Placeholder
    QwtPlotMarker = QwtMarker
    QwtCurve = _Placeholder
    QwtPlotItem = _Placeholder
    QwtPlotGrid = _Placeholder
    QwtWheel = _Placeholder
    __all__ = ["QwtPlot", "QwtMarker", "QwtCurve", "QwtPlotItem", "QwtPlotGrid", "QwtPlotMarker", "QwtWheel"]
