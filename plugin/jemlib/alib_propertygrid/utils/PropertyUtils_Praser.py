
# Field Imports
from jemlib.alib_propertygrid.fields.PropertyField import PropertyField
from jemlib.alib_propertygrid.fields.PropertyField_Float import PropertyField_Float
from jemlib.alib_propertygrid.fields.PropertyField_Int import PropertyField_Int
from jemlib.alib_propertygrid.fields.PropertyField_Bool import PropertyField_Bool
from jemlib.alib_propertygrid.fields.PropertyField_Str import PropertyField_Str
from jemlib.alib_propertygrid.fields.PropertyField_TypedList import PropertyField_TypedList

# Special Field Imports
from jemlib.alib_propertygrid.special_fields.PropertyField_KsColor import PropertyField_KsColor

#Type Imports
from jemlib.alib_datatypes.TypedList import TypedList



class PropertyUtils_Praser:

    def __init__(self):
        self.__prasers: list[PropertyUtils_PraserExtension] = []
        self.installPraser(PropertyUtils_PraserExtension())

    def installPraser(self, praser: "PropertyUtils_PraserExtension"):
        self.__prasers.append(praser)

    def isSpecialType(self, varName, variable, item):
        for praser in self.__prasers:
            if praser.isSpecialType(varName, variable, item):
                return True
        return False

    def getSpecialType(self, varName, variable, item):
        for praser in self.__prasers:
            result = praser.getSpecialType(varName, variable, item)
            if result: return result
        return PropertyField(varName, variable, item)


    @staticmethod
    def getListType(variable: any):
        varType = type(variable)
        if varType == TypedList:
            list: TypedList = variable
            listType = list.allowedTypes()
            if listType != None and listType != tuple:
                return listType
        return None

    def getPropertyType(self, varName, variable, item):
        varType = type(variable)
        
        if self.isSpecialType(varName, variable, item):
            return self.getSpecialType(varName, variable, item)
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
        
class PropertyUtils_PraserExtension:

    def __init__(self):
        pass
    
    def isSpecialType(self, varName, variable, item):
        from jemlib.alib_kis.dataclass.KisColor import KisColor
        varType = type(variable)
        listType = PropertyUtils_Praser.getListType(variable)
        
        if varType == KisColor:
            return True
        else:
            return False

    def getSpecialType(self, varName, variable, item):
        from jemlib.alib_kis.dataclass.KisColor import KisColor
        varType = type(variable)
        listType = PropertyUtils_Praser.getListType(variable)
        
        if varType == KisColor:
            return PropertyField_KsColor(varName, variable, item)
        else:
            return None