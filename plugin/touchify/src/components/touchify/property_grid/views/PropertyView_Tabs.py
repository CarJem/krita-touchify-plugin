from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.pyqt.VerticalQTabBar import VerticalQTabBar
from touchify.src.components.touchify.property_grid.PropertyGrid import PropertyGrid
from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import *
from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Praser import *
from touchify.src.components.touchify.property_grid.dialogs.PropertyGrid_SelectorDialog import *


from touchify.src.components.touchify.property_grid.views.PropertyView import PropertyView
from touchify.src.ext.types.TypedList import *
from touchify.src.resources import *


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.components.touchify.property_grid.PropertyPage import PropertyPage
    from touchify.src.components.touchify.property_grid.PropertyGrid import PropertyGrid


class PropertyView_Tabs(QTabWidget, PropertyView):


    def __init__(self, parent: "PropertyPage", isVertical: bool = False):
        QTabWidget.__init__(self, parent)
        PropertyView.__init__(self, parent)

        self.is_vertical = isVertical

        if self.is_vertical:
            self.setTabBar(VerticalQTabBar(self))
            self.setTabPosition(QTabWidget.TabPosition.West)
            self.setStyleSheet("QTabWidget::tab-bar {left : 0;}")

        self.setElideMode(Qt.TextElideMode.ElideNone)
        self.tabBar().adjustSize()

        self.pages: list["PropertyPage" | "PropertyGrid"] = []
        self.tabs: list[str] = []

        self.setContentsMargins(0,0,0,0)


    def setStackHost(self, host: PropertyGrid):
        for page in self.pages:
            page.setStackHost(host)

    def createTab(self, varName: str, labelData: dict):
        labelText: str = PropertyUtils_Extensions.getVariableLabel(labelData, varName)
        self.tabs.append(varName)
        return labelText
    

    def createSisterPage(self, source: any, sister_items: list[str]):
        from touchify.src.components.touchify.property_grid.PropertyPage import PropertyPage
        page = PropertyPage(self.parent_page.stackHost)
        page.propertyChanged.connect(self.onPropertyChanged)
        page.setParent(self)
        page.setLimiters(sister_items)
        page.setViewOverride("default")
        page.updateDataObject(source)
        self.pages.append(page)
        return page        
    
    def createPage(self, source: any, _varName: str):
        variable = PropertyUtils_Extensions.getVariable(source, _varName)
        restictions = PropertyUtils_Extensions.classRestrictions(source, _varName)

        is_expandable_area = False
        has_nested_tabs = False

        for entry in restictions:
            for key, value in entry.items():
                if key == "type" and value == "expandable":
                    is_expandable_area = True
                elif key == "type" and value == "nested_tabs":
                    has_nested_tabs = True

        if is_expandable_area:
            from touchify.src.components.touchify.property_grid.PropertyPage import PropertyPage
            page = PropertyPage(self.parent_page.stackHost)
            page.propertyChanged.connect(self.onPropertyChanged)
            page.setParent(self)
            page.updateDataObject(variable)
            self.pages.append(page)
            return page
        else:
            if has_nested_tabs:
                from touchify.src.components.touchify.property_grid.PropertyGrid import PropertyGrid
                page = PropertyGrid(self)
                page.rootPropertyGrid.propertyChanged.connect(self.onPropertyChanged)
                page.rootPropertyGrid.setLimiters([_varName])
                page.rootPropertyGrid.setModifiers({"no_labels": ""})
                page.rootPropertyGrid.setViewOverride("default")
                page.rootPropertyGrid.updateDataObject(source)
                self.pages.append(page)
                return page
            else:
                from touchify.src.components.touchify.property_grid.PropertyPage import PropertyPage
                page = PropertyPage(self.parent_page.stackHost)
                page.propertyChanged.connect(self.onPropertyChanged)
                page.setParent(self)
                page.setLimiters([_varName])
                page.setModifiers({"no_labels": ""})
                page.setViewOverride("default")
                page.updateDataObject(source)
                self.pages.append(page)
                return page
        
    def updateVisibility(self):
        if self.item == None:
            return
        
        hiddenItems = PropertyView.getHiddenVariableNames(self)

        for index, field in enumerate(self.tabs):     
            if field in hiddenItems: self.setTabVisible(index, False)
            else: self.setTabVisible(index, True)

    def onPropertyChanged(self, value):
        super().onPropertyChanged(value)
        self.updateVisibility()

    def unloadPropertyView(self):
        self.pages.clear()
        self.tabs.clear()
        self.clear()

    def updateDataObject(self, item):
        PropertyView.updateDataObject(self, item)

        self.unloadPropertyView()

        if self.item == None:
            return

        labelData = PropertyUtils_Extensions.classVariableLabels(item)
        variable_data, known_sisters, sister_data = PropertyView.getClassVariablesWithSisters(self, item)

        for variable_id in variable_data:    
            variable_id: str     
            page = None
            if variable_id.startswith("#"):
                pass
            elif variable_id in known_sisters:
                sister_info = sister_data[variable_id]
                if "is_group" in sister_info:
                    if bool(sister_info["is_group"]):
                        page = self.createSisterPage(item, sister_info["items"])
            else:
                page = self.createPage(item, variable_id)

            if page:
                tab = self.createTab(variable_id, labelData)
                tabIndex = self.addTab(page, tab)

        self.updateVisibility()

