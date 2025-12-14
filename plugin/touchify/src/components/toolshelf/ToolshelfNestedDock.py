from typing import TYPE_CHECKING
from touchify.src.components.toolshelf.ShelfContainer import ShelfContainer
from touchify.src.components.toolshelf.ShelfDock import ShelfDock





from PyQt5.QtWidgets import QSizePolicy

from touchify.src.config.toolshelf.ToolshelfContainer import ToolshelfContainer
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock

if TYPE_CHECKING:
    from touchify.src.components.toolshelf.ShelfWidget import ShelfWidget
    from touchify.src.PluginManagers import TouchifyManagers

class ToolshelfNestedDock(ShelfDock):
    def __init__(self, parent: "ShelfWidget", config: ToolshelfDock, managers: "TouchifyManagers"):
        self._isAllowedToEditContainer: bool = False
        ShelfDock.__init__(self, config)
        self.managers = managers
        self.parentShelf = parent
        self.nestedShelf: "ShelfWidget" = None


        from touchify.src.components.toolshelf.ShelfWidget import ShelfWidget
        self.nestedShelf = ShelfWidget(self, self.managers, parent_dock_widget=self)
        self.nestedShelf.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.nestedShelf.setTitlebarVisibility(self._dockSettings.special_nested_show_titlebar)
        self.addWidget(self.nestedShelf)
        self.loadLayout()

        self.nestedShelf.sigEditModeChanged.connect(self.onContainerEditModeChanged)

    def setContainerEditMode(self, state: bool):
        self._isAllowedToEditContainer = state
        self.nestedShelf.setEditMode(state)

    def onContainerEditModeChanged(self, state: bool):
        self._isAllowedToEditContainer = state
        self.updateContainerEditMode()

    def updateContainerEditMode(self):
        if self._isEditMode:
            self.editableDragArea.setEditMode(not self._isAllowedToEditContainer)
        else:
            self.editableDragArea.setEditMode(False)
            self._isAllowedToEditContainer = False

    def setEditMode(self, enabled):
        super().setEditMode(enabled)
        self.updateContainerEditMode()



    def onShelfIndexChanged(self):
        pass

    def shelfReloadEvent(self, state: ToolshelfContainer):
        pass
        #from touchify.src.config.toolshelf.ToolshelfSettings import ToolshelfSettings
        #if state.options.resize_style == ToolshelfSettings.ResizeStyle.Minimum:
        #    self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        #    self.sizeManagementType = ToolshelfSettings.ResizeStyle.Minimum
        #elif state.options.resize_style == ToolshelfSettings.ResizeStyle.AdjustSize:
        #    self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        #    self.sizeManagementType = ToolshelfSettings.ResizeStyle.AdjustSize
        #elif state.options.resize_style == ToolshelfSettings.ResizeStyle.SizeHintMinimum:
        #    self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        #    self.sizeManagementType = ToolshelfSettings.ResizeStyle.SizeHintMinimum
        #elif state.options.resize_style == ToolshelfSettings.ResizeStyle.SizeHint:
        #    self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        #    self.sizeManagementType = ToolshelfSettings.ResizeStyle.SizeHint
        #else:
        #    self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        #    self.sizeManagementType = ToolshelfSettings.ResizeStyle.Default

    def setMetadata(self, state: ToolshelfContainer):
        self._dockSettings.special_nested_data = state
        self.parentShelf.saveLayout()

    def getMetadata(self) -> ToolshelfContainer:
        return self._dockSettings.special_nested_data
    
    def loadLayout(self):
        self.nestedShelf.loadLayout()

    def saveLayout(self):
        self.nestedShelf.saveLayout()