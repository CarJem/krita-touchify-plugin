from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from touchify.paths import REGISTERED_ACTIONS_FILE
from touchify.src.cfg.menu.TriggerMenuItem import TriggerMenuItem
from touchify.src.cfg.resource_pack.ResourcePack import ResourcePack
from touchify.src.cfg.resource_pack.ResourcePackMetadata import ResourcePackMetadata
from touchify.src.cfg.canvas_preset.CanvasPreset import CanvasPreset
from touchify.src.cfg.docker_group.DockerGroup import DockerGroup
from touchify.src.cfg.menu.TriggerMenu import TriggerMenu
from touchify.src.components.pyqt.event_filters.MouseReleaseListener import MouseReleaseListener

from touchify.src.components.touchify.actions.TouchifyActionMenu import TouchifyActionMenu

from touchify.src.components.touchify.actions.TouchifyActionButton import TouchifyActionButton

from touchify.src.variables import *

from functools import partial

from touchify.src.cfg.triggers.Trigger import Trigger
from touchify.src.cfg.popup.PopupData import PopupData
from touchify.src.ext.KritaExtensions import *

from touchify.src.settings import TouchifySettings
from touchify.src.resources import ResourceManager

from touchify.src.components.touchify.special.TouchifyPopup import TouchifyPopup

from touchify.src.enums.common_actions import CommonActions

import xml.etree.ElementTree as ET
from xml.dom import minidom as MiniDOM

if TYPE_CHECKING:
    from .window import TouchifyWindow

