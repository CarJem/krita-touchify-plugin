from re import L
from typing import TYPE_CHECKING, Any

from touchify.src.alib_pyqtgraph.dockarea.Container import Container, HContainer, TContainer, VContainer

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from touchify.src.components.toolshelf.ShelfDockArea import ShelfDockArea

if TYPE_CHECKING:
    from touchify.src.components.toolshelf.ShelfDock import ShelfDockLabel, ShelfDock


class ShelfContainer(object):
    def __init__(self):
        self.isEditMode: bool = False
        self.parentAreaId: str = ""

    def saveState(self):
        return {}
        
    def restoreState(self, state):
        pass

    def setParentAreaId(self, val: str):
        self.parentAreaId = val

    def setEditMode(self, state: bool):
        self.isEditMode = state
    
    def enterEvent(self, a0: QEvent):
        pass

    def leaveEvent(self, a0: QEvent):
        pass

    def setItemFold(self, item: "ShelfDock", state: bool):
        pass

    @staticmethod
    def isContainer(obj: object):
        return isinstance(obj, ShelfVContainer) or isinstance(obj, ShelfHContainer) or isinstance(obj, ShelfTContainer)

    @staticmethod
    def asContainer(obj: object):
        res: ShelfHContainer | ShelfVContainer | ShelfTContainer = obj
        return res

class ShelfVContainer(ShelfContainer, VContainer):
    def __init__(self, area):
        VContainer.__init__(self, area)
        ShelfContainer.__init__(self)

    def saveState(self):
        return VContainer.saveState(self) | ShelfContainer.saveState(self)

    def restoreState(self, state):
        VContainer.restoreState(self, state)
        ShelfContainer.restoreState(self, state)

    def setItemFold(self, item: "ShelfDock", state: bool):
        ShelfContainer.setItemFold(self, item, state)
        if state: item.show()
        else: item.hide()

        if all(self.widget(x).isHidden() for x in range(self.count())) == True: self.hide()
        else: self.show()

class ShelfHContainer(ShelfContainer, HContainer):
    def __init__(self, area):
        HContainer.__init__(self, area)
        ShelfContainer.__init__(self)

    def saveState(self):
        return HContainer.saveState(self) | ShelfContainer.saveState(self)

    def restoreState(self, state):
        HContainer.restoreState(self, state)
        ShelfContainer.restoreState(self, state)

    def setItemFold(self, item: "ShelfDock", state: bool):
        ShelfContainer.setItemFold(self, item, state)
        if state: item.show()
        else: item.hide()

        if all(self.widget(x).isHidden() for x in range(self.count())) == True: self.hide()
        else: self.show()

class ShelfTContainer(ShelfContainer, TContainer):
    def __init__(self, area):
        TContainer.__init__(self, area)
        ShelfContainer.__init__(self)

    def saveState(self):
        return TContainer.saveState(self) | ShelfContainer.saveState(self)
    
    def restoreState(self, state):
        TContainer.restoreState(self, state)
        ShelfContainer.restoreState(self, state)

    def setItemFold(self, item: "ShelfDock", state: bool):
        ShelfContainer.setItemFold(self, item, state)
        if state: item.show()
        else: item.hide()

        if all(self.widget(x).isHidden() for x in range(self.count())) == True: self.hide()
        else: self.show()

