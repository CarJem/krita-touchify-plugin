
from jemlib.alib_propertygrid.utils.PropertyUtils_Praser import PropertyUtils_Praser, PropertyUtils_PraserExtension
from touchify.src.alib_propertygrid.special_fields.PropertyField_TriggerGroups import PropertyField_TriggerGroups
from touchify.src.alib_propertygrid.special_fields.PropertyField_TriggerList import PropertyField_TriggerList



class PropertyUtils_TouchifyPraser(PropertyUtils_PraserExtension):

    def __init__(self):
        super().__init__()

    def isSpecialType(self, varName, variable, item):
        from touchify.src.config.triggers.TriggerGroup import TriggerGroup
        from touchify.src.config.triggers.Trigger import Trigger
        varType = type(variable)
        listType = PropertyUtils_Praser.getListType(variable)
        
        if listType == TriggerGroup:
            return True
        if listType == Trigger:
            return True
        else:
            return False

    def getSpecialType(self, varName, variable, item):
        from touchify.src.config.triggers.TriggerGroup import TriggerGroup
        from touchify.src.config.triggers.Trigger import Trigger
        varType = type(variable)
        listType = PropertyUtils_Praser.getListType(variable)
        
        if listType == TriggerGroup:
            return PropertyField_TriggerGroups(varName, variable, item)
        elif listType == Trigger:
            return PropertyField_TriggerList(varName, variable, item)
        else:
            return None
        