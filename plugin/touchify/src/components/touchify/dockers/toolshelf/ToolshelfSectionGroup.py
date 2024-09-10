from uuid import uuid4
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from krita import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfPage import ToolshelfPage

class ToolshelfSectionGroup(QWidget):
    def __init__(self, parent: "ToolshelfPage") -> None:
        super().__init__(parent)
        
        self.page: "ToolshelfPage" = parent
        self.tabTitles: dict[int, str] = {}

        self.setAutoFillBackground(True)

        self.__layout = QVBoxLayout(self)
        self.__layout.setSpacing(1)
        self.__layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.__layout)
        
        self.mode = self.page.tabType

        if self.mode == "buttons":
            self.tabButton = QPushButton(self)
            self.tabButtonMenu = QMenu(self)
            self.tabButton.setMenu(self.tabButtonMenu)
            self.__layout.addWidget(self.tabButton)   
        else:
            self.tabBar = QTabBar(self)
            self.tabBar.setExpanding(False)
            self.tabBar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self.tabBar.currentChanged.connect(self.onTabBarIndexChanged)
            self.__layout.addWidget(self.tabBar) 

        self.stackPanel = QStackedWidget(self)
        self.stackPanel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.stackPanel.currentChanged.connect(self.onCurrentChanged)
        self.__layout.addWidget(self.stackPanel)    
    
    def setCurrentIndex(self, index):
        self.stackPanel.setCurrentIndex(index)
        self.onCurrentChanged(index)

    def addTab(self, item: QWidget, title: str):
        index = self.stackPanel.addWidget(item)
        if self.mode == "buttons":
            self.tabButtonMenu.addAction(title, lambda: self.setCurrentIndex(index))
            self.tabTitles[index] = title
            self.onCurrentChanged(0)
        else:
            self.tabBar.addTab(title)
            self.tabTitles[index] = title

    def onTabBarIndexChanged(self):
        self.setCurrentIndex(self.tabBar.currentIndex())

    def onCurrentChanged(self, index):
        for i in range(0, self.stackPanel.count()):

            widget = self.stackPanel.widget(i)
            if i == index:
                policy = QSizePolicy.Policy.Preferred
                widget.setSizePolicy(policy, policy)
                widget.setEnabled(True)
                widget.updateGeometry()
                widget.adjustSize()
            else:
                policy = QSizePolicy.Policy.Ignored
                widget.setSizePolicy(policy, policy)
                widget.setDisabled(False)
                widget.updateGeometry()
                widget.adjustSize()

        if self.mode == "buttons":
            if index in self.tabTitles:
                self.tabButton.setText(self.tabTitles[index])
        else:
            pass

        self.stackPanel.adjustSize()
        self.adjustSize()
        self.page.toolshelf.rootWidget.onSizeChanged()
