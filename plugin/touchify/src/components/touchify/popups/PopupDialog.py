from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from touchify.src.stylesheet import Stylesheet

from touchify.src.components.touchify.popups.PopupDialog_Titlebar import PopupDialog_Titlebar

from touchify.src.cfg.action.CfgTouchifyActionPopup import CfgTouchifyActionPopup
from touchify.src.settings import *
from touchify.src.resources import *

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
        self.oldMinSize = None
        self.autoConceal = False
        self.time_since_opening = QTime()

        self.closing_method = args.closing_method

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        self.windowMode = self.metadata.window_type
        self.popupType = self.metadata.type
        self.window_allow_resize = True

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


        match self.metadata.popup_position_x:
            case CfgTouchifyActionPopup.PopupPosition.Start:
                offset_x -= 0 
            case CfgTouchifyActionPopup.PopupPosition.Center:
                offset_x -= (dialog_width // 2) 
            case CfgTouchifyActionPopup.PopupPosition.End:
                offset_x -= dialog_width
            case _:
                offset_x -= 0 

        match self.metadata.popup_position_y:
            case CfgTouchifyActionPopup.PopupPosition.Start:
                offset_y -= 0 
            case CfgTouchifyActionPopup.PopupPosition.Center:
                offset_y -= (dialog_height // 2) 
            case CfgTouchifyActionPopup.PopupPosition.End:
                offset_y -= dialog_height
            case _:
                offset_y -= 0 

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
                        if action.text() == self.metadata.id + POPUP_BTN_IDENTIFIER:
                            return self.getGeometry(qobj.mapToGlobal(QPoint(0,0)), qobj.width(), qobj.height())
            return 0, 0, 0, 0

    #endregion

    #region Interface Methods

    def initLayout(self):
        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)

        if self.windowMode == CfgTouchifyActionPopup.WindowType.Popup:
            self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        elif self.windowMode == CfgTouchifyActionPopup.WindowType.Window:
            self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
            self.setMouseTracking(True)

        if self.allowOpacity:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setWindowOpacity(self.metadata.actions_opacity)

        if self.windowMode == CfgTouchifyActionPopup.WindowType.Window:
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
        self.frameWidget.setStyleSheet(Stylesheet.instance().touchify_popup_frame(self.allowOpacity, self.metadata.actions_opacity))
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

    def generateMaxMinSize(self):
        return [0, 0, 0, 0]


    def generateSize(self):
        return [0, 0]
    
    def updateSize(self, dialog_width: int, dialog_height: int):
        if self.windowMode == CfgTouchifyActionPopup.WindowType.Popup:
            self.setFixedSize(dialog_width, dialog_height)
        elif self.windowMode == CfgTouchifyActionPopup.WindowType.Window:
            if self.isCollapsed == False:
                self.setMinimumSize(dialog_width, dialog_height)
                if self.window_allow_resize == False:
                    self.resize(dialog_width, dialog_height)
    
    def triggerPopup(self, parent: QWidget | None):
        if self.isVisible():
            self.close()
            if not self.windowMode == CfgTouchifyActionPopup.WindowType.Popup: 
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
        self.time_since_opening = QTime.currentTime()

        if self.windowMode == CfgTouchifyActionPopup.WindowType.Popup:
            self.updateSize(dialog_width, dialog_height)
            self.activateWindow()
        elif self.windowMode == CfgTouchifyActionPopup.WindowType.Window:
            self.updateSize(dialog_width, dialog_height)

    def shutdownWidget(self):
        qApp.removeEventFilter(self)

    #endregion

    #region Window Methods

    def toggleMinimized(self):
        if self.windowMode == CfgTouchifyActionPopup.WindowType.Window:
            if self._toolbar:
                if self.isCollapsed:
                    self.setMinimumSize(self.oldMinSize)
                    self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
                    self.resize(self.oldSize)
                    self.containerWidget.setVisible(True)
                    self.oldSize = None
                    self.oldMinSize = None
                    self.isCollapsed = False
                else:
                    self.oldSize = self.size()
                    self.oldMinSize = self.minimumSize()
                    self.setFixedSize(self._toolbar.width(), self._toolbar.height() + 1)
                    self.containerWidget.setVisible(False)
                    self.isCollapsed = True


    #endregion
    
    #region Events 
    
    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if (event.type() == QEvent.Type.MouseButtonRelease) or (event.type() == QEvent.Type.TabletPress) or (event.type() == QEvent.Type.TouchBegin):
            cursor_pos = QCursor.pos()
            widget_under_cursor = QApplication.widgetAt(cursor_pos)
        
            if isinstance(widget_under_cursor, QOpenGLWidget):
                if widget_under_cursor.metaObject().className() == "KisOpenGLCanvas2":
                    if self.closing_method == CfgTouchifyActionPopup.ClosingMethod.CanvasFocus and \
                        self.time_since_opening.addSecs(1) < QTime.currentTime():
                        qApp.removeEventFilter(self)
                        self.close()
                        return False

        return super().eventFilter(source, event)

    def event(self, event: QEvent):
        if event.type() == QEvent.Type.WindowDeactivate:
            if self.closing_method == CfgTouchifyActionPopup.ClosingMethod.Default:
                if self.windowMode != CfgTouchifyActionPopup.WindowType.Window:
                    self.close()
            elif self.closing_method == CfgTouchifyActionPopup.ClosingMethod.Deactivation:
                self.close()
        return super().event(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    def paintEvent(self, event=None):
        if self.allowOpacity:
            painter = QPainter(self)
            baseColor = self.palette().brush(QPalette.ColorRole.Window)
            painter.setOpacity(self.metadata.actions_opacity)
            painter.setBrush(baseColor)
            painter.setPen(baseColor.color())   
            painter.drawRect(self.rect())

    def mousePressEvent(self, e: QMouseEvent):
        return super().mousePressEvent(e)

    def enterEvent(self, e: QEnterEvent):
        return super().enterEvent(e)
    
    #endregion
