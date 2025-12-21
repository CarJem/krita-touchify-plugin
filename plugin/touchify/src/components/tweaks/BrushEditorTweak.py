from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.managers.IconRepository import IconRepository
from krita import *
from touchify.src.settings.TouchifySettings import TouchifySettings
from PyQt5.QtWidgets import *


class BrushEditorTweak(QObject):

    def __init__(self, window: WindowAPI):
        self.qWin = window.qwindow
        self.notifier = window.notifier

        self.stack_docker: BrushEditorTweakContainer | None = None
        self.stack_index: int | None = None

    def Get_DockArea(self) -> QStackedWidget | None:
        mdi_area: QMdiArea = self.qWin.findChild(QMdiArea)
        if not mdi_area: return None

        stack_area: QStackedWidget = mdi_area.parentWidget()
        if not stack_area: return None
        if not isinstance(stack_area, QStackedWidget): return None

        return stack_area

    def Get_Editor(self):
        container = self.qWin.findChild(QWidget, "KisPaintOpPresetsEditor")
        if not container: return None
        if not container.isVisible(): return None

        editor = container.parentWidget()
        if not editor: return None

        return editor

    def Subwindow_Spawn(self):
        if self.stack_docker: return

        docking_area = self.Get_DockArea()
        if not docking_area: return None

        editor = self.Get_Editor()
        if not editor: return

        self.stack_docker = BrushEditorTweakContainer(docking_area, self, editor)
        stack_index = docking_area.addWidget(self.stack_docker)
        docking_area.setCurrentIndex(stack_index)

    def Subwindow_Kill(self):
        if self.stack_docker == None: return
        self.stack_docker.OnEvent_Close()

    def Update_State(self):
        is_docked = TouchifySettings.preferences().Styles_DockedBrushEditor
        fix_zoom = TouchifySettings.preferences().Styles_BrushEditorZoomFix

        if is_docked: self.Subwindow_Spawn()
        else: self.Subwindow_Kill()

        if fix_zoom:
            canvas = self.notifier.getCurrentCanvas()
            if canvas: canvas.resetZoom()

class BrushEditorTweakContainer(QWidget):
    def __init__(self, parent: QStackedWidget, tweak: "BrushEditorTweak", editor: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setContentsMargins(0,0,0,0)

        self.Stack = parent
        self.Tweak = tweak

        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0,0,0,0)
        self.lay.setSpacing(0)
        self.setLayout(self.lay)

        self.close_action = QAction(self)
        self.close_action.setIcon(IconRepository.kritaIcon("window-close"))
        self.close_action.setText("Close")
        self.close_action.setToolTip("Close")
        self.close_action.triggered.connect(self.OnEvent_Close)

        self.toolbar = QToolBar(self)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.toolbar.addAction(self.close_action)
        self.lay.addWidget(self.toolbar)

        self.OnEvent_Show(editor)

    def OnEvent_Close(self):
        self.editor.setParent(self.__widget_last_parent)
        self.editor.setWindowFlags(self.__widget_last_winflags)

        self.Stack.removeWidget(self)
        self.Tweak.stack_docker = None
        self.close()

    def OnEvent_Show(self, editor: QWidget):
        self.editor = editor
        self.__widget_last_parent = editor.parent()
        self.__widget_last_winflags = editor.windowFlags()
        self.lay.addWidget(editor)