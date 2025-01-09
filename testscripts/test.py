from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *

win = Krita.instance().activeWindow()

try: index = win.views().index(win.activeView())
except: index = -1

if index != -1:
    qwin = win.qwindow()
    pobj = qwin.findChild(QWidget,'view_{0}'.format(index))
    wobj = pobj.findChild(QOpenGLWidget)

    qwin.setFocus(True)
    qwin.activateWindow()
    qwin.raise_()

    QtCore.QCoreApplication.sendEvent(wobj, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Control, Qt.KeyboardModifier.NoModifier))
    QtCore.QCoreApplication.sendEvent(wobj, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Alt, Qt.KeyboardModifier.NoModifier))
    QtCore.QCoreApplication.sendEvent(wobj, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_7, Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier))
    QtCore.QCoreApplication.sendEvent(wobj, QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_7, Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier))
    QtCore.QCoreApplication.sendEvent(wobj, QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_Alt, Qt.KeyboardModifier.NoModifier))
    QtCore.QCoreApplication.sendEvent(wobj, QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_Control, Qt.KeyboardModifier.NoModifier))

