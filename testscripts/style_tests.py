from calendar import c
from inspect import _void, stack
from json import tool
from PyQt5.QtCore import *;
from PyQt5.QtGui import *;
from PyQt5.QtWidgets import *;
from PyQt5.Qt import QWIDGETSIZE_MAX;
import sys, os

sys.path.append('C:/Users/demo/Documents/Apps/Scripts/KritaDev/modules')




# For autocomplete
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .PyKrita import *
else:
    from krita import *


from touchify.src.components.nu_tools.nt_logic.Nt_ScrollAreaContainer import Nt_ScrollAreaContainer
from touchify.src.components.toolshelf.ToolshelfWidget import ToolshelfContainer
from krita import *
qwin = Krita.instance().activeWindow().qwindow()
wobj = qwin.findChild(QMdiArea)
toolOptionsPad = wobj.findChildren(QWidget, 'toolOptionsPad')
for item in toolOptionsPad:
    scrollContainer: QWidget = item.findChild(Nt_ScrollAreaContainer)
    scrollArea: QScrollArea = scrollContainer.findChild(QScrollArea)


    #region Stylesheets

    stylesheet_data = f"""
    QScrollArea {{ background: transparent; }}
    QScrollArea > QWidget > ToolshelfContainer {{ background: transparent; }}
    """

    scrollArea.setStyleSheet(stylesheet_data)

    #endregion

    #region Viewport Stuff
    #stackArea: ToolshelfContainer = scrollArea.findChild(ToolshelfContainer)
    #for i in range(0, stackArea.count()):
        #panel = stackArea.widget(i)
        #if panel.isVisible():
            #viewport_size = scrollArea.viewport().size()
            #viewport_sizeHint = scrollArea.viewportSizeHint()
            #actual_size = scrollArea.size()
            #actual_sizeHint = scrollArea.sizeHint()

            #print("Viewport Size: " + str(viewport_size.width()) + "," + str(viewport_size.height()))
            #print("Viewport Size Hint: " + str(viewport_sizeHint.width()) + "," + str(viewport_sizeHint.height()))
            #print("Actual Size: " + str(actual_size.width()) + "," + str(actual_size.height()))
            #print("Actual Size Hint: " + str(actual_sizeHint.width()) + "," + str(actual_sizeHint.height()))
            #print("---")

            #panel.adjustSize()
            #stackArea.adjustSize()
            #stackArea.parentWidget().adjustSize()

            #scrollArea.viewport().setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            #scrollArea.viewport().resize(panel.minimumSize())
            #scrollArea.viewport().adjustSize()
            #scrollArea.viewport().setFixedSize(scrollArea.viewport().sizeHint())
    #endregion