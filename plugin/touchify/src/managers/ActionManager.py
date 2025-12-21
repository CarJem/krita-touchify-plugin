from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from jemlib.api_krita import KritaAPI

from touchify.__env__ import REGISTERED_ACTIONS_FILE
from touchify.src.config.menu.TriggerMenuItem import TriggerMenuItem
from touchify.src.config.pie_wheel.PieWheelData import PieWheelData
from touchify.src.config.resource_pack.ResourcePack import ResourcePack
from touchify.src.config.resource_pack.ResourcePackMetadata import ResourcePackMetadata
from touchify.src.config.canvas_preset.CanvasPreset import CanvasPreset
from touchify.src.config.docker_group.DockerGroup import DockerGroup
from touchify.src.config.menu.TriggerMenu import TriggerMenu
from touchify.src.config.script.CustomScript import CustomScript

import jemlib.alib_vaporjem.extensions.pyqt_extensions as PyQtExtensions
from touchify.src.components.widgets.triggers.TriggerMenu import TriggerMenuWidget

from touchify.src.components.widgets.triggers.TriggerButton import TriggerButton

from jemlib.managers.GlobalEvents import GlobalEvents
from jemlib.api_touchify.env import *

from functools import partial

from touchify.src.config.triggers.Trigger import Trigger
from touchify.src.config.popup.PopupData import PopupData
from jemlib.alib_vaporjem.extensions.krita_extensions import *

from touchify.src.settings.TouchifySettings import TouchifySettings
from jemlib.managers.IconRepository import IconRepository

from touchify.src.components.popup.PopupWidget import PopupWidget

from jemlib.alib_kis.KritaActions import KritaActions

import xml.etree.ElementTree as ET
from xml.dom import minidom as MiniDOM



if TYPE_CHECKING:
    from ..PluginManagers import TouchifyManagers

ENABLE_DEBUG=False

def printDebug(value: str):
    if ENABLE_DEBUG: print("[ActionManager] :: ", value)

