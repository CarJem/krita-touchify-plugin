from PyQt5.QtWidgets import QMdiArea, QDockWidget
from PyQt5.QtCore import QObject, QEvent, QPoint

from ....ext.KritaSettings import KritaSettings

from ....docker_manager import DockerManager
from ....action_manager import ActionManager


from ....ext.extensions_krita import KritaExtensions
from ....settings.TouchifySettings import TouchifySettings
from ....settings.TouchifyConfig import TouchifyConfig
from ....stylesheet import Stylesheet
from .NtWidgetPad import NtWidgetPad
from krita import *
from ....variables import *
from ..dockers.toolshelf.ToolshelfDockWidget import ToolshelfDockWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .NtCanvas import NtCanvas

class NtToolshelf(NtWidgetPad):

    def __init__(self, canvas: "NtCanvas", window: Window, isPrimaryPanel: bool, docker_manager: DockerManager, actions_manager: ActionManager):
        super().__init__(window, canvas, True)   
        panel_index = 0 if isPrimaryPanel else 1

        self.toolshelf = ToolshelfDockWidget(panel_index, docker_manager, actions_manager)
        self.toolshelf.installEventFilter(self.adjustFilter)
        self.toolshelf.sizeChanged.connect(self.onSizeChanged)

        self.setObjectName("toolshelfPad")
        self.borrowDocker(self.toolshelf)

        toolshelf_cfg = TouchifyConfig.instance().getActiveToolshelf(panel_index)
        if toolshelf_cfg:
            if toolshelf_cfg.header_options:
                if toolshelf_cfg.header_options.default_to_resize_mode == True:
                    self.toggleResizing()

    def onSizeChanged(self):
        self.canvas.updateView()
    
    def close(self):
        self.toolshelf.sizeChanged.disconnect(self.onSizeChanged)
        self.toolshelf.removeEventFilter(self.adjustFilter)
        self.toolshelf.onUnload()
        result = super().close()
        self.toolshelf.close()
        return result

