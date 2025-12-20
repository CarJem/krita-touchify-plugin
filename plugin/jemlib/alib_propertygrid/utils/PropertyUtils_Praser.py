
# Field Imports
from jemlib.alib_propertygrid.fields.PropertyField import PropertyField
from jemlib.alib_propertygrid.fields.PropertyField_Float import PropertyField_Float
from jemlib.alib_propertygrid.fields.PropertyField_Int import PropertyField_Int
from jemlib.alib_propertygrid.fields.PropertyField_Bool import PropertyField_Bool
from jemlib.alib_propertygrid.fields.PropertyField_Str import PropertyField_Str
from jemlib.alib_propertygrid.fields.PropertyField_TypedList import PropertyField_TypedList

# Special Field Imports
from jemlib.alib_propertygrid.special_fields.PropertyField_KsColor import PropertyField_KsColor
from jemlib.alib_propertygrid.special_fields.PropertyField_TriggerGroups import PropertyField_TriggerGroups
from jemlib.alib_propertygrid.special_fields.PropertyField_TriggerList import PropertyField_TriggerList

#Type Imports
from jemlib.alib_datatypes.TypedList import TypedList

class PropertyUtils_Praser:


    def getListType(variable: any):
        varType = type(variable)
        if varType == TypedList:
            list: TypedList = variable
            listType = list.allowedTypes()
            if listType != None and listType != tuple:
                return listType
        return None

    def isSpecialType(varName, variable, item):
        from touchify.src.config.triggers.TriggerGroup import TriggerGroup
        from touchify.src.config.triggers.Trigger import Trigger
        from jemlib.alib_kis.dataclass.KisColor import KisColor
        varType = type(variable)
        listType = PropertyUtils_Praser.getListType(variable)
        
        if listType == TriggerGroup:
            return True
        if listType == Trigger:
            return True
        elif varType == KisColor:
            return True
        else:
            return False

    def getSpecialType(varName, variable, item):
        from touchify.src.config.triggers.TriggerGroup import TriggerGroup
        from touchify.src.config.triggers.Trigger import Trigger
        from jemlib.alib_kis.dataclass.KisColor import KisColor
        varType = type(variable)
        listType = PropertyUtils_Praser.getListType(variable)
        
        if listType == TriggerGroup:
            return PropertyField_TriggerGroups(varName, variable, item)
        if listType == Trigger:
            return PropertyField_TriggerList(varName, variable, item)
        elif varType == KisColor:
            return PropertyField_KsColor(varName, variable, item)
        else:
            return PropertyField(varName, variable, item)

    def getPropertyType(varName, variable, item):
        varType = type(variable)
        
        if PropertyUtils_Praser.isSpecialType(varName, variable, item):
            return PropertyUtils_Praser.getSpecialType(varName, variable, item)
        elif varType == str:
            return PropertyField_Str(varName, variable, item)
        elif varType == int:
            return PropertyField_Int(varName, variable, item)
        elif varType == float:
            return PropertyField_Float(varName, variable, item)            
        elif varType == bool:
            return PropertyField_Bool(varName, variable, item)
        elif varType == TypedList:
            return PropertyField_TypedList(varName, variable, item)
        else:
            return PropertyField(varName, variable, item)