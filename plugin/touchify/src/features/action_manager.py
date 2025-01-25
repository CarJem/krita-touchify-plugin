from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from touchify.paths import REGISTERED_ACTIONS_FILE
from touchify.src.cfg.menu.TriggerMenuItem import TriggerMenuItem
from touchify.src.cfg.pie_wheel.PieWheelData import PieWheelData
from touchify.src.cfg.resource_pack.ResourcePack import ResourcePack
from touchify.src.cfg.resource_pack.ResourcePackMetadata import ResourcePackMetadata
from touchify.src.cfg.canvas_preset.CanvasPreset import CanvasPreset
from touchify.src.cfg.docker_group.DockerGroup import DockerGroup
from touchify.src.cfg.menu.TriggerMenu import TriggerMenu
from touchify.src.cfg.script.CustomScript import CustomScript

from touchify.src.components.pyqt.extensions import PyQtExtensions as QtExt
from touchify.src.components.touchify.actions.TouchifyActionMenu import TouchifyActionMenu

from touchify.src.components.touchify.actions.TouchifyActionButton import TouchifyActionButton

from touchify.src.global_events import GlobalEvents
from touchify.src.variables import *

from functools import partial

from touchify.src.cfg.triggers.Trigger import Trigger
from touchify.src.cfg.popup.PopupData import PopupData
from touchify.src.components.krita.extensions import *

from touchify.src.settings import TouchifySettings
from touchify.src.resources import ResourceManager

from touchify.src.components.touchify.special.TouchifyPopup import TouchifyPopup

from touchify.src.components.touchify.enums.common_actions import CommonActions

import xml.etree.ElementTree as ET
from xml.dom import minidom as MiniDOM

if TYPE_CHECKING:
    from ..window import TouchifyWindow

