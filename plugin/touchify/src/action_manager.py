from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .variables import *

from .cfg.CfgTouchifyAction import *
from .ext.extensions_krita import *

from .components.touchify.popups.PopupDialog import *
from .components.touchify.popups.PopupDialog_Actions import *
from .components.touchify.popups.PopupDialog_Docker import *







#class ActionManager(QObject):
class ActionManager:
    
    class TriggerConstants:
        KNOWN_UNCHECKABLES = [
            "show_brush_editor"
        ]

        EXPANDING_SPACERS = [
            "expanding_spacer1",
            "expanding_spacer2"
        ]
    
    #def __init__(self, window: Window, docker_manager: DockerManager):  
        #super().__init__(window)
        #self.custom_docker_states = {}
        #self.docker_management = docker_manager
        #self.mainWindow = window
        #self.qWin = window.qwindow()
        
    def __init__(self):  
        self.custom_docker_states = {}       
        
    def windowCreated(self, window: Window, docker_manager: DockerManager):
        self.docker_management = docker_manager
        self.mainWindow = window
        self.qWin = window.qwindow()
        
    def executeAction(self, data: CfgTouchifyAction, action: QAction):
        match data.variant:
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
            
    def createButton(self, data: CfgTouchifyAction, isTool: bool):
        match data.variant:
            case CfgTouchifyAction.Variants.Brush:
                self.button_brush(data.brush_name, isTool)
            case CfgTouchifyAction.Variants.Menu:
                return self.button_menu(data, isTool)
            case CfgTouchifyAction.Variants.Action:
                return self.button_trigger(data, isTool)
            case _:
                return None
    
    def createAction(self, data: CfgTouchifyAction, window: Window, actionPath: str):
        actionIdentifier ='TouchifyAction_{0}'.format(data.id)
        displayName = data.text

        action = window.createAction(actionIdentifier, displayName, actionPath) 
           
        TouchifyConfig.instance().addHotkeyOption(actionIdentifier, displayName, self.executeAction, {'data': data, 'action': action})      
        action.triggered.connect(lambda: self.executeAction(data, action))
        
        (use_text, text, use_icon, icon) = self.__getActionDisplay(data)
        if use_icon:
            action.setIcon(icon)
         
        return action


         
    def __getActionSource(self, action: QAction):
        _sender = action.sender()
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
    
    def __getActionDisplay(self, data: CfgTouchifyAction) -> tuple[bool, QIcon, bool, str]:   
      
        text: str = data.text  
        icon_loader_index = 0
        
        if data.variant == CfgTouchifyAction.Variants.Brush:
            if data.brush_override_icon and data.showIcon:
                icon_loader_index = 3
        elif data.variant == CfgTouchifyAction.Variants.Action:
            if data.showIcon and data.action_use_icon:
                icon_loader_index = 2
            elif data.showIcon:
                icon_loader_index = 1
        elif data.showIcon:
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

    def __setButtonDisplay(self, act: CfgTouchifyAction, btn: TouchifyActionPushButton | TouchifyActionToolButton, isTool: bool):
        (use_text, text, use_icon, icon) = self.__getActionDisplay(act)
        
        if isTool:
            btn.setText(text)
        elif use_text:
            btn.setText(text)
        
        if use_icon: 
            btn.setIcon(icon)        

       
    def button_main(self, onClick: any, toolTip: str, checkable: bool, isTool: bool):
        if isTool:
            btn = TouchifyActionToolButton()
        else:
            btn = TouchifyActionPushButton()
        
        if onClick:
            btn.clicked.connect(onClick) # collect and disconnect all when closing
        btn.setToolTip(toolTip)
        btn.setContentsMargins(0,0,0,0)
        btn.setCheckable(checkable)
        return btn
   
    def button_brush(self, act: CfgTouchifyAction, isTool: bool):
        btn: TouchifyActionPushButton | TouchifyActionToolButton | None = None
        id = act.brush_name
        brush_presets = ResourceManager.getBrushPresets()
        
        if id in brush_presets:
            preset = brush_presets[id]
            btn = self.button_main(lambda: self.action_brush(act.brush_name), preset.name(), False, isTool)
            self.__setButtonDisplay(act, btn, isTool)
        return btn
                   
    def button_menu(self, act: CfgTouchifyAction, isTool: bool):
        btn: TouchifyActionPushButton | TouchifyActionToolButton = self.button_main(None, act.text, False, isTool)   
        self.__setButtonDisplay(act, btn, isTool)
        
        contextMenu = TouchifyActionMenu(act, btn)
        btn.setMenu(contextMenu)
        btn.clicked.connect(btn.showMenu)
        return btn
        
    def button_trigger(self, act: CfgTouchifyAction, isTool: bool):
        action = Krita.instance().action(act.action_id)
        btn: TouchifyActionPushButton | TouchifyActionToolButton | None = None
        if action:
            checkable = action.isCheckable()
            if act.action_id in ActionManager.TriggerConstants.KNOWN_UNCHECKABLES:
                checkable = False
                  
            btn = self.button_main(action.trigger, action.toolTip(), checkable, isTool)
            self.__setButtonDisplay(act, btn, isTool)

            if checkable:
                btn.setChecked(action.isChecked())
                btn.setCheckable(True)
        return btn

    
    def action_trigger(self, data: CfgTouchifyAction):
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
            Krita.instance().activeWindow().activeView().setCurrentBrushPreset(preset)
    
    def action_docker(self, path):
        dockersList = Krita.instance().dockers()
        for docker in dockersList:
            if (docker.objectName() == path):
                docker.setVisible(not docker.isVisible())
                    
    def action_workspace(self, path):
        main_menu = self.qWin.menuBar()
        for root_items in main_menu.actions():
            if root_items.objectName() == 'window':
                for sub_item in root_items.menu().actions():
                    if sub_item.text() == 'Wor&kspace':
                        for workspace in sub_item.menu().actions():
                            if workspace.text() == path:
                                workspace.trigger()
                                break
                            
    def action_dockergroup(self, data: CfgDockerGroup):
        dockersList = Krita.instance().dockers()
        
        if data.id not in self.custom_docker_states:
            paths = []
            for dockerName in data.docker_names:
                paths.append(str(dockerName))

            self.custom_docker_states[data.id] = {
                "enabled": False,
                "paths": paths,
                "groupId": data.groupId,
                "tabsMode": data.tabsMode
            }
        dockerGroup = self.custom_docker_states[data.id]
            

        isVisible = not dockerGroup["enabled"]
        dockerGroup["enabled"] = isVisible

        if dockerGroup["tabsMode"]:
            for index, key in enumerate(self.custom_docker_states):
                entry = self.custom_docker_states[key]
                if key is not id and dockerGroup["groupId"] == entry["groupId"] and entry["tabsMode"]:
                    sub_visibility = False
                    entry["enabled"] = sub_visibility
                    for path in entry["paths"]:
                        for docker in dockersList:
                            if (docker.objectName() == path):
                                docker.setVisible(sub_visibility)

        for path in self.custom_docker_states[id]["paths"]:
            for docker in dockersList:
                if (docker.objectName() == path):
                    docker.setVisible(isVisible)
                            
    def action_popup(self, action: QAction, data: CfgPopup):    
        _parent = self.__getActionSource(action)            
        if data.type == "actions":
            popup = PopupDialog_Actions(self.qWin, data, self)
        elif data.type == "docker":
            popup = PopupDialog_Docker(self.qWin, data, self.docker_management)
        else:
            popup = PopupDialog(self.qWin, data)  
        popup.triggerPopup(_parent)