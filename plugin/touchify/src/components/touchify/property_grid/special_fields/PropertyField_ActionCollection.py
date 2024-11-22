import copy
from typing import Literal
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from touchify.src.cfg.action.CfgTouchifyAction import CfgTouchifyAction
from touchify.src.cfg.action.CfgTouchifyActionCollection import CfgTouchifyActionCollection
from touchify.src.components.touchify.property_grid.dialogs.PropertyGrid_Dialog import PropertyGrid_Dialog
from touchify.src.components.touchify.property_grid.fields.PropertyField import PropertyField
from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import PropertyUtils_Extensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.resources import *

from touchify.src.components.touchify.property_grid.fields.PropertyField_TempValue import PropertyField_TempValue


class PropertyField_ActionCollection(PropertyField):
    def __init__(self, variable_name=str, variable_data=TypedList[CfgTouchifyActionCollection], variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)
        self.variable_list_type = variable_data.allowedTypes()
        self.variable_data: TypedList[CfgTouchifyActionCollection]
        print(self.variable_list_type)

        self.selectedIndex = -1
        self.selectedSubIndex = -1

        self.selectedItem = None
        self.selectedSubItem = None
        
        field = QVBoxLayout(self)
        field.setSpacing(0)
        field.setContentsMargins(0,0,0,0)

        self.view = QTreeView()
        self.view.setHeaderHidden(True)
        self.view.doubleClicked.connect(self.itemOptions_edit)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        btns = QHBoxLayout()
        btns.setAlignment(Qt.AlignmentFlag.AlignBottom)
        btn_width = 24

        self.model = QtGui.QStandardItemModel()
        self.updateList()

        self.view.setModel(self.model)
        field.addWidget(self.view)
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

        self.selection_model = self.view.selectionModel()
        self.selection_model.currentChanged.connect(self.updateSelected)

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
        self.subwindowItem = ""

    def dlg_accept(self):
        if (self.subwindowMode == "edit"):
            if self.subwindowItem == "subitem":
                variableType = type(self.selectedSubItem)
                if variableType == PropertyField_TempValue:
                    self.selectedSubItem.updateData()
                self.updateList()
            else:
                variableType = type(self.selectedItem)
                if variableType == PropertyField_TempValue:
                    self.selectedItem.updateData()
                self.updateList()
        elif (self.subwindowMode == "add"):
            if self.subwindowItem == "subitem":
                variableType = type(self.subwindowEditable)
                if variableType == PropertyField_TempValue:
                    self.selectedItem.actions.append(self.subwindowEditable.value)
                else:
                    self.selectedItem.actions.append(self.subwindowPropGrid.currentData())
                self.updateList()
            else:
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
            if self.selectedSubIndex != -1:
                variable = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
                length = len(variable)
                child: CfgTouchifyActionCollection = variable[self.selectedIndex]
                sub_variable = child.actions
                sub_length = len(sub_variable)

                oldIndex = self.selectedSubIndex
                newIndex = self.selectedSubIndex

                parentIndex = self.selectedIndex
                moveToOtherArray = False
                

                if direction == 'up':
                    if not newIndex - 1 < 0:
                        newIndex -= 1
                    elif not parentIndex - 1 < 0:
                        
                        parentIndex -= 1
                        moveToOtherArray = True
                elif direction == 'down':
                    if not newIndex + 1 > sub_length - 1:
                        newIndex += 1
                    elif not parentIndex + 1 > length - 1:
                        parentIndex += 1
                        moveToOtherArray = True

                if moveToOtherArray:
                    new_child: CfgTouchifyActionCollection = variable[parentIndex]
                    new_sub_variable = new_child.actions
                
                    if direction == 'up': newIndex = len(new_sub_variable)
                    else: newIndex = 0

                    moved_item = sub_variable.pop(oldIndex)
                    new_sub_variable.insert(newIndex, moved_item)

                else:
                    sub_variable.insert(newIndex, sub_variable.pop(oldIndex))

                self.updateList()

                self.selection_model.setCurrentIndex(self.model.index(parentIndex, 0).child(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)

            else:
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
        self.dlg.setWindowTitle(self.variable_name + ' - ' + str(self.selectedItem))
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
                if self.selectedSubIndex != -1:
                    self.subwindowItem = "subitem"
                    self.subwindowPropGrid.updateDataObject(self.selectedSubItem)
                else:
                    self.subwindowItem = "normal"
                    self.subwindowPropGrid.updateDataObject(self.selectedItem)
                self.stackHost.goForward(self.dlg)
                self.dlg.show()
        elif mode == 'add':
            if self.selectedSubIndex != -1:
                editableValue = self.getEditableValue(CfgTouchifyAction())
                self.subwindowMode = "add"
                self.subwindowItem = "subitem"
                self.subwindowEditable = editableValue
                self.subwindowPropGrid.updateDataObject(self.subwindowEditable)
                self.stackHost.goForward(self.dlg)
                self.dlg.show()
            else:
                editableValue = self.getEditableValue(self.variable_list_type())
                self.subwindowMode = "add"
                self.subwindowItem = "normal"
                self.subwindowEditable = editableValue
                self.subwindowPropGrid.updateDataObject(self.subwindowEditable)
                self.stackHost.goForward(self.dlg)
                self.dlg.show()

    def list_duplicate(self):
        if self.selectedIndex != -1:
            if self.selectedSubIndex != -1:
                variable: TypedList = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
                list: TypedList = variable[self.selectedIndex].actions
                item = list[self.selectedSubIndex]
                newItem = copy.deepcopy(item)
                list.append(newItem)
                self.updateList()
            else:
                variable: TypedList = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
                item = variable[self.selectedIndex]
                newItem = copy.deepcopy(item)
                variable.append(newItem)
                self.updateList()

    def list_remove(self):
        if self.selectedIndex != -1:
            if self.selectedSubIndex != -1:
                variable: TypedList = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
                newIndex = self.selectedSubIndex
                list: TypedList = variable[self.selectedIndex].actions
                if not newIndex - 1 < 0:
                    newIndex -= 1
                list.pop(self.selectedSubIndex)
                self.updateList()
                self.selection_model.setCurrentIndex(self.model.index(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
            else:
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
        for varItem in self.variable_data:
            varItem: CfgTouchifyActionCollection
            item = QtGui.QStandardItem(str(varItem))
            columns = []

            for subAction in varItem.actions:
                subAction: CfgTouchifyAction
                subItem = QtGui.QStandardItem(str(subAction))
                columns.append(subItem)

            item.appendColumn(columns)
            self.model.appendRow(item)
        self.selectedIndex = -1
        self.selectedItem = None
        QTimer.singleShot(100, self.view.expandAll)
        

    def updateSelected(self, current: QModelIndex, previous: QModelIndex):
        x = -1
        y = -1

        if current.parent().row() == -1:
            y = -1
            x = current.row()
        else:
            y = current.row()
            x = current.parent().row()

        self.selectedIndex = x
        self.selectedSubIndex = y
 
        if self.selectedIndex != -1:
            item = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)[self.selectedIndex]
            self.selectedItem = self.getEditableValue(item)
        else:
            self.selectedItem = None

        if self.selectedItem != None and self.selectedSubIndex != -1:
            source: CfgTouchifyActionCollection = self.selectedItem
            item = source.actions[self.selectedSubIndex]
            self.selectedSubItem = self.getEditableValue(item)
        else:
            self.selectedSubItem = None

        self.view.expandAll()


    def getEditableValue(self, item):
        if hasattr(item, "forceLoad"):
            item.forceLoad()
        return item        