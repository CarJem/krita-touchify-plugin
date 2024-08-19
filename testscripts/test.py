from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.actions.TouchifyActionButton import TouchifyActionButton
from touchify.src.components.touchify.actions.TouchifyActionPanel import TouchifyActionPanel


#Krita.instance().notifier().configurationChanged.emit()
#Krita.instance().activeWindow().qwindow().slotPreferences()
                          

qwin = Krita.instance().activeWindow().qwindow()
panels = qwin.findChildren(TouchifyActionPanel)
for panel in panels:
    toolbars = panel.findChildren(QToolBar)
    for toolbar in toolbars:
        toolbar.layout().setContentsMargins(0, 0, 0, 0)
        


