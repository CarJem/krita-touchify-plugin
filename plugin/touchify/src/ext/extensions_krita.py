import inspect

from .typedlist import *
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys

from krita import *


class KritaExtensions:

    def showQuickMessage(message):
        Krita.instance().activeWindow().activeView().showFloatingMessage(message, Krita.instance().icon('move_layer_up'), 1000, 0)