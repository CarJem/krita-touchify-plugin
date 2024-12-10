
# Field Imports
from touchify.src.components.touchify.property_grid.fields.PropertyField import PropertyField
from touchify.src.components.touchify.property_grid.fields.PropertyField_Float import PropertyField_Float
from touchify.src.components.touchify.property_grid.fields.PropertyField_Int import PropertyField_Int
from touchify.src.components.touchify.property_grid.fields.PropertyField_Bool import PropertyField_Bool
from touchify.src.components.touchify.property_grid.fields.PropertyField_Str import PropertyField_Str
from touchify.src.components.touchify.property_grid.fields.PropertyField_TypedList import PropertyField_TypedList

# Special Field Imports
from touchify.src.components.touchify.property_grid.special_fields.PropertyField_KsColor import PropertyField_KsColor
from touchify.src.components.touchify.property_grid.special_fields.PropertyField_ActionCollection import PropertyField_ActionCollection
from touchify.src.components.touchify.property_grid.special_fields.PropertyField_ActionList import PropertyField_ActionList

#Type Imports
from touchify.src.ext.types.TypedList import TypedList

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
        from touchify.src.cfg.action.CfgTouchifyActionCollection import CfgTouchifyActionCollection
        from touchify.src.cfg.action.CfgTouchifyAction import CfgTouchifyAction
        from touchify.src.ext.KritaSettings import KS_Color
        varType = type(variable)
        listType = PropertyUtils_Praser.getListType(variable)
        
        if listType == CfgTouchifyActionCollection:
            return True
        if listType == CfgTouchifyAction:
            return True
        elif varType == KS_Color:
            return True
        else:
            return False

    def getSpecialType(varName, variable, item):
        from touchify.src.cfg.action.CfgTouchifyActionCollection import CfgTouchifyActionCollection
        from touchify.src.cfg.action.CfgTouchifyAction import CfgTouchifyAction
        from touchify.src.ext.KritaSettings import KS_Color
        varType = type(variable)
        listType = PropertyUtils_Praser.getListType(variable)
        
        if listType == CfgTouchifyActionCollection:
            return PropertyField_ActionCollection(varName, variable, item)
        if listType == CfgTouchifyAction:
            return PropertyField_ActionList(varName, variable, item)
        elif varType == KS_Color:
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