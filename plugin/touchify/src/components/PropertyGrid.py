from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET

from .propertygrid.IconSelector import IconSelector
from ..ext.typedlist import *
from ..resources import *
from ..ext.extensions import KritaExtensions
from .CollapsibleBox import CollapsibleBox


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
            return PropertyField_Str(varName, variable, item)
        elif varType == int:
            return PropertyField_Int(varName, variable, item)
        elif varType == float:
            return PropertyField_Float(varName, variable, item)            
        elif varType == bool:
            return PropertyField_Bool(varName, variable, item)
        elif varType == TypedList:
            return PropertyField_TypedList(varName, variable, item)
        else:
            return PropertyField(varName, variable, item)

class PropertyField_Str(PropertyField):
    def __init__(self, variable_name=str, variable_data=str, variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)


        self.is_icon_viewer = False
        self.is_docker_selector = False
        self.is_combobox = False
        self.combobox_items = []

        restric_func = PropertyGridExtensions.getVariable(self.variable_source, "propertygrid_restrictions")
        if callable(restric_func):
            restrictions = restric_func()
            if variable_name in restrictions:
                if restrictions[variable_name]["type"] == "values":
                    self.combobox_items = restrictions[variable_name]["entries"]
                    self.is_combobox = True
                elif restrictions[variable_name]["type"] == "docker_selection":
                    self.is_docker_selector = True
                elif restrictions[variable_name]["type"] == "icon_selection":
                    self.is_icon_viewer = True
                    

        if self.is_icon_viewer or self.is_docker_selector:
            self.editor = QLineEdit()
            self.editor.textChanged.connect(self.textChanged)
            self.editor.setText(self.variable_data.replace("\n", "\\n"))

            self.editorHelper = QPushButton()
            if self.is_icon_viewer: 
                self.editorHelper.setIcon(ResourceManager.iconLoader(self.variable_data.replace("\n", "\\n")))
            else:
                self.editorHelper.setIcon(ResourceManager.iconLoader("properties"))


            editorHelperType = "none"
            if self.is_icon_viewer: editorHelperType = "icons"
            elif self.is_docker_selector: editorHelperType = "dockers"

            self.editorHelper.clicked.connect(lambda: self.helperRequested(editorHelperType))

            editorLayout = QHBoxLayout()
            editorLayout.addWidget(self.editor)
            editorLayout.addWidget(self.editorHelper)
            self.setLayout(editorLayout)
            self.setLayout(editorLayout)
        elif self.is_combobox:
            self.editor = QComboBox()
            self.editor.insertItems(0, self.combobox_items)
            index = self.editor.findText(self.variable_data, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.editor.setCurrentIndex(index)
            self.editor.currentIndexChanged.connect(self.currentIndexChanged)

            editorLayout = QHBoxLayout()
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)
        else:
            self.editor = QLineEdit()
            self.editor.textChanged.connect(self.textChanged)
            self.editor.setText(self.variable_data.replace("\n", "\\n"))

            editorLayout = QHBoxLayout()
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)

    def helperRequested(self, mode):
        dlg = IconSelector(self)
        dlg.load_list(mode)
        if dlg.exec_():
            result = dlg.selectedResult()
            if self.is_icon_viewer: 
                self.editorHelper.setIcon(ResourceManager.iconLoader(result))
            self.editor.setText(result)

    def currentIndexChanged(self):
        self.variable_data = str(self.editor.currentText()).replace("\\n", "\n")
        PropertyGridExtensions.setVariable(self.variable_source, self.variable_name, self.variable_data)

    def textChanged(self):
        self.variable_data = self.editor.text().replace("\\n", "\n")
        PropertyGridExtensions.setVariable(self.variable_source, self.variable_name, self.variable_data)

class PropertyField_Int(PropertyField):
    def __init__(self, variable_name=str, variable_data=int, variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)
        
        self.editor = QSpinBox()
        self.editor.setMaximum(2147483647)
        self.editor.setMinimum(-2147483648)
        self.editor.valueChanged.connect(self.updateValue)
        self.editor.setValue(self.variable_data)

        restric_func = PropertyGridExtensions.getVariable(self.variable_source, "propertygrid_restrictions")
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
            PropertyGridExtensions.setVariable(self.variable_source, self.variable_name, self.variable_data)