class ActionManager(QObject):
    composerTriggerEnded=pyqtSignal()

    brushChanged=pyqtSignal(Resource)
    gradientChanged=pyqtSignal(Resource)
    patternChanged=pyqtSignal(Resource)
    toolChanged=pyqtSignal(str)
    viewChanged=pyqtSignal(View)
    canvasChanged=pyqtSignal(Canvas)
    
    selectedNodesChanged=pyqtSignal()
    selectedNodeColorsChanged=pyqtSignal()
    
    brushSizeChanged=pyqtSignal(float)
    brushOpacityChanged=pyqtSignal(float)
    brushRotationChanged=pyqtSignal(float)
    brushFlowChanged=pyqtSignal(float)

    brushBlendingModeChanged=pyqtSignal(str)
    layerBlendingModeChanged=pyqtSignal(str)

    backgroundColorChanged=pyqtSignal(ManagedColor)
    foregroundColorChanged=pyqtSignal(ManagedColor)
    
    def __init__(self, instance: "TouchifyWindow"):
        super().__init__()
        self.appEngine = instance
        self.Variables()
        self.Connections()

    #region Init Functions

    def Variables(self):
        self.custom_docker_states = {}
        self.registeredActions = {}
        self.registeredActionsData = {}
        self.active_popups: dict[str, TouchifyPopup] = {}
        self.composer_action_down: bool = False

        self.__lastView: View = None
        self.__lastBrushPreset: Resource = None
        self.__lastCanvas: Canvas = None
        self.__lastGradient: Resource = None
        self.__lastPattern: Resource = None

        self.__lastToolboxTool: str = ""

        self.__lastBrushSize: float = 0
        self.__lastBrushOpacity: float = 0
        self.__lastBrushFlow: float = 0
        self.__lastBrushRotation: float = 0

        self.__lastBrushBlendingMode: str = ""
        self.__lastLayerBlendingMode: str = ""

        self.__lastForegroundColor: ManagedColor = None
        self.__lastBackgroundColor: ManagedColor = None

        self.__lastSelectedNodes: list[Node] = []
        self.__lastNodeColors: list[int] = []

    def Connections(self):
        GlobalEvents.instance().SIGNAL_MOUSE_RELEASED.connect(self.OnEvent_GlobalMouseRelease)
        GlobalEvents.instance().SIGNAL_TIMER_TICKED.connect(self.OnEvent_TimerTicked)
        GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.OnEvent_ConfigUpdated)

    #endregion

    #region Window Functions

    def Window_Load(self):
        qwin = Krita.instance().activeWindow().qwindow()
        mobj = next((w for w in qwin.findChildren(QWidget) if w.metaObject().className() == 'KoToolBox'), None)
        wobj = mobj.findChild(QButtonGroup)
        wobj.buttonToggled.connect(self.OnEvent_ToolChanged)

    #endregion

    #region Get Functions

    def getCurrentGradient(self):
        return self.__lastGradient
    
    def getCurrentPattern(self):
        return self.__lastPattern

    def getCurrentView(self):
        return self.__lastView

    def getCurrentTool(self):
        return self.__lastToolboxTool

    def getBrushBlendingMode(self):
        return self.__lastBrushBlendingMode
    
    def getLayerBlendingMode(self):
        return self.__lastLayerBlendingMode

    def getCurrentCanvas(self):
        return self.__lastCanvas
    
    def getCurrentBrush(self):
        return self.__lastBrushPreset
    
    def getBrushSize(self):
        return self.__lastBrushSize
    
    def getBrushOpacity(self):
        return self.__lastBrushOpacity
    
    def getBrushFlow(self):
        return self.__lastBrushFlow
    
    def getBrushRotation(self):
        return self.__lastBrushRotation

    def getCanvasColor(self, is_background: bool = False):
        if is_background: return self.__lastBackgroundColor
        else: return self.__lastForegroundColor

    #endregion

    #region Create Functions

    def Create_RegistryAction(self, actionIdentifier: str, data: Trigger, window: Window, actionPath: str):
        displayName = data.display_custom_text
        action = window.createAction(actionIdentifier, displayName, actionPath)

        self.registeredActions[actionIdentifier] = action
        self.registeredActionsData[actionIdentifier] = data  
        action.triggered.connect(partial(self.Execute_RegistryAction, actionIdentifier, action))
             
        (has_text, text, has_icon, icon, using_action_icon) = self.Helper_GetTriggerDisplay(data)
        if has_icon: action.setIcon(icon)
        return action   
    
    def Create_Button(self, parent: QWidget, data: Trigger):
        if data.variant == Trigger.Variants.Action:
            if data.action_id and data.action_id in self.registeredActions:
                data = self.registeredActionsData[data.action_id]

        match data.variant:
            case Trigger.Variants.Brush:
                result = self.Button_Brush(data)
            case Trigger.Variants.Menu:
                result = self.Button_Menu(data)
            case Trigger.Variants.Popup:
                result = self.Button_Popup(data)
            case Trigger.Variants.Action:
                result = self.Button_Trigger(data)
            case _:
                result = self.Button_Generic(data)

        if result and result != None:
            if data.extra_closes_popup == True:
                result.triggerActivated.connect(lambda: self.ButtonEvent_ClosePopup(result))
            result.setParent(parent)

        return result
    
    def Create_MenuItem(self, parent: TouchifyActionMenu, data: TriggerMenuItem):
        if data.variant == TriggerMenuItem.Variants.Action:
            if data.action_id and data.action_id in self.registeredActions:
                data = self.registeredActionsData[data.action_id]

        match data.variant:
            case TriggerMenuItem.Variants.Menu:
                actual_menu = TouchifyActionMenu(data, parent, self)
                actual_menu.setTitle(data.display_custom_text)
                parent.addMenu(actual_menu)
            case TriggerMenuItem.Variants.Action:
                if data.action_id in CommonActions.EXPANDING_SPACERS:
                    actual_action = QAction(parent)
                    actual_action.setSeparator(True)
                else:
                    actual_action = parent.krita_instance.action(data.action_id)
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

        if id == "touchify_internal_brush_picker":
            data: PopupData = PopupData()
            data.type = "docker"
            data.window_type = "popup"
            data.docker_id = "PresetDocker"
            data.popup_width = 300
            data.popup_height = 500
        elif id == "gradient_chooser_popup" or id == "pattern_chooser_popup":    
            main_window = self.appEngine.krita_window.qwindow()
            frames = main_window.findChildren(QFrame,'KisPopupButtonFrame')
            for frame in frames:
                result = frame.findChild(QWidget, id)
                if result: 
                    frame.show()
                    if _parent: position = QtExt.Geometry.clampToTarget(
                        _parent.mapToGlobal(QPoint(0,0)), frame.size(), main_window, QPoint(0, _parent.height()))
                    else: position = QCursor.pos()
                    frame.move(position.x(), position.y())
                    break
            return
        else:
            data: PopupData = TouchifySettings.instance().getRegistryItem(id, PopupData)
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

            popup = TouchifyPopup.construct(id, self.appEngine.krita_window.qwindow().window(), data, self.appEngine)
            if popup == None: return
            
            self.active_popups[popup_id] = popup

        popup.triggerPopup(_parent)

    #endregion

    #region Registered Action Functions

    def Actions_Post(self, menu: QMenu):
        menu.addMenu(self.__registry_menu)

    def Actions_Init(self, window: Window, subItemPath: str):
        cfg = TouchifySettings.instance().getConfig()

        self.__registry_menu = QtWidgets.QMenu("Registered Actions", window.qwindow())
        root_action = window.createAction(TOUCHIFY_ID_ACTION_REGISTERED_ACTIONS_MENU, "Registered Actions", subItemPath)
        root_action.setMenu(self.__registry_menu)
        registryItemsPath = "{0}/{1}".format(subItemPath, TOUCHIFY_ID_ACTION_REGISTERED_ACTIONS_MENU)

        registered_elements: dict[str, tuple[ResourcePackMetadata, list[ET.Element]]] = {}

        for pack in cfg.resources.presets:
            pack: ResourcePack
            packMeta = pack.metadata
            pack_name = packMeta.registry_name
            pack_id = packMeta.registry_id

            pack_menu = QtWidgets.QMenu(pack_name, window.qwindow())
            pack_action = window.createAction(pack_id, pack_name, registryItemsPath)
            pack_action.setMenu(pack_menu)
            packItemsPath = "{0}/{1}".format(registryItemsPath, pack_id)

            registered_elements[packMeta.registry_id] = packMeta, []
            for data in pack.triggers:
                data: Trigger
                id = '{0}{1}_{2}'.format(TOUCHIFY_REGISTRY_PREFIX, packMeta.registry_id, data.registry_id)
                action = self.appEngine.mgr_actions.Create_RegistryAction(id, data, window, packItemsPath)
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
            icon = ResourceManager.iconLoader(data.display_custom_icon)
        else:
            if is_brush: icon = ResourceManager.brushIcon(data.brush_name)
            elif is_action: 
                icon = ResourceManager.actionIcon(data.action_id)
                using_action_icon = True
            else: icon = QIcon()

        if use_custom_text:
            text: str = data.display_custom_text  
        else:
            if is_brush: text = data.brush_name
            elif is_action: text = ResourceManager.actionText(data.action_id)
            else: text = ""

        has_icon = not icon.isNull()
        has_text = text != ""

        if data.display_text_hide: has_text = False
        if data.display_icon_hide: has_icon = False

        return (has_text, text, has_icon, icon, using_action_icon)

    def Helper_SetButtonDisplay(self, act: Trigger, btn: TouchifyActionButton):
        (has_text, text, has_icon, icon, using_action_icon) = self.Helper_GetTriggerDisplay(act)  
        if has_text: btn.setText(text)      
        if has_icon: btn.setIcon(icon) 
        if using_action_icon: btn.setupActionIcon()        
        btn.setMetadata(text, icon)

    #endregion    
    
    #region OnEvent Functions

    def OnEvent_ConfigUpdated(self):
        registered_ids: list[str] = []
        for data in self.registeredActions:
            registered_ids.append(data)

        for popup_id in self.active_popups:
            try:
                popup: TouchifyPopup = self.active_popups[popup_id]
                popup.shutdownWidget()
            except:
                pass
        self.active_popups.clear()
        

        cfg = TouchifySettings.instance().getConfig()

        for pack in cfg.resources.presets:
            pack: ResourcePack
            meta: ResourcePackMetadata = pack.metadata
            for data in pack.triggers:
                data: Trigger
                subActionIdentifier = '{0}{1}_{2}'.format(TOUCHIFY_REGISTRY_PREFIX, meta.registry_id, data.registry_id)
                if subActionIdentifier in self.registeredActions:
                    self.registeredActionsData[subActionIdentifier] = data
        
    def OnEvent_ToolChanged(self, obj: QAbstractButton):
        if obj:
            toolboxTool = obj.objectName()
            if toolboxTool != self.__lastToolboxTool:
                self.__lastToolboxTool = toolboxTool
                self.toolChanged.emit(toolboxTool)

    def OnEvent_GlobalMouseRelease(self):
        if self.composer_action_down == True:
            QApplication.instance().sendEvent(Krita.instance().activeWindow().qwindow(), QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier))
            self.composerTriggerEnded.emit()
            try:
                self.composerTriggerEnded.disconnect()
            except:
                pass
            self.composer_action_down = False

    def OnEvent_TimerTicked(self):
        currentBrush: Resource = None
        currentGradient: Resource = None
        currentPattern: Resource = None
        currentView: View = None
        currentCanvas: Canvas = None

        currentBrushBlendingMode: str = ""
        currentLayerBlendingMode: str = ""

        currentSize: float = 0
        currentOpacity: float = 0
        currentFlow: float = 0
        currentRotation: float = 0

        currentForegroundColor: ManagedColor = None
        currentBackgroundColor: ManagedColor = None

        selectedNodes: list[Node] = []
        selectedNodeColors: list[int] = []

        try:
            win = self.appEngine.krita_window
            if win: 
                currentView = win.activeView()
                if currentView: 
                    currentDocument = currentView.document()
                    if currentDocument:
                        currentNode = currentDocument.activeNode()
                        if currentNode:
                            currentLayerBlendingMode = currentNode.blendingMode()

                    selectedNodes = currentView.selectedNodes()
                    selectedNodeColors = [node.colorLabel() for node in currentView.selectedNodes() ]

                    currentGradient = currentView.currentGradient()
                    currentPattern = currentView.currentPattern()
                    currentBrush = currentView.currentBrushPreset()
                    currentSize = currentView.brushSize()
                    currentOpacity = currentView.paintingOpacity()
                    currentFlow = currentView.paintingFlow()
                    currentRotation = currentView.brushRotation()
                    currentBrushBlendingMode = currentView.currentBlendingMode()
                    
                    currentCanvas = currentView.canvas()

                    currentForegroundColor = currentView.foregroundColor()
                    currentBackgroundColor = currentView.backgroundColor()


        except:
            pass

        if currentGradient != self.__lastGradient:
            self.gradientChanged.emit(currentGradient)
            self.__lastGradient = currentGradient

        if currentPattern != self.__lastPattern:
            self.patternChanged.emit(currentPattern)
            self.__lastPattern = currentPattern

        if currentCanvas != self.__lastCanvas:
            self.canvasChanged.emit(currentCanvas)
            self.__lastCanvas = currentCanvas

        if currentView != self.__lastView:
            self.viewChanged.emit(currentView)
            self.__lastView = currentView

        if selectedNodes != self.__lastSelectedNodes:
            self.selectedNodesChanged.emit()
            self.__lastSelectedNodes = selectedNodes

        if selectedNodeColors != self.__lastNodeColors:
            self.selectedNodeColorsChanged.emit()
            self.__lastNodeColors = selectedNodeColors

        if currentLayerBlendingMode != self.__lastLayerBlendingMode:
            self.layerBlendingModeChanged.emit(currentLayerBlendingMode)
            self.__lastLayerBlendingMode = currentLayerBlendingMode

        if currentBrushBlendingMode != self.__lastBrushBlendingMode:
            self.brushBlendingModeChanged.emit(currentBrushBlendingMode)
            self.__lastBrushBlendingMode = currentBrushBlendingMode

        if currentForegroundColor != self.__lastForegroundColor:
            #print("foreground changed")
            self.foregroundColorChanged.emit(currentForegroundColor)
            self.__lastForegroundColor = currentForegroundColor

        if currentBackgroundColor != self.__lastBackgroundColor:
            #print("foreground changed")
            self.backgroundColorChanged.emit(currentBackgroundColor)
            self.__lastBackgroundColor = currentBackgroundColor

        
        if currentSize != self.__lastBrushSize:
            self.brushSizeChanged.emit(currentSize)
            self.__lastBrushSize = currentSize

        if currentFlow != self.__lastBrushFlow:
            self.brushFlowChanged.emit(currentFlow)
            self.__lastBrushFlow = currentFlow

        if currentOpacity != self.__lastBrushOpacity:
            self.brushOpacityChanged.emit(currentOpacity)
            self.__lastBrushOpacity = currentOpacity

        if currentRotation != self.__lastBrushRotation:
            self.brushRotationChanged.emit(currentRotation)
            self.__lastBrushRotation = currentRotation

        if currentBrush != self.__lastBrushPreset:
            self.brushChanged.emit(currentBrush)
            self.__lastBrushPreset = currentBrush

    #endregion
        
    #region ButtonEvent Functions

    def ButtonEvent_ShortcutComposer(self, btn: TouchifyActionButton, onClick: any):
        def tryFindParentPopup(source: QWidget):
            from touchify.src.components.touchify.special.TouchifyPopup import TouchifyPopup
            try:
                widget = source.parent()
                while (widget):
                    foo = widget
                    if isinstance(foo, TouchifyPopup):
                        return foo
                    widget = widget.parent()
                return None
            except:
                return None
            
        parentPopup = tryFindParentPopup(btn)
        if parentPopup: 
            parentPopup.composer_work_around = True
            self.composerTriggerEnded.connect(parentPopup.composerEndEvent)

        onClick()
        self.composer_action_down = True

    def ButtonEvent_ClosePopup(self, btn: TouchifyActionButton):
        if btn:
            parent: QWidget | None = btn.parentWidget()
            while parent:
                if isinstance(parent, TouchifyPopup):
                    parent.closePopup()
                    return
                else:
                    parent = parent.parentWidget()
            return
                
    #endregion

    #region Button Constructors

    def Button_Core(self, onClick: any, toolTip: str, composerMode: bool = False):
        btn = TouchifyActionButton()
        
        if onClick:
            if composerMode: btn.setTrigger(lambda: self.ButtonEvent_ShortcutComposer(btn, onClick), True)
            else: btn.setTrigger(onClick) # collect and disconnect all when closing
                
        btn.setToolTip(toolTip)
        btn.setContentsMargins(0,0,0,0)
        return btn
   
    def Button_Brush(self, act: Trigger):
        btn: TouchifyActionButton | None = None
        id = act.brush_name
        brush_presets = ResourceManager.brushPresets()
        
        if id in brush_presets:
            preset = brush_presets[id]
            btn = self.Button_Core(lambda: self.Execute_Brush(id), preset.name())
            btn.setupBrushChange(self, id, preset == self.__lastBrushPreset)
            self.Helper_SetButtonDisplay(act, btn)
        return btn
                   
    def Button_Menu(self, act: Trigger):
        data: TriggerMenu = TouchifySettings.instance().getRegistryItem(act.context_menu_id, TriggerMenu)
        if not isinstance(data, TriggerMenu) or data == None: return None
        
        btn: TouchifyActionButton = self.Button_Core(None, act.display_custom_text)   
        self.Helper_SetButtonDisplay(act, btn)
        
        contextMenu = TouchifyActionMenu(data, btn, self)
        btn.setMenu(contextMenu)
        btn.triggerActivated.connect(btn.showMenu)
        return btn
    
    def Button_Popup(self, data: Trigger):
        btn: TouchifyActionButton | None = None
        btn = self.Button_Core(None, data.display_custom_text)
        btn.triggerActivated.connect((lambda: self.Create_Popup(data.popup_data, btn)))
        self.Helper_SetButtonDisplay(data, btn)
        return btn

    def Button_Generic(self, data: Trigger):
        btn: TouchifyActionButton | None = None
        
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

        btn = self.Button_Core(onClick, data.display_custom_text)
        self.Helper_SetButtonDisplay(data, btn)
        return btn
        
    def Button_Trigger(self, act: Trigger):
        action = Krita.instance().action(act.action_id)
        btn: TouchifyActionButton | None = None
        if action:
            checkable = action.isCheckable()
            toolbox_item = False
            
            if act.action_id in CommonActions.KNOWN_UNCHECKABLES:
                checkable = False
            
            if act.action_id in CommonActions.TOOLBOX_ITEMS:
                toolbox_item = True

            
            btn = self.Button_Core(action.trigger, action.toolTip(), act.extra_composer_mode)

            if toolbox_item: btn.setupToolChange(self, act.action_id, self.__lastToolboxTool == act.action_id)
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
            act.trigger()
        else:
            action = Krita.instance().action(data.action_id)
            if action:
                action.trigger()
    
    def Execute_Menu(self, action: QAction, id: str):
        data: TriggerMenu = TouchifySettings.instance().getRegistryItem(id, TriggerMenu)
        if not isinstance(data, TriggerMenu) or data == None: return

        _parent = self.Helper_GetActionSource(action)
        contextMenu = TouchifyActionMenu(data, _parent, self)
        contextMenu.show()
            
    def Execute_Brush(self, id):
        brush_presets = ResourceManager.brushPresets()
        if id in brush_presets:
            preset = brush_presets[id]
            self.appEngine.krita_window.activeView().setCurrentBrushPreset(preset)
    
    def Execute_Docker(self, path):
        dockersList = self.appEngine.krita_window.dockers()
        for docker in dockersList:
            if (docker.objectName() == path):
                docker.setVisible(not docker.isVisible())
                    
    def Execute_Workspace(self, path):
        main_menu = self.appEngine.krita_window.qwindow().menuBar()
        for root_items in main_menu.actions():
            if root_items.objectName() == 'window':
                for sub_item in root_items.menu().actions():
                    if sub_item.text() == 'Wor&kspace':
                        for workspace in sub_item.menu().actions():
                            if workspace.text() == path:
                                workspace.trigger()
                                break
                            
    def Execute_DockerGroup(self, id: str):
        data: DockerGroup = TouchifySettings.instance().getRegistryItem(id, DockerGroup)
        if not isinstance(data, DockerGroup) or data == None: return


        dockersList = self.appEngine.krita_window.dockers()
        
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
        data: CanvasPreset = TouchifySettings.instance().getRegistryItem(id, CanvasPreset)
        if not isinstance(data, CanvasPreset) or data == None: return
    
        def slotConfigChanged(obj: QObject):
            canvas_call = getattr(obj, "slotConfigChanged", None)
            if callable(canvas_call):
                canvas_call()
                
        data.activate()

        qwin = self.appEngine.krita_window.qwindow()
        for i, view in enumerate(self.appEngine.krita_window.views()):
            view_obj = qwin.findChild(QWidget,'view_' + str(i))     
            for child in view_obj.children():
                slotConfigChanged(child)
            
            canvas_obj = view_obj.findChild(QOpenGLWidget)
            slotConfigChanged(canvas_obj)
            
        for docker in self.appEngine.krita_window.dockers():
            if (docker.objectName() == "KisLayerBox"):
                slotConfigChanged(docker)
    
    def Execute_Script(self, script_registry_id: str):
        data: CustomScript = TouchifySettings.instance().getRegistryItem(script_registry_id, CustomScript)
        if not isinstance(data, CustomScript) or data == None: return

        try:
            code = compile(data.script_code, '<string>', 'exec')
            exec(code, {'__name__': '__main__'})
        except Exception as ex:
            pass

    def Execute_PieWheel(self, pie_wheel_registry_id: str):
        data: PieWheelData = TouchifySettings.instance().getRegistryItem(pie_wheel_registry_id, PieWheelData)
        if not isinstance(data, PieWheelData) or data == None: return
        
        result = self.appEngine.mgr_sc.PieWheel_Generate(data)
        if result != None: 
            result.Show()
            self.composer_action_down = True

    #endregion