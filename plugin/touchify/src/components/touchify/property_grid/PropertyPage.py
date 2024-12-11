from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.property_grid.PropertyGrid import PropertyGrid
from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import *
from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Praser import *
from touchify.src.components.touchify.property_grid.dialogs.PropertyGrid_SelectorDialog import *


from touchify.src.components.touchify.property_grid.views.PropertyView import PropertyView
from touchify.src.components.touchify.property_grid.views.PropertyView_Form import PropertyView_Form
from touchify.src.components.touchify.property_grid.views.PropertyView_Tabs import PropertyView_Tabs
from touchify.src.ext.types.TypedList import *
from touchify.src.resources import *


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum


class PropertyPage(QScrollArea):

    propertyChanged = pyqtSignal(bool)

    def __init__(self, parentStack: PropertyGrid):
        super().__init__()
        self.stackHost = parentStack
        self.current_view_type = "unloaded"

        self.override_view_type = False
        self.desired_view_type = "default"


        self.modifiers: dict[str, any] = {}
        self.limiters: list[str]  = []

        self.formWidget: PropertyView = None
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setContentsMargins(0,0,0,0)

    def updateView(self):
        if self.formWidget != None:
            self.deleteLater()
            self.formWidget = None

        match self.current_view_type:
            case "tabs":
                result = PropertyView_Tabs(self)
                self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            case "tabs_vertical":
                result = PropertyView_Tabs(self, True)
                self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            case _:
                result = PropertyView_Form(self)
        
        self.formWidget = result
        self.setWidget(self.formWidget)

    def setViewOverride(self, view_type: str):
        if view_type == "":
            self.override_view_type = False
            self.desired_view_type = "default"
        else:
            self.override_view_type = True
            self.desired_view_type = view_type

    def setModifiers(self, modifiers: dict[str, any] = {}):
        self.modifiers = modifiers

    def setLimiters(self, limiters: list[str] = []):
        self.limiters = limiters
            
    def setStackHost(self, host: PropertyGrid):
        self.stackHost = host
        if self.formWidget:
            self.formWidget.setStackHost(self.stackHost)

    def onPropertyChanged(self, value: bool):
        if self.formWidget:
            self.formWidget.onPropertyChanged(value)

        self.propertyChanged.emit(True)

    def updateDataObject(self, item):
        if self.override_view_type:
            view_type = self.desired_view_type
        else:
            view_type = PropertyUtils_Extensions.classViewType(item)

        if view_type != self.current_view_type:
            self.current_view_type = view_type
            self.updateView()
        self.formWidget.updateDataObject(item)

