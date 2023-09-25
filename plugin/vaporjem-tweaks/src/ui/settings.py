from krita import Krita, Extension
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
import sys
import importlib.util
from ..classes.config import *
from ..classes.resources import *
from ..ext.extensions import *
import xml.etree.ElementTree as ET
import re
import functools
import copy
import json


class SettingsGenerator:
    def createTextField(layout, variable_name, variable_data, variable_source):
        field = QLineEdit(variable_data)
        layout.addRow(variable_name + ': ', field)

    def createNumberField(layout, variable_name, variable_data, variable_source):
        field = QSpinBox()
        field.setValue(variable_data)
        layout.addRow(variable_name + ': ', field)


    def createListSubSection(current: QModelIndex, previous: QModelIndex, parentHost: QGroupBox, variable_name, variable_data, variable_source):
        layout = QFormLayout()
        index = current.row()
        item = Extensions.getVariable(variable_source, variable_name)[index]

        for varName in Extensions.getClassVariables(item):
            variable = Extensions.getVariable(item, varName)
            SettingsGenerator.createFromVariable(layout, varName, variable, item)

        parentHost.setLayout(layout)
        parentHost.update()

    def createListField(layout, variable_name, variable_data, variable_source):
        field = QHBoxLayout() 
        list = QListView()
        editor = QGroupBox()
        model = QtGui.QStandardItemModel()
        for i in variable_data:
            item = QtGui.QStandardItem(str(i))
            model.appendRow(item)
        list.setModel(model)
        field.addWidget(list)
        field.addWidget(editor)
        selection_model = list.selectionModel()
        selection_model.currentChanged.connect(lambda x, y: SettingsGenerator.createListSubSection(x, y, editor, variable_name, variable_data, variable_source))
        layout.addRow(variable_name + ': ', field)

    def createFromVariable(layout, varName, variable, item):
        if type(variable) == str:
            SettingsGenerator.createTextField(layout, varName, variable, item)
        elif type(variable) == int:
            SettingsGenerator.createNumberField(layout, varName, variable, item)
        elif type(variable) == list:
            SettingsGenerator.createListField(layout, varName, variable, item)

    def generate(item):
        layout = QFormLayout()
        for varName in Extensions.getClassVariables(item):
            variable = Extensions.getVariable(item, varName)
            SettingsGenerator.createFromVariable(layout, varName, variable, item)
        return layout


class SettingsDialog:

    def __init__(self):
        self.qwin = Krita.instance().activeWindow().qwindow()
        self.cfg = ConfigManager.getJSON()
        self.generateDialog()

    def show(self):
        self.dlg.show()
    
    def updateSelectionList(self):
        self.widgetItemsModel.clear()
        currentList = getattr(self.cfg, self.widgetSelector.currentText())

        for attr in currentList:
            display_data = attr.getDisplayData()
            item = QtGui.QStandardItem(display_data['name'])
            item.setData(attr)
            self.widgetItemsModel.appendRow(item)

    def updateSelection(self, current: QModelIndex, previous: QModelIndex):
        PyQtExtensions.clearLayout(self.widgetValuesLayout)
        index = current.row()
        element = self.widgetSelector.currentText()
        entry = Extensions.getVariable(self.cfg, element)[index]
        layout = SettingsGenerator.generate(entry)
        self.widgetValuesLayout.addLayout(layout) 
    
    def generateDialog(self):
        self.dlg = QDialog(self.qwin)

        self.layout = QVBoxLayout()

        self.widgetItemsList = QListView()
        self.widgetItemsModel = QtGui.QStandardItemModel()
        self.widgetItemsList.setModel(self.widgetItemsModel)
        self.widgetItemsSelectionModel = self.widgetItemsList.selectionModel()
        self.widgetItemsSelectionModel.currentChanged.connect(self.updateSelection)

        self.widgetValuesLayout = QVBoxLayout()

        self.widgetSelector = QComboBox()
        
        for attr in Extensions.getClassVariables(self.cfg):
            self.widgetSelector.addItem(attr)
        self.widgetSelector.currentTextChanged.connect(lambda: self.updateSelectionList())
        self.layout.addWidget(self.widgetSelector)

        self.widgetGroup = QGroupBox('Widget Options')
        
        self.widgetOptions = QHBoxLayout()
        self.widgetOptions.addWidget(self.widgetItemsList)
        self.widgetOptions.addLayout(self.widgetValuesLayout)
        self.widgetGroup.setLayout(self.widgetOptions)
        self.layout.addWidget(self.widgetGroup)

        self.container = QVBoxLayout()
        self.dlg.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dlg.btns.rejected.connect(self.dlg.reject)
        self.container.addLayout(self.layout)
        self.container.addWidget(self.dlg.btns)
        self.dlg.setLayout(self.container)
