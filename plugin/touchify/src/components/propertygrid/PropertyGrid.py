from PyQt5.QtWidgets import QStackedWidget, QWidget, QScrollArea


class PropertyGrid(QStackedWidget):


    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        from .PropertyGridPanel import PropertyGridPanel
        self.rootPropertyGrid = PropertyGridPanel(self)
        self.insertWidget(0, self.rootPropertyGrid)

    #def setGrid(self, obj: QWidget):
    #    if self.rootPropertyGrid == None:
    #        self.rootPropertyGrid = obj
    #        self.insertWidget(0, self.rootPropertyGrid)

    #def getGrid(self):
    #    return self.rootPropertyGrid
    
    def updateDataObject(self, data: any):
        self.rootPropertyGrid.updateDataObject(data)

    def goForward(self, newPage):
        pass

    def goBack(self):
        lastIndex = self.currentIndex() - 1
        currentWidget = self.currentWidget()
        self.setCurrentIndex(lastIndex)
        self.removeWidget(currentWidget)