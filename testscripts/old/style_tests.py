from calendar import c
from inspect import _void, stack
from json import tool
from PyQt5.QtCore import *;
from PyQt5.QtGui import *;
from PyQt5.QtWidgets import *;
from PyQt5.Qt import QWIDGETSIZE_MAX;
import sys, os

sys.path.append('C:/Users/demo/Documents/Apps/Scripts/KritaDev/modules')

highlight = qApp.palette().color(QPalette.Highlight).name().split("#")[1]


from touchify.src.components.krita_ext.KisSliderSpinBox import KisSliderSpinBox
from krita import *
qwin = Krita.instance().activeWindow().qwindow()
wobj = qwin.findChild(QMdiArea)
objective = wobj.findChildren(KisSliderSpinBox)
for item in objective:
    #item.lineEdit().setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
    #item.lineEdit().setMinimumSize(0, 0)
    item.lineEdit().adjustSize()