import copy
from typing import TYPE_CHECKING, Literal
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *



from jemlib.alib_propertygrid.data.DataPath import DataPath
from jemlib.alib_propertygrid.dialogs.PropertyGrid_Dialog import PropertyGrid_Dialog
from jemlib.alib_propertygrid.fields.PropertyField import PropertyField
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.managers.IconRepository import *

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler
    from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid



class PropertyField_TypedList(PropertyField[TypedList]):
    def __init__(self, handler: "DataHandler", property: DataPath[TypedList], manual_restrictions: list[dict[str, any]] = []):
        super(PropertyField_TypedList, self).__init__(handler, property, True)
        self.variable_list_type = self.propertyData.variableData().allowedTypes()

        self.nested_list_id = ""
        self.has_sub_array = False
        self.has_property_view = False
        
        self.allow_move = True
        self.allow_clipboard = True
        self.allow_length_changes = True

        self.test_restrictions(manual_restrictions)

        self.selected_row = -1
        self.selected_sub_row = -1

        self.selected_item = None
        self.selected_sub_item = None
        
        self.field_layout = QHBoxLayout(self)
        self.field_layout.setSpacing(0)
        self.field_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.field_layout)

        self.view_widget = QWidget(self)
        self.view_widget.setContentsMargins(0,0,0,0)
        self.field_layout.addWidget(self.view_widget)

        self.view_layout = QVBoxLayout(self.view_widget)
        self.view_layout.setSpacing(0)
        self.view_layout.setContentsMargins(0,0,0,0)
        self.view_widget.setLayout(self.view_layout)

        self.view_editor = None

        self.model = QtGui.QStandardItemModel(self)
        if self.has_sub_array:
            self.view = QTreeView(self)
            self.view.setHeaderHidden(True)
        else:
            self.view = QListView(self)
            self.view.setSelectionBehavior(QListView.SelectionBehavior.SelectItems)
        self.view.doubleClicked.connect(self.list_edit)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view.setModel(self.model)
        self.view_layout.addWidget(self.view)



        if self.has_property_view:
            from ..PropertyViewport import PropertyViewport
            self.view_editor = PropertyViewport(self, self.praser)
            self.view_editor.sigPropertiesChanged.connect(self.onPropertyViewUpdate)
            self.field_layout.addWidget(self.view_editor)


        self.selection_model = self.view.selectionModel()
        self.selection_model.currentChanged.connect(self.updateSelected)

        self.updateList()

        self.btns_widget = QWidget(self)
        self.btns_widget.setContentsMargins(0,0,0,0)
        self.view_layout.addWidget(self.btns_widget)

        btns = QHBoxLayout(self.btns_widget)
        btns.setContentsMargins(0,0,0,0)
        btns.setSpacing(0)
        btns.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.btns_widget.setLayout(btns)

        if self.allow_length_changes == True:
            addButton = QPushButton(self.btns_widget)
            addButton.setIcon(IconRepository.iconLoader("material:plus"))
            addButton.setFixedHeight(24)
            addButton.clicked.connect(self.list_add)
            btns.addWidget(addButton)

            removeButton = QPushButton(self.btns_widget)
            removeButton.setIcon(IconRepository.iconLoader("material:minus"))
            removeButton.setFixedHeight(24)
            removeButton.clicked.connect(self.list_remove)
            btns.addWidget(removeButton)

        if self.allow_move == True:
            moveUpButton = QPushButton(self.btns_widget)
            moveUpButton.setIcon(IconRepository.iconLoader("material:arrow-up"))
            moveUpButton.setFixedHeight(24)
            moveUpButton.clicked.connect(self.list_moveUp)
            btns.addWidget(moveUpButton)

            moveDownButton = QPushButton(self.btns_widget)
            moveDownButton.setIcon(IconRepository.iconLoader("material:arrow-down"))  
            moveDownButton.setFixedHeight(24)
            moveDownButton.clicked.connect(self.list_moveDown)
            btns.addWidget(moveDownButton)

        editButton = QPushButton(self.btns_widget)
        editButton.setIcon(IconRepository.iconLoader("material:pencil"))                                                                                                                                                                                                                                                                                                                                 
        editButton.setFixedHeight(24)
        editButton.clicked.connect(self.list_edit)
        btns.addWidget(editButton)

        if self.allow_clipboard == True:
            moreButton = QPushButton(self.btns_widget)
            moreButton.setIcon(IconRepository.iconLoader("material:menu"))                                                                                                                                                                                                                                                                                                              
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


    def test_restrictions(self, manual_restrictions: list[dict[str, any]] = []):
        restrictions: list[dict[str, any]] = []
        if len(manual_restrictions) != 0: 
            restrictions = manual_restrictions
        else: 
            restrictions = self.praser.getObjectConstraints(self.propertyData)

        sub_array_setup = False

        for restriction in restrictions:
            if restriction["type"] == DataConstraints.ListMod.Subarray and sub_array_setup == False:
                self.nested_list_id: str = restriction["sub_id"]
                self.nested_list_nested_type: type = restriction["sub_type"]
                self.has_sub_array = True
                sub_array_setup = True
            if restriction["type"] == DataConstraints.ListMod.PropertyView:
                self.has_property_view = True
            if restriction["type"] == DataConstraints.ListMod.AddRemoveEditOnly:
                self.allow_move = False
                self.allow_clipboard = False
            if restriction["type"] == DataConstraints.ListMod.Inmovable:
                self.allow_move = False
            if restriction["type"] == DataConstraints.ListMod.Locked:
                self.allow_move = False
                self.allow_clipboard = False
                self.allow_length_changes = False


    #region Get / Set Functions

    def getNestedList(self, item: any):
        try:
            attr = getattr(item, self.nested_list_id)
            if isinstance(attr, TypedList):
                return attr
            else:
                return []
        except:
            return []

    def getParentContainer(self):
        return super().getParentContainer()    
    
    def setParentContainer(self, container: "PropertyGrid"):
        super().setParentContainer(container)
        if self.has_property_view: self.view_editor.setContainer(container)

    def getNewEditorPage(self):
        dlg = PropertyGrid_Dialog(self)
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        dlg.setWindowTitle(self.propertyData.variableName() + ' - ' + str(self.selected_item))
        dlg.setWindowFlags(Qt.WindowType.Widget)
        dlg.rejected.connect(self.updateList)
        
        container = QVBoxLayout(dlg)
        container.setContentsMargins(0,0,0,0)
        container.setSpacing(0)

        from ..PropertyViewport import PropertyViewport
        container_props = PropertyViewport(self.getParentContainer(), self.praser)
        container_props.setParent(dlg)
        container.addWidget(container_props)
        dlg.setLayout(container)

        return (container_props, dlg)

    def getEditableValue(self, item):
        if hasattr(item, "forceLoad"):
            item.forceLoad()
        return item     

    #endregion

    #region List Actions

    def list_moveUp(self):
        self.list_move('up')

    def list_moveDown(self):
        self.list_move('down')    

    def list_move(self, direction: Literal['up', 'down'] = 'up'):
        if self.selected_row != -1:
            if self.selected_sub_row != -1:
                variable = self.propertyData.currentData()
                length = len(variable)
                child = variable[self.selected_row]
                sub_variable = self.getNestedList(child)
                sub_length = len(sub_variable)

                oldIndex = self.selected_sub_row
                newIndex = self.selected_sub_row

                parentIndex = self.selected_row
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
                self.sigPropertyFieldChanged.emit()

            else:
                variable = self.propertyData.currentData()
                length = len(variable)

                oldIndex = self.selected_row
                newIndex = self.selected_row
                
                if direction == 'up':
                    if not newIndex - 1 < 0:
                        newIndex -= 1
                elif direction == 'down':
                    if not newIndex + 1 > length - 1:
                        newIndex += 1

                variable.insert(newIndex, variable.pop(oldIndex))
                self.updateList()
                self.selection_model.setCurrentIndex(self.model.index(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
                self.sigPropertyFieldChanged.emit()

    def list_add(self):
        self.list_modify("add")

    def list_edit(self):
        self.list_modify("edit")
    
    def list_modify(self, mode: Literal['edit', 'add'] = 'add'):
        if mode == 'add':
            if self.selected_sub_row != -1:
                newIndex = self.selected_sub_row + 1
                parent_row = self.selected_row
                editableValue = self.getEditableValue(type(self.selected_sub_item)())
                self.getNestedList(self.selected_item).append(editableValue)
                self.updateList()
                self.selection_model.setCurrentIndex(self.model.index(parent_row, 0).child(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
                self.sigPropertyFieldChanged.emit()
            else:
                newIndex = self.selected_row + 1
                editableValue = self.getEditableValue(self.variable_list_type())
                self.propertyData.variableData().append(editableValue)
                self.updateList()
                self.selection_model.setCurrentIndex(self.model.index(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
                self.sigPropertyFieldChanged.emit()
            
        elif mode == 'edit':
            prop_grid = None
            page_dialog = None

            if self.has_property_view: prop_grid = self.view_editor
            else: prop_grid, page_dialog = self.getNewEditorPage()


            if self.selected_row != -1:
                if self.selected_sub_row != -1:
                    prop_grid.setDataObject(self.selected_sub_item)
                else:
                    prop_grid.setDataObject(self.selected_item)

            if not self.has_property_view and page_dialog:
                self.getParentContainer().navigateForwards(page_dialog)
                page_dialog.show()

    def list_copy(self):
        item_type: type | None = None
        item_data: any | None = None

        if self.selected_row != -1:
            if self.selected_sub_row != -1:
                variable: TypedList = self.propertyData.currentData()
                item_type = type(self.selected_sub_item)
                item_data = copy.deepcopy(self.getNestedList(variable[self.selected_row])[self.selected_sub_row])
            else:
                variable: TypedList = self.propertyData.currentData()
                item_type = self.variable_list_type
                item_data = copy.deepcopy(variable[self.selected_row])

            if item_data != None and item_type != None:
                self.onItemDuplication(item_data)
                IconRepository.setSettingsClipboard(item_type, item_data)

    def list_paste(self):
        item_type: type | None = None
        
        if self.selected_row != -1:
            if self.selected_sub_row != -1: 
                item_type = type(self.selected_sub_item)
            else: 
                item_type = self.variable_list_type

            if item_type != None:
                clipboard_data = IconRepository.getSettingsClipboard(item_type)
                if clipboard_data != None:
                    pastable_data = copy.deepcopy(clipboard_data)
                    variable: TypedList = self.propertyData.currentData()
                    if self.selected_sub_row != -1:
                        list: TypedList = self.getNestedList(variable[self.selected_row])
                        list.append(pastable_data)
                    else:
                        variable.append(pastable_data)
                    self.updateList()

    def list_duplicate(self):
        if self.selected_row != -1:
            if self.selected_sub_row != -1:
                variable: TypedList = self.propertyData.currentData()
                list: TypedList = self.getNestedList(variable[self.selected_row])
                item = list[self.selected_sub_row]
                newItem = copy.deepcopy(item)
                self.onItemDuplication(newItem)
                list.append(newItem)
                self.updateList()
            else:
                variable: TypedList = self.propertyData.currentData()
                item = variable[self.selected_row]
                newItem = copy.deepcopy(item)
                self.onItemDuplication(newItem)
                variable.append(newItem)
                self.updateList()

    def list_remove(self):
        if self.selected_row != -1:
            if self.selected_sub_row != -1:
                variable: TypedList = self.propertyData.currentData()
                newIndex = self.selected_sub_row
                parent_row = self.selected_row
                list: TypedList = self.getNestedList(variable[self.selected_row])
                if not newIndex - 1 < 0:
                    newIndex -= 1
                list.pop(self.selected_sub_row)
                self.updateList()
                self.selection_model.setCurrentIndex(self.model.index(parent_row, 0).child(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
                self.sigPropertyFieldChanged.emit()
            else:
                variable: TypedList = self.propertyData.currentData()
                newIndex = self.selected_row
                if not newIndex - 1 < 0:
                    newIndex -= 1
                variable.pop(self.selected_row)
                self.updateList()
                self.selection_model.setCurrentIndex(self.model.index(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
                self.sigPropertyFieldChanged.emit()
    
    #endregion

    #region Update Actions

    def updateList(self):
        if self.selection_model: self.selection_model.blockSignals(True)

        self.model.index
        self.model.clear()
        index = 0

        indicies = []

        for varItem in self.propertyData.variableData():
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

        self.selected_row = -1
        self.selected_item = None
        self.selected_sub_row = -1
        self.selected_sub_item = None

        if self.has_property_view:
            self.updatePropertyView()

        if self.has_sub_array:
            QTimer.singleShot(100, self.view.expandAll)

        if self.selection_model: self.selection_model.blockSignals(False)

            
        
    def updateSelected(self, current: QModelIndex, previous: QModelIndex):
        x = -1
        y = -1

        if current.parent().row() == -1:
            y = -1
            x = current.row()
        else:
            y = current.row()
            x = current.parent().row()

        self.selected_row = x
        self.selected_sub_row = y



 
        if self.selected_row != -1:
            item = self.propertyData.currentData()[self.selected_row]
            self.selected_item = self.getEditableValue(item)
        else:
            self.selected_item = None

        if self.selected_item != None and self.selected_sub_row != -1:
            source = self.selected_item
            item = self.getNestedList(source)[self.selected_sub_row]
            self.selected_sub_item = self.getEditableValue(item)
        else:
            self.selected_sub_item = None

        if self.has_sub_array:
            self.view.expandAll()

        if self.has_property_view:
            self.updatePropertyView()

    def updatePropertyView(self):
        if not self.has_property_view: return
        if self.view_editor == None: return

        if self.selected_row != -1:
            if self.selected_sub_row != -1:
                self.view_editor.setDataObject(self.selected_sub_item)
            else:
                self.view_editor.setDataObject(self.selected_item)
        else:
            self.view_editor.setDataObject(None)
    
    #endregion

    #region Signal Recievers

    def onItemDuplication(self, item):
        if hasattr(item, "propertygrid_on_duplicate"):
            item.propertygrid_on_duplicate()   
    
    #endregion