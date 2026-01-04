from typing import TYPE_CHECKING
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.managers.IconRepository import IconRepository

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class PropertyGrid(QWidget):

    def __init__(self, parent: QWidget | None = None, praser: "DataHandler" = None, scrolling=True, **kwargs) -> None:
        super(QWidget, self).__init__(parent)
        
        from jemlib.alib_propertygrid.data.DataHandler import DataHandler
        self.__praser = praser if praser else DataHandler()
        self.__navigation_connection = None

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        
        self.back_button = QPushButton(self)
        self.back_button.setContentsMargins(0,0,0,0)
        self.back_button.setFlat(True)
        self.back_button.setIcon(IconRepository.materialIcon("arrow-left"))
        self.back_button.clicked.connect(self.navigateBackwards)
        layout.addWidget(self.back_button, 0, 0)

        self.tab_bar = QTabBar(self)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.tab_bar.setMovable(False)
        self.tab_bar.setUsesScrollButtons(True)
        self.tab_bar.installEventFilter(self)
        self.tab_bar.setTabsClosable(False)
        layout.addWidget(self.tab_bar, 0, 1)
        layout.setColumnStretch(1, 1)

        self.page_stack = QStackedWidget(self)
        layout.addWidget(self.page_stack, 1, 0, 1, 2)

        from .PropertyViewport import PropertyViewport
        self.__property_grid = PropertyViewport(self, self.__praser, scrolling)
        self.__property_grid.setWindowTitle("ROOT")
        self.page_stack.insertWidget(0, self.__property_grid)

        self.onNavigationTabsChanged()

    #region Event Recievers

    def eventFilter(self, obj, event):
        if obj is self.tab_bar and event.type() == QEvent.Type.Wheel:
            return True
        return super(PropertyGrid, self).eventFilter(obj, event)

    #endregion

    #region Get / Set Functions

    def getPropertyGrid(self):
        return self.__property_grid

    def getCurrentIndex(self):
        return self.page_stack.currentIndex()
    
    def setCurrentIndex(self, index):
        self.setNavigationConnection(False)
        self.page_stack.setCurrentIndex(index)
        self.onNavigationTabsChanged()
    
    def getCurrentWidget(self):
        return self.page_stack.currentWidget()

    def setNavigationConnection(self, s: bool):
        if s and self.__navigation_connection == None:
            self.__navigation_connection = self.tab_bar.currentChanged.connect(self.onNavigationIndexChanged)
        elif self.__navigation_connection and s == False:
            self.tab_bar.currentChanged.disconnect(self.onNavigationIndexChanged)
            self.__navigation_connection = None

    def getDataObject(self):
        return self.__property_grid.getDataObject()

    def setDataObject(self, data: any):
        self.__property_grid.setDataObject(data)
        self.onNavigationTabsChanged()

    #endregion

    #region Signal Recievers

    def onNavigationIndexChanged(self):
        tabIndex = self.tab_bar.currentIndex()
        stackIndex = self.page_stack.currentIndex()

        if stackIndex > tabIndex:
            navigate_back_amount = stackIndex - tabIndex
            self.navigateBackwards(navigate_back_amount)

    def onNavigationTabsChanged(self):
        self.setNavigationConnection(False)
        while self.tab_bar.count() != 0:
            self.tab_bar.removeTab(0)

        for i in range(0, self.page_stack.count()):
            item = self.page_stack.widget(i)
            self.tab_bar.addTab(item.windowTitle())

        self.tab_bar.setCurrentIndex(self.page_stack.currentIndex())
        self.tab_bar.scroll(self.tab_bar.width(), 0)
        self.setNavigationConnection(True)

    #endregion

    #region Action Functions

    def navigateForwards(self, newPage: QWidget):
        self.setNavigationConnection(False)
        new_index = self.page_stack.addWidget(newPage)
        self.setCurrentIndex(new_index)

    def navigateBackwards(self, amount: int = 1):
        if self.page_stack.count() == 1: return
        if amount < 1: amount = 1
        self.setNavigationConnection(False)
        for i in range(0, amount):
            lastIndex = self.getCurrentIndex() - 1
            currentWidget = self.getCurrentWidget()
            if isinstance(currentWidget, QDialog):
                currentWidget.reject()
            self.setCurrentIndex(lastIndex)
            self.page_stack.removeWidget(currentWidget)
        self.onNavigationTabsChanged()

    #endregion

    #region 




    
