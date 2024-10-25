# This Python file uses the following encoding: utf-8
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from krita import *


from .....variables import *
from .ToolboxWidget import ToolboxWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....extension import TouchifyExtension

TOOLBOX_ITEMS: dict[str, str] = {
        "KisToolTransform": "KisToolTransform",
        "KritaTransform/KisToolMove": "KritaTransform/KisToolMove",
        "KisToolCrop": "KisToolCrop",
        "InteractionTool": "InteractionTool",
        "SvgTextTool": "SvgTextTool",
        "PathTool": "PathTool",
        "KarbonCalligraphyTool": "KarbonCalligraphyTool",
        "KritaShape/KisToolBrush": "KritaShape/KisToolBrush",
        "KritaShape/KisToolDyna": "KritaShape/KisToolDyna",
        "KritaShape/KisToolMultiBrush": "KritaShape/KisToolMultiBrush",
        "KritaShape/KisToolSmartPatch": "KritaShape/KisToolSmartPatch",
        "KisToolPencil": "KisToolPencil",
        "KritaFill/KisToolFill": "KritaFill/KisToolFill",
        "KritaSelected/KisToolColorSampler": "KritaSelected/KisToolColorPicker",
        "KritaShape/KisToolLazyBrush": "KritaShape/KisToolLazyBrush",
        "KritaFill/KisToolGradient": "KritaFill/KisToolGradient",
        "KritaShape/KisToolRectangle": "KritaShape/KisToolRectangle",
        "KritaShape/KisToolLine": "KritaShape/KisToolLine",
        "KritaShape/KisToolEllipse": "KritaShape/KisToolEllipse",
        "KisToolPolygon": "KisToolPolygon",
        "KisToolPolyline": "KisToolPolyline",
        "KisToolPath": "KisToolPath",
        "KisToolEncloseAndFill": "KisToolEncloseAndFill",
        "KisToolSelectRectangular": "KisToolSelectRectangular",
        "KisToolSelectElliptical": "KisToolSelectElliptical",
        "KisToolSelectPolygonal": "KisToolSelectPolygonal",
        "KisToolSelectPath": "KisToolSelectPath",
        "KisToolSelectOutline": "KisToolSelectOutline",
        "KisToolSelectContiguous": "KisToolSelectContiguous",
        "KisToolSelectSimilar": "KisToolSelectSimilar",
        "KisToolSelectMagnetic": "KisToolSelectMagnetic",
        "ToolReferenceImages": "ToolReferenceImages",
        "KisAssistantTool": "KisAssistantTool",
        "KritaShape/KisToolMeasure": "KritaShape/KisToolMeasure",
        "PanTool": "PanTool",
        "ZoomTool": "ZoomTool"
}

class ToolboxDocker(QDockWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.floating = False
        self.setWindowTitle('Touchify Toolbox') # window title also acts as the Docker title in Settings > Dockers
        self.setContentsMargins(0,0,0,0)

        label = QLabel(" ") # label conceals the 'exit' buttons and Docker title
        label.setFrameShape(QFrame.StyledPanel)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameStyle(QFrame.Panel | QFrame.Raised)
        label.setMinimumWidth(16)

        self.toolboxWidget = ToolboxWidget(self)
        self.setWidget(self.toolboxWidget)

    def onConfigUpdated(self):
        self.toolboxWidget.reload()

    def setup(self, instance: "TouchifyExtension.TouchifyWindow"):
        self.toolboxWidget.setup(instance)