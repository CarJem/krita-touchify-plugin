import typing
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import sys
import importlib.util
import inspect

from PyQt5.QtWidgets import QWidget
from ..classes.config import *
from ..classes.resources import *
from ..ext.extensions import *
import xml.etree.ElementTree as ET
import json

class ListPropertyFieldTempValue:

    __variable_name: any
    __variable_source: any
    __index: any
    
    def __init__(self, variable_data, variable_source, variable_name, index):
        self.value = variable_data
        self.__variable_name = variable_name
        self.__variable_source = variable_source
        self.__index = index

    #TODO: Implement Proper Restriction Handling for Values that are not sub classable
    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions

    #TODO: This does not actually work at all
    def updateData(self):
        new_array = Extensions.getVariable(self.__variable_source, self.__variable_name)
        self.variable_data = self.value
        new_array[self.__index] = self.value
        Extensions.setVariable(self.__variable_source, self.__variable_name, new_array)
        


#region Property Fields

class PropertyField(QWidget):

    labelText: str
    variable_data: any

    def __init__(self, variable_name=str, variable_data=any, variable_source=any):
        super().__init__()
        self.setup(variable_name, variable_data, variable_source)

    def getFieldData(self):
         return [self.variable_name, self.variable_data, self.variable_source]
         
    def setup(self, variable_name=str, variable_data=any, variable_source=any):
        self.variable_name = variable_name
        self.variable_data = variable_data
        self.variable_source = variable_source

        self.labelText = self.variable_name
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)

    def getPropertyType(varName, variable, item):
        varType = type(variable)
        if varType == str:
            return StrPropertyField(varName, variable, item)
        elif varType == int:
            return IntPropertyField(varName, variable, item)
        elif varType == float:
            return FloatPropertyField(varName, variable, item)            
        elif varType == bool:
            return BoolPropertyField(varName, variable, item)
        elif varType == list:
            return ListPropertyField(varName, variable, item)
        else:
            return PropertyField(varName, variable, item)

class StrPropertyField(PropertyField):
        def __init__(self, variable_name=str, variable_data=str, variable_source=any):
            super(PropertyField, self).__init__()
            self.setup(variable_name, variable_data, variable_source)

            self.editor = QLineEdit()
            self.editor.textChanged.connect(self.textChanged)
            self.editor.setText(self.variable_data.replace("\n", "\\n"))

            editorLayout = QHBoxLayout()
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)

        def textChanged(self):
            self.variable_data = self.editor.text().replace("\\n", "\n")
            Extensions.setVariable(self.variable_source, self.variable_name, self.variable_data)

class IntPropertyField(PropertyField):
        def __init__(self, variable_name=str, variable_data=int, variable_source=any):
            super(PropertyField, self).__init__()
            self.setup(variable_name, variable_data, variable_source)
            
            self.editor = QSpinBox()
            self.editor.setMaximum(2147483647)
            self.editor.setMinimum(-2147483648)
            self.editor.valueChanged.connect(self.updateValue)
            self.editor.setValue(self.variable_data)

            restric_func = Extensions.getVariable(self.variable_source, "propertygrid_restrictions")
            if callable(restric_func):
                restrictions = restric_func()
                if variable_name in restrictions:
                    if restrictions[variable_name]["type"] == "range":
                        self.editor.setMinimum(restrictions[variable_name]["min"])
                        self.editor.setMaximum(restrictions[variable_name]["max"])
            
            editorLayout = QHBoxLayout()
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)

        def updateValue(self):
             self.variable_data = self.editor.value()
             Extensions.setVariable(self.variable_source, self.variable_name, self.variable_data)

class FloatPropertyField(PropertyField):
        def __init__(self, variable_name=str, variable_data=float, variable_source=any):
            super(PropertyField, self).__init__()
            self.setup(variable_name, variable_data, variable_source)
            
            self.editor = QDoubleSpinBox()
            self.editor.setMaximum(sys.float_info.max)
            self.editor.setMinimum(sys.float_info.min)
            self.editor.valueChanged.connect(self.updateValue)
            self.editor.setValue(self.variable_data)

            restric_func = Extensions.getVariable(self.variable_source, "propertygrid_restrictions")
            if callable(restric_func):
                restrictions = restric_func()
                if variable_name in restrictions:
                    if restrictions[variable_name]["type"] == "range":
                        self.editor.setMinimum(restrictions[variable_name]["min"])
                        self.editor.setMaximum(restrictions[variable_name]["max"])
            
            editorLayout = QHBoxLayout()
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)

        def updateValue(self):
             self.variable_data = self.editor.value()
             Extensions.setVariable(self.variable_source, self.variable_name, self.variable_data)

