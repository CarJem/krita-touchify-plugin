
from typing import TYPE_CHECKING
from jemlib.alib_propertygrid.data.DataExtension import DataExtension
from jemlib.alib_propertygrid.data.DataPath import DataPath
from touchify.src.alib_propertygrid.fields.PropertyField_ToolboxDataItem import PropertyField_ToolboxDataItem
from touchify.src.alib_propertygrid.fields.PropertyField_ToolboxDataSubitem import PropertyField_ToolboxDataSubitem
from touchify.src.alib_propertygrid.fields.PropertyField_TriggerGroups import PropertyField_TriggerGroups
from touchify.src.alib_propertygrid.fields.PropertyField_TriggerList import PropertyField_TriggerList
from touchify.src.alib_propertygrid.fields.PropertyField_ConditionBuilder import PropertyField_ConditionBuilder


if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class TouchifyDataExtension(DataExtension):


    @staticmethod
    def Praser():
        from jemlib.alib_propertygrid.data.DataHandler import DataHandler
        praser = DataHandler()
        praser.installExtension(TouchifyDataExtension())
        return praser

    def __init__(self):
        super().__init__()


    def isOverridenType(self, property: DataPath):
        from touchify.src.alib_propertygrid.data.TouchifyDataConstraints import TouchifyDataConstraints as DCT
        if not self.getGlobalHandler(): return False

        value: str | None = self.getGlobalHandler().getObjectValueTypeOverride(property)
        if not value: return False

        match value:
            case DCT.TypeOverride.RestrictionContextBuilder:
                return True
            case _:
                return False
    
    def isSpecialType(self, property: DataPath):
        from touchify.src.config.triggers.TriggerGroup import TriggerGroup
        from touchify.src.config.triggers.Trigger import Trigger
        from touchify.src.config.toolbox.ToolboxDataItem import ToolboxDataItem
        from touchify.src.config.toolbox.ToolboxDataSubitem import ToolboxDataSubitem
        varType = property.variableType()
        listType = property.variableListType()
        
        if listType == ToolboxDataItem:
            return True
        elif listType == ToolboxDataSubitem:
            return True
        elif listType == TriggerGroup:
            return True
        elif listType == Trigger:
            return True
        else:
            return False
        
    def getOverridenType(self,  handler: "DataHandler", property: DataPath):
        from touchify.src.alib_propertygrid.data.TouchifyDataConstraints import TouchifyDataConstraints as DCT
        if not self.getGlobalHandler(): return None

        value: str | None = self.getGlobalHandler().getObjectValueTypeOverride(property)
        if not value: return None

        match value:
            case DCT.TypeOverride.RestrictionContextBuilder:
                return PropertyField_ConditionBuilder(handler, property)
            case _:
                return None

    def getSpecialType(self, handler: "DataHandler", property: DataPath):
        from touchify.src.config.triggers.TriggerGroup import TriggerGroup
        from touchify.src.config.triggers.Trigger import Trigger
        from touchify.src.config.toolbox.ToolboxDataItem import ToolboxDataItem
        from touchify.src.config.toolbox.ToolboxDataSubitem import ToolboxDataSubitem
        varType = property.variableType()
        listType = property.variableListType()
        
        if listType == TriggerGroup:
            return PropertyField_TriggerGroups(handler, property)
        elif listType == Trigger:
            return PropertyField_TriggerList(handler, property)
        elif listType == ToolboxDataItem:
            return PropertyField_ToolboxDataItem(handler, property)
        elif listType == ToolboxDataSubitem:
            return PropertyField_ToolboxDataSubitem(handler, property)
        else:
            return None
        