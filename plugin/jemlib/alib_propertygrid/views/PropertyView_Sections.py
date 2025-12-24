from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid
from jemlib.alib_propertygrid.data.DataHandler import *
from jemlib.alib_propertygrid.dialogs.PropertyGrid_SelectorDialog import *


from jemlib.alib_propertygrid.views.PropertyView import PropertyView
from jemlib.alib_datatypes.TypedList import *
from jemlib.managers.IconRepository import *
import jemlib.alib_vaporjem.extensions.pyqt_extensions as PyQtExtensions

ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from jemlib.alib_propertygrid.PropertyViewport import PropertyViewport, PropertyViewportNested
    from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid


class PropertyView_Sections(QWidget, PropertyView):

    def __init__(self, parent: "PropertyViewport", praser: DataHandler):
        QWidget.__init__(self, parent)
        PropertyView.__init__(self, parent, praser)

        self.__sections: list["PropertyViewport" | "PropertyViewportNested"] = []
        self.__titles: list[QLabel] = []

        self.setContentsMargins(0,0,0,0)

        self.gridLayout = QVBoxLayout(self)
        self.gridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.gridLayout)



    #region Get / Set Functions

    def setViewport(self, host: PropertyGrid):
        PropertyView.setViewport(self, host)
        for page in self.__sections: page.setContainer(host)

    #endregion

    #region Create Functions

    def createTitle(self, varName: str, labelData: dict):
        labelText: str = self.getPraser().getPropertyLabel(labelData, varName)
        label = QLabel(labelText.upper())
        label.setContentsMargins(6,0,0,0)
        label.setStyleSheet("""QLabel {
            font-size: 15px;
            font-weight: bold;
            padding: 0px;
            margin: 0px;
            opacity: 0.5;
        }""")
        self.__titles.append(label)
        return label
    
    def createSisterSection(self, source: any, sister_items: list[str]):
        from jemlib.alib_propertygrid.PropertyViewport import PropertyViewport
        page = PropertyViewport(self.getViewport().getContainer(), self.getPraser())
        page.sigPropertiesChanged.connect(self.onPropertiesChanged)
        page.setParent(self)
        page.setLimiters(sister_items)
        page.setViewType("default")
        page.setDataObject(source)
        self.__sections.append(page)
        return page        
    
    def createSection(self, source: any, _varName: str):
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
            page.sigPropertiesChanged.connect(self.onPropertiesChanged)
            page.setParent(self)
            page.setDataObject(variable.variableData())
            self.__sections.append(page)
            return page
        else:
            if has_nested_tabs:
                from jemlib.alib_propertygrid.PropertyViewport import PropertyViewportNested
                page = PropertyViewportNested(self, self.getViewport().getContainer(), self.getPraser())
                page.sigPropertiesChanged.connect(self.onPropertiesChanged)
                page.setLimiters([_varName])
                page.setModifiers({"no_labels": ""})
                page.setViewType("default")
                page.setDataObject(source)
                self.__sections.append(page)
                return page
            else:
                from jemlib.alib_propertygrid.PropertyViewport import PropertyViewport
                page = PropertyViewport(self.getViewport().getContainer(), self.getPraser())
                page.sigPropertiesChanged.connect(self.onPropertiesChanged)
                page.setParent(self)
                page.setLimiters([_varName])
                page.setModifiers({"no_labels": ""})
                page.setViewType("default")
                page.setDataObject(source)
                self.__sections.append(page)
                return page

    #endregion

    #region Common Functions

    def setSectionVisible(self, index: int, visible: bool):
        self.__sections[index].setVisible(visible)
        self.__titles[index].setVisible(visible)

    def addTab(self, page: "PropertyViewport | PropertyViewportNested", title: QLabel):
        from jemlib.alib_propertygrid.PropertyViewport import PropertyViewport, PropertyViewportNested
        if isinstance(page, PropertyViewport):
            page: PropertyViewport
            page.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            page.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            page.setContentsMargins(0,0,0,0)
            page.setFrameShape(QFrame.Shape.NoFrame)
            page.widget().setContentsMargins(0,0,0,0)
            page.setMinimumSize(page.widget().sizeHint().grownBy(QMargins(0,5,0,5)))
            page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        elif isinstance(page, PropertyViewportNested):
            page: PropertyViewportNested
            page.getPropertyGrid().setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            page.getPropertyGrid().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            page.getPropertyGrid().setContentsMargins(0,0,0,0)
            page.getPropertyGrid().setFrameShape(QFrame.Shape.NoFrame)
            page.getPropertyGrid().widget().setContentsMargins(0,0,0,0)
            page.setMinimumSize(page.getPropertyGrid().widget().sizeHint().grownBy(QMargins(0,5,0,5)))
            page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.gridLayout.addWidget(title)
        self.gridLayout.addWidget(page)

    #endregion

    #region Signal Recievers

    def onPropertiesChanged(self):
        PropertyView.onPropertiesChanged(self)

        if self.getDataObject() == None: return
        
        hiddenItems = PropertyView.getHiddenVariableNames(self)

        for index, field in enumerate(self.__titles):     
            if field in hiddenItems: self.setSectionVisible(index, False)
            else: self.setSectionVisible(index, True)

    def onDataObjectChanged(self):
        self.__sections.clear()
        self.__titles.clear()
        PyQtExtensions.CommonHelpers.clearLayout(self.gridLayout)

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
                if "is_group" in sister_info:
                    if bool(sister_info["is_group"]):
                        page = self.createSisterSection(item, sister_info["items"])
            else:
                page = self.createSection(item, variable_id)

            if page:
                tab = self.createTitle(variable_id, labelData)
                tabIndex = self.addTab(page, tab)

    #endregion
