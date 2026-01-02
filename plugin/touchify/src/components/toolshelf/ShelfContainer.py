from typing import TYPE_CHECKING

from jemlib.alib_pyqtgraph.dockarea.Container import HContainer, TContainer, VContainer

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *





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
    
class ShelfSplitterContainer:

    @staticmethod
    def setItemFold(self: "ShelfVContainer | ShelfHContainer", item: "ShelfDock", state: bool):
        if state: item.show()
        else: item.hide()

        if all(self.widget(x).isHidden() for x in range(self.count())) == True: self.hide()
        else: self.show()

    @staticmethod
    def updateGrips(self: "ShelfVContainer | ShelfHContainer", item: "ShelfDock" = None):
        from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock

        def set_handle_state(dock_index: int, is_visible: bool):
            handler = self.handle(dock_index)
            is_vert = isinstance(self, ShelfVContainer)
            if handler:
                if is_visible: 
                    handler.setMaximumSize(QSize(QWIDGETSIZE_MAX,4) if is_vert else QSize(4,QWIDGETSIZE_MAX))
                    self.setCollapsible(dock_index, True)
                else: 
                    handler.setMaximumSize(QSize(1,1))
                    self.setCollapsible(dock_index, False)

        if not item:
            for idx in range(0, self.count()): set_handle_state(idx, True)
            return
        
        section_handles = item.getHandleMode()

        show_left_grip = section_handles == ToolshelfDock.SectionHandles.BothHandles or \
            section_handles == ToolshelfDock.SectionHandles.LeftHandle
        
        show_right_grip = section_handles == ToolshelfDock.SectionHandles.BothHandles or \
            section_handles == ToolshelfDock.SectionHandles.RightHandle
        
        set_handle_state(self.indexOf(item), show_left_grip)
        set_handle_state(self.indexOf(item) + 1, show_right_grip)
        


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
        ShelfSplitterContainer.setItemFold(self, item, state)

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
        ShelfSplitterContainer.setItemFold(self, item, state)

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

