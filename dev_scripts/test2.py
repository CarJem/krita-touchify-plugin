from krita import *

qwin = Krita.instance().activeWindow().qwindow()
wobj = qwin.findChildren(QDockWidget,'Touchify/ToolshelfDocker')
dock: QDockWidget = wobj[0]
dock.setFloating(False)
dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)