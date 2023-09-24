from krita import Krita, Extension
from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util
from ..classes.config import *
from ..classes.resources import *


class QSeperator:

    def _init__(self, args):
        pass

    def addSeperator(self, view_menu):
        self.view_menu = view_menu
        self.view_menu.addSeparator()
        self.__menu_temp = view_menu.addAction('temp')  # <---- Temporary menu item
        self.view_menu.aboutToShow.connect(self.view_menu_build)  # <---- Remove item before menu is displayed

    def view_menu_build(self):
        """ Remove temporary menu item """
        self.view_menu.removeAction(self.__menu_temp)
