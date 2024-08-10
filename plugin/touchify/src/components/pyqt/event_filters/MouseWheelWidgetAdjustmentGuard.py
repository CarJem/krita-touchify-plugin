from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtWidgets import QWidget

class MouseWheelWidgetAdjustmentGuard(QObject):
    def __init__(self, parent: QObject):
        super().__init__(parent)

    def eventFilter(self, o: QObject, e: QEvent) -> bool:
        widget: QWidget = o
        if e.type() == QEvent.Wheel and not widget.hasFocus():
            e.ignore()
            return True
        return super().eventFilter(o, e)