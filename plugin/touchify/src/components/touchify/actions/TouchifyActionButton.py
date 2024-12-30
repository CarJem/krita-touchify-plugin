import typing
from touchify.src.variables import *
from touchify.src.ext.KritaExtensions import *
from krita import *
from touchify.src.settings import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class TouchifyActionButton(QToolButton):

    update_requested = pyqtSignal()

    triggerActivated = pyqtSignal()

    toggled: typing.ClassVar[QtCore.pyqtSignal]
    clicked: typing.ClassVar[QtCore.pyqtSignal]
    released: typing.ClassVar[QtCore.pyqtSignal]
    pressed: typing.ClassVar[QtCore.pyqtSignal]

    def __init__(self, parent = None):
        super(TouchifyActionButton, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.NoFocus)
        self.toggled.connect(self.onToggled)
        self._resizing = False

        self.trigger_source = None
        
        self.meta_icon: QIcon = None
        self.meta_text: str = ""

        self.use_action_icon = False

        self.is_toolbox_button = False
        self.is_toolbox_menu = False
        self.toolbox_action_id = ""
        self.is_composer_active = False

        self.brushSelected = False

        qApp.paletteChanged.connect(self.updatePalette)
        self.updatePalette()

        self.released.connect(self.onReleased)
        self.pressed.connect(self.onPressed)
        self.clicked.connect(self.onClicked)

    def getToolboxItem(self):
        if self.is_toolbox_button:
            return self.toolbox_action_id
        return ""

    def onReleased(self):
        if self.is_toolbox_button:
            if self.is_toolbox_menu:
                self.trigger()

        elif self.is_composer_active:
            self.trigger()

    def onPressed(self):
        if self.is_toolbox_button:
            if not self.is_toolbox_menu:
                self.trigger()

        elif self.is_composer_active:
            self.trigger()

    def onClicked(self):
        if self.is_toolbox_button == False and self.is_composer_active == False:
            self.trigger()


    def trigger(self):
        if self.trigger_source:
            self.trigger_source()
        self.triggerActivated.emit()

    def updatePalette(self):
        if self.is_toolbox_button:
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


    def useActionIcon(self):
        self.use_action_icon = True
    
    def useToolboxButton(self, is_toolbox_menu: bool):
        self.is_toolbox_button = True
        self.is_toolbox_menu = is_toolbox_menu
        self.updatePalette()

    def setTrigger(self, onClick, is_composer: bool = False):
        self.is_composer_active = is_composer
        self.trigger_source = onClick

    def setMetadata(self, text, icon):
        self.meta_text = text
        self.meta_icon = icon

    def setBrushSelected(self, state: bool):
        self.brushSelected = state
        self.repaint()

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
        if self.is_toolbox_button:
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



    def onToggled(self, toggled):
        p = self.window().palette()
        if toggled:
            p.setColor(QPalette.Button, p.color(QPalette.Highlight))
        self.setPalette(p)


    def paintEvent(self, e: QPaintEvent):
        super().paintEvent(e)
        if self.brushSelected: self.paintBrushHighlight(e)
        if self.is_toolbox_button: self.paintToolboxMenu(e)

    def enterEvent(self, event):
        super().enterEvent(event)

        if self.is_toolbox_button: self.enterToolboxEvent(event)

    def enterToolboxEvent(self, event):
        if len(Krita.instance().documents()) == 0: # disable buttons before document is visible
            self.setEnabled(False)
        else:
            self.setEnabled(True)


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


