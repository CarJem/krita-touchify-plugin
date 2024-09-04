from PyQt5.QtWidgets import QStackedWidget, QWidget, QScrollArea


class PropertyGrid(QStackedWidget):


    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        from .PropertyGrid_Panel import PropertyGrid_Panel
        self.rootPropertyGrid = PropertyGrid_Panel(self)
        self.insertWidget(0, self.rootPropertyGrid)

    def forceUpdate(self):
        pass
    
    def updateDataObject(self, data: any):
        self.rootPropertyGrid.updateDataObject(data)

    def goForward(self, newPage):
        self.setCurrentIndex(self.addWidget(newPage))

    def goBack(self):
        lastIndex = self.currentIndex() - 1
        currentWidget = self.currentWidget()
        self.setCurrentIndex(lastIndex)
        self.removeWidget(currentWidget)