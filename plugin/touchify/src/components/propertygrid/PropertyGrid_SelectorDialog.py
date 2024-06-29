from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from krita import *
from .PropertyGrid_Dialog import PropertyGrid_Dialog

from ...resources import ResourceManager

from ...ext.extensions import KritaExtensions

class PropertyGrid_SelectorDialog(PropertyGrid_Dialog):

    selected_item: str

    def __init__(self, parent: QStackedWidget):
        super().__init__(parent)

        self.listView = QListWidget()
        self.listView.setResizeMode(QListView.ResizeMode.Adjust)
        self.listView.setUniformItemSizes(True)
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

                filterAllows = currentFilter.lower() in currentItem.text().lower() or currentFilter.lower() in str(currentItem.data(0)).lower()

                if filterAllows or currentFilter == "":
                    currentItem.setHidden(False)
                else:
                    currentItem.setHidden(True)
        

    def updateSelected(self):
        currentItem = self.listView.currentItem()
        if currentItem:
            self.selected_item = str(currentItem.data(0))
        else: 
            self.selected_item = "null"


    def selectedResult(self):
        return self.selected_item

    def load_list(self, mode):
        if mode == "icons":
            self.listView.setViewMode(QListView.ViewMode.IconMode)
            icons = KritaExtensions.getIconList()
            for iconName in icons:
                listItem = QListWidgetItem()
                listItem.setIcon(ResourceManager.iconLoader(iconName))
                listItem.setText(iconName)
                listItem.setData(0, iconName)
                self.listView.addItem(listItem)

            custom_icons = ResourceManager.getCustomIconList()
            for customIconName in custom_icons:
                displayName = str(customIconName)[len("custom:"):] + " (Custom)"
                listItem = QListWidgetItem()
                listItem.setIcon(ResourceManager.iconLoader(customIconName))
                listItem.setText(displayName)
                listItem.setData(0, customIconName)
                self.listView.addItem(listItem)

        elif mode == "dockers":
            dockers = Krita.instance().dockers()
            for dockerData in dockers:
                displayName = dockerData.windowTitle() + " [{0}]".format(dockerData.objectName())
                listItem = QListWidgetItem()
                listItem.setText(displayName)
                listItem.setData(0, dockerData.objectName())
                self.listView.addItem(listItem)
        elif mode == "actions":
            actions = Krita.instance().actions()
            for actionData in actions:
                displayName = actionData.text() + " [{0}]".format(actionData.objectName())
                listItem = QListWidgetItem()
                listItem.setText(displayName)
                listItem.setIcon(actionData.icon())
                listItem.setData(0, actionData.objectName())
                self.listView.addItem(listItem)
        
        self.listView.model().sort(0, Qt.SortOrder.DescendingOrder)