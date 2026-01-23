from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.api_krita import KritaAPI
from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.alib_vaporjem.extensions.krita_extensions import KritaExtensions
from jemlib.api_touchify.env import *
from touchify.src.settings.TouchifySettings import *

from enum import Enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..PluginWindow import TouchifyWindow

from krita import *
    
class ShortcutsManager(object):

    class TransformSelectionAction(Enum):
        Free_FlipX = 0
        Free_FlipY = 1
        Free_RotateCW = 2
        Free_RotateCCW = 3
        Apply = 4
        Reset = 5

    def __init__(self, instance: "TouchifyWindow"):
        self.appEngine = instance

    #region Signals

    def Window_Load(self):
        self.qWin = self.appEngine.api_window.qwindow

        self._hiddenDockers: dict[Qt.DockWidgetArea, list[str]] = {}

        self._hiddenDockers[1] = TouchifySettings.preferences().dockers.hidden_dockers_left.split(",")
        self._hiddenDockers[2] = TouchifySettings.preferences().dockers.hidden_dockers_right.split(",")
        self._hiddenDockers[4] = TouchifySettings.preferences().dockers.hidden_dockers_up.split(",")
        self._hiddenDockers[8] = TouchifySettings.preferences().dockers.hidden_dockers_down.split(",")

    #endregion

    #region Getters

    def getTransformToolActionSource(self, action: TransformSelectionAction):
        transform_tool_options = self.qWin.findChild(QWidget, "KisToolTransform option widget")
        if not transform_tool_options: return None

        actions_group = transform_tool_options.findChild(QGroupBox, "quickTransformGroup")
        if not actions_group: return None
        
        match action:
            case ShortcutsManager.TransformSelectionAction.Free_FlipX:
                buttonName = "flipXButton"
                item_type = "free"
            case ShortcutsManager.TransformSelectionAction.Free_FlipY:
                buttonName = "flipYButton"
                item_type = "free"
            case ShortcutsManager.TransformSelectionAction.Free_RotateCW:
                buttonName = "rotateCWButton"
                item_type = "free"
            case ShortcutsManager.TransformSelectionAction.Free_RotateCCW:
                buttonName = "rotateCCWButton"
                item_type = "free"
            case ShortcutsManager.TransformSelectionAction.Apply:
                buttonName = "apply"
                item_type = "button_box"
            case ShortcutsManager.TransformSelectionAction.Reset:
                buttonName = "reset"
                item_type = "button_box"
            case _:
                buttonName = None
                item_type = None

        if buttonName == None: return None
        if item_type == None: return None

        if item_type == "free":
            actions_group = transform_tool_options.findChild(QGroupBox, "quickTransformGroup")
            if not actions_group: return None

            action_button = actions_group.findChild(QToolButton, buttonName)
            if not action_button: return None

            return action_button
        elif item_type == "button_box":
            button_box = transform_tool_options.findChild(QDialogButtonBox, "buttonBox")
            if not button_box: return None

            if len(button_box.buttons()) != 2: return None

            match buttonName:
                case "apply":
                    index = 1
                case "reset":
                    index = 0
                case _:
                    index = None

            if index == None: return None

            button = button_box.buttons()[index]
            if not button: return None

            return button

    def getCropToolActionSource(self, action: str):
        crop_tool_options = self.qWin.findChild(QWidget, "KisToolCrop option widget")
        if not crop_tool_options: return None

        match action:
            case "center":
                item_type = "checkbox"
                item_name = "boolCenter"
            case "grow":
                item_type = "checkbox"
                item_name = "boolGrow"
            case "lock_width":
                item_type = "button"
                item_name = "lockWidthButton"
            case "lock_height":
                item_type = "button"
                item_name = "lockHeightButton"
            case "lock_ratio":
                item_type = "button"
                item_name = "lockRatioButton"
            case _:
                item_type = None
                item_name = None

        if item_type == None: return None
        if item_name == None: return None

        if item_type == "checkbox":
            checkbox = crop_tool_options.findChild(QCheckBox, item_name)
            if not checkbox: return None
            return checkbox
        elif item_type == "button":
            button = crop_tool_options.findChild(QPushButton, item_name)
            if not button: return None
            return button
        else:
            return None

    #endregion

    #region Update Functions

    #region Actions

    def triggerCropToolAction(self, selector: str):
        source = self.getCropToolActionSource(selector)
        if not source: return
        source.click()

    def triggerTransformToolAction(self, action: TransformSelectionAction):
        source = self.getTransformToolActionSource(action)
        if not source: return
        source.click()

    def showPopupPalette(self):
        pobj = self.appEngine.api_window.active_qview
        if not pobj: return

        mobj = next((w for w in pobj.findChildren(QWidget) if w.metaObject().className() == 'KisPopupPalette'), None)
        if not mobj: return

        if not mobj.isVisible():
            parentWidget = mobj.parentWidget()
            center_x = int(parentWidget.width() / 2) - int(mobj.width() / 2)
            center_y = int(parentWidget.height() / 2) - int(mobj.height() / 2)
            mobj.move(center_x, center_y)
            mobj.show()
        else:
            mobj.hide()

    def showMenubarPopup(self):
        def iterateActions(destination: QMenu, menu: QMenu | QMenuBar):
            for action in menu.actions():
                if action.menu():
                    sourceMenu = action.menu()
                    subMenu = QMenu(destination)
                    subMenu.setTitle(sourceMenu.title())
                    iterateActions(subMenu, sourceMenu)
                    destination.addMenu(subMenu)
                else:
                    destination.addAction(action)

        activeWindow = self.qWin
        popupMenu = QMenu(activeWindow)
        menuBar = activeWindow.menuBar()
        iterateActions(popupMenu, menuBar)
        popupMenu.exec(QCursor.pos())

    def toggleDirectionalDockers(self, area: int):
        dockers = self.appEngine.api_window.dockers
        mainWindow = self.qWin

        if len(self._hiddenDockers[area]) > 0: # show
            for dockerId in self._hiddenDockers[area]:
                docker = next((w for w in dockers if w.objectName() == dockerId), None)
                if docker:
                    docker.setVisible(True)
            self._hiddenDockers[area] = []
        else: # hide
            for docker in dockers:
                if docker.isHidden() or docker.isFloating():
                    continue

                if mainWindow.dockWidgetArea(docker) == area:
                    self._hiddenDockers[area].append(docker.objectName())
                    docker.setVisible(False)

        match area:
            case 1:
                TouchifySettings.preferences().dockers.hidden_dockers_left = ",".join(self._hiddenDockers[area])
            case 2:
                TouchifySettings.preferences().dockers.hidden_dockers_right = ",".join(self._hiddenDockers[area])
            case 4:
                TouchifySettings.preferences().dockers.hidden_dockers_up = ",".join(self._hiddenDockers[area])
            case 8:
                TouchifySettings.preferences().dockers.hidden_dockers_down = ",".join(self._hiddenDockers[area])
        TouchifySettings.preferences().save()

    #endregion

    #region Action Registration

    def Actions_Post(self):
        settings_menu = self.qWin.findChild(QMenu, 'settings')

        configureAction = KritaExtensions.moveActionTo(TouchifyEnv.ActionID.CONFIGURE, settings_menu, settings_menu, 'options_configure')
        configureAction.setIcon(KritaAPI.get_icon("configure"))

        popupPaletteAction = KritaExtensions.moveActionTo(TouchifyEnv.ActionID.Other.SHOWPOPUPPALETTE, settings_menu, settings_menu, 'toolbars_submenu_action')
        popupMenuAction = KritaExtensions.moveActionTo(TouchifyEnv.ActionID.Other.SHOWMENUBARPOPUP, settings_menu, settings_menu, 'toolbars_submenu_action')
        settings_menu.insertSeparator(popupMenuAction)

        KritaExtensions.moveActionTo(TouchifyEnv.ActionID.DockerUtils.MENU, settings_menu, settings_menu, 'view_toggledockers')

    def Actions_Init(self, window: WindowAPI, subItemPath: str, settingsItemPath: str):

        # Show Popup Palette
        popupPaletteToggle = window.create_action(TouchifyEnv.ActionID.Other.SHOWPOPUPPALETTE, "Show Popup Palette", settingsItemPath)
        popupPaletteToggle.setCheckable(False)
        popupPaletteToggle.triggered.connect(self.showPopupPalette)

        # Show Popup Menu
        popupMenuToggle = window.create_action(TouchifyEnv.ActionID.Other.SHOWMENUBARPOPUP, "Show Popup Menu", settingsItemPath)
        popupMenuToggle.setCheckable(False)
        popupMenuToggle.triggered.connect(self.showMenubarPopup)

        # region Toggle Dockers
        docker_utils_path = "{0}/{1}".format(settingsItemPath, TouchifyEnv.ActionID.DockerUtils.MENU)
        self.docker_utils_menu = QtWidgets.QMenu("Docker Utils", window.qwindow)
        self.docker_utils_action = window.create_action(TouchifyEnv.ActionID.DockerUtils.MENU, "Toggle Dockers...", settingsItemPath)
        self.docker_utils_action.setMenu(self.docker_utils_menu)

        toggleDockersLeft = window.create_action(TouchifyEnv.ActionID.DockerUtils.TOGGLELEFT, "Toggle Left Dockers", docker_utils_path)
        toggleDockersLeft.triggered.connect(lambda: self.toggleDirectionalDockers(1))
        self.docker_utils_menu.addAction(toggleDockersLeft)

        toggleDockersRight = window.create_action(TouchifyEnv.ActionID.DockerUtils.TOGGLERIGHT, "Toggle Right Dockers", docker_utils_path)
        toggleDockersRight.triggered.connect(lambda: self.toggleDirectionalDockers(2))
        self.docker_utils_menu.addAction(toggleDockersRight)

        toggleDockersTop = window.create_action(TouchifyEnv.ActionID.DockerUtils.TOGGLEUP, "Toggle Top Dockers", docker_utils_path)
        toggleDockersTop.triggered.connect(lambda: self.toggleDirectionalDockers(4))
        self.docker_utils_menu.addAction(toggleDockersTop)

        toggleDockersBottom = window.create_action(TouchifyEnv.ActionID.DockerUtils.TOGGLEDOWN, "Toggle Bottom Dockers", docker_utils_path)
        toggleDockersBottom.triggered.connect(lambda: self.toggleDirectionalDockers(8))
        self.docker_utils_menu.addAction(toggleDockersBottom)
        #endregion

        # region Transform Tool Selection Actions
        transform_selection_utils_path = "{0}/{1}".format(subItemPath, TouchifyEnv.ActionID.TransformTool.MENU)
        self.transform_selection_menu = QtWidgets.QMenu("Transform Tool Actions", window.qwindow)
        self.transform_selection_action = window.create_action(TouchifyEnv.ActionID.TransformTool.MENU, "Transform Tool Actions", subItemPath)
        self.transform_selection_action.setMenu(self.transform_selection_menu)

        transform_selection_flip_x = window.create_action(TouchifyEnv.ActionID.TransformTool.FREE_FLIPX, "Mirror Horizontal", transform_selection_utils_path)
        transform_selection_flip_x.triggered.connect(lambda: self.triggerTransformToolAction(ShortcutsManager.TransformSelectionAction.Free_FlipX))
        self.transform_selection_menu.addAction(transform_selection_flip_x)

        transform_selection_flip_y = window.create_action(TouchifyEnv.ActionID.TransformTool.FREE_FLIPY, "Mirror Vertical", transform_selection_utils_path)
        transform_selection_flip_y.triggered.connect(lambda: self.triggerTransformToolAction(ShortcutsManager.TransformSelectionAction.Free_FlipY))
        self.transform_selection_menu.addAction(transform_selection_flip_y)

        transform_selection_rotate_cw = window.create_action(TouchifyEnv.ActionID.TransformTool.FREE_ROTATECW, "Rotate 90 degrees Clockwise", transform_selection_utils_path)
        transform_selection_rotate_cw.triggered.connect(lambda: self.triggerTransformToolAction(ShortcutsManager.TransformSelectionAction.Free_RotateCW))
        self.transform_selection_menu.addAction(transform_selection_rotate_cw)

        transform_selection_rotate_ccw = window.create_action(TouchifyEnv.ActionID.TransformTool.FREE_ROTATECCW, "Rotate 90 degrees CounterClockwise", transform_selection_utils_path)
        transform_selection_rotate_ccw.triggered.connect(lambda: self.triggerTransformToolAction(ShortcutsManager.TransformSelectionAction.Free_RotateCCW))
        self.transform_selection_menu.addAction(transform_selection_rotate_ccw)

        self.transform_selection_menu.addSeparator()

        transform_selection_apply = window.create_action(TouchifyEnv.ActionID.TransformTool.APPLY, "Apply", transform_selection_utils_path)
        transform_selection_apply.triggered.connect(lambda: self.triggerTransformToolAction(ShortcutsManager.TransformSelectionAction.Apply))
        self.transform_selection_menu.addAction(transform_selection_apply)

        transform_selection_reset = window.create_action(TouchifyEnv.ActionID.TransformTool.RESET, "Reset", transform_selection_utils_path)
        transform_selection_reset.triggered.connect(lambda: self.triggerTransformToolAction(ShortcutsManager.TransformSelectionAction.Reset))
        self.transform_selection_menu.addAction(transform_selection_reset)
        #endregion

        # region Crop Tool Actions
        crop_tool_actions_path = "{0}/{1}".format(subItemPath, TouchifyEnv.ActionID.CropTools.MENU)
        self.crop_tool_actions_menu = QtWidgets.QMenu("Crop Tool Actions", window.qwindow)
        self.crop_tool_actions_menu_action = window.create_action(TouchifyEnv.ActionID.CropTools.MENU, "Crop Tool Actions", subItemPath)
        self.crop_tool_actions_menu_action.setMenu(self.crop_tool_actions_menu)

        self.crop_tools_actions_center = window.create_action(TouchifyEnv.ActionID.CropTools.CENTER, "Center", crop_tool_actions_path)
        self.crop_tools_actions_center.triggered.connect(lambda: self.triggerCropToolAction("center"))
        self.crop_tool_actions_menu.addAction(self.crop_tools_actions_center)

        self.crop_tools_actions_grow = window.create_action(TouchifyEnv.ActionID.CropTools.GROW, "Grow", crop_tool_actions_path)
        self.crop_tools_actions_grow.triggered.connect(lambda: self.triggerCropToolAction("grow"))
        self.crop_tool_actions_menu.addAction(self.crop_tools_actions_grow)

        self.crop_tool_actions_menu.addSeparator()

        self.crop_tools_actions_lock_width = window.create_action(TouchifyEnv.ActionID.CropTools.LOCKWIDTH, "Lock Width", crop_tool_actions_path)
        self.crop_tools_actions_lock_width.triggered.connect(lambda: self.triggerCropToolAction("lock_width"))
        self.crop_tool_actions_menu.addAction(self.crop_tools_actions_lock_width)

        self.crop_tools_actions_lock_height = window.create_action(TouchifyEnv.ActionID.CropTools.LOCKHEIGHT, "Lock Height", crop_tool_actions_path)
        self.crop_tools_actions_lock_height.triggered.connect(lambda: self.triggerCropToolAction("lock_height"))
        self.crop_tool_actions_menu.addAction(self.crop_tools_actions_lock_height)

        self.crop_tools_actions_lock_ratio = window.create_action(TouchifyEnv.ActionID.CropTools.LOCKRATIO, "Lock Ratio", crop_tool_actions_path)
        self.crop_tools_actions_lock_ratio.triggered.connect(lambda: self.triggerCropToolAction("lock_ratio"))
        self.crop_tool_actions_menu.addAction(self.crop_tools_actions_lock_ratio)
        #endregion

    #endregion
        

        
