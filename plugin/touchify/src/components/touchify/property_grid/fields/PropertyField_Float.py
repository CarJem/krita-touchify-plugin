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


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

class PropertyField_Float(PropertyField):
    def __init__(self, variable_name=str, variable_data=float, variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)
        
        self.editor = QDoubleSpinBox()
        self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
        self.editor.setMaximum(sys.float_info.max)
        self.editor.setMinimum(sys.float_info.min)
        self.editor.valueChanged.connect(self.updateValue)
        self.editor.setValue(self.variable_data)

        restrictions = PropertyUtils_Extensions.getRestrictions(self.variable_source)
        if variable_name in restrictions:
            if restrictions[variable_name]["type"] == "range":
                if "min" in restrictions[variable_name]:
                    self.editor.setMinimum(restrictions[variable_name]["min"])
                if "max" in restrictions[variable_name]:
                    self.editor.setMaximum(restrictions[variable_name]["max"])
        
        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def updateValue(self):
        self.variable_data = self.editor.value()
        super().setVariable(self.variable_source, self.variable_name, self.variable_data)
