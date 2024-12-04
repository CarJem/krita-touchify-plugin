from PyQt5 import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget

from touchify.src.components.touchify.property_grid.PropertyGrid import PropertyGrid
from touchify.src.components.touchify.property_grid.fields.PropertyLabel import PropertyLabel
from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import *
from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Praser import *
from touchify.src.components.touchify.property_grid.dialogs.PropertyGrid_SelectorDialog import *


from touchify.src.ext.types.TypedList import *
from touchify.src.resources import *


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum


class PropertyGrid_Panel(QScrollArea):


    def __init__(self, parentStack: PropertyGrid):
        super().__init__()

        self.fields: list[PropertyField] = []
        self.labels: list[PropertyGrid_Panel.Label] = []
        

        self.stackHost = parentStack
        self.formWidget = QWidget(self)
        self.formWidget.setContentsMargins(0,0,0,0)

        self.formLayout = QFormLayout()
        self.formLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.formLayout.setSpacing(0)
        self.formLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.formWidget.setLayout(self.formLayout)
        self.setWidget(self.formWidget)

    def currentData(self):
        field: PropertyField
        newItem = self.item
        for field in self.fields:
            name, data, source = field.getFieldData()
            PropertyUtils_Extensions.setVariable(newItem, name, data)
        return newItem
    
    def onPropertyChanged(self, value: bool):
        self.updateVisibility()

    def updateVisibility(self):
        if self.item == None:
            return
        
        hiddenItems = PropertyUtils_Extensions.classHiddenVariables(self.currentData())
        hiddenItems.append("json_version")

        for field in self.fields:     
            if field.variable_name in hiddenItems: field.setHidden(True)
            else: field.setHidden(False)

        for label in self.labels:     
            if label.variable_name in hiddenItems: label.setHidden(True)
            else: label.setHidden(False)

    def createLabel(self, varName: str, labelData: dict, hintData: dict, is_nested: bool = False):
        labelText = PropertyUtils_Extensions.getVariableLabel(labelData, varName)
        hintText = PropertyUtils_Extensions.getVariableHint(hintData, varName)
        header = PropertyLabel(varName, labelText, hintText, is_nested)
        self.labels.append(header)
        return header
    
    def createField(self, source: any, _varName: str):
        variable = PropertyUtils_Extensions.getVariable(source, _varName)
        field = PropertyUtils_Praser.getPropertyType(_varName, variable, source)
        field.propertyChanged.connect(self.onPropertyChanged)
        field.setStackHost(self.stackHost)
        if field:
            self.fields.append(field)
            field.setSizePolicy(ROW_SIZE_POLICY_X, ROW_SIZE_POLICY_Y)
            return field
        return None

    def createSisterField(self, source: any, sister_data: dict[str, any], labelData: dict, hintData: dict):
        sister_items = list[str](sister_data["items"])

        use_labels: bool = False
        if "use_labels" in sister_data:
            use_labels = bool(sister_data["use_labels"])
        

        sister_field = QWidget(self)
        sister_field.setContentsMargins(0,0,0,0)
        
        if use_labels:
            layout = QVBoxLayout(sister_field)
            layout.setContentsMargins(0,0,0,0)
            layout.setSpacing(0)
        else:
            layout = QHBoxLayout(sister_field)
            layout.setContentsMargins(0,0,0,0)
            layout.setSpacing(0)

        for index, variable_name in enumerate(sister_items):
            field = self.createField(source, variable_name)

            if use_labels:
                sub_layout = QHBoxLayout()
                sub_layout.setContentsMargins(0,0,0,0)
                sub_layout.setSpacing(0)
                
                header = self.createLabel(variable_name, labelData, hintData, True)
                field.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                sub_layout.addWidget(field)
                sub_layout.addWidget(header,1)
                layout.addLayout(sub_layout)
            else:
                layout.addWidget(field, 1)

        return sister_field

    def updateDataObject(self, item):
        self.item = item
        self.fields.clear()
        self.labels.clear()
        
        PropertyUtils_Extensions.clearLayout(self.formLayout)
        labelData = PropertyUtils_Extensions.classVariableLabels(item)
        hintData = PropertyUtils_Extensions.classVariableHints(item)

        sister_data = PropertyUtils_Extensions.classSisters(item)
        variable_data = PropertyUtils_Extensions.getClassVariables(item)

        known_sisters = []

        for sister_id in sister_data:
            sister_id: str
            sister_items = list[str](sister_data[sister_id]["items"])
            known_sisters.append(str(sister_id))
            for sister_variable in sister_items:
                if sister_id not in variable_data:
                    index = variable_data.index(str(sister_variable))
                    variable_data.insert(index, str(sister_id))
                variable_data.remove(sister_variable)

        for variable_id in variable_data:    
            variable_id: str     
            if variable_id in known_sisters:
                sister_info = sister_data[variable_id]
                header = self.createLabel(variable_id, labelData, hintData)
                header.setFixedWidth(200)
                field = self.createSisterField(item, sister_info, labelData, hintData)
                self.formLayout.addRow(header, field)
            else:
                header = self.createLabel(variable_id, labelData, hintData)
                header.setFixedWidth(200)
                field = self.createField(item, variable_id)
                self.formLayout.addRow(header, field)

        self.updateVisibility()
