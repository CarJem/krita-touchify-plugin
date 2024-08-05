from uuid import uuid4
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .ToolshelfDockerButtons import ToolshelfDockerButtons
from krita import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..pages.ToolshelfPage import ToolshelfPage

class ToolshelfPageTabWidget(QWidget):
    def __init__(self, parent: "ToolshelfPage") -> None:
        super().__init__(parent)
        
        self.page: "ToolshelfPage" = parent
        self.tabTitles: dict[int, str] = {}

        self.setAutoFillBackground(True)

        self.__layout = QVBoxLayout(self)
        self.__layout.setSpacing(1)
        self.__layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.__layout)

        self.tabBar = QPushButton(self)
        self.tabBarMenu = QMenu(self)
        self.tabBar.setMenu(self.tabBarMenu)
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
        self.tabBarMenu.addAction(title, lambda: self.setCurrentIndex(index))
        self.tabTitles[index] = title
        self.onCurrentChanged(0)

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

        if index in self.tabTitles:
            self.tabBar.setText(self.tabTitles[index])
        self.stackPanel.adjustSize()
        self.adjustSize()
        self.page.toolshelf.dockWidget.onSizeChanged()
