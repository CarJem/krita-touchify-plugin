from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


#Krita.instance().notifier().configurationChanged.emit()
#Krita.instance().activeWindow().qwindow().slotPreferences()
                                

qwin = Krita.instance().activeWindow().qwindow()
for i, views in enumerate(Krita.instance().activeWindow().views()):
    index = i - 1
    pobj = qwin.findChild(QWidget,'view_' + str(i))
    for child in pobj.children():
        call = getattr(child, "slotConfigChanged", None)
        if callable(call):
            call()