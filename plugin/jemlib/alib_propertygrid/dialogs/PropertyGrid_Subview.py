from typing import Callable
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from jemlib.alib_vaporjem.extensions import pyqt_extensions
from krita import *


class PropertyGrid_Subview(QDialog):

    @staticmethod
    def Setup(dlg: "PropertyGrid_Subview", parent: QWidget, mode: str, options: dict[str, any], cls: type["PropertyGrid_Subview"]=None):
        if dlg != None:
            if pyqt_extensions.CommonHelpers.isDeleted(dlg) == False:
                dlg.deleteLater()
                dlg = None

        if not cls:
            cls = PropertyGrid_Subview
    
        dlg = cls(parent, mode, options)
        return dlg

    def __init__(self, parent: QWidget, mode: str, options: dict[str, any]):
        super().__init__(parent)

        self.__dialogFullyLoaded = False


        from ..PropertyGrid import PropertyGrid

        self.setContentsMargins(0,0,0,0)
        self.setWindowTitle("EDITOR")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self.__mode = mode
        self.__options = options
        self.__rootContainer: PropertyGrid = None

        self.onRejectFunction: Callable[[], None] = None
        self.onAcceptFunction: Callable[[any], None] = None

        if 'title' in self.__options:
            self.setWindowTitle(self.__options['title'])

        if 'container' in self.__options:
            if isinstance(self.__options['container'], PropertyGrid):
                self.__rootContainer = self.__options['container']

        self.initContents()

        self.__dialogFullyLoaded = True

    def getOptions(self):
        return self.__options
    
    def getRootContainer(self):
        return self.__rootContainer

    def getAcceptResult(self):
        return 1

    def initContents(self):
        pass

    def showAsWidget(self):
        self.setWindowFlags(Qt.WindowType.Widget)
        if self.getRootContainer(): self.getRootContainer().navigateForwards(self)
        self.show()

    def show(self):
        super().show()
    
    def close(self):
        response = super().close()
        if response and self.onRejectFunction: self.onRejectFunction()
        return response
    
    def closeEvent(self, a0):
        if not self.__dialogFullyLoaded: a0.ignore()
        a0.accept()

    def onApply(self):
        if self.onAcceptFunction: self.onAcceptFunction(self.getAcceptResult())

    def onSave(self):
        self.accept()

    def onClose(self):
        self.reject()

    def accept(self):
        if self.onAcceptFunction: self.onAcceptFunction(self.getAcceptResult())
        return super().accept()

    def reject(self):
        if self.onRejectFunction: self.onRejectFunction()
        return super().reject()
