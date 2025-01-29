from PyQt5.QtCore import *
from PyQt5.QtWidgets import *



class NtCanvasFilter(QObject):
    """Event Filter object. Ensure that a target widget is moved
    to a desired position (corner of the view) when the subwindow area updates."""

    SIGNAL_EVENT_REQUESTED = pyqtSignal()

    def __init__(self, parent=None):
        super(NtCanvasFilter, self).__init__(parent)
        self.target = None



    def setTargetWidget(self, wdgt):
        """Set which QWidget to adjust the position of."""
        self.target = wdgt