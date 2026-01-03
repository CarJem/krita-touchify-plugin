from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_propertygrid.data.DataPath import DataPath
from touchify.src.alib_propertygrid.fields.PropertyField_TouchifyExtras import PropertyField_TouchifyExtras
from touchify.src.config.menu.TriggerMenuItem import TriggerMenuItem
from touchify.src.config.triggers.Trigger import Trigger
from jemlib.alib_propertygrid.fields.PropertyField_TypedList import PropertyField_TypedList
from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.managers.IconRepository import *

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class PropertyField_TriggerMenuItemList(PropertyField_TypedList):
    def __init__(self, handler: "DataHandler", property: DataPath[TypedList[TriggerMenuItem]]):
        manual_restrictions = [DataConstraints.listMod(DataConstraints.ListMod.Icons)]
        super(PropertyField_TriggerMenuItemList, self).__init__(handler, property, manual_restrictions)

    def list_on_quick_add(self, source: Trigger):
        newIndex = self.selected_row + 1
        self.propertyData.variableData().append(source)
        self.updateList()
        self.selection_model.setCurrentIndex(self.model.index(newIndex, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
        self.sigPropertyFieldChanged.emit()

    def list_add(self):
        PropertyField_TouchifyExtras.triggermenuitem_list_quick_add(self)

        