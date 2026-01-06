from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.alib_widgets.containers.VerticalQTabBar import VerticalQTabBar
from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid
from jemlib.alib_propertygrid.data.DataHandler import *
from jemlib.alib_propertygrid.dialogs.PropertyGrid_SelectorDialog import *


from jemlib.alib_propertygrid.views.PropertyView import PropertyView
from jemlib.alib_datatypes.TypedList import *
from jemlib.managers.IconRepository import *


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from jemlib.alib_propertygrid.PropertyViewport import PropertyViewport, PropertyViewportNested
    from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid


class PropertyView_Tabs(PropertyView):

    def __init__(self, parent: "PropertyViewport", praser: DataHandler, isVertical: bool = False):
        PropertyView.__init__(self, parent, praser)

        self.__pages: list["PropertyViewport" | "PropertyViewportNested"] = []
        self.__tabs: list[str] = []

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.gridLayout.setSpacing(0)
        self.setLayout(self.gridLayout)

        self.__tabBar = QTabWidget(self)
        if isVertical:
            self.__tabBar.setTabBar(VerticalQTabBar(self))
            self.__tabBar.setTabPosition(QTabWidget.TabPosition.West)
            self.__tabBar.setStyleSheet("QTabWidget::tab-bar {left : 0;}")
        self.__tabBar.setContentsMargins(0,0,0,0)
        self.__tabBar.setElideMode(Qt.TextElideMode.ElideNone)
        self.gridLayout.addWidget(self.__tabBar, 0, 0)

        self.__tabBar.tabBar().adjustSize()




    #region Get / Set Functions

    def setViewport(self, host: PropertyGrid):
        PropertyView.setViewport(self, host)
        for page in self.__pages: page.setContainer(host)

    #endregion

    #region Create Functions

    def createTab(self, varName: str, labelData: dict):
        labelText: str = self.getPraser().getPropertyLabel(labelData, varName)
        self.__tabs.append(varName)
        return labelText
    
    def createSisterPage(self, source: any, sister_items: list[str], sister_view_type: str):
        from jemlib.alib_propertygrid.PropertyViewport import PropertyViewport
        page = PropertyViewport(self.getViewport().getContainer(), self.getPraser())
        page.sigPropertiesChanged.connect(self.onPropertiesChanged)
        page.setParent(self)
        page.setLimiters(sister_items)
        page.setViewType(sister_view_type)
        page.setDataObject(source)
        self.__pages.append(page)
        return page        
    
    def createPage(self, source: any, _varName: str):
        variable = self.getPraser().getPropertyVariable(source, _varName)
        restictions = self.getPraser().getObjectConstraints(variable)

        is_expandable_area = False
        has_nested_tabs = False

        for entry in restictions:
            for key, value in entry.items():
                if key == "type" and value == "expandable":
                    is_expandable_area = True
                elif key == "type" and value == "nested_tabs":
                    has_nested_tabs = True

        if is_expandable_area:
            from jemlib.alib_propertygrid.PropertyViewport import PropertyViewport
            page = PropertyViewport(self.getViewport().getContainer(), self.getPraser())
            page.setParent(self)
            page.setDataObject(variable.variableData())
            page.sigPropertiesChanged.connect(self.onPropertiesChanged)
            self.__pages.append(page)
            return page
        else:
            if has_nested_tabs:
                from jemlib.alib_propertygrid.PropertyViewport import PropertyViewportNested
                page = PropertyViewportNested(self, self.getViewport().getContainer(), self.getPraser())
                page.setParent(self)
                page.setLimiters([_varName])
                page.setModifiers({"no_labels": ""})
                page.setViewType("default")
                page.setDataObject(source)
                page.setFrameShape(QFrame.Shape.NoFrame)
                page.sigPropertiesChanged.connect(self.onPropertiesChanged)
                self.__pages.append(page)
                return page
            else:
                from jemlib.alib_propertygrid.PropertyViewport import PropertyViewport
                page = PropertyViewport(self.getViewport().getContainer(), self.getPraser())
                page.setParent(self)
                page.setLimiters([_varName])
                page.setModifiers({"no_labels": ""})
                page.setViewType("default")
                page.setDataObject(source)
                page.setFrameShape(QFrame.Shape.NoFrame)
                page.sigPropertiesChanged.connect(self.onPropertiesChanged)
                self.__pages.append(page)
                return page

    #endregion

    #region Signal Recievers

    def onPropertiesChanged(self):
        PropertyView.onPropertiesChanged(self)

        if self.getDataObject() == None: return
        
        hiddenItems = PropertyView.getHiddenVariableNames(self)

        for index, field in enumerate(self.__tabs):     
            if field in hiddenItems: self.__tabBar.setTabVisible(index, False)
            else: self.__tabBar.setTabVisible(index, True)

    def onDataObjectChanged(self):
        self.__pages.clear()
        self.__tabs.clear()
        self.__tabBar.clear()

        item = self.getDataObject()
        if item == None: return

        labelData = self.getPraser().getObjectVariableLabels(item)
        variable_data, known_sisters, sister_data = PropertyView.getClassVariablesWithSisters(self, item)

        for variable_id in variable_data:    
            variable_id: str     
            page = None
            if variable_id.startswith("#"):
                pass
            elif variable_id in known_sisters:
                sister_info = sister_data[variable_id]
                view_type = "default"
                if "view_type" in sister_info:
                    view_type = sister_info["view_type"]

                if "is_group" in sister_info:
                    if bool(sister_info["is_group"]):
                        page = self.createSisterPage(item, sister_info["items"], view_type)
            else:
                page = self.createPage(item, variable_id)

            if page:
                tab = self.createTab(variable_id, labelData)
                tabIndex = self.__tabBar.addTab(page, tab)
                


    #endregion
