from krita import *
from touchify.__env__ import TOUCHIFY_DOCKERID_WIDGETPAD
from touchify.src.components.toolshelf.ShelfDockWidgetPad import ShelfWidgetPad
from touchify.src.components.toolshelf.ShelfWidget import ShelfWidget

docker_id = TOUCHIFY_DOCKERID_WIDGETPAD + "_1"

qdock: ShelfWidgetPad | None = next((w for w in Krita.instance().dockers() if w.objectName() == docker_id), None)
if qdock != None:
    qdock: ShelfWidgetPad
    shelf: ShelfWidget = qdock.widget()
    shelf.setVisible(True)
    shelf.dockStack.setVisible(True)
    shelf.resize(100,100)
    shelf.adjustSize()