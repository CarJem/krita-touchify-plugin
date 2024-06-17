from PyQt5.QtWidgets import QStackedWidget, QWidget


class PropertyGridHost(QStackedWidget):

    def init(self, obj: QWidget):
        self.propertyGrid = obj
        self.insertWidget(0, self.propertyGrid)

    def getGridObject(self):
        return self.propertyGrid

    def goForward(self, newPage):
        pass

    def goBack(self):
        lastIndex = self.currentIndex() - 1
        currentWidget = self.currentWidget()
        self.setCurrentIndex(lastIndex)
        self.removeWidget(currentWidget)