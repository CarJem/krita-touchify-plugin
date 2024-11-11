from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .components.touchify.popups.PopupDialog_Toolshelf import PopupDialog_Toolshelf

from .components.touchify.actions.TouchifyActionMenu import TouchifyActionMenu

from .components.touchify.actions.TouchifyActionButton import TouchifyActionButton

from .variables import *

from .cfg.action.CfgTouchifyAction import CfgTouchifyAction
from .cfg.action.CfgTouchifyActionDockerGroup import CfgTouchifyActionDockerGroup
from .cfg.action.CfgTouchifyActionPopup import CfgTouchifyActionPopup
from .cfg.action.CfgTouchifyActionCanvasPreset import CfgTouchifyActionCanvasPreset
from .ext.KritaExtensions import *

from touchify.src.settings.TouchifyConfig import TouchifyConfig
from touchify.src.resources import ResourceManager

from .components.touchify.popups.PopupDialog import PopupDialog
from .components.touchify.popups.PopupDialog_Actions import PopupDialog_Actions
from .components.touchify.popups.PopupDialog_Docker import PopupDialog_Docker

if TYPE_CHECKING:
    from .window import TouchifyWindow

class ActionManager(QObject):
    
    class TriggerConstants:
        KNOWN_UNCHECKABLES = [
            "show_brush_editor"
        ]

        EXPANDING_SPACERS = [
            "expanding_spacer1",
            "expanding_spacer2"
        ]

        TOOLBOX_ITEMS: dict[str, str] = {
            "KisToolTransform": "KisToolTransform",
            "KritaTransform/KisToolMove": "KritaTransform/KisToolMove",
            "KisToolCrop": "KisToolCrop",
            "InteractionTool": "InteractionTool",
            "SvgTextTool": "SvgTextTool",
            "PathTool": "PathTool",
            "KarbonCalligraphyTool": "KarbonCalligraphyTool",
            "KritaShape/KisToolBrush": "KritaShape/KisToolBrush",
            "KritaShape/KisToolDyna": "KritaShape/KisToolDyna",
            "KritaShape/KisToolMultiBrush": "KritaShape/KisToolMultiBrush",
            "KritaShape/KisToolSmartPatch": "KritaShape/KisToolSmartPatch",
            "KisToolPencil": "KisToolPencil",
            "KritaFill/KisToolFill": "KritaFill/KisToolFill",
            "KritaSelected/KisToolColorSampler": "KritaSelected/KisToolColorPicker",
            "KritaShape/KisToolLazyBrush": "KritaShape/KisToolLazyBrush",
            "KritaFill/KisToolGradient": "KritaFill/KisToolGradient",
            "KritaShape/KisToolRectangle": "KritaShape/KisToolRectangle",
            "KritaShape/KisToolLine": "KritaShape/KisToolLine",
            "KritaShape/KisToolEllipse": "KritaShape/KisToolEllipse",
            "KisToolPolygon": "KisToolPolygon",
            "KisToolPolyline": "KisToolPolyline",
            "KisToolPath": "KisToolPath",
            "KisToolEncloseAndFill": "KisToolEncloseAndFill",
            "KisToolSelectRectangular": "KisToolSelectRectangular",
            "KisToolSelectElliptical": "KisToolSelectElliptical",
            "KisToolSelectPolygonal": "KisToolSelectPolygonal",
            "KisToolSelectPath": "KisToolSelectPath",
            "KisToolSelectOutline": "KisToolSelectOutline",
            "KisToolSelectContiguous": "KisToolSelectContiguous",
            "KisToolSelectSimilar": "KisToolSelectSimilar",
            "KisToolSelectMagnetic": "KisToolSelectMagnetic",
            "ToolReferenceImages": "ToolReferenceImages",
            "KisAssistantTool": "KisAssistantTool",
            "KritaShape/KisToolMeasure": "KritaShape/KisToolMeasure",
            "PanTool": "PanTool",
            "ZoomTool": "ZoomTool"
    }
        
    def __init__(self, instance: "TouchifyWindow"):
        super().__init__()
        self.appEngine = instance
        self.custom_docker_states = {}
        self.registeredActions = {}
        self.registeredActionsData = {}


        self.__lastToolboxTool: str = ""
        self.__lastBrushPreset: Resource = None

    def onTimerTick(self):
        self.__onTimerTick()


    def onWindowCreated(self):
        def initToolboxHook():
            def onButtonToggled(obj: QAbstractButton):
                if obj:
                    toolboxTool = obj.objectName()
                    if toolboxTool != self.__lastToolboxTool:
                        self.__lastToolboxTool = toolboxTool
                        self.__updateActionToggleStates()
                        
            qwin = Krita.instance().activeWindow().qwindow()
            mobj = next((w for w in qwin.findChildren(QWidget) if w.metaObject().className() == 'KoToolBox'), None)
            wobj = mobj.findChild(QButtonGroup)
            wobj.buttonToggled.connect(onButtonToggled)
        
        initToolboxHook()

        
    def executeAction(self, data: CfgTouchifyAction, action: QAction):
        match data.variant:
            case CfgTouchifyAction.Variants.CanvasPreset:
                self.action_canvas(data.canvas_preset_data)
            case CfgTouchifyAction.Variants.Docker:
                self.action_docker(data.docker_id)
            case CfgTouchifyAction.Variants.Workspace:
                self.action_workspace(data.workspace_id)
            case CfgTouchifyAction.Variants.Popup:
                self.action_popup(action, data.popup_data)
            case CfgTouchifyAction.Variants.Brush:
                self.action_brush(data.brush_name)
            case CfgTouchifyAction.Variants.DockerGroup:
                self.action_dockergroup(data.docker_group_data)
            case CfgTouchifyAction.Variants.Menu:
                self.action_menu(action, data)
            case CfgTouchifyAction.Variants.Action:
                self.action_trigger(data)
            
    def createButton(self, parent: QWidget, data: CfgTouchifyAction):

        if data.variant == CfgTouchifyAction.Variants.Action:
            if data.action_id and data.action_id in self.registeredActions:
                data = self.registeredActionsData[data.action_id]

        match data.variant:
            case CfgTouchifyAction.Variants.Brush:
                result = self.button_brush(data)
            case CfgTouchifyAction.Variants.Menu:
                result = self.button_menu(data)
            case CfgTouchifyAction.Variants.Popup:
                result = self.button_popup(data)
            case CfgTouchifyAction.Variants.Action:
                result = self.button_trigger(data)
            case _:
                result = self.button_generic(data)

        if result and result != None:
            result.setParent(parent)
        return result
    
    def createAction(self, data: CfgTouchifyAction, window: Window, actionPath: str):
        actionIdentifier ='TouchifyAction_{0}'.format(data.id)
        displayName = data.text

        action = window.createAction(actionIdentifier, displayName, actionPath)
        self.registeredActions[actionIdentifier] = action
        self.registeredActionsData[actionIdentifier] = data
           
        TouchifyConfig.instance().addHotkeyOption(actionIdentifier, displayName, self.executeAction, {'data': data, 'action': action})      
        action.triggered.connect(lambda: self.executeAction(data, action))
        
        (use_text, text, use_icon, icon) = self.__getActionDisplay(data)
        if use_icon:
            action.setIcon(icon)
         
        return action
   
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
    
    def __checkActionIcon(self, result_icon: QIcon) -> tuple[bool, QIcon, bool]:
        icon: QIcon = None
        use_icon: bool = False  
        fallback_text: bool = False
        
        if not (result_icon == None or result_icon.isNull()):
            use_icon = True
            icon = result_icon
        else:
            fallback_text = True
        return (use_icon, icon, fallback_text)
    
    def __getActionDisplay(self, data: CfgTouchifyAction) -> tuple[bool, str, bool, QIcon]:   
      
        text: str = data.text  
        icon_loader_index = 0
        
        if data.variant == CfgTouchifyAction.Variants.Brush:
            if data.show_icon:
                if data.brush_override_icon and data.show_icon:
                    icon_loader_index = 1
                else:
                    icon_loader_index = 3
        elif data.variant == CfgTouchifyAction.Variants.Action:
            if data.show_icon and data.action_use_icon:
                icon_loader_index = 2
            elif data.show_icon:
                icon_loader_index = 1
        elif data.show_icon:
            icon_loader_index = 1
            
                
        match icon_loader_index:        
            case 1:
                result_icon = ResourceManager.iconLoader(data.icon)
                use_icon, icon, use_text = self.__checkActionIcon(result_icon)
            case 2:
                target_action = Krita.instance().action(data.action_id)
                result_icon: QIcon = None     
                if target_action: result_icon = target_action.icon()
                use_icon, icon, use_text = self.__checkActionIcon(result_icon)
            case 3:
                result_icon = ResourceManager.brushIcon(data.brush_name)
                use_icon, icon, use_text = self.__checkActionIcon(result_icon)
            case _:
                use_icon = False
                icon = None
                use_text = True

        return (use_text, text, use_icon, icon)

    def __setButtonDisplay(self, act: CfgTouchifyAction, btn: TouchifyActionButton):
        (use_text, text, use_icon, icon) = self.__getActionDisplay(act)
        
        if use_text:
            btn.setText(text)
        
        if use_icon: 
            btn.setIcon(icon)
            
        btn.setMetadata(text, icon)

    def __onTimerTick(self):
                
        def getCurrentBrush():
            try:
                win = self.appEngine.windowSource
                if not win: return None
                view = win.activeView()
                if not view: return None
                currentPreset: Resource = view.currentBrushPreset()
                if not currentPreset: return None

                return currentPreset
            except:
                pass
            return None
    
        queue_update = False
        currentPreset: Resource = getCurrentBrush()

        if currentPreset != self.__lastBrushPreset:
            queue_update = True
            self.__lastBrushPreset = currentPreset

        if queue_update:
            self.__updateActionToggleStates()

    def __updateActionToggleStates(self):
        src = self.appEngine.windowSource
        if not src: return

        win = src.qwindow()
        if not win: return
    
        btns = win.findChildren(TouchifyActionButton)
        for btn in btns: btn.timer_interval_triggered.emit()


    def __brushButtonUpdate(self, __btn: TouchifyActionButton, id: str):

        __brush_presets = ResourceManager.getBrushPresets()
        if id not in __brush_presets: return
        btn_preset = __brush_presets[id]
        
        if self.__lastBrushPreset != btn_preset: __btn.setBrushSelected(False)
        else: __btn.setBrushSelected(True)

    def __toolboxToolUpdate(self, __btn: TouchifyActionButton, id: str):
        if self.__lastToolboxTool != id: __btn.setChecked(False)
        else: __btn.setChecked(True)

    def __triggerPopup(self, data: CfgTouchifyActionPopup, _parent: QWidget = None):
        if data.type == CfgTouchifyActionPopup.Variants.Actions:
            popup = PopupDialog_Actions(self.appEngine.windowSource.qwindow().window(), data, self)
        elif data.type == CfgTouchifyActionPopup.Variants.Docker:
            popup = PopupDialog_Docker(self.appEngine.windowSource.qwindow().window(), data, self.appEngine.docker_management)
        elif data.type == CfgTouchifyActionPopup.Variants.Toolshelf:
            popup = PopupDialog_Toolshelf(self.appEngine.windowSource.qwindow().window(), data, self, self.appEngine.docker_management)
        else:
            popup = PopupDialog(self.appEngine.windowSource.qwindow().window(), data)  
        popup.triggerPopup(_parent)

       
    def button_main(self, onClick: any, toolTip: str, checkable: bool):
        btn = TouchifyActionButton()
        
        if onClick:
            btn.clicked.connect(onClick) # collect and disconnect all when closing
        btn.setToolTip(toolTip)
        btn.setContentsMargins(0,0,0,0)
        btn.setCheckable(checkable)
        return btn
   
    def button_brush(self, act: CfgTouchifyAction):
        btn: TouchifyActionButton | None = None
        id = act.brush_name
        brush_presets = ResourceManager.getBrushPresets()
        
        if id in brush_presets:
            preset = brush_presets[id]
            btn = self.button_main(lambda: self.action_brush(id), preset.name(), False)
            btn.timer_interval_triggered.connect(lambda: self.__brushButtonUpdate(btn, id))
            self.__setButtonDisplay(act, btn)
        return btn
                   
    def button_menu(self, act: CfgTouchifyAction):
        btn: TouchifyActionButton = self.button_main(None, act.text, False)   
        self.__setButtonDisplay(act, btn)
        
        contextMenu = TouchifyActionMenu(act, btn)
        btn.setMenu(contextMenu)
        btn.clicked.connect(btn.showMenu)
        return btn
    
    def button_popup(self, data: CfgTouchifyAction):
        btn: TouchifyActionButton | None = None
        btn = self.button_main(None, data.text, False)
        btn.clicked.connect((lambda: self.__triggerPopup(data.popup_data, btn)))
        self.__setButtonDisplay(data, btn)
        return btn

    def button_generic(self, data: CfgTouchifyAction):
        btn: TouchifyActionButton | None = None
        
        onClick = None
        
        match data.variant:
            case CfgTouchifyAction.Variants.Docker:
                onClick = (lambda: self.action_docker(data.docker_id))
            case CfgTouchifyAction.Variants.Workspace:
                onClick = (lambda: self.action_workspace(data.workspace_id))
            case CfgTouchifyAction.Variants.DockerGroup:
                onClick = (lambda: self.action_dockergroup(data.docker_group_data))

        btn = self.button_main(onClick, data.text, False)
        self.__setButtonDisplay(data, btn)
        return btn
        
    def button_trigger(self, act: CfgTouchifyAction):
        action = Krita.instance().action(act.action_id)
        btn: TouchifyActionButton | None = None
        if action:
            checkable = action.isCheckable()
            if act.action_id in ActionManager.TriggerConstants.KNOWN_UNCHECKABLES:
                checkable = False
            
            if act.action_id in ActionManager.TriggerConstants.TOOLBOX_ITEMS:
                checkable = True
            
            btn = self.button_main(action.trigger, action.toolTip(), checkable)

            if act.action_id in ActionManager.TriggerConstants.TOOLBOX_ITEMS:
                btn.timer_interval_triggered.connect(lambda: self.__toolboxToolUpdate(btn, act.action_id))

            self.__setButtonDisplay(act, btn)

            if checkable:
                btn.setChecked(action.isChecked())
                btn.setCheckable(True)
        return btn

    
    def action_trigger(self, data: CfgTouchifyAction):
        if data.action_id in self.registeredActions:
            act: QAction = self.registeredActions[data.action_id]
            act.trigger()
        else:
            action = Krita.instance().action(data.action_id)
            if action:
                action.trigger()
    
    def action_menu(self, action: QAction, data: CfgTouchifyAction):
        _parent = self.__getActionSource(action)
        contextMenu = TouchifyActionMenu(data, _parent)
        contextMenu.show()
            
    def action_brush(self, id):
        brush_presets = ResourceManager.getBrushPresets()
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
                            
    def action_dockergroup(self, data: CfgTouchifyActionDockerGroup):
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
                            
    def action_popup(self, action: QAction, data: CfgTouchifyActionPopup):    
        _parent = self.__getActionSource(action)            
        self.__triggerPopup(data, _parent)
    
    def action_canvas(self, data: CfgTouchifyActionCanvasPreset):
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