from typing import TYPE_CHECKING
from jemlib.api_krita.wrappers.window import WindowAPI
from krita import *

from touchify.src.settings.TouchifySettings import TouchifySettings
from PyQt5.QtWidgets import *
if TYPE_CHECKING:
    from touchify.src.PluginManagers import TouchifyManagers


class BrushEditorTweak(QObject):

    def __init__(self, window: WindowAPI, managers: "TouchifyManagers"):
        super().__init__(window.qwindow)
        self.qWin = window.qwindow
        self.notifier = window.notifier
        self.managers = managers
        self._blockSignals = False

    def eventFilter(self, a0: QObject, a1: QEvent):
        if TouchifySettings.preferences().Styles_DockedBrushEditor:
            if a1.type() == QEvent.Type.Resize or a1.type() == QEvent.Type.Move:
                if not self._blockSignals: self.update()
        return super().eventFilter(a0, a1)

    def installTweak(self):
        container = self.qWin.findChild(QWidget, "KisPaintOpPresetsEditor")
        if not container: return None
        if not container.isVisible(): return None

        editor = container.parentWidget()
        if not editor: return

        if not editor.property("eventFilterInstalled"):
            editor.setProperty("eventFilterInstalled", True)
            editor.installEventFilter(self)
            self.update()

    def update(self):
        if not TouchifySettings.preferences().Styles_DockedBrushEditor: return

        container = self.qWin.findChild(QWidget, "KisPaintOpPresetsEditor")
        if not container: return None
        if not container.isVisible(): return None

        editor = container.parentWidget()
        if not editor: return

        canvas = self.managers.mgr_canvas.active_canvas
        self._blockSignals = True
        editor.move(canvas.mapToGlobal(QPoint(0,0)))
        editor.resize(canvas.size())
        if editor.size() != canvas.size():
            editor_bounds = QRect(canvas.pos(), editor.size())
            editor_bounds.moveCenter(canvas.mapToGlobal(canvas.rect().center()))
            editor.move(editor_bounds.topLeft())
        self._blockSignals = False

    def refresh(self):

        is_docked = TouchifySettings.preferences().Styles_DockedBrushEditor
        if is_docked: self.installTweak()

        fix_zoom = TouchifySettings.preferences().Styles_BrushEditorZoomFix
        if fix_zoom:
            canvas = self.notifier.getCurrentCanvas()
            if canvas: canvas.resetZoom()