class PropertyField_Float(PropertyField):
    def __init__(self, variable_name=str, variable_data=float, variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)
        
        self.editor = QDoubleSpinBox()
        self.editor.setMaximum(sys.float_info.max)
        self.editor.setMinimum(sys.float_info.min)
        self.editor.valueChanged.connect(self.updateValue)
        self.editor.setValue(self.variable_data)

        restric_func = PropertyGridExtensions.getVariable(self.variable_source, "propertygrid_restrictions")
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
            PropertyGridExtensions.setVariable(self.variable_source, self.variable_name, self.variable_data)

class PropertyField_Bool(PropertyField):
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
        PropertyGridExtensions.setVariable(self.variable_source, self.variable_name, self.variable_data)

class PropertyField_TypedList(PropertyField):
    def __init__(self, variable_name=str, variable_data=TypedList, variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)
        self.variable_list_type = variable_data.allowedTypes()
        print(self.variable_list_type)

        self.selectedIndex = -1
        self.selectedItem = None
        
        field = QHBoxLayout()
        listView = QListView()
        listView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        btns = QVBoxLayout()
        btn_width = 20

        self.model = QtGui.QStandardItemModel()
        self.updateList()

        listView.setModel(self.model)
        field.addWidget(listView)
        field.addLayout(btns)

        addButton = QPushButton()
        addButton.setText("+")
        addButton.setFixedWidth(btn_width)
        addButton.clicked.connect(self.itemOptions_add)
        btns.addWidget(addButton)

        removeButton = QPushButton()
        removeButton.setText("-")
        removeButton.setFixedWidth(btn_width)
        removeButton.clicked.connect(self.itemOptions_remove)
        btns.addWidget(removeButton)

        moveUpButton = QPushButton()
        moveUpButton.setText("↑")
        moveUpButton.setFixedWidth(btn_width)
        moveUpButton.clicked.connect(self.itemOptions_moveup)
        btns.addWidget(moveUpButton)

        moveDownButton = QPushButton()
        moveDownButton.setText("↓")
        moveDownButton.setFixedWidth(btn_width)
        moveDownButton.clicked.connect(self.itemOptions_movedown)
        btns.addWidget(moveDownButton)

        editButton = QPushButton()
        editButton.setText("...")
        editButton.setFixedWidth(btn_width)
        editButton.clicked.connect(self.itemOptions_edit)
        btns.addWidget(editButton)

        self.selection_model = listView.selectionModel()
        self.selection_model.currentChanged.connect(lambda x, y: self.updateSelected(x, y))

        self.setLayout(field)

    def itemOptions_add(self):
        self.itemOptions("add")

    def itemOptions_remove(self):
        self.itemOptions("remove")

    def itemOptions_moveup(self):
        self.itemOptions("moveup")

    def itemOptions_movedown(self):
        self.itemOptions("movedown")

    def itemOptions_edit(self):
        self.itemOptions("edit")

    def itemOptions(self, mode):
        if mode == "edit" or mode == "add":
            dlg = QDialog(self)
            container = QVBoxLayout()
            dlg.setMinimumSize(800,450)
            dlg.setBaseSize(800,800)
            dlg.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            dlg.btns.accepted.connect(dlg.accept)
            dlg.btns.rejected.connect(dlg.reject)

            propetryGrid = PropertyGrid()
            container.addWidget(propetryGrid)
            container.addWidget(dlg.btns)
            dlg.setLayout(container)

            if mode == "edit":
                if self.selectedIndex != -1:
                    propetryGrid.updateDataObject(self.selectedItem)
                    if dlg.exec_():
                        variableType = type(self.selectedItem)
                        if variableType == PropertyField_TempValue:
                            self.selectedItem.updateData()
                        self.updateList()

            elif mode == "add":
                editableValue = self.getEditableValue(self.variable_list_type(), -1)
                propetryGrid.updateDataObject(editableValue)
                if dlg.exec_():
                    variableType = type(editableValue)
                    if variableType == PropertyField_TempValue:
                        self.variable_data.append(editableValue.value)
                    else:
                        self.variable_data.append(propetryGrid.currentData())
                    self.updateList()
        
        elif mode == "remove":
            if self.selectedIndex != -1:
                variable = PropertyGridExtensions.getVariable(self.variable_source, self.variable_name)
                newIndex = self.selectedIndex
                if not newIndex - 1 < 0:
                    newIndex -= 1
                variable.pop(self.selectedIndex)
                self.updateList()
                self.selection_model.setCurrentIndex(self.model.index(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
        
        elif mode == "moveup" or mode == "movedown":
            if self.selectedIndex != -1:
                variable = PropertyGridExtensions.getVariable(self.variable_source, self.variable_name)
                length = len(variable)

                oldIndex = self.selectedIndex
                newIndex = self.selectedIndex
                
                if mode == "moveup":
                    if not newIndex - 1 < 0:
                        newIndex -= 1
                elif mode == "movedown":
                    if not newIndex + 1 > length - 1:
                        newIndex += 1

                variable.insert(newIndex, variable.pop(oldIndex))
                self.updateList()
                self.selection_model.setCurrentIndex(self.model.index(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)

    def updateList(self):
        self.model.clear()
        for i in self.variable_data:
            item = QtGui.QStandardItem(str(i))
            self.model.appendRow(item)
        self.selectedIndex = -1
        self.selectedItem = None

    def updateSelected(self, current: QModelIndex, previous: QModelIndex):
        self.selectedIndex = current.row()
        item = PropertyGridExtensions.getVariable(self.variable_source, self.variable_name)[self.selectedIndex]
        self.selectedItem = self.getEditableValue(item, self.selectedIndex)

    def getEditableValue(self, item, index):
        if hasattr(item, "forceLoad"):
            item.forceLoad()

        attrCount = len(PropertyGridExtensions.getClassVariables(item))
        isClassModel = PropertyGridExtensions.isClassModel(item)

        if attrCount <= 1 and not isClassModel:
                return PropertyField_TempValue(item, self.variable_source, self.variable_name, index)
        else:
            return item        

class PropertyField_TempValue:
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

    def updateData(self):
        new_array = PropertyGridExtensions.getVariable(self.__variable_source, self.__variable_name)
        self.variable_data = self.value
        new_array[self.__index] = self.value
        PropertyGridExtensions.setVariable(self.__variable_source, self.__variable_name, new_array)





class PropertyGridExtensions:

    def tryGetVariable(obj, varName):
        if hasattr(obj, varName):
            return getattr(obj, varName)
        else: return None

    def getVariable(obj, varName):
        return getattr(obj, varName)
    
    def setVariable(obj, varName, data):
        return setattr(obj, varName, data)
    
    def getClassVariables(obj):
        return [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and 
                not attr.startswith("__") and 
                not attr.startswith("_"  + type(obj).__name__ + "__")]
    
    def getGroups(obj):
        if hasattr(obj, "propertygrid_groups"):
            return dict(obj.propertygrid_groups())
        else: return {}
    
    def isClassModel(obj):
        return hasattr(obj, "propertygrid_ismodel")

    
    def quickDialog(parent, text):
        dlg = QMessageBox(parent)
        dlg.setText(text)
        dlg.show()

    def clearLayout(layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    PropertyGridExtensions.clearLayout(child.layout())

class PropertyGrid(QScrollArea):
    fields: list[PropertyField] = []

    def __init__(self):
        super().__init__()
        
        self.formWidget = QWidget()
        self.formLayout = QFormLayout()
        self.formLayout.setVerticalSpacing(0)
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
            PropertyGridExtensions.setVariable(newItem, name, data)
        return newItem
    
    def updateDataObject(self, item):
        self.item = item
        self.fields.clear()
        PropertyGridExtensions.clearLayout(self.formLayout)
        groupData = PropertyGridExtensions.getGroups(item)
        claimedSections = []

        for groupId in groupData:
            groupName = groupData[groupId]["name"]
            groupItems = list(groupData[groupId]["items"])
            for varName in groupItems:
                claimedSections.append(varName)

        for varName in PropertyGridExtensions.getClassVariables(item):
            if varName not in claimedSections:
                variable = PropertyGridExtensions.getVariable(item, varName)
                field = PropertyField.getPropertyType(varName, variable, item)
                if field:
                    self.fields.append(field)
                    field.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
                    #self.formLayout.addWidget(field)
                    self.formLayout.addRow(field.labelText, field)
        
        for groupId in groupData:
            groupName = groupData[groupId]["name"]
            groupItems = list(groupData[groupId]["items"])
            section = CollapsibleBox(groupName, self.formWidget)
            sectionLayout = QFormLayout()
            section.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

            for varName in groupItems:
                variable = PropertyGridExtensions.getVariable(item, varName)
                field = PropertyField.getPropertyType(varName, variable, item)
                if field:
                    self.fields.append(field)
                    field.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
                    sectionLayout.addRow(field.labelText, field)
            section.setContentLayout(sectionLayout)
            self.formLayout.addRow(section)
