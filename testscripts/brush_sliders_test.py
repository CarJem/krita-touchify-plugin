from json import tool
from krita import *
import krita

def getSlider(name: str) -> QWidgetAction:
    activeWindow = Krita.instance().activeWindow().qwindow()
    wobj = activeWindow.findChild(QWidget,'paintopbox')
    brushSlider = wobj.findChild(QWidgetAction, name)
    return brushSlider

dlg = QDialog(Krita.instance().activeWindow().qwindow())
dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

layout = QHBoxLayout()
dlg.setLayout(layout)

toolbar = QToolBar(dlg)
layout.addWidget(toolbar)

activeWindow = Krita.instance().activeWindow().qwindow()
paintopbox = activeWindow.findChild(QWidget,'paintopbox')

action_name = "brushslider2"
slider_data = getSlider(action_name)
action = Krita.instance().action("brushslider2")

toolbar.addAction(action)
toolbar.r

dlg.show()



