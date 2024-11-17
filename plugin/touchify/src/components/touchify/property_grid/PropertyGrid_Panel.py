from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.property_grid.PropertyGrid import PropertyGrid
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
        self.labels: dict[str, QWidget] = {}
        

        self.stackHost = parentStack
        self.formWidget = QWidget(self)
        self.formWidget.setContentsMargins(0,0,0,0)
        self.formLayout = QFormLayout()
        self.formLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.formLayout.setSpacing(0)
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.formLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
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
    
    def createRow(self, item: any, varName: str, layout: QFormLayout, labelData: dict, sisterData: dict):

        def getFieldText(field: PropertyField):
            resultText = field.labelText
            if field.labelText in labelData:
                propData = labelData[field.labelText]
                if propData != None:
                    resultText = propData
            return resultText

        def createDataRow(_varName: str):
            variable = PropertyUtils_Extensions.getVariable(item, _varName)
            field = PropertyUtils_Praser.getPropertyType(_varName, variable, item)
            field.propertyChanged.connect(self.onPropertyChanged)
            field.setStackHost(self.stackHost)
            if field:
                self.fields.append(field)
                field.setSizePolicy(ROW_SIZE_POLICY_X, ROW_SIZE_POLICY_Y)
                return field
            return None
        
        def createSisDataRow(field: PropertyField, sister_fields: list[PropertyField]):
            row_fields = QWidget(self)
            row_fields.setContentsMargins(0,0,0,0)
            
            fields_layout = QHBoxLayout(self)
            fields_layout.setContentsMargins(0,0,0,0)
            fields_layout.setSpacing(0)
            fields_layout.addWidget(field)
            for sis_field in sister_fields:
                fields_layout.addWidget(sis_field)
            row_fields.setLayout(fields_layout)
            return row_fields
        
        def createLabelRow(resultText: str):
            header = QLabel()
            header.setText(resultText)
            header.setMargin(0)
            header.setContentsMargins(5,0,5,0)
            return header
        
        def createSisLabelRow(field: PropertyField, _sisters: list):
            headerText = getFieldText(field)
            if varName in sisterData:
                headerText = sisterData[varName]["name"]
            
            return createLabelRow(headerText)

        def populateSisDataRows():
            sister_fields = []
            if varName in sisterData:
                data = sisterData[varName]
                for sisterName in list[str](data["items"]):
                    sisterField = createDataRow(sisterName)
                    if sisterField:
                        sister_fields.append(sisterField)
            return sister_fields

        field = createDataRow(varName)
        if field:
            sisters = populateSisDataRows()
            if len(sisters) == 0:
                header = createLabelRow(getFieldText(field))
                self.labels[field.variable_name] = header
                layout.addRow(header, field)
            else:
                header = createSisLabelRow(field, sisters)
                self.labels[field.variable_name] = header
                sister_field = createSisDataRow(field, sisters)
                layout.addRow(header, sister_field)

    def updateVisibility(self):
        if self.item == None:
            return
        
        hiddenItems = PropertyUtils_Extensions.getHidden(self.currentData())
        hiddenItems.append("json_version")
        for field in self.fields:     
            if field.variable_name in hiddenItems:
                field.setHidden(True)
                if field.variable_name in self.labels:
                    self.labels[field.variable_name].setHidden(True)
            else:
                field.setHidden(False)
                if field.variable_name in self.labels:
                    self.labels[field.variable_name].setHidden(False)

    def updateDataObject(self, item):
        self.item = item
        self.fields.clear()
        self.labels.clear()
        PropertyUtils_Extensions.clearLayout(self.formLayout)
        sisterData = PropertyUtils_Extensions.getSisters(item)
        labelData = PropertyUtils_Extensions.getLabels(item)

        claimedSections = []
        claimedSisters = []
        sisterParentData = {}

        for sisterId in sisterData:
            sisterName = sisterData[sisterId]["name"]
            sisterItems = list[str](sisterData[sisterId]["items"])
            
            if len(sisterItems) >= 2:
                firstItem = sisterItems.pop(0)
                sisterParentData[firstItem] = {
                    "name": sisterName,
                    "items": sisterItems
                }

                for varName in sisterItems:
                    claimedSisters.append(varName)

        for varName in PropertyUtils_Extensions.getClassVariables(item):
            if varName not in claimedSections and varName not in claimedSisters:
                self.createRow(item, varName, self.formLayout, labelData, sisterParentData)

        self.updateVisibility()
