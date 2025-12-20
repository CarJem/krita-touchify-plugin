from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from jemlib.alib_propertygrid.data.DataPath import DataPath
from touchify.src.config.triggers.Trigger import Trigger
from jemlib.alib_propertygrid.fields.PropertyField_TypedList import PropertyField_TypedList
from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.managers.IconRepository import *

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class PropertyField_TriggerList(PropertyField_TypedList):
    def __init__(self, handler: "DataHandler", property: DataPath[TypedList[Trigger]]):
        manual_restrictions = []
        super(PropertyField_TriggerList, self).__init__(handler, property, manual_restrictions)