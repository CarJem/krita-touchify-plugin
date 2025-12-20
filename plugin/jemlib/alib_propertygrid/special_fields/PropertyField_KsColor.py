from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.alib_datatypes.TypedList import *
from jemlib.managers.IconRepository import *
from jemlib.alib_propertygrid.utils.PropertyUtils_Extensions import *
from jemlib.alib_propertygrid.PropertyGrid import *
from jemlib.alib_propertygrid.fields.PropertyField import *
from jemlib.alib_kis.dataclass.KisColor import KisColor
from jemlib.alib_widgets.buttons.ColorButton import ColorButton

class PropertyField_KsColor(PropertyField):
    def __init__(self, variable_name=str, variable_data=KisColor, variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)
        
        self.editor = ColorButton(self)
        self.editor.setColor(variable_data.toQt())
        self.editor.colorChanged.connect(self.updateColor)
        
        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def updateColor(self):
        self.variable_data = KisColor.fromQt(self.editor.color())
        super().setVariable(self.variable_source, self.variable_name, self.variable_data)