class BoolPropertyField(PropertyField):
        def __init__(self, variable_name=str, variable_data=bool, variable_source=any):
            super(PropertyField, self).__init__()
            self.setup(variable_name, variable_data, variable_source)
            
            self.editor = QCheckBox()
            self.editor.stateChanged.connect(self.updateChecked)
            self.editor.setChecked(self.variable_data)
            
            editorLayout = QHBoxLayout()
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)

        def updateChecked(self):
             self.variable_data = self.editor.isChecked()
             Extensions.setVariable(self.variable_source, self.variable_name, self.variable_data)

class ListPropertyField(PropertyField):
        def __init__(self, variable_name=str, variable_data=list, variable_source=any):
            super(PropertyField, self).__init__()
            self.setup(variable_name, variable_data, variable_source)
            
            field = QHBoxLayout()
            list = QListView()

            btns = QVBoxLayout()
            btn_width = 20

            model = QtGui.QStandardItemModel()

            for i in variable_data:
                item = QtGui.QStandardItem(str(i))
                model.appendRow(item)

            list.setModel(model)
            field.addWidget(list)
            field.addLayout(btns)

            addButton = QPushButton()
            addButton.setText("+")
            addButton.setFixedWidth(btn_width)
            btns.addWidget(addButton)

            removeButton = QPushButton()
            removeButton.setText("-")
            removeButton.setFixedWidth(btn_width)
            btns.addWidget(removeButton)

            moveUpButton = QPushButton()
            moveUpButton.setText("↑")
            moveUpButton.setFixedWidth(btn_width)
            btns.addWidget(moveUpButton)

            moveDownButton = QPushButton()
            moveDownButton.setText("↓")
            moveDownButton.setFixedWidth(btn_width)
            btns.addWidget(moveDownButton)

            editButton = QPushButton()
            editButton.setText("...")
            editButton.setFixedWidth(btn_width)
            editButton.clicked.connect(self.editItem)
            btns.addWidget(editButton)

            selection_model = list.selectionModel()
            selection_model.currentChanged.connect(lambda x, y: self.updateSelected(x, y))
    
            self.setLayout(field)

        def editItem(self):
            dlg = QDialog()
            container = QVBoxLayout()
            dlg.setFixedSize(800,400)
            dlg.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            dlg.btns.accepted.connect(dlg.accept)
            dlg.btns.accepted.connect(self.itemEditUpdate)
            dlg.btns.rejected.connect(dlg.reject)

            propetryGrid = PropertyGrid()
            propetryGrid.updateDataObject(self.selectedItem)
            container.addWidget(propetryGrid)
            
            container.addWidget(dlg.btns)
            dlg.setLayout(container)
            dlg.exec_()

        def itemEditUpdate(self):
            if type(self.selectedItem) == type(ListPropertyFieldTempValue):
                self.selectedItem.updateData()
             

        def updateSelected(self, current: QModelIndex, previous: QModelIndex):
            index = current.row()
            item = Extensions.getVariable(self.variable_source, self.variable_name)[index]
            attrCount = len(Extensions.getClassVariables(item))

            if attrCount <= 1:
                 self.selectedItem = ListPropertyFieldTempValue(item, self.variable_source, self.variable_name, index)
            else:
                self.selectedItem = item

            

#endregion

class PropertyGrid(QScrollArea):
    fields: list[PropertyField] = []

    def __init__(self):
        super().__init__()
        
        self.formWidget = QWidget()
        self.formLayout = QFormLayout()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)

        self.formWidget.setLayout(self.formLayout)
        self.setWidget(self.formWidget)

    def currentData(self):
        field: PropertyField
        newItem = self.item
        for field in self.fields:
            name, data, source = field.getFieldData()
            Extensions.setVariable(newItem, name, data)
        return newItem
    
    def updateDataObject(self, item):
        self.item = item
        self.fields.clear()
        PyQtExtensions.clearLayout(self.formLayout)
        
        for varName in Extensions.getClassVariables(item):
            variable = Extensions.getVariable(item, varName)
            field = PropertyField.getPropertyType(varName, variable, item)
            if field:
                self.fields.append(field)
                field.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
                self.formLayout.addRow(field.labelText, field)

