from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from touchify.src.components.pyqt.event_filters.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from touchify.src.ext.types.TypedList import *
from touchify.src.resources import *

from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import *
from touchify.src.components.touchify.property_grid.PropertyGrid import *
from touchify.src.components.touchify.property_grid.fields.PropertyField import *



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

        restrictions = PropertyUtils_Extensions.classRestrictions(self.variable_source)
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