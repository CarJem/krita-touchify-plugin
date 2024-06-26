from PyQt5.QtWidgets import QMdiArea, QDockWidget
from ...ext.extensions import KritaExtensions
from ...config import InternalConfig, KritaSettings
from ... import stylesheet
from ...variables import KRITA_ID_DOCKER_SHAREDTOOLDOCKER, KRITA_ID_MENU_SETTINGS, TOUCHIFY_ID_OPTIONS_NU_OPTIONS_ALTERNATIVE_TOOLBOX_POSITION, TOUCHIFY_ID_OPTIONSROOT_MAIN
from .NtWidgetPad import NtWidgetPad
from krita import *
from PyQt5.QtCore import QObject, QEvent, QPoint
from PyQt5.QtWidgets import QMdiArea, QDockWidget
from ...variables import *
from ..toolshelf.ToolshelfWidget import ToolshelfWidget

class NtToolboxContainer():

    def __init__(self, window: Window):
        self.qWin = window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)
        toolbox = self.qWin.findChild(QDockWidget, 'ToolBox')

        # Create "pad"
        self.pad = NtWidgetPad(self.mdiArea)
        self.pad.setObjectName("toolBoxPad")
        self.pad.borrowDocker(toolbox)
        self.pad.setViewAlignment('left')

        # Create and install event filter
        self.adjustFilter = Nt_AdjustToSubwindowFilter(self.mdiArea)
        self.adjustFilter.setTargetWidget(self.pad)
        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)
        self.qWin.installEventFilter(self.adjustFilter)

        # Create visibility toggle action
        action = window.createAction(KRITA_ID_DOCKER_SHAREDTOOLDOCKER, "Show Toolbox", KRITA_ID_MENU_SETTINGS)
        action.toggled.connect(self.pad.toggleWidgetVisible)
        action.setCheckable(True)
        action.setChecked(True)

        # Disable the related QDockWidget
        self.dockerAction = window.qwindow().findChild(QDockWidget, "ToolBox").toggleViewAction()
        self.dockerAction.setEnabled(False)

    def onSubWindowActivated(self, subWin):
        if subWin:
            self.pad.adjustToView()
            self.updateStyleSheet()

    def findDockerAction(self, window, text):
        dockerMenu = None

        for m in window.qwindow().actions():
            if m.objectName() == "settings_dockers_menu":
                dockerMenu = m

                for a in dockerMenu.menu().actions():
                    if a.text().replace('&', '') == text:
                        return a

        return False

    def updateStyleSheet(self):
        self.pad.setStyleSheet(stylesheet.nu_toolbox_style)

    def close(self):
        self.mdiArea.subWindowActivated.disconnect(self.ensureFilterIsInstalled)
        self.qWin.removeEventFilter(self.adjustFilter)
        self.dockerAction.setEnabled(True)
        return self.pad.close()

class NtToolOptions(QObject):
    def __init__(self, window):
        super(NtToolOptions, self).__init__(window.qwindow())
        self.qWin: QWindow = window.qwindow()

        if InternalConfig.instance().nuOptions_ToolboxOnRight: 
            self.alignment = 'left'
        else: 
            self.alignment= 'right'

        self.tooloptions = NtDockers(window, self.alignment, True)
        self.setViewAlignment(self.alignment)


    def onConfigUpdate(self):
        if self.tooloptions:
            self.tooloptions.toolshelf.onConfigUpdated()

    def setViewAlignment(self, alignment):
        self.alignment = alignment
        self.tooloptions.pad.setViewAlignment(self.alignment)

    def onKritaConfigUpdate(self):
        if self.tooloptions:
            self.tooloptions.toolshelf.onKritaConfigUpdate()

        if self.alignment == 'right' and InternalConfig.instance().nuOptions_ToolboxOnRight:
            self.setViewAlignment('left')
        elif self.alignment == 'left' and not InternalConfig.instance().nuOptions_ToolboxOnRight:
            self.setViewAlignment('right')

    def updateStyleSheet(self):
        self.tooloptions.updateStyleSheet()

    def show(self):
        self.tooloptions.pad.show()

    def close(self):
        self.tooloptions.close()

