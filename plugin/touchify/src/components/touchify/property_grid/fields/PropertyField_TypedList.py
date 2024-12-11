import copy
from typing import Literal
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from touchify.src.components.touchify.property_grid.dialogs.PropertyGrid_Dialog import PropertyGrid_Dialog
from touchify.src.components.touchify.property_grid.fields.PropertyField import PropertyField
from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import PropertyUtils_Extensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.helpers import TouchifyHelpers
from touchify.src.resources import *



class PropertyField_TypedList(PropertyField):
    def __init__(self, variable_name: str, variable_data: TypedList, variable_source: any, manual_restrictions: list[dict[str, any]] = []):
        super().__init__(variable_name, variable_data, variable_source, True)
        self.variable_list_type = variable_data.allowedTypes()
        self.variable_data: TypedList

        self.nested_list_id = ""
        self.has_sub_array = False
        self.has_property_view = False
        

        self.add_remove_edit_only = False

        self.test_restrictions(manual_restrictions)

        self.selectedIndex = -1
        self.selectedSubIndex = -1

        self.selectedItem = None
        self.selectedSubItem = None
        
        self.field_layout = QHBoxLayout(self)
        self.field_layout.setSpacing(0)
        self.field_layout.setContentsMargins(0,0,0,0)

        self.view_layout = QVBoxLayout()
        self.view_layout.setSpacing(0)
        self.view_layout.setContentsMargins(0,0,0,0)
        self.field_layout.addLayout(self.view_layout)

        self.view_editor = None

        self.model = QtGui.QStandardItemModel()
        if self.has_sub_array:
            self.view = QTreeView()
            self.view.setHeaderHidden(True)
        else:
            self.view = QListView()
        self.view.doubleClicked.connect(self.list_edit)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.updateList()
        self.view.setModel(self.model)
        self.view_layout.addWidget(self.view)



        if self.has_property_view:
            from ..PropertyPage import PropertyPage
            self.view_editor = PropertyPage(None)
            self.view_editor.propertyChanged.connect(self.onPropertyViewUpdate)
            self.field_layout.addWidget(self.view_editor)


        self.selection_model = self.view.selectionModel()
        self.selection_model.currentChanged.connect(self.updateSelected)

        btns = QHBoxLayout()
        btns.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.view_layout.addLayout(btns)


        addButton = QPushButton()
        addButton.setIcon(ResourceManager.iconLoader("material:plus"))
        addButton.setFixedHeight(24)
        addButton.clicked.connect(self.list_add)
        btns.addWidget(addButton)

        removeButton = QPushButton()
        removeButton.setIcon(ResourceManager.iconLoader("material:minus"))
        removeButton.setFixedHeight(24)
        removeButton.clicked.connect(self.list_remove)
        btns.addWidget(removeButton)

        if self.add_remove_edit_only == False:
            moveUpButton = QPushButton()
            moveUpButton.setIcon(ResourceManager.iconLoader("material:arrow-up"))
            moveUpButton.setFixedHeight(24)
            moveUpButton.clicked.connect(self.list_moveUp)
            btns.addWidget(moveUpButton)

            moveDownButton = QPushButton()
            moveDownButton.setIcon(ResourceManager.iconLoader("material:arrow-down"))  
            moveDownButton.setFixedHeight(24)
            moveDownButton.clicked.connect(self.list_moveDown)
            btns.addWidget(moveDownButton)

        editButton = QPushButton()
        editButton.setIcon(ResourceManager.iconLoader("material:pencil"))                                                                                                                                                                                                                                                                                                                                 
        editButton.setFixedHeight(24)
        editButton.clicked.connect(self.list_edit)
        btns.addWidget(editButton)

        if self.add_remove_edit_only == False:
            moreButton = QPushButton()
            moreButton.setIcon(ResourceManager.iconLoader("material:menu"))                                                                                                                                                                                                                                                                                                              
            moreButton.setFixedHeight(24)
            btns.addWidget(moreButton)

            moreMenu = QMenu(moreButton)
            dupeAct = moreMenu.addAction("Duplicate")
            dupeAct.triggered.connect(self.list_duplicate)
            copyAct = moreMenu.addAction("Copy")
            copyAct.triggered.connect(self.list_copy)
            pateAct = moreMenu.addAction("Paste")
            pateAct.triggered.connect(self.list_paste)
            moreButton.setMenu(moreMenu)

        self.setLayout(self.field_layout)

    def test_restrictions(self, manual_restrictions: list[dict[str, any]] = []):
        restrictions: list[dict[str, any]] = []
        if len(manual_restrictions) != 0: 
            restrictions = manual_restrictions
        else: 
            restrictions = PropertyUtils_Extensions.classRestrictions(self.variable_source, self.variable_name)

        sub_array_setup = False

        for restriction in restrictions:
            if restriction["type"] == "sub_array" and sub_array_setup == False:
                self.nested_list_id: str = restriction["sub_id"]
                self.nested_list_nested_type: type = restriction["sub_type"]
                self.has_sub_array = True
                sub_array_setup = True
            if restriction["type"] == "property_view":
                self.has_property_view = True
            if restriction["type"] == "add_remove_edit_only":
                self.add_remove_edit_only = True


    def setStackHost(self, host):
        super().setStackHost(host)
        if self.has_property_view:
            self.view_editor.setStackHost(host)
    #region List Actions

    def list_moveUp(self):
        self.list_move('up')

    def list_moveDown(self):
        self.list_move('down')    

    def list_move(self, direction: Literal['up', 'down'] = 'up'):
        if self.selectedIndex != -1:
            if self.selectedSubIndex != -1:
                variable = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
                length = len(variable)
                child = variable[self.selectedIndex]
                sub_variable = self.getNestedList(child)
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
                    new_child = variable[parentIndex]
                    new_sub_variable = self.getNestedList(variable[parentIndex])
                
                    if direction == 'up': newIndex = len(new_sub_variable)
                    else: newIndex = 0

                    moved_item = sub_variable.pop(oldIndex)
                    new_sub_variable.insert(newIndex, moved_item)

                else:
                    sub_variable.insert(newIndex, sub_variable.pop(oldIndex))

                self.updateList()
                self.selection_model.setCurrentIndex(self.model.index(parentIndex, 0).child(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
                self.propertyChanged.emit(True)

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
                self.propertyChanged.emit(True)

    def list_add(self):
        self.list_modify("add")

    def list_edit(self):
        self.list_modify("edit")
    
    
    def list_modify(self, mode: Literal['edit', 'add'] = 'add'):


        def createPage():
            dlg = PropertyGrid_Dialog(self)
            dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
            dlg.setWindowTitle(self.variable_name + ' - ' + str(self.selectedItem))
            dlg.setWindowFlags(Qt.WindowType.Widget)
            dlg.rejected.connect(self.updateList)
            
            container = QVBoxLayout(self)
            container.setContentsMargins(0,0,0,0)
            container.setSpacing(0)

            from ..PropertyPage import PropertyPage
            container_props = PropertyPage(self.stack_host)
            container.addWidget(container_props)
            dlg.setLayout(container)

            return (container_props, dlg)

        if mode == 'add':
            if self.selectedSubIndex != -1:
                editableValue = self.getEditableValue(type(self.selectedSubItem)())
                self.getNestedList(self.selectedItem).append(editableValue)
            else:
                editableValue = self.getEditableValue(self.variable_list_type())
                self.variable_data.append(editableValue)
            self.updateList()
            self.propertyChanged.emit(True)
        elif mode == 'edit':
            prop_grid = None
            page_dialog = None

            if self.has_property_view: prop_grid = self.view_editor
            else: prop_grid, page_dialog = createPage()


            if self.selectedIndex != -1:
                if self.selectedSubIndex != -1:
                    prop_grid.updateDataObject(self.selectedSubItem)
                else:
                    prop_grid.updateDataObject(self.selectedItem)

            if not self.has_property_view and page_dialog:
                self.stack_host.goForward(page_dialog)
                page_dialog.show()




    def list_copy(self):
        item_type: type | None = None
        item_data: any | None = None

        if self.selectedIndex != -1:
            if self.selectedSubIndex != -1:
                variable: TypedList = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
                item_type = type(self.selectedSubItem)
                item_data = copy.deepcopy(self.getNestedList(variable[self.selectedIndex])[self.selectedSubIndex])
            else:
                variable: TypedList = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
                item_type = self.variable_list_type
                item_data = copy.deepcopy(variable[self.selectedIndex])

            if item_data != None and item_type != None:
                self.prepareCopiedItem(item_data)
                TouchifyHelpers.getExtension().setSettingsClipboard(item_type, item_data)


    def list_paste(self):
        item_type: type | None = None
        
        if self.selectedIndex != -1:
            if self.selectedSubIndex != -1: 
                item_type = type(self.selectedSubItem)
            else: 
                item_type = self.variable_list_type

            if item_type != None:
                clipboard_data = TouchifyHelpers.getExtension().getSettingsClipboard(item_type)
                if clipboard_data != None:
                    pastable_data = copy.deepcopy(clipboard_data)
                    variable: TypedList = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
                    if self.selectedSubIndex != -1:
                        list: TypedList = self.getNestedList(variable[self.selectedIndex])
                        list.append(pastable_data)
                    else:
                        variable.append(pastable_data)
                    self.updateList()

                        


    def list_duplicate(self):
        if self.selectedIndex != -1:
            if self.selectedSubIndex != -1:
                variable: TypedList = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
                list: TypedList = self.getNestedList(variable[self.selectedIndex])
                item = list[self.selectedSubIndex]
                newItem = copy.deepcopy(item)
                self.prepareCopiedItem(newItem)
                list.append(newItem)
                self.updateList()
            else:
                variable: TypedList = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
                item = variable[self.selectedIndex]
                newItem = copy.deepcopy(item)
                self.prepareCopiedItem(newItem)
                variable.append(newItem)
                self.updateList()

    def list_remove(self):
        if self.selectedIndex != -1:
            if self.selectedSubIndex != -1:
                variable: TypedList = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
                newIndex = self.selectedSubIndex
                list: TypedList = self.getNestedList(variable[self.selectedIndex])
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
        index = 0

        indicies = []

        for varItem in self.variable_data:
            item = QtGui.QStandardItem(str(varItem))
            index += 1

            sub_index = 0
            columns = []

            for subAction in self.getNestedList(varItem):
                subItem = QtGui.QStandardItem(str(subAction))
                sub_index += 1

                columns.append(subItem)

            item.appendColumn(columns)
            self.model.appendRow(item)
            indicies.append(sub_index + 1)

        self.selectedIndex = -1
        self.selectedItem = None
        self.selectedSubIndex = -1
        self.selectedSubItem = None


        if self.has_property_view:
            self.updatePropertyView()

        if self.has_sub_array:
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
            source = self.selectedItem
            item = self.getNestedList(source)[self.selectedSubIndex]
            self.selectedSubItem = self.getEditableValue(item)
        else:
            self.selectedSubItem = None

        if self.has_sub_array:
            self.view.expandAll()

        if self.has_property_view:
            self.updatePropertyView()

    def onPropertyViewUpdate(self, value: bool):
        pass
        #self.updateList()

    def updatePropertyView(self):
        if not self.has_property_view: return
        if self.view_editor == None: return

        if self.selectedIndex != -1:
            if self.selectedSubIndex != -1:
                self.view_editor.updateDataObject(self.selectedSubItem)
            else:
                self.view_editor.updateDataObject(self.selectedItem)
        else:
            self.view_editor.updateDataObject(None)


    def getNestedList(self, item: any):
        try:
            attr = getattr(item, self.nested_list_id)
            if isinstance(attr, TypedList):
                return attr
            else:
                return []
        except:
            return []
        
    def prepareCopiedItem(self, item):
        if hasattr(item, "propertygrid_on_duplicate"):
            item.propertygrid_on_duplicate()

    def getEditableValue(self, item):
        if hasattr(item, "forceLoad"):
            item.forceLoad()
        return item        