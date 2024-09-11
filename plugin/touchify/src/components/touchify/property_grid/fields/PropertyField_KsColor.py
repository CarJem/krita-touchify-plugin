from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET
from ....pyqt.event_filters.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from .....ext.TypedList import *
from .....resources import *
from .....ext.extensions_krita import KritaExtensions
from ....pyqt.widgets.CollapsibleBox import CollapsibleBox

from ..utils.PropertyUtils_Extensions import *
from ..PropertyGrid import *
from ..dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from .PropertyField import *
from .....ext.KritaSettings import KS_Color
from ....pyqt.widgets.ColorButton import ColorButton


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

class PropertyField_KsColor(PropertyField):
    def __init__(self, variable_name=str, variable_data=KS_Color, variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)
        
        self.editor = ColorButton(self)
        self.editor.setColor(variable_data.toQt())
        self.editor.colorChanged.connect(self.updateColor)
        
        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def updateColor(self):
        self.variable_data = KS_Color.fromQt(self.editor.color())
        super().setVariable(self.variable_source, self.variable_name, self.variable_data)
