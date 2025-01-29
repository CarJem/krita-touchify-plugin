
from touchify.src.datatypes.sequence.TypedList import *
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *



class PyQtExtensions:
    

    class General:
        @staticmethod  
        def isDeleted(item: QObject):
            try:
                item.objectName()
                return False
            except RuntimeError as e:
                return True

        @staticmethod
        def clearLayout(layout: QLayout | None):
            if layout is not None:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget() is not None:
                        child.widget().deleteLater()
                    elif child.layout() is not None:
                        PyQtExtensions.General.clearLayout(child.layout())

    class Geometry:

        def clampToTarget(position: QPoint, size: QSize, source: QWidget, offset: QPoint = None):
            __x = position.x()
            __y = position.y()

            if offset != None:
                __x = __x + offset.x()
                __y = __y + offset.y()

            __hint_width = size.width()
            __hint_height = size.height()

            screen_x = source.geometry().x()
            screen_y = source.geometry().y()
            screen_height = source.size().height()
            screen_width = source.size().width()

            if __x + __hint_width > screen_x + screen_width:
                __x = screen_x + screen_width - __hint_width
            elif __x < screen_x:
                __x = screen_x

            if __y + __hint_height > screen_y + screen_height:
                __y = screen_y + screen_height - __hint_height

            return QPoint(__x, __y)

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

