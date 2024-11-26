from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.ext.types.TypedList import *
from touchify.src.resources import *

from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import *
from touchify.src.components.touchify.property_grid.PropertyGrid import *
from touchify.src.components.touchify.property_grid.fields.PropertyField import *
from touchify.src.ext.KritaSettings import KS_Color
from touchify.src.components.pyqt.widgets.ColorButton import ColorButton




class PropertyField_KsColor(PropertyField):
    def __init__(self, variable_name=str, variable_data=KS_Color, variable_source=any):
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
        self.variable_data = KS_Color.fromQt(self.editor.color())
        super().setVariable(self.variable_source, self.variable_name, self.variable_data)
