from krita import *
from ...extensions.calculations import *
from ...DockerToolbar import DockerToolbar

# Variables
EO_ENCODING = "utf-8"

BASE_NORMAL_ICON = Krita.instance().icon("select")
BASE_SELECT_ICON = Krita.instance().icon("tool_rect_selection")
BASE_MOVE_ICON = Krita.instance().icon("krita_tool_move")
BASE_CAMERA_PAN_ICON = Krita.instance().icon("tool_pan")
BASE_CAMERA_ZOOM_ICON = Krita.instance().icon("tool_zoom")
BASE_ICON_SIZE = QSize(14,14) 


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ReferenceSection import ReferenceSection

class ReferenceToolbar(DockerToolbar):

    def __init__(self, parent: "ReferenceSection"):
        super().__init__(parent, Qt.Orientation.Horizontal)
        self.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setFixedHeight(25)
        self.Section: "ReferenceSection" = parent
        self.Components()
        self.Connections()

    def Components( self ):
        self.base_modeset_button = QPushButton(self)
        self.base_modeset_button.setFixedHeight(25)
        self.base_modeset_button.setFixedWidth(45)
        self.base_modeset_button.setIcon(BASE_NORMAL_ICON)
        self.base_modeset_button.setIconSize(BASE_ICON_SIZE)
        self.mode_menu = QMenu(self.base_modeset_button)
        self.mode_normal_action = self.mode_menu.addAction(BASE_NORMAL_ICON, "Normal")
        self.mode_normal_action.setIconVisibleInMenu(True)
        self.mode_select_action = self.mode_menu.addAction(BASE_SELECT_ICON, "Select")
        self.mode_select_action.setIconVisibleInMenu(True)
        self.mode_selectmove_action = self.mode_menu.addAction(BASE_MOVE_ICON, "Move")
        self.mode_selectmove_action.setIconVisibleInMenu(True)
        self.mode_move_action = self.mode_menu.addAction(BASE_CAMERA_PAN_ICON, "Pan")
        self.mode_move_action.setIconVisibleInMenu(True)
        self.mode_zoom_action = self.mode_menu.addAction(BASE_CAMERA_ZOOM_ICON, "Zoom")
        self.mode_zoom_action.setIconVisibleInMenu(True)
        self.base_modeset_button.setMenu(self.mode_menu)
        self.addWidget(self.base_modeset_button)

        self.label_editor_button = QtWidgets.QToolButton(self)
        self.label_editor_button.setCheckable(True)
        self.label_editor_button.setChecked(False)
        self.label_editor_button.setIcon(Krita.instance().icon("draw-text"))
        self.addWidget(self.label_editor_button)

        self.color_picker_button = QtWidgets.QToolButton(self)
        self.color_picker_button.setCheckable(True)
        self.color_picker_button.setChecked(False)
        self.color_picker_button.setIcon(Krita.instance().icon("krita_tool_color_sampler"))
        self.addWidget(self.color_picker_button)

        self.snap_button = QtWidgets.QToolButton(self)
        self.snap_button.setCheckable(True)
        self.snap_button.setChecked(False)
        self.snap_button.setIcon(Krita.instance().icon("chain-broken-icon"))
        self.addWidget(self.snap_button)

        self.lock_button = QtWidgets.QToolButton(self)
        self.lock_button.setCheckable(True)
        self.lock_button.setChecked(False)
        self.lock_button.setIcon(Krita.instance().icon("unlocked"))
        self.addWidget(self.lock_button)
    
    def Connections( self ):
        self.color_picker_button.clicked.connect(self.Action_ColorPickerToggled)
        self.label_editor_button.clicked.connect(self.Action_LabelEditorToggled)
        self.snap_button.clicked.connect(self.Action_SnapToggle)
        self.lock_button.clicked.connect(self.Action_LockToggled)

        self.base_modeset_button.clicked.connect(self.base_modeset_button.showMenu)
        self.mode_normal_action.triggered.connect(self.Action_Base_NormalToggled)
        self.mode_select_action.triggered.connect(self.Action_Base_SelectionToggled)
        self.mode_selectmove_action.triggered.connect(self.Action_Base_SelectionMoveToggled)
        self.mode_move_action.triggered.connect(self.Action_Base_MoveToggled)
        self.mode_zoom_action.triggered.connect(self.Action_Base_ZoomToggled)
        self.Board().SIGNAL_ACTIONS_UPDATED.connect(self.OnEvent_ActionsUpdated)

    def Board(self):
        return self.Section.view

    def Action_LabelEditorToggled(self):
        self.Board().ModeSet_Label()

    def Action_ColorPickerToggled(self):
        self.Board().ModeSet_ColorPicker()

    def Action_SnapToggle(self):
        self.Board().ModeSet_Snap()

    def Action_Base_NormalToggled(self):
        self.Board().ModeSet_Base_Reset()

    def Action_Base_SelectionToggled(self):
        self.Board().ModeSet_Base_Selection(True)

    def Action_Base_SelectionMoveToggled(self):
        self.Board().ModeSet_Base_SelectionMove(True)
        
    def Action_Base_MoveToggled(self):
        self.Board().ModeSet_Base_CameraMove(True)

    def Action_Base_ZoomToggled(self):
        self.Board().ModeSet_Base_CameraScale(True)

    def Action_LockToggled(self):
        self.Board().ModeSet_Lock()

    def OnEvent_ActionsUpdated(self):
        self.snap_button.setChecked(self.Board().state_snap)
        if self.Board().state_snap: self.snap_button.setIcon(Krita.instance().icon("chain-icon"))
        else: self.snap_button.setIcon(Krita.instance().icon("chain-broken-icon"))

        self.lock_button.setChecked(self.Board().mode_lock)
        if self.Board().mode_lock: self.lock_button.setIcon(Krita.instance().icon("locked"))
        else: self.lock_button.setIcon(Krita.instance().icon("unlocked"))

        self.color_picker_button.setChecked(self.Board().mode_pickcolor)
        self.label_editor_button.setChecked(self.Board().mode_label)

        if self.Board().mode_base_cameramove:
            self.base_modeset_button.setIcon(BASE_CAMERA_PAN_ICON)
            self.base_modeset_button.setIconSize(BASE_ICON_SIZE)
        elif self.Board().mode_base_selectionmove:
            self.base_modeset_button.setIcon(BASE_MOVE_ICON)
            self.base_modeset_button.setIconSize(BASE_ICON_SIZE)
        elif self.Board().mode_base_camerascale:
            self.base_modeset_button.setIcon(BASE_CAMERA_ZOOM_ICON)
            self.base_modeset_button.setIconSize(BASE_ICON_SIZE)
        elif self.Board().mode_base_selection:
            self.base_modeset_button.setIcon(BASE_SELECT_ICON)
            self.base_modeset_button.setIconSize(BASE_ICON_SIZE)
        else:
            self.base_modeset_button.setIcon(BASE_NORMAL_ICON)
            self.base_modeset_button.setIconSize(BASE_ICON_SIZE)