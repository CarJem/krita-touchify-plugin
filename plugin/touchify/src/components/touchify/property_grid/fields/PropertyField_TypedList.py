from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET

from ..dialogs.PropertyGrid_Dialog import PropertyGrid_Dialog
from ....pyqt.event_filters.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from .....ext.TypedList import *
from .....resources import *
from .....ext.extensions_krita import KritaExtensions
from ....pyqt.widgets.CollapsibleBox import CollapsibleBox

from ..utils.PropertyUtils_Extensions import *
from ..dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from .PropertyField import *
from .PropertyField_TempValue import *




ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

class PropertyField_TypedList(PropertyField):
    def __init__(self, variable_name=str, variable_data=TypedList, variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)
        self.variable_list_type = variable_data.allowedTypes()
        print(self.variable_list_type)

        self.selectedIndex = -1
        self.selectedItem = None
        
        field = QVBoxLayout(self)
        field.setSpacing(0)
        field.setContentsMargins(0,0,0,0)
        listView = QListView()
        listView.doubleClicked.connect(self.itemOptions_edit)
        listView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        btns = QHBoxLayout()
        btns.setAlignment(Qt.AlignmentFlag.AlignBottom)
        btn_width = 24

        self.model = QtGui.QStandardItemModel()
        self.updateList()

        listView.setModel(self.model)
        field.addWidget(listView)
        field.addLayout(btns)

        addButton = QPushButton()
        addButton.setIcon(ResourceManager.iconLoader("material:plus"))
        addButton.setFixedHeight(btn_width)
        addButton.clicked.connect(self.itemOptions_add)
        btns.addWidget(addButton)

        removeButton = QPushButton()
        removeButton.setIcon(ResourceManager.iconLoader("material:minus"))
        removeButton.setFixedHeight(btn_width)
        removeButton.clicked.connect(self.itemOptions_remove)
        btns.addWidget(removeButton)

        moveUpButton = QPushButton()
        moveUpButton.setIcon(ResourceManager.iconLoader("material:arrow-up"))
        moveUpButton.setFixedHeight(btn_width)
        moveUpButton.clicked.connect(self.itemOptions_moveup)
        btns.addWidget(moveUpButton)

        moveDownButton = QPushButton()
        moveDownButton.setIcon(ResourceManager.iconLoader("material:arrow-down"))  
        moveDownButton.setFixedHeight(btn_width)
        moveDownButton.clicked.connect(self.itemOptions_movedown)
        btns.addWidget(moveDownButton)

        editButton = QPushButton()
        editButton.setIcon(ResourceManager.iconLoader("material:pencil"))                                                                                                                                                                                                                                                                                                                                 
        editButton.setFixedHeight(btn_width)
        editButton.clicked.connect(self.itemOptions_edit)
        btns.addWidget(editButton)

        duplicateButton = QPushButton()
        duplicateButton.setIcon(ResourceManager.iconLoader("material:content-copy"))                                                                                                                                                                                                                                                                                                              
        duplicateButton.setFixedHeight(btn_width)
        duplicateButton.clicked.connect(self.itemOptions_duplicate)
        btns.addWidget(duplicateButton)

        self.selection_model = listView.selectionModel()
        self.selection_model.currentChanged.connect(lambda x, y: self.updateSelected(x, y))

        self.setLayout(field)

    #region Item Options
    def itemOptions_add(self):
        self.list_modify("add")

    def itemOptions_remove(self):
        self.list_remove()

    def itemOptions_moveup(self):
        self.list_move('up')

    def itemOptions_movedown(self):
        self.list_move('down')

    def itemOptions_edit(self):
        self.list_modify("edit")

    def itemOptions_duplicate(self):
        self.list_duplicate()

    #endregion

    #region Dialog
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
    #endregion

    #region List Actions
    def list_move(self, direction: Literal['up', 'down'] = 'up'):
        if self.selectedIndex != -1:
            variable = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
            length = len(variable)

            oldIndex = self.selectedIndex
            newIndex = self.selectedIndex
            
            if direction == 'up':
                if not newIndex - 1 < 0:
                    newIndex -= 1
            elif direction == 'down':
                if not newIndex + 1 > length - 1:
                    newIndex += 1

            variable.insert(newIndex, variable.pop(oldIndex))
            self.updateList()
            self.selection_model.setCurrentIndex(self.model.index(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)

    def list_modify(self, mode: Literal['edit', 'add'] = 'add'):
        self.dlg = PropertyGrid_Dialog(self)
        self.dlg.setWindowFlags(Qt.WindowType.Widget)
        self.container = QVBoxLayout(self)
        self.dlg.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dlg.btns.accepted.connect(lambda: self.dlg_accept())
        self.dlg.btns.rejected.connect(lambda: self.dlg_reject())

        from ..PropertyGrid_Panel import PropertyGrid_Panel
        self.subwindowPropGrid = PropertyGrid_Panel(self.stackHost)
        self.container.addWidget(self.subwindowPropGrid)
        self.container.addWidget(self.dlg.btns)
        self.dlg.setLayout(self.container)

        if mode == 'edit':
            if self.selectedIndex != -1:
                self.subwindowMode = "edit"
                self.subwindowPropGrid.updateDataObject(self.selectedItem)
                self.stackHost.goForward(self.dlg)
                self.dlg.show()
        elif mode == 'add':
            editableValue = self.getEditableValue(self.variable_list_type(), -1)
            self.subwindowMode = "add"
            self.subwindowEditable = editableValue
            self.subwindowPropGrid.updateDataObject(self.subwindowEditable)
            self.stackHost.goForward(self.dlg)
            self.dlg.show()

    def list_duplicate(self):
        if self.selectedIndex != -1:
            variable: TypedList = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
            item = variable[self.selectedIndex]
            newItem = copy.deepcopy(item)
            variable.append(newItem)
            self.updateList()

    def list_remove(self):
        if self.selectedIndex != -1:
            variable: TypedList = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
            newIndex = self.selectedIndex
            if not newIndex - 1 < 0:
                newIndex -= 1
            variable.pop(self.selectedIndex)
            self.updateList()
            self.selection_model.setCurrentIndex(self.model.index(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
    #endregion

    def updateList(self):
        self.model.clear()
        for i in self.variable_data:
            item = QtGui.QStandardItem(str(i))
            self.model.appendRow(item)
        self.selectedIndex = -1
        self.selectedItem = None

    def updateSelected(self, current: QModelIndex, previous: QModelIndex):
        self.selectedIndex = current.row()
        item = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)[self.selectedIndex]
        self.selectedItem = self.getEditableValue(item, self.selectedIndex)

    def getEditableValue(self, item, index):
        if hasattr(item, "forceLoad"):
            item.forceLoad()

        attrCount = len(PropertyUtils_Extensions.getClassVariables(item))
        isClassModel = PropertyUtils_Extensions.isClassModel(item)

        if attrCount <= 1 and not isClassModel:
            return PropertyField_TempValue(item, self.variable_source, self.variable_name, index)
        else:
            return item        
