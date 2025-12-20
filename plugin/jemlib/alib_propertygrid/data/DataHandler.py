
# Field Imports
from copy import deepcopy
from jemlib.alib_propertygrid.data.DataPath import DataPath
from jemlib.alib_propertygrid.fields.PropertyField_Dict import PropertyField_Dict
from jemlib.alib_propertygrid.fields.PropertyField import PropertyField
from jemlib.alib_propertygrid.fields.PropertyField_Float import PropertyField_Float
from jemlib.alib_propertygrid.fields.PropertyField_Int import PropertyField_Int
from jemlib.alib_propertygrid.fields.PropertyField_Bool import PropertyField_Bool
from jemlib.alib_propertygrid.fields.PropertyField_Str import PropertyField_Str
from jemlib.alib_propertygrid.fields.PropertyField_TypedList import PropertyField_TypedList

# Special Field Imports
from jemlib.alib_propertygrid.data.DataExtension import DataExtension

#Type Imports
from jemlib.alib_datatypes.TypedList import TypedList



class DataHandler:

    def __init__(self):
        self.__extensions: list[DataExtension] = []
        self.installExtension(DataExtension())

    def installExtension(self, ext: "DataExtension"):
        self.__extensions.append(ext)

    def isSpecialType(self, property: DataPath):
        for praser in self.__extensions:
            if praser.isSpecialType(property):
                return True
        return False

    def getSpecialType(self, property: DataPath):
        for praser in self.__extensions:
            result = praser.getSpecialType(self, property)
            if result: return result
        return PropertyField(self, property)
    
    def getPropertyVariable(self, variable_source, variable_name):
        return DataPath(variable_name, variable_source)

    def getPropertyField(self, property: DataPath):
        varType = property.variableType()
        
        if self.isSpecialType(property):
            return self.getSpecialType(property)
        elif varType == str:
            return PropertyField_Str(self, property)
        elif varType == int:
            return PropertyField_Int(self, property)
        elif varType == float:
            return PropertyField_Float(self, property)            
        elif varType == bool:
            return PropertyField_Bool(self, property)
        elif varType == dict:
            return PropertyField_Dict(self, property)
        elif varType == TypedList:
            return PropertyField_TypedList(self, property)
        else:
            return PropertyField(self, property)

    def getPropertyLabel(self, labelData: dict[str,str], variable_name: str):
        resultText = variable_name
        if variable_name in labelData:
            propData = labelData[variable_name]
            if propData != None:
                resultText = propData
        return resultText
    
    def getPropertyTextHint(self, hintData: dict[str,str], variable_name: str):
        hintText = ""
        if variable_name in hintData:
            hintText = str(hintData[variable_name])
        return hintText

    def getObjectVariableLabels(self, obj):
        if hasattr(obj, "propertygrid_labels"):
            return deepcopy(dict(obj.propertygrid_labels()))
        else: return deepcopy({})

    def getObjectVariableTextHints(self, obj):
        if hasattr(obj, "propertygrid_hints"):
            return dict(obj.propertygrid_hints())
        else: return {}

    def getObjectHiddenVariables(self, obj) -> list[str]:
        if hasattr(obj, "propertygrid_hidden"):
            return list(obj.propertygrid_hidden())
        else: return []

    def getObjectVariableGroups(self, obj):
        if hasattr(obj, "propertygrid_sisters"):
            return deepcopy(dict(obj.propertygrid_sisters()))
        else: return deepcopy({})

    def getObjectVariables(self, obj: any):
        sorted_results = []
        sister_items = []

        if hasattr(obj, "propertygrid_sorted"):
            sorted_results = list[str](obj.propertygrid_sorted())
        else:
            sorted_results = []

        if hasattr(obj, "propertygrid_sisters"):
            sister_items = list[str](dict(obj.propertygrid_sisters()).keys())
            
        found_results = [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and
                not attr.startswith("__") and
                not attr.startswith("_"  + type(obj).__name__ + "__")]
        
        for item in sorted_results[:]:
            if item not in found_results and item not in sister_items and item.startswith("#") == False:
                sorted_results.remove(item)
        
        for item in found_results:
            if item not in sorted_results:
                sorted_results.append(item)

        for item in sister_items:
            if item not in sorted_results:
                sorted_results.append(item)
                
        return sorted_results

    def getObjectViewType(self, obj: any):
        if hasattr(obj, "propertygrid_view_type"):
            return str(obj.propertygrid_view_type())
        return "default"

    def getObjectConstraints(self, property: DataPath) -> list[dict[str, any]]:
        if hasattr(property.variableSource(), "propertygrid_restrictions"):
            cfg =  dict(property.variableSource().propertygrid_restrictions())
            if property.variableName() in cfg:
                result = cfg[property.variableName()]
                returnable_result = []
                if isinstance(result, dict):
                    returnable_result.append(result)
                elif isinstance(result, list):
                    returnable_result = result
                
                return returnable_result
        return []
