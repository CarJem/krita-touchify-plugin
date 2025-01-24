from PyQt5.QtCore import *
from PyQt5.QtWidgets import *



class NtSubWinFilter(QObject):
    """Event Filter object. Ensure that a target widget is moved
    to a desired position (corner of the view) when the subwindow area updates."""

    SIGNAL_EVENT_REQUESTED = pyqtSignal()

    def __init__(self, parent=None):
        super(NtSubWinFilter, self).__init__(parent)
        self.target = None

    def eventFilter(self, obj: QObject, e: QEvent):
        """Event filter: Update the Target's position to match to the current view 
        if the (sub-)window has moved, changed in size or been activated."""

        if not self.target: return False
        elif not (e.type() in [ QEvent.Type.Move, QEvent.Type.Resize, QEvent.Type.WindowActivate ]): return False
        else: self.target.subWindowEvent()

        return False

        

    def setTargetWidget(self, wdgt):
        """Set which QWidget to adjust the position of."""
        self.target = wdgt