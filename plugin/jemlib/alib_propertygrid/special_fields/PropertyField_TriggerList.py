from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from touchify.src.config.triggers.Trigger import Trigger
from jemlib.alib_propertygrid.fields.PropertyField_TypedList import PropertyField_TypedList
from jemlib.alib_datatypes.TypedList import TypedList
from touchify.src.managers.ResourceManager import *



class PropertyField_TriggerList(PropertyField_TypedList):
    def __init__(self, variable_name=str, variable_data=TypedList[Trigger], variable_source=any):
        manual_restrictions = []
        super(PropertyField_TriggerList, self).__init__(variable_name, variable_data, variable_source, manual_restrictions)