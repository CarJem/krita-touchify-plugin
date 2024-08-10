

from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *

from ..settings.TouchifySettings import *
from ..ui.CanvasPresetEditor import *
from ..cfg.CfgCanvasPreset import *
from ..ext.KritaSettings import *
from ..ext.extensions_json import *
from ..ext.extensions_krita import *
from touchify.src import stylesheet
import json
import copy

from ..components.krita.KisSliderSpinBox import KisSliderSpinBox
from ..components.krita.KisAngleSelector import KisAngleSelector
from ..components.pyqt.widgets.ColorButton import ColorButton

if TYPE_CHECKING:
    from ..touchify import TouchifyInstance

class CanvasPresets:
    def __init__(self, instance: "TouchifyInstance"):
        self.appEngine = instance
        
    def getEntries(self, parent: QMenu, mode: str, useParent: bool = False):
        actions: dict[str, list[QAction]] = dict()
        root_actions: list[QAction] = list()
                    
        for index in TouchifySettings.instance().CanvasPresets_Items:
            item = TouchifySettings.instance().CanvasPresets_Items[index]
            if mode == "remove":
                connection = (lambda x, y=index: self.removePreset(y))
            elif mode == "edit":
                connection = (lambda x, y=index: self.editPreset(y))
            elif mode == "activate":
                connection = (lambda x, y=index: self.activatePreset(y))
            
            preset_entry = QAction(item.presetName)
            preset_entry.triggered.connect(connection)
            
            if item.subgroup_enabled:
                subgroup = item.subgroup_name   
                if subgroup not in actions:
                    actions[subgroup] = list()
                actions[subgroup].append(preset_entry)
            else:
                root_actions.append(preset_entry)
                   
        menu = parent if useParent else QMenu(parent)
        
        for action in root_actions:
            action.setParent(menu)
            menu.addAction(action)
        
        for group in actions:
            submenu = QMenu(menu)
            submenu.setTitle(group)
            menu.addMenu(submenu)
            for sub_action in actions[group]:
                sub_action.setParent(submenu)
                submenu.addAction(sub_action)

        return menu
        
    def show(self):
        popup = QMenu(self.appEngine.instanceWindow.qwindow())

        popup.addSeparator().setText("Presets:")   
        self.getEntries(popup, "activate", True)
        
        popup.addSeparator().setText("Options:")   
        popup.addAction(Krita.instance().icon("list-add"), "New Preset", self.addPreset)
        
        editMenu = self.getEntries(popup, "edit")
        editMenu.setIcon(Krita.instance().icon("document-edit"))
        editMenu.setTitle("Edit Preset...")
        popup.addMenu(editMenu)
        
        deleteMenu = self.getEntries(popup, "remove")
        deleteMenu.setIcon(Krita.instance().icon("edit-delete"))
        deleteMenu.setTitle("Delete Preset...")
        popup.addMenu(deleteMenu)
        
        popup.move(QCursor.pos())
        popup.show()
           
    def refreshView(self):
        
        def slotConfigChanged(obj: QObject):
            canvas_call = getattr(obj, "slotConfigChanged", None)
            if callable(canvas_call):
                canvas_call()
        
        qwin = Krita.instance().activeWindow().qwindow()
        for i, view in enumerate(Krita.instance().activeWindow().views()):
            view_obj = qwin.findChild(QWidget,'view_' + str(i))     
            for child in view_obj.children():
                slotConfigChanged(child)
            
            canvas_obj = view_obj.findChild(QOpenGLWidget)
            slotConfigChanged(canvas_obj)
            
        for docker in Krita.instance().dockers():
            if (docker.objectName() == "KisLayerBox"):
                slotConfigChanged(docker)
                
    def addPreset(self):
        dlg = CanvasPresetEditor(CfgCanvasPreset.current(), self.appEngine.instanceWindow.qwindow())
        if dlg.exec_():
            TouchifySettings.instance().CanvasPresets_Items[str("new")] = dlg.preset
            TouchifySettings.instance().saveSettings()
            
    def editPreset(self, index: int):
        dlg = CanvasPresetEditor(TouchifySettings.instance().CanvasPresets_Items[index], self.appEngine.instanceWindow.qwindow())
        if dlg.exec_():
            TouchifySettings.instance().CanvasPresets_Items[index] = dlg.preset
            TouchifySettings.instance().saveSettings()
    
    def removePreset(self, index: int):
        TouchifySettings.instance().CanvasPresets_Items.pop(index)
        TouchifySettings.instance().saveSettings()
        
    def activatePreset(self, index: int):
        TouchifySettings.instance().CanvasPresets_Items[index].activate()
        self.refreshView()