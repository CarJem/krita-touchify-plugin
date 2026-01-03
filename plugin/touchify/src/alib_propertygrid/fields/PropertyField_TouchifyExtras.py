from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from touchify.src.alib_propertygrid.dialogs.QuickActionPickerDialog import QuickToolItemPickerDialog
from touchify.src.alib_propertygrid.dialogs.QuickTriggerPickerDialog import QuickTriggerPickerDialog
from jemlib.managers.IconRepository import *

if TYPE_CHECKING:
    from touchify.src.alib_propertygrid.fields.PropertyField_ToolboxDataItem import PropertyField_ToolboxDataItem
    from touchify.src.alib_propertygrid.fields.PropertyField_TriggerGroups import PropertyField_TriggerGroups
    from touchify.src.alib_propertygrid.fields.PropertyField_TriggerList import PropertyField_TriggerList
    from touchify.src.alib_propertygrid.fields.PropertyField_TriggerMenuItemList import PropertyField_TriggerMenuItemList

class PropertyField_TouchifyExtras:
    @staticmethod
    def triggermenuitem_list_quick_add(parent: "PropertyField_TriggerMenuItemList"):
        dlg = QuickTriggerPickerDialog(parent, menuMode=True)
        dlg.sigOnNewItem.connect(parent.list_on_quick_add)
        dlg.exec()

    @staticmethod
    def trigger_list_quick_add(parent: "PropertyField_TriggerGroups | PropertyField_TriggerList"):
        dlg = QuickTriggerPickerDialog(parent)
        dlg.sigOnNewItem.connect(parent.list_on_quick_add)
        dlg.exec()

    @staticmethod
    def toolbox_item_list_quick_add(parent: "PropertyField_ToolboxDataItem"):
        dlg = QuickToolItemPickerDialog(parent)
        dlg.sigOnNewItem.connect(parent.list_on_quick_add)
        dlg.exec()



        