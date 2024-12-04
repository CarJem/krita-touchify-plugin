from copy import deepcopy
from PyQt5.QtWidgets import QMessageBox


class PropertyUtils_Extensions:

    def tryGetVariable(obj, varName):
        if hasattr(obj, varName):
            return getattr(obj, varName)
        else: return None

    def getVariable(obj, varName):
        return getattr(obj, varName)

    def setVariable(obj, varName, data):
        return setattr(obj, varName, data)

    def getClassVariables(obj):
        sorted_results = []
        if hasattr(obj, "propertygrid_sorted"):
            sorted_results = list[str](obj.propertygrid_sorted())
        else:
            sorted_results = []
            
        found_results = [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and
                not attr.startswith("__") and
                not attr.startswith("_"  + type(obj).__name__ + "__")]
        
        for item in sorted_results:
            if item not in found_results:
                sorted_results.remove(item)
        
        for item in found_results:
            if item not in sorted_results:
                sorted_results.append(item)
        return sorted_results
                
    def classRestrictions(obj):
        if hasattr(obj, "propertygrid_restrictions"):
            return dict(obj.propertygrid_restrictions())
        else: return {}            

    def classSisters(obj):
        if hasattr(obj, "propertygrid_sisters"):
            return deepcopy(dict(obj.propertygrid_sisters()))
        else: return deepcopy({})

    def classHiddenVariables(obj) -> list[str]:
        if hasattr(obj, "propertygrid_hidden"):
            return list(obj.propertygrid_hidden())
        else: return []

    def classVariableLabels(obj):
        if hasattr(obj, "propertygrid_labels"):
            return deepcopy(dict(obj.propertygrid_labels()))
        else: return deepcopy({})

    def classVariableHints(obj):
        if hasattr(obj, "propertygrid_hints"):
            return dict(obj.propertygrid_hints())
        else: return {}

    def classIsModel(obj):
        return hasattr(obj, "propertygrid_ismodel")


    def getVariableLabel(labelData: dict[str,str], variable_name: str):
        resultText = variable_name
        if variable_name in labelData:
            propData = labelData[variable_name]
            if propData != None:
                resultText = propData
        return resultText
    
    def getVariableHint(hintData: dict[str,str], variable_name: str):
        hintText = ""
        if variable_name in hintData:
            hintText = str(hintData[variable_name])
        return hintText

    def quickDialog(parent, text):
        dlg = QMessageBox(parent)
        dlg.setText(text)
        dlg.show()

    def clearLayout(layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    PropertyUtils_Extensions.clearLayout(child.layout())