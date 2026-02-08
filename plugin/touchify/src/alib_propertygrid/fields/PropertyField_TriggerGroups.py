from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from jemlib.alib_propertygrid.data.DataPath import DataPath
from touchify.src.alib_propertygrid.fields.PropertyField_TouchifyExtras import PropertyField_TouchifyExtras
from jemlib.api_touchify.config.triggers.Trigger import Trigger
from jemlib.api_touchify.config.triggers.TriggerGroup import TriggerGroup
from jemlib.alib_propertygrid.fields.PropertyField_TypedList import PropertyField_TypedList
from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.managers.IconRepository import *

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class PropertyField_TriggerGroups(PropertyField_TypedList):
    def __init__(self, handler: "DataHandler", property: DataPath[TypedList[TriggerGroup]]):
        manual_restrictions = [DataConstraints.listSubArray("actions", Trigger), DataConstraints.listMod(DataConstraints.ListMod.Icons)]
        super(PropertyField_TriggerGroups, self).__init__(handler, property, manual_restrictions)

    def list_on_quick_add(self, source: Trigger):
        if self.selected_sub_row != -1:
            newIndex = self.selected_sub_row + 1
            parentIndex = self.selected_row
            self.getNestedList(self.selected_item).append(source)
            self.updateList()
            self.selection_model.setCurrentIndex(self.model.index(parentIndex, 0).child(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
            self.sigPropertyFieldChanged.emit()

    def list_add(self):
        if self.selected_sub_row != -1:
            PropertyField_TouchifyExtras.trigger_list_quick_add(self)
        else:
            super().list_add()