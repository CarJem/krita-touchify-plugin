from krita import Krita, Extension
from PyQt5 import QtWidgets, QtGui

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QToolButton, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt, QEvent, QPoint, QRect, QSize

class Function:
    def __init__(self):
        pass
    
    def alert(self, text):
        dlg = QDialog(Krita.instance().activeWindow().qwindow())
        dlg.setWindowTitle(text)
        dlg.show()
    
    def visibilityChanged(self, s):
        if self.docker.isVisible() == False:
          self.alert('bye')
          self.docker.visibilityChanged.disconnect(self.visibilityChanged)
        else:
           self.alert('hi')

    def patch(self, docker):
        self.docker = docker
        self.docker.visibilityChanged.connect(self.visibilityChanged)

        
        
dockersList = Krita.instance().dockers()
for docker in dockersList:
    if (docker.objectName() == "quick_settings_docker"):
        print(docker.windowFlags())
        print(docker.focusPolicy())
        #tst = Function()
        #tst.patch(docker)