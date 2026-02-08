from enum import IntEnum
from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


from jemlib.api_touchify.env import *

from jemlib.alib_vaporjem.extensions.krita_extensions import *

if TYPE_CHECKING:
    from touchify.src.PluginManagers import TouchifyManagers
    from touchify.src.Plugin import TouchifyWindow
    from touchify_toolshelves.src.components.ToolshelfDockerWidgetPad import ToolshelfDockerWidgetPad


EDGE_PADDING: int = 5
    
class WidgetPadManager(QObject):

    class Alignment(IntEnum):
        AlignNone = 0,
        TopLeft = 1,
        TopCenter = 2,
        TopRight = 3,
        MidLeft = 4,
        MidRight = 5,
        BottomLeft = 6,
        BottomCenter = 7,
        BottomRight = 8       

    def __init__(self, parent: QObject, managers: "TouchifyManagers"):
        super().__init__(parent)
        self.managers = managers
        self.LAYOUT_CACHE: dict[WidgetPadManager.Alignment, list["ToolshelfDockerWidgetPad"]] = {}
        self.LAYOUT_LIST: list["ToolshelfDockerWidgetPad"] = []
        self.__currentlyUpdating = False

        for alignKey in WidgetPadManager.Alignment:
            self.LAYOUT_CACHE[alignKey] = []

    def Window_Load(self, window: "TouchifyWindow"):
        window.sigWindowMoved.connect(self.onWidgetPadAreaUpdate)
        window.sigWindowResized.connect(self.onWidgetPadAreaUpdate)
        self.managers.mgr_canvas.canvasResized.connect(self.onWidgetPadAreaUpdate)
        self.managers.mgr_canvas.canvasMoved.connect(self.onWidgetPadAreaUpdate)
    
    #region Get / Set

    def widgetPadOffset(self, src: "ToolshelfDockerWidgetPad"):
        if src._previousNeighbor == None: 
            return QSize(0,0)
        else:
            if src._previousNeighbor.isVisible():
                return src._previousNeighbor.size() + QSize(EDGE_PADDING, EDGE_PADDING) + self.widgetPadOffset(src._previousNeighbor)
            else:
                return self.widgetPadOffset(src._previousNeighbor)

    #endregion

    #region Actions

    def removeWidgetPad(self, src: "ToolshelfDockerWidgetPad", alignmentKey: Alignment):
        if src in self.LAYOUT_CACHE[alignmentKey]: 
            self.LAYOUT_CACHE[alignmentKey].remove(src)
            src.setAllowSignals(False)
            self.reorderWidgetPads(alignmentKey)

            try: src.sigOnMoved.disconnect(self.onWidgetPadMoved)
            except: pass

            try: src.sigOnResized.disconnect(self.onWidgetPadResized)
            except: pass
            self.onWidgetPadMoved(src)
            src.setAllowSignals(True)

    def addWidgetPad(self, src: "ToolshelfDockerWidgetPad", alignmentKey: Alignment):
        if src not in self.LAYOUT_CACHE[alignmentKey]: 
            self.LAYOUT_CACHE[alignmentKey].append(src)
            src.setAllowSignals(False)
            self.reorderWidgetPads(alignmentKey)

            try: src.sigOnMoved.connect(self.onWidgetPadMoved)
            except: pass

            try: src.sigOnResized.connect(self.onWidgetPadResized)
            except: pass
            self.onWidgetPadMoved(src)
            src.setAllowSignals(True)

    def moveWidgetPad(self, src: "ToolshelfDockerWidgetPad", alignFrom: Alignment, alignTo: Alignment):
        if alignFrom == alignTo:
            return
        
        self.removeWidgetPad(src, alignFrom)
        self.addWidgetPad(src, alignTo)
        self.onWidgetPadMoved(src)

    def nudgeWidgetPad(self, src: "ToolshelfDockerWidgetPad"):
        self.reorderWidgetPads(src._alignment)
        self.onWidgetPadMoved(src)

    def reorderWidgetPads(self, alignKey: Alignment):

        def getElement(index: int):
            if index <= -1:
                return None
            elif index > len(self.LAYOUT_CACHE[alignKey]) - 1:
                return None
            else:
                return self.LAYOUT_CACHE[alignKey][index]    

        self.LAYOUT_CACHE[alignKey].sort(key=lambda x: (x._priority))
        for i, j in enumerate(self.LAYOUT_CACHE[alignKey]):
            j._previousNeighbor = getElement(i-1)
            j._nextNeighbor = getElement(i+1)

    #endregion

    #region Signals

    def onSyncWidgetPad(self, src: "ToolshelfDockerWidgetPad"):
        if not src.isVisible():
            return
        
        if src.isFloating() == False:
            src.setFloating(True)

        if not src.managers:
            return
        
        active_canvas = self.managers.mgr_canvas.active_canvas

        if not active_canvas:
            return
        

        _lastNeighborSize = self.widgetPadOffset(src)
        
        space_rect = active_canvas.rect()
        docker_width = src.width()
        docker_height = src.height()

        if docker_width != 0 and docker_height != 0:
            docker_halfwidth = int(docker_width / 2)
            docker_halfheight = int(docker_height / 2)
        else:
            docker_halfwidth = 0
            docker_halfheight = 0

    
        top_left = QPoint(space_rect.topLeft()) + QPoint(EDGE_PADDING, EDGE_PADDING)
        top_center = QPoint(space_rect.center().x(),space_rect.top()) - QPoint(docker_halfwidth, 0) + QPoint(0, EDGE_PADDING)
        top_right = QPoint(space_rect.topRight()) - QPoint(docker_width, 0) + QPoint(-EDGE_PADDING, EDGE_PADDING)

        mid_left = QPoint(space_rect.left(), space_rect.center().y()) - QPoint(0, docker_halfheight) + QPoint(EDGE_PADDING, 0)
        mid_right = QPoint(space_rect.right(), space_rect.center().y()) - QPoint(docker_width, docker_halfheight) + QPoint(-EDGE_PADDING, 0)

        bottom_left = QPoint(space_rect.bottomLeft()) - QPoint(0, docker_height) + QPoint(EDGE_PADDING, -EDGE_PADDING)
        bottom_center = QPoint(space_rect.center().x(), space_rect.bottom()) - QPoint(docker_halfwidth, docker_height) + QPoint(0, -EDGE_PADDING)
        bottom_right = QPoint(space_rect.bottomRight()) - QPoint(docker_width, docker_height) + QPoint(-EDGE_PADDING, -EDGE_PADDING)


        _position: QPoint = QPoint(0,0)

        match src._alignment:
            case WidgetPadAlignment.TopLeft:
                _position = active_canvas.mapToGlobal(top_left)
                _position.setX(_position.x() + _lastNeighborSize.width())
            case WidgetPadAlignment.TopRight:
                _position = active_canvas.mapToGlobal(top_right)
                _position.setX(_position.x() - _lastNeighborSize.width())
            case WidgetPadAlignment.BottomRight:
                _position = active_canvas.mapToGlobal(bottom_right)
                _position.setX(_position.x() - _lastNeighborSize.width())
            case WidgetPadAlignment.BottomLeft:
                _position = active_canvas.mapToGlobal(bottom_left)
                _position.setX(_position.x() + _lastNeighborSize.width())
            case WidgetPadAlignment.TopCenter:
                _position = active_canvas.mapToGlobal(top_center)
                _position.setY(_position.y() + _lastNeighborSize.height())
            case WidgetPadAlignment.BottomCenter:
                _position = active_canvas.mapToGlobal(bottom_center)
                _position.setY(_position.y() - _lastNeighborSize.height())
            case WidgetPadAlignment.MidLeft:
                _position = active_canvas.mapToGlobal(mid_left)
                _position.setX(_position.x() + _lastNeighborSize.width())
            case WidgetPadAlignment.MidRight:
                _position = active_canvas.mapToGlobal(mid_right)
                _position.setX(_position.x() - _lastNeighborSize.width())
            case _:
                _position = active_canvas.mapToGlobal(QPoint(0,0))

        #TODO: Determine if we actually want to account for the space avaliable
        #------
        #_max_height = space_rect.height() - EDGE_PADDING * 2
        #_max_width = space_rect.width() - EDGE_PADDING * 2

        #TODO: Determine if we actually want to account for the space avaliable
        #------
        #_c_width = src.width()
        #_c_height = src.height()
        _c_pos = src.pos()

        src.shrinkToFit()
        
        #TODO: Determine if we actually want to account for the space avaliable|
        #------
        #if _c_width > _max_width:
        #    src.resize(_max_width, _c_height)
        #
        #if _c_height > _max_height:
        #    src.resize(_c_width, _max_height)

        if _c_pos != _position:
            src.move(_position)

    def onWidgetPadMoved(self, src: "ToolshelfDockerWidgetPad", event: QMoveEvent = None, direction: str = "both"):
        src.setAllowSignals(False)
        self.onSyncWidgetPad(src)
        if src._previousNeighbor and direction in ['left', 'both']: self.onWidgetPadMoved(src._previousNeighbor, direction='left')
        if src._nextNeighbor and direction in ['right', 'both']: self.onWidgetPadMoved(src._nextNeighbor, direction='right')
        src.setAllowSignals(True)

    def onWidgetPadResized(self, src: "ToolshelfDockerWidgetPad", event: QResizeEvent = None, direction: str = "both"):
        src.setAllowSignals(False)
        self.onSyncWidgetPad(src)
        if src._previousNeighbor and direction in ['left', 'both']: self.onWidgetPadResized(src._previousNeighbor, direction='left')
        if src._nextNeighbor and direction in ['right', 'both']: self.onWidgetPadResized(src._nextNeighbor, direction='right')
        src.setAllowSignals(True)

    def onWidgetPadAreaUpdate(self):
        if self.__currentlyUpdating:
            return
        
        self.__currentlyUpdating = True

        for x in [element for inner_list in self.LAYOUT_CACHE.values() for element in inner_list]:
            self.onSyncWidgetPad(x)

        self.__currentlyUpdating = False

    #endregion

WidgetPadAlignment = WidgetPadManager.Alignment