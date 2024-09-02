from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

qwin = Krita.instance().activeWindow().qwindow()
mobj = next((w for w in qwin.findChildren(QWidget) if w.metaObject().className() == 'KoToolBox'), None)
#wobj = mobj.findChild(QButtonGroup)
#print(wobj.checkedButton().objectName())
event = QContextMenuEvent(QContextMenuEvent.Reason.Keyboard, QPoint(0,0))
mobj.event(event)

#wobj = mobj.findChild(QButtonGroup)
#print(wobj.checkedButton().objectName())
        


