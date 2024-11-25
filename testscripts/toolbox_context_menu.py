from krita import *



window = Krita.instance().activeWindow()
qwin = window.qwindow()

QApplication.setActiveWindow(qwin.window())



qApp.activeWindow().setWindowState(qApp.activeWindow().windowState() & Qt.WindowState.WindowMinimized)
qApp.activeWindow().show()
qApp.activeWindow().raise_()
qApp.activeWindow().activateWindow()

qApp.activeWindow().setWindowState((qApp.activeWindow().windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive)
qApp.activeWindow().show()
qApp.activeWindow().raise_()
qApp.activeWindow().activateWindow()



#QCursor.setPos(wobj.mapToGlobal(wobj.pos()))

QApplication.instance().sendEvent(qwin, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_7, Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier))
QApplication.instance().sendEvent(qwin, QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_7, Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier))