from krita import *


activeWindow = Krita.instance().activeWindow()
qWin = activeWindow.qwindow()

viewIndex = activeWindow.views().index(activeWindow.activeView())
pobj = qWin.findChild(QWidget,'view_' + str(viewIndex))
mobj = next((w for w in pobj.findChildren(QWidget) if w.metaObject().className() == 'KisPopupPalette'), None)
#print(mobj)
mobj.setMouseTracking(True)
mobj.show()