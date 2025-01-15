from PyQt5.QtCore import *
from PyQt5.QtWidgets import *



class NtSubWinFilter(QObject):
    """Event Filter object. Ensure that a target widget is moved
    to a desired position (corner of the view) when the subwindow area updates."""

    SIGNAL_ACTIVATE_FORCE = pyqtSignal()
    SIGNAL_ACTIVATE_QUEUE = pyqtSignal()

    def __init__(self, parent=None):
        super(NtSubWinFilter, self).__init__(parent)
        self.target = None

    def eventFilter(self, obj: QObject, e: QEvent):
        """Event filter: Update the Target's position to match to the current view 
        if the (sub-)window has moved, changed in size or been activated."""
        is_queue_event = (e.type() == QEvent.Type.Resize or e.type() == QEvent.Type.WindowActivate or e.type() == QEvent.Type.Move)
        is_force_event = (False)

        if is_queue_event:
            #print("SIGNAL_ACTIVATE_QUEUE")
            self.SIGNAL_ACTIVATE_QUEUE.emit()
        elif is_force_event:
            #print("SIGNAL_ACTIVATE_FORCE")
            self.SIGNAL_ACTIVATE_FORCE.emit()

        return False