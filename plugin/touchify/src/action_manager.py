from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .variables import *

from .cfg.CfgTouchifyAction import *

from .components.popups.PopupDialog import *
from .components.popups.PopupDialog_Actions import *
from .components.popups.PopupDialog_Docker import *




class ActionManager(QObject):
    def __init__(self, window: Window, docker_manager: DockerManager):  
        super().__init__(window)
        
        self.custom_docker_states = {}
        self.docker_management = docker_manager
        self.mainWindow = window
        self.qWin = window.qwindow()
        
    def executeAction(self, action: QAction, data: CfgTouchifyAction, overMouse: bool):
        if data.action_type == CfgTouchifyAction.ActionType.Docker:
            self.action_docker(data.docker_id)
        elif data.action_type == CfgTouchifyAction.ActionType.Workspace:
            self.action_workspace(data.workspace_id)
        elif data.action_type == CfgTouchifyAction.ActionType.Popup:
            self.action_popup(action, data.popup_data, overMouse)
            
    
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
                            
    def action_popup(self, action: QAction, data: CfgPopup, overMouse: bool):    
        
        _mode = "mouse" if overMouse else "button"
        _sender = action.sender()
        _parent = None
        if isinstance(_sender, QWidget):
            _parent: QWidget = _sender
            
        if data.type == "actions":
            popup = PopupDialog_Actions(self.qWin, data)
        elif data.type == "docker":
            popup = PopupDialog_Docker(self.qWin, data, self.docker_management)
        else:
            popup = PopupDialog(self.qWin, data)
            
        popup.triggerPopup(_mode, _parent)