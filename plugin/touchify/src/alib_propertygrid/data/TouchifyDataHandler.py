
from typing import TYPE_CHECKING
from jemlib.alib_propertygrid.data.DataExtension import DataExtension
from jemlib.alib_propertygrid.data.DataPath import DataPath
from touchify.src.alib_propertygrid.fields.PropertyField_TriggerGroups import PropertyField_TriggerGroups
from touchify.src.alib_propertygrid.fields.PropertyField_TriggerList import PropertyField_TriggerList

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class TouchifyDataHandler(DataExtension):

    def __init__(self):
        super().__init__()

    def isSpecialType(self, property: DataPath):
        from touchify.src.config.triggers.TriggerGroup import TriggerGroup
        from touchify.src.config.triggers.Trigger import Trigger
        varType = property.variableType()
        listType = property.variableListType()
        
        if listType == TriggerGroup:
            return True
        if listType == Trigger:
            return True
        else:
            return False

    def getSpecialType(self, handler: "DataHandler", property: DataPath):
        from touchify.src.config.triggers.TriggerGroup import TriggerGroup
        from touchify.src.config.triggers.Trigger import Trigger
        varType = property.variableType()
        listType = property.variableListType()
        
        if listType == TriggerGroup:
            return PropertyField_TriggerGroups(handler, property)
        elif listType == Trigger:
            return PropertyField_TriggerList(handler, property)
        else:
            return None
        