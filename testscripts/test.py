from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *




actual_window = Krita.instance().activeWindow().qwindow()
mobj = next((w for w in actual_window.findChildren(QFrame) if w.metaObject().className() == 'KisGradientChooser'), None)
print(mobj.currentResource())

