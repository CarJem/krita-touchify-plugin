from enum import IntEnum
from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from touchify.src.api_krita import KritaAPI

from touchify.src.managers.GlobalEvents import GlobalEvents
from touchify.src.settings.TouchifySettings import TouchifySettings
from touchify.__env__ import *

from touchify.src.extensions.krita_extensions import *

if TYPE_CHECKING:
    from ..PluginManagers import TouchifyManagers
    from touchify.src.components.toolshelf.ToolshelfDockerWidgetPad import ToolshelfDockerWidgetPad



    
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
        self.WIDGETPAD_DIRECTIONS: dict[int, list["ToolshelfDockerWidgetPad"]] = {}

    def updateNeighbors(self, alignKey: Alignment):
        if alignKey not in self.WIDGETPAD_DIRECTIONS:
            self.WIDGETPAD_DIRECTIONS[alignKey] = []
    
        self.WIDGETPAD_DIRECTIONS[alignKey].sort(key=lambda x: x._priority, reverse=False)
        for i, j in enumerate(self.WIDGETPAD_DIRECTIONS[alignKey]):
            if i == 0: 
                j.setNeighbor(None)
            else: 
                j.setNeighbor(self.WIDGETPAD_DIRECTIONS[alignKey][i-1])

    def movePadTo(self, src: "ToolshelfDockerWidgetPad", alignFrom: Alignment, alignTo: Alignment):
        if alignFrom == alignTo:
            return

        if alignFrom not in self.WIDGETPAD_DIRECTIONS:
            self.WIDGETPAD_DIRECTIONS[alignFrom] = []
        
        if src in self.WIDGETPAD_DIRECTIONS[alignFrom]:
            self.WIDGETPAD_DIRECTIONS[alignFrom].remove(src)
        

        if alignTo not in self.WIDGETPAD_DIRECTIONS:
            self.WIDGETPAD_DIRECTIONS[alignTo] = []

        self.WIDGETPAD_DIRECTIONS[alignTo].append(src)
        self.updateNeighbors(alignFrom)
        self.updateNeighbors(alignTo)

WidgetPadAlignment = WidgetPadManager.Alignment