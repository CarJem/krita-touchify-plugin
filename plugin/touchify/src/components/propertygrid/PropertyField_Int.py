from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET
from ..extras.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from ...ext.typedlist import *
from ...resources import *
from ...ext.extensions import KritaExtensions
from ..CollapsibleBox import CollapsibleBox

from .PropertyGridExtensions import *
from .PropertyGrid import *
from .PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from .PropertyField import *


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum


class PropertyField_Int(PropertyField):
    def __init__(self, variable_name=str, variable_data=int, variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)
        
        self.editor = QSpinBox()
        self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
        self.editor.setMaximum(2147483647)
        self.editor.setMinimum(-2147483648)
        self.editor.valueChanged.connect(self.updateValue)
        self.editor.setValue(self.variable_data)

        restric_func = PropertyGridExtensions.getVariable(self.variable_source, "propertygrid_restrictions")
        if callable(restric_func):
            restrictions = restric_func()
            if variable_name in restrictions:
                if restrictions[variable_name]["type"] == "range":
                    self.editor.setMinimum(restrictions[variable_name]["min"])
                    self.editor.setMaximum(restrictions[variable_name]["max"])
        
        editorLayout = QHBoxLayout()
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def updateValue(self):
        self.variable_data = self.editor.value()
        PropertyGridExtensions.setVariable(self.variable_source, self.variable_name, self.variable_data)
