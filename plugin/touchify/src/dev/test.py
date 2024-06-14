from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import QSize

from krita import *

qwin = Krita.instance().activeWindow().qwindow()
pobj = qwin.findChild(QWidget,'toolOptionsPad')
mobj: QWidget = next((w for w in pobj.findChildren(QWidget) if w.metaObject().className() == 'OverviewWidget'), None)


#mobj.setFixedWidth(300)
#mobj.setFixedHeight(300)
#mobj.pos().setX(0)
#mobj.pos().setY(0)
sizePolicy = mobj.sizePolicy()
print(dir(sizePolicy))
mobj.updateGeometry()
