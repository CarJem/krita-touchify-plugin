from PyQt5 import QtCore, QtWidgets

class ProgressBar(QtWidgets.QProgressBar):
    SIGNAL_VISIBILITY_CHANGED = QtCore.pyqtSignal()
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setStyleSheet( "{ background-color: rgba( 0, 0, 0, 50 ); }" )

    def hideEvent(self, a0):
        self.SIGNAL_VISIBILITY_CHANGED.emit()
        return super().hideEvent(a0)
    
    def showEvent(self, a0):
        self.SIGNAL_VISIBILITY_CHANGED.emit()
        return super().showEvent(a0)