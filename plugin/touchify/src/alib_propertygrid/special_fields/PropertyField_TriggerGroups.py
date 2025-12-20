from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from touchify.src.config.triggers.Trigger import Trigger
from touchify.src.config.triggers.TriggerGroup import TriggerGroup
from jemlib.alib_propertygrid.fields.PropertyField_TypedList import PropertyField_TypedList
from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_propertygrid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions
from jemlib.managers.IconRepository import *



class PropertyField_TriggerGroups(PropertyField_TypedList):
    def __init__(self, variable_name=str, variable_data=TypedList[TriggerGroup], variable_source=any):
        manual_restrictions = [PropertyGrid_Restrictions.listSubArray("actions", Trigger)]
        super(PropertyField_TriggerGroups, self).__init__(variable_name, variable_data, variable_source, manual_restrictions)