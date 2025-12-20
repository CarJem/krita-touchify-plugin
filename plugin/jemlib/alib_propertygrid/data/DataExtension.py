from typing import TYPE_CHECKING
from jemlib.alib_propertygrid.data.DataPath import DataPath
from jemlib.alib_propertygrid.fields.PropertyField_KsColor import PropertyField_KsColor

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler


class DataExtension:

    def __init__(self):
        pass
    
    def isSpecialType(self, property: DataPath):
        from jemlib.alib_kis.dataclass.KisColor import KisColor
        varType = property.variableType()
        listType = property.variableListType()
        
        if varType == KisColor:
            return True
        else:
            return False

    def getSpecialType(self, handler: "DataHandler", property: DataPath):
        from jemlib.alib_kis.dataclass.KisColor import KisColor
        varType = property.variableType()
        listType = property.variableListType()
        
        if varType == KisColor:
            return PropertyField_KsColor(handler, property)
        else:
            return None