from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from krita import *
from .PropertyGrid_Dialog import PropertyGrid_Dialog

from ...resources import ResourceManager

from ...ext.extensions import KritaExtensions

DATA_INDEX = 3

class PropertyGrid_SelectorDialogItem(QListWidgetItem):
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

class PropertyGrid_SelectorDialog(PropertyGrid_Dialog):
    def __init__(self, parent: QStackedWidget):
        super().__init__(parent)

        self.listView = QListWidget()
        self.listView.setResizeMode(QListView.ResizeMode.Adjust)
        self.listView.setMovement(QListView.Movement.Static)
        self.listView.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.listView.itemSelectionChanged.connect(self.updateSelected)

        self.selected_item = "null"

        self.filterBar = QLineEdit()
        self.filterBar.setPlaceholderText("Filter...")
        self.filterBar.textChanged.connect(self.onFilterUpdate)

        self.dlgLayout = QVBoxLayout()
        self.dlgLayout.addWidget(self.listView)
        self.dlgLayout.addWidget(self.filterBar)

        self.setLayout(self.dlgLayout)

    def onFilterUpdate(self):
        currentFilter = self.filterBar.text()
        for i in range(self.listView.count()):
            currentItem = self.listView.item(i)
            if currentItem:

                filterAllows = currentFilter.lower() in currentItem.text().lower() or currentFilter.lower() in str(currentItem.data(DATA_INDEX)).lower()

                if filterAllows or currentFilter == "":
                    currentItem.setHidden(False)
                else:
                    currentItem.setHidden(True)
        

    def updateSelected(self):
        currentItem = self.listView.currentItem()
        if currentItem:
            self.selected_item = str(currentItem.data(DATA_INDEX))
        else: 
            self.selected_item = "null"


    def selectedResult(self):
        return self.selected_item

    def load_list(self, mode):
        if mode == "icons":
            self.listView.setViewMode(QListView.ViewMode.IconMode)
            self.listView.setUniformItemSizes(True)
            icons = KritaExtensions.getIconList()
            for iconName in icons:
                listItem = QListWidgetItem()
                listItem.setIcon(ResourceManager.iconLoader(iconName))
                listItem.setData(DATA_INDEX, iconName)
                self.listView.addItem(listItem)

            custom_icons = ResourceManager.getCustomIconList()
            for customIconName in custom_icons:
                listItem = QListWidgetItem()
                listItem.setIcon(ResourceManager.iconLoader(customIconName))
                listItem.setData(DATA_INDEX, customIconName)
                self.listView.addItem(listItem)
        elif mode == "dockers":
            self.listView.setViewMode(QListView.ViewMode.ListMode)
            self.listView.setUniformItemSizes(True)
            dockers = Krita.instance().dockers()
            for dockerData in dockers:
                displayName = f"{dockerData.windowTitle()}\n---[{dockerData.objectName()}]---"
                listItem = QListWidgetItem()
                listItem.setText(displayName)
                listItem.setData(DATA_INDEX, dockerData.objectName())
                self.listView.addItem(listItem)
        elif mode == "actions":
            self.listView.setViewMode(QListView.ViewMode.ListMode)
            self.listView.setUniformItemSizes(True)
            actions = Krita.instance().actions()
            for actionData in actions:
                displayName = f"{actionData.toolTip()}\n---[{actionData.objectName()}]---"
                icon = actionData.icon()
                if icon.isNull():
                    icon = ResourceManager.getFallbackIcon()
                listItem = QListWidgetItem()
                listItem.setText(displayName)
                listItem.setIcon(icon)
                listItem.setData(DATA_INDEX, actionData.objectName())
                self.listView.addItem(listItem)
        
        self.listView.model().sort(0, Qt.SortOrder.DescendingOrder)