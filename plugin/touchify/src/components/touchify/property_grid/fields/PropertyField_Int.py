from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from touchify.src.components.touchify.property_grid.event_filters.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from touchify.src.datatypes.sequence.TypedList import *
from touchify.src.components.touchify.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions
from touchify.src.managers.shared.resources import *

from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import *
from touchify.src.components.touchify.property_grid.PropertyGrid import *
from touchify.src.components.touchify.property_grid.fields.PropertyField import *



class PropertyField_Int(PropertyField):
    def __init__(self, variable_name=str, variable_data=int, variable_source=any):
        super().__init__(variable_name, variable_data, variable_source, True)
        
        self.editor = QSpinBox(self)
        self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
        self.editor.setMaximum(2147483647)
        self.editor.setMinimum(-2147483648)
        self.editor.valueChanged.connect(self.updateValue)
        self.editor.setValue(self.variable_data)

        restrictions = PropertyUtils_Extensions.classRestrictions(self.variable_source, variable_name)
        for restriction in restrictions:
            if restriction["type"] == PropertyGrid_Restrictions.NumberMod.Range:
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