from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from jemlib.alib_propertygrid.event_filters.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from jemlib.alib_datatypes.TypedList import *
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.managers.IconRepository import *


from jemlib.alib_propertygrid.PropertyGrid import *
from jemlib.alib_propertygrid.fields.PropertyField import *

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class PropertyField_Int(PropertyField[int]):
    def __init__(self, handler: "DataHandler", property: DataPath[int]):
        super().__init__(handler, property, True)
        
        self.editor = QSpinBox(self)
        self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
        self.editor.setMaximum(2147483647)
        self.editor.setMinimum(-2147483648)
        self.editor.valueChanged.connect(self.updateValue)
        self.editor.setValue(self.propertyData.variableData())

        restrictions = self.praser.getObjectConstraints(self.propertyData)
        for restriction in restrictions:
            if restriction["type"] == DataConstraints.NumberMod.Range:
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
        new_data = self.editor.value()
        super().setVariable(new_data)