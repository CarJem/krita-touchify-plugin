from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import PropertyUtils_Extensions



ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.components.touchify.property_grid.PropertyPage import PropertyPage


class PropertyView(QObject):

    def __init__(self, parent: "PropertyPage"):
        super(PropertyView, self).__init__(parent)
        self.parent_page: "PropertyPage" = parent
        self.item = None

    def getHiddenVariableNames(self):
        if self.item == None:
            return
        
        hidden_variables = []
        variables_requested_to_hide = PropertyUtils_Extensions.classHiddenVariables(self.item)
        variable_names, b, c = self.getClassVariablesWithSisters(self.item)

        hidden_variables.append("json_version")

        for varName in variable_names:
            if varName.startswith("INTERNAL_"):
                hidden_variables.append(varName)

        for varName in variables_requested_to_hide:
            if varName in variables_requested_to_hide:
                hidden_variables.append(varName)
        
        return hidden_variables
        
    def getClassVariablesWithSisters(self, item):
        known_sisters = []
        sister_props = []

        sister_data = PropertyUtils_Extensions.classSisters(item)
        variable_data = PropertyUtils_Extensions.getClassVariables(item)
        limiters = self.parent_page.limiters

        for var_name in variable_data[:]:
            if var_name.startswith("INTERNAL_") or var_name == "json_version":
                variable_data.remove(var_name)

        for sister_id in sister_data:
            sister_id: str
            sister_items = list[str](sister_data[sister_id]["items"])
            known_sisters.append(str(sister_id))

            for sister_variable in sister_items:
                if sister_variable in variable_data:
                    if sister_id not in variable_data:
                        index = variable_data.index(str(sister_variable))
                        variable_data.insert(index, str(sister_id))
                    variable_data.remove(sister_variable)
                    sister_props.append(sister_variable)

        if len(limiters) != 0:
            result = []
            for limiter in limiters:
                if limiter in variable_data or limiter in sister_props:
                    result.append(limiter)
            return result, known_sisters, sister_data
        else:
            return variable_data, known_sisters, sister_data

    def setStackHost(self, host):
        pass
    
    def onPropertyChanged(self, value: bool):
        pass

    def unloadPropertyView(self):
        pass

    def updateDataObject(self, item):
        self.item = item

