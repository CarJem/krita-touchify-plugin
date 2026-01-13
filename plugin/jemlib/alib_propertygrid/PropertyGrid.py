from typing import TYPE_CHECKING
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.alib_propertygrid.PropertyTabs import PropertyTabs
from jemlib.managers.IconRepository import IconRepository
from jemlib.alib_vaporjem import Logger

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class PropertyGrid(QWidget):

    def __init__(self, parent: QWidget | None = None, praser: "DataHandler" = None, scrolling=True, **kwargs) -> None:
        super(QWidget, self).__init__(parent)

        self.setContentsMargins(0,0,0,0)
        
        from jemlib.alib_propertygrid.data.DataHandler import DataHandler
        self.__praser = praser if praser else DataHandler()
        self.__navigation_connection = None

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        
        self.page_stack = QStackedWidget(self)
        self.page_stack.setContentsMargins(0,0,0,0)
        layout.addWidget(self.page_stack, 0, 0, 1, 2)

        self.back_button = QPushButton(self)
        self.back_button.setContentsMargins(0,0,0,0)
        self.back_button.setFlat(True)
        self.back_button.setIcon(IconRepository.materialIcon("arrow-left"))
        self.back_button.clicked.connect(self.navigateBackwards)
        layout.addWidget(self.back_button, 1, 0)

        self.tab_bar = PropertyTabs(self)
        self.tab_bar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.tab_bar.setContentsMargins(0,0,0,0)
        layout.addWidget(self.tab_bar, 1, 1)
        layout.setColumnStretch(1, 1)

        from .PropertyViewport import PropertyViewport
        self.__property_grid = PropertyViewport(self, self.__praser, scrolling)
        self.__property_grid.setWindowTitle("ROOT")
        self.page_stack.insertWidget(0, self.__property_grid)

        self.onNavigationTabsChanged()

    #region Get / Set Functions

    def getPraser(self):
        return self.__praser

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
        try:
            if s and self.__navigation_connection == None:
                self.__navigation_connection = self.tab_bar.currentChanged.connect(self.onNavigationIndexChanged)
            elif self.__navigation_connection and s == False:
                self.tab_bar.currentChanged.disconnect(self.onNavigationIndexChanged)
                self.__navigation_connection = None
        except (RuntimeError) as ex:
            Logger.logError("JemLib", "PropertyGrid", "setNavigationConnection", f"Failed to Update Navigation Connection : {ex}")


    def getDataObject(self):
        return self.__property_grid.getDataObject()

    def setDataObject(self, data: any):
        try:
            Logger.logDebug("JemLib", "PropertyGrid", "setDataObject", f"Setting Data: {str(data)}")
            self.__property_grid.setDataObject(data)
            Logger.logDebug("JemLib", "PropertyGrid", "setDataObject", f"Data Set: {str(data)}")
            self.onNavigationTabsChanged()
            Logger.logDebug("JemLib", "PropertyGrid", "setDataObject", f"Data Loaded: {str(data)}")
        except Exception as ex:
            Logger.logError("JemLib", "PropertyGrid", "setDataObject", f"Setting Data Failed for: {str(data)} : {ex}")

    #endregion

    #region Signal Recievers

    def onNavigationIndexChanged(self):
        try:
            tabIndex = self.tab_bar.currentIndex()
            stackIndex = self.page_stack.currentIndex()

            if stackIndex > tabIndex:
                navigate_back_amount = stackIndex - tabIndex
                self.navigateBackwards(navigate_back_amount)
        except Exception as ex:
            Logger.logError("JemLib", "PropertyGrid", "onNavigationIndexChanged", f"Failed to Update Navigation Tabs : {ex}")

    def onNavigationTabsChanged(self):
        try:
            self.setNavigationConnection(False)
            while self.tab_bar.count() != 0:
                self.tab_bar.removeTab(0)

            for i in range(0, self.page_stack.count()):
                item = self.page_stack.widget(i)
                self.tab_bar.addTab(item.windowTitle())

            self.tab_bar.setCurrentIndex(self.page_stack.currentIndex())
            self.tab_bar.scroll(self.tab_bar.width(), 0)
            self.setNavigationConnection(True)
        except Exception as ex:
            Logger.logError("JemLib", "PropertyGrid", "onNavigationTabsChanged", f"Failed to Update Navigation Tabs : {ex}")

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
            self.setCurrentIndex(lastIndex)
            self.page_stack.removeWidget(currentWidget)
        self.onNavigationTabsChanged()

    #endregion

    #region 




    
