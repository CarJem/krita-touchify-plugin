from PyQt5.QtGui import QPaintEvent
from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *

class KisSliderSpinBox(QDoubleSpinBox):
   
    def __init__(self, min: float = 0, max: float = 100, isInt: bool = False, parent=None):
        super(KisSliderSpinBox, self).__init__(parent)

        self.setMinimumWidth(100)
        self.setFixedHeight(30)

        self.editMode = False
        self.editModeInit = False
        self.scaling = 1
        self.isInt = isInt
        self.contextMenuOpened = False

        self.setRange(min, max)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.lineEdit().setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.lineEdit().installEventFilter(self)
        self.lineEdit().setMouseTracking(True)
        self.endEdit()

        self.editingFinished.connect(self.endEdit)
        self.lineEdit().selectionChanged.connect(self.onSelectionChanged)
        self.lineEdit().returnPressed.connect(self.endEdit)
        super().valueChanged.connect(self.updateProgBar)

    def onSelectionChanged(self):
        if self.editMode == False:
            self.lineEdit().deselect()

    def eventFilter(self, o: QObject, e: QEvent) -> bool:
        if e.type() == QEvent.Type.MouseButtonPress or e.type() == QEvent.Type.MouseMove:
            m: QMouseEvent = e
            if self.editMode == False:
                if m.buttons() == Qt.MouseButton.LeftButton:
                    self.setFocus()
                    delta = m.pos().x() / self.lineEdit().width()
                    spinboxValue = delta**self.scaling * self.maximum()
                    if self.isInt:
                        self.setValue(int(spinboxValue))
                    else:
                        self.setValue(spinboxValue)
                elif m.buttons() == Qt.MouseButton.RightButton:
                    self.startEdit()
                    e.ignore()
            return True
        elif e.type() == QEvent.Type.KeyPress:
            e: QKeyEvent = e
            if self.editMode:
                if (e.key() == Qt.Key.Key_Return or
                    e.key() == Qt.Key.Key_Enter or
                    e.key() == Qt.Key.Key_Escape): self.endEdit()
            else:
                e.ignore()
            return True
        return super().eventFilter(o, e)
    
    def textFromValue(self, value: float):
        if self.isInt:
            return str(int(value))
        else:
            return super().textFromValue(value)
         
    def contextMenuEvent(self, e: QContextMenuEvent):
        if self.editMode == False:
            e.ignore()
        elif self.editModeInit == False:
            self.editModeInit = True
            e.ignore()
        else:
            self.contextMenuOpened = True
            super().contextMenuEvent(e)

    def focusInEvent(self, e: QFocusEvent):
        if self.contextMenuOpened:
            self.contextMenuOpened = False
        super().focusInEvent(e)

    def focusOutEvent(self, e: QFocusEvent):
        super().focusOutEvent(e)

    def getDelta(self):
        return (self.value() / self.maximum())**(1./self.scaling)

    def endEdit(self):
        if self.contextMenuOpened:
            return
        
        self.editMode = False
        self.editModeInit = False
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setCursor(Qt.CursorShape.SplitHCursor)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.lineEdit().deselect()
        self.updateProgBar()

    def startEdit(self):
        self.editMode = True
        self.lineEdit().unsetCursor()
        self.lineEdit().setReadOnly(False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.lineEdit().selectAll()
        self.updateProgBar()
        
    def setRange(self, min, max):
        super().setRange(min, max)

    def setScaling(self, s):
        self.scaling = s

    def stepDown(self):
        self.endEdit()
        super().stepDown()

    def stepBy(self, step):
        self.endEdit()
        super().stepBy(step)

    def stepUp(self):
        self.endEdit()
        super().stepUp()

    def updateProgBar(self):
        delta = self.getDelta()
        pre_highlight = qApp.palette().color(QPalette.ColorRole.Highlight)

        if self.editMode:
            pre_highlight = pre_highlight.darker(150)

        highlight = pre_highlight.name().split("#")[1]
        background = qApp.palette().color(QPalette.ColorRole.Base).name().split("#")[1]

        if delta == 0:
            self.lineEdit().setStyleSheet(f"QLineEdit {{background-color: #{background}}}")
        elif delta >= 1:
            self.lineEdit().setStyleSheet(f"QLineEdit {{background-color: #{highlight}}}")
        else:
            buttonStyle = f"""QLineEdit {{background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #{highlight}, 
            stop:{delta} #{highlight}, 
            stop:{delta + 0.001} #{background}, 
            stop:1 #{background}) }}"""
            self.lineEdit().setStyleSheet(buttonStyle)

    def paintEvent(self, e: QPaintEvent | None) -> None:
        return super().paintEvent(e)

    def setValue(self, val):
        super().setValue(val)

    def setAffixes(self, pre, suf):
        self.setPrefix(pre)
        self.setSuffix(suf)

    def connectValueChanged(self, func):
        super().valueChanged.connect(func)

    def synchronize(self):
        pass
