from PyQt5.QtCore import QObject

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.components.touchify.special.TouchifyPopup import TouchifyPopup
    from touchify.src.components.canvas.NtWidgetPad import NtWidgetPad

class Helpers():
    def findPopup(self: QObject) -> "TouchifyPopup":
        from touchify.src.components.touchify.special.TouchifyPopup import TouchifyPopup
        try:
            widget = self.parent()
            while (widget):
                foo = widget
                if isinstance(foo, TouchifyPopup):
                    return foo
                widget = widget.parent()
            return None
        except:
            return None

    def findWidgetPad(self: QObject) -> "NtWidgetPad":
        from touchify.src.components.canvas.NtWidgetPad import NtWidgetPad
        try:
            widget = self.parent()
            while (widget):
                foo = widget
                if isinstance(foo, NtWidgetPad):
                    return foo
                widget = widget.parent()
            return None
        except:
            return None