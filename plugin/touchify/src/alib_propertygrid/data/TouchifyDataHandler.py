
from typing import TYPE_CHECKING
from jemlib.alib_propertygrid.data.DataExtension import DataExtension
from jemlib.alib_propertygrid.data.DataPath import DataPath
from touchify.src.alib_propertygrid.fields.PropertyField_ToolboxDataItem import PropertyField_ToolboxDataItem
from touchify.src.alib_propertygrid.fields.PropertyField_ToolboxDataSubitem import PropertyField_ToolboxDataSubitem
from touchify.src.alib_propertygrid.fields.PropertyField_TriggerGroups import PropertyField_TriggerGroups
from touchify.src.alib_propertygrid.fields.PropertyField_TriggerList import PropertyField_TriggerList


if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class TouchifyDataHandler(DataExtension):


    @staticmethod
    def Praser():
        from jemlib.alib_propertygrid.data.DataHandler import DataHandler
        praser = DataHandler()
        praser.installExtension(TouchifyDataHandler())
        return praser

    def __init__(self):
        super().__init__()

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
        