class ActionManager(QObject):
    composerTriggerEnded=pyqtSignal()
    selectedToolChanged=pyqtSignal(str)
    
    def __init__(self, parent: QObject, managers: "TouchifyManagers"):
        super().__init__(parent)
        self.managers = managers
        self.api_window: WindowAPI | None = None

        self.Variables()
        self.Connections()

    #region Init Functions

    def Variables(self):
        self.__lastToolboxTool = ""
        self.__lastBrushPreset = None
        self.custom_docker_states = {}
        self.registeredActions = {}
        self.registeredActionsData = {}
        self.active_popups: dict[str, PopupWidget] = {}
        self.composer_action_down: bool = False
        self.composer_action_down_start: QDateTime = QDateTime.currentDateTime()
        self.pie_wheel_api: Extension = None


    def Connections(self):
        GlobalEvents().SIGNAL_MOUSE_RELEASED.connect(self.OnEvent_GlobalMouseRelease)
        GlobalEvents().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.OnEvent_ConfigUpdated)
        GlobalEvents().SIGNAL_PIE_TRIGGER_SENT.connect(self.OnEvent_PieTrigger)

    #endregion

    #region Window Functions

    def Window_Load(self, app_window: WindowAPI):
        self.api_window = app_window
        self.notifier = self.api_window.notifier

        self.__lastToolboxTool = self.notifier.getCurrentTool()
        self.__lastBrushPreset = self.notifier.getCurrentBrush()
        self.notifier.toolChanged.connect(self.Notifier_ToolChanged)
        self.notifier.brushChanged.connect(self.Notifier_BrushChanged)

    def Notifier_ToolChanged(self, tool: str):
        printDebug("tool changed")
        self.__lastToolboxTool = tool

    def Notifier_BrushChanged(self, resource: Resource):
        printDebug("brush changed")
        self.__lastBrushPreset = resource

    #endregion

    #region Create Functions

    def Create_RegistryAction(self, actionIdentifier: str, data: Trigger, window: WindowAPI, actionPath: str):
        displayName = data.display_custom_text
        action = window.create_action(actionIdentifier, displayName, actionPath)

        self.registeredActions[actionIdentifier] = action
        self.registeredActionsData[actionIdentifier] = data  
        action.triggered.connect(partial(self.Execute_RegistryAction, actionIdentifier, action))
             
        (has_text, text, has_icon, icon, using_action_icon) = self.Helper_GetTriggerDisplay(data)
        if has_icon: action.setIcon(icon)
        return action   
    
    def Create_Button(self, parent: QWidget, data: Trigger, classType: type = TriggerButton):
        if data.variant == Trigger.Variants.Action:
            if data.action_id and data.action_id in self.registeredActions:
                data = self.registeredActionsData[data.action_id]

        match data.variant:
            case Trigger.Variants.Brush:
                result = self.Button_Brush(data, classType=classType)
            case Trigger.Variants.Menu:
                result = self.Button_Menu(data, classType=classType)
            case Trigger.Variants.Popup:
                result = self.Button_Popup(data, classType=classType)
            case Trigger.Variants.Action:
                result = self.Button_Trigger(data, classType=classType)
            case _:
                result = self.Button_Generic(data, classType=classType)

        if result and result != None:
            if data.extra_closes_popup == True:
                result.triggerActivated.connect(lambda: self.ButtonEvent_ClosePopup(result))
            result.setParent(parent)

        return result
    
    def Create_MenuItem(self, parent: TriggerMenuWidget, data: TriggerMenuItem):
        if data.variant == TriggerMenuItem.Variants.Action:
            if data.action_id and data.action_id in self.registeredActions:
                data = self.registeredActionsData[data.action_id]

        match data.variant:
            case TriggerMenuItem.Variants.Menu:
                actual_menu = TriggerMenuWidget(data, parent, self)
                actual_menu.setTitle(data.display_custom_text)
                parent.addMenu(actual_menu)
            case TriggerMenuItem.Variants.Action:
                if data.action_id in KritaActions.EXPANDING_SPACERS:
                    actual_action = QAction(parent)
                    actual_action.setSeparator(True)
                else:
                    actual_action = KritaAPI.get_action(data.action_id)
                if actual_action: parent.addAction(actual_action)
            case TriggerMenuItem.Variants.Seperator:
                actual_action = QAction(parent)
                actual_action.setText(data.display_custom_text)
                actual_action.setSeparator(True)
                if actual_action: parent.addAction(actual_action)                
            case _:
                actual_action = QAction(parent)
                actual_action.setText(data.display_custom_text)
                actual_action.triggered.connect(lambda: self.Actions_Run(data, actual_action))
                if actual_action: parent.addAction(actual_action)

    def Create_Popup(self, id: str, _parent: QWidget = None):

        if id == TouchifyEnv.InternalPopups.BRUSH_PICKER:
            data: PopupData = PopupData()
            data.type = "docker"
            data.window_type = "popup"
            data.docker_id = "PresetDocker"
            data.popup_width = 300
            data.popup_height = 500
        elif id == TouchifyEnv.InternalPopups.PATTERN_CHOOSER or id == TouchifyEnv.InternalPopups.GRADIENT_CHOOSER:    
            main_window = self.api_window.qwindow
            frames = main_window.findChildren(QFrame,'KisPopupButtonFrame')
            for frame in frames:
                result = frame.findChild(QWidget, id)
                if result: 
                    frame.show()
                    if _parent: position = PyQtExtensions.GeometryHelpers.clampToTarget(
                        _parent.mapToGlobal(QPoint(0,0)), frame.size(), main_window, QPoint(0, _parent.height()))
                    else: position = QCursor.pos()
                    frame.move(position.x(), position.y())
                    break
            return
        else:
            data: PopupData = TouchifySettings.registryItem(id, PopupData)
            if not isinstance(data, PopupData) or data == None: return


        is_dead = True
        popup_id = str(data.id)
        if popup_id in self.active_popups:
            is_dead = False
            popup = self.active_popups[popup_id]
            try: 
                popup.isVisible()
            except:
                is_dead = True

        if is_dead:
            if popup_id in self.active_popups: 
                del self.active_popups[popup_id]

            print("attempting to build")
            popup = PopupWidget(self.api_window.qwindow.window(), id, data, self.managers)
            if popup == None: 
                print("failed to build")
                return
            
            self.active_popups[popup_id] = popup

        popup.openPopup(_parent)

    #endregion

    #region Registered Action Functions

    def Actions_Post(self, menu: QMenu):
        menu.addMenu(self.__registry_menu)

    def Actions_Init(self, window: WindowAPI, subItemPath: str):
        self.__registry_menu = QtWidgets.QMenu(TouchifyEnv.Title.REGISTERED_ACTIONS, window.qwindow)
        root_action = window.create_action(TouchifyEnv.ActionID.RegisteredActions.MENU, TouchifyEnv.Title.REGISTERED_ACTIONS, subItemPath)
        root_action.setMenu(self.__registry_menu)
        registryItemsPath = "{0}/{1}".format(subItemPath, TouchifyEnv.ActionID.RegisteredActions.MENU)

        registered_elements: dict[str, tuple[ResourcePackMetadata, list[ET.Element]]] = {}

        for pack in TouchifySettings.resourcePacks():
            pack: ResourcePack
            packMeta = pack.metadata
            pack_name = packMeta.registry_name
            pack_id = packMeta.registry_id

            pack_menu = QtWidgets.QMenu(pack_name, window.qwindow)
            pack_action = window.create_action(pack_id, pack_name, registryItemsPath)
            pack_action.setMenu(pack_menu)
            packItemsPath = "{0}/{1}".format(registryItemsPath, pack_id)

            registered_elements[packMeta.registry_id] = packMeta, []
            for data in pack.triggers:
                data: Trigger
                id = '{0}{1}_{2}'.format(TouchifyEnv.ActionID.RegisteredActions.PREFIX, packMeta.registry_id, data.registry_id)
                action = self.Create_RegistryAction(id, data, window, packItemsPath)
                registered_elements[packMeta.registry_id][1].append(self.Actions_Add(id))
                pack_menu.addAction(action)
            
        self.Actions_Write(registered_elements)

    def Actions_Run(self, data: Trigger, action: QAction):
        match data.variant:
            case Trigger.Variants.CanvasPreset:
                self.Execute_CanvasCfg(data.canvas_preset_data)
            case Trigger.Variants.Docker:
                self.Execute_Docker(data.docker_id)
            case Trigger.Variants.Workspace:
                self.Execute_Workspace(data.workspace_id)
            case Trigger.Variants.Popup:
                self.Execute_Popup(action, data.popup_data)
            case Trigger.Variants.Brush:
                self.Execute_Brush(data.brush_name)
            case Trigger.Variants.DockerGroup:
                self.Execute_DockerGroup(data.docker_group_data)
            case Trigger.Variants.Menu:
                self.Execute_Menu(action, data.context_menu_id)
            case Trigger.Variants.Action:
                self.Execute_Trigger(data)
            case Trigger.Variants.Script:
                self.Execute_Script(data.script_id)
            case Trigger.Variants.PieWheel:
                self.Execute_PieWheel(data.piewheel_id)

    def Actions_Add(self, actionname):
        element = ET.Element("Action",{"name":"{0}".format(actionname)})
        ET.SubElement(element,"text").text = actionname
        ET.SubElement(element,"shortcut").text = "none"
        return element
    
    def Actions_Write(self, registry: dict[str, tuple[ResourcePackMetadata, list[ET.Element]]]):
        tree = ET.ElementTree(ET.Element("ActionCollection",{"version":"2","name":"Touchify"}))
        action_collection = tree.getroot()


        for registry_name, registry_data in registry.items():
            registry_meta = registry_data[0]
            registry_actions = registry_data[1]

            pack_collection = ET.SubElement(action_collection, "Actions", {"category":"Touchify"})
            ET.SubElement(pack_collection, "text").text = "{0}".format(registry_meta.registry_name)

            for action in registry_actions:
                pack_collection.append(action)

        xmlstr = MiniDOM.parseString(ET.tostring(action_collection, encoding='UTF-8', xml_declaration=True, short_empty_elements=False)).toprettyxml(indent="   ")
        with open(REGISTERED_ACTIONS_FILE, "w") as f:
            f.write(xmlstr)

    #endregion

    #region Helper Functions

    def Helper_GetActionSource(self, action: QAction):
        _sender: QObject = action
        _parent: QWidget | None = None  
        
        if isinstance(_sender, QWidgetAction):
            _sender: QWidgetAction

            for widget in _sender.associatedWidgets():
                if isinstance(widget, QToolButton) or isinstance(widget, QPushButton):
                    if widget.underMouse():
                        _parent = widget
                        break
            return _parent
        else:
            return _sender
    
    def Helper_GetTriggerDisplay(self, data: Trigger):
        use_custom_icon: bool = data.display_custom_icon_enabled
        use_custom_text: bool = data.display_custom_text_enabled
        is_brush: bool = data.variant == Trigger.Variants.Brush
        is_action: bool = data.variant == Trigger.Variants.Action
        using_action_icon: bool = False

        if use_custom_icon:
            icon = IconRepository.iconLoader(data.display_custom_icon)
        else:
            if is_brush: icon = IconRepository.brushIcon(data.brush_name)
            elif is_action: 
                icon = IconRepository.actionIcon(data.action_id)
                using_action_icon = True
            else: icon = QIcon()

        if use_custom_text:
            text: str = data.display_custom_text  
        else:
            if is_brush: text = data.brush_name
            elif is_action: text = IconRepository.actionText(data.action_id)
            else: text = ""

        has_icon = not icon.isNull()
        has_text = text != ""

        if data.display_text_hide: has_text = False
        if data.display_icon_hide: has_icon = False

        return (has_text, text, has_icon, icon, using_action_icon)

    def Helper_SetButtonDisplay(self, act: Trigger, btn: TriggerButton):
        (has_text, text, has_icon, icon, using_action_icon) = self.Helper_GetTriggerDisplay(act)  
        if has_text: btn.setText(text)      
        if has_icon: btn.setIcon(icon) 
        if using_action_icon: btn.setupActionIcon()        
        btn.setMetadata(text, icon)

    #endregion    
    
    #region OnEvent Functions

    def OnEvent_ConfigUpdated(self):
        printDebug("config_updating")
        registered_ids: list[str] = []
        for data in self.registeredActions:
            registered_ids.append(data)

        for popup_id in self.active_popups:
            try:
                popup: PopupWidget = self.active_popups[popup_id]
                popup.dispose()
            except:
                pass
        self.active_popups.clear()

        for pack in TouchifySettings.resourcePacks():
            pack: ResourcePack
            meta: ResourcePackMetadata = pack.metadata
            for data in pack.triggers:
                data: Trigger
                subActionIdentifier = '{0}{1}_{2}'.format(TouchifyEnv.ActionID.RegisteredActions.PREFIX, meta.registry_id, data.registry_id)
                if subActionIdentifier in self.registeredActions:
                    self.registeredActionsData[subActionIdentifier] = data
        printDebug("config_updating_done")


    def OnEvent_GlobalMouseRelease(self):
        if self.composer_action_down and self.composer_action_down_start.addMSecs(250) < QDateTime.currentDateTime():
            QApplication.instance().sendEvent(KritaAPI.get_active_qwindow(), QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier))
            self.composerTriggerEnded.emit()
            try:
                self.composerTriggerEnded.disconnect()
            except:
                pass
            self.composer_action_down = False

    def OnEvent_PieTrigger(self, data: Trigger):
        self.Actions_Run(data, None)

    def OnEvent_ComposerStart(self):
        self.composer_action_down_start = QDateTime.currentDateTime()
        self.composer_action_down = True


    #endregion
        
    #region ButtonEvent Functions

    def ButtonEvent_ShortcutComposer(self, btn: TriggerButton, onClick: any):
        def tryFindParentPopup(source: QWidget):
            from touchify.src.components.popup.PopupWidget import PopupWidget
            try:
                widget = source.parent()
                while (widget):
                    foo = widget
                    if isinstance(foo, PopupWidget):
                        return foo
                    widget = widget.parent()
                return None
            except:
                return None
            
        parentPopup = tryFindParentPopup(btn)
        if parentPopup: 
            parentPopup._hasComposerWorkAround = True
            self.composerTriggerEnded.connect(parentPopup.onComposerTriggerEnded)

        onClick()
        self.OnEvent_ComposerStart()

    def ButtonEvent_ClosePopup(self, btn: TriggerButton):
        if btn:
            parent: QWidget | None = btn.parentWidget()
            while parent:
                if isinstance(parent, PopupWidget):
                    parent.closePopup()
                    return
                else:
                    parent = parent.parentWidget()
            return
                
    #endregion

    #region Button Constructors

    def Button_Core(self, onClick: any, toolTip: str, composerMode: bool = False, trigger_mode: TriggerButton.TriggerMode = TriggerButton.TriggerMode.OnClick, classType: type = TriggerButton):
        btn: TriggerButton = classType()
        
        if onClick:
            if composerMode: btn.setTrigger(lambda: self.ButtonEvent_ShortcutComposer(btn, onClick), TriggerButton.TriggerMode.OnRelease)
            else: btn.setTrigger(onClick, trigger_mode) # collect and disconnect all when closing
                
        btn.setToolTip(toolTip)
        btn.setContentsMargins(0,0,0,0)
        return btn
   
    def Button_Brush(self, act: Trigger, classType: type = TriggerButton):
        btn: TriggerButton | None = None
        id = act.brush_name
        brush_presets = IconRepository.brushPresets()
        
        if id in brush_presets:
            preset = brush_presets[id]
            btn = self.Button_Core(lambda: self.Execute_Brush(id), preset.name(), classType=classType)
            match_tool = self.__lastBrushPreset == preset
            btn.setupBrushChange(self.api_window, id, match_tool)
            self.Helper_SetButtonDisplay(act, btn)
        return btn
                   
    def Button_Menu(self, act: Trigger, classType: type = TriggerButton):
        data: TriggerMenu = TouchifySettings.registryItem(act.context_menu_id, TriggerMenu)
        if not isinstance(data, TriggerMenu) or data == None: return None
        
        btn: TriggerButton = self.Button_Core(None, act.display_custom_text, classType=classType)   
        self.Helper_SetButtonDisplay(act, btn)
        
        contextMenu = TriggerMenuWidget(data, btn, self)
        btn.setMenu(contextMenu)
        btn.triggerActivated.connect(btn.showMenu)
        return btn
    
    def Button_Popup(self, data: Trigger, classType: type = TriggerButton):
        btn: TriggerButton | None = None
        btn = self.Button_Core(None, data.display_custom_text, False, TriggerButton.TriggerMode.OnRelease, classType=classType)
        btn.triggerActivated.connect((lambda: self.Create_Popup(data.popup_data, btn)))
        self.Helper_SetButtonDisplay(data, btn)
        return btn

    def Button_Generic(self, data: Trigger, classType: type = TriggerButton):
        btn: TriggerButton | None = None
        
        onClick = None
        
        match data.variant:
            case Trigger.Variants.Docker:
                onClick = (lambda: self.Execute_Docker(data.docker_id))
            case Trigger.Variants.Workspace:
                onClick = (lambda: self.Execute_Workspace(data.workspace_id))
            case Trigger.Variants.DockerGroup:
                onClick = (lambda: self.Execute_DockerGroup(data.docker_group_data))
            case Trigger.Variants.CanvasPreset:
                onClick = (lambda: self.Execute_CanvasCfg(data.canvas_preset_data))
            case Trigger.Variants.Script:
                onClick = (lambda: self.Execute_Script(data.script_id))

        btn = self.Button_Core(onClick, data.display_custom_text, classType=classType)
        self.Helper_SetButtonDisplay(data, btn)
        return btn
        
    def Button_Trigger(self, act: Trigger, classType: type = TriggerButton):
        action = KritaAPI.get_action(act.action_id)
        btn: TriggerButton | None = None
        if action:
            checkable = action.isCheckable()
            toolbox_item = False
            
            if act.action_id in KritaActions.KNOWN_UNCHECKABLES:
                checkable = False
            
            if act.action_id in KritaActions.TOOLBOX_ITEMS:
                toolbox_item = True

            
            btn = self.Button_Core(action.trigger, action.toolTip(), act.extra_composer_mode, classType=classType)

            if toolbox_item: 
                match_tool = self.__lastToolboxTool == act.action_id
                btn.setupToolChange(self.api_window, act.action_id, match_tool)
            elif checkable: btn.setupActionCheckChange(action, act.action_id, action.isChecked())
            else: btn.setupAction(action, act.action_id)

            self.Helper_SetButtonDisplay(act, btn)
        return btn
    
    #endregion

    #region Execution Functions    

    def Execute_RegistryAction(self, identifier: str, action: QAction):
        if identifier in self.registeredActions:
            data: Trigger = self.registeredActionsData[identifier]
            if isinstance(data, Trigger):
                self.Actions_Run(data, action)

    def Execute_Trigger(self, data: Trigger):
        if data.action_id in self.registeredActions:
            act: QAction = self.registeredActions[data.action_id]
            if data.extra_composer_mode: self.OnEvent_ComposerStart()
            act.trigger()
            
        else:
            action = KritaAPI.get_action(data.action_id)
            if action:
                if data.extra_composer_mode: self.OnEvent_ComposerStart()
                action.trigger()
    
    def Execute_Menu(self, action: QAction, id: str):
        data: TriggerMenu = TouchifySettings.registryItem(id, TriggerMenu)
        if not isinstance(data, TriggerMenu) or data == None: return

        _parent = self.Helper_GetActionSource(action)
        contextMenu = TriggerMenuWidget(data, _parent, self)
        contextMenu.show()
            
    def Execute_Brush(self, id):
        brush_presets = IconRepository.brushPresets()
        if id in brush_presets:
            preset = brush_presets[id]
            self.api_window.active_view.setCurrentBrushPreset(preset)
    
    def Execute_Docker(self, path):
        dockersList = self.api_window.dockers
        for docker in dockersList:
            if (docker.objectName() == path):
                docker.setVisible(not docker.isVisible())
                    
    def Execute_Workspace(self, path):
        main_menu = self.api_window.qwindow.menuBar()
        for root_items in main_menu.actions():
            if root_items.objectName() == 'window':
                for sub_item in root_items.menu().actions():
                    if sub_item.text() == 'Wor&kspace':
                        for workspace in sub_item.menu().actions():
                            if workspace.text() == path:
                                workspace.trigger()
                                break
                            
    def Execute_DockerGroup(self, id: str):
        data: DockerGroup = TouchifySettings.registryItem(id, DockerGroup)
        if not isinstance(data, DockerGroup) or data == None: return


        dockersList = self.api_window.dockers
        
        if data.id not in self.custom_docker_states:
            paths = []
            for dockerName in data.docker_names:
                paths.append(str(dockerName))

            self.custom_docker_states[data.id] = {
                "enabled": False,
                "paths": paths,
                "groupId": data.group_id,
                "tabsMode": data.tabs_mode
            }
        dockerGroup = self.custom_docker_states[data.id]
            

        isVisible = not dockerGroup["enabled"]
        dockerGroup["enabled"] = isVisible

        if dockerGroup["tabsMode"]:
            for index, key in enumerate(self.custom_docker_states):
                entry = self.custom_docker_states[key]
                if key is not data.id and dockerGroup["groupId"] == entry["groupId"] and entry["tabsMode"]:
                    sub_visibility = False
                    entry["enabled"] = sub_visibility
                    for path in entry["paths"]:
                        for docker in dockersList:
                            if (docker.objectName() == path):
                                docker.setVisible(sub_visibility)

        for path in self.custom_docker_states[data.id]["paths"]:
            for docker in dockersList:
                if (docker.objectName() == path):
                    docker.setVisible(isVisible)
                            
    def Execute_Popup(self, action: QAction, id: str):    
        _parent = self.Helper_GetActionSource(action)            
        self.Create_Popup(id, _parent)
    
    def Execute_CanvasCfg(self, id: str):
        data: CanvasPreset = TouchifySettings.registryItem(id, CanvasPreset)
        if not isinstance(data, CanvasPreset) or data == None: return
    
        def slotConfigChanged(obj: QObject):
            canvas_call = getattr(obj, "slotConfigChanged", None)
            if callable(canvas_call):
                canvas_call()
                
        data.activate()

        qwin = self.api_window.qwindow
        for i, view in enumerate(self.api_window.views):
            view_obj = qwin.findChild(QWidget,'view_' + str(i))     
            for child in view_obj.children():
                slotConfigChanged(child)
            
            canvas_obj = view_obj.findChild(QOpenGLWidget)
            slotConfigChanged(canvas_obj)
            
        for docker in self.api_window.dockers:
            if (docker.objectName() == "KisLayerBox"):
                slotConfigChanged(docker)
    
    def Execute_Script(self, script_registry_id: str):
        data: CustomScript = TouchifySettings.registryItem(script_registry_id, CustomScript)
        if not isinstance(data, CustomScript) or data == None: return

        try:
            code = compile(data.script_code, '<string>', 'exec')
            exec(code, {'__name__': '__main__'})
        except Exception as ex:
            pass

    def Execute_PieWheel(self, pie_wheel_registry_id: str):
        try:

            from touchify.src.components.pie_wheel.TouchifyPieWheel import TouchifyPieWheel
            from shortcut_composer.templates.pie_menu_utils import PieWidget

            data: PieWheelData = TouchifySettings.registryItem(pie_wheel_registry_id, PieWheelData)
            if not isinstance(data, PieWheelData) or data == None: return

            result = TouchifyPieWheel.generate(data)
            result.Show()
            self.OnEvent_ComposerStart()

        except Exception as ex:
            raise ex

    #endregion