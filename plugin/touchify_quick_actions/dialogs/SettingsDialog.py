
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from jemlib.alib_propertygrid.dialogs.PropertyGrid_Window import PropertyGrid_Window
from jemlib.api_krita.wrappers.window import WindowAPI

from krita import *
from touchify.src.alib_propertygrid.data.TouchifyDataExtension import TouchifyDataExtension

class SettingsDialog(PropertyGrid_Window):
    @staticmethod
    def Setup(dlg: "SettingsDialog", api_window: WindowAPI, title: str, input: any):
        result = PropertyGrid_Window.Setup(dlg, api_window.qwindow.window(), input, TouchifyDataExtension.Praser(), cls=SettingsDialog)
        result.setWindowTitle(title)
        return result

    def __init__(self, qwin, options, prasers = None, buttons = None):
        super().__init__(qwin, options, prasers, buttons)
        self.resize(325, 420)
        self.setMinimumSize(600,400)
        self.setBaseSize(800,800)

