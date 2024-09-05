import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from krita import *
from .KisAngleGauge import *

class KisAngleSelectorSpinBox(QDoubleSpinBox):


    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_flat = False
        self._has_focus = False
        self._is_hovered = False
        self._cached_size_hint = QSize()
        self._update_style_sheet()

    def setRange(self, min, max):
        self._cached_size_hint = QSize()
        super().setRange(min, max)

    def valueFromText(self, text):
        v = super().valueFromText(text)
        return self._closest_coterminal_angle_in_range(v, self.minimum(), self.maximum())

    def isFlat(self):
        return self._is_flat

    def setFlat(self, new_flat):
        self._is_flat = new_flat
        self._update_style_sheet()

    def enterEvent(self, e):
        self._is_hovered = True
        self._update_style_sheet()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._is_hovered = False
        self._update_style_sheet()
        super().leaveEvent(e)

    def focusInEvent(self, e):
        self._has_focus = True
        self._update_style_sheet()
        super().focusInEvent(e)

    def focusOutEvent(self, e):
        self._has_focus = False
        self._update_style_sheet()
        super().focusOutEvent(e)

    def minimumSizeHint(self):
        if self._cached_size_hint.isEmpty():
            self.ensurePolished()
            fm = QFontMetrics(self.font())
            h = self.lineEdit().minimumSizeHint().height()
            w = 0
            s = self.textFromValue(self.minimum())[:18] + self.suffix() + " "
            w = max(w, fm.horizontalAdvance(s))
            s = self.textFromValue(self.maximum())[:18] + self.suffix() + " "
            w = max(w, fm.horizontalAdvance(s))
            w += 2  # cursor blinking space
            option = QStyleOptionSpinBox()
            self.initStyleOption(option)
            hint = QSize(w, h)
            tmp = QDoubleSpinBox()
            self._cached_size_hint = self.style().sizeFromContents(QStyle.CT_SpinBox, option, hint, tmp)
        return self._cached_size_hint

    def sizeHint(self):
        return self.minimumSizeHint()

    def refreshStyle(self):
        self._cached_size_hint = QSize()
        self.updateGeometry()
        self._update_style_sheet()

    def _closest_coterminal_angle_in_range(self, angle, minimum, maximum, ok=None):
        hasCoterminalAngleInRange = True

        if angle < minimum:
            d = minimum - angle
            cycles = math.floor(d / 360.0) + 1
            angle += cycles * 360.0
            if angle > maximum:
                hasCoterminalAngleInRange = False
                angle = minimum
        elif angle > maximum:
            d = angle - maximum
            cycles = math.floor(d / 360.0) + 1
            angle -= cycles * 360.0
            if angle < minimum:
                hasCoterminalAngleInRange = False
                angle = maximum
        if ok:
            ok = hasCoterminalAngleInRange
        return angle

    def _update_style_sheet(self):
        if not self._is_flat or self._has_focus or self._is_hovered:
            self.setStyleSheet("QDoubleSpinBox{}")
        else:
            self.setStyleSheet("""
                QDoubleSpinBox{background:transparent; border:transparent;}
                QDoubleSpinBox::up-button{background:transparent; border:transparent;}
                QDoubleSpinBox::down-button{background:transparent; border:transparent;}
            """)
        self.lineEdit().setStyleSheet("QLineEdit{background:transparent;}")

