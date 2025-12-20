from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.alib_datatypes.TypedList import *
from jemlib.managers.IconRepository import *


from jemlib.alib_propertygrid.PropertyGrid import *
from jemlib.alib_propertygrid.fields.PropertyField import *

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class PropertyField_Bool(PropertyField[bool]):
    def __init__(self, handler: "DataHandler", property: DataPath[bool]):
        super().__init__(handler, property, True)
        self.setMaximumWidth(20)
        self.setMinimumWidth(20)
        
        
        self.editor = QCheckBox(self)
        self.editor.stateChanged.connect(self.updateChecked)
        self.editor.setChecked(self.propertyData.variableData())
        
        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def updateChecked(self):
        new_data = self.editor.isChecked()
        super().setVariable(new_data)