class NtToolbox(QObject):
    def __init__(self, window):
        super(NtToolbox, self).__init__(window.qwindow())
        self.qWin: QWindow = window.qwindow()

        viewAlignment = InternalConfig.instance().nuOptions_ToolboxOnRight

        self.toolbox = NtToolboxContainer(window)
        self.tooloptions = NtDockers(window, viewAlignment)

        if viewAlignment: self.setViewAlignment('right')
        else: self.setViewAlignment('left')

        self.alternativeToolboxPos = InternalConfig.instance().nuOptions_AlternativeToolboxPosition

        self.toolbox.pad.btnHide.clicked.connect(self.adjustToPad)
        self.tooloptions.pad.btnHide.clicked.connect(self.adjustToPad)

        self.tooloptions.pad.installEventFilter(self)
        self.toolbox.pad.installEventFilter(self)
        self.qWin.installEventFilter(self)

    def eventFilter(self, obj, e):

        if (e.type() == QEvent.Type.Move or e.type() == QEvent.Type.Resize):
            self.adjustToPad()
        
        return False 

    def adjustToPad(self):
        if self.tooloptions == None:
            if self.toolbox:
                self.toolbox.pad.offset_x_left = 0
                self.toolbox.pad.offset_x_right = 0
                self.toolbox.pad.adjustToView()
            return
        elif self.toolbox == None:
            if self.tooloptions:
                self.tooloptions.pad.offset_x_left = 0
                self.tooloptions.pad.offset_x_right = 0
                self.tooloptions.pad.adjustToView()
            return
        else:
            if self.alternativeToolboxPos:
                if self.alignment == 'left':
                    self.toolbox.pad.offset_x_left = self.tooloptions.pad.width()
                    self.toolbox.pad.offset_x_right = 0
                elif self.alignment == 'right':
                    self.toolbox.pad.offset_x_right = self.tooloptions.pad.width()
                    self.toolbox.pad.offset_x_left = 0

                self.tooloptions.pad.offset_x_right = 0
                self.tooloptions.pad.offset_x_left = 0
            else:
                if self.alignment == 'left':
                    self.tooloptions.pad.offset_x_left = self.toolbox.pad.width()
                    self.tooloptions.pad.offset_x_right = 0
                elif self.alignment == 'right':
                    self.tooloptions.pad.offset_x_right = self.toolbox.pad.width()
                    self.tooloptions.pad.offset_x_left = 0

                self.toolbox.pad.offset_x_right = 0
                self.toolbox.pad.offset_x_left = 0
            self.tooloptions.pad.adjustToView()

    def onConfigUpdate(self):
        if self.tooloptions:
            self.tooloptions.toolshelf.onConfigUpdated()

    def setViewAlignment(self, alignment):
        self.alignment = alignment
        self.toolbox.pad.setViewAlignment(self.alignment)
        self.tooloptions.pad.setViewAlignment(self.alignment)

    def show(self):
        self.tooloptions.pad.show()
        self.toolbox.pad.show()

    def onKritaConfigUpdate(self):
        if self.tooloptions:
            self.tooloptions.toolshelf.onKritaConfigUpdate()

        if not self.alternativeToolboxPos and InternalConfig.instance().nuOptions_AlternativeToolboxPosition:
            self.alternativeToolboxPos = True
            self.adjustToPad()
        elif self.alternativeToolboxPos and not InternalConfig.instance().nuOptions_AlternativeToolboxPosition:
            self.alternativeToolboxPos = False
            self.adjustToPad()

        if self.alignment == 'left' and InternalConfig.instance().nuOptions_ToolboxOnRight:
            self.setViewAlignment('right')
            self.adjustToPad()
        elif self.alignment == 'right' and not InternalConfig.instance().nuOptions_ToolboxOnRight:
            self.setViewAlignment('left')
            self.adjustToPad()

    def updateStyleSheet(self):
        self.toolbox.updateStyleSheet()
        self.tooloptions.updateStyleSheet()

    def close(self):
        self.toolbox.pad.btnHide.clicked.disconnect(self.adjustToPad)
        self.tooloptions.pad.btnHide.clicked.disconnect(self.adjustToPad)

        self.tooloptions.pad.removeEventFilter(self)
        self.toolbox.pad.removeEventFilter(self)
        self.qWin.removeEventFilter(self)

        self.tooloptions.close()
        self.toolbox.close()
        self.toolbox = None
        self.tooloptions = None

class NtDockers():

    def __init__(self, window: Window, alignment: str, isPrimaryPanel: bool = False):
        self.qWin = window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)

        self.toolshelf = ToolshelfWidget(isPrimaryPanel)

        # Create "pad"
        self.pad = NtWidgetPad(self.mdiArea)
        self.pad.setObjectName("toolOptionsPad")
        self.pad.setViewAlignment(alignment)
        self.pad.borrowDocker(self.toolshelf)

        # Create and install event filter
        self.adjustFilter = Nt_AdjustToSubwindowFilter(self.mdiArea)
        self.adjustFilter.setTargetWidget(self.pad)
        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)
        self.qWin.installEventFilter(self.adjustFilter)

        # Create visibility toggle action 
        action_id = TOUCHIFY_ID_ACTION_SHOW_TOOL_OPTIONS if isPrimaryPanel else TOUCHIFY_ID_ACTION_SHOW_TOOL_OPTIONS_ALT
        action_name = "Show Tool Options Shelf" if isPrimaryPanel else "Show Toolbox Shelf"
        action = window.createAction(action_id, action_name, KRITA_ID_MENU_SETTINGS)
        action.toggled.connect(self.pad.toggleWidgetVisible)
        action.setCheckable(True)
        action.setChecked(True)

    def onSubWindowActivated(self, subWin):
        if subWin:
            self.pad.adjustToView()
            self.updateStyleSheet()
    
    def onConfigUpdate(self):
        pass

    def onKritaConfigUpdate(self):
        pass

    def updateStyleSheet(self):
        self.toolshelf.updateStyleSheet()
        return
    
    def close(self):
        self.mdiArea.subWindowActivated.disconnect(self.onSubWindowActivated)
        self.qWin.removeEventFilter(self.adjustFilter)
        self.toolshelf.onUnload()
        self.pad.widget = None
        self.pad.widgetDocker = None
        return self.pad.close()
    
class Nt_AdjustToSubwindowFilter(QObject):
    """Event Filter object. Ensure that a target widget is moved
    to a desired position (corner of the view) when the subwindow area updates."""
    
    def __init__(self, parent=None):
        super(Nt_AdjustToSubwindowFilter, self).__init__(parent)
        self.target = None

    def eventFilter(self, obj, e):
        """Event filter: Update the Target's position to match to the current view 
        if the (sub-)window has moved, changed in size or been activated."""
        if (self.target and
            (e.type() == QEvent.Move or
            e.type() == QEvent.Resize or
            e.type() == QEvent.WindowActivate)):
            self.target.adjustToView()
            
        return False

    def setTargetWidget(self, wdgt):
        """Set which QWidget to adjust the position of."""
        self.target = wdgt