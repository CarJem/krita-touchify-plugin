from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET

from .PropertyGridExtensions import *

from .PropertyGridHost import *

from .extras.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from .propertygrid.IconSelector import IconSelector
from ..ext.typedlist import *
from ..resources import *
from ..ext.extensions import KritaExtensions
from .CollapsibleBox import CollapsibleBox


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum


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
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(ROW_SIZE_POLICY_X, ROW_SIZE_POLICY_Y)

    def setStackHost(self, host: PropertyGridHost):
        self.stackHost = host

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
        self.is_action_selection = False
        self.is_combobox = False
        self.combobox_items = []

        restric_func = PropertyGridExtensions.getVariable(self.variable_source, "propertygrid_restrictions")
        if callable(restric_func):
            restrictions = restric_func()
            if variable_name in restrictions:
                if restrictions[variable_name]["type"] == "values":
                    self.combobox_items = restrictions[variable_name]["entries"]
                    self.is_combobox = True
                elif restrictions[variable_name]["type"] == "action_selection":
                    self.is_action_selection = True
                elif restrictions[variable_name]["type"] == "docker_selection":
                    self.is_docker_selector = True
                elif restrictions[variable_name]["type"] == "icon_selection":
                    self.is_icon_viewer = True
                    

        if self.is_icon_viewer or self.is_docker_selector or self.is_action_selection:
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
            elif self.is_action_selection: editorHelperType = "actions"

            self.editorHelper.clicked.connect(lambda: self.helperRequested(editorHelperType))

            editorLayout = QHBoxLayout()
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            editorLayout.addWidget(self.editorHelper)
            self.setLayout(editorLayout)
            self.setLayout(editorLayout)
        elif self.is_combobox:
            self.editor = QComboBox()
            self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
            self.editor.insertItems(0, self.combobox_items)
            index = self.editor.findText(self.variable_data, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.editor.setCurrentIndex(index)
            self.editor.currentIndexChanged.connect(self.currentIndexChanged)

            editorLayout = QHBoxLayout()
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)
        else:
            self.editor = QLineEdit()
            self.editor.textChanged.connect(self.textChanged)
            self.editor.setText(self.variable_data.replace("\n", "\\n"))

            editorLayout = QHBoxLayout()
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)


    def dlg_accept(self):
        self.stackHost.goBack()
        self.dlg.accept()
    
    def dlg_reject(self):
        self.stackHost.goBack()
        self.dlg.reject()

    def helperRequested(self, mode):
        self.dlg = IconSelector(self.stackHost)
        self.dlg.setWindowFlags(Qt.WindowType.Widget)
        self.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btns.accepted.connect(lambda: self.dlg_accept())
        self.btns.rejected.connect(lambda: self.dlg_reject())
        self.dlg.dlgLayout.addWidget(self.btns)

        self.dlg.load_list(mode)
        self.stackHost.setCurrentIndex(self.stackHost.addWidget(self.dlg))
        if self.dlg.exec_():
            result = self.dlg.selectedResult()
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
        self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
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
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
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
        self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
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
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
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
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
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
        field.setSpacing(0)
        field.setContentsMargins(0,0,0,0)
        listView = QListView()
        listView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        btns = QVBoxLayout()
        btns.setAlignment(Qt.AlignmentFlag.AlignTop)
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

    def dlg_dispose(self):
        self.subwindowEditable = None
        self.subwindowPropGrid.deleteLater()
        self.subwindowMode = ""

    def dlg_accept(self):
        if (self.subwindowMode == "edit"):
            variableType = type(self.selectedItem)
            if variableType == PropertyField_TempValue:
                self.selectedItem.updateData()
            self.updateList()
        elif (self.subwindowMode == "add"):
            variableType = type(self.subwindowEditable)
            if variableType == PropertyField_TempValue:
                self.variable_data.append(self.subwindowEditable.value)
            else:
                self.variable_data.append(self.subwindowPropGrid.currentData())
            self.updateList()
        self.dlg.accept()
        self.stackHost.goBack()
        self.dlg_dispose()
    
    def dlg_reject(self):
        self.dlg.reject()
        self.stackHost.goBack()
        self.dlg_dispose()

    def itemOptions(self, mode):
        if mode == "edit" or mode == "add":
            self.dlg = QDialog(self)
            self.dlg.setWindowFlags(Qt.WindowType.Widget)
            self.container = QVBoxLayout()
            self.dlg.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.dlg.btns.accepted.connect(lambda: self.dlg_accept())
            self.dlg.btns.rejected.connect(lambda: self.dlg_reject())

            self.subwindowPropGrid = PropertyGrid(self.stackHost)
            self.container.addWidget(self.subwindowPropGrid)
            self.container.addWidget(self.dlg.btns)
            self.dlg.setLayout(self.container)

            if mode == "edit":
                if self.selectedIndex != -1:
                    self.subwindowMode = "edit"
                    self.subwindowPropGrid.updateDataObject(self.selectedItem)
                    self.stackHost.setCurrentIndex(self.stackHost.addWidget(self.dlg))
                    self.dlg.show()
            elif mode == "add":
                editableValue = self.getEditableValue(self.variable_list_type(), -1)
                self.subwindowMode = "add"
                self.subwindowEditable = editableValue
                self.subwindowPropGrid.updateDataObject(self.subwindowEditable)
                self.stackHost.setCurrentIndex(self.stackHost.addWidget(self.dlg))
                self.dlg.show()

        
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





class PropertyGrid(QScrollArea):
    fields: list[PropertyField] = []

    def __init__(self, parentStack: PropertyGridHost):
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
            PropertyGridExtensions.setVariable(newItem, name, data)
        return newItem
    

    def createDataRow(self, item, varName):
        variable = PropertyGridExtensions.getVariable(item, varName)
        field = PropertyField.getPropertyType(varName, variable, item)
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
        PropertyGridExtensions.clearLayout(self.formLayout)
        groupData = PropertyGridExtensions.getGroups(item)
        labelData = PropertyGridExtensions.getLabels(item)
        claimedSections = []

        for groupId in groupData:
            groupName = groupData[groupId]["name"]
            groupItems = list(groupData[groupId]["items"])
            for varName in groupItems:
                claimedSections.append(varName)

        for varName in PropertyGridExtensions.getClassVariables(item):
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
