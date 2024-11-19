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
    
    def createRow(self, item: any, varName: str, layout: QFormLayout, labelData: dict, hintData: dict, sisterData: dict):

        def getDisplayText(variable_name: str):
            resultText = variable_name
            if variable_name in labelData:
                propData = labelData[variable_name]
                if propData != None:
                    resultText = propData
            return resultText
        
        def getHintText(variable_name: str):
            hintText = ""
            if variable_name in hintData:
                hintText = str(hintData[variable_name])
            return hintText

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
        
        def createLabelRow(resultText: str, hintText: str):

            def showHint():
                QToolTip.showText(hintLabel.mapToGlobal(QPoint(0,0)), hintText)

            header = QWidget()
            header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            header.setContentsMargins(0,0,0,0)

            layout = QHBoxLayout(header)
            layout.setSpacing(0)
            layout.setContentsMargins(0,0,0,0)

            leadingLine = QFrame(header)
            leadingLine.setLineWidth(1)
            leadingLine.setMaximumWidth(10)
            leadingLine.setContentsMargins(2,0,2,0)
            leadingLine.setFrameShape(QFrame.Shape.HLine)
            leadingLine.setFrameShadow(QFrame.Shadow.Sunken)
            layout.addWidget(leadingLine, 1)

            label = QLabel(header)
            label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            label.setMargin(0)
            label.setContentsMargins(2,0,2,0)
            label.setText(resultText)
            layout.addWidget(label)

            trailingLine = QFrame(header)
            trailingLine.setLineWidth(1)
            trailingLine.setContentsMargins(2,0,2,0)
            trailingLine.setFrameShape(QFrame.Shape.HLine)
            trailingLine.setFrameShadow(QFrame.Shadow.Sunken)
            layout.addWidget(trailingLine, 1)

            if hintText != "":
                hintLabel = QPushButton(header)
                hintLabel.setFlat(True)
                hintLabel.clicked.connect(showHint)
                hintLabel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                hintLabel.setIcon(ResourceManager.iconLoader("material:information-variant"))
                hintLabel.setToolTip(hintText)
                layout.addWidget(hintLabel)


            return header

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
                header = createLabelRow(getDisplayText(varName), getHintText(varName))
                self.labels[field.variable_name] = header
                layout.addRow(header)
                layout.addRow(field)
            else:
                sister_id = sisterData[varName]["sister_id"]
                header = createLabelRow(getDisplayText(sister_id), getHintText(sister_id))
                self.labels[field.variable_name] = header
                sister_field = createSisDataRow(field, sisters)
                layout.addRow(header)
                layout.addRow(sister_field)

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
        hintData = PropertyUtils_Extensions.getHints(item)

        claimedSections = []
        claimedSisters = []
        sisterParentData = {}

        for sisterId in sisterData:
            sisterItems = list[str](sisterData[sisterId]["items"])
            
            if len(sisterItems) >= 2:
                firstItem = sisterItems.pop(0)
                sisterParentData[firstItem] = {
                    "items": sisterItems,
                    "sister_id": sisterId
                }

                for varName in sisterItems:
                    claimedSisters.append(varName)

        for varName in PropertyUtils_Extensions.getClassVariables(item):
            if varName not in claimedSections and varName not in claimedSisters:
                self.createRow(item, varName, self.formLayout, labelData, hintData, sisterParentData)

        self.updateVisibility()
