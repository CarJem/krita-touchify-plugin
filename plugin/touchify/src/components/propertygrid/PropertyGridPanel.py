from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET

from .PropertyGrid import PropertyGrid
from .PropertyUtils_Extensions import *
from .PropertyUtils_Praser import *
from .PropertyGrid_SelectorDialog import *

from ..extras.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from ...ext.typedlist import *
from ...resources import *
from ...ext.extensions import KritaExtensions
from ..CollapsibleBox import CollapsibleBox


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum


class PropertyGridPanel(QScrollArea):
    fields: list[PropertyField] = []

    def __init__(self, parentStack: PropertyGrid):
        super().__init__()
        

        self.stackHost = parentStack
        self.formWidget = QWidget()
        self.formWidget.setContentsMargins(0,0,0,0)
        self.formLayout = QVBoxLayout()
        self.formLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.formLayout.setSpacing(0)
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
    

    def createDataRow(self, item, varName):
        variable = PropertyUtils_Extensions.getVariable(item, varName)
        field = PropertyUtils_Praser.getPropertyType(varName, variable, item)
        field.setStackHost(self.stackHost)
        if field:
            self.fields.append(field)
            field.setSizePolicy(ROW_SIZE_POLICY_X, ROW_SIZE_POLICY_Y)
            return field
        return None
    
    def createLabelRow(self, layout: QLayout, field: PropertyField, labelData: dict):

        resultText = field.labelText


        if field.labelText in labelData:
            propData = labelData[field.labelText]
            if propData == None:
                return
            resultText = propData

        header = QLabel()
        header.setText(resultText)
        header.setMargin(0)
        header.setContentsMargins(0,0,0,0)
        layout.addWidget(header)
    
    
    def updateDataObject(self, item):
        self.item = item
        self.fields.clear()
        PropertyUtils_Extensions.clearLayout(self.formLayout)
        groupData = PropertyUtils_Extensions.getGroups(item)
        labelData = PropertyUtils_Extensions.getLabels(item)
        claimedSections = []

        for groupId in groupData:
            groupName = groupData[groupId]["name"]
            groupItems = list(groupData[groupId]["items"])
            for varName in groupItems:
                claimedSections.append(varName)

        for varName in PropertyUtils_Extensions.getClassVariables(item):
            if varName not in claimedSections:
                field = self.createDataRow(item, varName)
                if field:
                    self.createLabelRow(self.formLayout, field, labelData)
                    self.formLayout.addWidget(field)

        
        for groupId in groupData:
            groupName = groupData[groupId]["name"]
            groupItems = list(groupData[groupId]["items"])
            section = CollapsibleBox(groupName, self.formWidget)
            sectionLayout = QVBoxLayout()
            sectionLayout.setSpacing(0)
            sectionLayout.setContentsMargins(0,0,0,0)
            section.setSizePolicy(GROUP_SIZE_POLICY_X, GROUP_SIZE_POLICY_Y)

            for varName in groupItems:
                field = self.createDataRow(item, varName)
                if field:
                    self.createLabelRow(sectionLayout, field, labelData)
                    sectionLayout.addWidget(field)

            section.setContentLayout(sectionLayout)

            self.formLayout.addWidget(section)
