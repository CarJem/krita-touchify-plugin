from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

qwin = Krita.instance().activeWindow().qwindow()
viewIndex = Krita.instance().activeWindow().views().index(Krita.instance().activeWindow().activeView())
pobj = qwin.findChild(QWidget,'view_' + str(viewIndex))
mobj = next((w for w in pobj.findChildren(QWidget) if w.metaObject().className() == 'KisPopupPalette'), None)
parentWidget = mobj.parentWidget()
center_x = int(parentWidget.width() / 2) - int(mobj.width() / 2)
center_y = int(parentWidget.height() / 2) - int(mobj.height() / 2)
mobj.move(center_x, center_y)
mobj.show()

