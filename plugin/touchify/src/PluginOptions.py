
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from jemlib.alib_propertygrid.dialogs.PropertyGrid_Window import PropertyGrid_Window
from touchify.src.alib_propertygrid.data.TouchifyDataHandler import TouchifyDataHandler

from krita import *

class PluginOptions:

    @staticmethod
    def Setup(dlg: "PropertyGrid_Window", qwin: QWidget, input: any, buttons: list[QDialogButtonBox.StandardButton] = None):
        return PropertyGrid_Window.Setup(dlg, qwin, input, TouchifyDataHandler.Praser(), buttons=buttons)
    


