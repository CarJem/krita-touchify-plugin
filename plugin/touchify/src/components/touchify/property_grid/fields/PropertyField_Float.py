from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from touchify.src.components.pyqt.event_filters.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from touchify.src.ext.types.TypedList import *
from touchify.src.resources import *

from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import *
from touchify.src.components.touchify.property_grid.PropertyGrid import *
from touchify.src.components.touchify.property_grid.fields.PropertyField import *




class PropertyField_Float(PropertyField):
    def __init__(self, variable_name=str, variable_data=float, variable_source=any):
        super().__init__(variable_name, variable_data, variable_source, True)
        
        self.editor = QDoubleSpinBox()
        self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
        self.editor.setMaximum(sys.float_info.max)
        self.editor.setMinimum(sys.float_info.min)
        self.editor.valueChanged.connect(self.updateValue)
        self.editor.setValue(self.variable_data)

        restrictions = PropertyUtils_Extensions.classRestrictions(self.variable_source, variable_name)
        for restriction in restrictions:
            if restriction["type"] == "range":
                if "min" in restriction:
                    self.editor.setMinimum(restriction["min"])
                if "max" in restriction:
                    self.editor.setMaximum(restriction["max"])
        
        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def updateValue(self):
        self.variable_data = self.editor.value()
        super().setVariable(self.variable_source, self.variable_name, self.variable_data)
