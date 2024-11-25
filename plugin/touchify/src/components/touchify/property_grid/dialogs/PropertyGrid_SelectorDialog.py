from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from krita import *
from touchify.src.stylesheet import Stylesheet
from touchify.src.components.touchify.property_grid.dialogs.PropertyGrid_Dialog import PropertyGrid_Dialog

from touchify.src.resources import ResourceManager


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
        self.listView.itemClicked.connect(self.updateSelected)

        self.selected_item = "null"

        self.filterBar = QLineEdit()
        self.filterBar.setPlaceholderText("Filter...")
        self.filterBar.textChanged.connect(self.onFilterUpdate)

        self.list_info_layout = QHBoxLayout()
        self.list_info_layout.setContentsMargins(0,0,0,0)
        self.list_info_layout.setSpacing(0)

        self.list_info = QFrame(self)
        self.list_info.setContentsMargins(0,0,0,0)
        self.list_info.setLayout(self.list_info_layout)

        self.list_info_text = QLabel(self.list_info)
        self.list_info_text.setContentsMargins(0,0,0,0)

        self.list_info_icon = QPushButton(self.list_info)
        self.list_info_icon.setContentsMargins(0,0,0,0)
        self.list_info_icon.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.list_info_icon.setFlat(True)


        self.list_info_layout.addWidget(self.list_info_icon)
        self.list_info_layout.addWidget(self.list_info_text, 1)

        self.dlgLayout = QVBoxLayout(self)
        self.dlgLayout.addWidget(self.listView)
        self.dlgLayout.addWidget(self.list_info)
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
            self.list_info_icon.setIcon(currentItem.icon())
            self.list_info_text.setText(self.selected_item)
        else: 
            self.selected_item = "null"
            self.list_info_icon.setIcon(QIcon())
            self.list_info_text.setText("")


    def selectedResult(self):
        return self.selected_item

    def load_list(self, mode):
        self.listView.setSelectionRectVisible(True)
        self.listView.setStyleSheet(Stylesheet.instance().propertygrid_selectordialog_listview)
        if mode == "icons":
            self.listView.setViewMode(QListView.ViewMode.IconMode)
            self.listView.setUniformItemSizes(True)
            presets = ResourceManager.getIconList()
            for preset_key in presets:
                listItem = QListWidgetItem()
                listItem.setIcon(ResourceManager.iconLoader(preset_key))
                listItem.setData(DATA_INDEX, preset_key)
                self.listView.addItem(listItem)

            custom_icons = ResourceManager.getCustomIconList()
            for customIconName in custom_icons:
                listItem = QListWidgetItem()
                listItem.setIcon(ResourceManager.iconLoader(customIconName))
                listItem.setData(DATA_INDEX, customIconName)
                self.listView.addItem(listItem)
        elif mode == "brushes":
            self.listView.setViewMode(QListView.ViewMode.ListMode)
            self.listView.setUniformItemSizes(True)
            presets = ResourceManager.getBrushPresets()
            for preset_key in presets:
                preset = presets[preset_key]
                listItem = QListWidgetItem()
                listItem.setIcon(ResourceManager.brushIcon(preset.name()))
                listItem.setText(preset.name())
                listItem.setData(DATA_INDEX, preset_key)
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
                listItem = QListWidgetItem()
                listItem.setText(displayName)
                listItem.setIcon(icon)
                listItem.setData(DATA_INDEX, actionData.objectName())
                self.listView.addItem(listItem)
        
        self.listView.model().sort(0, Qt.SortOrder.DescendingOrder)