from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET
from ....extras.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from .....ext.TypedList import *
from .....resources import *
from .....ext.extensions_krita import KritaExtensions
from ....CollapsibleBox import CollapsibleBox

from ..utils.PropertyUtils_Extensions import *
from ..PropertyGrid import *
from ..dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from .PropertyField import *


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

class PropertyField_Bool(PropertyField):
    def __init__(self, variable_name=str, variable_data=bool, variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)
        
        self.editor = QCheckBox()
        self.editor.stateChanged.connect(self.updateChecked)
        self.editor.setChecked(self.variable_data)
        
        editorLayout = QHBoxLayout()
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def updateChecked(self):
        self.variable_data = self.editor.isChecked()
        super().setVariable(self.variable_source, self.variable_name, self.variable_data)