class ActionManager(QObject):

    

    composerTriggerEnded=pyqtSignal()

    brushChanged=pyqtSignal(Resource)
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
        self.custom_docker_states = {}
        self.registeredActions = {}
        self.registeredActionsData = {}
        self.active_popups: dict[str, TouchifyPopup] = {}


        self.queue_update_running = False

        self.composer_action_down: bool = False
        self.composer_listener = MouseReleaseListener()
        self.composer_listener.mouseReleased.connect(self.onMouseRelease)
        qApp.installEventFilter(self.composer_listener)


        self.__lastView: View = None
        self.__lastBrushPreset: Resource = None
        self.__lastCanvas: Canvas = None

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



    def runAction(self, data: Trigger, action: QAction):
        match data.variant:
            case Trigger.Variants.CanvasPreset:
                self.action_canvas(data.canvas_preset_data)
            case Trigger.Variants.Docker:
                self.action_docker(data.docker_id)
            case Trigger.Variants.Workspace:
                self.action_workspace(data.workspace_id)
            case Trigger.Variants.Popup:
                self.action_popup(action, data.popup_data)
            case Trigger.Variants.Brush:
                self.action_brush(data.brush_name)
            case Trigger.Variants.DockerGroup:
                self.action_dockergroup(data.docker_group_data)
            case Trigger.Variants.Menu:
                self.action_menu(action, data.context_menu_id)
            case Trigger.Variants.Action:
                self.action_trigger(data)
            
    def createButton(self, parent: QWidget, data: Trigger):
        if data.variant == Trigger.Variants.Action:
            if data.action_id and data.action_id in self.registeredActions:
                data = self.registeredActionsData[data.action_id]

        match data.variant:
            case Trigger.Variants.Brush:
                result = self.button_brush(data)
            case Trigger.Variants.Menu:
                result = self.button_menu(data)
            case Trigger.Variants.Popup:
                result = self.button_popup(data)
            case Trigger.Variants.Action:
                result = self.button_trigger(data)
            case _:
                result = self.button_generic(data)

        if result and result != None:
            if data.extra_closes_popup == True:
                result.triggerActivated.connect(lambda: self.__btn_closePopup(result))
            result.setParent(parent)

        return result
    
    def createMenuItem(self, parent: TouchifyActionMenu, data: TriggerMenuItem):
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
                actual_action.triggered.connect(lambda: self.runAction(data, actual_action))
                if actual_action: parent.addAction(actual_action)

    def openPopup(self, id: str, _parent: QWidget = None):

        if id == "touchify_internal_brush_picker":
            data: PopupData = PopupData()
            data.type = "docker"
            data.window_type = "popup"
            data.docker_id = "PresetDocker"
            data.popup_width = 300
            data.popup_height = 500
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

            popup = TouchifyPopup.construct(id, self.appEngine.windowSource.qwindow().window(), data, self.appEngine)
            if popup == None: return
            
            self.active_popups[popup_id] = popup

        popup.triggerPopup(_parent)

    #region Getters

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

    #region Event Functions
    def onWindowCreated(self):
        qwin = Krita.instance().activeWindow().qwindow()
        mobj = next((w for w in qwin.findChildren(QWidget) if w.metaObject().className() == 'KoToolBox'), None)
        wobj = mobj.findChild(QButtonGroup)
        wobj.buttonToggled.connect(self.onToolChanged)

    def onComposerBtnPressed(self, btn: TouchifyActionButton, onClick: any):
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

    def onConfigUpdated(self):
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
                subActionIdentifier = '{0}{1}_{2}'.format(TOUCHIFY_ID_ACTION_REGISTERED, meta.registry_id, data.registry_id)
                if subActionIdentifier in self.registeredActions:
                    self.registeredActionsData[subActionIdentifier] = data
        
    def onToolChanged(self, obj: QAbstractButton):
        if obj:
            toolboxTool = obj.objectName()
            if toolboxTool != self.__lastToolboxTool:
                self.__lastToolboxTool = toolboxTool
                self.toolChanged.emit(toolboxTool)

    def onMouseRelease(self):
        if self.composer_action_down == True:
            QApplication.instance().sendEvent(Krita.instance().activeWindow().qwindow(), QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier))
            self.composerTriggerEnded.emit()
            try:
                self.composerTriggerEnded.disconnect()
            except:
                pass
            self.composer_action_down = False

    def onTimerTick(self):
        currentBrush: Resource = None
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
            win = self.appEngine.windowSource
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
            print("foreground changed")
            self.foregroundColorChanged.emit(currentForegroundColor)
            self.__lastForegroundColor = currentForegroundColor

        if currentBackgroundColor != self.__lastBackgroundColor:
            print("foreground changed")
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
        
    #region Registered Actions

    def createRegisteredElement(self, actionname):
        element = ET.Element("Action",{"name":"{0}".format(actionname)})
        ET.SubElement(element,"text").text = actionname
        ET.SubElement(element,"shortcut").text = "none"
        return element
    
    def runRegisteredAction(self, identifier: str, action: QAction):
        if identifier in self.registeredActions:
            data: Trigger = self.registeredActionsData[identifier]
            if isinstance(data, Trigger):
                self.runAction(data, action)

    def installRegisteredAction(self, actionIdentifier: str, data: Trigger, window: Window, actionPath: str):
        displayName = data.display_custom_text
        action = window.createAction(actionIdentifier, displayName, actionPath)

        self.registeredActions[actionIdentifier] = action
        self.registeredActionsData[actionIdentifier] = data  
        action.triggered.connect(partial(self.runRegisteredAction, actionIdentifier, action))
             
        (has_text, text, has_icon, icon, using_action_icon) = self.__getTouchifyActionDisplay(data)
        if has_icon: action.setIcon(icon)
        return action
    
    def writeRegisteredActions(self, registry: dict[str, tuple[ResourcePackMetadata, list[ET.Element]]]):
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

    def createRegisteredActions(self, window: Window, actionPath: str):
        subItemPath = actionPath
        cfg = TouchifySettings.instance().getConfig()
        root_menu = QtWidgets.QMenu("Registered Actions")

        registered_elements: dict[str, tuple[ResourcePackMetadata, list[ET.Element]]] = {}

        for pack in cfg.resources.presets:
            pack: ResourcePack
            packMeta = pack.metadata
            pack_menu = root_menu.addMenu(packMeta.registry_name)
            registered_elements[packMeta.registry_id] = packMeta, []
            for data in pack.triggers:
                data: Trigger
                id = '{0}{1}_{2}'.format(TOUCHIFY_ID_ACTION_REGISTERED, packMeta.registry_id, data.registry_id)
                
                action = self.appEngine.action_management.installRegisteredAction(id, data, window, subItemPath)
                registered_elements[packMeta.registry_id][1].append(self.createRegisteredElement(id))
                pack_menu.addAction(action)
            
        self.writeRegisteredActions(registered_elements)

        return root_menu

    #endregion

    #region Helper Functions

    def __getActionSource(self, action: QAction):
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
    
    def __getTouchifyActionDisplay(self, data: Trigger):
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

    def __setButtonDisplay(self, act: Trigger, btn: TouchifyActionButton):
        (has_text, text, has_icon, icon, using_action_icon) = self.__getTouchifyActionDisplay(act)  
        if has_text: btn.setText(text)      
        if has_icon: btn.setIcon(icon) 
        if using_action_icon: btn.setupActionIcon()        
        btn.setMetadata(text, icon)

    #endregion    
    
    #region Button Callbacks

    def __btn_closePopup(self, btn: TouchifyActionButton):
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
    def button_main(self, onClick: any, toolTip: str, composerMode: bool = False):
        btn = TouchifyActionButton()
        
        if onClick:
            if composerMode: btn.setTrigger(lambda: self.onComposerBtnPressed(btn, onClick), True)
            else: btn.setTrigger(onClick) # collect and disconnect all when closing
                
        btn.setToolTip(toolTip)
        btn.setContentsMargins(0,0,0,0)
        return btn
   
    def button_brush(self, act: Trigger):
        btn: TouchifyActionButton | None = None
        id = act.brush_name
        brush_presets = ResourceManager.brushPresets()
        
        if id in brush_presets:
            preset = brush_presets[id]
            btn = self.button_main(lambda: self.action_brush(id), preset.name())
            btn.setupBrushChange(self, id, preset == self.__lastBrushPreset)
            self.__setButtonDisplay(act, btn)
        return btn
                   
    def button_menu(self, act: Trigger):
        data: TriggerMenu = TouchifySettings.instance().getRegistryItem(act.context_menu_id, TriggerMenu)
        if not isinstance(data, TriggerMenu) or data == None: return None
        
        btn: TouchifyActionButton = self.button_main(None, act.display_custom_text)   
        self.__setButtonDisplay(act, btn)
        
        contextMenu = TouchifyActionMenu(data, btn, self)
        btn.setMenu(contextMenu)
        btn.triggerActivated.connect(btn.showMenu)
        return btn
    
    def button_popup(self, data: Trigger):
        btn: TouchifyActionButton | None = None
        btn = self.button_main(None, data.display_custom_text)
        btn.triggerActivated.connect((lambda: self.openPopup(data.popup_data, btn)))
        self.__setButtonDisplay(data, btn)
        return btn

    def button_generic(self, data: Trigger):
        btn: TouchifyActionButton | None = None
        
        onClick = None
        
        match data.variant:
            case Trigger.Variants.Docker:
                onClick = (lambda: self.action_docker(data.docker_id))
            case Trigger.Variants.Workspace:
                onClick = (lambda: self.action_workspace(data.workspace_id))
            case Trigger.Variants.DockerGroup:
                onClick = (lambda: self.action_dockergroup(data.docker_group_data))
            case Trigger.Variants.CanvasPreset:
                onClick = (lambda: self.action_canvas(data.canvas_preset_data))

        btn = self.button_main(onClick, data.display_custom_text)
        self.__setButtonDisplay(data, btn)
        return btn
        
    def button_trigger(self, act: Trigger):
        action = Krita.instance().action(act.action_id)
        btn: TouchifyActionButton | None = None
        if action:
            checkable = action.isCheckable()
            toolbox_item = False
            
            if act.action_id in CommonActions.KNOWN_UNCHECKABLES:
                checkable = False
            
            if act.action_id in CommonActions.TOOLBOX_ITEMS:
                toolbox_item = True

            
            btn = self.button_main(action.trigger, action.toolTip(), act.extra_composer_mode)

            if toolbox_item: btn.setupToolChange(self, act.action_id, self.__lastToolboxTool == act.action_id)
            elif checkable: btn.setupActionCheckChange(action, act.action_id, action.isChecked())
            else: btn.setupAction(action, act.action_id)

            self.__setButtonDisplay(act, btn)
        return btn
    #endregion

    #region Action Functions    
    def action_trigger(self, data: Trigger):
        if data.action_id in self.registeredActions:
            act: QAction = self.registeredActions[data.action_id]
            act.trigger()
        else:
            action = Krita.instance().action(data.action_id)
            if action:
                action.trigger()
    
    def action_menu(self, action: QAction, id: str):
        data: TriggerMenu = TouchifySettings.instance().getRegistryItem(id, TriggerMenu)
        if not isinstance(data, TriggerMenu) or data == None: return

        _parent = self.__getActionSource(action)
        contextMenu = TouchifyActionMenu(data, _parent, self)
        contextMenu.show()
            
    def action_brush(self, id):
        brush_presets = ResourceManager.brushPresets()
        if id in brush_presets:
            preset = brush_presets[id]
            self.appEngine.windowSource.activeView().setCurrentBrushPreset(preset)
    
    def action_docker(self, path):
        dockersList = self.appEngine.windowSource.dockers()
        for docker in dockersList:
            if (docker.objectName() == path):
                docker.setVisible(not docker.isVisible())
                    
    def action_workspace(self, path):
        main_menu = self.appEngine.windowSource.qwindow().menuBar()
        for root_items in main_menu.actions():
            if root_items.objectName() == 'window':
                for sub_item in root_items.menu().actions():
                    if sub_item.text() == 'Wor&kspace':
                        for workspace in sub_item.menu().actions():
                            if workspace.text() == path:
                                workspace.trigger()
                                break
                            
    def action_dockergroup(self, id: str):
        data: DockerGroup = TouchifySettings.instance().getRegistryItem(id, DockerGroup)
        if not isinstance(data, DockerGroup) or data == None: return


        dockersList = self.appEngine.windowSource.dockers()
        
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
                            
    def action_popup(self, action: QAction, id: str):    
        _parent = self.__getActionSource(action)            
        self.openPopup(id, _parent)
    
    def action_canvas(self, id: str):
        data: CanvasPreset = TouchifySettings.instance().getRegistryItem(id, CanvasPreset)
        if not isinstance(data, CanvasPreset) or data == None: return
    
        def slotConfigChanged(obj: QObject):
            canvas_call = getattr(obj, "slotConfigChanged", None)
            if callable(canvas_call):
                canvas_call()
                
        data.activate()

        qwin = self.appEngine.windowSource.qwindow()
        for i, view in enumerate(self.appEngine.windowSource.views()):
            view_obj = qwin.findChild(QWidget,'view_' + str(i))     
            for child in view_obj.children():
                slotConfigChanged(child)
            
            canvas_obj = view_obj.findChild(QOpenGLWidget)
            slotConfigChanged(canvas_obj)
            
        for docker in self.appEngine.windowSource.dockers():
            if (docker.objectName() == "KisLayerBox"):
                slotConfigChanged(docker)
    #endregion