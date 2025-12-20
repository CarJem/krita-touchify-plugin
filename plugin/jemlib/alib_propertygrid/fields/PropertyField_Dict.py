from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *



from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_propertygrid.data.DataPath import DataPath
from jemlib.alib_propertygrid.fields.PropertyField import PropertyField
from jemlib.alib_propertygrid.fields.PropertyField_TypedList import PropertyField_TypedList
from jemlib.managers.IconRepository import *

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler
    from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid



class PropertyField_Dict(PropertyField[dict]):

    class Workspace:
        def __init__(self):
            pass

    def __init__(self, handler: "DataHandler", property: DataPath[dict]):
        super().__init__(handler, property, True)

        mode = "default"
        restrictions = handler.getObjectConstraints(property)
        for restriction in restrictions:
            if restriction["type"] == DataConstraints.DictMod.ListLike:
                mode = DataConstraints.DictMod.ListLike

        if mode == DataConstraints.DictMod.ListLike:
            self.listViewer(handler, property)
        else:
            self.standardViewer(handler, property)

    def setStackHost(self, host: "PropertyGrid"):
        self.stack_host = host
        if hasattr(self, "list_view"):
            self.list_view.setStackHost(self.stack_host)

    def listViewer(self, handler: "DataHandler", property: DataPath[dict]):
        keyType = type(property.variableData().keys().__iter__().__next__())
        valueType = type(property.variableData().values().__iter__().__next__())
        items = list(property.variableData().values())

        print(valueType)
        print(items)

        working_list = TypedList(items, valueType)

        workspace = PropertyField_Dict.Workspace()
        workspace.__setattr__("working", working_list)
        
        emulated_property = DataPath("working", workspace)
        
        self.list_view = PropertyField_TypedList(handler, emulated_property, [DataConstraints.listMod(DataConstraints.ListMod.Locked)])
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.list_view)

    def standardViewer(self, handler: "DataHandler", property: DataPath[dict]):
        def fillModel(parent, d):
            if isinstance(d, dict):
                input = d.items()
            elif isinstance(d, list):
                input = enumerate(d)
            else:
                input = None

            if not input: 
                return
            
            for key, value in input:
                it = QtGui.QStandardItem(str(key))
                if isinstance(value, dict) or isinstance(value, list):
                    parent.appendRow(it)
                    fillModel(it, value)
                else:
                    it2 = QtGui.QStandardItem(str(value))
                    parent.appendRow([it, it2])

        self.tree = QtWidgets.QTreeView(self)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.tree)

        root_model = QtGui.QStandardItemModel()
        self.tree.setModel(root_model)
        self.tree.model().setHorizontalHeaderLabels(['Level','Values'])
        fillModel(root_model.invisibleRootItem(), self.propertyData.variableData())

