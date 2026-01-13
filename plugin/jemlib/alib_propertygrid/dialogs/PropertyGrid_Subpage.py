from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from jemlib.alib_propertygrid.dialogs.PropertyGrid_Subview import PropertyGrid_Subview
from krita import *

class PropertyGrid_Subpage(PropertyGrid_Subview):
    @staticmethod
    def Setup(dlg: "PropertyGrid_Subpage", parent: QWidget, mode: str, options: dict[str, any]):
        return PropertyGrid_Subview.Setup(dlg, parent, mode, options, cls=PropertyGrid_Subpage)
    
    def initContents(self):
        from ..PropertyViewport import PropertyViewport
        if not self.getRootContainer(): return

        self.__viewport = PropertyViewport(self.getRootContainer(), self.getRootContainer().getPraser())
        self.__viewport.setParent(self)

        if 'item' in self.getOptions():
            self.__viewport.setDataObject(self.getOptions()['item'])

        self.__viewLayout = QVBoxLayout(self)
        self.__viewLayout.setContentsMargins(0,0,0,0)
        self.__viewLayout.setSpacing(0)

        self.__viewLayout.addWidget(self.__viewport)
        self.setLayout(self.__viewLayout)