from typing import TYPE_CHECKING
from krita import QStackedWidget

from touchify.src.managers.DockerManager import QStackedWidget
from touchify.src.settings.TouchifySettings import QStackedWidget


from PyQt5.QtWidgets import QStackedWidget

if TYPE_CHECKING:
    from touchify_toolshelves.src.components.ShelfWidget import ShelfWidget


class ShelfWidgetStack(QStackedWidget):
    def __init__(self, parent: "ShelfWidget" = None):
        super().__init__(parent)
        self.shelf = parent

    def setCurrentIndex(self, index):
        super().setCurrentIndex(index)
        self.shelf.onShelfIndexChanged()

    def sizeHint(self):
        widget = self.currentWidget()
        if widget:
            return self.currentWidget().sizeHint()
        else:
            return super().sizeHint()

    def minimumSizeHint(self):
        widget = self.currentWidget()
        if widget:
            return self.currentWidget().minimumSizeHint()
        else:
            return super().minimumSizeHint()