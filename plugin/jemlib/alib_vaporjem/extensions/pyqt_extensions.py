
import json
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class QPainterTools:

    @staticmethod
    def setAlpha(color: QColor, alpha: int):
        color.setAlpha(alpha)
        return color

    @staticmethod
    def blendColors(foreground: QColor, background: QColor):
        #Get the alpha value of the foreground color (0 to 255)
        alpha = foreground.alpha()

        #If fully opaque or fully transparent, no blending is needed
        if (alpha == 255):
            return foreground
        
        if (alpha == 0):
            return background

        #Convert alpha to a float percentage (0.0 to 1.0)
        alphaF = alpha / 255.0
        invAlphaF = 1.0 - alphaF

        #Manually blend each color component using linear interpolation (lerp)
        blendedRed = int(foreground.red() * alphaF + background.red() * invAlphaF)
        blendedGreen = int(foreground.green() * alphaF + background.green() * invAlphaF)
        blendedBlue = int(foreground.blue() * alphaF + background.blue() * invAlphaF)

        #The resulting color is fully opaque (alpha = 255) because it's already "baked" onto the background
        return QColor(blendedRed, blendedGreen, blendedBlue, 255)

class CommonHelpers:
    @staticmethod  
    def isDeleted(item: any):
        if isinstance(item, QObject):
            try:
                item.objectName()
                return False
            except RuntimeError as e:
                return True
        elif isinstance(item, QLayoutItem):
            try:
                item.widget()
                return False
            except RuntimeError as e:
                return True
        else:
            raise Exception(f"Unsupported Wrapped C/C++ Object or Other Object: {str(item)}")

    @staticmethod
    def clearLayout(layout: QLayout | None):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    CommonHelpers.clearLayout(child.layout())

class GeometryHelpers:
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
    
    def normalizeSize(targetSize: QSize):
        result: QSize = QSize(targetSize)

        if result.width() < 0: result.setWidth(0)
        if result.height() < 0: result.setHeight(0)
            
        return result

    def fitToTarget(sourceSize: QSize, targetSize: QSize):
        """
        Resize the source size to fit the target size"""
        
        result: QSize = QSize(targetSize)
        
        if sourceSize.width() < result.width():
            result.setWidth(sourceSize.width())
                
        if sourceSize.height() < result.height():
            result.setHeight(sourceSize.height())

        if result.width() < 0: result.setWidth(0)
        if result.height() < 0: result.setHeight(0)
            
        return result

    def fitToSource(sourceSize: QSize, targetSize: QSize):
        """
        Resize the target size to fit the source size"""
        
        result: QSize = QSize(targetSize)
        
        if sourceSize.width() > result.width():
            result.setWidth(sourceSize.width())
                
        if sourceSize.height() > result.height():
            result.setHeight(sourceSize.height())

        if result.width() < 0: result.setWidth(0)
        if result.height() < 0: result.setHeight(0)
            
        return result

class EventTypes:
    """Stores a string name for each event type.

    With PySide2 str() on the event type gives a nice string name,
    but with PyQt5 it does not. So this method works with both systems.
    """

    def __init__(self):
        """Create mapping for all known event types."""
        self.string_name = {}
        for name in vars(QEvent):
            attribute = getattr(QEvent, name)
            if type(attribute) == QEvent.Type:
                self.string_name[attribute] = name

    def as_string(self, event: QEvent.Type) -> str:
        """Return the string name for this event."""
        try:
            return self.string_name[event]
        except KeyError:
            return f"UnknownEvent:{event}"


class JsonQt:

    @staticmethod
    def serialize_qbytearray(array: QByteArray):
        return json.dumps(bytes(array.toHex()).decode('ascii'))
    
    @staticmethod
    def deserialize_qbytearray(array_data: str):
        return QByteArray.fromHex(bytes(json.loads(array_data), 'ascii'))

    @staticmethod
    def serialize_qpointf(point: QPointF) -> dict:
        """Serializes a QPoint object to a dict."""
        return {
            "x": point.x(),
            "y": point.y()
        }

    @staticmethod
    def deserialize_qpointf(data: dict) -> QPointF:
        """Deserializes a dict into a QPoint object."""
        return QPointF(
            data["x"],
            data["y"]
        )
    
    @staticmethod
    def serialize_qpoint(point: QPoint) -> dict:
        """Serializes a QPoint object to a dict."""
        return {
            "x": point.x(),
            "y": point.y()
        }

    @staticmethod
    def deserialize_qpoint(data: dict) -> QPoint:
        """Deserializes a dict into a QPoint object."""
        return QPoint(
            data["x"],
            data["y"]
        )

    @staticmethod
    def serialize_qrectf(rect: QRectF) -> dict:
        """Serializes a QRectF object to a dict."""
        return {
            "x": rect.x(),
            "y": rect.y(),
            "width": rect.width(),
            "height": rect.height()
        }

    @staticmethod
    def deserialize_qrectf(rect_data: dict) -> QRectF:
        """Deserializes a dict into a QRectF object."""
        return QRectF(
            rect_data["x"],
            rect_data["y"],
            rect_data["width"],
            rect_data["height"]
        )

    @staticmethod
    def serialize_qrect(rect: QRect) -> dict:
        """Serializes a QRect object to a dict."""
        return {
            "x": rect.x(),
            "y": rect.y(),
            "width": rect.width(),
            "height": rect.height()
        }

    @staticmethod
    def deserialize_qrect(rect_data: dict) -> QRect:
        """Deserializes a dict into a QRect object."""
        return QRect(
            rect_data["x"],
            rect_data["y"],
            rect_data["width"],
            rect_data["height"]
        )