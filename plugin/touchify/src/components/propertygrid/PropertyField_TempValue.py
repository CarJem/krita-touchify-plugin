from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET

from .PropertyField import PropertyField

from .PropertyUtils_Extensions import *
from .PropertyGrid import *

from ..extras.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from .PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from ...ext.TypedList import *
from ...resources import *
from ...ext.extensions_krita import KritaExtensions
from ..CollapsibleBox import CollapsibleBox


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

class PropertyField_TempValue(PropertyField):
    def __init__(self, variable_data, variable_source, variable_name, index):
        super().__init__(variable_name, variable_data, variable_source)
        self.value: any = variable_data
        self.__index: any = index

    def updateData(self):
        new_array = PropertyUtils_Extensions.getVariable(self.variable_source, self.variable_name)
        self.variable_data = self.value
        new_array[self.__index] = self.value
        super().setVariable(self.variable_source, self.variable_name, new_array)



