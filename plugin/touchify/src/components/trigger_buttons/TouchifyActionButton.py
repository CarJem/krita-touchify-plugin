from enum import Enum
import typing
from touchify.src.managers.shared.resources import ResourceManager
from touchify.__env__ import *
from touchify.src.extensions.krita_extensions import *
from krita import *
from touchify.src.managers.shared.settings import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from PyQt5.QtCore import pyqtProperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.managers.normal.action_manager import ActionManager


class TouchifyActionButton(QToolButton):

    class TriggerMode(Enum):
        OnClick=0
        OnPress=1
        OnRelease=2

    triggerActivated = pyqtSignal()
    triggerToggled = pyqtSignal(bool)

    clicked: typing.ClassVar[QtCore.pyqtSignal]
    released: typing.ClassVar[QtCore.pyqtSignal]
    pressed: typing.ClassVar[QtCore.pyqtSignal]

    def __init__(self, parent = None):
        super(TouchifyActionButton, self).__init__(parent)
        self.triggerToggled.connect(self.onToggled)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.NoFocus)
        self._resizing = False

        self.trigger_source = None
        self.trigger_mode = TouchifyActionButton.TriggerMode.OnClick

        self._toggled = False
        self._menu_toggled = False
        
        self.meta_icon: QIcon = None
        self.meta_text: str = ""

        self.is_action = False
        self.is_action_checkable = False
        self.action_id: str = ""
        self.action_use_icon = False
        self.action_source: QAction = None

        self.is_toolbox_child = False
        self.is_toolbox_menu = False
        self.toolbox_item_list = []

        self.is_tool_action = False
        self.tool_action_id = ""
        self.tool_last_action_id = ""

        self.brush_id = ""
        self.is_brush_selected = False


        qApp.paletteChanged.connect(self.onPaletteChanged)
        self.onPaletteChanged()

        self.released.connect(self.onReleased)
        self.pressed.connect(self.onPressed)
        self.clicked.connect(self.onClicked)

    @pyqtProperty(bool)
    def menu_toggled(self):
        return self._menu_toggled
    
    @menu_toggled.setter
    def menu_toggled(self, state):
        self._menu_toggled = state
        self.style().polish(self)

    @pyqtProperty(bool)
    def toggled(self):
        return self._toggled
    
    @toggled.setter
    def toggled(self, state):
        self._toggled = state
        self.style().polish(self)
        self.triggerToggled.emit(state)

    def trigger(self):
        if self.trigger_source:
            self.trigger_source()
        self.triggerActivated.emit()

    #region Setup

    def setupBrushChange(self, source_window: "WindowAPI", brush_id: str, is_active: bool):
        self.brush_id = brush_id
        source_window.notifier.brushChanged.connect(self.onBrushChanged)
        if is_active: 
            self.is_brush_selected = True
            self.repaint()

    def setupToolChange(self, source_window: "WindowAPI", tool_id: str, is_active: bool):
        self.is_tool_action = True
        self.tool_action_id = tool_id
        source_window.notifier.toolChanged.connect(self.onToolChanged)

        if is_active: self.toggled = (True)

    def setupToolboxButton(self, is_toolbox_menu: bool, item_list: list[str]):
        self.is_toolbox_child = True
        self.is_toolbox_menu = is_toolbox_menu
        self.trigger_mode = TouchifyActionButton.TriggerMode.OnRelease if is_toolbox_menu else TouchifyActionButton.TriggerMode.OnPress
        self.toolbox_item_list = item_list
        self.onPaletteChanged()

    def setupAction(self, action: QAction, action_id: str):
        self.is_action = True
        self.action_source = action
        self.action_id = action_id

        action.changed.connect(self.onActionChanged)

    def setupActionCheckChange(self, action: QAction, action_id: str, is_active: bool):
        self.is_action = True
        self.is_action_checkable = True
        self.action_id = action_id
        self.action_source = action

        action.changed.connect(self.onActionChanged)
        action.toggled.connect(self.onActionToggled)

        if is_active: self.toggled = (True)
    
    def setupActionIcon(self):
        self.action_use_icon = True

    #endregion

    #region Signals

    def onToolboxButtonSwap(self, ac: QAction):
        self.tool_action_id = ac.objectName()
        self.setTrigger(ac.trigger, TouchifyActionButton.TriggerMode.OnClick)
        self.setText(ac.text())
        self.setIcon(ac.icon())

        if self.tool_action_id == self.tool_last_action_id: self.toggled = True
        else: self.toggled = False


        if self.tool_action_id in self.toolbox_item_list: self.menu_toggled = (True)
        else: self.menu_toggled = (False)

    def onActionChanged(self):
        if self.action_use_icon: 
            KritaAPI.get_action(self.action_source.objectName())
            self.setIcon(self.action_source.icon())

    def onPaletteChanged(self):
        if self.is_toolbox_child:
            self.setStyleSheet(f"""
                    QPushButton::menu-indicator {{ 
                        image: none; 
                    }} 
                    
                    QToolButton::menu-indicator {{ 
                        image: none; 
                    }}
                    
                    QToolButton {{
                        padding: 4px;
                        opacity: 0.65;
                    }}
            """)
            palette = QPalette()
            palette.setColor(QPalette.Button, QColor(74, 108, 134))
            self.setPalette(palette)
    
    def onActionToggled(self, checked: bool):
        self.toggled = (checked)

    def onBrushChanged(self, current_brush: Resource):
        __brush_presets = ResourceManager.brushPresets()
        if id not in __brush_presets: return
        btn_preset = __brush_presets[id]
        
        if current_brush != btn_preset: 
            self.is_brush_selected = False
            self.repaint()
        else: 
            self.is_brush_selected = True
            self.repaint()

    def onToolChanged(self, current_tool: str):
        self.tool_last_action_id = current_tool
        if self.tool_action_id != "" and current_tool == self.tool_action_id: self.toggled = (True)
        else: self.toggled = (False)

        if self.is_toolbox_menu and current_tool in self.toolbox_item_list: self.menu_toggled = (True)
        else: self.menu_toggled = (False)
        

    def onReleased(self):
        if self.trigger_mode == TouchifyActionButton.TriggerMode.OnRelease: self.trigger()

    def onPressed(self):
        if self.trigger_mode == TouchifyActionButton.TriggerMode.OnPress: self.trigger()

    def onClicked(self):
        if self.trigger_mode == TouchifyActionButton.TriggerMode.OnClick: self.trigger()

    def onToggled(self, toggled):
        p = self.window().palette()
        if toggled: p.setColor(QPalette.ColorRole.Button, p.color(QPalette.Highlight))
        self.setPalette(p)
        self.repaint()

    def onTriggered(self):
        if self.is_action_checkable:
            self.toggled = (self.action_source.isChecked())
        elif self.is_tool_action:
            self.toggled = (self.tool_action_id == self.tool_last_action_id)

        if self.is_toolbox_menu:
            self.menu_toggled = (self.tool_last_action_id in self.toolbox_item_list)

    #endregion

    #region Setters

    def setTrigger(self, onClick, mode: TriggerMode):
        self.trigger_mode = mode
        self.trigger_source = onClick

    def setMetadata(self, text, icon):
        self.meta_text = text
        self.meta_icon = icon

    def setIcon(self, icon):
        if isinstance(icon, QIcon):
            super().setIcon(icon)
        elif isinstance(icon, QPixmap):
            super().setIcon(QIcon(icon))
        elif isinstance(icon, QImage):
            super().setIcon(QIcon(QPixmap.fromImage(icon)))
        else:
            raise TypeError(f"Unable to set icon of invalid type {type(icon)}")

    def setMenu(self, menu: QMenu):
        if self.is_toolbox_child:
            self.is_toolbox_menu = True if menu else False
        else:
            self.is_toolbox_menu = False

        super().setMenu(menu)

    def setColor(self, color): # In case the Krita API opens up for a "color changed" signal, this could be useful...
        if isinstance(color, QColor):
            pxmap = QPixmap(self.iconSize())
            pxmap.fill(color)
            self.setIcon(pxmap)
        else:
            raise TypeError(f"Unable to set color of invalid type {type(color)}")




    #endregion

    #region Events

    def enterEvent(self, event):
        super().enterEvent(event)

        if self.is_toolbox_child: self.enterToolboxEvent(event)

    def enterToolboxEvent(self, event):
        if len(KritaAPI.get_documents()) == 0: # disable buttons before document is visible
            self.setEnabled(False)
        else:
            self.setEnabled(True)

    #endregion

    #region Painting

    def paintEvent(self, e: QPaintEvent):
        super().paintEvent(e)
        if self.is_brush_selected: self.paintBrushHighlight(e)
        if self.is_toolbox_child: self.paintToolboxMenu(e)

    def paintToolboxMenu(self, e: QPaintEvent):
        if self.is_toolbox_menu:
            rect = e.rect()

            triangleScale = 4
            triangleOffset = 2
            triangleFill = qApp.palette().text().color()

            point1 = QPoint(rect.bottomRight().x() - triangleOffset, rect.bottomRight().y() - triangleOffset)
            point2 = QPoint(point1.x(), point1.y() - triangleScale)
            point3 = QPoint(point1.x() - triangleScale, point1.y())

            painter = QPainter(self)
            path = QPainterPath()
            #painter.begin(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path.moveTo(point1)
            path.lineTo(point2)
            path.lineTo(point3)
            path.lineTo(point1)
            painter.fillPath(path, triangleFill)

    def paintBrushHighlight(self, e: QPaintEvent):
        hc = self.window().palette().color(QPalette.ColorRole.Highlight)
        rect = e.rect()
        opacity = 75
        thickness = 4

        painter = QPainter(self)
        painter.setBrush(QColor(hc.red(), hc.green(), hc.blue(), opacity))
        painter.drawRect(rect)

        rectPath = QPainterPath()
        rectPath.addRect(rect.x(),rect.y(),rect.width(),rect.height())
        painter.setPen(QPen(hc, thickness))
        painter.drawPath(rectPath)

    #endregion

