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


from touchify.src.dockers.BrushOptionsDocker import SliderSpinBox
from krita import *
qwin = Krita.instance().activeWindow().qwindow()
wobj = qwin.findChild(QMdiArea)
objective = wobj.findChildren(SliderSpinBox)
for item in objective:
    delta = (item.spinbox.value() / item.spinbox.maximum())**(1./item.scaling)
    value = int(delta * item.progbar.maximum())

    buttonStyle = f"""background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #{highlight}, stop:{delta} #{highlight}, stop:{delta + 0.01} black, stop:1 black)"""
    item.spinbox.lineEdit().setStyleSheet(buttonStyle)