class KisAngleSelector(QWidget):
    angleChanged = pyqtSignal(float)

    class FlipOptionsMode:
        NoFlipOptions = 0
        MenuButton = 1
        Buttons = 2
        ContextMenu = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.angleGauge = KisAngleGauge(self)
        self.spinBox = KisAngleSelectorSpinBox(self)
        self.spinBox.setSuffix(u"\N{DEGREE SIGN}")
        self.spinBox.setRange(0, 360)
        self.spinBox.setWrapping(True)
        self._flip_options_mode = KisAngleSelector.FlipOptionsMode.Buttons
        self._common_widgets_height = 0
        self._init_ui()
        self._init_connections()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        main_layout.addWidget(self.angleGauge)
        main_layout.addWidget(self.spinBox)
        self._init_flip_buttons()

    def _init_flip_buttons(self):
        layout_flip_buttons = QHBoxLayout(self)
        layout_flip_buttons.setSpacing(1)
        layout_flip_buttons.setContentsMargins(0, 0, 0, 0)


        self.actionFlipHorizontally = QAction(self)
        self.actionFlipHorizontally.setText(
            i18nc(
                "Flips the angle horizontally, around the vertical axis",
                "Flip the angle horizontally"
            )
        )
        self.actionFlipVertically = QAction(self)
        self.actionFlipVertically.setText(
            i18nc(
                "Flips the angle vertically, around the horizontal axis",
                "Flip the angle vertically"
            )
        )
        self.actionFlipHorizontallyAndVertically = QAction(self)
        self.actionFlipHorizontallyAndVertically.setText(
            i18nc(
                "Flips the angle horizontally and vertically",
                "Flip the angle horizontally and vertically"
            )
        )
        menuSeparator = QAction(self)
        menuSeparator.setSeparator(True)
        self.actionResetAngle = QAction(self)
        self.actionResetAngle.setText(
            i18nc(
                "Reset the angle to a predefined value",
                "Reset angle"
            )
        )
        self.menuFlip = QMenu(self)
        self.menuFlip.addAction(self.actionFlipHorizontally)
        self.menuFlip.addAction(self.actionFlipVertically)
        self.menuFlip.addAction(self.actionFlipHorizontallyAndVertically)
        self.menuFlip.addAction(menuSeparator)
        self.menuFlip.addAction(self.actionResetAngle)


        self._tool_button_flip_options = QToolButton(self)
        self._tool_button_flip_options.setPopupMode(QToolButton.InstantPopup)
        self._tool_button_flip_options.setAutoRaise(True)
        self._tool_button_flip_options.setIcon(Krita.instance().icon("view-choose"))
        self._tool_button_flip_options.setStyleSheet("QToolButton::menu-indicator { image: none }")
        self._tool_button_flip_options.setMenu(self.menuFlip)
        self._tool_button_flip_options.setFocusPolicy(Qt.StrongFocus)
        self._tool_button_flip_horizontally = QToolButton(self)
        self._tool_button_flip_horizontally.setAutoRaise(True)
        self._tool_button_flip_horizontally.setIcon(Krita.instance().icon("flip_angle_h"))
        self._tool_button_flip_horizontally.setIconSize(QSize(20, 20))
        self._tool_button_flip_horizontally.setToolTip(self.tr("Flip the angle horizontally"))
        self._tool_button_flip_horizontally.setFocusPolicy(Qt.StrongFocus)
        self._tool_button_flip_vertically = QToolButton(self)
        self._tool_button_flip_vertically.setAutoRaise(True)
        self._tool_button_flip_vertically.setIcon(Krita.instance().icon("flip_angle_v"))
        self._tool_button_flip_vertically.setIconSize(QSize(20, 20))
        self._tool_button_flip_vertically.setToolTip(self.tr("Flip the angle vertically"))
        self._tool_button_flip_vertically.setFocusPolicy(Qt.StrongFocus)
        self._tool_button_flip_horizontally_and_vertically = QToolButton(self)
        self._tool_button_flip_horizontally_and_vertically.setAutoRaise(True)
        self._tool_button_flip_horizontally_and_vertically.setIcon(Krita.instance().icon("flip_angle_hv"))
        self._tool_button_flip_horizontally_and_vertically.setIconSize(QSize(20, 20))
        self._tool_button_flip_horizontally_and_vertically.setToolTip(self.tr("Flip the angle horizontally and vertically"))
        self._tool_button_flip_horizontally_and_vertically.setFocusPolicy(Qt.StrongFocus)
        layout_flip_buttons.addWidget(self._tool_button_flip_options)
        layout_flip_buttons.addWidget(self._tool_button_flip_horizontally)
        layout_flip_buttons.addWidget(self._tool_button_flip_vertically)
        layout_flip_buttons.addWidget(self._tool_button_flip_horizontally_and_vertically)
        main_layout = self.layout()
        main_layout.addLayout(layout_flip_buttons)

    def _init_connections(self):

        self.actionFlipHorizontally.triggered.connect(self._flipHorizontally)
        self.actionFlipHorizontallyAndVertically.triggered.connect(self._flipHorizontallyAndVertically)
        self.actionFlipVertically.triggered.connect(self._flipVertically)
        self.actionResetAngle.triggered.connect(self.angleGauge.reset)

        self.angleGauge.angleChanged.connect(self._onAngleGaugeAngleChanged)
        self.spinBox.valueChanged.connect(self._onSpinBoxValueChanged)
        self._tool_button_flip_horizontally.clicked.connect(self._flipHorizontally)
        self._tool_button_flip_vertically.clicked.connect(self._flipVertically)
        self._tool_button_flip_horizontally_and_vertically.clicked.connect(self._flipHorizontallyAndVertically)

    def _onAngleGaugeAngleChanged(self, angle):
        self.spinBox.setValue(self._closestCoterminalAngleInRange(angle, self.spinBox.minimum(), self.spinBox.maximum()))

    def _onSpinBoxValueChanged(self, value):
        self.angleGauge.setAngle(value)
        self.angleChanged.emit(value)

    def _closestCoterminalAngleInRange(self, angle, minimum, maximum, ok=None):
        hasCoterminalAngleInRange = True

        if angle < minimum:
            d = minimum - angle
            cycles = math.floor(d / 360.0) + 1
            angle += cycles * 360.0
            if angle > maximum:
                hasCoterminalAngleInRange = False
                angle = minimum
        elif angle > maximum:
            d = angle - maximum
            cycles = math.floor(d / 360.0) + 1
            angle -= cycles * 360.0
            if angle < minimum:
                hasCoterminalAngleInRange = False
                angle = maximum
        if ok:
            ok = hasCoterminalAngleInRange
        return angle

    def _flipHorizontally(self):
        self.flip(Qt.Orientation.Horizontal)

    def _flipVertically(self):
        self.flip(Qt.Orientation.Vertical)

    def _flipHorizontallyAndVertically(self):
        self.flip(Qt.Orientation.Horizontal | Qt.Orientation.Vertical)

    def angle(self):
        return self.spinBox.value()

    def setAngle(self, angle):
        self.spinBox.setValue(angle)

    def setFlipOptionsMode(self, mode: FlipOptionsMode):
        self._flip_options_mode = mode
        self._updateFlipButtonsVisibility()

    def setWidgetsHeight(self, height):
        if height < 0:
            return
        self._common_widgets_height = height
        self._resizeWidgets()

    def flip(self, orientations):
        angle = self.spinBox.value()
        flipped_angle = self._flipAngle(angle, orientations)
        self.spinBox.setValue(flipped_angle)
        self.spinBox.valueChanged.emit(flipped_angle)

    def _flipAngle(self, angle, orientations: Qt.Orientations | Qt.Orientation):
        if orientations == Qt.Orientation.Horizontal | Qt.Orientation.Vertical:
            angle += 180.0
        elif orientations == Qt.Orientation.Horizontal:
            a = math.fmod(angle, 360.0)
            if a < 0:
                a += 360.0
            if a > 270.0:
                angle -= 2.0 * (a - 270.0)
            elif a > 180.0:
                angle += 2.0 * (270.0 - a)
            elif a > 90.0:
                angle -= 2.0 * (a - 90.0)
            else:
                angle += 2.0 * (90.0 - a)
        elif orientations == Qt.Orientation.Vertical:
            a = math.fmod(angle, 360.0)
            if a < 0:
                a += 360.0
            if a > 270.0:
                angle += 2.0 * (360.0 - a)
            elif a > 180.0:
                angle -= 2.0 * (a - 180.0)
            elif a > 90.0:
                angle += 2.0 * (180.0 - a)
            else:
                angle -= 2.0 * a
        return angle

    def _resizeWidgets(self):
        h = self._common_widgets_height
        if h == 0:
            h = self.spinBox.sizeHint().height()
        self.angleGauge.setFixedSize(h, h)
        self.spinBox.setFixedHeight(h)
        self._tool_button_flip_options.setFixedHeight(h)
        self._tool_button_flip_horizontally.setFixedHeight(h)
        self._tool_button_flip_vertically.setFixedHeight(h)
        self._tool_button_flip_horizontally_and_vertically.setFixedHeight(h)

    def event(self, e):
        if e.type() == QEvent.PaletteChange:
            self.spinBox.refreshStyle()
        elif e.type() == QEvent.StyleChange or e.type() == QEvent.FontChange:
            self.spinBox.refreshStyle()
            self._resizeWidgets()
        return super().event(e)

    def eventFilter(self, o, e):
        w = o
        if (w is not self.angleGauge or not w.isEnabled() or not e or
                e.type() != QEvent.ContextMenu):
            return False
        cme = QContextMenuEvent(e)
        self._tool_button_flip_options.menu().exec_(cme.globalPos())
        return True

    def _updateFlipButtonsVisibility(self):
        use_buttons = self._flip_options_mode == KisAngleSelector.FlipOptionsMode.Buttons
        self._tool_button_flip_horizontally.setVisible(use_buttons)
        self._tool_button_flip_vertically.setVisible(use_buttons)
        self._tool_button_flip_horizontally_and_vertically.setVisible(use_buttons)
        show_menus = self._flip_options_mode != KisAngleSelector.FlipOptionsMode.NoFlipOptions
        self._tool_button_flip_options.setVisible(show_menus)

