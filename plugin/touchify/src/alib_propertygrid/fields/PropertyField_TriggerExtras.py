from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from touchify.src.alib_propertygrid.dialogs.ActionPickerDialog import ActionPickerDialog
from jemlib.managers.IconRepository import *

if TYPE_CHECKING:
    from touchify.src.alib_propertygrid.fields.PropertyField_TriggerGroups import PropertyField_TriggerGroups
    from touchify.src.alib_propertygrid.fields.PropertyField_TriggerList import PropertyField_TriggerList

class PropertyField_TriggerExtras:
    @staticmethod
    def list_quick_add(parent: "PropertyField_TriggerGroups | PropertyField_TriggerList"):
        dlg = ActionPickerDialog(parent)
        dlg.sigOnNewItem.connect(parent.list_on_quick_add)
        dlg.exec()



        