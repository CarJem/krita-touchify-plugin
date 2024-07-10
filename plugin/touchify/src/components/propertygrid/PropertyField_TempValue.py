from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET

from .PropertyUtils_Extensions import *
from .PropertyGrid import *

from ..extras.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from .PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from ...ext.typedlist import *
from ...resources import *
from ...ext.extensions_krita import KritaExtensions
from ..CollapsibleBox import CollapsibleBox


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

class PropertyField_TempValue:
    def __init__(self, variable_data, variable_source, variable_name, index):
        self.value: any = variable_data
        self.__variable_name: any = variable_name
        self.__variable_source: any = variable_source
        self.__index: any = index

    #TODO: Implement Proper Restriction Handling for Values that are not sub classable
    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions

    def updateData(self):
        new_array = PropertyUtils_Extensions.getVariable(self.__variable_source, self.__variable_name)
        self.variable_data = self.value
        new_array[self.__index] = self.value
        PropertyUtils_Extensions.setVariable(self.__variable_source, self.__variable_name, new_array)



