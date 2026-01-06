from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid
from jemlib.alib_propertygrid.data.DataHandler import *
from jemlib.alib_propertygrid.dialogs.PropertyGrid_SelectorDialog import *


from jemlib.alib_propertygrid.views.PropertyView import PropertyView
from jemlib.alib_propertygrid.views.PropertyView_Form import PropertyView_Form
from jemlib.alib_propertygrid.views.PropertyView_Sections import PropertyView_Sections
from jemlib.alib_propertygrid.views.PropertyView_Tabs import PropertyView_Tabs
from jemlib.alib_datatypes.TypedList import *
from jemlib.managers.IconRepository import *

class PropertyViewport(QWidget):

    sigPropertiesChanged = pyqtSignal()

    def __init__(self, container: PropertyGrid, praser: DataHandler, scrolling=True):
        super().__init__(parent=container)

        self.__scrolling = scrolling
        self.__parent_container = container
        self.__praser = praser
        self.__last_view_type = ""
        self.__view_type = "referenced"
        self.__modifiers: dict[str, any] = {}
        self.__limiters: list[str]  = []
        self.__dataObject = None

        self.property_view: PropertyView = None

        self.__scrollArea = None


        self.__gridLayout = QGridLayout(self)
        self.__gridLayout.setSpacing(0)
        self.__gridLayout.setContentsMargins(0,0,0,0)

        self.setLayout(self.__gridLayout)
        self.setContentsMargins(0,0,0,0)

        if self.__scrolling:
            self.__scrollArea = QScrollArea(self)
            self.__scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn) 
            self.__scrollArea.setWidgetResizable(True)
            self.__scrollArea.setContentsMargins(0,0,0,0)
            self.__gridLayout.addWidget(self.__scrollArea)

            
    #region Get / Set Functions

    def getPraser(self):
        return self.__praser

    def getLastViewType(self):
        return self.__last_view_type
    
    def setLastViewType(self, view_type: str):
        self.__last_view_type = view_type

    def getViewType(self):
        return self.__view_type
    
    def setViewType(self, view_type: str):
        if view_type == "": self.__view_type = "referenced"
        else: self.__view_type = view_type

    def getModifiers(self):
        return self.__modifiers

    def setModifiers(self, modifiers: dict[str, any] = {}):
        self.__modifiers = modifiers

    def getLimiters(self):
        return self.__limiters
    
    def setLimiters(self, limiters: list[str] = []):
        self.__limiters = limiters

    def getContainer(self):
        return self.__parent_container
            
    def setContainer(self, host: PropertyGrid):
        self.__parent_container = host
        if self.property_view: self.property_view.setViewport(self)

    def getDataObject(self):
        return self.__dataObject

    def setDataObject(self, item: any):
        try:
            Logger.logDebug("JemLib", "PropertyViewport", "setDataObject", f"Setting Data: {str(item)}")
            self.__dataObject = item

            if self.getViewType() == "referenced": view_type = self.getPraser().getObjectViewType(item)
            else: view_type = self.getViewType()

            if view_type != self.getLastViewType():
                self.setLastViewType(view_type)
                if self.property_view != None: 
                    self.property_view.deleteLater()
                    self.property_view = None

                match view_type:
                    case "tabs":
                        self.property_view = PropertyView_Tabs(self, self.getPraser())
                        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                        self.setWidget(self.property_view)
                    case "tabs_vertical":
                        self.property_view = PropertyView_Tabs(self, self.getPraser(), True)
                        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                        self.setWidget(self.property_view)
                    case "sections":
                        self.property_view = PropertyView_Sections(self, self.getPraser())
                        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                        self.setWidget(self.property_view)
                    case "form_alt":
                        self.property_view = PropertyView_Form(self, self.getPraser())
                        self.property_view.setHorizontalLabels(True)
                        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                        self.setWidget(self.property_view)
                    case "form":
                        self.property_view = PropertyView_Form(self, self.getPraser())
                        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                        self.setWidget(self.property_view)
                    case _:
                        self.property_view = PropertyView_Form(self, self.getPraser())
                        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                        self.setWidget(self.property_view)

            Logger.logDebug("JemLib", "PropertyViewport", "setDataObject", f"Updating Data Viewtype: {str(self.property_view)}")
            self.property_view.setDataObject(item)
            Logger.logDebug("JemLib", "PropertyViewport", "setDataObject", f"Data Viewtype Updated: {str(self.property_view)}")

            Logger.logDebug("JemLib", "PropertyViewport", "setDataObject", f"Setting Data Complete: {str(item)}")
        except Exception as ex:
            Logger.logError("JemLib", "PropertyViewport", "setDataObject", f"Setting Data Failed: {ex}")
            

    def setFrameShape(self, shape: QFrame.Shape):
        if self.__scrollArea:
            self.__scrollArea.setFrameShape(shape)

    def setVerticalScrollBarPolicy(self, policy: Qt.ScrollBarPolicy):
        if self.__scrollArea: self.__scrollArea.setVerticalScrollBarPolicy(policy)

    def setHorizontalScrollBarPolicy(self, policy: Qt.ScrollBarPolicy):
        if self.__scrollArea: self.__scrollArea.setHorizontalScrollBarPolicy(policy)

    def setWidget(self, widget: QWidget):
        if self.__scrollArea:
            self.__scrollArea.setWidget(widget)
        else:
            self.__gridLayout.addWidget(widget)


    #endregion

    #region General Functions

    def syncProperties(self):
        if self.property_view: self.property_view.onPropertiesChanged()
        self.sigPropertiesChanged.emit()

    #endregion

class PropertyViewportNested(PropertyGrid):

    sigPropertiesChanged = pyqtSignal()

    def __init__(self, parent: "PropertyView", container: "PropertyGrid", praser: "DataHandler", scrolling=True):
        super().__init__(parent, praser, scrolling)

        self.getPropertyGrid().sigPropertiesChanged.connect(self.onParentPropertiesChanged)

    #region Get / Set

    def getLastViewType(self):
        return self.getPropertyGrid().getLastViewType()
    
    def setLastViewType(self, view_type: str):
        return self.getPropertyGrid().setLastViewType(view_type)

    def getViewType(self):
        return self.getPropertyGrid().getViewType()
    
    def setViewType(self, view_type: str):
        self.getPropertyGrid().setViewType(view_type)

    def getModifiers(self):
        return self.getPropertyGrid().getModifiers()

    def setModifiers(self, modifiers: dict[str, any] = {}):
        self.getPropertyGrid().setModifiers(modifiers)

    def getLimiters(self):
        return self.getPropertyGrid().getLimiters()
    
    def setLimiters(self, limiters: list[str] = []):
        self.getPropertyGrid().setLimiters(limiters)

    def getDataObject(self):
        return self.getPropertyGrid().getDataObject()
    
    def setDataObject(self, item: any):
        self.getPropertyGrid().setDataObject(item)

    def setFrameShape(self, shape: QFrame.Shape):
        self.getPropertyGrid().setFrameShape(shape)

    #endregion

    #region Signal Reciever

    def onParentPropertiesChanged(self):
        self.sigPropertiesChanged.emit()

    #endregion

    #region General Functions

    def syncProperties(self):
        self.getPropertyGrid().syncProperties()
        self.sigPropertiesChanged.emit()

    #endregion

    