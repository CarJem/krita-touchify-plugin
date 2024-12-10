from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.ext.types.TypedList import *
from touchify.src.resources import *

from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import *
from touchify.src.components.touchify.property_grid.PropertyGrid import *
from touchify.src.components.touchify.property_grid.fields.PropertyField import *



class PropertyField_Bool(PropertyField):
    def __init__(self, variable_name=str, variable_data=bool, variable_source=any):
        super().__init__(variable_name, variable_data, variable_source, True)
        self.setMaximumWidth(20)
        self.setMinimumWidth(20)
        
        
        self.editor = QCheckBox(self)
        self.editor.stateChanged.connect(self.updateChecked)
        self.editor.setChecked(self.variable_data)
        
        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def updateChecked(self):
        self.variable_data = self.editor.isChecked()
        super().setVariable(self.variable_source, self.variable_name, self.variable_data)
