from PyQt5.QtWidgets import QStackedWidget


class PropertyGridHost(QStackedWidget):
    def goBack(self):
        lastIndex = self.currentIndex() - 1
        currentWidget = self.currentWidget()
        self.setCurrentIndex(lastIndex)
        self.removeWidget(currentWidget)