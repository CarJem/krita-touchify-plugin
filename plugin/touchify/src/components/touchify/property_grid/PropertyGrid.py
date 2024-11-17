from PyQt5.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QTabBar, QSizePolicy


class PropertyGrid(QWidget):


    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setLayout(QVBoxLayout(self))
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)

        self.navi_connection = None

        self.naviTabBar = QTabBar(self)
        self.naviTabBar.setExpanding(False)
        self.naviTabBar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.naviTabBar.setMovable(False)
        self.naviTabBar.setUsesScrollButtons(False)
        self.naviTabBar.setTabsClosable(False)
        self.layout().addWidget(self.naviTabBar)

        from .PropertyGrid_Panel import PropertyGrid_Panel
        self.rootPropertyGrid = PropertyGrid_Panel(self)
        self.rootPropertyGrid.setWindowTitle("ROOT")

        self.stackWidget = QStackedWidget(self)
        self.stackWidget.insertWidget(0, self.rootPropertyGrid)
        self.layout().addWidget(self.stackWidget)

        self.updateNavigationTabs()

    def forceUpdate(self):
        pass

    def navigationIndexChanged(self):
        tabIndex = self.naviTabBar.currentIndex()
        stackIndex = self.stackWidget.currentIndex()

        if stackIndex > tabIndex:
            navigate_back_amount = stackIndex - tabIndex
            self.goBack(navigate_back_amount)
        
    def setNavigationConnection(self, s: bool):
        if s and self.navi_connection == None:
            self.navi_connection = self.naviTabBar.currentChanged.connect(self.navigationIndexChanged)
        elif self.navi_connection and s == False:
            self.naviTabBar.currentChanged.disconnect(self.navigationIndexChanged)
            self.navi_connection = None

    def updateNavigationTabs(self):
        self.setNavigationConnection(False)
        while self.naviTabBar.count() != 0:
            self.naviTabBar.removeTab(0)

        for i in range(0, self.stackWidget.count()):
            item = self.stackWidget.widget(i)
            self.naviTabBar.addTab(item.windowTitle())

        self.naviTabBar.setCurrentIndex(self.stackWidget.currentIndex())
        self.setNavigationConnection(True)

    def currentIndex(self):
        return self.stackWidget.currentIndex()
    
    def currentWidget(self):
        return self.stackWidget.currentWidget()

    def addWidget(self, w: QWidget):
        return self.stackWidget.addWidget(w)

    def setCurrentIndex(self, index):
        self.setNavigationConnection(False)
        self.stackWidget.setCurrentIndex(index)
        self.updateNavigationTabs()
    
    def updateDataObject(self, data: any):
        self.rootPropertyGrid.updateDataObject(data)
        self.updateNavigationTabs()

    def goForward(self, newPage):
        self.setNavigationConnection(False)
        self.setCurrentIndex(self.addWidget(newPage))
        self.updateNavigationTabs()

    def goBack(self, amount: int = 1):
        if amount < 1: amount = 1
        self.setNavigationConnection(False)
        for i in range(0, amount):
            lastIndex = self.currentIndex() - 1
            currentWidget = self.currentWidget()
            self.setCurrentIndex(lastIndex)
            self.stackWidget.removeWidget(currentWidget)
        self.updateNavigationTabs()