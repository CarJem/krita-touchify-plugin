from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from touchify.src.cfg.triggers.Trigger import Trigger
from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup
from touchify.src.components.touchify.property_grid.fields.PropertyField_TypedList import PropertyField_TypedList
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.resources import *



class PropertyField_TriggerGroups(PropertyField_TypedList):
    def __init__(self, variable_name=str, variable_data=TypedList[TriggerGroup], variable_source=any):
        manual_restrictions = [
            {
                "type": "sub_array",
                "sub_id": "actions",
                "sub_type": Trigger
            }
        ]
        super(PropertyField_TriggerGroups, self).__init__(variable_name, variable_data, variable_source, manual_restrictions)