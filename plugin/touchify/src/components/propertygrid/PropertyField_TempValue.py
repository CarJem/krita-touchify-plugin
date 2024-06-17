from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET

from .PropertyGridExtensions import *
from .PropertyGrid import *

from ..extras.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from .IconSelector import IconSelector
from ...ext.typedlist import *
from ...resources import *
from ...ext.extensions import KritaExtensions
from ..CollapsibleBox import CollapsibleBox


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

class PropertyField_TempValue:
    __variable_name: any
    __variable_source: any
    __index: any
    
    def __init__(self, variable_data, variable_source, variable_name, index):
        self.value = variable_data
        self.__variable_name = variable_name
        self.__variable_source = variable_source
        self.__index = index

    #TODO: Implement Proper Restriction Handling for Values that are not sub classable
    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions

    def updateData(self):
        new_array = PropertyGridExtensions.getVariable(self.__variable_source, self.__variable_name)
        self.variable_data = self.value
        new_array[self.__index] = self.value
        PropertyGridExtensions.setVariable(self.__variable_source, self.__variable_name, new_array)



