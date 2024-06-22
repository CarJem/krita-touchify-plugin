from .PropertyField import *
from .PropertyField_Float import *
from .PropertyField_Int import *
from .PropertyField_Bool import *
from .PropertyField_Str import *
from .PropertyField_TypedList import *
from .PropertyField_TempValue import *

class PropertyUtils_Praser:
    def getPropertyType(varName, variable, item):
        varType = type(variable)
        if varType == str:
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