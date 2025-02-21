from dataclasses import dataclass
from typing import List, Iterable, Union, TYPE_CHECKING
from PyQt5 import (QtGui, QtCore)
from krita import (
    ManagedColor as KritaManagedColor
)

if TYPE_CHECKING:
    from touchify.src.api_krita.wrappers.canvas import CanvasAPI


@dataclass
class ManagedColorAPI:

    color: KritaManagedColor

    def isValid(self):
        return self.color != None

    @property
    def components(self) -> List[float]:
        if self.isValid(): return self.color.components()
        else: return []
    
    @components.setter
    def components(self, values: Iterable[float]) -> None:
        if self.isValid(): self.color.setComponents(values)

    def components_ordered(self):
        if self.isValid(): return self.color.componentsOrdered()
        else: return ""
    
    def colorProfile(self) -> str: 
        if self.isValid(): return self.color.colorProfile()
        else: return ""

    def colorModel(self) -> str: 
        if self.isValid(): return self.color.colorModel()
        else: return ""

    def colorDepth(self) -> str: 
        if self.isValid(): return self.color.colorDepth()
        else: return ""

    def setColorProfile(self, colorProfile: str) -> bool: 
        if self.isValid(): return self.color.setColorProfile(colorProfile)
        else: return False

    def setColorSpace(self, colorModel: str, colorDepth: str, colorProfile: str) -> bool:
        if self.isValid(): return self.color.setColorProfile(colorModel, colorDepth, colorProfile)
        else: return False
    
    def to_qt(self, canvas: 'CanvasAPI') -> QtGui.QColor: 
        if not self.isValid(): return QtGui.QColor()
        if canvas.isValid(): return self.color.colorForCanvas(canvas.canvas)
        else: return QtGui.QColor()
    

    @staticmethod
    def from_qt(qcolor: Union[QtGui.QColor, QtCore.Qt.GlobalColor], canvas: 'CanvasAPI' = None) -> 'ManagedColorAPI':
        if canvas != None: 
            if not canvas.isValid(): return ManagedColorAPI(None)
            else: return ManagedColorAPI(KritaManagedColor.fromQColor(qcolor, canvas.canvas))
        else: return ManagedColorAPI(KritaManagedColor.fromQColor(qcolor))

    @staticmethod
    def of(colorModel: str, colorDepth: str, colorProfile: str) -> 'ManagedColorAPI':
        return ManagedColorAPI(KritaManagedColor(colorModel, colorDepth, colorProfile))
        
    def __ne__(self, other: object):
        if isinstance(other, ManagedColorAPI):
            return self.color.__ne__(other.color)
        else: return self.color.__ne__(other)

    def __eq__(self, other: object):
        if isinstance(other, ManagedColorAPI):
            return self.color.__eq__(other.color)
        else: return self.color.__eq__(other)

