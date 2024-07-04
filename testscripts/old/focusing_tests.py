from krita import Krita, Extension
from PyQt5 import QtWidgets, QtGui

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QEvent, QPoint, QRect, QSize




def sendMessage(message: str):
    activeWindow = Krita.instance().activeWindow()
    if not activeWindow: return

    activeView = activeWindow.activeView()
    if not activeView: return

    activeView.showFloatingMessage(message, Krita.instance().icon('arrow-up'), 1000, 0)

def test():

    activeWindow = Krita.instance().activeWindow()
    if not activeWindow: return

    activeView = activeWindow.activeView()
    if not activeView: return

    activeViewIndex = activeWindow.views().index(activeView)


    subWindows = activeWindow.qwindow().findChildren(QMdiSubWindow)
    activeViewWidget = None
    for subWindow in subWindows:
        activeViewWidget = subWindow.findChild(QWidget, 'view_' + str(activeViewIndex))
    if not activeViewWidget: return

    canvasWidget = activeViewWidget.findChild(QOpenGLWidget)

test()
