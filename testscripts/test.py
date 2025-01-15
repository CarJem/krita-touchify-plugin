from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *
from touchify.src.components.touchify.canvas.NtCanvas import NtToolshelf

qwin = Krita.instance().activeWindow().qwindow()
wobj = qwin.findChild(QMdiArea)
toolshelves = wobj.findChildren(NtToolshelf)
for toolshelf in toolshelves:
    print(toolshelf.pos())