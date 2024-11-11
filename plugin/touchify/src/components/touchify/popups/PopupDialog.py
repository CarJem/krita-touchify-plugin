from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ....stylesheet import Stylesheet

from .PopupDialog_Titlebar import PopupDialog_Titlebar

from ....cfg.action.CfgTouchifyActionPopup import CfgTouchifyActionPopup
from ....settings.TouchifyConfig import *
from ....resources import *

from krita import *

POPUP_BTN_IDENTIFIER = " [Popup]"


class PopupDialog(QDockWidget):


    
    def __init__(self, parent: QWidget, args: CfgTouchifyActionPopup):     
        super().__init__(parent)  
        self.grid: QLayout = None
        self.parent: QWidget = parent
        self.metadata = args
        self.allowOpacity = False
        self.titlebarEnabled = False
        self.isCollapsed = False
        self.oldSize = None
        self.autoConceal = False

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        self.windowMode = self.metadata.window_type
        self.popupType = self.metadata.type

        qApp.installEventFilter(self)

    #region Helper Methods

    def getGeometry(self, position, width, height, isMouse = False):
        dialog_width, dialog_height = self.generateSize()

        screen = QGuiApplication.screenAt(position)
        screen_geometry = screen.geometry()
        screenSize = screen.size()

        screen_x = screen_geometry.x()
        screen_y = screen_geometry.y()
        screen_height = screenSize.height()
        screen_width = screenSize.width()

        
        offset_x = position.x() 
        offset_y = position.y()
        
        if not isMouse:
            offset_x += (width // 2) - (dialog_width // 2)
            offset_y += (height)

        actual_x = offset_x
        actual_y = offset_y

        if actual_x + dialog_width > screen_x + screen_width:
            actual_x = screen_x + screen_width - dialog_width
        elif actual_x < screen_x:
            actual_x = screen_x

        if actual_y + dialog_height > screen_y + screen_height:
            actual_y = screen_y + screen_height - dialog_height

        return [actual_x, actual_y, dialog_width, dialog_height]

    def getActionSource(self, parent: QWidget | None):
        if parent != None:
            return self.getGeometry(parent.mapToGlobal(QPoint(0,0)), parent.width(), parent.height())
        else:
            for qobj in self.parent.findChildren(QToolButton):
                actions = qobj.actions()
                if actions:
                    for action in actions:
                        if action.text() == self.metadata.display_name + POPUP_BTN_IDENTIFIER:
                            return self.getGeometry(qobj.mapToGlobal(QPoint(0,0)), qobj.width(), qobj.height())
            return 0, 0, 0, 0

    #endregion

    #region Interface Methods

    def initLayout(self):
        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)

        if self.windowMode == "popup":
            self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
            self.autoConceal = True
        elif self.windowMode == "window":
            self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
            self.setMouseTracking(True)
            self.autoConceal = False

        if self.allowOpacity:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setWindowOpacity(self.metadata.opacity)

        if self.windowMode == "window":
            self.titlebarEnabled = True
            self._toolbar = PopupDialog_Titlebar(self)
            self.setTitleBarWidget(self._toolbar)
            
        else:
            self.setTitleBarWidget(QWidget(self))
    
        self.frameWidget = QFrame(self)      
        self.frameWidget.setFrameShape(QFrame.Box)
        self.frameWidget.setFrameShadow(QFrame.Plain)
        self.frameWidget.setLineWidth(1)
        self.frameWidget.setObjectName("popupFrame")
        self.frameWidget.setStyleSheet(Stylesheet.instance().touchify_popup_frame(self.allowOpacity, self.metadata.opacity))
        self.frameWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWidget(self.frameWidget)

        self.frameLayout = QVBoxLayout(self)
        self.frameLayout.setSpacing(0)
        self.frameLayout.setContentsMargins(0,0,0,0)
        self.frameWidget.setLayout(self.frameLayout)

        self.containerWidget = QWidget(self)
        self.containerWidget.setContentsMargins(0,0,0,0)
        self.containerWidget.setLayout(self.grid)
        self.containerWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.frameLayout.addWidget(self.containerWidget)

    def generateSize(self):
        return [0, 0]
    
    def triggerPopup(self, parent: QWidget | None):
        if self.isVisible():
            self.close()
            if not self.windowMode == "popup":
                return
        
        actual_x = 0
        actual_y = 0
        dialog_width = 0
        dialog_height = 0
        
        if parent == None:
            actual_x, actual_y, dialog_width, dialog_height = self.getGeometry(QCursor.pos(), 0, 0, True)
        else:
            actual_x, actual_y, dialog_width, dialog_height = self.getActionSource(parent)
        
        self.setGeometry(actual_x, actual_y, dialog_width, dialog_height)
        self.show()

        if self.windowMode == "popup":
            self.setFixedSize(dialog_width, dialog_height)
            self.activateWindow()

    def shutdownWidget(self):
        qApp.removeEventFilter(self)

    #endregion

    #region Window Methods

    def toggleMinimized(self):
        if self._toolbar:
            if self.isCollapsed:
                self.setMinimumSize(0, 0)
                self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
                self.resize(self.oldSize)
                self.containerWidget.setVisible(True)
                self.oldSize = None
                self.isCollapsed = False
            else:
                self.oldSize = self.size()
                self.setFixedSize(self._toolbar.width(), self._toolbar.height())
                self.containerWidget.setVisible(False)
                self.isCollapsed = True


    #endregion
    
    #region Events 
    
    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        #if event.type() == QEvent.Type.MouseMove:
            #pass
        return super().eventFilter(source, event)

    def event(self, event: QEvent):
        if event.type() == QEvent.Type.WindowDeactivate:
            if self.autoConceal:
                self.close()
        return super().event(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    def paintEvent(self, event=None):
        if self.allowOpacity:
            painter = QPainter(self)
            baseColor = self.palette().brush(QPalette.ColorRole.Window)
            painter.setOpacity(self.metadata.opacity)
            painter.setBrush(baseColor)
            painter.setPen(baseColor.color())   
            painter.drawRect(self.rect())

    def mousePressEvent(self, e: QMouseEvent):
        return super().mousePressEvent(e)

    def enterEvent(self, e: QEnterEvent):
        return super().enterEvent(e)
    
    #endregion
