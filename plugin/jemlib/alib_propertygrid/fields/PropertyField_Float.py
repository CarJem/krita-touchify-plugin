from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from jemlib.alib_propertygrid.event_filters.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from jemlib.alib_datatypes.TypedList import *
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.managers.IconRepository import *


from jemlib.alib_propertygrid.PropertyGrid import *
from jemlib.alib_propertygrid.fields.PropertyField import *

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler


class PropertyField_Float(PropertyField[float]):
    def __init__(self, handler: "DataHandler", property: DataPath[float]):
        super().__init__(handler, property, True)
        
        self.editor = QDoubleSpinBox(self)
        self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
        self.editor.setMaximum(sys.float_info.max)
        self.editor.setMinimum(sys.float_info.min)

        restrictions = self.praser.getObjectConstraints(self.propertyData)
        for restriction in restrictions:
            if restriction["type"] == DataConstraints.NumberMod.Range:
                if "min" in restriction:
                    self.editor.setMinimum(restriction["min"])
                if "max" in restriction:
                    self.editor.setMaximum(restriction["max"])

        self.editor.valueChanged.connect(self.updateValue)
        self.editor.setValue(self.propertyData.variableData())
        
        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def updateValue(self):
        new_data = self.editor.value()
        super().setVariable(new_data)
