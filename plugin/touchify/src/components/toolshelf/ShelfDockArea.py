from typing import TYPE_CHECKING
from jemlib.alib_pyqtgraph.dockarea.DockArea import DockArea
from touchify.src.components.toolshelf.ShelfContainer import ShelfContainer, ShelfHContainer, ShelfSplitterContainer, ShelfVContainer
from touchify.src.components.toolshelf.ShelfDockDrop import ShelfDropDock


if TYPE_CHECKING:
    from touchify.src.components.toolshelf.ShelfDock import ShelfDock

class ShelfDockArea(DockArea):
    def __init__(self, parent=None, temporary=False, home=None):
        super().__init__(parent, temporary, home)
        self.dockdrop = ShelfDropDock(self)
        self.dockdrop.removeAllowedArea('center')
        self.dockdrop.raiseOverlay()
        self.setMouseTracking(True)
        self._parentAreaId: str = ""
        self._isEditMode: bool = False
    
    #region Overrides

    def makeContainer(self, typ):
        from touchify.src.components.toolshelf.ShelfContainer import ShelfHContainer, ShelfTContainer, ShelfVContainer
        if typ == 'vertical':
            new = ShelfVContainer(self)
        elif typ == 'horizontal':
            new = ShelfHContainer(self)
        elif typ == 'tab':
            new = ShelfTContainer(self)
        else:
            raise ValueError("typ must be one of 'vertical', 'horizontal', or 'tab'")

        new.setParentAreaId(self._parentAreaId)
        new.setEditMode(self._isEditMode)

        return new

    def addDock(self, dock=None, position='bottom', relativeTo=None, **kwds):
        """Adds a dock to this area.
        
        ============== =================================================================
        **Arguments:**
        dock           The new Dock object to add. If None, then a new Dock will be 
                       created.
        position       'bottom', 'top', 'left', 'right', 'above', or 'below'
        relativeTo     If relativeTo is None, then the new Dock is added to fill an 
                       entire edge of the window. If relativeTo is another Dock, then 
                       the new Dock is placed adjacent to it (or in a tabbed 
                       configuration for 'above' and 'below'). 
        ============== =================================================================
        
        All extra keyword arguments are passed to Dock.__init__() if *dock* is
        None.        
        """
        if dock is None:
            dock = ShelfDock(**kwds)
            
        # store original area that the dock will return to when un-floated
        if not self.temporary:
            dock.orig_area = self
        
        
        ## Determine the container to insert this dock into.
        ## If there is no neighbor, then the container is the top.
        if relativeTo is None or relativeTo is self:
            if self.topContainer is None:
                container = self
                neighbor = None
            else:
                container = self.topContainer
                neighbor = None
        else:
            if isinstance(relativeTo, str):
                relativeTo = self.docks[relativeTo]
            container = self.getContainer(relativeTo)
            if container is None:
                raise TypeError("Dock %s is not contained in a DockArea; cannot add another dock relative to it." % relativeTo)
            neighbor = relativeTo
        
        ## what container type do we need?
        neededContainer = {
            'bottom': 'vertical',
            'top': 'vertical',
            'left': 'horizontal',
            'right': 'horizontal',
            'above': 'tab',
            'below': 'tab'
        }[position]
        
        ## Can't insert new containers into a tab container; insert outside instead.
        if neededContainer != container.type() and container.type() == 'tab':
            neighbor = container
            container = container.container()
            
        ## Decide if the container we have is suitable.
        ## If not, insert a new container inside.
        if neededContainer != container.type():
            if neighbor is None:
                container = self.addContainer(neededContainer, self.topContainer)
            else:
                container = self.addContainer(neededContainer, neighbor)
            
        ## Insert the new dock before/after its neighbor
        insertPos = {
            'bottom': 'after',
            'top': 'before',
            'left': 'before',
            'right': 'after',
            'above': 'before',
            'below': 'after'
        }[position]
        #print "request insert", dock, insertPos, neighbor
        old = dock.container()
        container.insert(dock, insertPos, neighbor)
        self.docks[dock.name()] = dock
        if old is not None:
            old.apoptose()
        
        self.updateDocks()
        return dock

    def moveDock(self, dock, position, neighbor):
        super().moveDock(dock, position, neighbor)
        self.updateDocks()

    def restoreState(self, state, missing='error', extra='bottom'):
        super().restoreState(state, missing, extra)
        self.updateDocks()


    #endregion

    def updateDocks(self):
        from touchify.src.components.toolshelf.ShelfDock import ShelfDock
        for cnt in self.findChildren(ShelfContainer):
            if isinstance(cnt, ShelfVContainer) or isinstance(cnt, ShelfHContainer):
                ShelfSplitterContainer.updateGrips(cnt)

        for uuid in self.docks:
            dock = self.docks[uuid]
            if isinstance(dock, ShelfDock):
                dock.updateGrips()

    def setEditMode(self, state: bool):
        from touchify.src.components.toolshelf.ShelfDock import ShelfDock
        self._isEditMode = state
        for uuid in self.docks:
            dock = self.docks[uuid]
            if isinstance(dock, ShelfDock):
                dock: ShelfDock
                dock.setEditMode(state)
    
    def setAreaId(self, value: str):
        self._parentAreaId = value
        self.dockdrop.setParentAreaId(value)

    
