from krita import *

qdock = next((w for w in Krita.instance().dockers() if w.objectName() == 'ToolBox'), None)
qdock.contextMenuEvent(QContextMenuEvent(QContextMenuEvent.Reason.Keyboard, QPoint(0,0)))
