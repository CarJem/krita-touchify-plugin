from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from touchify.src.cfg.action.CfgTouchifyAction import CfgTouchifyAction
from touchify.src.components.touchify.property_grid.fields.PropertyField_TypedList import PropertyField_TypedList
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.resources import *



class PropertyField_ActionList(PropertyField_TypedList):
    def __init__(self, variable_name=str, variable_data=TypedList[CfgTouchifyAction], variable_source=any):
        manual_restrictions = []
        super(PropertyField_ActionList, self).__init__(variable_name, variable_data, variable_source, manual_restrictions)