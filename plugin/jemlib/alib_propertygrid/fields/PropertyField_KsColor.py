from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.alib_datatypes.TypedList import *
from jemlib.managers.IconRepository import *
from jemlib.alib_propertygrid.PropertyGrid import *
from jemlib.alib_propertygrid.fields.PropertyField import *
from jemlib.alib_kis.dataclass.KisColor import KisColor
from jemlib.alib_widgets.buttons.ColorButton import ColorButton

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class PropertyField_KsColor(PropertyField[KisColor]):
    def __init__(self, handler: "DataHandler", property: DataPath[KisColor]):
        super().__init__(handler, property, True)
        
        self.editor = ColorButton(self)
        self.editor.setColor(self.propertyData.variableData().toQt())
        self.editor.colorChanged.connect(self.updateColor)
        
        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def updateColor(self):
        newData = KisColor.fromQt(self.editor.color())
        super().setVariable(newData)
