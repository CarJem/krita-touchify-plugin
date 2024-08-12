import inspect

from .TypedList import *
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys

from krita import *

from PyQt5.QtWidgets import QMessageBox


class PyQtExtensions:
    
    class QSize:
        def fitToTarget(sourceSize: QSize, targetSize: QSize):
            """
            Resize the source size to fit the target size"""
            
            result: QSize = QSize(targetSize)
            
            if sourceSize.width() < result.width():
                result.setWidth(sourceSize.width())
                    
            if sourceSize.height() < result.height():
                result.setHeight(sourceSize.height())
                
            return result

        def fitToSource(sourceSize: QSize, targetSize: QSize):
            """
            Resize the target size to fit the source size"""
            
            result: QSize = QSize(targetSize)
            
            if sourceSize.width() > result.width():
                result.setWidth(sourceSize.width())
                    
            if sourceSize.height() > result.height():
                result.setHeight(sourceSize.height())
                
            return result
    
    
    def isDeleted(item: QObject):
        try:
            item.objectName()
            return False
        except RuntimeError as e:
            return True

    def quickDialog(parent, text):
        dlg = QMessageBox(parent)
        dlg.setText(text)
        dlg.show()

    def clearLayout(layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    PyQtExtensions.clearLayout(child.layout())