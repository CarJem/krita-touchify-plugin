from typing import TYPE_CHECKING, TypeVar
from touchify.src.alib_pyqtgraph.dockarea.Container import HContainer, TContainer, VContainer
from touchify.src.alib_pyqtgraph.dockarea.DockArea import DockArea
from touchify.src.components.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

if TYPE_CHECKING:
    from touchify.src.components.toolshelf.ShelfDock import ShelfDock, ShelfLabel


class ShelfPanel(DockArea):
    def __init__(self, parent=None, temporary=False, home=None):
        super().__init__(parent, temporary, home)

    def makeContainer(self, typ):
        if typ == 'vertical':
            new = ShelfVContainer(self)
        elif typ == 'horizontal':
            new = ShelfHContainer(self)
        elif typ == 'tab':
            new = ShelfTContainer(self)
        else:
            raise ValueError("typ must be one of 'vertical', 'horizontal', or 'tab'")
        return new

T = TypeVar('T', VContainer, HContainer, TContainer)    


class ShelfContainer:
    def __init__(self):
        sup: VContainer | HContainer | TContainer = self
        self.currentTool: str = ""
        self.isEditMode: bool = False
        self.requiredTools: list[str] = []
        self.selected = False

    def getOptions(self):
        result = ShelfContainerOptions()
        result.requires_specific_tool = ",".join(self.requiredTools)
        return result
    
    def setOptions(self, cfg: "ShelfContainerOptions"):
        self.requiredTools = cfg.requires_specific_tool.split(",")
        if "" in self.requiredTools: self.requiredTools.remove("")

    def saveState(self):
        return {"requires_tools": ",".join(self.requiredTools)}
        
    def restoreState(self, state):
        try:
            input: str = state['requires_tools']
            self.requiredTools = input.split(",")
            if "" in self.requiredTools: self.requiredTools.remove("")
        except:
            pass

    def matchesCurrentTool(self):
        return self.currentTool in self.requiredTools or self.currentTool == "" or len(self.requiredTools) == 0

    def setEditMode(self, state: bool):
        self.isEditMode = state
        self.selected = False
        self.sync()

    def onToolChanged(self, current_tool: str):
        self.currentTool = current_tool
        self.sync()
        
    def sync(self):
        sup: VContainer | HContainer | TContainer = self
        if self.matchesCurrentTool() or self.isEditMode: sup.setVisible(True)
        else: sup.setVisible(False)

    def highlight(self, state: bool):
        sup: VContainer | HContainer | TContainer = self
        if state != self.selected:
            self.selected = state
            if self.selected:
                sup.setStyleSheet(f"""
                    VContainer, HContainer, TContainer {{
                        background-color: rgba(255,255,255,0.2);
                    }}
                """)
            else:
                sup.setStyleSheet("")
    
class ShelfContainerOptions:
    def __init__(self) -> None:
        self.requires_specific_tool: str = ""

    def propertygrid_hidden(self):
        return []

    def forceLoad(self):
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["requires_specific_tool"] = "Requires Specific Tool"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["requires_specific_tool"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.MultiToolSelection)
        return restrictions    

class ShelfVContainer(ShelfContainer, VContainer):
    def __init__(self, area):
        VContainer.__init__(self, area)
        ShelfContainer.__init__(self)

    def saveState(self):
        return VContainer.saveState(self) | ShelfContainer.saveState(self)

    def restoreState(self, state):
        VContainer.restoreState(self, state)
        ShelfContainer.restoreState(self, state)

class ShelfHContainer(ShelfContainer, HContainer):
    def __init__(self, area):
        HContainer.__init__(self, area)
        ShelfContainer.__init__(self)

    def saveState(self):
        return HContainer.saveState(self) | ShelfContainer.saveState(self)

    def restoreState(self, state):
        HContainer.restoreState(self, state)
        ShelfContainer.restoreState(self, state)

class ShelfTContainer(ShelfContainer, TContainer):
    def __init__(self, area):
        TContainer.__init__(self, area)
        ShelfContainer.__init__(self)

    def saveState(self):
        return TContainer.saveState(self) | ShelfContainer.saveState(self)

    def restoreState(self, state):
        TContainer.restoreState(self, state)
        ShelfContainer.restoreState(self, state)

    #def _insertItem(self, item: "ShelfDock", index: int):
    #    from touchify.src.components.toolshelf.ShelfDock import ShelfDock, ShelfLabel
    #    if not isinstance(item, ShelfDock):
    #        raise Exception("Tab containers may hold only shelf docks, not other containers.")
    #    item.showTitleBar(False)
    #    self.stack.insertWidget(index, item)
    #    self.hTabLayout.insertWidget(index, item.label)
    #    item.label.sigClicked.connect(self.tabClicked)
    #    self.tabClicked(item.label)

        

