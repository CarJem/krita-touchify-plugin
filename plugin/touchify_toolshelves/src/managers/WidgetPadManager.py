from enum import IntEnum
from jemlib.alib_vaporjem.extensions.pyqt_extensions import CommonHelpers
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
        self.LAYOUT_ITEMS: dict[int, "ToolshelfDockerWidgetPad"] = {}
        self.__currentlyUpdating = False
        self.__window: "TouchifyWindow" = None

        for alignKey in WidgetPadManager.Alignment:
            self.LAYOUT_CACHE[alignKey] = []

    def Window_Load(self, window: "TouchifyWindow"):
        self.__window = window
        window.sigWindowMoved.connect(self.onWidgetPadAreaUpdate)
        window.sigWindowResized.connect(self.onWidgetPadAreaUpdate)
        self.managers.mgr_canvas.canvasChanged.connect(self.onCanvasChanged)
        self.managers.mgr_canvas.canvasResized.connect(self.onWidgetPadAreaUpdate)
        self.managers.mgr_canvas.canvasMoved.connect(self.onWidgetPadAreaUpdate)
        if self.dockWidgetMode(): self.Dockers_Install()
        else: self.Overlays_Load()


    @staticmethod
    def Dockers_Load(amount: int):
        from touchify_toolshelves.src.components.ToolshelfDockerWidgetPad import DynamicToolshelfDockerWidgetPad
        from jemlib.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
        for idx in range (0, amount):
            actual_id = idx + 1
            docker_name = TouchifyEnv.DockerID.WIDGETPAD + "_" + str(actual_id)
            docker_class = DynamicToolshelfDockerWidgetPad(actual_id)
            KritaAPI.add_dock_widget_factory(docker_name, DockWidgetFactoryAPI.DockPosition.DockTornOff, docker_class)

    def Dockers_Install(self):
        for i in self.managers.api_window().dockers:
            if i.objectName().startswith(TouchifyEnv.DockerID.WIDGETPAD):
                i.setupDocker(self)

    def Overlays_Load(self):
        from touchify.src.settings.TouchifySettings import TouchifySettings
        for idx in range (0, TouchifySettings.preferences().dockers.number_of_widgetpads):
            actual_id = idx + 1
            self.Overlays_Reload(actual_id)

    def Overlays_Reload(self, docker_id: int):
        from touchify_toolshelves.src.components.ToolshelfDockerWidgetPad import DynamicToolshelfDockerWidgetPad
        docker_name = TouchifyEnv.DockerID.WIDGETPAD + "_" + str(docker_id)
        docker_type = DynamicToolshelfDockerWidgetPad(docker_id)
        docker_widget: ToolshelfDockerWidgetPad = docker_type()
        docker_widget.setObjectName(docker_name)
        docker_widget.setAutoFillBackground(True)
        docker_widget.setup(self.__window)
        docker_widget.setupDocker(self)
        self.LAYOUT_ITEMS[docker_id] = docker_widget
            
    #region Get / Set

    def mapToGlobal(self, active_canvas: QOpenGLWidget | None, point: QPoint):
        if active_canvas == None: 
            return QPoint(0,0)
        elif self.dockWidgetMode(): 
            return active_canvas.mapToGlobal(point)
        else: 
            return active_canvas.mapTo(active_canvas, point)

    def dockWidgetMode(self):
        from touchify_toolshelves.Extension import TouchifyToolshelfExtension
        return TouchifyToolshelfExtension.isDockWidgetMode()

    def widgetPadOffset(self, src: "ToolshelfDockerWidgetPad"):
        if src._previousNeighbor == None: 
            return QSize(0,0)
        else:
            if CommonHelpers.isDeleted(src._previousNeighbor):
                return self.widgetPadOffset(src._previousNeighbor)
            elif src._previousNeighbor.isVisible():
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

    def onCanvasChanged(self):
        self.onSyncOverlays()

    def onSyncOverlays(self):
        if self.dockWidgetMode(): return
        if not self.managers: return

        active_canvas = self.managers.mgr_canvas.active_canvas

        if not active_canvas:
            if self.__window: self.Overlays_Load()
            return
        
        if not self.__window: return
        
        for key in self.LAYOUT_ITEMS: 
            if CommonHelpers.isDeleted(self.LAYOUT_ITEMS[key]):
                self.Overlays_Reload(key)
            
            i = self.LAYOUT_ITEMS[key]
            if i.parentWidget() != active_canvas: 
                i.mgr_widgetpad = self
                i.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
                i.setParent(active_canvas)
            i.setVisible(True)
            self.onSyncWidgetPad(i)

    def onSyncWidgetPad(self, src: "ToolshelfDockerWidgetPad"):
        if CommonHelpers.isDeleted(src):
            return

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
                _position = self.mapToGlobal(active_canvas, top_left)
                _position.setX(_position.x() + _lastNeighborSize.width())
            case WidgetPadAlignment.TopRight:
                _position = self.mapToGlobal(active_canvas, top_right)
                _position.setX(_position.x() - _lastNeighborSize.width())
            case WidgetPadAlignment.BottomRight:
                _position = self.mapToGlobal(active_canvas, bottom_right)
                _position.setX(_position.x() - _lastNeighborSize.width())
            case WidgetPadAlignment.BottomLeft:
                _position = self.mapToGlobal(active_canvas, bottom_left)
                _position.setX(_position.x() + _lastNeighborSize.width())
            case WidgetPadAlignment.TopCenter:
                _position = self.mapToGlobal(active_canvas, top_center)
                _position.setY(_position.y() + _lastNeighborSize.height())
            case WidgetPadAlignment.BottomCenter:
                _position = self.mapToGlobal(active_canvas, bottom_center)
                _position.setY(_position.y() - _lastNeighborSize.height())
            case WidgetPadAlignment.MidLeft:
                _position = self.mapToGlobal(active_canvas, mid_left)
                _position.setX(_position.x() + _lastNeighborSize.width())
            case WidgetPadAlignment.MidRight:
                _position = self.mapToGlobal(active_canvas, mid_right)
                _position.setX(_position.x() - _lastNeighborSize.width())
            case _:
                _position = self.mapToGlobal(active_canvas, QPoint(0,0))

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