from PyQt5.QtWidgets import QVBoxLayout, QScrollArea


from ...pyqt.widgets.QResizableWidget import QResizableWidget
from ....settings.TouchifyConfig import *


class NtScrollAreaContainer(QResizableWidget):

    def __init__(self, scrollArea = None, parent=None):
        super(NtScrollAreaContainer, self).__init__(parent)
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0,0,0,0)
        self.sa = None

        self.setScrollArea(scrollArea)

    def sizeHint(self):
        """
        Reimplemented function. If a QScrollArea as been set
        the size hint of it's widget will be returned."""
        if self.sa and self.sa.widget():
            return self.sa.widget().sizeHint()

        return super().sizeHint()
    
    
    



    def setScrollArea(self, scrollArea):
        """
        Set the QScrollArea for the container to hold.

        True will be returned upon success and if no prior QScrollArea was set. 
        If another QScrollArea was already set it will be returned so that 
        it can be disposed of properly.

        If an invalid arguement (i.e. not a QScrollArea) or the same QScrollArea
        as the currently set one is passed, nothing happens and False is returned."""
        if (isinstance(scrollArea, QScrollArea) and
            scrollArea is not self.sa):
            ret = True

            if not self.sa:
                self.layout().addWidget(scrollArea)
            else:
                self.layout().replaceWidget(self.sa, scrollArea)
                ret = self.sa # set the old QScrollArea to be returned

            self.sa = scrollArea
            return ret

        return False

    def scrollArea(self):
        return self.sa