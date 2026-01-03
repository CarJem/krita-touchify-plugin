from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from jemlib.alib_propertygrid.data.DataHandler import DataHandler



ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from jemlib.alib_propertygrid.PropertyViewport import PropertyViewport


class PropertyView(QObject):

    def __init__(self, parent: "PropertyViewport", praser: DataHandler):
        super(PropertyView, self).__init__(parent)

        self.__praser: DataHandler = praser
        self.__viewport: "PropertyViewport" = parent
        self.__item = None


    def getHiddenVariableNames(self):
        if self.__item == None:
            return
        
        hidden_variables = []
        variables_requested_to_hide = self.__praser.getObjectHiddenVariables(self.__item)
        variable_names, known_sisters, sister_data = self.getClassVariablesWithSisters(self.__item, False)

        hidden_variables.append("json_version")

        for varName in variable_names:
            if varName.startswith("INTERNAL_"):
                hidden_variables.append(varName)

        for varName in variables_requested_to_hide:
            if varName in variable_names:
                hidden_variables.append(varName)
        
        return hidden_variables
        
    def getClassVariablesWithSisters(self, item, exclude_nested: bool = True):
        known_sisters = []
        sister_props = []

        sister_data = self.__praser.getObjectVariableGroups(item)
        variable_data = self.__praser.getObjectVariables(item)
        limiters = self.__viewport.getLimiters()

        for var_name in variable_data[:]:
            if var_name.startswith("INTERNAL_") or var_name == "json_version":
                variable_data.remove(var_name)

        for sister_id in sister_data:
            sister_id: str
            sister_items = list[str](sister_data[sister_id]["items"])
            known_sisters.append(str(sister_id))

            for sister_variable in sister_items:
                if sister_variable in variable_data and exclude_nested:
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


    #region Get / Set Functions

    def getDataObject(self):
        return self.__item
    
    def setDataObject(self, item: Any):
        self.__item = item
        self.onDataObjectChanged()
        self.onPropertiesChanged()

    def getPraser(self):
        return self.__praser
    
    def setPraser(self, praser: DataHandler):
        self.__praser = praser

    def getViewport(self):
        return self.__viewport

    def setViewport(self, viewport: "PropertyViewport"):
        self.__viewport = viewport
    
    #endregion

    #region Signal Recievers

    def onPropertiesChanged(self):
        pass

    def onDataObjectChanged(self):
        pass

    #endregion

